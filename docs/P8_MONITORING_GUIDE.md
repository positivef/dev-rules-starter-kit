# P8 80% Coverage Standard - Monitoring Guide

**Date**: 2025-11-08
**Change**: P8 coverage reduced from 90% → 80%
**Duration**: Monitor for 1 week (2025-11-08 to 2025-11-15)

---

## 📊 What We're Monitoring

### Hypothesis
"80% coverage (industry standard) provides sufficient quality with 40% time savings compared to 90%"

**Expected Results**:
- ✅ Test writing time: **-40%** (based on ROI analysis)
- ✅ Coverage: **80% ± 2%** (acceptable range 78-82%)
- ✅ Bug escape rate: **≤10%** (maintained quality)

**Failure Criteria** (trigger rollback to 90%):
- ❌ Coverage drops below 75%
- ❌ Bug escape rate >15%
- ❌ Multiple production incidents due to insufficient testing

---

## 🚀 Quick Start

### 1. Set Baseline (90% Historical Data)

If you have historical data from 90% coverage period:

```bash
python scripts/p8_impact_monitor.py --baseline \
  --baseline-time 15.0 \
  --baseline-coverage 90.0 \
  --baseline-escape 5.0
```

**Parameters**:
- `--baseline-time`: Average time per test (minutes) under 90% standard
- `--baseline-coverage`: Average coverage achieved (should be ~90%)
- `--baseline-escape`: Bug escape rate (%) under 90% standard

**Example** (estimated values):
- Baseline time: 15 min/test (includes time to reach 90%)
- Baseline coverage: 90%
- Baseline escape: 5% (typical for high coverage)

### 2. Record Daily Metrics

After each development session:

```bash
python scripts/p8_impact_monitor.py --record \
  --time 30.0 \
  --coverage 82.0 \
  --tests 5 \
  --bugs-testing 3 \
  --bugs-prod 0 \
  --notes "Auth module refactoring"
```

**Parameters**:
- `--time`: Total test writing time for this session (minutes)
- `--coverage`: Coverage percentage achieved
- `--tests`: Number of tests written
- `--bugs-testing`: Bugs found during testing
- `--bugs-prod`: Bugs that escaped to production (discovered later)
- `--notes`: Optional session description

### 3. Generate Weekly Report

```bash
python scripts/p8_impact_monitor.py --report
```

**Output Example**:
```
============================================================
P8 Impact Monitor - Weekly Report
Generated: 2025-11-15 10:30
============================================================

CURRENT PERFORMANCE (80% Standard)
------------------------------------------------------------
  Period: Last 7 days
  Data points: 12
  Avg coverage: 81.2%
  Avg time/test: 9.5 min
  Bug escape rate: 4.2%

COMPARISON WITH 90% BASELINE
------------------------------------------------------------
IMPROVEMENTS:
  [SUCCESS] FASTER by 5.5 min/test (36.7%)
  [SUCCESS] Coverage maintained (-8.8%)
  [SUCCESS] Quality maintained (-0.8% escape rate)

VERDICT: SUCCESS: 80% standard is working well

RECOMMENDATIONS
------------------------------------------------------------
  [SUCCESS] Coverage meets 80% standard
  [SUCCESS] Bug escape rate acceptable

============================================================
```

---

## 📅 Weekly Monitoring Schedule

### Week 1 (2025-11-08 to 2025-11-15)

**Daily** (Mon-Fri):
1. After each development session: Record metrics
2. Review coverage: Should be 78-82%
3. Note any testing difficulties

**Friday**:
1. Generate weekly report
2. Review with team/yourself
3. Decide: Continue, Adjust, or Rollback

### Decision Matrix

| Coverage | Bug Escape | Time Savings | Decision |
|----------|------------|--------------|----------|
| 78-82% | ≤10% | >30% | ✅ **CONTINUE** |
| 75-78% | ≤10% | >30% | ⚠️ **MONITOR** closely |
| <75% | >15% | Any | ❌ **ROLLBACK** to 90% |
| 78-82% | >15% | Any | ❌ **ROLLBACK** to 90% |

---

## 🔧 Advanced Usage

### Compare Current vs Baseline

```bash
python scripts/p8_impact_monitor.py --compare
```

Returns detailed JSON comparison for analysis.

### View Raw Metrics

```bash
cat RUNS/p8_monitoring/metrics.jsonl
```

### Manual Analysis

```python
from scripts.p8_impact_monitor import P8ImpactMonitor

monitor = P8ImpactMonitor()
metrics = monitor.load_metrics(days=30)  # Last 30 days

# Custom analysis
avg_coverage = sum(m['coverage_percent'] for m in metrics) / len(metrics)
print(f"30-day average coverage: {avg_coverage:.1f}%")
```

---

## 📈 Metrics Dictionary

### Test Writing Time
- **Definition**: Total time spent writing tests for this session
- **Unit**: Minutes
- **Good**: Decreasing over time (more efficient)
- **Bad**: Increasing (struggling with 80% standard)

### Coverage Percent
- **Definition**: Percentage of code covered by tests
- **Unit**: %
- **Good**: 78-82% (target range)
- **Bad**: <75% (insufficient), >85% (over-testing)

### Time Per Test
- **Definition**: Average time to write one test
- **Unit**: Minutes per test
- **Good**: 8-12 min/test (efficient)
- **Bad**: >15 min/test (inefficient)

### Bug Escape Rate
- **Definition**: % of bugs that escaped to production
- **Formula**: `bugs_prod / (bugs_testing + bugs_prod) * 100`
- **Good**: <10%
- **Bad**: >15% (quality issue)

---

## 🚨 Troubleshooting

### Issue 1: Coverage Dropping Below 75%

**Symptoms**: Weekly average <75%

**Diagnosis**:
1. Are tests being skipped? Check `git log` for test commits
2. Is team aware of 80% target? Communicate change
3. Are certain modules harder to test? Identify patterns

**Solutions**:
1. Re-communicate 80% standard to team
2. Review difficult-to-test modules
3. Consider temporary 85% target for critical modules
4. If persistent: Rollback to 90%

### Issue 2: Bug Escape Rate >15%

**Symptoms**: More bugs reaching production

**Diagnosis**:
1. Are bugs in uncovered code? Check coverage reports
2. Are test quality issues? Review test assertions
3. Is it temporary spike? Check trend over 2+ weeks

**Solutions**:
1. Increase coverage for bug-prone modules
2. Review test quality (not just quantity)
3. Add integration tests for critical paths
4. If persistent: Rollback to 90%

### Issue 3: Time Not Decreasing

**Symptoms**: Time per test same or higher than baseline

**Diagnosis**:
1. Are developers overthinking? Check test complexity
2. Are tests still targeting 90%? Review test files
3. Is baseline accurate? Re-verify 90% historical data

**Solutions**:
1. Training on 80% mindset (focus on critical paths)
2. Show time savings potential
3. Review test examples (good 80% tests)

---

## 📋 Rollback Procedure

If monitoring shows unacceptable results:

### 1. Document Failure

```bash
python scripts/p8_impact_monitor.py --report > RUNS/p8_monitoring/failure_report.txt
```

### 2. Revert Constitution

```bash
cd config
git diff constitution.yaml  # Review change
git checkout HEAD~1 constitution.yaml  # Revert to 90%
```

### 3. Update Documentation

```bash
# Revert CLAUDE.md
git checkout HEAD~1 CLAUDE.md
```

### 4. Notify Team

Send report with:
- Metrics that triggered rollback
- Lessons learned
- Path forward (keep 90% or try 85%?)

---

## 💡 Success Criteria (Week 1 Review)

**GREEN (Continue 80%)**:
- ✅ Coverage: 78-82%
- ✅ Bug escape: <10%
- ✅ Time savings: >30%
- ✅ Team feedback: Positive

**YELLOW (Monitor Week 2)**:
- ⚠️ Coverage: 75-78%
- ⚠️ Bug escape: 10-15%
- ⚠️ Time savings: 20-30%
- ⚠️ Team feedback: Mixed

**RED (Rollback)**:
- ❌ Coverage: <75%
- ❌ Bug escape: >15%
- ❌ Time savings: <20%
- ❌ Team feedback: Negative

---

## 📚 References

- Constitution P8: Test-First Development (80% standard)
- Verification Report: `constitution_verification_report.md`
- Industry Standards: Google 80%, Microsoft 70-80%
- ROI Analysis: 80→90% = +3% quality, +40% time (P8 rationale)

---

**Contact**: Check `constitution_verification_report.md` for detailed analysis
**Last Updated**: 2025-11-08
