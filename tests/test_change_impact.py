"""Tests for the change impact analyzer."""
from __future__ import annotations

import pytest
from tools.change_impact import (
    FileDiff,
    ComplexityInfo,
    FileChurn,
    ImpactReport,
    parse_diff,
    score_size,
    score_complexity,
    score_churn,
    score_test_ratio,
    score_critical_path,
    score_cognitive,
    compute_composite,
    _cognitive_score_for_hunks,
    _fallback_complexity,
    format_text,
    format_json,
    format_markdown,
)


# ── Diff Parsing ──────────────────────────────────────────────────────

SAMPLE_DIFF = """\
diff --git a/seasons/spring.py b/seasons/spring.py
index abc1234..def5678 100644
--- a/seasons/spring.py
+++ b/seasons/spring.py
@@ -10,6 +10,8 @@ SPRING = SeasonInfo(
     ),
+    activities=(
+        "Hiking",
+    ),
 )
-
"""

SAMPLE_DIFF_NEW_FILE = """\
diff --git a/seasons/new.py b/seasons/new.py
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/seasons/new.py
@@ -0,0 +1,3 @@
+# New file
+def hello():
+    pass
"""


def test_parse_diff_basic():
    files = parse_diff(SAMPLE_DIFF)
    assert len(files) == 1
    assert files[0].path == "seasons/spring.py"
    assert files[0].lines_added == 3
    assert files[0].lines_removed == 1
    assert not files[0].is_new


def test_parse_diff_new_file():
    files = parse_diff(SAMPLE_DIFF_NEW_FILE)
    assert len(files) == 1
    assert files[0].is_new is True
    assert files[0].lines_added == 3


def test_parse_diff_empty():
    files = parse_diff("")
    assert files == []


# ── Size Scoring ──────────────────────────────────────────────────────

def test_score_size_zero():
    assert score_size([]) == 0.0


def test_score_size_small():
    files = [FileDiff(path="a.py", lines_added=5, lines_removed=2)]
    score = score_size(files)
    assert 0 < score < 50


def test_score_size_large():
    files = [FileDiff(path=f"f{i}.py", lines_added=100, lines_removed=50) for i in range(10)]
    score = score_size(files)
    assert score > 60


# ── Complexity Scoring ────────────────────────────────────────────────

def test_score_complexity_no_change():
    assert score_complexity([]) == 0.0


def test_score_complexity_increase():
    info = [ComplexityInfo(path="a.py", before=2.0, after=5.0)]
    score = score_complexity(info)
    assert score > 30


def test_score_complexity_decrease():
    info = [ComplexityInfo(path="a.py", before=5.0, after=2.0)]
    score = score_complexity(info)
    # Decrease is still some risk but less
    assert score < 30


# ── Churn Scoring ─────────────────────────────────────────────────────

def test_score_churn_zero():
    assert score_churn([]) == 0.0


def test_score_churn_hot_files():
    churn = [FileChurn(path="hot.py", commit_count=20)]
    score = score_churn(churn)
    assert score > 50


# ── Test Ratio Scoring ────────────────────────────────────────────────

def test_score_test_ratio_no_prod():
    files = [FileDiff(path="tests/test_a.py", lines_added=10)]
    assert score_test_ratio(files) == 0.0


def test_score_test_ratio_no_tests():
    files = [FileDiff(path="seasons/core.py", lines_added=50)]
    score = score_test_ratio(files)
    assert score >= 80.0


def test_score_test_ratio_good():
    files = [
        FileDiff(path="seasons/core.py", lines_added=20),
        FileDiff(path="tests/test_core.py", lines_added=25),
    ]
    score = score_test_ratio(files)
    assert score == 0.0  # ratio >= 1.0


# ── Critical Path Scoring ────────────────────────────────────────────

def test_score_critical_path_none():
    files = [FileDiff(path="seasons/spring.py")]
    assert score_critical_path(files) == 0.0


def test_score_critical_path_hit():
    files = [
        FileDiff(path="seasons/__init__.py"),
        FileDiff(path="seasons/cli.py"),
    ]
    score = score_critical_path(files)
    assert score >= 40.0


# ── Cognitive Scoring ─────────────────────────────────────────────────

def test_cognitive_empty():
    assert _cognitive_score_for_hunks([]) == 0.0


def test_cognitive_simple():
    hunks = ["+x = 1\n+y = 2\n+z = x + y"]
    score = _cognitive_score_for_hunks(hunks)
    assert score < 30


def test_cognitive_complex():
    hunks = [
        "+        if condition:\n"
        "+            for item in items:\n"
        "+                if item.valid and item.active or item.override:\n"
        "+                    try:\n"
        "+                        process(item)\n"
        "+                    except Exception:\n"
        "+                        handle(item)"
    ]
    score = _cognitive_score_for_hunks(hunks)
    assert score > 20  # Deep nesting + branching


# ── Fallback Complexity ───────────────────────────────────────────────

def test_fallback_complexity_simple():
    src = "x = 1\ny = 2\nz = x + y\n"
    score = _fallback_complexity(src)
    assert score == 0.0


def test_fallback_complexity_branchy():
    src = "\n".join([
        "if a:",
        "    for x in y:",
        "        if z and w:",
        "            try:",
        "                pass",
        "            except:",
        "                pass",
    ])
    score = _fallback_complexity(src)
    assert score > 0


# ── Composite Score ───────────────────────────────────────────────────

def test_compute_composite_low():
    report = ImpactReport(
        size_score=10, complexity_score=5, churn_score=0,
        test_ratio_score=0, critical_path_score=0, cognitive_score=5,
    )
    compute_composite(report)
    assert report.composite_score < 25
    assert report.grade == "Low"


def test_compute_composite_high():
    report = ImpactReport(
        size_score=80, complexity_score=90, churn_score=70,
        test_ratio_score=80, critical_path_score=60, cognitive_score=70,
    )
    compute_composite(report)
    assert report.composite_score > 50
    assert report.grade in ("High", "Critical")


# ── Output Formatters ─────────────────────────────────────────────────

@pytest.fixture
def sample_report() -> ImpactReport:
    report = ImpactReport(
        files=[
            FileDiff(path="seasons/spring.py", lines_added=10, lines_removed=3),
            FileDiff(path="tests/test_spring.py", lines_added=8, lines_removed=0, is_new=True),
        ],
        complexity=[ComplexityInfo(path="seasons/spring.py", before=2.0, after=3.5)],
        churn=[FileChurn(path="seasons/spring.py", commit_count=5)],
        size_score=30, complexity_score=25, churn_score=15,
        test_ratio_score=10, critical_path_score=0, cognitive_score=12,
    )
    compute_composite(report)
    return report


def test_format_text(sample_report: ImpactReport):
    output = format_text(sample_report)
    assert "Change Impact Analysis" in output
    assert "spring.py" in output
    assert sample_report.grade in output


def test_format_json(sample_report: ImpactReport):
    output = format_json(sample_report)
    data = __import__("json").loads(output)
    assert "composite_score" in data
    assert "grade" in data
    assert data["files_changed"] == 2


def test_format_markdown(sample_report: ImpactReport):
    output = format_markdown(sample_report)
    assert "Change Impact" in output
    assert "| Metric | Score |" in output
    assert "spring.py" in output


# ── ImpactReport.to_dict ─────────────────────────────────────────────

def test_report_to_dict(sample_report: ImpactReport):
    d = sample_report.to_dict()
    assert d["files_changed"] == 2
    assert d["total_lines_added"] == 18
    assert d["total_lines_removed"] == 3
    assert "subscores" in d
    assert len(d["files"]) == 2
