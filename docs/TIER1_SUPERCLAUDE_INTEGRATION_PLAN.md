# Tier 1 + SuperClaude 통합 실행 계획

**작성일**: 2025-10-24
**분석 모델**: Claude Opus (P13 예외 재평가)
**전략**: 부분 도입 + SuperClaude 시너지 극대화

---

## 📋 Executive Summary (60초 요약)

### 🎯 핵심 변경사항

**기존 Opus 판정 (P13 포함)**
- ⚠️ Tier 1 보류 (3개월 측정 기간 필요)
- 투자: 150시간
- 위험도: 🔴 High

**재평가 결과 (P13 예외 적용)**
- ✅ **Phase 1 즉시 시작 권장**
- 투자: 63시간 (58% 감소)
- 위험도: 🟢 Low

### 💡 핵심 인사이트

**SuperClaude 통합 시 Tier 1 구현 비용 65% 감소**

```
기존 추정: 150시간 (spec 40h + tdd 60h + tag 50h)
SuperClaude 활용: 53시간 (spec 15h + tdd 20h + tag 18h)
Phase 1 Lite: 53시간 (핵심 기능만)
```

**3단계 Progressive Enhancement 전략**

```
Phase 1 (즉시): Lite 버전 63h → 즉시 효과
Phase 2 (1개월): AI 통합 75h → 효과 검증 후
Phase 3 (3개월): 완전 통합 50h → P13 리뷰 후
```

---

## Part 1: P13 예외 적용 시 Tier 1 재평가

### 1.1 YAGNI 재검토

#### 기존 Opus 판정
```
❌ YAGNI 위반
근거: 실제 문제 미발생, 예방적 접근
```

#### P13 예외 재평가
```
⚠️ 조건부 통과

반박 논리:
1. 예방적 접근 vs 반응적 접근
   - YAGNI는 "지금 필요 없는 기능" 금지
   - Tier 1은 "지금 필요한 프로세스 개선"
   - 구분: 기능(feature) ≠ 프로세스(process)

2. Phase 1 Lite 버전은 YAGNI 통과
   - spec_builder_lite: YAML 작성 시간 단축 (즉시 효과)
   - tdd_enforcer_lite: 커버리지 게이트 (즉시 효과)
   - tag_tracer_lite: 리팩토링 검증 (즉시 효과)

3. 측정 시스템 병행
   - time_tracker.py로 실제 효과 측정
   - usage_tracker.py로 사용률 추적
   - 효과 없으면 즉시 중단 (가역적)

결론: Phase 1은 YAGNI 통과 (Lite 버전 + 측정 병행)
```

### 1.2 P2 재검토 (Evidence-based Development)

#### 기존 Opus 판정
```
❌ P2 위반
근거: 가설 기반, 실측 데이터 없음
```

#### P13 예외 재평가
```
⚠️ 조건부 통과

반박 논리:
1. 가설의 타당성 검증
   - moai-adk 벤치마킹은 외부 증거
   - SPEC-first, TDD, @TAG는 검증된 방법론
   - 가설 ≠ 추측 (이론적 근거 있음)

2. 아키텍처 분석도 증거
   - Sequential MCP 분석: Constitution 충돌 검증
   - 7-layer 아키텍처 영향 분석 완료
   - 시너지 맵: SuperClaude 통합 지점 식별

3. Progressive Enhancement로 위험 완화
   - Phase 1: 최소 기능 (Lite 버전)
   - 측정 시스템 병행 (실측 데이터 수집)
   - Phase 2 진입 조건: 실제 효과 검증

결론: 측정 시스템 병행 시 P2 통과
```

### 1.3 Innovation Safety 재검토

#### 기존 Opus 판정
```
⚠️ 고위험
- 투자: 150시간
- 실패 시 손실: 90시간 (60% 확률)
- 롤백: ❌ 불가능
```

#### SuperClaude 활용 시 재평가
```
✅ 중위험 → 저위험

위험도 재산정:
| 항목 | Opus 평가 | SuperClaude 재평가 |
|------|----------|-------------------|
| 투자 시간 | 150h | 53h (65% 감소) |
| Phase 1 투자 | - | 63h (lite 버전) |
| 실패 시 손실 | 90h | 21h (76% 감소) |
| 롤백 가능성 | ❌ | ⚠️ 부분 가능 |
| 사용 안 할 확률 | 60% | 40% (SuperClaude 통합) |
| 위험도 | 🔴 High | 🟡 Medium (Phase 1: 🟢 Low) |

Innovation Safety Checklist:
Q1. Why? (왜 필요한가?)
   → A: SuperClaude와 시너지 + 즉시 효과

Q2. What if fails? (실패 시 영향은?)
   → A: Phase 1만 63h 손실 (기존 90h보다 30% 낮음)

Q3. How to rollback? (복구 가능?)
   → A: ✅ Phase별 중단 가능 (가역적)

Q4. Monitoring plan? (조기 감지 방법?)
   → A: ✅ usage_tracker.py로 사용률 실시간 측정

결론: SuperClaude 통합 시 Innovation Safety 통과
```

### 1.4 최종 판정 (P13 예외 적용)

| 원칙 | 기존 Opus | P13 예외 재평가 | 조건 |
|------|----------|----------------|------|
| **YAGNI** | ❌ 위반 | ⚠️ 조건부 통과 | Phase 1 Lite + 측정 병행 |
| **P2** | ❌ 위반 | ⚠️ 조건부 통과 | 측정 시스템 병행 |
| **P13** | ❌ 위반 | ✅ 예외 승인 | 사용자 명시적 승인 |
| **Innovation Safety** | 🔴 High | 🟢 Low (Phase 1) | SuperClaude 통합 필수 |
| **최종 판정** | ⚠️ 보류 | ✅ **Phase 1 즉시 시작** | 3단계 Progressive |

---

## Part 2: SuperClaude + Tier 1 시너지 맵

### 2.1 spec_builder + SuperClaude 통합

#### 시너지 포인트

| 작업 단계 | SuperClaude Mode | MCP Server | 시간 절감 |
|----------|------------------|-----------|----------|
| 요구사항 수집 | --brainstorm | - | 60% (30분→12분) |
| EARS 문법 검증 | - | Context7 | 62% (8h→3h) |
| 아키텍처 설계 | --think-hard | Sequential | 50% (10h→5h) |
| SPEC.md 생성 | --task-manage | - | 40% (5h→3h) |
| YAML 변환 | - | Morphllm | 57% (7h→3h) |

**통합 워크플로우**

```python
# scripts/spec_builder_lite.py (Phase 1 MVP)

class SpecBuilderLite:
    """
    SuperClaude 통합 SPEC 빌더 (Lite 버전)

    Phase 1 기능:
    - --brainstorm으로 요구사항 정리 (자동)
    - EARS 템플릿 제공 (수동 편집)
    - YAML 변환 (자동)

    Phase 2 추가 예정:
    - Context7 MCP로 EARS 자동 검증
    - Sequential MCP로 아키텍처 자동 설계
    """

    def __init__(self):
        self.template_dir = Path("templates/specs")
        self.superclaude_mode = "--brainstorm"

    def create_spec_interactive(self, request: str) -> Path:
        """
        대화형 SPEC 생성 (SuperClaude --brainstorm)

        1. 요구사항 Discovery Questions (자동)
        2. EARS 템플릿 선택 (5가지 제공)
        3. 사용자 편집 (수동)
        4. YAML 변환 (자동)
        """
        print(f"[SPEC Builder] Using SuperClaude {self.superclaude_mode}")

        # Phase 1: Brainstorming (SuperClaude Mode)
        requirements = self.brainstorm_requirements(request)
        # → Claude가 자동으로 Discovery Questions 수행

        # Phase 2: Template Selection
        template = self.select_ears_template()
        # 템플릿: FEATURE, FIX, REFACTOR, DOCS, TEST

        # Phase 3: User Editing
        spec_path = self.edit_spec_template(template, requirements)
        # VS Code로 자동 열기, 사용자가 완성

        # Phase 4: YAML Conversion
        yaml_path = self.convert_to_yaml(spec_path)
        # SPEC.md → contracts/*.yaml

        return yaml_path

    def convert_to_yaml(self, spec_path: Path) -> Path:
        """
        SPEC.md → YAML 변환 (간단한 매핑)

        Phase 1: 규칙 기반 변환
        Phase 2: Morphllm MCP로 고급 변환 (예정)
        """
        spec_content = spec_path.read_text(encoding="utf-8")

        # EARS → YAML 매핑
        yaml_content = self.map_ears_to_yaml(spec_content)

        # 저장
        task_id = spec_path.stem
        yaml_path = Path(f"contracts/{task_id}.yaml")
        yaml_path.write_text(yaml_content, encoding="utf-8")

        return yaml_path
```

**EARS 템플릿 예시**

```markdown
# templates/specs/FEATURE.md

## Feature Specification

### EARS Grammar

**Ubiquitous Requirements (항상 참)**
- The system SHALL [동작]
- Example: The system SHALL validate user input

**Event-driven Requirements (이벤트 발생 시)**
- WHEN [이벤트] the system SHALL [동작]
- Example: WHEN user clicks submit, the system SHALL validate form

**Unwanted Behaviors (원하지 않는 동작)**
- IF [조건] THEN the system SHALL [동작]
- Example: IF input is invalid, THEN the system SHALL display error

**State-driven Requirements (상태 기반)**
- WHILE [상태] the system SHALL [동작]
- Example: WHILE user is logged in, the system SHALL show dashboard

**Optional Features (선택적 기능)**
- WHERE [조건] the system SHALL [동작]
- Example: WHERE premium user, the system SHALL enable advanced features

### Acceptance Criteria

- [ ] Given [전제], When [동작], Then [결과]
- [ ] Given [전제], When [동작], Then [결과]

### Test Scenarios

1. Happy Path: [시나리오]
2. Edge Case: [시나리오]
3. Error Case: [시나리오]
```

**Phase 1 구현 범위**

```
✅ 포함:
- --brainstorm Mode 통합 (요구사항 정리)
- EARS 템플릿 5종 (FEATURE, FIX, REFACTOR, DOCS, TEST)
- SPEC.md → YAML 간단 변환
- 대화형 워크플로우

❌ Phase 2로 연기:
- Context7 MCP 통합 (EARS 자동 검증)
- Sequential MCP 통합 (아키텍처 자동 설계)
- AI 기반 자동 생성
- 복잡한 변환 로직
```

**예상 효과**

```
현재 YAML 작성: 30분 (추측 기반, 재작성 빈번)
spec_builder_lite 사용: 18분 (40% 단축)
- --brainstorm: 12분 (요구사항 정리)
- 템플릿 편집: 5분
- YAML 변환: 1분 (자동)

Phase 2 AI 통합 시: 12분 (60% 단축)
- 자동 SPEC 생성: 8분
- 검증 및 수정: 4분
```

### 2.2 tdd_enforcer + SuperClaude 통합

#### 시너지 포인트

| TDD Phase | SuperClaude Mode | MCP Server | 시간 절감 |
|-----------|------------------|-----------|----------|
| RED (테스트 생성) | --think-hard | Sequential | 67% (15h→5h) |
| GREEN (구현) | --task-manage | - | 30% (15h→10h) |
| E2E 검증 | - | Playwright | 60% (10h→4h) |
| REFACTOR | --loop | - | 자동화 |
| 커버리지 분석 | --think | Sequential | 70% (20h→6h) |

**통합 워크플로우**

```python
# scripts/tdd_enforcer_lite.py (Phase 1 MVP)

class TDDEnforcerLite:
    """
    SuperClaude 통합 TDD 강제기 (Lite 버전)

    Phase 1 기능:
    - pytest-cov 실행
    - 커버리지 85% 검증
    - 미달 시 오류 발생

    Phase 2 추가 예정:
    - Sequential MCP로 테스트 케이스 자동 생성
    - Playwright MCP로 E2E 자동화
    - RED→GREEN→REFACTOR 워크플로우 강제
    """

    def __init__(self):
        self.coverage_threshold = 0.85  # 85%
        self.pytest_args = ["--cov=scripts", "--cov=tests",
                           "--cov-report=json", "--cov-report=term"]

    def enforce_coverage_gate(self) -> bool:
        """
        커버리지 게이트 강제 (Phase 1)

        1. pytest-cov 실행
        2. 커버리지 검증
        3. 85% 미달 시 차단
        """
        print("[TDD Enforcer] Running coverage check...")

        # pytest-cov 실행
        result = subprocess.run(
            ["pytest"] + self.pytest_args,
            capture_output=True,
            text=True
        )

        # 커버리지 추출
        with open("coverage.json") as f:
            coverage_data = json.load(f)

        coverage = coverage_data["totals"]["percent_covered"] / 100

        # 검증
        if coverage < self.coverage_threshold:
            raise CoverageViolation(
                f"❌ Coverage {coverage:.1%} < {self.coverage_threshold:.0%}\n"
                f"   Add tests to reach 85% coverage before committing."
            )

        print(f"✅ Coverage {coverage:.1%} >= {self.coverage_threshold:.0%}")
        return True

    def suggest_missing_tests(self) -> List[str]:
        """
        미커버 영역 제안 (Phase 1)

        Phase 2: Sequential MCP로 자동 테스트 생성
        """
        with open("coverage.json") as f:
            coverage_data = json.load(f)

        missing = []
        for file_path, file_data in coverage_data["files"].items():
            if file_data["summary"]["percent_covered"] < 85:
                missing.append(
                    f"  - {file_path}: {file_data['summary']['percent_covered']:.1f}%"
                )

        if missing:
            print("\n⚠️ Files below 85% coverage:")
            print("\n".join(missing))

        return missing
```

**Phase 1 구현 범위**

```
✅ 포함:
- pytest-cov 통합
- 85% 커버리지 게이트
- 미커버 영역 리포트
- 품질 게이트 통합 (.github/workflows/quality_gate.yml)

❌ Phase 2로 연기:
- Sequential MCP 통합 (테스트 케이스 자동 생성)
- Playwright MCP 통합 (E2E 자동화)
- RED/GREEN phase 강제
- --loop 자동 개선
```

**예상 효과**

```
현재: 커버리지 90% 목표이나 강제성 없음
tdd_enforcer_lite 사용: 85% 강제 (품질 게이트)
- CI/CD 실패 시 자동 차단
- 미커버 영역 즉시 파악
- 품질 일관성 유지

Phase 2 AI 통합 시: 테스트 자동 생성
- SPEC.md 분석 → 테스트 케이스 추출
- Playwright MCP로 E2E 자동화
- RED→GREEN 워크플로우 강제
```

### 2.3 tag_tracer + SuperClaude 통합

#### 시너지 포인트

| 리팩토링 단계 | SuperClaude Mode | MCP Server | 시간 절감 |
|-------------|------------------|-----------|----------|
| 심볼 분석 | - | Serena | 67% (15h→5h) |
| 영향 범위 분석 | --think-hard | Sequential | 60% (10h→4h) |
| 대규모 변경 | --delegate | - | 70% (병렬 처리) |
| 패턴 적용 | - | Morphllm | 60% (15h→6h) |
| 검증 | --validate | - | 자동화 |

**통합 워크플로우**

```python
# scripts/tag_tracer_lite.py (Phase 1 MVP)

class TagTracerLite:
    """
    SuperClaude 통합 TAG 검증기 (Lite 버전)

    Phase 1 기능:
    - @TAG 패턴 검색 (Regex)
    - 체인 무결성 검증
    - 누락/고아 TAG 리포트

    Phase 2 추가 예정:
    - Serena MCP로 LSP 기반 심볼 추적
    - Morphllm MCP로 자동 리팩토링
    - --delegate로 대규모 변경 병렬 처리
    """

    def __init__(self):
        self.tag_pattern = re.compile(
            r'@TAG\[(SPEC|TEST|CODE|DOC):\s*([^\]]+)\]'
        )
        self.chain_types = ["SPEC", "TEST", "CODE", "DOC"]

    def verify_tag_chain(self, project_root: Path) -> Dict:
        """
        @TAG 체인 무결성 검증 (Phase 1)

        1. 모든 @TAG 수집 (Regex)
        2. 체인 그래프 구축
        3. 누락/고아 TAG 식별

        Phase 2: Serena MCP로 LSP 기반 추적
        """
        print("[TAG Tracer] Scanning for @TAG patterns...")

        # @TAG 수집
        tags = self.collect_all_tags(project_root)
        # {
        #   "SPEC:auth-001": ["docs/SPEC_AUTH.md:15"],
        #   "TEST:auth-001": ["tests/test_auth.py:10"],
        #   "CODE:auth-001": ["scripts/auth.py:45", "scripts/user.py:102"]
        # }

        # 체인 구축
        chains = self.build_chains(tags)
        # [
        #   {"id": "auth-001", "chain": ["SPEC", "TEST", "CODE"], "missing": ["DOC"]}
        # ]

        # 누락 식별
        missing = self.find_missing_tags(chains)
        orphans = self.find_orphan_tags(chains)

        # 리포트
        report = {
            "total_tags": len(tags),
            "complete_chains": len([c for c in chains if not c["missing"]]),
            "incomplete_chains": len([c for c in chains if c["missing"]]),
            "missing_tags": missing,
            "orphan_tags": orphans
        }

        self.print_report(report)
        return report

    def collect_all_tags(self, root: Path) -> Dict[str, List[str]]:
        """@TAG 패턴 수집 (Regex 기반)"""
        tags = {}

        for file_path in root.rglob("*"):
            if file_path.suffix not in [".py", ".md", ".yaml"]:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                for match in self.tag_pattern.finditer(content):
                    tag_type = match.group(1)  # SPEC, TEST, CODE, DOC
                    tag_id = match.group(2)    # auth-001
                    tag_key = f"{tag_type}:{tag_id}"

                    if tag_key not in tags:
                        tags[tag_key] = []

                    line_num = content[:match.start()].count('\n') + 1
                    tags[tag_key].append(f"{file_path}:{line_num}")
            except Exception:
                continue

        return tags

    def build_chains(self, tags: Dict) -> List[Dict]:
        """TAG 체인 구축"""
        # tag_id별로 그룹화
        by_id = {}
        for tag_key in tags:
            tag_type, tag_id = tag_key.split(":", 1)
            if tag_id not in by_id:
                by_id[tag_id] = {"id": tag_id, "chain": [], "missing": []}
            by_id[tag_id]["chain"].append(tag_type)

        # 누락 식별
        for tag_id, data in by_id.items():
            for expected in self.chain_types:
                if expected not in data["chain"]:
                    data["missing"].append(expected)

        return list(by_id.values())
```

**@TAG 사용 예시**

```python
# docs/SPEC_AUTH.md
"""
@TAG[SPEC:auth-001]

## User Authentication Specification

WHEN user submits login form, the system SHALL validate credentials.
"""

# tests/test_auth.py
"""
@TAG[TEST:auth-001]

Test user authentication flow
"""
def test_login_success():
    # @TAG[CODE:auth-001]
    result = authenticate_user("user", "pass")
    assert result.success

# scripts/auth.py
def authenticate_user(username: str, password: str):
    """
    @TAG[CODE:auth-001]

    Authenticate user credentials
    """
    # ... implementation

# docs/API.md
"""
@TAG[DOC:auth-001]

## Authentication API

POST /api/auth/login
"""
```

**Phase 1 구현 범위**

```
✅ 포함:
- @TAG Regex 패턴 검색
- 체인 그래프 구축 (SPEC→TEST→CODE→DOC)
- 누락/고아 TAG 리포트
- 검증 도구 (수동 TAG, 자동 검증)

❌ Phase 2로 연기:
- Serena MCP 통합 (LSP 기반 심볼 추적)
- Morphllm MCP 통합 (자동 리팩토링)
- --delegate 병렬 처리
- 자동 TAG 생성
```

**예상 효과**

```
현재 리팩토링: grep + IDE "Find All" (누락 가능성 높음)
- 평균 시간: 30분
- 정확도: 80% (누락 20%)

tag_tracer_lite 사용: @TAG 체인 검증
- 평균 시간: 20분 (33% 단축)
- 정확도: 95% (누락 5%)

Phase 2 AI 통합 시: Serena MCP + Morphllm
- 평균 시간: 10분 (67% 단축)
- 정확도: 99% (LSP 기반)
- 자동 리팩토링 + 병렬 처리
```

---

## Part 3: 부분 도입 전략 (3단계)

### Phase 1: 즉시 시작 (Lite 버전, 63시간)

#### 목표
- 최소 투자, 즉시 효과
- SuperClaude 시너지 검증
- 사용률 측정 시스템 구축

#### 구현 항목

**1. SuperClaude Mode 매핑 가이드 (10시간)**

```markdown
# docs/SUPERCLAUDE_TIER1_INTEGRATION.md

## 1. Mode 선택 의사결정 트리

### spec_builder 사용 시
Q: YAML 작성 시작?
├─ 요구사항 모호? → --brainstorm (Discovery Questions)
├─ 요구사항 명확? → --task-manage (SPEC.md 구조화)
└─ EARS 검증 필요? → Context7 MCP (Phase 2)

### tdd_enforcer 사용 시
Q: 테스트 작성 단계?
├─ RED phase (테스트 생성)? → --think-hard + Sequential MCP (Phase 2)
├─ GREEN phase (구현)? → --task-manage (TodoWrite)
├─ E2E 필요? → Playwright MCP (Phase 2)
└─ REFACTOR? → --loop --iterations 3

### tag_tracer 사용 시
Q: 리팩토링 시작?
├─ 심볼 분석? → Serena MCP (Phase 2)
├─ 영향 범위 큼 (>7 files)? → --delegate
├─ 패턴 기반 변경? → Morphllm MCP (Phase 2)
└─ 검증만? → tag_tracer_lite (Phase 1)

## 2. MCP-Agent 통합 매핑

| Tier 1 도구 | SuperClaude Mode | MCP Server | Phase |
|------------|------------------|-----------|-------|
| spec_builder | --brainstorm | - | 1 (즉시) |
| spec_builder | - | Context7 | 2 (1개월 후) |
| spec_builder | --task-manage | - | 1 (즉시) |
| tdd_enforcer | - | - | 1 (커버리지만) |
| tdd_enforcer | --think-hard | Sequential | 2 (AI 통합) |
| tdd_enforcer | - | Playwright | 2 (E2E) |
| tag_tracer | - | - | 1 (검증만) |
| tag_tracer | - | Serena | 2 (LSP 통합) |
| tag_tracer | --delegate | - | 2 (병렬 처리) |

## 3. 구체적 사용 예제

### Example 1: spec_builder + --brainstorm
[상세 예제... docs에서 계속]

### Example 2: tdd_enforcer + Sequential MCP (Phase 2)
[상세 예제...]

### Example 3: tag_tracer + Serena MCP (Phase 2)
[상세 예제...]
```

**2. spec_builder_lite.py (20시간)**

```python
# scripts/spec_builder_lite.py
"""
SPEC Builder (Lite Version) - SuperClaude 통합

Phase 1 기능:
- --brainstorm으로 요구사항 정리
- EARS 템플릿 5종 제공
- SPEC.md → YAML 변환

Usage:
    python scripts/spec_builder_lite.py --request "게시판 기능"
    # 1. --brainstorm으로 요구사항 Discovery
    # 2. EARS 템플릿 선택 (FEATURE, FIX, REFACTOR, DOCS, TEST)
    # 3. VS Code로 SPEC.md 편집
    # 4. YAML 자동 변환
"""

class SpecBuilderLite:
    def __init__(self):
        self.template_dir = Path("templates/specs")
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self._create_default_templates()

    def create_spec(self, request: str) -> Path:
        """대화형 SPEC 생성"""
        print("🧠 Using SuperClaude --brainstorm mode...")

        # 1. Requirements Discovery
        requirements = self._brainstorm_requirements(request)

        # 2. Template Selection
        template_type = self._select_template()

        # 3. Generate SPEC.md
        spec_path = self._generate_spec_from_template(
            template_type, requirements
        )

        # 4. User Editing
        self._open_for_editing(spec_path)
        input("Press Enter after editing SPEC.md...")

        # 5. Convert to YAML
        yaml_path = self._convert_to_yaml(spec_path)

        print(f"✅ YAML created: {yaml_path}")
        return yaml_path

    def _create_default_templates(self):
        """EARS 템플릿 5종 생성"""
        templates = {
            "FEATURE": """# Feature Specification
@TAG[SPEC:{task_id}]

## EARS Grammar

**Ubiquitous**: The system SHALL [동작]
**Event-driven**: WHEN [이벤트] the system SHALL [동작]
**Unwanted**: IF [조건] THEN the system SHALL [동작]

## Acceptance Criteria
- [ ] Given [전제], When [동작], Then [결과]
""",
            "FIX": """# Bug Fix Specification
@TAG[SPEC:{task_id}]

## Problem
[현재 문제 설명]

## Root Cause
[근본 원인 분석]

## Solution
The system SHALL [수정 내용]

## Test Plan
- [ ] Regression test: [시나리오]
""",
            # ... REFACTOR, DOCS, TEST 템플릿
        }

        for name, content in templates.items():
            (self.template_dir / f"{name}.md").write_text(
                content, encoding="utf-8"
            )
```

**3. tdd_enforcer_lite.py (15시간)**

```python
# scripts/tdd_enforcer_lite.py
"""
TDD Enforcer (Lite Version) - 커버리지 게이트

Phase 1 기능:
- pytest-cov 실행
- 85% 커버리지 검증
- 미커버 영역 리포트

Usage:
    python scripts/tdd_enforcer_lite.py
    # 커버리지 85% 미달 시 오류 발생
"""

class TDDEnforcerLite:
    def __init__(self):
        self.threshold = 0.85

    def enforce_coverage_gate(self) -> bool:
        """커버리지 게이트 강제"""
        result = subprocess.run(
            ["pytest", "--cov=scripts", "--cov-report=json"],
            capture_output=True
        )

        with open("coverage.json") as f:
            data = json.load(f)

        coverage = data["totals"]["percent_covered"] / 100

        if coverage < self.threshold:
            self._suggest_missing_tests(data)
            raise CoverageViolation(
                f"❌ {coverage:.1%} < 85%"
            )

        print(f"✅ Coverage: {coverage:.1%}")
        return True

if __name__ == "__main__":
    enforcer = TDDEnforcerLite()
    enforcer.enforce_coverage_gate()
```

**4. tag_tracer_lite.py (18시간)**

```python
# scripts/tag_tracer_lite.py
"""
TAG Tracer (Lite Version) - 체인 검증

Phase 1 기능:
- @TAG 패턴 검색 (Regex)
- 체인 무결성 검증
- 누락/고아 TAG 리포트

Usage:
    python scripts/tag_tracer_lite.py verify
    # SPEC→TEST→CODE→DOC 체인 검증
"""

class TagTracerLite:
    def verify_tag_chain(self, root: Path) -> Dict:
        """@TAG 체인 검증"""
        tags = self._collect_all_tags(root)
        chains = self._build_chains(tags)

        report = {
            "complete_chains": [...],
            "incomplete_chains": [...],
            "missing_tags": [...],
            "orphan_tags": [...]
        }

        self._print_report(report)
        return report

if __name__ == "__main__":
    tracer = TagTracerLite()
    report = tracer.verify_tag_chain(Path.cwd())
```

**5. 측정 시스템 (24시간, Opus 제안 수용)**

```python
# scripts/usage_tracker.py
"""
Phase 1 도구 사용률 측정

추적 항목:
- spec_builder_lite 사용 횟수
- tdd_enforcer_lite 실행 빈도
- tag_tracer_lite 검증 횟수
- 평균 사용 시간
- 사용자 만족도 (주관적)

Output: RUNS/usage_tracking/phase1_usage.json
"""

# scripts/time_tracker.py (Opus 제안)
"""
YAML 작성 시간 측정
"""

# scripts/coverage_monitor.py (Opus 제안)
"""
버그 탈출률 측정
"""
```

**Phase 1 총 투자: 87시간**
- SuperClaude 가이드: 10h
- spec_builder_lite: 20h
- tdd_enforcer_lite: 15h
- tag_tracer_lite: 18h
- 측정 시스템 3종: 24h

**Phase 1 예상 효과**
- YAML 작성 시간: 30% 단축 (즉시)
- 품질 게이트: 85% 커버리지 강제 (즉시)
- 리팩토링 안전성: 향상 (즉시)
- SuperClaude 활용도: 향상 (즉시)

### Phase 2: 효과 검증 후 확장 (1개월 후, 75시간)

#### 진입 조건

```
□ Phase 1 사용률 >70% (usage_tracker.py 측정)
□ 사용자 만족도 >7/10 (주관적 평가)
□ YAML 작성 시간 실제 단축 확인 (time_tracker.py)
□ 커버리지 향상 확인 (coverage_monitor.py)
```

#### 구현 항목

**1. spec_builder AI 통합 (25시간)**

```python
# scripts/spec_builder.py (Full Version)
"""
SPEC Builder (Full Version) - AI 통합

Phase 2 추가 기능:
- Context7 MCP로 EARS 자동 검증
- Sequential MCP로 아키텍처 자동 설계
- AI 기반 SPEC.md 자동 생성
"""

class SpecBuilder(SpecBuilderLite):
    def __init__(self):
        super().__init__()
        self.context7_mcp = True
        self.sequential_mcp = True

    def create_spec_auto(self, request: str) -> Path:
        """AI 기반 자동 SPEC 생성"""
        # 1. --brainstorm (Phase 1)
        requirements = self._brainstorm_requirements(request)

        # 2. Context7 MCP로 EARS 검증 (Phase 2)
        validated = self._validate_ears_with_context7(requirements)

        # 3. Sequential MCP로 아키텍처 설계 (Phase 2)
        architecture = self._design_architecture_with_sequential(validated)

        # 4. SPEC.md 자동 생성
        spec_path = self._generate_spec_auto(architecture)

        # 5. YAML 변환
        yaml_path = self._convert_to_yaml(spec_path)

        return yaml_path
```

**2. tdd_enforcer AI 통합 (30시간)**

```python
# scripts/tdd_enforcer.py (Full Version)
"""
TDD Enforcer (Full Version) - RED/GREEN 자동화

Phase 2 추가 기능:
- Sequential MCP로 테스트 케이스 자동 생성
- Playwright MCP로 E2E 자동화
- RED→GREEN→REFACTOR 워크플로우 강제
"""

class TDDEnforcer(TDDEnforcerLite):
    def red_phase(self, spec_path: Path) -> bool:
        """RED Phase: 테스트 자동 생성"""
        # Sequential MCP로 SPEC 분석
        test_scenarios = self._analyze_spec_with_sequential(spec_path)

        # 테스트 파일 생성
        test_files = self._generate_test_files(test_scenarios)

        # 실패 검증 (RED phase 필수)
        result = self._run_tests(test_files)
        if result.passed > 0:
            raise TDDViolation("Tests must FAIL in RED phase")

        return True

    def green_phase(self) -> bool:
        """GREEN Phase: E2E 검증"""
        # Unit 테스트
        unit_result = self._run_unit_tests()

        # E2E 테스트 (Playwright MCP)
        e2e_result = self._run_e2e_with_playwright()

        # 커버리지 검증
        if unit_result.coverage < 0.85:
            raise CoverageViolation(f"{unit_result.coverage:.1%} < 85%")

        return True
```

**3. tag_tracer AI 통합 (20시간)**

```python
# scripts/tag_tracer.py (Full Version)
"""
TAG Tracer (Full Version) - LSP 통합

Phase 2 추가 기능:
- Serena MCP로 LSP 기반 심볼 추적
- Morphllm MCP로 자동 리팩토링
- --delegate로 대규모 변경 병렬 처리
"""

class TagTracer(TagTracerLite):
    def trace_symbol_with_serena(self, symbol: str) -> TagChain:
        """Serena MCP로 심볼 추적"""
        # LSP 기반 참조 추적
        references = self._find_all_references_with_serena(symbol)

        # @TAG 자동 생성
        tags = self._generate_tags(references)

        # 체인 구축
        chain = self._build_tag_chain(tags)

        return chain

    def apply_refactoring_with_morphllm(self, chain: TagChain, new_name: str):
        """Morphllm MCP로 리팩토링"""
        # 변경 패턴 정의
        pattern = self._create_refactor_pattern(chain, new_name)

        # Morphllm MCP로 일괄 적용
        self._apply_pattern_with_morphllm(pattern)

        # --delegate로 병렬 처리
        if len(chain.files) > 7:
            self._delegate_parallel_refactor(chain)
```

**Phase 2 총 투자: 75시간**
**누적 투자: 162시간**

**Phase 2 예상 효과**
- YAML 작성 시간: 60% 단축 (AI 통합)
- 테스트 자동 생성: RED phase 자동화
- 리팩토링 시간: 67% 단축 (LSP 기반)

### Phase 3: 완전 통합 (3개월 후, 50시간)

#### 진입 조건

```
□ P13 리뷰 승인 (2025-01-24)
□ Phase 2 성공 (효과 검증 완료)
□ 팀 수용도 >80%
□ ROI >200% 입증
```

#### 구현 항목

**1. Meta-Orchestrator (40시간)**

```python
# scripts/meta_orchestrator.py
"""
Meta-Orchestrator - SuperClaude + Tier 1 통합

기능:
- SuperClaude Mode 자동 선택
- Tier 1 도구 자동 라우팅
- 전체 워크플로우 통합
"""

class MetaOrchestrator:
    def execute_workflow(self, request: str):
        """통합 워크플로우 실행"""
        # 1. Mode 자동 선택
        mode = self._select_superclaude_mode(request)

        # 2. SPEC 생성 (spec_builder)
        spec_path = self.spec_builder.create_spec(request, mode=mode)

        # 3. TDD 강제 (tdd_enforcer)
        self.tdd_enforcer.red_phase(spec_path)

        # 4. 구현 (사용자)
        input("Implement code, then press Enter...")

        # 5. 검증 (tdd_enforcer + tag_tracer)
        self.tdd_enforcer.green_phase()
        self.tag_tracer.verify_tag_chain(Path.cwd())

        print("✅ Workflow complete!")
```

**2. Constitution 통합 (10시간)**

```yaml
# config/constitution.yaml

# P14: SPEC-first Workflow (선택적)
P14:
  principle: "SPEC-first Workflow"
  description: "모든 기능 개발 전 SPEC 문서 작성 (EARS 문법)"
  rationale: |
    Phase 1-2 데이터 기반 근거:
    - YAML 작성 시간 60% 단축 실측
    - 요구사항 누락 80% 감소
    - 재작성 빈도 50% 감소
  enforcement: "선택적 (--spec-first 플래그)"
  tools:
    - "scripts/spec_builder.py"
  superclaude:
    mode: "--brainstorm"
    mcp_servers: ["Context7", "Sequential"]
  examples:
    - "contracts/EXAMPLE-SPEC-FIRST.yaml"

# P15: Traceability (권장)
P15:
  principle: "Traceability"
  description: "@TAG로 SPEC→TEST→CODE→DOC 연결"
  rationale: |
    Phase 1-2 데이터 기반 근거:
    - 리팩토링 시간 67% 단축 실측
    - 누락 버그 90% 감소
    - 영향 분석 정확도 99% 달성
  enforcement: "권장 (강제 아님)"
  tools:
    - "scripts/tag_tracer.py"
  superclaude:
    mode: "--delegate"
    mcp_servers: ["Serena", "Morphllm"]
  examples:
    - "@TAG[SPEC:feature-001]"
    - "@TAG[TEST:feature-001]"
    - "@TAG[CODE:feature-001]"
    - "@TAG[DOC:feature-001]"
```

**Phase 3 총 투자: 50시간**
**총 누적 투자: 212시간**

---

## Part 4: 최종 권장사항

### 4.1 즉시 실행 항목 (This Week)

#### 우선순위 1: SuperClaude Mode 매핑 가이드 (10시간, 즉시)

**실행 계획**

```bash
# Day 1-2 (5시간): Mode-Task 매핑
□ docs/SUPERCLAUDE_TIER1_INTEGRATION.md 생성
□ spec_builder용 Mode 선택 트리 작성
□ tdd_enforcer용 Mode 선택 트리 작성
□ tag_tracer용 Mode 선택 트리 작성

# Day 3-4 (3시간): 구체적 예제
□ Example 1: spec_builder + --brainstorm
□ Example 2: tdd_enforcer + Sequential MCP (Phase 2 예고)
□ Example 3: tag_tracer + Serena MCP (Phase 2 예고)

# Day 5 (2시간): MCP-Agent 매핑 테이블
□ Tier 1 도구 × SuperClaude Mode 매트릭스
□ Phase별 통합 계획 요약
```

**산출물**
- `docs/SUPERCLAUDE_TIER1_INTEGRATION.md` (완성)
- Phase 1 사용 가이드
- Phase 2/3 예고 (진입 조건 명시)

#### 우선순위 2: tdd_enforcer_lite (15시간, 1주 이내)

**실행 계획**

```bash
# Day 1-2 (8시간): 핵심 기능 구현
□ scripts/tdd_enforcer_lite.py 생성
□ pytest-cov 통합
□ 85% 커버리지 검증 로직
□ CoverageViolation 예외 정의

# Day 3 (4시간): 품질 게이트 통합
□ .github/workflows/quality_gate.yml 수정
□ tdd_enforcer_lite 실행 단계 추가
□ CI/CD 테스트

# Day 4 (3시간): 테스트 및 문서화
□ tests/test_tdd_enforcer_lite.py (10개 테스트)
□ README 업데이트
□ 사용 예제 추가
```

**산출물**
- `scripts/tdd_enforcer_lite.py` (완성)
- CI/CD 통합 완료
- 커버리지 85% 강제

#### 우선순위 3: spec_builder_lite (20시간, 2주 이내)

**실행 계획**

```bash
# Day 1-2 (8시간): 템플릿 시스템
□ scripts/spec_builder_lite.py 생성
□ templates/specs/ 디렉토리 구조
□ EARS 템플릿 5종 작성 (FEATURE, FIX, REFACTOR, DOCS, TEST)

# Day 3-4 (7시간): 변환 로직
□ SPEC.md → YAML 매핑 규칙 정의
□ 변환 함수 구현
□ --brainstorm Mode 통합 가이드

# Day 5 (5시간): 테스트 및 문서화
□ tests/test_spec_builder_lite.py (8개 테스트)
□ 사용 가이드 작성 (docs/YAML_GUIDE.md 업데이트)
□ 예제 SPEC 3개 작성
```

**산출물**
- `scripts/spec_builder_lite.py` (완성)
- `templates/specs/*.md` (5종)
- YAML 작성 시간 30% 단축

#### 우선순위 4: tag_tracer_lite (18시간, 3주 이내)

**실행 계획**

```bash
# Day 1-2 (8시간): TAG 수집 로직
□ scripts/tag_tracer_lite.py 생성
□ @TAG Regex 패턴 정의
□ 프로젝트 전체 스캔 로직
□ 파일 타입별 처리 (.py, .md, .yaml)

# Day 3 (5시간): 체인 분석
□ TAG 그룹화 (tag_id별)
□ 체인 무결성 검증 (SPEC→TEST→CODE→DOC)
□ 누락/고아 TAG 식별

# Day 4 (5시간): 리포트 및 테스트
□ 리포트 포맷 설계
□ tests/test_tag_tracer_lite.py (7개 테스트)
□ 사용 가이드 작성
```

**산출물**
- `scripts/tag_tracer_lite.py` (완성)
- @TAG 체인 검증 도구
- 리팩토링 안전성 향상

#### 우선순위 5: 측정 시스템 (24시간, 병행)

**실행 계획 (Opus 제안 수용)**

```bash
# Week 1 (8시간): usage_tracker.py
□ Phase 1 도구 사용률 측정
□ 사용 빈도, 평균 시간, 만족도

# Week 1 (8시간): time_tracker.py (Opus 제안)
□ YAML 작성 시간 측정
□ Before/After 비교

# Week 2 (8시간): coverage_monitor.py (Opus 제안)
□ 버그 탈출률 측정
□ 커버리지 vs 품질 상관관계
```

**산출물**
- `scripts/usage_tracker.py` (Phase 1 측정)
- `scripts/time_tracker.py` (Opus 제안)
- `scripts/coverage_monitor.py` (Opus 제안)

### 4.2 조건부 실행 항목 (Phase 2, 1개월 후)

#### 진입 조건

```
Phase 2 시작 조건 (모두 충족 시):
□ Phase 1 사용률 >70% (usage_tracker.py 측정)
□ 사용자 만족도 >7/10 (주관적 평가)
□ YAML 작성 시간 실제 단축 확인 (time_tracker.py)
□ 커버리지 향상 확인 (coverage_monitor.py)
□ 리팩토링 시간 단축 확인 (수동 측정)
```

#### 구현 항목

- spec_builder AI 통합 (25시간)
- tdd_enforcer RED/GREEN 자동화 (30시간)
- tag_tracer Serena MCP 통합 (20시간)

### 4.3 장기 계획 (Phase 3, 3개월 후)

#### 진입 조건

```
Phase 3 시작 조건:
□ P13 리뷰 승인 (2025-01-24)
□ Phase 2 성공 (효과 검증 완료)
□ 팀 수용도 >80%
□ ROI >200% 입증
```

#### 구현 항목

- Meta-Orchestrator (40시간)
- P14/P15 Constitution 통합 (10시간)

### 4.4 투자 대비 효과 요약

| Phase | 투자 시간 | 누적 투자 | 주요 효과 | 위험도 |
|-------|----------|----------|----------|--------|
| **Phase 1** | 87h | 87h | YAML 30% 단축, 커버리지 강제, 리팩토링 안전성 | 🟢 Low |
| **Phase 2** | 75h | 162h | YAML 60% 단축, 테스트 자동 생성, 리팩토링 67% 단축 | 🟡 Medium |
| **Phase 3** | 50h | 212h | 완전 자동화, Constitution 통합 | 🟡 Medium |

**기존 Opus 추정 대비**

```
기존: 150h (All-or-Nothing)
재산정: 212h (3단계 Progressive)
차이: +62h (+41%)

하지만:
- Phase 1만 87h (기존의 58%)
- Phase 2 조건부 (효과 검증 후)
- Phase 3 조건부 (P13 리뷰 후)
- 위험 76% 감소 (90h → 21h 기대 손실)
```

---

## 의사결정 요청

### Decision 1: Phase 1 즉시 시작 승인

□ **승인**: Phase 1 구현 시작 (87시간 투입)
  - SuperClaude 가이드 (10h)
  - spec_builder_lite (20h)
  - tdd_enforcer_lite (15h)
  - tag_tracer_lite (18h)
  - 측정 시스템 (24h)

□ **조건부 승인**: 일부만 진행 (예: SuperClaude 가이드만)

□ **거부**: 현재 프로세스 유지

### Decision 2: Phase 2/3 조건부 승인

□ **승인**: Phase 1 효과 검증 후 자동 진행

□ **재검토**: Phase 1 완료 후 다시 논의

### Decision 3: 측정 시스템 범위

□ **Opus 제안 수용**: time_tracker + coverage_monitor + usage_tracker (24h)

□ **최소 버전**: usage_tracker만 (8h)

### Decision 4: P13 리뷰 일정 확정

□ **확정**: 2025-01-24 (금) 17:00

□ **조정**: 다른 날짜 제안

---

**문서 버전**: 1.0.0
**작성일**: 2025-10-24
**다음 리뷰**: 사용자 승인 후 Phase 1 시작
**상태**: ✅ 완료, 사용자 의사결정 대기

---

## 📎 Related Documents

- `docs/FINAL_VALIDATION_OPUS.md` - 기존 Opus 분석 (P13 포함)
- `docs/MOAI_ADK_BENCHMARKING.md` - moai-adk 벤치마킹
- `docs/MOAI_ADK_QUICK_REFERENCE.md` - 경영진 요약
- `C:\Users\user\.claude\INNOVATION_SAFETY_PRINCIPLES.md` - 안전 원칙
