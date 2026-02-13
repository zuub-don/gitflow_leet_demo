#!/usr/bin/env python3
"""
Change Impact Analyzer
======================
Measures the complexity and risk impact of a git diff.

Metrics computed:
  1. Diff size        — lines added / removed / modified, files touched
  2. Complexity delta — cyclomatic complexity before vs after (radon)
  3. Cognitive load   — nested depth & branching in changed hunks
  4. File churn       — how frequently each changed file has been modified
  5. Test ratio       — proportion of test code relative to production code
  6. Critical path    — whether "core" files are touched (configurable)
  7. Composite score  — weighted sum → Low / Medium / High / Critical

Usage:
  # Analyze staged changes (pre-commit mode):
  python -m tools.change_impact --staged

  # Analyze diff between two refs:
  python -m tools.change_impact --base main --head HEAD

  # Output JSON (for CI):
  python -m tools.change_impact --base main --head HEAD --format json

  # Set score threshold (exit non-zero if exceeded):
  python -m tools.change_impact --staged --threshold 60
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class FileDiff:
    """Parsed diff information for a single file."""
    path: str
    lines_added: int = 0
    lines_removed: int = 0
    is_new: bool = False
    is_deleted: bool = False
    is_renamed: bool = False
    hunks: list[str] = field(default_factory=list)


@dataclass
class ComplexityInfo:
    """Cyclomatic complexity for a file, before and after."""
    path: str
    before: float = 0.0
    after: float = 0.0

    @property
    def delta(self) -> float:
        return self.after - self.before


@dataclass
class FileChurn:
    """Historical change frequency for a file."""
    path: str
    commit_count: int = 0


@dataclass
class ImpactReport:
    """Full impact analysis report."""
    files: list[FileDiff] = field(default_factory=list)
    complexity: list[ComplexityInfo] = field(default_factory=list)
    churn: list[FileChurn] = field(default_factory=list)

    # Subscores (0–100 scale each)
    size_score: float = 0.0
    complexity_score: float = 0.0
    churn_score: float = 0.0
    test_ratio_score: float = 0.0
    critical_path_score: float = 0.0
    cognitive_score: float = 0.0

    # Composite
    composite_score: float = 0.0
    grade: str = "Low"

    def to_dict(self) -> dict:
        return {
            "files_changed": len(self.files),
            "total_lines_added": sum(f.lines_added for f in self.files),
            "total_lines_removed": sum(f.lines_removed for f in self.files),
            "subscores": {
                "size": round(self.size_score, 1),
                "complexity_delta": round(self.complexity_score, 1),
                "churn": round(self.churn_score, 1),
                "test_ratio": round(self.test_ratio_score, 1),
                "critical_path": round(self.critical_path_score, 1),
                "cognitive": round(self.cognitive_score, 1),
            },
            "composite_score": round(self.composite_score, 1),
            "grade": self.grade,
            "files": [
                {
                    "path": f.path,
                    "added": f.lines_added,
                    "removed": f.lines_removed,
                }
                for f in self.files
            ],
        }


# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

# Weights for composite score (must sum to 1.0)
WEIGHTS = {
    "size": 0.20,
    "complexity": 0.25,
    "churn": 0.10,
    "test_ratio": 0.15,
    "critical_path": 0.15,
    "cognitive": 0.15,
}

# Glob patterns for files considered "critical" (high-risk when changed)
CRITICAL_PATTERNS: list[str] = [
    "**/cli.py",
    "**/registry.py",
    "**/__init__.py",
    "**/setup.py",
    "**/pyproject.toml",
    "**/*.yml",
    "**/*.yaml",
    "**/Dockerfile",
    "**/.env*",
]

# Grade thresholds
GRADE_THRESHOLDS = [
    (25, "Low"),
    (50, "Medium"),
    (75, "High"),
    (100, "Critical"),
]


# ═══════════════════════════════════════════════════════════════════════
# Git Helpers
# ═══════════════════════════════════════════════════════════════════════

def _run(cmd: list[str], check: bool = True) -> str:
    """Run a subprocess and return stdout."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check,
    )
    return result.stdout


def get_diff_text(*, staged: bool = False, base: str | None = None, head: str | None = None) -> str:
    """Retrieve the raw unified diff."""
    if staged:
        return _run(["git", "diff", "--cached", "-U3"])
    if base and head:
        return _run(["git", "diff", f"{base}...{head}", "-U3"])
    if base:
        return _run(["git", "diff", base, "-U3"])
    # Default: unstaged working tree changes
    return _run(["git", "diff", "-U3"])


def get_file_at_ref(path: str, ref: str) -> str | None:
    """Retrieve file contents at a given git ref. Returns None if missing."""
    try:
        return _run(["git", "show", f"{ref}:{path}"], check=True)
    except subprocess.CalledProcessError:
        return None


def get_file_churn(path: str, max_count: int = 200) -> int:
    """Count how many commits have touched this file."""
    try:
        log = _run(["git", "log", "--oneline", f"--max-count={max_count}", "--", path])
        return len(log.strip().splitlines()) if log.strip() else 0
    except subprocess.CalledProcessError:
        return 0


# ═══════════════════════════════════════════════════════════════════════
# Diff Parser
# ═══════════════════════════════════════════════════════════════════════

_DIFF_HEADER = re.compile(r"^diff --git a/(.*) b/(.*)")
_HUNK_HEADER = re.compile(r"^@@ .+ @@")
_NEW_FILE = re.compile(r"^new file mode")
_DELETED_FILE = re.compile(r"^deleted file mode")
_RENAME = re.compile(r"^rename (from|to)")


def parse_diff(diff_text: str) -> list[FileDiff]:
    """Parse unified diff into per-file structures."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    in_hunk = False
    hunk_lines: list[str] = []

    for line in diff_text.splitlines():
        header_match = _DIFF_HEADER.match(line)
        if header_match:
            # Flush previous hunk
            if current and hunk_lines:
                current.hunks.append("\n".join(hunk_lines))
            current = FileDiff(path=header_match.group(2))
            files.append(current)
            in_hunk = False
            hunk_lines = []
            continue

        if current is None:
            continue

        if _NEW_FILE.match(line):
            current.is_new = True
            continue
        if _DELETED_FILE.match(line):
            current.is_deleted = True
            continue
        if _RENAME.match(line):
            current.is_renamed = True
            continue

        if _HUNK_HEADER.match(line):
            if hunk_lines:
                current.hunks.append("\n".join(hunk_lines))
            hunk_lines = []
            in_hunk = True
            continue

        if in_hunk:
            hunk_lines.append(line)
            if line.startswith("+") and not line.startswith("+++"):
                current.lines_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                current.lines_removed += 1

    # Flush last hunk
    if current and hunk_lines:
        current.hunks.append("\n".join(hunk_lines))

    return files


# ═══════════════════════════════════════════════════════════════════════
# Complexity Analysis
# ═══════════════════════════════════════════════════════════════════════

def _avg_complexity_from_source(source: str) -> float:
    """Compute average cyclomatic complexity using radon, if available."""
    try:
        from radon.complexity import cc_visit
    except ImportError:
        return _fallback_complexity(source)

    try:
        blocks = cc_visit(source)
        if not blocks:
            return 0.0
        return sum(b.complexity for b in blocks) / len(blocks)
    except Exception:
        return 0.0


def _fallback_complexity(source: str) -> float:
    """
    Lightweight fallback when radon is not installed.
    Counts branching keywords as a rough proxy for cyclomatic complexity.
    """
    keywords = r"\b(if|elif|else|for|while|except|with|and|or|try)\b"
    matches = re.findall(keywords, source)
    # Normalize: ~1 per 10 lines is baseline
    line_count = max(len(source.splitlines()), 1)
    density = len(matches) / line_count
    # Scale to pseudo-complexity: density * 10 ≈ rough CC
    return round(density * 10, 2)


def compute_complexity(
    files: list[FileDiff],
    *,
    base_ref: str | None = None,
) -> list[ComplexityInfo]:
    """Compute complexity delta for each changed Python file."""
    results: list[ComplexityInfo] = []

    for f in files:
        if not f.path.endswith(".py"):
            continue

        info = ComplexityInfo(path=f.path)

        # "Before" complexity
        if base_ref and not f.is_new:
            before_src = get_file_at_ref(f.path, base_ref)
            if before_src:
                info.before = _avg_complexity_from_source(before_src)

        # "After" complexity — read from working tree or HEAD
        after_path = Path(f.path)
        if after_path.exists():
            info.after = _avg_complexity_from_source(after_path.read_text())
        elif not f.is_deleted:
            # Try HEAD
            after_src = get_file_at_ref(f.path, "HEAD")
            if after_src:
                info.after = _avg_complexity_from_source(after_src)

        results.append(info)

    return results


# ═══════════════════════════════════════════════════════════════════════
# Cognitive Complexity (heuristic)
# ═══════════════════════════════════════════════════════════════════════

def _cognitive_score_for_hunks(hunks: list[str]) -> float:
    """
    Estimate cognitive complexity of changed code hunks.

    Heuristics:
      - Nesting depth of added lines (indentation as proxy)
      - Branching keywords in added lines
      - Long lines (>100 chars) in added code
    """
    total = 0.0
    added_lines = []

    for hunk in hunks:
        for line in hunk.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                code = line[1:]
                added_lines.append(code)

    if not added_lines:
        return 0.0

    for code in added_lines:
        stripped = code.lstrip()
        if not stripped:
            continue

        # Nesting penalty: each 4-space indent level adds 0.5
        indent = len(code) - len(stripped)
        nesting = indent / 4
        total += nesting * 0.5

        # Branching keyword penalty
        branching = len(re.findall(r"\b(if|elif|else|for|while|try|except|and|or)\b", stripped))
        total += branching * 1.0

        # Long line penalty
        if len(stripped) > 100:
            total += 0.5

    # Normalize to 0–100 scale: 50 points of raw cognitive load ≈ 100 score
    return min(100.0, (total / max(len(added_lines), 1)) * 20)


# ═══════════════════════════════════════════════════════════════════════
# Scoring Functions (each returns 0–100)
# ═══════════════════════════════════════════════════════════════════════

def score_size(files: list[FileDiff]) -> float:
    """Score based on total lines changed. Uses logarithmic scaling."""
    total = sum(f.lines_added + f.lines_removed for f in files)
    file_count = len(files)

    if total == 0 and file_count == 0:
        return 0.0

    # Logarithmic: 10 lines → ~20, 100 lines → ~50, 500+ → ~80, 1000+ → ~95
    line_score = min(100, 25 * math.log10(max(total, 1) + 1))

    # File count bonus: many files = higher risk
    file_bonus = min(30, file_count * 5)

    return min(100.0, line_score + file_bonus)


def score_complexity(complexity: list[ComplexityInfo]) -> float:
    """Score based on aggregate complexity increase."""
    if not complexity:
        return 0.0

    total_delta = sum(c.delta for c in complexity)
    max_delta = max((c.delta for c in complexity), default=0)

    # Positive delta = complexity increased (bad)
    # Negative delta = complexity decreased (good, but still some risk)
    if total_delta <= 0:
        return max(0.0, 10.0 + abs(total_delta) * 2)  # Small base risk for any change

    # Scale: +1 avg CC delta ≈ 25 points, +4 ≈ 80
    return min(100.0, total_delta * 20 + max_delta * 5)


def score_churn(churn: list[FileChurn]) -> float:
    """Score based on file change frequency. Hot files = higher risk."""
    if not churn:
        return 0.0

    max_churn = max(c.commit_count for c in churn)
    avg_churn = sum(c.commit_count for c in churn) / len(churn)

    # Scale: avg 5 commits → 25, avg 15+ → 70
    return min(100.0, avg_churn * 5 + max_churn * 2)


def score_test_ratio(files: list[FileDiff]) -> float:
    """
    Score based on test-to-production code ratio.
    Low score = good (tests accompany changes). High score = tests missing.
    """
    prod_lines = 0
    test_lines = 0

    for f in files:
        is_test = "test" in f.path.lower() or f.path.startswith("tests/")
        added = f.lines_added + f.lines_removed
        if is_test:
            test_lines += added
        elif f.path.endswith(".py"):
            prod_lines += added

    if prod_lines == 0:
        return 0.0  # No production code changed

    ratio = test_lines / prod_lines
    # ratio >= 1.0 → excellent (score ~0), ratio 0 → bad (score ~80)
    if ratio >= 1.0:
        return 0.0
    if ratio >= 0.5:
        return 20.0
    if ratio >= 0.2:
        return 50.0
    if ratio > 0:
        return 65.0
    return 80.0  # No tests at all


def score_critical_path(files: list[FileDiff]) -> float:
    """Score based on whether critical files are touched."""
    from fnmatch import fnmatch

    critical_count = 0
    for f in files:
        for pattern in CRITICAL_PATTERNS:
            if fnmatch(f.path, pattern):
                critical_count += 1
                break

    if critical_count == 0:
        return 0.0

    # Each critical file adds ~20 points, capped at 100
    return min(100.0, critical_count * 20)


def score_cognitive(files: list[FileDiff]) -> float:
    """Aggregate cognitive complexity score across all changed files."""
    if not files:
        return 0.0

    scores = [_cognitive_score_for_hunks(f.hunks) for f in files if f.hunks]
    if not scores:
        return 0.0

    return min(100.0, sum(scores) / len(scores))


# ═══════════════════════════════════════════════════════════════════════
# Composite Score & Grading
# ═══════════════════════════════════════════════════════════════════════

def compute_composite(report: ImpactReport) -> None:
    """Compute the weighted composite score and assign a grade."""
    report.composite_score = (
        WEIGHTS["size"] * report.size_score
        + WEIGHTS["complexity"] * report.complexity_score
        + WEIGHTS["churn"] * report.churn_score
        + WEIGHTS["test_ratio"] * report.test_ratio_score
        + WEIGHTS["critical_path"] * report.critical_path_score
        + WEIGHTS["cognitive"] * report.cognitive_score
    )

    for threshold, grade in GRADE_THRESHOLDS:
        if report.composite_score <= threshold:
            report.grade = grade
            break
    else:
        report.grade = "Critical"


# ═══════════════════════════════════════════════════════════════════════
# Main Analysis Pipeline
# ═══════════════════════════════════════════════════════════════════════

def analyze(
    *,
    staged: bool = False,
    base: str | None = None,
    head: str | None = None,
) -> ImpactReport:
    """Run the full change impact analysis pipeline."""
    diff_text = get_diff_text(staged=staged, base=base, head=head)

    if not diff_text.strip():
        return ImpactReport(grade="None", composite_score=0.0)

    report = ImpactReport()

    # 1. Parse diff
    report.files = parse_diff(diff_text)

    # 2. Complexity
    base_ref = base if base else ("HEAD" if staged else "HEAD")
    report.complexity = compute_complexity(report.files, base_ref=base_ref)

    # 3. Churn
    report.churn = [
        FileChurn(path=f.path, commit_count=get_file_churn(f.path))
        for f in report.files
    ]

    # 4. Compute subscores
    report.size_score = score_size(report.files)
    report.complexity_score = score_complexity(report.complexity)
    report.churn_score = score_churn(report.churn)
    report.test_ratio_score = score_test_ratio(report.files)
    report.critical_path_score = score_critical_path(report.files)
    report.cognitive_score = score_cognitive(report.files)

    # 5. Composite
    compute_composite(report)

    return report


# ═══════════════════════════════════════════════════════════════════════
# Output Formatters
# ═══════════════════════════════════════════════════════════════════════

_GRADE_EMOJI = {"None": "⚪", "Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
_BAR_WIDTH = 20


def _bar(value: float, max_val: float = 100.0) -> str:
    filled = int((value / max_val) * _BAR_WIDTH)
    return "█" * filled + "░" * (_BAR_WIDTH - filled)


def format_text(report: ImpactReport) -> str:
    """Human-readable text report."""
    lines: list[str] = []
    emoji = _GRADE_EMOJI.get(report.grade, "⚪")

    lines.append("╔══════════════════════════════════════════════════════╗")
    lines.append(f"║  Change Impact Analysis        {emoji} {report.grade:>8}  ({report.composite_score:.1f}/100)  ║")
    lines.append("╠══════════════════════════════════════════════════════╣")

    lines.append(f"║  Files changed  : {len(report.files):<34} ║")
    added = sum(f.lines_added for f in report.files)
    removed = sum(f.lines_removed for f in report.files)
    lines.append(f"║  Lines          : +{added} / -{removed:<29} ║")
    lines.append("╠══════════════════════════════════════════════════════╣")
    lines.append("║  Subscores:                                        ║")

    for label, attr in [
        ("Diff Size      ", "size_score"),
        ("Complexity Δ   ", "complexity_score"),
        ("File Churn     ", "churn_score"),
        ("Test Ratio     ", "test_ratio_score"),
        ("Critical Path  ", "critical_path_score"),
        ("Cognitive Load ", "cognitive_score"),
    ]:
        val = getattr(report, attr)
        bar = _bar(val)
        lines.append(f"║  {label} {bar} {val:5.1f}  ║")

    lines.append("╠══════════════════════════════════════════════════════╣")
    lines.append("║  Files:                                            ║")

    for f in report.files[:15]:  # Cap display at 15 files
        status = "NEW" if f.is_new else "DEL" if f.is_deleted else "MOD"
        path_display = f.path[:38]
        lines.append(f"║    [{status}] {path_display:<38} +{f.lines_added}/-{f.lines_removed}  ║")

    if len(report.files) > 15:
        lines.append(f"║    ... and {len(report.files) - 15} more files               ║")

    lines.append("╚══════════════════════════════════════════════════════╝")
    return "\n".join(lines)


def format_json(report: ImpactReport) -> str:
    """JSON output for CI integration."""
    return json.dumps(report.to_dict(), indent=2)


def format_markdown(report: ImpactReport) -> str:
    """Markdown output suitable for GitHub PR comments."""
    emoji = _GRADE_EMOJI.get(report.grade, "⚪")
    lines: list[str] = []

    lines.append(f"## {emoji} Change Impact: **{report.grade}** ({report.composite_score:.1f}/100)")
    lines.append("")
    added = sum(f.lines_added for f in report.files)
    removed = sum(f.lines_removed for f in report.files)
    lines.append(f"**{len(report.files)}** files changed — **+{added}** / **-{removed}** lines")
    lines.append("")
    lines.append("| Metric | Score |")
    lines.append("|--------|------:|")

    for label, attr in [
        ("Diff Size", "size_score"),
        ("Complexity Delta", "complexity_score"),
        ("File Churn", "churn_score"),
        ("Test Coverage Ratio", "test_ratio_score"),
        ("Critical Path Risk", "critical_path_score"),
        ("Cognitive Load", "cognitive_score"),
    ]:
        val = getattr(report, attr)
        lines.append(f"| {label} | {val:.1f} |")

    lines.append("")
    lines.append("<details><summary>Files changed</summary>")
    lines.append("")
    lines.append("| File | Status | +/- |")
    lines.append("|------|--------|-----|")

    for f in report.files:
        status = "🆕" if f.is_new else "🗑️" if f.is_deleted else "✏️"
        lines.append(f"| `{f.path}` | {status} | +{f.lines_added}/-{f.lines_removed} |")

    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="change-impact",
        description="Analyze the complexity and risk impact of code changes.",
    )
    parser.add_argument(
        "--staged", action="store_true",
        help="Analyze staged (cached) changes (for pre-commit hooks).",
    )
    parser.add_argument(
        "--base", type=str, default=None,
        help="Base ref for comparison (e.g., 'main', 'develop').",
    )
    parser.add_argument(
        "--head", type=str, default=None,
        help="Head ref for comparison (e.g., 'HEAD', branch name).",
    )
    parser.add_argument(
        "--format", dest="output_format", choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--threshold", type=float, default=None,
        help="Score threshold. Exit non-zero if composite score exceeds this.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = analyze(staged=args.staged, base=args.base, head=args.head)

    if args.output_format == "json":
        print(format_json(report))
    elif args.output_format == "markdown":
        print(format_markdown(report))
    else:
        print(format_text(report))

    if args.threshold is not None and report.composite_score > args.threshold:
        print(
            f"\n⚠ Impact score {report.composite_score:.1f} exceeds "
            f"threshold {args.threshold:.1f}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
