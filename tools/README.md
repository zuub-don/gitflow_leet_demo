# Change Impact Analyzer

A programmatic tool for measuring the **complexity and risk impact** of code changes.
It scores every diff across six metrics and produces a composite **Impact Score** (0–100)
with a grade: 🟢 Low / 🟡 Medium / 🟠 High / 🔴 Critical.

## Metrics

| # | Metric | Weight | What It Measures |
|---|--------|-------:|------------------|
| 1 | **Diff Size** | 20% | Lines added/removed + file count (log-scaled) |
| 2 | **Complexity Delta** | 25% | Cyclomatic complexity change via [radon](https://radon.readthedocs.io/) (or keyword-based fallback) |
| 3 | **File Churn** | 10% | How frequently changed files appear in `git log` (hot = risky) |
| 4 | **Test Ratio** | 15% | Proportion of test code relative to production code changed |
| 5 | **Critical Path** | 15% | Whether core files (entry points, config, registries) are touched |
| 6 | **Cognitive Load** | 15% | Nesting depth, branching density, and line length in added code |

## Usage

### Local CLI

```bash
# Analyze staged changes (what you're about to commit):
python -m tools.change_impact --staged

# Compare two branches:
python -m tools.change_impact --base main --head feature/my-feature

# JSON output for scripting:
python -m tools.change_impact --base main --head HEAD --format json

# Markdown output (for PR comments):
python -m tools.change_impact --base main --head HEAD --format markdown

# Block if score > threshold:
python -m tools.change_impact --staged --threshold 60
```

### Pre-Commit Hook (manual install)

```bash
# Symlink the hook into .git/hooks/:
ln -sf ../../tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Configure threshold (default: 75):
export CHANGE_IMPACT_THRESHOLD=60
```

### Pre-Commit Framework

```bash
pip install pre-commit
pre-commit install

# The .pre-commit-config.yaml is already configured.
# Runs automatically on every commit.
```

### GitHub Action

The workflow at `.github/workflows/change-impact.yml` runs automatically on PRs
targeting `main` or `develop`. It:

1. Computes the impact score
2. Posts a Markdown summary as a **sticky PR comment**
3. Uploads the JSON report as a **build artifact**
4. **Fails the check** if the score exceeds the threshold

## Scoring Details

### Composite Score Formula

```
composite = 0.20 × size
          + 0.25 × complexity_delta
          + 0.10 × churn
          + 0.15 × test_ratio
          + 0.15 × critical_path
          + 0.15 × cognitive
```

### Grade Thresholds

| Score Range | Grade | Meaning |
|-------------|-------|---------|
| 0 – 25 | 🟢 Low | Routine change, low risk |
| 26 – 50 | 🟡 Medium | Moderate scope, review recommended |
| 51 – 75 | 🟠 High | Large or complex change, thorough review required |
| 76 – 100 | 🔴 Critical | High-risk change, consider splitting |

### Complexity Analysis

When `radon` is installed, the tool computes **cyclomatic complexity** per function
before and after the change. When `radon` is unavailable, it falls back to a
keyword-counting heuristic (counting `if/elif/else/for/while/try/except/and/or`).

### Cognitive Load Heuristic

For each added line in the diff, the tool calculates:
- **Nesting penalty**: 0.5 points per indentation level (4-space)
- **Branching penalty**: 1.0 point per branching keyword
- **Long line penalty**: 0.5 points for lines over 100 characters

### Critical Path Detection

Files matching these glob patterns are flagged as critical:
- `**/cli.py`, `**/registry.py`, `**/__init__.py`
- `**/pyproject.toml`, `**/*.yml`, `**/*.yaml`
- `**/Dockerfile`, `**/.env*`, `**/setup.py`

Customize by editing `CRITICAL_PATTERNS` in `tools/change_impact.py`.

## Example Output

```
╔══════════════════════════════════════════════════════╗
║  Change Impact Analysis        🟡  Medium  (38.2/100)  ║
╠══════════════════════════════════════════════════════╣
║  Files changed  : 4                                  ║
║  Lines          : +85 / -12                          ║
╠══════════════════════════════════════════════════════╣
║  Subscores:                                          ║
║  Diff Size       ████████░░░░░░░░░░░░  35.2  ║
║  Complexity Δ    ██████████░░░░░░░░░░  45.0  ║
║  File Churn      ████░░░░░░░░░░░░░░░░  18.5  ║
║  Test Ratio      ████████░░░░░░░░░░░░  20.0  ║
║  Critical Path   ████████░░░░░░░░░░░░  40.0  ║
║  Cognitive Load  ██████░░░░░░░░░░░░░░  28.3  ║
╚══════════════════════════════════════════════════════╝
```
