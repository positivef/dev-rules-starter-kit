# Spec-Kit Integration Guide

**새로 추가된 기능**: Specification-Driven Development (SDD) 워크플로우

이 문서는 dev-rules-starter-kit에 통합된 GitHub Spec-Kit 기능을 설명합니다.

---

## 🎯 Spec-Driven Development (SDD) 개요

### 철학

```
기존: 코드가 왕 → 문서는 코드를 안내
SDD:  스펙이 왕 → 코드는 스펙의 표현

핵심 변화:
- PRD가 구현을 "가이드"하는 것이 아니라 "생성"
- 기술 계획이 코딩을 "안내"하는 것이 아니라 "생산"
- 스펙 = 실행 가능한 artifact (executable specification)
```

### 6단계 워크플로우

```bash
/speckit-constitution  # 1. 프로젝트 헌법 (10개 조항)
/speckit-specify       # 2. 기능 스펙 (what/why)
/speckit-plan          # 3. 기술 계획 (how)
/speckit-tasks         # 4. 작업 분해
/speckit-implement     # 5. 구현 실행
```

---

## 🏛️ Constitution (10개 조항)

모든 개발은 `/memory/constitution.md`의 10개 조항을 준수해야 합니다:

| 조항 | 원칙 | 핵심 요구사항 |
|------|------|--------------|
| I | Library-First | 모든 기능은 독립 라이브러리로 |
| II | CLI Interface | 모든 라이브러리는 CLI 노출 |
| III | Test-First (TDD) | 테스트 작성 → 승인 → 실패 → 구현 |
| IV | Integration-First | 실제 환경 테스트 (mocking 최소화) |
| V | Windows Encoding | 코드에 emoji 금지 (cp949 호환) |
| VI | Observability | 구조화된 로깅 (JSON) |
| VII | Simplicity | 최대 3개 프로젝트 (YAGNI) |
| VIII | Anti-Abstraction | 프레임워크 직접 사용 |
| IX | SDD | 스펙 → 계획 → 작업 → 구현 |
| X | Conventional Commits | Semantic Versioning |

---

## 📋 명령어 상세

### 1. /speckit-constitution

프로젝트 헌법 생성 또는 업데이트

```bash
# Claude Code에서 실행
/speckit-constitution

# AI가 자동으로:
# - /memory/constitution.md 생성/업데이트
# - 버전 관리 (Semantic Versioning)
# - Sync Impact Report 생성
```

**생성 파일**:
- `/memory/constitution.md` - 10개 조항 + 거버넌스 규칙

---

### 2. /speckit-specify

자연어 설명으로 기능 스펙 생성

```bash
# Claude Code에서 실행
/speckit-specify "Add user authentication with OAuth2"

# AI가 자동으로:
# 1. 브랜치 생성: feat/user-auth
# 2. 디렉토리 생성: specs/feat-user-auth/
# 3. spec.md 작성 (User Stories + Acceptance Criteria)
# 4. 품질 체크리스트 생성
```

**생성 파일**:
```
specs/feat-user-auth/
├── spec.md                    # 기능 스펙
└── checklists/
    └── requirements.md        # 품질 체크리스트
```

**spec.md 구조**:
```markdown
# Feature Specification: User Authentication

## User Story 1 - Basic Login (Priority: P1) 🎯 MVP
**Why this priority**: Core functionality
**Independent Test**: User can login with email/password
**Acceptance Scenarios**:
1. Given valid credentials, When user logs in, Then dashboard displayed
2. Given invalid credentials, When user logs in, Then error message shown

## User Story 2 - OAuth2 Integration (Priority: P2)
...

## Success Criteria
- SC-001: Users can complete login in under 30 seconds
- SC-002: System supports 1000 concurrent login attempts
```

---

### 3. /speckit-plan

스펙을 기술 구현 계획으로 변환

```bash
# Claude Code에서 실행
/speckit-plan "FastAPI + SQLAlchemy + PostgreSQL"

# AI가 자동으로:
# 1. Constitutional Gates 검증
# 2. 기술 스택 문서화
# 3. 데이터 모델 추출
# 4. API 계약 생성
# 5. 검증 시나리오 작성
```

**생성 파일**:
```
specs/feat-user-auth/
├── plan.md                    # 기술 구현 계획
├── research.md                # 기술 결정 근거
├── data-model.md              # 엔티티 정의
├── quickstart.md              # 검증 시나리오
└── contracts/                 # API 스펙
    ├── auth.openapi.yaml
    └── user.openapi.yaml
```

**plan.md 구조**:
```markdown
# Implementation Plan: User Authentication

## Phase -1: Constitutional Gates
### Article VII: Simplicity (Pass/Fail)
- [ ] Using ≤3 projects? YES
- [ ] No future-proofing? YES

### Article VIII: Anti-Abstraction (Pass/Fail)
- [ ] Using framework directly? YES

## Technical Context
**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLAlchemy, Passlib
**Storage**: PostgreSQL
**Testing**: pytest

## Project Structure
src/
├── models/user.py
├── services/auth.py
└── routers/auth.py
```

---

### 4. /speckit-tasks

계획을 실행 가능한 작업으로 분해

```bash
# Claude Code에서 실행
/speckit-tasks

# AI가 자동으로:
# 1. User Story별 Phase 생성
# 2. 병렬화 가능 작업 [P] 표시
# 3. 의존성 그래프 생성
# 4. MVP 스코프 제안
```

**생성 파일**:
```
specs/feat-user-auth/
└── tasks.md                   # 실행 작업 목록
```

**tasks.md 구조**:
```markdown
# Tasks: User Authentication

## Phase 1: Setup
- [ ] T001 Create project structure
- [ ] T002 Initialize FastAPI dependencies
- [ ] T003 [P] Configure linting

## Phase 2: Foundational (BLOCKING)
- [ ] T004 Setup PostgreSQL schema
- [ ] T005 [P] Implement JWT token service

## Phase 3: User Story 1 (P1) 🎯 MVP
**Goal**: Basic email/password authentication
**Independent Test**: User can login successfully

### Implementation
- [ ] T010 [P] [US1] Create User model in src/models/user.py
- [ ] T011 [P] [US1] Create AuthService in src/services/auth.py
- [ ] T012 [US1] Implement /login endpoint in src/routers/auth.py

## Dependencies
- Setup (Phase 1): No dependencies
- Foundational (Phase 2): Depends on Setup - BLOCKS all stories
- User Story 1 (Phase 3): Depends on Foundational

## Parallel Opportunities
- Tasks T010, T011 can run in parallel (different files)
```

---

### 5. /speckit-implement

작업 목록을 실제로 실행

```bash
# Claude Code에서 실행
/speckit-implement

# AI가 자동으로:
# 1. 체크리스트 상태 확인
# 2. Constitutional 준수 검증
# 3. Phase별 순차 실행
# 4. [P] 작업 병렬 실행
# 5. 완료 작업 [X] 체크
```

**실행 흐름**:
```
1. Checklist 검증 → 불완전하면 STOP
2. Setup Phase → Project initialization
3. Foundational Phase → Core infrastructure
4. User Story 1 → MVP implementation
5. User Story 2 → Additional features
6. Polish Phase → Final touches
```

---

## 🎯 실제 사용 예시

### 예시 1: 새 API 기능 추가

```bash
# 1. 스펙 작성
/speckit-specify "Add product search API with filters"

# AI 출력:
# ✅ Created branch: feat/product-search-api
# ✅ Generated specs/feat-product-search-api/spec.md
# ✅ 3 User Stories identified (P1-P3)
# ❓ Clarifications needed:
#    Q1: Search algorithm (full-text vs fuzzy)?
#    Q2: Filter types (price range, categories, ratings)?

# 사용자 답변:
# Q1: A (full-text with Elasticsearch)
# Q2: A (all three filter types)

# 2. 기술 계획
/speckit-plan "FastAPI + Elasticsearch + Redis caching"

# AI 출력:
# ✅ Constitutional Gates: ALL PASS
# ✅ Generated plan.md, research.md, data-model.md
# ✅ Generated contracts/product-search.openapi.yaml

# 3. 작업 분해
/speckit-tasks

# AI 출력:
# ✅ Generated tasks.md
# ✅ 15 tasks total (5 parallel opportunities)
# ✅ MVP: User Story 1 only (Basic search)

# 4. 구현
/speckit-implement

# AI 출력:
# ✅ Phase 1: Setup complete (T001-T003)
# ✅ Phase 2: Foundational complete (T004-T007)
# 🚧 Phase 3: User Story 1 in progress...
#    ✅ T010 [P] [US1] ProductSearch model created
#    ✅ T011 [P] [US1] SearchService created
#    ✅ T012 [US1] /search endpoint implemented
# ✅ All tests passing (coverage: 92%)
```

---

## 💡 기존 시스템과의 통합

### TaskExecutor와의 비교

| 기능 | TaskExecutor (기존) | Spec-Kit (신규) |
|------|---------------------|-----------------|
| 작업 정의 | YAML | Markdown |
| 워크플로우 | 단일 실행 | 6단계 (specify → implement) |
| 검증 | 수동 | Constitutional Gates 자동 |
| 병렬화 | 없음 | [P] 마커 자동 인식 |
| 문서 생성 | 개발일지만 | spec, plan, tasks, contracts 전체 |

### 통합 사용 예시

```bash
# Spec-Kit으로 계획 수립
/speckit-specify "Feature X"
/speckit-plan "Tech stack Y"
/speckit-tasks

# TaskExecutor로 실행 (선택적)
python scripts/task_executor.py specs/feat-x/tasks.md

# 또는 Spec-Kit으로 직접 실행
/speckit-implement
```

---

## 📂 파일 구조

```
dev-rules-starter-kit/
├── memory/                          # NEW
│   └── constitution.md              # 프로젝트 헌법
│
├── .claude/                         # UPDATED
│   └── commands/                    # NEW Spec-Kit 명령어
│       ├── speckit-constitution.md
│       ├── speckit-specify.md
│       ├── speckit-plan.md
│       ├── speckit-tasks.md
│       └── speckit-implement.md
│
├── templates/                       # NEW
│   ├── spec-template.md
│   ├── plan-template.md
│   ├── tasks-template.md
│   └── checklists/
│       └── checklist-template.md
│
└── specs/                           # NEW (기능별 생성)
    └── feat-example/
        ├── spec.md
        ├── plan.md
        ├── tasks.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── contracts/
        │   └── api.openapi.yaml
        └── checklists/
            └── requirements.md
```

---

## ⚙️ 설정

### Constitution 커스터마이징

```bash
# 1. Constitution 열기
vim memory/constitution.md

# 2. 조항 수정 (예: Article V - Windows Encoding)
# 프로젝트가 Linux만 지원한다면 완화 가능

# 3. 버전 업데이트
# Version: 1.0.0 → 1.1.0 (MINOR: 조항 수정)

# 4. 검증
/speckit-constitution
```

### 템플릿 커스터마이징

```bash
# 1. 스펙 템플릿 수정
vim templates/spec-template.md

# 2. 섹션 추가/제거
# 예: "Security Requirements" 섹션 추가

# 3. 다음 스펙 생성 시 자동 적용
/speckit-specify "New feature"
```

---

## 🔍 트러블슈팅

### 문제 1: Constitutional Gate 실패

```bash
# 증상
/speckit-plan
# ERROR: Article VII: Simplicity gate failed
#        - Using 5 projects (limit: 3)

# 해결책 1: 프로젝트 구조 단순화 (권장)
# 5개 → 3개 프로젝트로 통합

# 해결책 2: 예외 정당화
# plan.md에 Complexity Tracking 섹션 추가:
## Complexity Tracking
| Violation | Why Needed | Alternative Rejected Because |
|-----------|------------|------------------------------|
| 5 projects | Microservices architecture required | Monolith insufficient for scale |
```

### 문제 2: 체크리스트 불완전

```bash
# 증상
/speckit-implement
# WARNING: Some checklists incomplete. Proceed anyway? (yes/no)

# 원인
specs/feat-x/checklists/requirements.md에 미완료 항목 존재

# 해결책
vim specs/feat-x/checklists/requirements.md
# 모든 [ ] → [X]로 변경 또는 실제 검증 완료
```

### 문제 3: [P] 병렬화 미작동

```bash
# 증상
/speckit-implement
# Tasks T010, T011 marked [P] but running sequentially

# 원인
두 작업이 동일 파일을 수정하거나 의존성 존재

# 해결책
tasks.md 수정:
# 잘못된 예
- [ ] T010 [P] [US1] Create User model in src/models/user.py
- [ ] T011 [P] [US1] Add User methods in src/models/user.py  # ❌ 같은 파일

# 올바른 예
- [ ] T010 [P] [US1] Create User model in src/models/user.py
- [ ] T011 [P] [US1] Create Auth service in src/services/auth.py  # ✅ 다른 파일
```

---

## 📊 효과 측정

### Spec-Kit 도입 전후 비교

| 단계 | Before (수동) | After (Spec-Kit) | 절감 |
|------|--------------|-----------------|------|
| 스펙 작성 | 2-3시간 | 5분 | 96% |
| 기술 설계 | 2-3시간 | 5분 | 96% |
| 작업 분해 | 1-2시간 | 3분 | 97% |
| Constitutional 검증 | 30분 (수동) | 자동 | 100% |
| **합계** | **6-9시간** | **15분** | **97%** |

---

## 🔗 관련 문서

- [GitHub Spec-Kit 공식 문서](https://github.com/github/spec-kit)
- [Specification-Driven Development 철학](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Constitution 예제](./memory/constitution.md)
- [템플릿 구조](./templates/)

---

**버전**: 1.0.0
**통합일**: 2025-10-20
**다음 리뷰**: 2026-01-20 (Quarterly)
