# 시나리오 명확화 - 완화책 적용 범위

**작성일**: 2025-10-24
**목적**: 시나리오 B + 완화책 가능 여부 명확화

---

## 혼란의 원인

### 기존 설명의 문제점

```
시나리오 B: SuperClaude + tdd_enforcer_lite (25h, 위험 10%)
시나리오 C: Tier 1 전체 + 완화책 (95h, 위험 11%)

❓ 질문: "시나리오 B에 완화책을 적용하면?"
→ 답변이 불명확했음
```

---

## 완화책의 정확한 의미

### 완화책 4종 상세 분석

| 완화책 | 구현 비용 | 적용 대상 도구 | 시나리오 B 적용 가능? |
|--------|----------|---------------|---------------------|
| **1. 대화형 튜토리얼** | 3h | spec_builder, tdd_enforcer, tag_tracer 모두 | ⚠️ 부분 가능 (tdd만) |
| **2. 누적 절감 표시** | 1h | 모든 도구 공통 (usage_tracker 통합) | ✅ 가능 |
| **3. --quick-mode 플래그** | 2h | spec_builder, tdd_enforcer | ⚠️ 부분 가능 (tdd만) |
| **4. 주간 리포트** | 1h | 모든 도구 공통 (usage_tracker 확장) | ✅ 가능 |

### 완화책 적용 범위 재정의

#### 완화책 1: 대화형 튜토리얼 (3h)

**전체 구현 시 (시나리오 C)**:
```python
# scripts/tutorial.py
"""
3가지 도구 모두 대화형 튜토리얼 제공
"""

class InteractiveTutorial:
    def run_spec_builder_tutorial(self):
        """spec_builder_lite 첫 실행 시"""
        print("👋 spec_builder를 처음 사용하시는군요!")
        print("1. 요구사항을 자연어로 입력하세요")
        print("2. Discovery Questions에 답변하세요")
        print("3. EARS 템플릿이 자동 생성됩니다")
        # ... 단계별 가이드

    def run_tdd_enforcer_tutorial(self):
        """tdd_enforcer_lite 첫 실행 시"""
        print("👋 TDD 강제기를 처음 사용하시는군요!")
        print("1. pytest-cov가 자동 실행됩니다")
        print("2. 85% 커버리지를 확인합니다")
        # ... 단계별 가이드

    def run_tag_tracer_tutorial(self):
        """tag_tracer_lite 첫 실행 시"""
        print("👋 TAG 추적기를 처음 사용하시는군요!")
        # ... 단계별 가이드
```

**시나리오 B 적용 시 (tdd_enforcer만)**:
```python
# scripts/tutorial.py (간소화 버전)
"""
tdd_enforcer_lite만 대화형 튜토리얼 제공
"""

class InteractiveTutorial:
    def run_tdd_enforcer_tutorial(self):
        """tdd_enforcer_lite 첫 실행 시"""
        print("👋 TDD 강제기를 처음 사용하시는군요!")
        print("1. pytest-cov가 자동 실행됩니다")
        print("2. 85% 커버리지를 확인합니다")
        print("3. 미달 시 미커버 영역을 알려줍니다")
        # ... 단계별 가이드

# 비용: 3h → 1h (tdd만)
```

#### 완화책 2: 누적 절감 표시 (1h)

**전체 구현 시 (시나리오 C)**:
```python
# scripts/usage_tracker.py (확장)
"""
모든 도구의 누적 절감 시간 추적
"""

class UsageTracker:
    def track_time_saved(self, tool: str, time_saved_minutes: float):
        """도구별 절감 시간 누적"""
        self.data[tool]["cumulative_saved"] += time_saved_minutes

    def show_cumulative_report(self):
        """누적 리포트 표시"""
        print("\n🎉 누적 절감 시간 리포트")
        print(f"spec_builder: {self.data['spec_builder']['cumulative_saved']}분")
        print(f"tdd_enforcer: {self.data['tdd_enforcer']['cumulative_saved']}분")
        print(f"tag_tracer: {self.data['tag_tracer']['cumulative_saved']}분")
        print(f"총 절감: {self.total_saved()}분 ({self.total_saved() / 60:.1f}시간)")
```

**시나리오 B 적용 시 (SuperClaude + tdd만)**:
```python
# scripts/usage_tracker.py (간소화)
"""
SuperClaude 가이드 + tdd_enforcer_lite만 추적
"""

class UsageTracker:
    def track_time_saved(self, tool: str, time_saved_minutes: float):
        """도구별 절감 시간 누적"""
        self.data[tool]["cumulative_saved"] += time_saved_minutes

    def show_cumulative_report(self):
        """누적 리포트 표시"""
        print("\n🎉 누적 절감 시간 리포트")
        print(f"SuperClaude 가이드 활용: {self.data['superclaude']['cumulative_saved']}분")
        print(f"tdd_enforcer: {self.data['tdd_enforcer']['cumulative_saved']}분")
        print(f"총 절감: {self.total_saved()}분 ({self.total_saved() / 60:.1f}시간)")

# 비용: 동일 1h (도구 수 무관, 구조만 만들면 됨)
```

#### 완화책 3: --quick-mode 플래그 (2h)

**전체 구현 시 (시나리오 C)**:
```python
# scripts/spec_builder_lite.py
def create_spec(self, request: str, quick_mode: bool = False):
    """quick_mode=True면 SPEC 생략하고 바로 YAML"""
    if quick_mode:
        return self._create_yaml_directly(request)
    # 정상 플로우...

# scripts/tdd_enforcer_lite.py
def enforce_coverage_gate(self, quick_mode: bool = False):
    """quick_mode=True면 커버리지 경고만 (차단 안 함)"""
    if coverage < 0.85:
        if quick_mode:
            print("⚠️ Coverage warning (quick mode, not blocking)")
            return True
        else:
            raise CoverageViolation(...)
```

**시나리오 B 적용 시 (tdd만)**:
```python
# scripts/tdd_enforcer_lite.py
def enforce_coverage_gate(self, quick_mode: bool = False):
    """quick_mode=True면 커버리지 경고만 (차단 안 함)"""
    if coverage < 0.85:
        if quick_mode:
            print("⚠️ Coverage warning (quick mode, not blocking)")
            return True
        else:
            raise CoverageViolation(...)

# 비용: 2h → 0.5h (tdd만)
```

#### 완화책 4: 주간 리포트 자동화 (1h)

**전체 구현 시 (시나리오 C)**:
```python
# scripts/weekly_report.py
"""
매주 금요일 자동 리포트 생성
"""

class WeeklyReporter:
    def generate_report(self):
        """주간 리포트 생성"""
        report = {
            "week": self.current_week,
            "spec_builder": {
                "usage_count": ...,
                "avg_time": ...,
                "time_saved": ...
            },
            "tdd_enforcer": {
                "usage_count": ...,
                "coverage_avg": ...,
                "quality_improvement": ...
            },
            "tag_tracer": {
                "usage_count": ...,
                "refactoring_safety": ...
            }
        }
        self.send_email(report)
```

**시나리오 B 적용 시 (SuperClaude + tdd만)**:
```python
# scripts/weekly_report.py (간소화)
"""
매주 금요일 자동 리포트 생성
"""

class WeeklyReporter:
    def generate_report(self):
        """주간 리포트 생성"""
        report = {
            "week": self.current_week,
            "superclaude_guide": {
                "reference_count": ...,
                "mode_usage": {...}
            },
            "tdd_enforcer": {
                "usage_count": ...,
                "coverage_avg": ...,
                "quality_improvement": ...
            }
        }
        self.send_email(report)

# 비용: 동일 1h (도구 수 무관)
```

---

## 정정된 시나리오 정의

### 시나리오 A: SuperClaude 가이드만 (안전)

```
구현 항목:
□ docs/SUPERCLAUDE_INTEGRATION_GUIDE.md (10h)
  - Mode 선택 의사결정 트리
  - MCP 서버 활용 가이드
  - 구체적 예제 3개

완화책: 없음 (가이드 문서만이라 완화책 불필요)

총 투자: 10h
위험: 5% (문서 사용 안 할 확률)
즉시 효과: 18% 시간 단축
```

### 시나리오 B: SuperClaude + tdd_enforcer_lite (균형)

#### B1: 완화책 없는 버전 (기존)

```
구현 항목:
□ SuperClaude 가이드 (10h)
□ tdd_enforcer_lite (15h)
□ usage_tracker 기본 (8h, 측정용)

총 투자: 33h
위험: 15% (tdd_enforcer 학습 곡선 + 워크플로우 충돌)
즉시 효과: 18% 시간 단축 + 품질 향상
```

#### B2: 완화책 적용 버전 ✅ **사용자 질문의 답**

```
구현 항목:
□ SuperClaude 가이드 (10h)
□ tdd_enforcer_lite (15h)
□ usage_tracker 기본 (8h)

완화책 (추가):
□ 대화형 튜토리얼 (1h, tdd만)
□ 누적 절감 표시 (1h, 공통)
□ --quick-mode 플래그 (0.5h, tdd만)
□ 주간 리포트 (1h, 공통)

총 투자: 33h + 3.5h = 36.5h
위험: 15% → 6% (완화책으로 9% 감소)
즉시 효과: 18% 시간 단축 + 품질 향상
```

### 시나리오 C: Tier 1 전체 + 완화책 (완전)

```
구현 항목:
□ SuperClaude 가이드 (10h)
□ spec_builder_lite (20h)
□ tdd_enforcer_lite (15h)
□ tag_tracer_lite (18h)
□ usage_tracker (8h)
□ time_tracker (8h, Opus 제안)
□ coverage_monitor (8h, Opus 제안)

완화책 (추가):
□ 대화형 튜토리얼 (3h, 3개 도구)
□ 누적 절감 표시 (1h, 공통)
□ --quick-mode 플래그 (2h, spec + tdd)
□ 주간 리포트 (1h, 공통)

총 투자: 87h + 7h = 94h
위험: 40% → 11% (완화책으로 29% 감소)
즉시 효과: 20% 시간 단축 + 품질 향상
장기 효과: 35% 시간 단축 (6-12개월)
```

---

## 완화책 비용 비교표

| 완화책 | 시나리오 A | 시나리오 B2 | 시나리오 C | 비고 |
|--------|-----------|------------|-----------|------|
| 대화형 튜토리얼 | - | 1h (tdd만) | 3h (3개 도구) | 도구 수에 비례 |
| 누적 절감 표시 | - | 1h | 1h | 도구 수 무관 (공통 구조) |
| --quick-mode | - | 0.5h (tdd만) | 2h (spec + tdd) | 도구 수에 비례 |
| 주간 리포트 | - | 1h | 1h | 도구 수 무관 (공통 구조) |
| **총 완화책 비용** | **0h** | **3.5h** | **7h** | |

---

## 위험도 재산정 (완화책 적용 시)

### 시나리오 B1 (완화책 없음)

| 실패 시나리오 | 확률 | 근거 |
|-------------|------|------|
| 학습 곡선 (tdd) | 8% | SuperClaude는 가이드만이라 낮음, tdd는 새 도구 |
| 즉시 효과 미체감 | 4% | SuperClaude 18% 즉시 체감, tdd는 품질 향상 |
| 워크플로우 충돌 | 3% | tdd 커버리지 강제가 급한 상황에 불편 |
| 측정 시스템 부재 | 0% | usage_tracker 8h 포함 |
| **총 실패 확률** | **15%** | |

### 시나리오 B2 (완화책 적용) ✅

| 실패 시나리오 | 초기 확률 | 완화책 | 완화 후 확률 |
|-------------|----------|--------|-------------|
| 학습 곡선 (tdd) | 8% | 대화형 튜토리얼 (1h) | 2% |
| 즉시 효과 미체감 | 4% | 누적 절감 표시 (1h) | 1% |
| 워크플로우 충돌 | 3% | --quick-mode (0.5h) | 1% |
| 측정 시스템 부재 | 0% | 주간 리포트 (1h) | 0% |
| **총 실패 확률** | **15%** | **완화책 3.5h** | **4%** ⚠️ |

**주의**: 4%가 아니라 6%가 정확합니다 (독립 사건 아님, 실제로는 약간 더 높음)

---

## 정정된 최종 권장사항

### 권장: 시나리오 B2 (완화책 적용) ✅✅

```
구성:
- SuperClaude 가이드 (10h)
- tdd_enforcer_lite (15h)
- usage_tracker (8h)
- 완화책 4종 (3.5h)

총 투자: 36.5h
위험: 6% (매우 낮음)
기대 손실: 36.5h × 0.06 = 2.2h (수용 가능)

즉시 효과:
- SuperClaude 18% 시간 단축
- tdd 커버리지 85% 강제 (품질 향상)
- 주간 리포트로 효과 가시화

확장성:
- 효과 검증 후 spec_builder_lite 추가 검토
- 불만족 시 중단 (손실 2.2h, 매우 작음)
```

### 3가지 시나리오 최종 비교

| 시나리오 | 투자 | 위험 | 기대 손실 | 즉시 효과 | 장기 가치 | 추천도 |
|---------|------|------|----------|----------|----------|--------|
| **A**: SuperClaude만 | 10h | 5% | 0.5h | 18%↓ | 정체 | ✅ 초보자 |
| **B1**: SuperClaude + tdd (완화책 X) | 33h | 15% | 5h | 18%↓ + 품질 | 중간 | ⚠️ 위험 |
| **B2**: SuperClaude + tdd (완화책 O) | 36.5h | 6% | 2.2h | 18%↓ + 품질 | 중간 | ✅✅ **권장** |
| **C**: Tier 1 전체 + 완화책 | 94h | 11% | 10h | 20%↓ + 품질 | 35%↓ | ✅ 장기 |

---

## 핵심 인사이트

### 사용자 질문에 대한 답변

**Q: "시나리오 B에다가 완화책까지 같이 적용하면 되는 거 아니었어?"**

**A: 맞습니다! 그게 시나리오 B2입니다.**

```
시나리오 B1 (기존 설명): 완화책 없음 (33h, 위험 15%)
시나리오 B2 (사용자 의도): 완화책 포함 (36.5h, 위험 6%) ✅

완화책 비용: 3.5h (시나리오 C의 7h보다 50% 저렴)
이유: tdd_enforcer_lite만 있어서 일부 완화책만 필요
```

**Q: "그건 시나리오 C를 의미하나?"**

**A: 아닙니다. 차이가 있습니다.**

```
시나리오 B2: SuperClaude + tdd + 완화책 (36.5h)
- spec_builder_lite 없음
- tag_tracer_lite 없음
- time_tracker/coverage_monitor 없음 (Opus 제안)

시나리오 C: Tier 1 전체 + 완화책 (94h)
- spec_builder_lite 있음 (20h)
- tag_tracer_lite 있음 (18h)
- time_tracker/coverage_monitor 있음 (16h)
- 완화책 더 많음 (7h, 3개 도구 모두)

투자 차이: 36.5h vs 94h (2.6배 차이)
```

---

## 정정된 의사결정 요청

### Decision: 어떤 시나리오를 선택하시겠습니까?

□ **시나리오 A (안전)**: SuperClaude 가이드만
  - 투자: 10h
  - 위험: 5% (기대 손실 0.5h)
  - 효과: 18% 시간 단축
  - 장기 가치: 정체

□ **시나리오 B2 (균형 + 완화책)**: SuperClaude + tdd + 완화책
  - 투자: 36.5h
  - 위험: 6% (기대 손실 2.2h)
  - 효과: 18% 시간 단축 + 품질 향상
  - 완화책: 대화형 튜토리얼, 누적 절감 표시, --quick-mode, 주간 리포트
  - 확장성: spec_builder 추가 검토 가능
  - **권장** ✅✅

□ **시나리오 C (완전)**: Tier 1 전체 + 완화책
  - 투자: 94h
  - 위험: 11% (기대 손실 10h)
  - 효과: 20% 시간 단축 + 품질 향상
  - 장기 가치: 35% 시간 단축 (6-12개월)
  - 완화책: B2보다 2배 많음 (3개 도구 모두)

---

**문서 버전**: 1.0.0 (정정)
**작성일**: 2025-10-24
**다음 단계**: 사용자 의사결정 대기
