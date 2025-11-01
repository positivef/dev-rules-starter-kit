# Hybrid Error Resolution - Quick Start Guide

**버전**: v3.0
**소요 시간**: 5분
**난이도**: 초급

## 🚀 5분 Quick Start

### 1단계: 기본 사용법 (1분)

```python
from scripts.unified_error_resolver import UnifiedErrorResolver

# 1. Resolver 초기화
resolver = UnifiedErrorResolver()

# 2. 에러 해결 시도
solution = resolver.resolve_error(
    error_msg="ModuleNotFoundError: No module named 'pandas'",
    context={"tool": "Python", "script": "app.py"}
)

# 3. 결과 처리
if solution:
    print(f"✅ 자동 해결: {solution}")
    # 솔루션 적용 (예: subprocess.run(solution.split()))
else:
    print("❓ 사용자 확인 필요")
    # MEDIUM/LOW confidence - 사용자에게 물어봄
```

### 2단계: 실제 테스트 (2분)

```bash
# 테스트 실행
python scripts/test_hybrid_quick.py

# 예상 출력:
# [TIER 1] Obsidian 검색... (없음)
# [TIER 2] Context7 검색... pip install pandas
# [TIER 2 AUTO] High confidence (100%), auto-applying...
# ✅ Auto-fixed from official docs
```

### 3단계: 통계 확인 (1분)

```python
# 통계 조회
stats = resolver.get_statistics()

print(f"총 해결: {stats['total']}")
print(f"Tier 1 (Obsidian): {stats['tier1']} ({stats['tier1_percentage']:.0%})")
print(f"Tier 2 AUTO: {stats['tier2_auto']}")
print(f"자동화율: {stats['automation_rate']:.0%}")
```

### 4단계: 설정 커스터마이징 (1분)

```yaml
# config/error_resolution_config.yaml 편집

# 임계값 조정 (기본값: 95%)
confidence_thresholds:
  auto_apply: 0.95  # 더 보수적으로: 0.98, 더 적극적으로: 0.90

# Circuit breaker 설정
circuit_breaker:
  enabled: true
  max_failures: 3  # 실패 허용 횟수
```

---

## 📝 실전 시나리오

### 시나리오 1: Python 패키지 설치 (AUTO)

```python
# 에러 발생
error = "ModuleNotFoundError: No module named 'requests'"

# 자동 해결
solution = resolver.resolve_error(error, {"tool": "Python"})
# → "pip install requests" (HIGH confidence, 자동 적용)

# 결과
# ✅ [TIER 2 AUTO] pip install requests 실행됨
# ✅ 다음번엔 Tier 1 (Obsidian)에서 <10ms에 해결
```

### 시나리오 2: 설정 변경 (CONFIRM)

```python
# 에러 발생
error = "ImportError: cannot import name 'SpecialClass' from 'mymodule'"

# MEDIUM confidence
solution = resolver.resolve_error(error, {"tool": "Python"})
# → None (사용자 확인 필요)

# AI가 사용자에게 물어봄:
# "Context7 제안: pip install mymodule==2.0.0"
# "적용할까요? (y/n/edit)"

# 사용자 확인 후 저장
if user_confirms:
    resolver.save_user_solution(error, "pip install mymodule==2.0.0", context)
    # → 다음번엔 Tier 1에서 즉시 해결
```

### 시나리오 3: 비즈니스 로직 (USER)

```python
# 에러 발생
error = "CustomBusinessError: Payment validation failed"

# LOW confidence
solution = resolver.resolve_error(error, {"tool": "Python"})
# → None (자동화 불가능)

# AI가 사용자에게 물어봄:
# "자동 해결 불가능합니다. 어떻게 하시겠습니까?"

# 사용자 솔루션 입력 후 저장
user_solution = "Check payment gateway config in .env"
resolver.save_user_solution(error, user_solution, context)
# → 다음번엔 Tier 1에서 즉시 해결
```

---

## 🔧 고급 사용법

### Circuit Breaker 테스트

```python
# 실패 기록
resolver.circuit_breaker.record_auto_apply(False)
resolver.circuit_breaker.record_auto_apply(False)
resolver.circuit_breaker.record_auto_apply(False)

# 상태 확인
if not resolver.circuit_breaker.is_auto_apply_allowed():
    print("⚠️ Circuit breaker 활성화: 자동 적용 일시 중단")
    # → 모든 솔루션이 사용자 확인 요청으로 전환됨
```

### 신뢰도 계산 직접 사용

```python
from scripts.confidence_calculator import ConfidenceCalculator

calc = ConfidenceCalculator()

# 신뢰도 계산
confidence, explanation = calc.calculate(
    error_msg="ModuleNotFoundError: No module named 'pandas'",
    solution="pip install pandas",
    context={"tool": "Python"}
)

print(f"신뢰도: {confidence:.0%}")
print(f"레벨: {explanation.level}")
print(f"계산 근거:\n{explanation}")

# 출력 예시:
# 신뢰도: 100%
# 레벨: ConfidenceLevel.HIGH
# 계산 근거:
#   Base score: 85%
#   +10%: Whitelisted safe pattern
#   +5%: Simple single command
```

### 설정별 비교

```python
# 시나리오 A: 보수적 설정 (기본값)
# auto_apply: 0.95, ask_confirm: 0.70
# → HIGH: 자동 / MEDIUM: 확인 / LOW: 사용자

# 시나리오 B: 적극적 설정
# auto_apply: 0.90, ask_confirm: 0.60
# → 더 많은 솔루션이 자동 적용됨

# 시나리오 C: 비활성화
# auto_apply: 1.0
# → 모든 솔루션이 사용자 확인 필요
```

---

## 🛡️ 안전하게 사용하기

### 1. 블랙리스트 확인

```yaml
# config/error_resolution_config.yaml

always_confirm_patterns:
  - "sudo"          # 절대 자동 적용 안 됨
  - "rm -rf"        # 절대 자동 적용 안 됨
  - "database"      # 항상 사용자 확인
  - "payment"       # 항상 사용자 확인
  - "auth"          # 항상 사용자 확인
```

### 2. 화이트리스트 확장

```yaml
# 안전한 패턴 추가
auto_apply_patterns:
  - "pip install mypackage"  # 회사 내부 패키지
  - "npm install @company/*" # 회사 스코프 패키지
```

### 3. Progressive Enhancement

```yaml
# Week 1 → Week 2로 이동 시
confidence_thresholds:
  auto_apply: 0.92  # 95% → 92%
  ask_confirm: 0.65 # 70% → 65%

# 조건: 정확도 >90% 달성 필요
# 모니터링: RUNS/confidence_metrics.json 확인
```

### 4. 긴급 롤백

```yaml
# 방법 1: 완전 비활성화
mode: "simple"

# 방법 2: 자동 적용만 비활성화
confidence_thresholds:
  auto_apply: 1.0  # 불가능한 임계값

# 방법 3: Circuit breaker 비활성화
circuit_breaker:
  enabled: false
```

---

## 📊 모니터링

### 통계 파일 확인

```bash
# 의사결정 로그
cat RUNS/confidence_decisions.log

# 메트릭 확인
cat RUNS/confidence_metrics.json

# 에비던스 확인
ls RUNS/evidence/
```

### Obsidian 동기화 확인

```bash
# Obsidian vault에 솔루션 저장 확인
ls "$OBSIDIAN_VAULT_PATH/지식베이스/에러해결/"

# MOC 업데이트 확인
cat "$OBSIDIAN_VAULT_PATH/MOC/에러해결-MOC.md"
```

---

## 🔍 Troubleshooting

### Q1: "Circuit breaker 활성화되었어요"

```bash
# 원인: 3번 연속 실패
# 해결:
1. 실패 원인 분석: RUNS/confidence_decisions.log 확인
2. 블랙리스트 추가: config/error_resolution_config.yaml
3. Circuit breaker 리셋: resolver.circuit_breaker.reset()
```

### Q2: "MEDIUM confidence가 너무 많아요"

```bash
# 원인: 임계값이 너무 높음
# 해결:
# config/error_resolution_config.yaml 편집
confidence_thresholds:
  auto_apply: 0.92  # 95% → 92%로 낮춤
```

### Q3: "Tier 1 hit rate가 낮아요"

```bash
# 원인: 아직 학습 초기 단계
# 해결:
1. 계속 사용 (자동으로 Obsidian에 저장됨)
2. 수동으로 솔루션 추가:
   resolver.save_user_solution(error, solution, context)
3. 2-3주 후 70% 도달
```

---

## 🎯 Next Steps

1. **Week 1**: 기본 사용 + 모니터링
2. **Week 2**: 통계 확인 + 임계값 조정 (정확도 >90% 달성 시)
3. **Week 3**: 화이트리스트 확장 + 커스텀 패턴 추가
4. **Week 4**: 최종 임계값 도달 (90%)

---

**문서 업데이트**: 2025-11-01
**다음 리뷰**: 2025-12-01 (1개월 후)
