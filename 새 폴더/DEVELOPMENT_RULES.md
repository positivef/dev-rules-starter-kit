# Development Rules & Standards

이 문서는 프로젝트의 개발 규칙과 표준을 정의합니다. 모든 개발자(AI 포함)는 이 규칙을 따라야 합니다.

**Note**: 이 파일은 dev-rules-starter-kit 템플릿입니다. `setup.sh`를 실행하면 PROJECT_NAME이 자동으로 치환됩니다.

---

## 📁 문서 생명주기 관리

### claudedocs/ 디렉토리 구조

```
claudedocs/
├── 00_ACTIVE/              # 현재 참조 중인 핵심 문서
│   ├── CURRENT_STATUS.md   # 프로젝트 현재 상태
│   ├── ARCHITECTURE.md     # 최신 아키텍처 문서
│   └── DEPLOYMENT.md       # 최신 배포 가이드
│
├── analysis/               # 분석 보고서 (3개월 보관)
│   ├── 2025-10/           # 월별 정리
│   └── 2025-09/
│
├── reports/               # 성능/백테스트 보고서 (6개월 보관)
│   ├── backtest/
│   └── performance/
│
└── archive/               # 3개월 이상 된 문서 (참조용)
    └── 2025-Q3/
```

### 문서 정리 규칙

**매월 초 (1-5일)**:
```bash
# 1. 3개월 이상 된 분석 보고서 아카이브
find claudedocs/analysis -name "*.md" -mtime +90 -exec mv {} claudedocs/archive/2025-Q3/ \;

# 2. 6개월 이상 된 아카이브 삭제
find claudedocs/archive -type d -mtime +180 -exec rm -rf {} \;

# 3. 중복 문서 정리 (수동 검토)
# - STATUS, SUMMARY 등 유사 이름 파일 통합
```

**파일명 규칙**:
```
분석 보고서: YYYYMMDD_주제_분석.md
예: 20251012_메모리최적화_분석.md

상태 보고서: CURRENT_주제_STATUS.md
예: CURRENT_SCHEDULER_STATUS.md

백테스트: backtest_YYYYMMDD_HHMMSS.md
예: backtest_20251012_143022.md
```

---

## 🎯 Git Commit Scope 표준화

### Conventional Commits 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 정의

| Type | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 추가 | `feat(auth): add OAuth2 login` |
| `fix` | 버그 수정 | `fix(api): handle null pointer exception` |
| `docs` | 문서 변경 | `docs(readme): update installation guide` |
| `style` | 코드 포맷팅 (기능 변경 없음) | `style(api): apply PEP 8 formatting` |
| `refactor` | 리팩토링 | `refactor(db): simplify query logic` |
| `perf` | 성능 개선 | `perf(cache): implement Redis caching` |
| `test` | 테스트 추가/수정 | `test(integration): add API endpoint tests` |
| `chore` | 빌드/설정 변경 | `chore(deps): update dependencies` |
| `revert` | 이전 커밋 되돌림 | `revert: feat(auth): add OAuth2 login` |

### Scope 정의 (프로젝트별 커스터마이징 필요)

**기본 제공 Scopes** (13개):
| Scope | 대상 모듈/영역 |
|-------|---------------|
| `api` | API 엔드포인트, 라우터 |
| `db` | 데이터베이스, 스키마 |
| `auth` | 인증, 인가 |
| `ui` | UI 컴포넌트, 프론트엔드 |
| `core` | 핵심 비즈니스 로직 |
| `config` | 설정 파일, 환경변수 |
| `deploy` | 배포 스크립트, Docker, CI/CD |
| `docs` | 문서 파일들 |
| `test` | 테스트 코드 |
| `perf` | 성능 최적화 |
| `security` | 보안 관련 |
| `deps` | 의존성 관리 |
| `build` | 빌드 시스템 |

**프로젝트별 추가 방법**:
```markdown
## Custom Scopes (프로젝트명)

| Scope | 대상 모듈/영역 |
|-------|---------------|
| `payment` | 결제 모듈 (src/payment/*) |
| `notification` | 알림 시스템 (src/notification/*) |
| `analytics` | 분석 엔진 (src/analytics/*) |
```

### Commit Message 예시

**좋은 예**:
```bash
feat(api): add user registration endpoint

- POST /api/users endpoint
- Email validation with regex
- Password hashing with bcrypt

Closes #123
```

**나쁜 예**:
```bash
update code          # ❌ 범위 불명확
fix bug              # ❌ 무엇을 수정했는지 불명확
feat: new feature    # ❌ scope 누락
```

### PR 규칙

모든 PR은 다음을 포함해야 함:
- [ ] 관련 이슈 링크 (`Closes #123`, `Fixes #456`)
- [ ] 변경 사항 요약 (무엇을, 왜, 어떻게)
- [ ] 위험 평가 및 롤백 계획
- [ ] 검증 아티팩트 첨부 (로그, 테스트 결과)
- [ ] Pre-commit 체크리스트 완료

---

## 📊 버전 관리 규칙 (Semantic Versioning)

### 버전 형식

```
MAJOR.MINOR.PATCH-LABEL

예: 1.2.3-beta
```

### 버전 업데이트 기준

| 버전 | 조건 | 예시 |
|------|------|------|
| **PATCH** (1.0.0 → 1.0.1) | 버그 수정, 성능 개선 | 메모리 누수 수정, API 오류 처리 개선 |
| **MINOR** (1.0.0 → 1.1.0) | 새로운 기능 추가 (하위 호환) | 새 API 엔드포인트, 새 UI 컴포넌트 |
| **MAJOR** (1.0.0 → 2.0.0) | 호환성 깨는 변경 | DB 스키마 변경, API 인터페이스 변경 |

### 버전 레이블

| 레이블 | 의미 | 사용 시점 |
|--------|------|----------|
| `-alpha` | 초기 개발 단계 | 기능 개발 중, 불안정 |
| `-beta` | 테스트 단계 | 기능 완료, 테스트 중 |
| `-rc` (Release Candidate) | 출시 후보 | 최종 검증 중 |
| (없음) | 안정 버전 | 프로덕션 배포 가능 |

### 버전 업데이트 절차

1. **버전 결정**:
   ```bash
   # 변경 사항 분석
   git log --oneline v1.0.0..HEAD

   # MAJOR: API 변경? DB 스키마 변경?
   # MINOR: 새 기능 추가?
   # PATCH: 버그 수정만?
   ```

2. **CHANGELOG.md 업데이트**:
   ```markdown
   ## [1.1.0] - 2025-10-18

   ### Added
   - User registration API endpoint (#123)
   - Email validation system

   ### Fixed
   - Memory leak in background worker (#145)

   ### Changed
   - Database connection timeout: 5s → 10s
   ```

3. **Git Tag 생성**:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0: User registration feature"
   git push origin v1.1.0
   ```

---

## 📝 옵시디언 동기화 규칙

### 언제 동기화하는가?

**자동 동기화 대상** (TaskExecutor 사용 시):
- ✅ 중요 작업 완료 시 (>3 파일 변경, 새 기능, 주요 수정)
- ✅ YAML 계약서로 실행한 모든 작업
- ✅ 증거 수집이 필요한 작업

**수동 동기화 대상** (선택 사항):
- 📝 간단한 버그 수정 (1-2 파일)
- 📝 문서 업데이트만
- 📝 설정 파일 변경만

### 동기화 절차

**1. YAML 계약서 작성**:
```yaml
# TASKS/FEAT-2025-10-18-01.yaml
task_id: "FEAT-2025-10-18-01"
title: "Add user registration"
project: "PROJECT_NAME"
priority: "high"
tags: [feature, auth]

commands:
  - id: "01-implement"
    exec:
      cmd: "python"
      args: ["-m", "pytest", "tests/test_registration.py"]

evidence:
  - "src/auth/registration.py"
  - "tests/test_registration.py"
```

**2. 실행 (자동 동기화)**:
```bash
# 플랜 확인
python scripts/task_executor.py TASKS/FEAT-2025-10-18-01.yaml --plan

# 실행 (옵시디언 자동 동기화 3초)
python scripts/task_executor.py TASKS/FEAT-2025-10-18-01.yaml
```

**3. 옵시디언에서 자동 생성**:
- `개발일지/2025-10-18_Add_user_registration.md` ✅
- `TASKS/FEAT-2025-10-18-01.md` (체크리스트 업데이트) ✅
- `MOCs/PROJECT_NAME_개발_지식맵.md` (자동 갱신) ✅

### 시간 절감 효과

**Before (수동)**:
- 개발일지 작성: 10분
- 체크리스트 업데이트: 3분
- MOC 갱신: 5분
- 링크 연결: 2분
- **총 소요: 20분** ⏱️

**After (자동)**:
- TaskExecutor 실행: 3초
- 옵시디언 자동 동기화: 3초
- **총 소요: 3초** ⚡
- **시간 절감: 95%** 🚀

---

## 🚦 Pre-Commit Hooks (Automated & Enforced)

이 프로젝트는 `pre-commit` 프레임워크를 사용하여 모든 커밋에 대해 아래의 규칙을 **자동으로 검사하고 강제합니다.**
`python setup.py` 실행 시 모든 설정이 자동으로 완료됩니다.

### 자동 실행 항목 (모든 커밋 전)

1.  **코드 품질 및 포맷팅 (Ruff)**
    -   Python 코드의 린팅 및 스타일 문제를 자동으로 검사하고 수정합니다.

2.  **커밋 메시지 형식 (Commitlint)**
    -   커밋 메시지가 [Conventional Commits](https://www.conventionalcommits.org/) 표준을 따르는지 검사합니다.

3.  **설정 파일 유효성 검사**
    -   `YAML`, `JSON` 파일의 문법이 올바른지 확인합니다.

4.  **기타 코드 스타일**
    -   파일 끝 개행 문자, 후행 공백 등을 자동으로 수정합니다.
    -   Git 병합 충돌 마커가 커밋되는 것을 방지합니다.

이전의 수동 체크리스트는 이제 시스템에 의해 자동으로 처리되므로, 개발자는 코드 작성과 커밋 메시지에만 집중할 수 있습니다.

### Pre-Push (원격 푸시 전)

```bash
# 1. 전체 테스트
pytest tests/ -v --cov

# 2. 문서 동기화 확인
git status | grep -E "CLAUDE.md|DEVELOPMENT_RULES.md"

# 3. 커밋 메시지 검증
git log --oneline -5 | grep -E "^(feat|fix|docs|style|refactor|perf|test|chore)"
```

---

## 📌 Quick Reference

### 일반적인 작업 흐름

**새 기능 추가**:
```bash
1. 브랜치 생성: git checkout -b feat/feature-name
2. 코드 작성 + 테스트 작성
3. Pre-commit 체크: ruff, pytest
4. 커밋: git commit -m "feat(scope): description"
5. 문서 업데이트: CLAUDE.md
6. Pre-push 체크
7. PR 생성
```

**버그 수정**:
```bash
1. 이슈 확인 및 재현
2. 테스트 케이스 추가 (실패하는)
3. 버그 수정
4. 테스트 통과 확인
5. 커밋: git commit -m "fix(scope): description (#issue)"
6. PATCH 버전 업데이트 검토
```

---

## 🔗 관련 문서

- `CLAUDE.md` - AI 에이전트 개발 가이드
- `AGENTS.md` - Repository 가이드라인
- `.env.example` - 환경 변수 템플릿
- `docs/QUICK_START.md` - 빠른 시작 가이드
- `docs/MULTI_CLI_STRATEGY.md` - 멀티 CLI 전략

---

**버전**: 1.0.0
**최종 업데이트**: 2025-10-18
**검토 주기**: 분기별 (3개월)
