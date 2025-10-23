# 신규 프로젝트에 Dev Rules Starter Kit 적용하기

**대상**: Cursor, Claude Code, GitHub Copilot 등 AI 코딩 도구로 새 프로젝트 시작할 때

---

## 🎯 이 가이드의 목적

Vibe Coding (AI와 협업)으로 신규 프로젝트 개발 시, Constitution 기반 개발 체계를 적용하는 방법

---

## 📋 준비물

1. **이 스타터킷** (다운로드 또는 Fork)
2. **AI 코딩 도구** (Cursor, Claude Code, GitHub Copilot 중 택1)
3. **새 프로젝트 아이디어**

---

## 🚀 빠른 시작 (5분)

### Step 1: 스타터킷 복사

```bash
# Option A: 템플릿으로 사용 (추천)
cd /path/to/your/new-project
curl -L https://github.com/positivef/dev-rules-starter-kit/archive/refs/heads/main.zip -o starter-kit.zip
unzip starter-kit.zip
cp -r dev-rules-starter-kit-main/* .
rm -rf dev-rules-starter-kit-main starter-kit.zip

# Option B: Git으로 직접 클론
git clone https://github.com/positivef/dev-rules-starter-kit.git my-new-project
cd my-new-project
rm -rf .git  # 기존 Git 히스토리 제거
git init     # 새 Git 저장소 초기화
```

### Step 2: 프로젝트명 교체

```bash
# 프로젝트명 자동 교체 (setup.sh 사용)
./setup.sh --project-name "MyAwesomeProject"

# 또는 수동 교체
find . -type f -name "*.md" -exec sed -i 's/Dev Rules Starter Kit/MyAwesomeProject/g' {} +
find . -type f -name "*.yaml" -exec sed -i 's/dev-rules-starter-kit/my-awesome-project/g' {} +
```

### Step 3: Constitution 커스터마이징 (선택)

```bash
# config/constitution.yaml 열기
code config/constitution.yaml

# P1-P13 조항 중:
# - 필요 없는 조항 제거 (P13 프로세스 준수)
# - 새 조항 추가 (P13 프로세스 준수)
# - 프로젝트에 맞게 수정
```

---

## 🤖 AI 도구별 설정

### Option 1: Cursor (추천)

**장점**: AI 컨텍스트 관리 우수, Composer 기능

#### 1. Cursor Rules 설정

```bash
# .cursor/rules/ 디렉토리에 규칙 파일 생성
mkdir -p .cursor/rules
cp .cursor/rules/README.md.template .cursor/rules/README.md
```

**`.cursor/rules/project-rules.md`** 생성:
```markdown
# MyAwesomeProject - Cursor Rules

## Constitution 준수 필수

이 프로젝트는 Constitution 기반 개발 체계를 따릅니다.

### 작업 시작 전 체크리스트

1. **NORTH_STAR.md 읽기** (1분)
2. **Constitution 조항 확인** (config/constitution.yaml)
3. **TASK_TEMPLATE.md 작성** (.github/TASK_TEMPLATE.md)

### Constitution 13개 조항

[P1] YAML 계약서 우선: TASKS/*.yaml 먼저 작성
[P2] 증거 기반 개발: 모든 실행 결과 RUNS/에 기록
[P3] 지식 자산화: Obsidian 자동 동기화
[P4] SOLID 원칙: DeepAnalyzer로 검증
[P5] 보안 우선: DeepAnalyzer로 검증
[P6] 품질 게이트: Quality Score ≥ 7.0
[P7] Hallucination 방지: 추측 금지, 증거 기반
[P8] 테스트 우선: pytest, coverage ≥ 90%
[P9] Conventional Commits: feat/fix/docs 등
[P10] Windows 인코딩: UTF-8 강제
[P11] 원칙 충돌 검증: 과거 지시와 충돌 시 리마인드
[P12] 트레이드오프 분석: Option A vs B 제시
[P13] 헌법 수정 검증: 조항 추가/제거 시 타당성 검증

### 코딩 스타일

- Python: Black, Ruff, Type hints
- Commit: Conventional Commits
- Test: pytest, ≥90% coverage
- Docs: Markdown, 한글/영어 병행

### 금지 사항

- [ ] TODO 주석 (구현 완료 필수)
- [ ] 추측 기반 코드 (P7 위반)
- [ ] 테스트 없는 기능 (P8 위반)
- [ ] 문서 없는 기능 (P3 위반)

### AI 작업 플로우

1. 사용자 요청 → NORTH_STAR.md 확인
2. Constitution 조항 매핑 (P1-P13 중)
3. TASK_TEMPLATE.md 작성
4. TaskExecutor로 실행 (YAML 계약서)
5. 결과 자동 기록 (RUNS/)
6. Obsidian 동기화 (P3)
```

#### 2. Cursor Composer 사용법

```
1. Cmd/Ctrl + I → Composer 열기
2. "NORTH_STAR.md와 Constitution 기반으로 [기능] 구현해줘" 입력
3. AI가 자동으로 Constitution 조항 매핑
4. TASK_TEMPLATE.md 생성 → YAML 계약서 작성 → 실행
```

---

### Option 2: Claude Code

**장점**: Constitution 기반 사고에 최적화

#### 1. CLAUDE.md 설정

```bash
# .claude/CLAUDE.md 파일 생성
cp CLAUDE.md.template .claude/CLAUDE.md
```

**`.claude/CLAUDE.md`** 수정:
```markdown
# MyAwesomeProject - Claude Instructions

## 프로젝트 정체성

이 프로젝트는 Constitution 기반 개발 체계를 따릅니다.

**필수 읽기**:
- NORTH_STAR.md (1분)
- config/constitution.yaml (15분)
- .github/TASK_TEMPLATE.md (5분)

## Constitution 준수 방법

### 작업 시작 전

1. NORTH_STAR.md 읽기
2. Constitution 조항 확인 (P1-P13)
3. TASK_TEMPLATE.md 작성

### 작업 중

1. P7 (Hallucination 방지): 추측 금지, 증거 기반
2. P11 (원칙 충돌): 과거 지시와 충돌 시 리마인드
3. P12 (트레이드오프): Option A vs B 분석

### 작업 후

1. P2 (증거 기반): RUNS/에 결과 기록
2. P3 (지식 자산화): Obsidian 동기화
3. P6 (품질 게이트): Quality Score ≥ 7.0

## 코딩 원칙

- SOLID 원칙 (P4)
- 보안 우선 (P5)
- 테스트 우선 (P8)
- Conventional Commits (P9)

## 7계층 아키텍처

[새 프로젝트에 맞게 수정]

Layer 1: Constitution (헌법)
Layer 2: Execution (TaskExecutor)
Layer 3: Analysis (DeepAnalyzer)
Layer 4: Optimization (Cache)
Layer 5: Evidence (자동 기록)
Layer 6: Knowledge Asset (ObsidianBridge)
Layer 7: Visualization (Dashboard)
```

#### 2. Claude Code 사용법

```bash
# 1. Claude Code 실행
claude

# 2. 프로젝트 열기
cd /path/to/my-new-project

# 3. 작업 요청
"NORTH_STAR.md를 기준으로 [기능]을 구현해줘.
Constitution P[X] 조항을 따라야 해."

# 4. Constitution 자동 준수
Claude가 자동으로:
- TASK_TEMPLATE.md 작성
- YAML 계약서 생성
- TaskExecutor 실행
- 결과 기록
```

---

### Option 3: GitHub Copilot

**장점**: VS Code 통합, 빠른 자동완성

#### 1. Copilot Instructions 설정

```bash
# .github/copilot-instructions.md 생성
cp .github/copilot-instructions.md.template .github/copilot-instructions.md
```

**`.github/copilot-instructions.md`** 수정:
```markdown
# MyAwesomeProject - GitHub Copilot Instructions

## Constitution 기반 개발

이 프로젝트는 Constitution (config/constitution.yaml) 기반입니다.

### 코딩 시 체크리스트

- [ ] NORTH_STAR.md 확인
- [ ] Constitution 조항 매핑 (P1-P13)
- [ ] SOLID 원칙 준수 (P4)
- [ ] 보안 검증 (P5)
- [ ] 테스트 작성 (P8)
- [ ] Conventional Commits (P9)

### 자동완성 컨텍스트

- Python: Type hints 필수
- Docstring: Google style
- Error handling: 구체적 예외 타입
- Logging: structured logging

### 금지 패턴

- TODO 주석 (구현 완료 필수)
- Magic numbers (상수화)
- Global variables (의존성 주입)
- Hardcoded secrets (환경변수)
```

#### 2. GitHub Copilot 사용법

```python
# 1. VS Code에서 파일 열기
# 2. 주석으로 의도 작성 + Tab

# Constitution P4 (SOLID) 준수: 단일 책임 원칙
# User 데이터를 관리하는 클래스
class UserManager:
    # Copilot이 자동완성

# 3. Copilot Chat 사용
# Ctrl/Cmd + I → "Constitution P8 기준으로 이 함수 테스트 작성해줘"
```

---

## 📝 실전 예시: 새 프로젝트 시작하기

### 시나리오: "할일 관리 앱" 만들기

#### Step 1: 프로젝트 초기화 (5분)

```bash
# 1. 스타터킷 복사
git clone https://github.com/positivef/dev-rules-starter-kit.git todo-app
cd todo-app
rm -rf .git
git init

# 2. 프로젝트명 교체
./setup.sh --project-name "TodoApp" --language python --framework fastapi

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Obsidian 경로 설정
echo "OBSIDIAN_VAULT_PATH=/path/to/your/vault" > .env
```

#### Step 2: NORTH_STAR.md 수정 (2분)

```markdown
# NORTH_STAR - TodoApp

## 우리가 만드는 것

**"할일 관리 앱"**

Constitution 기반으로 개발된 FastAPI + React 할일 관리 시스템

### 핵심 기능
1. 할일 추가/수정/삭제 (CRUD)
2. 카테고리 분류
3. 우선순위 설정
4. 마감일 알림

### 우리가 만드는 것이 **아닌** 것
- ❌ 복잡한 프로젝트 관리 도구
- ❌ 팀 협업 기능
- ❌ 타임트래킹

## 7계층 아키텍처

Layer 1: Constitution (헌법)
Layer 2: Execution (TaskExecutor)
Layer 3: Business Logic (TodoService)
Layer 4: Data Access (TodoRepository)
Layer 5: Evidence (Logging)
Layer 6: Knowledge Asset (ObsidianBridge)
Layer 7: API + Frontend
```

#### Step 3: Constitution 커스터마이징 (5분)

**`config/constitution.yaml`** 수정:

```yaml
constitution:
  project: "TodoApp"
  version: "1.0.0"
  philosophy: |
    Constitution 기반 할일 관리 앱.
    모든 기능은 P1-P13 조항을 따릅니다.

articles:
  - id: "P1"
    name: "YAML 계약서 우선"
    # ... (기존 내용 유지)

  # P14 추가 (프로젝트 특화)
  - id: "P14"
    name: "마감일 알림 우선"
    category: "business"
    priority: "high"
    principle: |
      모든 할일에는 마감일이 있어야 하며,
      마감일 3일 전 알림을 보내야 한다.
    requirements:
      - desc: "마감일 필수 입력"
        mandatory: true
      - desc: "3일 전 알림 자동 전송"
        automated: true
```

#### Step 4: 첫 기능 개발 (Cursor 예시)

**Cursor Composer에서**:

```
@NORTH_STAR.md @config/constitution.yaml

Constitution 기반으로 다음 기능을 구현해줘:

1. 할일 CRUD API (FastAPI)
   - POST /todos: 할일 생성
   - GET /todos: 할일 목록
   - PUT /todos/{id}: 할일 수정
   - DELETE /todos/{id}: 할일 삭제

2. Constitution 준수:
   - P1: TASKS/todo-crud.yaml 먼저 작성
   - P4: SOLID 원칙 (Repository 패턴)
   - P5: 입력 검증 (Pydantic)
   - P8: pytest 테스트
   - P9: Conventional Commits

3. 7계층:
   - Layer 3: TodoService (비즈니스 로직)
   - Layer 4: TodoRepository (데이터 접근)
   - Layer 7: FastAPI 엔드포인트
```

**AI가 자동 생성**:

1. `TASKS/todo-crud.yaml` (P1)
2. `src/services/todo_service.py` (Layer 3)
3. `src/repositories/todo_repository.py` (Layer 4)
4. `src/api/todo_routes.py` (Layer 7)
5. `tests/test_todo_service.py` (P8)
6. Git commit (P9)

#### Step 5: TaskExecutor로 실행 (P1, P2)

```bash
# 1. YAML 계약서 실행
python scripts/task_executor.py TASKS/todo-crud.yaml

# 2. 증거 자동 기록 (P2)
# RUNS/todo-crud-20251024/
#   ├── evidence.json
#   └── execution_log.txt

# 3. Obsidian 자동 동기화 (P3)
# ~/ObsidianVault/TodoApp/
#   └── 개발일지/2025-10-24 TODO CRUD 구현.md
```

#### Step 6: 품질 검증 (P6)

```bash
# DeepAnalyzer로 P4, P5, P7 검증
python scripts/deep_analyzer.py src/

# TeamStatsAggregator로 P6 점수 계산
python scripts/team_stats_aggregator.py

# Quality Score ≥ 7.0 확인
# {
#   "quality_score": 8.2,
#   "solid_score": 8.5,
#   "security_score": 7.8,
#   "hallucination_risk": 0.1
# }
```

---

## 🔄 개발 워크플로우

### 일일 루틴

```bash
# 1. 아침: NORTH_STAR.md 읽기 (1분)
cat NORTH_STAR.md

# 2. 작업 시작: TASK_TEMPLATE.md 작성 (5분)
cp .github/TASK_TEMPLATE.md TASKS/today-feature.md
# Constitution 조항 매핑, 7계층 위치 명시

# 3. AI에게 작업 요청
# Cursor/Claude/Copilot에게:
# "@TASKS/today-feature.md 기준으로 구현해줘"

# 4. TaskExecutor 실행 (P1, P2)
python scripts/task_executor.py TASKS/today-feature.yaml

# 5. 품질 검증 (P6)
python scripts/deep_analyzer.py src/
pytest --cov

# 6. 커밋 (P9)
git add .
git commit -m "feat(feature): add today feature"
# Pre-commit hooks 자동 실행

# 7. Obsidian 확인 (P3)
# 자동 동기화된 개발 일지 확인
```

---

## 💡 팁 & 트릭

### AI에게 효과적으로 요청하기

#### ❌ 나쁜 예
```
"로그인 기능 만들어줘"
```

#### ✅ 좋은 예
```
@NORTH_STAR.md @config/constitution.yaml

Constitution 기반으로 로그인 기능 구현해줘:

1. Constitution 조항:
   - P1: TASKS/auth-login.yaml 먼저 작성
   - P4: SOLID (Service/Repository 분리)
   - P5: 보안 (bcrypt, JWT)
   - P8: pytest 테스트 (≥90% coverage)

2. 7계층 위치:
   - Layer 3: AuthService
   - Layer 4: UserRepository
   - Layer 7: FastAPI /auth/login

3. 제외 사항:
   - OAuth (나중에 추가)
   - 2FA (Phase 2)

4. 성공 기준:
   - JWT 토큰 발급 성공
   - Quality Score ≥ 7.0
   - 모든 테스트 통과
```

---

### Constitution 조항 활용

#### P11 (원칙 충돌) 활용 예시

```
AI에게: "대시보드에 화려한 애니메이션 추가해줘"

AI 응답 (P11 적용):
"⚠️ P11 원칙 충돌 감지

과거 원칙 (NORTH_STAR.md):
- 이 프로젝트: 할일 관리 '앱'
- 화려한 UI: 범위 밖

대안:
- Option A: 최소한 애니메이션 (로딩 스피너만)
- Option B: 애니메이션 없음 (단순함 유지)

추천: Option A (사용성 개선)"
```

#### P12 (트레이드오프) 활용 예시

```
AI에게: "실시간 동기화 기능 추가할까?"

AI 응답 (P12 적용):
"P12 트레이드오프 분석:

Option A: WebSocket 실시간 동기화
- 장점: 즉시 반영, UX 좋음
- 단점: 복잡도 +50%, 서버 부하 ↑
- ROI: 멀티 디바이스 사용자만 혜택

Option B: 폴링 (30초마다)
- 장점: 단순함, 서버 부하 ↓
- 단점: 30초 지연
- ROI: 대부분 사용자에게 충분

추천: Option B (KISS 원칙)
Phase 2에서 Option A 재검토"
```

---

## 📊 진행 상황 추적

### Dashboard 활용

```bash
# Streamlit 대시보드 실행
streamlit run streamlit_app.py

# 확인 가능한 항목:
# - Constitution 준수율
# - Quality Score
# - 테스트 Coverage
# - P4 (SOLID) 점수
# - P5 (보안) 점수
# - P6 (품질 게이트) 통과 여부
```

### Obsidian 자동 동기화

```bash
# ObsidianBridge 설정 확인
cat .env | grep OBSIDIAN_VAULT_PATH

# 자동 생성되는 파일:
# ~/ObsidianVault/TodoApp/
#   ├── 개발 일지/
#   │   ├── 2025-10-24 TODO CRUD 구현.md
#   │   └── 2025-10-25 마감일 알림 추가.md
#   ├── 아키텍처/
#   │   └── 7계층 구조.md
#   └── Constitution/
#       └── 조항별 준수 현황.md
```

---

## 🚨 문제 해결

### "Constitution이 너무 복잡해요"

**해결**: 필요한 조항만 사용

```yaml
# config/constitution.yaml 간소화
articles:
  - id: "P1"  # YAML 계약서
  - id: "P7"  # Hallucination 방지
  - id: "P8"  # 테스트 우선
  - id: "P9"  # Conventional Commits
  # P2-P6, P10-P13 제거 (프로젝트에 불필요 시)
```

### "AI가 Constitution을 무시해요"

**해결**: 명시적으로 리마인드

```
매 요청마다:
"@config/constitution.yaml 기준으로 [작업]해줘.
특히 P[X] 조항 준수 필수!"
```

### "TaskExecutor가 작동 안해요"

**해결**: 디버그 모드 실행

```bash
# 디버그 모드
python scripts/task_executor.py TASKS/test.yaml --debug

# 로그 확인
cat RUNS/latest/execution_log.txt
```

---

## 📚 학습 자료

### 필수 문서 (순서대로)

1. **NORTH_STAR.md** (1분) - 프로젝트 정체성
2. **README.md** (5분) - 프로젝트 개요
3. **config/constitution.yaml** (15분) - 헌법 전문
4. **.github/TASK_TEMPLATE.md** (5분) - 작업 명세 방법
5. **docs/QUICK_START.md** (10분) - 빠른 시작

### 고급 문서

- **docs/FEEDBACK_GUIDE.md** - 피드백 수집/반영
- **docs/PHASE_E_DECISION.md** - P11/P12 적용 사례
- **docs/RELEASE_AND_OBSERVE.md** - 관찰 모드 가이드

---

## 🎯 체크리스트: 신규 프로젝트 적용

### 초기 설정 (30분)
- [ ] 스타터킷 복사
- [ ] 프로젝트명 교체
- [ ] NORTH_STAR.md 작성
- [ ] Constitution 커스터마이징
- [ ] Obsidian 경로 설정
- [ ] AI 도구 설정 (Cursor/Claude/Copilot)

### 첫 기능 개발 (2시간)
- [ ] TASK_TEMPLATE.md 작성
- [ ] AI에게 구현 요청
- [ ] TaskExecutor 실행
- [ ] 품질 검증 (P6)
- [ ] Obsidian 동기화 확인

### 일일 루틴 확립 (1주일)
- [ ] 아침 NORTH_STAR.md 읽기
- [ ] Constitution 조항 매핑
- [ ] AI와 협업 개발
- [ ] 품질 검증
- [ ] Obsidian 일지 확인

---

## 💡 핵심 원칙

1. **Constitution 중심**: 모든 결정은 헌법 기반
2. **AI는 도구**: Constitution을 강제하는 수단
3. **증거 기반**: 추측 금지, 데이터로 판단
4. **단순함 유지**: YAGNI, KISS 원칙
5. **지속 가능**: 기술부채 관리

---

**이제 Constitution 기반으로 신규 프로젝트를 시작할 준비가 되었습니다!** 🚀

**버전**: 1.0.0
**작성일**: 2025-10-24
**대상**: Vibe Coding 개발자
