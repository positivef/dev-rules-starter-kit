# Design Review: [Feature Name]

**Date**: YYYY-MM-DD
**Reviewer**: [Your Name]
**Feature**: [Brief description]
**Status**: Draft / In Review / Approved / Rejected

---

## 1. Feature Overview

**Goal**: [What problem does this solve?]

**Scope**:
- [In scope item 1]
- [In scope item 2]

**Out of Scope**:
- [Out of scope item 1]
- [Out of scope item 2]

**Success Criteria**:
- [Criterion 1]
- [Criterion 2]

---

## 2. Uncertainty Map Analysis

**Map Type**: [ ] 3-Item (Default) [ ] 10-Item (High-risk)

**Rationale for Map Choice**:
- Risk level: Low / Medium / High
- Domain knowledge: Known / Unknown
- Time available: [X] minutes

---

### 3-Item Uncertainty Map

*Use this section if you chose 3-Item Map*

#### 2.1 Known Knowns (90% Confidence)

**Technologies/Patterns We Know Work**:
- [Technology 1]
- [Pattern 1]

**What We Know**:
- [Fact 1]
- [Fact 2]

**Action**: Implement with standard process

---

#### 2.2 Known Unknowns (60% Confidence)

**Uncertain Areas**:

**Risk Area 1**: [Name]
- Question: [What don't we know?]
- Impact: Low / Medium / High
- Mitigation: [How to reduce risk?]

**Risk Area 2**: [Name]
- Question: [What don't we know?]
- Impact: Low / Medium / High
- Mitigation: [How to reduce risk?]

**Risks Found**: [N] major risks

**Action**: 2-Track pilot / Validation / PoC needed

---

#### 2.3 Unknown Unknowns (30% Confidence)

**Potential Surprises**:
- [Surprise scenario 1]
- [Surprise scenario 2]

**Action**: Progressive rollout + monitoring

---

**Summary**:
- Time spent: [X] minutes
- Risks identified: [N]
- Decision confidence: [1-5] / 5
- Proceed? [ ] Yes [ ] No [ ] More analysis needed

---

### 10-Item Uncertainty Map (Optional)

*Use this section if you chose 10-Item Map*

See `docs/UNCERTAINTY_MAP_10_ITEMS.md` for full template.

**Tier 1: Known Territory** (70-100% Confidence)
1. Fully Validated (95%): [Items]
2. Mostly Validated (80%): [Items]

**Tier 2: Partial Knowledge** (40-70% Confidence)
3. Partially Validated (65%): [Items]
4. Theoretically Sound (55%): [Items]
5. Educated Guess (45%): [Items]

**Tier 3: Unknown Territory** (10-40% Confidence)
6. Speculative (35%): [Items]
7. Highly Uncertain (25%): [Items]
8. Mostly Unknown (15%): [Items]

**Tier 4: Unknown Unknowns** (0-10% Confidence)
9. Known Unknowns (7%): [Items]
10. Unknown Unknowns (2%): [Items]

**PoC Needs**:
- [PoC 1]: [X] days
- [PoC 2]: [X] days

---

## 3. Pattern 4: 8-Risk Checklist

*Mandatory for all features*

### 3.1 기존 시스템 영향 (Impact on Existing Systems)

**Systems Affected**:
- [System 1]
- [System 2]

**Impact Assessment**:
- Breaking changes? [ ] Yes [ ] No
- Backward compatibility? [ ] Yes [ ] No
- Migration needed? [ ] Yes [ ] No

**Mitigation**:
- [Mitigation strategy]

---

### 3.2 Git Conflict (Repository Conflicts)

**Files to be Modified**:
- [File 1]
- [File 2]

**Conflict Risk**:
- Lock file needed? [ ] Yes [ ] No
- Multi-session risk? [ ] Yes [ ] No

**Mitigation**:
- [Strategy to avoid conflicts]

---

### 3.3 Multi-Session Coordination

**Concurrent Work Risk**:
- Other AI sessions active? [ ] Yes [ ] No
- File locking needed? [ ] Yes [ ] No

**Coordination Plan**:
- [How to coordinate]

---

### 3.4 Performance Impact

**Expected Impact**:
- Execution time: [+/- X%]
- Memory usage: [+/- X MB]
- Disk I/O: [+/- X operations]

**Threshold**:
- Target: < [X seconds / X MB / X ops]
- Red line: > [X seconds / X MB / X ops]

**Mitigation**:
- [Performance optimization strategy]

---

### 3.5 Complexity Increase

**Current Complexity**: [Low / Medium / High]
**After Change**: [Low / Medium / High]

**Metrics**:
- Lines of code: [+/- X]
- Cyclomatic complexity: [+/- X]
- Dependencies: [+/- X]

**Simplification Opportunities**:
- [How to keep it simple]

---

### 3.6 Workflow Disruption

**User Workflows Affected**:
- [Workflow 1]
- [Workflow 2]

**Disruption Level**: Low / Medium / High

**Migration Plan**:
- [How to transition users]
- Training needed? [ ] Yes [ ] No

---

### 3.7 Rollback Strategy

**Tier 1 (Immediate)**: < 10 seconds
- [ ] Strategy: [How to rollback immediately]

**Tier 2 (Fast)**: < 1 minute
- [ ] Strategy: [How to rollback quickly]

**Tier 3 (Standard)**: < 5 minutes
- [ ] Strategy: [Standard rollback procedure]

**Data Safety**:
- State preserved? [ ] Yes [ ] No
- Backup needed? [ ] Yes [ ] No

---

### 3.8 Test Coverage

**Test Types Needed**:
- [ ] Unit tests (target: 80% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance tests
- [ ] Security tests

**Test Plan**:
- [What to test]
- [How to test]
- [Expected coverage: X%]

---

## 4. Safety Mechanisms

### 4.1 Fail-Safe Defaults

**Default Behavior**:
- [Safe default 1]
- [Safe default 2]

**Failure Mode**:
- What happens if feature fails? [Description]
- Graceful degradation? [ ] Yes [ ] No

---

### 4.2 Idempotency

**Operations**:
- [Operation 1]: Idempotent? [ ] Yes [ ] No
- [Operation 2]: Idempotent? [ ] Yes [ ] No

**Retry Safety**:
- Safe to retry? [ ] Yes [ ] No
- Max retries: [N]

---

### 4.3 Read-Only Mode

**Read-Only Operations**:
- [List read-only operations]

**Write Operations**:
- [List write operations with validation]

**Validation**:
- Pre-write validation? [ ] Yes [ ] No

---

### 4.4 State Separation

**Persistent State**:
- [What state is saved?]
- Location: [Where?]

**Temporary State**:
- [What state is temporary?]
- Cleanup: [How to cleanup?]

**Isolation**:
- Isolated from other features? [ ] Yes [ ] No

---

## 5. Implementation Plan

### 5.1 Phases

**Phase 1: Foundation** (X days)
- [ ] Task 1
- [ ] Task 2

**Phase 2: Core Feature** (X days)
- [ ] Task 1
- [ ] Task 2

**Phase 3: Testing & Rollout** (X days)
- [ ] Task 1
- [ ] Task 2

---

### 5.2 Dependencies

**Requires**:
- [Dependency 1]
- [Dependency 2]

**Blocks**:
- [What this blocks]

---

### 5.3 RICE Scoring

**Impact**: [0.25 / 0.5 / 1.0 / 2.0 / 3.0]
- Rationale: [Why this score?]

**Confidence**: [50% / 80% / 100%]
- Rationale: [Validation status]

**Effort**: [1 / 2 / 3 / 5 / 8 / 13 / 21] person-days
- Breakdown: [How calculated?]

**RICE Score**: (Impact × Confidence) / Effort = **[Score]**

**Priority**: Low / Medium / High / Critical

---

## 6. Approval

### 6.1 Risks Summary

**Total Risks Identified**: [N]

**High-Priority Risks**:
1. [Risk 1]
2. [Risk 2]

**All Risks Mitigated**: [ ] Yes [ ] No

---

### 6.2 Go/No-Go Decision

**Decision**: [ ] APPROVED [ ] REJECTED [ ] NEEDS REVISION

**Rationale**:
- [Why approved/rejected?]

**Conditions** (if conditional approval):
- [ ] Condition 1
- [ ] Condition 2

---

### 6.3 Sign-Off

**Reviewer**: [Name]
**Date**: YYYY-MM-DD
**Signature**: [Initials]

---

## Appendix A: References

**Related Documents**:
- [Document 1]
- [Document 2]

**Constitution Articles**:
- P4 (SOLID)
- P5 (Security)
- P11 Pattern 4 (Design Review First)

**Guides**:
- docs/UNCERTAINTY_MAP_GUIDE.md
- docs/UNCERTAINTY_MAP_10_ITEMS.md

---

## Appendix B: Decision Log

**Version History**:

**v1.0** (YYYY-MM-DD):
- Initial design review
- Uncertainty map: [3-item / 10-item]
- Decision: [Approved / Rejected]

**v1.1** (YYYY-MM-DD):
- [Changes made]
- [Rationale]

---

**Template Version**: 1.0
**Last Updated**: 2025-11-09
**Source**: Dev-Rules-Starter-Kit Constitution P11 Pattern 4

**Usage**:
1. Copy this template to `docs/[FEATURE]_DESIGN_REVIEW.md`
2. Fill in all sections (don't skip!)
3. Choose uncertainty map (3-item or 10-item)
4. Complete 8-risk checklist
5. Get user approval before implementation

**Related**:
- Pattern 4: Design Review First (config/constitution.yaml:706-759)
- Uncertainty Map Guide (docs/UNCERTAINTY_MAP_GUIDE.md)
- Pattern 2: Unverified ≠ Rejection (validated 2025-11-09)
