# Pattern 4 Monitoring Guide

## Pattern 4: Design Review First

**Purpose**: Measure the effectiveness of mandatory design review before implementation

**Period**: 2025-11-09 ~ 2025-11-15 (Week 1)

---

## Metrics to Track

### 1. Design Review Compliance

**Metric**: Percentage of new features that went through design review

```bash
# Track: Did we do design review?
Total New Features: N
Design Reviews Done: M
Compliance Rate: M/N * 100%

Target: 100% for features >10 lines
Acceptable: 90% (allow 1-2 small exceptions)
Warning: <80%
```

### 2. Risk Detection Rate

**Metric**: Number of risks identified during design review

```yaml
Per Design Review:
  - Risks Found: [0-8]
  - Severity: [LOW, MEDIUM, HIGH, CRITICAL]
  - Mitigated Before Implementation: [Yes/No]

Success Indicator:
  - Average risks found: >2 per review
  - Mitigation rate: >90%
```

### 3. Post-Implementation Issues

**Metric**: Problems discovered AFTER implementation

```yaml
Before Pattern 4 (Historical):
  - Bugs found post-implementation: ~30%
  - Rollbacks needed: ~10%
  - Design changes needed: ~20%

After Pattern 4 (Target):
  - Bugs found post-implementation: <10%
  - Rollbacks needed: <3%
  - Design changes needed: <5%
```

### 4. Time Investment vs Savings

**Metric**: Design review time vs bug-fix time saved

```yaml
Time Breakdown:
  - Design review time: T_review (typically 15-30 min)
  - Bug fix time saved: T_saved (typically 60-120 min)

ROI: T_saved / T_review > 2.0 (200%)
Target: Save 2+ hours per hour invested in design review
```

---

## Data Collection

### Template: Design Review Record

Save to: `RUNS/pattern4_monitoring/design_review_YYYYMMDD_NN.yaml`

```yaml
design_review:
  date: "2025-11-09"
  feature: "Auth middleware enhancement"

  # 8 Risk Checks
  risks_found:
    - id: "risk_1"
      category: "Git conflict"
      severity: "MEDIUM"
      description: "Multi-session editing auth.py"
      mitigation: "File lock + session coordination"
      status: "mitigated"

    - id: "risk_2"
      category: "Performance"
      severity: "LOW"
      description: "Session start delay +0.2s"
      mitigation: "Lazy loading + caching"
      status: "mitigated"

  # Design Review Outcome
  review_time_minutes: 25
  risks_total: 3
  risks_mitigated: 3
  approved: true

  # Implementation Tracking
  implementation:
    started: "2025-11-09 14:30"
    completed: "2025-11-09 15:45"
    bugs_found: 0
    rollback_needed: false
```

### Template: Implementation Record

Save to: `RUNS/pattern4_monitoring/implementation_YYYYMMDD_NN.yaml`

```yaml
implementation:
  date: "2025-11-09"
  feature: "Auth middleware enhancement"
  design_review_done: true
  design_review_file: "design_review_20251109_01.yaml"

  # Post-Implementation Issues
  issues_found:
    - type: "bug"
      severity: "LOW"
      description: "Edge case not covered"
      found_at: "testing"
      time_to_fix_minutes: 10

  # Comparison
  expected_vs_actual:
    expected_risks: 3
    actual_issues: 1
    design_review_effectiveness: "67%"  # 2 out of 3 risks prevented
```

---

## Weekly Report Generation

### Command

```bash
python scripts/pattern4_impact_monitor.py --report
```

### Report Template

```markdown
# Pattern 4 Weekly Report: 2025-11-09 ~ 2025-11-15

## Summary

- Total Features: 5
- Design Reviews Done: 5 (100%)
- Total Risks Found: 12
- Risks Mitigated: 11 (92%)
- Post-Implementation Issues: 2 (17%)

## Metrics

### 1. Compliance Rate
- [OK] 100% compliance (5/5 features)

### 2. Risk Detection
- Average risks per review: 2.4
- [OK] Above target (>2.0)

### 3. Issue Prevention
- Before Pattern 4: ~30% post-impl issues (historical)
- After Pattern 4: 17% post-impl issues
- [OK] 43% reduction

### 4. Time ROI
- Total design review time: 120 minutes
- Total bug-fix time saved: 240 minutes
- ROI: 200% (2.0x)
- [OK] Above target (>2.0x)

## Decision

[GREEN] Pattern 4 is effective - CONTINUE

Rationale:
- 100% compliance
- 43% issue reduction
- 200% time ROI
- Team feedback: Positive

## Next Steps

- Continue monitoring Week 2
- Track long-term trends
- Refine risk checklist based on findings
```

---

## Automation Script

### Usage

```bash
# Record design review
python scripts/pattern4_impact_monitor.py --record-review \
  --feature "Auth middleware" \
  --time 25 \
  --risks 3 \
  --mitigated 3

# Record implementation
python scripts/pattern4_impact_monitor.py --record-impl \
  --feature "Auth middleware" \
  --bugs 0 \
  --rollback false

# Generate weekly report
python scripts/pattern4_impact_monitor.py --report
```

---

## Success Criteria

### Week 1 Goals

- [x] Baseline established (historical data: 30% post-impl issues)
- [ ] 5+ design reviews completed
- [ ] Compliance rate >90%
- [ ] Issue reduction >20%
- [ ] Time ROI >150%

### Long-term Goals (4 weeks)

- Compliance rate stabilizes at >95%
- Post-impl issues <10% (vs 30% historical)
- Time ROI >300% (proven effectiveness)
- Team adoption without resistance

---

## Emergency Procedures

### Rollback Triggers

- Compliance rate <50% (resistance to process)
- Post-impl issues INCREASE (not effective)
- Time ROI <100% (waste of time)

### Rollback Process

1. Document failure
2. Analyze root cause (process? checklist? enforcement?)
3. Decide: Modify process vs Remove Pattern 4
4. Update Constitution if needed

---

## References

- `config/constitution.yaml` - Pattern 4 definition
- `~/.claude/INNOVATION_SAFETY_PRINCIPLES.md` - Global Pattern 4
- `docs/PATTERN_PRIORITY_GUIDE.md` - Conflict resolution
- `scripts/pattern_sync_manager.py` - Consistency verification

---

**Version**: 1.0
**Created**: 2025-11-09
**Status**: Active Monitoring
