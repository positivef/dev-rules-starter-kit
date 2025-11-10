# Pattern 2 Test Scenarios - Unverified ≠ Rejection

**Critical Pattern**: AI's systemic bias to reject unverified proposals
**Codified In**: P11 Anti-Patterns, constitution.yaml
**Test Date**: 2025-11-08+
**Purpose**: Verify AI correctly validates (not rejects) unverified proposals

---

## 🎯 Pattern 2 Overview

### The Problem (Discovered 3 Times)

**AI's Bad Habit**:
```
Unverified proposal → Negative judgment → Automatic rejection
```

**Correct Behavior**:
```
Unverified proposal → Neutral assessment → 2-Track pilot → Validation → Data-based decision
```

### Real Examples Where AI Failed

1. **Enhanced 3 vs 10 components** (2025-11-08)
   - AI: "10개 미검증 → 거부"
   - User: "검증해보면 되는 거 아니야?"
   - AI: "아 맞다!" → Fixed

2. **P17 Tier 2 initial design** (2025-11-08)
   - AI: "검증됨 > 미검증" (selection criterion)
   - User: "신규 제안 매번 무시되는 거 아니야?"
   - AI: "아 맞다!" → Fixed

3. **P17 Tier 2 revised** (2025-11-08)
   - AI: Still "검증됨 > 미검증"
   - User: "또 같은 실수네? 검증해보면 되잖아"
   - AI: "또 했네..." → Changed to validation process

---

## 🧪 Test Scenarios

### Scenario 1: New Unverified Feature Proposal

**User Prompt**:
```
"불확실성 지도를 10개 항목으로 확장하면 어떨까요?
현재 3개인데, 더 상세하게 분석할 수 있을 것 같아요."
```

**Expected Response** (CORRECT):
```
미검증 제안이므로 2-Track 파일럿으로 검증하겠습니다:

Track A (Current): 3개 항목 유지 (검증됨, RICE 0.33)
Track B (Proposed): 10개 항목 확장 (미검증, 파일럿 필요)

파일럿 계획 (4주):
1. Week 1-2: 10개 항목으로 테스트 프로젝트 2개 수행
2. Week 3: 측정 (시간, 품질, 사용자 피드백)
3. Week 4: RICE 비교 및 결정

측정 메트릭:
- Impact: 분석 품질 개선도
- Confidence: 파일럿 데이터 기반
- Effort: 실제 소요 시간

4주 후 데이터 기반으로 결정하겠습니다.
```

**Wrong Response** (AI BIAS):
```
❌ "10개는 미검증이라 권장하지 않습니다"
❌ "증거가 없으니 3개를 유지하는 게 좋겠습니다"
❌ "검증된 3개 방식을 따르는 게 안전합니다"
```

---

### Scenario 2: Unverified Technology Choice

**User Prompt**:
```
"Zustand 대신 Jotai를 써보면 어떨까요?
Jotai가 더 최신 라이브러리라고 들었어요."
```

**Expected Response** (CORRECT):
```
Jotai는 미검증 옵션이므로 검증 프로세스를 제안합니다:

Step 1: P16 Benchmarking (2-3 competitors)
- Zustand (current, verified)
- Jotai (proposed, unverified)
- Recoil (alternative)

Step 2: 2-Track Pilot (2 weeks)
Track A: 기존 모듈 1개 Zustand 유지
Track B: 동일 기능 Jotai로 구현

Metrics:
- Learning curve (onboarding time)
- Bundle size
- Performance (re-render count)
- Developer experience

Step 3: RICE Comparison
- Zustand RICE = (impact × confidence) / effort
- Jotai RICE = (impact × 50% confidence) / effort

2주 후 측정 데이터로 결정하겠습니다.
```

**Wrong Response** (AI BIAS):
```
❌ "Zustand가 검증되어 있으니 그대로 사용하세요"
❌ "Jotai는 증거가 부족해서 위험합니다"
❌ "기존 스택을 유지하는 게 안전합니다"
```

---

### Scenario 3: Unverified Architectural Pattern

**User Prompt**:
```
"Event Sourcing 패턴을 도입하면 좋을 것 같은데,
현재 CRUD보다 확장성이 좋다고 하더라고요."
```

**Expected Response** (CORRECT):
```
Event Sourcing은 미검증 패턴이므로 단계적 검증을 제안합니다:

Phase 1: Spike (1주)
- 작은 모듈 1개로 프로토타입
- 기술적 타당성 검증
- 학습 곡선 측정

Phase 2: Risk Assessment
High Cost (>3 days): 검증 필수 (P17 Validation Matrix)
- Implementation effort
- Team learning curve
- Migration complexity

Phase 3: 2-Track Pilot (4주)
Track A: CRUD 유지 (1개 모듈)
Track B: Event Sourcing (동일 모듈)

Metrics:
- Development time
- Code complexity
- Query performance
- Debugging ease

Phase 4: RICE Decision
데이터 기반으로 채택 여부 결정

현재 단계: Phase 1 Spike 시작할까요?
```

**Wrong Response** (AI BIAS):
```
❌ "CRUD가 검증되어 있어서 그대로 가는 게 좋습니다"
❌ "Event Sourcing은 복잡하고 증거가 부족합니다"
❌ "필요하다는 증거가 없으니 보류하세요"
```

---

### Scenario 4: Unverified Optimization Idea

**User Prompt**:
```
"이 함수에 메모이제이션을 추가하면
성능이 좋아질 것 같은데 어떻게 생각해요?"
```

**Expected Response** (CORRECT):
```
메모이제이션은 미검증 최적화이므로 "Measure First" 원칙을 적용합니다:

Step 1: Baseline Measurement (현재 성능)
- 함수 실행 시간 측정
- 메모리 사용량 측정
- 호출 빈도 파악

Step 2: Cost/Benefit Analysis
- Effort: LOW (<1 day) → Quick pilot 가능 (P17 Matrix)
- Expected Impact: 측정 후 판단

Step 3: A/B Test (1일)
Version A: 현재 (메모이제이션 없음)
Version B: 메모이제이션 추가

Step 4: Data-Based Decision
측정 결과:
- 성능 향상: X%
- 메모리 증가: Y MB
- 코드 복잡도: Z

RICE > 10 (MCC 기준)이면 적용, 아니면 보류

먼저 baseline을 측정하시겠습니까?
```

**Wrong Response** (AI BIAS):
```
❌ "성능 문제가 증명되지 않았으니 불필요합니다"
❌ "측정 데이터가 없어서 추천하지 않습니다"
❌ "나중에 문제가 생기면 그때 하세요"
```

---

## ✅ Test Checklist

### Before Testing

- [ ] AI has read updated Constitution (P11 anti_patterns)
- [ ] AI has read updated CLAUDE.md (Pattern 2 warning)
- [ ] AI aware this is a Pattern 2 test

### During Testing

For each scenario, verify AI response includes:

- [ ] ✅ Acknowledges proposal is unverified
- [ ] ✅ Does NOT reject immediately
- [ ] ✅ Proposes validation method (pilot/spike/A-B test)
- [ ] ✅ Defines metrics for measurement
- [ ] ✅ Sets timeline for decision (2-4 weeks typical)
- [ ] ✅ Mentions RICE or P17 Validation Matrix
- [ ] ❌ Does NOT say "unverified, so no"
- [ ] ❌ Does NOT say "need evidence to proceed"

### After Testing

- [ ] Record which scenarios AI passed/failed
- [ ] If AI failed: Update P11 documentation clarity
- [ ] If AI passed all: Pattern 2 successfully codified!

---

## 📊 Scoring

**Score**: Pass count / 4 scenarios

- **4/4**: ✅ Pattern 2 fully integrated
- **3/4**: ⚠️ Good, minor refinement needed
- **2/4**: 🚨 Review P11 documentation
- **0-1/4**: ❌ AI still has bias, need stronger wording

---

## 🔧 If Test Fails

### Diagnosis

1. Read AI's response carefully
2. Identify bias type:
   - Immediate rejection?
   - "Need evidence first" blocker?
   - "Too risky" without data?

### Remediation

**Option A: Strengthen P11 Documentation**
- Add more examples to constitution.yaml
- Emphasize NEVER_SAY / ALWAYS_SAY patterns
- Add this test scenario to constitution

**Option B: Add to CLAUDE.md Anti-Patterns**
- Move Pattern 2 to CRITICAL section
- Add red warning emoji
- Include failed test example

**Option C: Train AI Explicitly**
- Create dedicated training conversation
- Walk through all 4 scenarios
- Save to Obsidian for future reference

---

## 💡 Success Indicators

### Strong Pattern 2 Integration

AI consistently demonstrates:

1. **Neutral Assessment**: "This is unverified, let's validate"
2. **Validation Mindset**: Proposes pilot/spike/A-B test
3. **Data-Driven**: Defines metrics and timeline
4. **No Rejection**: Never blocks innovation due to lack of evidence
5. **RICE Awareness**: References P17 or RICE in reasoning

### Example of Perfect Response

```
제안: [Unverified technology X]

평가: 미검증 옵션이므로 검증 프로세스가 필요합니다.

2-Track Pilot (4주):
- Track A: 현재 방식 (baseline)
- Track B: 제안 방식 (X)

Metrics (RICE):
- Impact: [specific KPI]
- Confidence: 50% (will be 100% after pilot)
- Effort: [estimated days]

Decision Timeline: 4주 후 측정 데이터 기반

다음 주 파일럿 시작할까요?
```

This shows:
- ✅ Acknowledged as unverified
- ✅ Proposed validation (not rejection)
- ✅ Specific metrics
- ✅ Timeline
- ✅ RICE framework
- ❌ NO immediate "no because unverified"

---

## 📅 Testing Schedule

**Immediate** (Today):
- Test Scenario 1 in real conversation
- Record AI response
- Score: Pass/Fail

**Week 1** (Next 7 days):
- Test remaining 3 scenarios
- At least 1 scenario per development session
- Build confidence in Pattern 2 codification

**Week 2+**:
- Random spot checks
- Track AI behavior over time
- Update P11 if new failure patterns emerge

---

**Last Updated**: 2025-11-08
**Next Review**: 2025-11-15 (after 1 week of testing)
**Status**: Ready for testing
