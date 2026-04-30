# Skill-Creator Quick Start Guide

## Basic Usage (No Changes)
Create skills as before - no new dependencies required for basic skill creation.

```bash
# Validate a skill
python3 scripts/quick_validate.py path/to/skill/SKILL.md

# Package a skill
python3 scripts/package_skill.py path/to/skill output/dir
```

---

## New Evaluation Features (Requires Python 3.10+ & PyYAML)

### 1. Run Evaluations
Test if your skill triggers correctly:

```bash
cd /path/to/skill-creator
python3 scripts/run_eval.py \
  --skill-path /path/to/your-skill/SKILL.md \
  --eval-set /path/to/evals.json \
  --workers 4 \
  --runs-per-query 3
```

### 2. Visual Review Interface
Generate interactive HTML to review test outputs:

```bash
# Server mode (opens in browser)
python3 eval-viewer/generate_review.py /path/to/workspace --skill-name "my-skill"

# Static HTML mode (for headless/Cowork)
python3 eval-viewer/generate_review.py \
  /path/to/workspace \
  --static /path/to/output.html \
  --skill-name "my-skill"
```

### 3. Aggregate Benchmark Results
Analyze multiple test runs statistically:

```bash
python3 scripts/aggregate_benchmark.py \
  /path/to/benchmark_dir \
  --skill-name "my-skill" \
  --output benchmark.json
```

### 4. Automated Optimization Loop
Iteratively improve skill description:

```bash
python3 scripts/run_loop.py \
  --skill-path /path/to/skill/SKILL.md \
  --eval-set /path/to/evals.json \
  --max-iterations 5 \
  --holdout 0.2  # 20% test set
```

---

## Agent Prompts

Use these for specialized evaluation tasks:

- `agents/grader.md` - Grade test outputs against assertions
- `agents/comparator.md` - A/B compare two skill versions  
- `agents/analyzer.md` - Analyze benchmark statistics

---

## JSON Schemas

See `references/schemas.md` for:
- `evals.json` - Test case definitions
- `grading.json` - Evaluation results
- `feedback.json` - User review feedback
- `benchmark.json` - Statistical summaries

---

## Setup Requirements

### For Evaluation Features
```bash
# 1. Check Python version (need 3.10+)
python3 --version

# 2. Install Python 3.10+ if needed
brew install python@3.11  # or python@3.10, python@3.12

# 3. Install PyYAML
pip3 install PyYAML

# 4. Verify Claude CLI
claude --version
claude -p "test prompt"
```

### Optional: Set up Python path for scripts
```bash
export PYTHONPATH=/path/to/skill-creator:$PYTHONPATH
```

---

## Typical Workflow

1. **Create/Update Skill** (basic SKILL.md editing)
2. **Write Test Cases** (create evals.json)
3. **Run Tests** (run_eval.py)
4. **Review Results** (generate_review.py)
5. **Get Feedback** (review in browser, download feedback.json)
6. **Iterate** (revise skill based on feedback)
7. **Benchmark** (aggregate_benchmark.py for stats)
8. **Optimize** (run_loop.py for description tuning)
9. **Package** (package_skill.py)

---

## Help

All scripts support `--help`:
```bash
python3 scripts/run_eval.py --help
python3 scripts/aggregate_benchmark.py --help
python3 eval-viewer/generate_review.py --help
python3 scripts/run_loop.py --help
```

Read `SKILL.md` for complete documentation.
