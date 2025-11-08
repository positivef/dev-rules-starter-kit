# CI/CD Guide - GitHub Actions Constitution Check

**Stage 5 Phase 2**: Automated Constitution enforcement in CI/CD

---

## 🎯 Overview

GitHub Actions workflow that automatically checks Constitution compliance on every PR and push.

**Key Features**:
- ✅ Automatic Constitution verification (P4/P5/P7/P10)
- ✅ Security scanning (P5)
- ✅ Test coverage check (P8)
- ✅ Quality Gate enforcement (P6)
- ✅ PR auto-comment with results
- ✅ Merge blocking on failures

---

## 🚀 Quick Start

### 1. Enable GitHub Actions

GitHub Actions is automatically enabled when you push `.github/workflows/constitution-check.yml`.

### 2. Create a Pull Request

```bash
git checkout -b feature/my-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

Create PR on GitHub → CI automatically runs

### 3. Review Results

Check the "Constitution Check" workflow in the PR:
- Green checkmark (✅): All checks passed
- Red X (❌): Some checks failed
- Yellow dot (●): Running

### 4. View Details

Click on "Details" to see:
- Which checks failed
- Detailed error messages
- Downloadable reports (artifacts)

---

## 📋 Workflow Jobs

### Job 1: Constitution Guard (P4/P5/P7/P10)

**What it checks**:
- P4 (SOLID): `eval()` usage, function length
- P5 (Security): Hardcoded secrets, SQL injection, `os.system()`
- P7 (Hallucination): TODO overload, pass-only functions
- P10 (Encoding): Emoji in Python code

**Timeout**: 10 minutes

**Failure**: Blocks PR merge

### Job 2: Ruff Linter (P10)

**What it checks**:
- Code formatting
- Linting errors
- Encoding issues

**Timeout**: 5 minutes

**Failure**: Blocks PR merge

### Job 3: Security Scan (P5)

**What it checks**:
- Secrets in code (Gitleaks)
- API keys, passwords, tokens

**Timeout**: 10 minutes

**Failure**: Blocks PR merge

### Job 4: Test Coverage (P8)

**What it checks**:
- Test coverage ≥ 80%
- Tests pass

**Timeout**: 15 minutes

**Failure**: Warning only (doesn't block)

### Job 5: Quality Gate (P6)

**What it checks**:
- All previous checks passed
- Constitution compliance

**Timeout**: 5 minutes

**Failure**: Blocks PR merge

### Job 6: Constitution Full Check

**What it checks**:
- P1-P16 comprehensive validation
- Generates summary report

**Timeout**: 10 minutes

**Failure**: Warning only

### Job 7: PR Comment

**What it does**:
- Posts results as PR comment
- Shows pass/fail for each check
- Links to detailed reports

---

## 🔧 Configuration

### Trigger Events

**Pull Requests**:
```yaml
on:
  pull_request:
    branches:
      - main
      - master
      - develop
```

**Pushes**:
```yaml
on:
  push:
    branches:
      - tier1/**
      - tier2/**
      - feature/**
      - fix/**
```

### Customize Branches

Edit `.github/workflows/constitution-check.yml`:

```yaml
on:
  pull_request:
    branches:
      - your-branch-name
```

### Adjust Timeouts

```yaml
jobs:
  constitution-guard:
    timeout-minutes: 10  # Change this
```

### Coverage Threshold

Edit `scripts/quality_gate_ci.py`:

```python
threshold = 80.0  # Change to 70.0, 90.0, etc.
```

---

## 📊 Understanding Results

### PR Comment Format

```markdown
## Constitution Check Results

| Check | Status |
|-------|--------|
| Constitution Guard (P4/P5/P7/P10) | ✅ Passed |
| Ruff Linter (P10) | ✅ Passed |
| Security Scan (P5) | ✅ Passed |
| Test Coverage (P8) | ⚠️ Warning |
| Quality Gate (P6) | ✅ Passed |
```

### Status Icons

- ✅ **Passed**: Check succeeded
- ❌ **Failed**: Check failed, PR blocked
- ⚠️ **Warning**: Check failed, but PR not blocked

---

## 🐛 Troubleshooting

### "Constitution Guard failed"

**Cause**: Code violates P4/P5/P7/P10

**Solution**:
1. Click "Details" in the workflow
2. Read the violation messages
3. Fix the code
4. Push again

**Example**:
```
[HIGH] P4: eval() 사용 금지
  Fix: Use ast.literal_eval() or json.loads()
```

### "Security Scan failed"

**Cause**: Hardcoded secret detected

**Solution**:
1. Remove hardcoded secrets
2. Use environment variables
3. Add to `.env` (not committed)

**Example**:
```python
# ❌ Wrong
APIKEY = "hardcoded-secret-value"

# ✅ Correct
import os
API_KEY = os.getenv("API_KEY")
```

### "Test Coverage failed"

**Cause**: Coverage < 80%

**Solution**:
1. Write more tests
2. Or adjust threshold in `quality_gate_ci.py`

**Note**: This is a warning, not a blocker

### "Quality Gate failed"

**Cause**: One or more checks failed

**Solution**:
1. Fix all failing checks
2. Push again
3. Quality Gate will re-run

### "Workflow not running"

**Possible causes**:
1. Branch name doesn't match trigger pattern
2. Workflow file has syntax error
3. GitHub Actions not enabled

**Solution**:
1. Check branch name (should match pattern)
2. Validate YAML syntax
3. Enable Actions in repo settings

---

## 🔐 Secrets Configuration

### Required Secrets (Optional)

**GITLEAKS_LICENSE** (optional):
- For Gitleaks Pro features
- Not required for basic usage

**How to add**:
1. Go to repo Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `GITLEAKS_LICENSE`
4. Value: Your license key

---

## 📦 Artifacts

### Available Reports

After workflow runs, download:

1. **constitution-guard-report**: Detailed violations
2. **coverage-report**: Test coverage XML
3. **quality-gate-report**: Quality Gate results

### How to Download

1. Go to workflow run page
2. Scroll to "Artifacts" section
3. Click to download

### Retention

Reports are kept for **30 days**.

---

## 🚫 Bypassing CI (Not Recommended)

### Local Bypass

```bash
git commit --no-verify
```

**Warning**: CI will still run on PR!

### Skip CI (Emergency Only)

Add to commit message:
```
[skip ci]
```

**Warning**: Violates Constitution! Only for emergencies.

---

## 📈 Performance

### Expected Execution Time

| Job | Time |
|-----|------|
| Constitution Guard | ~30s |
| Ruff Linter | ~15s |
| Security Scan | ~45s |
| Test Coverage | 1-5min |
| Quality Gate | ~5s |
| **Total** | **2-7min** |

### Optimization Tips

1. **Cache dependencies**: Already enabled
2. **Parallel jobs**: Already optimized
3. **Skip tests on drafts**: Add `if: github.event.pull_request.draft == false`

---

## 🔄 Workflow Diagram

```
PR Created/Updated
    ↓
[Constitution Guard] ──┐
[Ruff Linter] ─────────┤
[Security Scan] ───────┤
[Test Coverage] ───────┤
    ↓                  ↓
[Quality Gate] ← All checks
    ↓
[Constitution Full Check]
    ↓
[PR Comment]
    ↓
✅ Merge allowed / ❌ Blocked
```

---

## 📝 Best Practices

### 1. Fix Locally First

Run hooks before pushing:
```bash
pre-commit run --all-files
```

### 2. Small PRs

Keep PRs small for faster CI:
- Fewer files = faster checks
- Easier to fix violations

### 3. Write Tests

Maintain 80%+ coverage:
- CI won't block, but good practice
- Aligns with P8 (Test-First)

### 4. Review Before Merge

Even if CI passes, review:
- Code quality
- Architecture decisions
- Documentation

### 5. Monitor CI Metrics

Track over time:
- Average CI time
- Failure rate
- Most common violations

---

## 🆘 Getting Help

### Common Issues

See "Troubleshooting" section above.

### Contact

- Team channel: #dev-rules
- Documentation: `/docs`
- Issues: GitHub Issues

---

**Last Updated**: 2025-11-07
**Stage**: 5 Phase 2
**Version**: 1.0.0
