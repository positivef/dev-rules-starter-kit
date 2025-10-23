# YAML 계약서 작성 가이드

**목적**: TaskExecutor로 실행 가능한 YAML 계약서 작성법을 단계별로 학습

**학습 시간**: 10분

**Constitutional Compliance**:
- [P1] YAML 계약서 우선
- [P2] 증거 기반 개발
- [P8] 테스트 우선

---

## 기본 구조

모든 YAML 계약서는 다음 구조를 따릅니다:

```yaml
# 작업 식별자 (필수)
task_id: "FEAT-2025-10-24-01"

# 작업 제목 (필수)
title: "사용자 인증 API 추가"

# 작업 타입 (선택)
type: "feature"  # feature, fix, refactor, docs, test

# 우선순위 (선택)
priority: "high"  # critical, high, medium, low

# 인수 기준 (필수)
acceptance_criteria:
  - "JWT 토큰 발급 API 동작"
  - "토큰 검증 미들웨어 작성"
  - "테스트 커버리지 90% 이상"

# 실행 명령 (필수)
commands:
  - id: "01-test"
    exec:
      cmd: "pytest"
      args: ["tests/test_auth.py", "-v"]

# 품질 게이트 (선택)
gates:
  - type: "constitutional"
    articles: ["P4", "P5"]  # SOLID + 보안
```

---

## 5가지 실전 예제

### 1. 새 기능 추가 (FEAT)

**시나리오**: 사용자 인증 API를 추가하고 테스트 작성

```yaml
task_id: "FEAT-2025-10-24-01"
title: "사용자 인증 API 추가"
type: "feature"
priority: "high"

description: |
  JWT 기반 사용자 인증 시스템 구현
  - 로그인 엔드포인트
  - 토큰 검증 미들웨어
  - 리프레시 토큰 로직

acceptance_criteria:
  - "POST /api/auth/login 엔드포인트 동작"
  - "JWT 토큰 발급 및 검증 성공"
  - "인증 실패 시 401 에러 반환"
  - "테스트 커버리지 95% 이상"

commands:
  - id: "01-create-endpoints"
    description: "인증 엔드포인트 생성"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Create API endpoints in api/auth.py')"

  - id: "02-write-tests"
    description: "테스트 작성"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Write tests in tests/test_auth.py')"

  - id: "03-run-tests"
    description: "테스트 실행"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_auth.py"
        - "-v"
        - "--cov=api"
        - "--cov-report=term"

gates:
  - type: "constitutional"
    articles: ["P4", "P5", "P8"]  # SOLID + 보안 + 테스트 우선
    threshold: 7.0

evidence:
  - type: "file"
    path: "api/auth.py"
    description: "인증 API 구현 코드"

  - type: "file"
    path: "tests/test_auth.py"
    description: "인증 API 테스트"

  - type: "test_results"
    path: "RUNS/FEAT-2025-10-24-01/test_results.json"
```

---

### 2. 버그 수정 (FIX)

**시나리오**: 비밀번호 해싱 버그 수정

```yaml
task_id: "FIX-2025-10-24-02"
title: "비밀번호 해싱 버그 수정"
type: "fix"
priority: "critical"

description: |
  Issue #123: 비밀번호가 평문으로 저장되는 보안 버그
  bcrypt를 사용한 안전한 해싱으로 변경

acceptance_criteria:
  - "모든 비밀번호가 bcrypt로 해싱됨"
  - "평문 비밀번호 저장 코드 제거"
  - "기존 비밀번호 마이그레이션 스크립트 작성"
  - "보안 테스트 통과"

commands:
  - id: "01-install-bcrypt"
    description: "bcrypt 설치"
    exec:
      cmd: "pip"
      args: ["install", "bcrypt"]

  - id: "02-fix-code"
    description: "코드 수정"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Update auth.py to use bcrypt')"

  - id: "03-migration"
    description: "마이그레이션 스크립트 실행"
    exec:
      cmd: "python"
      args: ["scripts/migrate_passwords.py"]

  - id: "04-test"
    description: "보안 테스트 실행"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_security.py"
        - "-v"

gates:
  - type: "constitutional"
    articles: ["P5"]  # 보안 우선
    threshold: 9.0  # 보안 버그는 높은 기준

evidence:
  - type: "file"
    path: "api/auth.py"
    description: "수정된 인증 코드"

  - type: "test_results"
    path: "RUNS/FIX-2025-10-24-02/security_test_results.json"
```

---

### 3. 리팩토링 (REFACTOR)

**시나리오**: SOLID 원칙 위반 코드 리팩토링

```yaml
task_id: "REFACTOR-2025-10-24-03"
title: "UserService SOLID 원칙 적용"
type: "refactor"
priority: "medium"

description: |
  UserService 클래스가 SRP, DIP 위반
  - 너무 많은 책임 (인증, 이메일, 로깅)
  - 직접 의존성 (EmailClient를 직접 import)

acceptance_criteria:
  - "UserService는 사용자 관리만 담당"
  - "EmailService 분리"
  - "의존성 주입으로 DIP 준수"
  - "기존 테스트 모두 통과"

commands:
  - id: "01-analyze"
    description: "SOLID 위반 분석"
    exec:
      cmd: "python"
      args: ["scripts/deep_analyzer.py", "services/user_service.py"]

  - id: "02-refactor"
    description: "리팩토링 수행"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Refactor UserService')"

  - id: "03-test"
    description: "리팩토링 후 테스트"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_user_service.py"
        - "-v"

  - id: "04-verify"
    description: "SOLID 준수 검증"
    exec:
      cmd: "python"
      args: ["scripts/deep_analyzer.py", "services/"]

gates:
  - type: "constitutional"
    articles: ["P4"]  # SOLID 원칙
    threshold: 8.0

evidence:
  - type: "file"
    path: "services/user_service.py"
    description: "리팩토링된 UserService"

  - type: "file"
    path: "services/email_service.py"
    description: "분리된 EmailService"

  - type: "analysis"
    path: "RUNS/REFACTOR-2025-10-24-03/deep_analysis.json"
```

---

### 4. 문서화 (DOCS)

**시나리오**: API 문서 업데이트

```yaml
task_id: "DOCS-2025-10-24-04"
title: "API 문서 업데이트"
type: "docs"
priority: "low"

description: |
  새 인증 API 엔드포인트 문서화
  - OpenAPI 3.0 스펙 업데이트
  - README.md 예제 추가

acceptance_criteria:
  - "OpenAPI 스펙에 /api/auth/* 추가"
  - "README.md에 사용 예제 추가"
  - "코드 예제 동작 검증"

commands:
  - id: "01-update-openapi"
    description: "OpenAPI 스펙 업데이트"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Update docs/openapi.yaml')"

  - id: "02-update-readme"
    description: "README 업데이트"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Update README.md with examples')"

  - id: "03-validate-examples"
    description: "코드 예제 검증"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_docs_examples.py"
        - "-v"

# 문서화는 gates 불필요 (선택 사항)

evidence:
  - type: "file"
    path: "docs/openapi.yaml"
    description: "업데이트된 API 스펙"

  - type: "file"
    path: "README.md"
    description: "업데이트된 README"
```

---

### 5. 테스트 작성 (TEST)

**시나리오**: 기존 코드에 테스트 추가 (테스트 커버리지 향상)

```yaml
task_id: "TEST-2025-10-24-05"
title: "결제 모듈 테스트 커버리지 향상"
type: "test"
priority: "high"

description: |
  payment.py 테스트 커버리지 60% → 90%
  - 엣지 케이스 테스트 추가
  - 에러 처리 테스트 추가

acceptance_criteria:
  - "테스트 커버리지 90% 이상"
  - "모든 엣지 케이스 커버"
  - "에러 시나리오 테스트 완료"

commands:
  - id: "01-check-current-coverage"
    description: "현재 커버리지 확인"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_payment.py"
        - "--cov=modules/payment"
        - "--cov-report=term"

  - id: "02-write-tests"
    description: "테스트 작성"
    exec:
      cmd: "python"
      args:
        - "-c"
        - "print('[MANUAL] Write edge case tests')"

  - id: "03-run-tests"
    description: "전체 테스트 실행"
    exec:
      cmd: "pytest"
      args:
        - "tests/test_payment.py"
        - "-v"
        - "--cov=modules/payment"
        - "--cov-report=term"
        - "--cov-report=html"

gates:
  - type: "constitutional"
    articles: ["P8"]  # 테스트 우선
    threshold: 9.0  # 테스트는 높은 기준

evidence:
  - type: "file"
    path: "tests/test_payment.py"
    description: "확장된 테스트 케이스"

  - type: "test_results"
    path: "RUNS/TEST-2025-10-24-05/coverage_report.html"
```

---

## 고급 기능

### 1. Prompt Compression (토큰 최적화)

```yaml
task_id: "FEAT-2025-10-24-06"
title: "AI 프롬프트 압축 적용"

# Prompt 최적화 활성화
prompt_optimization:
  enabled: true
  compression_level: medium  # light, medium, aggressive
  auto_learn: true
  report_path: "RUNS/FEAT-2025-10-24-06/compression_report.json"

commands:
  - id: "01-ai-generation"
    exec:
      cmd: "python"
      args:
        - "scripts/ai_generator.py"
        - "--prompt"
        - "Please implement a comprehensive authentication feature with JWT tokens, refresh tokens, and proper error handling. Make sure to follow SOLID principles and write extensive unit tests."
        # 위 프롬프트가 자동으로 30-50% 압축됨
```

**효과**: 토큰 사용량 30-50% 절감, API 비용 절감

### 2. 인간 승인 게이트

```yaml
task_id: "DEPLOY-2025-10-24-07"
title: "프로덕션 배포"
priority: "critical"

# 인간 승인 필요
human_approval_required: true

commands:
  - id: "01-build"
    exec:
      cmd: "docker"
      args: ["build", "-t", "myapp:latest", "."]

  - id: "02-deploy"
    exec:
      cmd: "kubectl"
      args: ["apply", "-f", "k8s/production.yaml"]

# 승인 방법:
# 1. --plan으로 실행 계획 확인
# 2. echo 'HASH_VALUE' > RUNS/DEPLOY-2025-10-24-07/.human_approved
# 3. 실제 실행
```

### 3. Cost Budget (비용 제한)

```yaml
task_id: "AI-HEAVY-2025-10-24-08"
title: "AI 기반 코드 생성"

# 비용 제한 (API 호출 제한)
cost_budget_usd: 5.00
cost_hard_limit: true  # true면 초과 시 실패, false면 경고만

commands:
  - id: "01-generate"
    exec:
      cmd: "python"
      args: ["scripts/ai_codegen.py", "--budget", "5.00"]
```

---

## YAML 작성 체크리스트

실행 전 다음을 확인하세요:

- [ ] `task_id`가 유일한가? (FEAT/FIX/REFACTOR/DOCS/TEST-YYYY-MM-DD-XX)
- [ ] `title`이 명확한가?
- [ ] `acceptance_criteria`가 구체적인가? (테스트 가능한가?)
- [ ] `commands`의 `cmd`가 ALLOWED_CMDS에 있는가?
- [ ] `gates`의 `articles`가 유효한가? (P1-P13)
- [ ] `evidence` 경로가 존재하거나 생성되는가?
- [ ] 인간 승인이 필요한 경우 `human_approval_required: true`인가?

---

## 실행 방법

### 1. 계획 확인 (Dry-run)

```bash
python scripts/task_executor.py TASKS/FEAT-2025-10-24-01.yaml --plan
```

**출력**:
- 실행될 명령 목록
- 예상 실행 시간
- 비용 추정 (해당되는 경우)

### 2. 실제 실행

```bash
python scripts/task_executor.py TASKS/FEAT-2025-10-24-01.yaml
```

**실행 과정**:
1. YAML 파싱 및 검증
2. Commands 순차 실행
3. Gates 검증
4. Evidence 수집
5. Obsidian 자동 동기화 (3초)

### 3. 결과 확인

```bash
# 통합 로그 뷰어
python scripts/view_logs.py

# 특정 태스크 증거
python scripts/view_logs.py --agent evidence --task-id FEAT-2025-10-24-01

# Dashboard
streamlit run streamlit_app.py
```

---

## 문제 해결

### "Command not in allowlist"

**원인**: ALLOWED_CMDS에 없는 명령 사용

**해결**:
```python
# scripts/task_executor.py
ALLOWED_CMDS = {
    "python", "pytest", "ruff",
    "your_command",  # 추가
}
```

### "YAML parsing failed"

**원인**: YAML 문법 오류

**해결**:
```bash
# YAML 검증
python -c "import yaml; yaml.safe_load(open('TASKS/your_task.yaml'))"
```

### "Gate failed"

**원인**: Constitutional 검증 실패 (품질 점수 < threshold)

**해결**:
1. DeepAnalyzer 리포트 확인: `RUNS/your_task/deep_analysis.json`
2. SOLID/보안 이슈 수정
3. 재실행

---

## 다음 단계

1. **템플릿 복사**: `TASKS/TEMPLATE.yaml` 복사 후 수정
2. **예제 실행**: 위 5가지 예제 중 하나 실행해보기
3. **자동화 적용**: 반복 작업을 YAML로 문서화
4. **지식 자산화**: Obsidian에서 개발일지 확인

**Constitutional Compliance**: 이 가이드는 P1 (YAML 우선) 조항을 강제합니다.

**참고 문서**:
- `TASKS/TEMPLATE.yaml` - 공식 템플릿
- `NORTH_STAR.md` - 프로젝트 방향성 (1분 읽기)
- `config/constitution.yaml` - 전체 헌법 (20분 읽기)
