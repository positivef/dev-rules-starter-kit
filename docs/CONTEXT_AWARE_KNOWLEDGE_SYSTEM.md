# 컨텍스트 보존형 지식 시스템 (Context-Aware Knowledge System)

## 🚨 이전 설계의 문제점

### 극단적 압축의 부작용

#### 문제 1: 맥락 손실로 인한 오판

**나쁜 예 (과도한 압축)**:
```markdown
💻 pytest tests/ --cov=src
✅ 95%
```

**AI가 놓치는 것**:
- ❌ **언제** 이 명령어를 써야 하는가?
- ❌ **왜** coverage가 중요한가?
- ❌ **어떤 상황**에서 실패했었는가?
- ❌ **무엇을** 조심해야 하는가?

**결과**: AI가 부적절한 상황에서 이 명령어를 제안할 수 있음!

#### 문제 2: 학습 맥락 누락

**압축된 버전**:
```markdown
⚠️ auth.py 에러 → ✅ 테스트 추가
```

**AI가 이해하지 못하는 것**:
- ❌ 어떤 종류의 에러였나?
- ❌ 왜 테스트 추가가 해결책이었나?
- ❌ 다음에 비슷한 에러를 어떻게 예방할까?

**결과**: AI가 패턴을 학습하지 못하고 같은 실수 반복!

#### 문제 3: 의존성 정보 손실

**압축**:
```markdown
💻 npm run build
```

**누락된 중요 정보**:
- ❌ Node 버전 제약
- ❌ 환경 변수 필요 여부
- ❌ 선행 작업 (npm install 등)
- ❌ 실패 시 대처법

**결과**: AI가 제안했지만 실행 실패!

---

## 🎯 올바른 접근: 적응형 상세도 (Adaptive Detail)

### 핵심 원칙

**압축 vs 컨텍스트 트레이드오프를 AI가 상황에 따라 조절**

```python
상세도 = f(
    작업_복잡도,      # 복잡할수록 더 상세히
    에러_빈도,        # 자주 실패하면 더 상세히
    학습_단계,        # 초보일수록 더 상세히
    사용_빈도         # 자주 쓰면 압축 가능
)
```

---

## 📐 3-Level 상세도 시스템

### Level 1: Quick Reference (토큰 효율 우선)

**사용 조건**:
- ✅ 이미 5회 이상 사용한 명령어
- ✅ 에러 없이 성공한 적 있음
- ✅ 표준 환경에서 실행

**형식**:
```markdown
## [Quick] pytest 실행

💻 `pytest tests/ --cov=src --cov-report=html`

✅ 마지막 성공: 2025-11-02
📊 사용 횟수: 15회
⚠️ 주의: 가상환경 활성화 필요

🔗 상세: [[Testing-Guide#pytest-coverage]]
```

**토큰**: ~100 (압축)
**컨텍스트**: 최소 (링크로 보완)

---

### Level 2: Standard Context (균형)

**사용 조건**:
- ✅ 2-4회 사용
- ⚠️ 1-2회 실패 경험 있음
- ✅ 일반적인 작업

**형식**:
```markdown
## [Standard] pytest 실행

### 💻 실행 명령어
```bash
# 1. 가상환경 활성화 (필수)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 2. 테스트 + 커버리지
pytest tests/ --cov=src --cov-report=html

# 3. 결과 확인
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

### 📋 컨텍스트
- **목적**: 코드 품질 확인 + 테스트 커버리지 측정
- **시점**: PR 생성 전, 리팩토링 후
- **성공 조건**: 모든 테스트 통과 + 커버리지 ≥ 80%

### ⚠️ 주의사항
- 가상환경 미활성화 시 글로벌 패키지 사용 (위험)
- Windows에서 경로 이슈 가능 → 절대 경로 사용

### 🔧 트러블슈팅
- `ModuleNotFoundError` → `pip install -r requirements.txt`
- 느린 실행 → `-n auto` (병렬 실행)

### 📊 히스토리
- 사용 횟수: 15회
- 성공률: 93% (14/15)
- 마지막 실패: 2025-10-28 (의존성 누락)

🔗 상세: [[Testing-Guide#pytest-coverage]]
```

**토큰**: ~400 (균형)
**컨텍스트**: 충분 (단독 실행 가능)

---

### Level 3: Full Context (컨텍스트 우선)

**사용 조건**:
- ❌ 처음 사용하는 명령어
- ❌ 실패율 > 30%
- ❌ 복잡한 설정 필요
- ❌ 환경 의존성 높음

**형식**:
```markdown
## [Full] pytest 실행 (Complete Guide)

### 🎯 목적 및 배경

**왜 pytest인가?**
- Python 표준 unittest보다 간결한 문법
- 강력한 fixture 시스템
- 풍부한 플러그인 생태계
- 병렬 실행 지원 (pytest-xdist)

**언제 사용하는가?**
- PR 생성 전 필수 체크
- 리팩토링 후 회귀 테스트
- CI/CD 파이프라인에서 자동 실행
- 로컬 개발 중 수시 확인

### 🔧 사전 준비

#### 1. 환경 설정
```bash
# Python 3.8+ 필수
python --version  # 확인

# 가상환경 생성 (프로젝트당 1회)
python -m venv .venv

# 활성화 (매 세션마다)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest 포함
```

#### 2. 설정 파일 확인
```ini
# pytest.ini (프로젝트 루트)
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### 💻 실행 명령어 (단계별)

#### 기본 실행
```bash
# 모든 테스트
pytest

# 특정 디렉토리
pytest tests/unit/

# 특정 파일
pytest tests/test_auth.py

# 특정 테스트 함수
pytest tests/test_auth.py::test_login_success
```

#### 커버리지 측정
```bash
# HTML 리포트 생성
pytest --cov=src --cov-report=html

# 터미널에서 바로 확인
pytest --cov=src --cov-report=term-missing

# 커버리지 최소 기준 설정
pytest --cov=src --cov-fail-under=80
```

#### 병렬 실행 (빠른 실행)
```bash
# CPU 코어 수만큼 자동 분산
pytest -n auto

# 특정 워커 수 지정
pytest -n 4
```

#### 디버깅 모드
```bash
# 실패 시 즉시 중단
pytest -x

# 상세 출력
pytest -v

# 로그 출력 포함
pytest -s

# 조합
pytest -xvs tests/test_auth.py
```

### 📊 출력 해석

#### 성공 예시
```
tests/test_auth.py::test_login_success PASSED          [ 50%]
tests/test_auth.py::test_logout PASSED                 [100%]

---------- coverage: platform linux, python 3.9.7 -----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/auth.py             50      2    96%   45-46
src/utils.py            20      0   100%
--------------------------------------------------
TOTAL                   70      2    97%

============= 2 passed in 0.42s =============
```

#### 실패 예시 및 대응
```
tests/test_auth.py::test_login_fail FAILED             [ 50%]
...
AssertionError: Expected 401, got 200

해결:
1. 테스트 코드 확인: 예상값이 맞는가?
2. 구현 확인: 실제 로직이 올바른가?
3. Mock 확인: 의존성이 제대로 mocked 되었나?
```

### ⚠️ 주의사항 및 함정

#### 1. 가상환경 미활성화
**증상**: `ModuleNotFoundError` 연발
**원인**: 글로벌 Python 환경 사용
**해결**:
```bash
which python  # /path/to/.venv/bin/python 확인
.venv\Scripts\activate  # 재활성화
```

#### 2. Windows 경로 이슈
**증상**: `FileNotFoundError` with backslash
**원인**: Windows 경로 구분자 `\` vs Unix `/`
**해결**:
```python
from pathlib import Path  # 권장
path = Path("tests") / "fixtures" / "data.json"

# 또는
import os
path = os.path.join("tests", "fixtures", "data.json")
```

#### 3. 느린 테스트 실행
**증상**: 1분+ 소요
**원인**: 직렬 실행, 무거운 fixture
**해결**:
```bash
# 병렬 실행
pytest -n auto

# 느린 테스트 식별
pytest --durations=10

# 특정 테스트만 스킵
@pytest.mark.slow
def test_heavy_computation():
    ...

pytest -m "not slow"  # 느린 테스트 제외
```

#### 4. 캐시 문제
**증상**: 코드 변경했는데 테스트 결과 동일
**원인**: pytest 캐시
**해결**:
```bash
# 캐시 클리어
pytest --cache-clear

# 캐시 사용 안 함
pytest -p no:cacheprovider
```

### 🔧 트러블슈팅 플레이북

| 에러 | 원인 | 해결책 |
|------|------|--------|
| `ModuleNotFoundError: pytest` | pytest 미설치 | `pip install pytest` |
| `No tests ran` | 테스트 파일 명명 규칙 위반 | `test_*.py` 또는 `*_test.py` |
| `fixture not found` | fixture import 누락 | `conftest.py` 확인 |
| `AssertionError` | 테스트 로직 오류 | 예상값 vs 실제값 비교 |
| `coverage < 80%` | 테스트 부족 | 미커버 라인 확인 후 테스트 추가 |

### 📈 성과 추적

#### 나의 pytest 사용 히스토리
- **사용 횟수**: 15회
- **성공률**: 93% (14/15)
- **평균 실행 시간**: 2.3초
- **커버리지 추이**:
  - 2025-10-01: 75%
  - 2025-10-15: 82%
  - 2025-11-02: 95% ⬆️

#### 학습 곡선
- **Week 1**: 기본 실행만 (pytest)
- **Week 2**: 커버리지 측정 (--cov)
- **Week 3**: 병렬 실행 (-n auto)
- **Week 4**: 디버깅 마스터 (-xvs)
- **현재**: 고급 설정 및 최적화

### 🎯 다음 학습 목표
- [ ] parametrize로 테스트 케이스 확장
- [ ] fixture 고급 활용 (scope, autouse)
- [ ] pytest plugin 작성
- [ ] CI/CD 파이프라인 통합

### 🔗 관련 자료
- **공식 문서**: https://docs.pytest.org/
- **내부 가이드**: [[Testing-Guide#pytest-coverage]]
- **팀 컨벤션**: [[Team-Conventions#testing]]
- **관련 이슈**: [[Issue-123-Slow-Tests]]
```

**토큰**: ~2000 (풍부한 컨텍스트)
**컨텍스트**: 완벽 (독립 실행 + 학습 가능)

---

## 🤖 AI의 적응형 선택 로직

### 자동 Level 결정 알고리즘

```python
# scripts/adaptive_knowledge_retriever.py (신규)

class AdaptiveKnowledgeRetriever:
    """AI가 상황에 맞는 상세도를 자동 선택"""

    def get_optimal_detail_level(self, query: str, context: Dict) -> int:
        """
        상황 분석 후 최적 Level 결정

        Returns:
            1: Quick Reference (토큰 효율)
            2: Standard Context (균형)
            3: Full Context (컨텍스트 우선)
        """
        score = 0

        # Factor 1: 사용 경험 (0-3점)
        usage_count = self.get_usage_count(query)
        if usage_count == 0:
            score += 3  # 처음 → Full
        elif usage_count < 3:
            score += 2  # 초보 → Standard
        else:
            score += 0  # 숙련 → Quick

        # Factor 2: 실패 이력 (0-3점)
        failure_rate = self.get_failure_rate(query)
        if failure_rate > 0.3:
            score += 3  # 자주 실패 → Full
        elif failure_rate > 0.1:
            score += 2  # 가끔 실패 → Standard
        else:
            score += 0  # 안정적 → Quick

        # Factor 3: 복잡도 (0-2점)
        complexity = self.analyze_complexity(query)
        if complexity == "high":
            score += 2  # 복잡 → 상세히
        elif complexity == "medium":
            score += 1
        else:
            score += 0  # 단순 → 간결히

        # Factor 4: 토큰 여유 (0-2점)
        token_budget = context.get("remaining_tokens", 100000)
        if token_budget < 10000:
            score -= 2  # 토큰 부족 → 압축
        elif token_budget < 50000:
            score -= 1

        # 최종 결정
        if score >= 6:
            return 3  # Full Context
        elif score >= 3:
            return 2  # Standard
        else:
            return 1  # Quick

    def retrieve_with_adaptive_detail(self, query: str) -> str:
        """적응형 상세도로 검색"""

        # 1. 최적 Level 결정
        level = self.get_optimal_detail_level(query, self.get_context())

        # 2. 해당 Level로 검색
        results = self.search_obsidian(query, level=level)

        # 3. 메타 정보 추가 (AI 판단 돕기)
        metadata = f"""
[검색 Level: {level}]
[이유: {self.explain_level_choice(level)}]
[더 자세히 보려면: /detail-up]
[더 간결히 보려면: /detail-down]
"""

        return metadata + "\n\n" + results
```

### 실제 동작 예시

#### 시나리오 1: 처음 사용하는 명령어

```python
# AI 내부 로직
query = "docker compose up -d"
context = {
    "usage_count": 0,      # 처음
    "failure_rate": None,  # 이력 없음
    "complexity": "high",  # Docker는 복잡
    "remaining_tokens": 100000
}

# 점수 계산
score = 3 (처음) + 3 (이력없음=최대주의) + 2 (복잡) = 8
level = 3  # Full Context

# 결과: 상세한 가이드 제공
# - Docker 설치 확인
# - docker-compose.yml 설정
# - 포트 충돌 체크
# - 로그 확인 방법
# - 트러블슈팅 플레이북
```

#### 시나리오 2: 익숙한 명령어

```python
query = "pytest tests/"
context = {
    "usage_count": 15,     # 숙련
    "failure_rate": 0.07,  # 안정적 (1/15 실패)
    "complexity": "low",   # 단순
    "remaining_tokens": 80000
}

# 점수 계산
score = 0 (숙련) + 0 (안정) + 0 (단순) = 0
level = 1  # Quick Reference

# 결과: 간결한 참조
# 💻 pytest tests/ --cov=src
# ✅ 마지막 성공: 2025-11-02
# 🔗 상세: [[Testing-Guide]]
```

#### 시나리오 3: 불안정한 작업

```python
query = "deploy to production"
context = {
    "usage_count": 5,      # 중간
    "failure_rate": 0.4,   # 자주 실패! (2/5)
    "complexity": "high",  # 매우 복잡
    "remaining_tokens": 50000
}

# 점수 계산
score = 2 (중간) + 3 (자주실패) + 2 (복잡) - 1 (토큰여유) = 6
level = 3  # Full Context

# 결과: 완전한 체크리스트
# - 환경 변수 확인
# - 데이터베이스 백업
# - 롤백 계획
# - 모니터링 설정
# - 과거 실패 사례 및 해결책
```

---

## 💡 점진적 상세화 (Progressive Detail)

### 사용자 요청으로 Level 조정

```markdown
## [Standard] pytest 실행

... (Standard 내용) ...

---
📊 이 가이드는 **Standard** 레벨입니다.

🔼 **더 자세히 보기**: `/detail-up`
   → Full Context (환경 설정, 트러블슈팅 플레이북)

🔽 **더 간결히 보기**: `/detail-down`
   → Quick Reference (명령어만)

📌 **항상 이 레벨로**: `/set-default standard`
```

### AI가 추가 정보 제안

```python
# AI 내부 로직

if level == 1 and query_indicates_confusion():
    suggest = """
⚠️ Quick Reference를 제공했지만, 혼란스러워 보입니다.
더 자세한 설명이 필요하신가요? (Y/n)
"""

if level == 3 and user_is_expert():
    suggest = """
💡 Full Context를 제공했지만, 이미 익숙하신 것 같습니다.
다음부터 Standard로 줄일까요? (Y/n)
```

---

## 🎯 균형잡힌 시스템 설계

### 핵심 원칙

1. **기본은 Standard** (80% 경우)
   - 토큰도 적당히 절약
   - 컨텍스트도 충분히 제공

2. **처음이면 Full** (10% 경우)
   - 학습 기회 제공
   - 실수 방지

3. **숙련되면 Quick** (10% 경우)
   - 토큰 효율 극대화
   - 빠른 참조

### 안전장치

```python
# 컨텍스트 손실 방지 규칙

SAFETY_RULES = {
    "never_quick_if_first_time": True,
    "never_quick_if_failure_rate_high": True,
    "never_quick_if_complex": True,
    "always_link_to_full_version": True,
    "allow_manual_override": True
}
```

---

## 📊 예상 효과 (현실적)

### 토큰 사용량

| Scenario | Level | 토큰 | 비율 |
|----------|-------|------|------|
| 처음 사용 | 3 (Full) | 2000 | 10% |
| 일반 작업 | 2 (Std) | 400 | 80% |
| 숙련 작업 | 1 (Quick) | 100 | 10% |
| **평균** | - | **490** | 100% |

**Before**: 평균 3000 토큰
**After**: 평균 490 토큰
**절감**: -84% (과도한 -90%가 아닌 현실적 절감)

### 컨텍스트 정확도

| Level | 컨텍스트 | AI 이해도 | 성공률 |
|-------|----------|-----------|--------|
| Quick | 최소 | 70% | 85% |
| Standard | 충분 | 90% | 95% |
| Full | 완벽 | 98% | 99% |

**가중 평균**: 92% AI 이해도, 95% 성공률

---

## 🔧 구현 우선순위 (재조정)

### Phase 1: 기본 구조 (2일)
- [ ] Level 1-2-3 템플릿 정의
- [ ] Obsidian 개발일지에 Level 표시 추가
- [ ] 기본 Level = Standard (안전하게 시작)

### Phase 2: 적응형 선택 (2일)
- [ ] `AdaptiveKnowledgeRetriever` 구현
- [ ] 사용 횟수/실패율 추적
- [ ] 자동 Level 결정 로직

### Phase 3: 사용자 제어 (1일)
- [ ] `/detail-up`, `/detail-down` 명령어
- [ ] `/set-default` 설정 저장
- [ ] AI 제안 시스템

---

## ✅ 안전성 체크리스트

- [ ] 처음 사용 시 절대 Quick 안 함
- [ ] 실패율 30% 이상이면 Full 강제
- [ ] 모든 Level에서 Full 버전 링크 제공
- [ ] 사용자가 언제든 Level 변경 가능
- [ ] AI가 혼란 감지 시 자동 상세화 제안
- [ ] 토큰 부족 시에만 강제 압축 (경고와 함께)

---

**Status**: Balanced Design Complete
**Risk**: Low (컨텍스트 보존 + 토큰 효율)
**Next**: Phase 1 Implementation
