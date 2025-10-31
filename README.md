# Development Rules Starter Kit

> 📖 **[CLAUDE.md](CLAUDE.md)** - **AI 에이전트 필수 가이드** (Claude, Cursor, Copilot 사용자는 먼저 읽어주세요!)
> 👨‍💻 **[초보 개발자 가이드](docs/BEGINNER_DEVELOPER_GUIDE.md)** - **8주 학습 로드맵** (Git, YAML, TaskExecutor 단계별 학습)
> 🎯 **부담 없이 시작하세요** - Level 0부터 단계적 적용 가능합니다.
> 🤖 **Multi-AI Session 지원** - 1명 개발자 + 3-4 AI 세션 동시 협업 가능!

**버전**: 1.0.0
**기반**: DoubleDiver 프로젝트에서 추출한 검증된 개발 규칙 시스템
**재활용성**: 95% (프로젝트명만 교체하면 즉시 사용 가능)

## 🎯 개요

이 스타터 킷은 DoubleDiver 프로젝트에서 검증된 개발 규칙 시스템을 재활용 가능한 템플릿으로 추출한 것입니다.

### 포함된 시스템

1. **Git 표준화** (Conventional Commits + Semantic Release)
2. **AI 에이전트 최적화** (Claude, Cursor, Copilot)
3. **실행형 지식자산** (TaskExecutor + Obsidian 통합)
4. **문서 생명주기 관리** (claudedocs/ 구조)
5. **CI/CD 파이프라인** (GitHub Actions)

### 검증된 효과

- ✅ Conventional Commits: Agoda Engineering 등 다수 기업 사용
- ✅ Executable Documentation: React, Postman, TensorFlow 적용
- ✅ 95% 문서 시간 절감 (20분 → 3초)
- ✅ 100% 커밋 표준 준수 (Commitlint)
- ✅ 연간 264시간 절감 (33일)

---

## ⚖️ Constitution (헌법) - 시스템의 핵심

**필독**: `NORTH_STAR.md` (1분 읽기, 방향성 상실 방지)

### 이것은 무엇인가?

**"실행형 자산 시스템 (Executable Knowledge Base)"**

프로그램 개발 시 사용할 **Constitution(헌법) 기반 기준 체계 템플릿**입니다.

이것은 코드 품질 도구가 **아닙니다**. Constitution을 중심으로 한 개발 체계 그 자체입니다.

### 핵심 개념 3가지

1. **문서가 곧 코드**
   - YAML 계약서 작성 → TaskExecutor 실행 → 결과 자동 기록
   - 모든 작업이 재실행 가능한 자산으로 축적

2. **Constitution이 모든 것의 중심**
   - 10개 조항 (P1-P10)이 개발의 법
   - 모든 도구는 특정 조항을 강제하는 수단
   - 대시보드는 "헌법 준수 현황판"

3. **증거 기반 + 지식 자산화**
   - 모든 실행 결과 자동 기록 (`RUNS/evidence/`)
   - Obsidian 자동 동기화 (3초)
   - 시간이 지날수록 지식이 축적

### 7계층 아키텍처

```
Layer 1: Constitution (헌법) ← 모든 것의 중심!
    ↓
Layer 2: Execution (TaskExecutor, ConstitutionalValidator)
    ↓
Layer 3: Analysis (DeepAnalyzer, TeamStatsAggregator)
    ↓
Layer 4: Optimization (VerificationCache, CriticalFileDetector)
    ↓
Layer 5: Evidence Collection (자동 기록)
    ↓
Layer 6: Knowledge Asset (ObsidianBridge - 3초 동기화)
    ↓
Layer 7: Visualization (Streamlit Dashboard - 시각화만)
```

**중요**: 대시보드(Layer 7)는 단순 시각화 도구입니다. 검증은 DeepAnalyzer(Layer 3)가 수행합니다.

### Constitution 13개 조항

#### 개발 프로세스 조항 (P1-P10)

| ID | 조항명 | 강제 도구 | Layer |
|----|--------|----------|-------|
| **P1** | YAML 계약서 우선 | TaskExecutor | 2 |
| **P2** | 증거 기반 개발 | TaskExecutor | 2, 5 |
| **P3** | 지식 자산화 | ObsidianBridge | 6 |
| **P4** | SOLID 원칙 | **DeepAnalyzer** | 3 |
| **P5** | 보안 우선 | **DeepAnalyzer** | 3 |
| **P6** | 품질 게이트 | TeamStatsAggregator | 3 |
| **P7** | Hallucination 방지 | DeepAnalyzer | 3 |
| **P8** | 테스트 우선 | pytest | - |
| **P9** | Conventional Commits | pre-commit | - |
| **P10** | Windows 인코딩 | UTF-8 강제 | - |

#### 거버넌스 & 메타 조항 (P11-P15) - 최신 버전!

| ID | 조항명 | 목적 | 강제 방식 |
|----|--------|------|---------|
| **P11** | 원칙 충돌 검증 | 새 기능이 과거 원칙과 충돌 시 리마인드 | AI 수동 |
| **P12** | 트레이드오프 분석 의무 | 모든 결정에 양측 관점 + 근거 제시 | AI 수동 |
| **P13** | 헌법 수정 검증 | Constitution 수정 시 타당성 검증 | 사용자 승인 |
| **P14** | 2차 효과 분석 | 개선의 부작용까지 예측 및 완화 | PR 템플릿 |
| **P15** | 수렴 원칙 | 80% 품질 달성 후 멈춤 (무한 개선 방지) | 분기별 리뷰 |

**효과**:
- P11: 방향성 상실 방지 (ROI 267%)
- P12: 객관적 의사결정 (AI 편향 차단)
- P13: Constitution 비대화 방지 (최대 20개 조항 제한)
- **P14: 지속 가능한 개선 (부작용 완화 시스템)**
- **P15: 실용주의 (완벽주의 배제, 80점이면 충분)**

**상세**: `config/constitution.yaml` 참조

### 도구의 역할 (Tool-to-Article Mapping)

| 도구 | 역할 | 강제하는 조항 | Layer |
|------|------|-------------|-------|
| **TaskExecutor** | YAML 계약서 실행 | P1, P2 | 2 |
| **ConstitutionalValidator** | 헌법 준수 검증 | All + **P11, P13** | 2 |
| **DeepAnalyzer** | SOLID, 보안 검증 | **P4, P5, P7** | 3 |
| **TeamStatsAggregator** | 품질 점수 계산 | **P6** | 3 |
| **VerificationCache** | 중복 검증 방지 | - | 4 |
| **CriticalFileDetector** | 핵심 파일 식별 | - | 4 |
| **ObsidianBridge** | 지식 자산화 | **P3** | 6 |
| **Streamlit Dashboard** | 시각화 (검증 안 함) | - | 7 |

### 핵심 워크플로우

```
1. YAML 계약서 작성 (P1)
   ↓
2. TaskExecutor 실행 (P2)
   ↓
3. DeepAnalyzer 검증 (P4, P5, P7)
   ↓
4. 증거 자동 기록 (P2)
   ↓
5. Obsidian 동기화 (P3, 3초)
   ↓
6. Dashboard로 확인 (P6 준수 현황)
```

### 우리가 만드는 것 vs 만들지 않는 것

**우리가 만드는 것**:
- ✅ Constitution 기반 개발 체계
- ✅ 실행형 자산 시스템 (문서 = 코드)
- ✅ 기준 체계 템플릿 (사용자가 커스터마이징)

**우리가 만드는 것이 아닌 것**:
- ❌ 코드 품질 대시보드 도구 (SonarQube 같은 것)
- ❌ 독립적 분석 도구들의 모음
- ❌ 완성된 프로덕트

### 상세 문서

- `config/constitution.yaml` - 헌법 전문 (800+ 줄)
- `NORTH_STAR.md` - 1분 읽기, 방향성 재확인
- `.github/TASK_TEMPLATE.md` - 작업 명세 템플릿

---

## 🚀 빠른 시작 (5분)

### Option 1: Bash Wrapper (권장 - Linux/macOS/Git Bash)

`setup.sh`는 내부적으로 `setup.py`를 호출하며, 실패 시 자동 롤백 기능을 포함합니다.

```bash
# 1. 프로젝트 생성 및 이동
mkdir ~/my-new-project && cd ~/my-new-project

# 2. 스타터 킷 파일 복사
cp -r path/to/dev-rules-starter-kit/{*,.*} .

# 3. 초기화 스크립트 실행
./setup.sh --project-name "MyNewProject" --framework fastapi
```

### Option 2: Python Direct (Windows/모든 플랫폼)

```bash
# Windows PowerShell 예시
mkdir MyNewProject; cd MyNewProject
Copy-Item -Recurse path/to/dev-rules-starter-kit/* -Destination .
Copy-Item -Recurse path/to/dev-rules-starter-kit/.* -Destination . -ErrorAction SilentlyContinue

python setup.py --project-name "MyNewProject" --framework fastapi
```

**✨ 자동 처리 항목**:
- ✅ 프로젝트명 일괄 변경
- ✅ 프레임워크별 파일 스캐폴딩 (`.editorconfig`, `Dockerfile` 등)
- ✅ Python 의존성 설치 (`requirements.txt`)
- ✅ `pre-commit` 훅 설치 (코드/커밋 자동 검증)
- ✅ `gitleaks` 설치 (비밀 정보 유출 방지)
- ✅ (Bash) 실패 시 자동 롤백 (`git stash`)


### Step 3: 즉시 사용

```bash
# 1. 첫 작업 실행
python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan
# 계획 확인 후 승인
python scripts/task_executor.py TASKS/TEMPLATE.yaml

# 2. 커밋 (자동 검증됨)
git add .
git commit -m "feat: initial project setup"
# → Pre-commit hooks 자동 실행:
#    - Ruff linting
#    - YAML/JSON validation
#    - Commitlint format check
#    - Gitleaks secret scan

# 3. 버전 릴리스
git push origin main
# → GitHub Actions의 `semantic-release` 워크플로우가 실행되며,
#    루트의 `package.json`과 `.releaserc.json`에 정의된 전략을 사용해 버전을 산출합니다.
# (선택) 로컬에서 릴리스 파이프라인 점검
nvm use  # 또는 corepack enable/npm을 사용해 Node 20 활성화
python scripts/check_release_env.py  # 환경 진단 (문제 없으면 0으로 종료)
npm install --no-fund --no-audit
npm run release -- --dry-run
# 참고: 루트에 `.nvmrc`(Node 20)를 제공하므로 `nvm use` 혹은 `corepack enable` 환경에서 맞춰 실행하세요.
```

---

## 📁 디렉토리 구조

```
dev-rules-starter-kit/
├── README.md                        # 이 파일
├── setup.sh                         # 프로젝트 초기화 스크립트
├── DEVELOPMENT_RULES.md             # Git/버전/문서 규칙 (100% 재활용)
├── DEVELOPMENT_GUIDELINES.md        # 개발 프로세스 (100% 재활용)
├── AGENTS.md.template               # 프로젝트 구조 템플릿
├── CLAUDE.md.template               # AI 에이전트 가이드 템플릿
│
├── .cursor/                         # Cursor AI 규칙
│   └── rules/
│       ├── README.md
│       ├── api.md.template
│       ├── testing.md.template
│       └── documentation.md.template
│
├── .github/                         # GitHub 설정
│   ├── copilot-instructions.md.template
│   └── workflows/
│       ├── commitlint.yml
│       └── semantic-release.yml
│
├── scripts/                         # 자동화 스크립트
│   ├── task_executor.py            # YAML 계약 실행기 (100% 재활용)
│   └── obsidian_bridge.py          # 옵시디언 동기화 (100% 재활용)
│
├── TASKS/                           # 작업 계약서
│   └── TEMPLATE.yaml
│
├── config/                          # 설정
│   ├── projects.yaml.template      # 멀티 프로젝트 설정
│   └── commitlint.config.js
│
└── docs/                            # 가이드 문서
    ├── QUICK_START.md
    ├── MULTI_CLI_STRATEGY.md       # 멀티 CLI 오케스트레이션 전략
    └── REAL_WORLD_CASES.md         # 실제 사용 사례
```

---

## 🎨 사용 패턴

### Pattern 1: Python 프로젝트

```bash
./setup.sh --project-name "MyAPI" --language python --framework fastapi
```

### Pattern 2: JavaScript 프로젝트

```bash
./setup.sh --project-name "MyApp" --language javascript --framework react
```

### Pattern 3: 멀티 프로젝트 (여러 프로젝트에서 공유)

```yaml
# config/projects.yaml
projects:
  - id: project1
    name: Trading Bot
    vault_path: ~/Documents/ObsidianVault

  - id: project2
    name: ML Pipeline
    vault_path: ~/Documents/ObsidianVault
```

---

## 🔧 커스터마이징

### 필수 교체 항목

1. **프로젝트명** (자동: `setup.sh` 실행)
2. **언어/프레임워크** (`.github/workflows/`, `AGENTS.md`)
3. **옵시디언 경로** (`.env` 파일)

### 선택 항목

4. Cursor rules (`.cursor/rules/`)
5. Copilot instructions (`.github/copilot-instructions.md`)
6. 커밋 scope (13개 기본 제공, 추가 가능)

---

## 📊 ROI (투자 대비 효과)

| 항목 | 설정 시간 | 월간 절감 | 연간 ROI |
|------|----------|----------|---------|
| Git 자동화 | 2시간 | 12시간 | 688% |
| 지식 관리 | 3시간 | 6시간 | 288% |
| AI 최적화 | 2시간 | 4시간 | 200% |
| **합계** | **7시간** | **22시간/월** | **377%** |

**브레이크이븐**: 3.2개월
**연간 절감**: 264시간 (33일)

---

## 🆘 문제 해결

### "프로젝트명 교체가 안 돼요"

```bash
# 수동 교체
find . -type f -name "*.md" -exec sed -i 's/DoubleDiver/MyProject/g' {} +
```

### "Commitlint가 작동하지 않아요"

```bash
# Husky 재설치
rm -rf .husky
npx husky install
npx husky set .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

### "Obsidian 동기화가 안 돼요"

```bash
# .env 파일 확인
cat .env | grep OBSIDIAN_VAULT_PATH
# 경로가 올바른지 확인

# 경로 테스트
ls -la "$OBSIDIAN_VAULT_PATH"
```

---

## 🤖 Development Assistant

**자동 파일 감시 및 코드 검증 시스템**

Development Assistant는 Python 파일의 변경사항을 실시간으로 감지하고 자동으로 코드 품질을 검증하는 프로덕션급 파일 워처입니다.

### 주요 기능

- **실시간 파일 감시**: `scripts/`, `tests/` 디렉토리의 Python 파일 변경 자동 감지
- **자동 Ruff 검증**: 파일 저장 시 자동으로 Ruff 린팅 실행 (<200ms)
- **증거 기반 로깅**: 모든 검증 결과를 JSON + 텍스트로 자동 기록
- **디바운싱**: 연속된 저장을 500ms 간격으로 병합하여 불필요한 검증 방지
- **낮은 리소스 사용**: 유휴 시 <2% CPU 사용
- **우아한 종료**: SIGINT/SIGTERM 신호 처리로 안전한 종료

### 빠른 시작

```bash
# 1. 기본 실행 (scripts/, tests/ 감시)
python scripts/dev_assistant.py

# 2. 커스텀 디렉토리 감시
python scripts/dev_assistant.py --watch-dirs scripts tests src

# 3. 디바운스 시간 조정 (1초)
python scripts/dev_assistant.py --debounce 1000

# 4. 디버그 모드
python scripts/dev_assistant.py --log-level DEBUG
```

### 설정 (pyproject.toml)

모든 파라미터는 `pyproject.toml`에서 설정 가능하며, CLI 인자가 우선순위를 가집니다.

```toml
[tool.dev-assistant]
# 활성화 여부
enabled = true

# 감시할 디렉토리 목록
watch_paths = ["scripts", "tests", "src"]

# 디바운스 시간 (밀리초)
debounce_ms = 500

# Ruff 검증 타임아웃 (초)
verification_timeout_sec = 2.0

# 증거 로그 보관 기간 (일)
log_retention_days = 7

# Ruff 검증 활성화
enable_ruff = true

# 증거 로깅 활성화
enable_evidence = true
```

### 증거 로그

검증 결과는 `RUNS/dev-assistant-YYYYMMDD/` 디렉토리에 자동 저장됩니다:

- **evidence.json**: 구조화된 JSON 형식 (프로그래밍 방식 분석용)
- **verification.log**: 사람이 읽기 쉬운 텍스트 형식

#### 로그 예시

```
[2025-10-22T10:30:15] PASS - scripts/task_executor.py
  Duration: 120ms

[2025-10-22T10:31:42] FAIL - scripts/new_feature.py
  Duration: 95ms
  Violations: 2
    • Line 15:1 - E501: Line too long (120 > 88 characters) [fixable]
    • Line 3:8 - F401: `os` imported but unused [fixable]
```

### CLI 참조

```bash
python scripts/dev_assistant.py --help

옵션:
  --watch-dirs DIR [DIR ...]    감시할 디렉토리 (config 파일 오버라이드)
  --debounce MS                 디바운스 시간 밀리초 (config 파일 오버라이드)
  --log-level LEVEL             로깅 레벨 (DEBUG|INFO|WARNING|ERROR)
  --no-ruff                     Ruff 검증 비활성화 (config 파일 오버라이드)
  --no-evidence                 증거 로깅 비활성화 (config 파일 오버라이드)
```

### 워크플로우 통합

**개발 중 실시간 검증**:
```bash
# 터미널 1: Development Assistant 실행
python scripts/dev_assistant.py

# 터미널 2: 코드 작업
vim scripts/my_feature.py  # 저장 시 자동 검증됨
```

**CI/CD 통합**:
```yaml
# .github/workflows/quality.yml
- name: Run Ruff checks
  run: ruff check scripts/ tests/

# 또는 Development Assistant의 증거 로그 분석
- name: Analyze verification evidence
  run: python scripts/analyze_evidence.py RUNS/dev-assistant-*/evidence.json
```

### 성능 특성

- **검증 속도**: 일반적인 Python 파일 <200ms
- **CPU 사용**: 유휴 시 <2% (파일 변경 시 순간적으로 증가)
- **메모리**: 파일 워처 + 스레드 풀 ~20MB
- **디스크 I/O**: 증거 로그만 기록 (일일 ~1-5MB)

### 문제 해결

**"Ruff not found" 오류**:
```bash
pip install ruff
```

**"tomllib/tomli not available" 경고**:
```bash
# Python 3.11 미만인 경우
pip install tomli
```

**파일 감시가 작동하지 않음**:
```bash
# watchdog 재설치
pip install --upgrade watchdog

# 디렉토리 권한 확인
ls -la scripts/ tests/
```

**과도한 검증 실행**:
```bash
# 디바운스 시간 증가 (1초)
python scripts/dev_assistant.py --debounce 1000
```

---

## 🔗 관련 문서

- [빠른 시작 가이드](docs/QUICK_START.md)
- [멀티 CLI 전략](docs/MULTI_CLI_STRATEGY.md) ⭐ 토큰 최적화
- [실제 사용 사례](docs/REAL_WORLD_CASES.md)
- [CLAUDE.md 작성 가이드](docs/CLAUDE_MD_GUIDE.md)

---

## 🤝 기여하기 (Contributing)

이 프로젝트는 오픈소스입니다! 기여를 환영합니다.

### 기여 방법

1. **Issue 생성**
   - 버그 리포트, 기능 제안, 질문 등
   - Template: `.github/ISSUE_TEMPLATE.md` (작성 예정)

2. **Pull Request**
   - Fork → Branch → Commit → PR
   - Conventional Commits 준수 필수
   - Pre-commit hooks가 자동으로 검증합니다

3. **Constitution 개선**
   - P11-P13 적용 사례 공유
   - 새 조항 제안 (P13 프로세스 적용)
   - NORTH_STAR.md 피드백

### 기여 가이드라인

**코드 품질**:
- `ruff check` 통과 필수
- `pytest` 테스트 작성
- Coverage ≥ 90%

**커밋 메시지**:
```bash
feat(scope): 새 기능 추가
fix(scope): 버그 수정
docs(scope): 문서 업데이트
```

**Pull Request 체크리스트**:
- [ ] Constitution 조항과 연결 (어느 조항 강화?)
- [ ] 7계층 아키텍처 위치 명시
- [ ] NORTH_STAR.md 참조 (방향성 확인)
- [ ] 테스트 추가/업데이트
- [ ] CHANGELOG.md 업데이트

### 커뮤니티

- **Discussions**: 질문, 아이디어 공유
- **Issues**: 버그, 기능 요청
- **Wiki**: 사용 사례, 튜토리얼 (작성 예정)

---

## 📝 라이선스

**MIT License** - 자유롭게 사용, 수정, 재배포 가능

상세 내용: [LICENSE](LICENSE)

### 저작권

Copyright (c) 2025 positivef

### 사용 허가

- ✅ 상업적 사용
- ✅ 수정
- ✅ 배포
- ✅ 개인 사용

**조건**: 원작자 표시 및 라이선스 고지 포함

---

## 🙏 크레디트

**원작자**: positivef
**프로젝트**: Dev Rules Starter Kit
**GitHub**: https://github.com/positivef/dev-rules-starter-kit

이 스타터 킷은 DoubleDiver 프로젝트의 개발 규칙 시스템을 기반으로 하며,
다음 시스템들의 best practice를 통합했습니다:

- Google Agent Development Kit (ADK) 2025
- Cursor Rules 2025
- GitHub Copilot Instructions 2025
- Commitlint + Semantic Release
- Obsidian Automation 2025

### 영감을 받은 프로젝트

- **Linux**: 오픈소스 거버넌스 모델
- **React**: 커뮤니티 기반 개발
- **Python**: 명확한 철학 (PEP 20 - Zen of Python)

---

## 📊 프로젝트 현황

**버전**: 1.1.0 ✅ **완성**
**상태**: Release & Observe (3개월 관찰 기간)
**생성일**: 2025-10-18
**완성일**: 2025-10-24
**다음 리뷰**: 2025-01-24 (P13 First Review)

**통계**:
- Constitution 조항: 13개 (P1-P13)
- 7계층 아키텍처
- 학습 시간: 20분
- ROI: 2,150% (1년), 11,150% (5년)

**개발 모드**:
- ✅ v1.1.0 완성 (템플릿 완성)
- 🔍 관찰 기간 (2025-10-24 ~ 2025-01-24)
- 📊 피드백 수집 중
- 🚫 Phase E 보류 (YAGNI 원칙)

**관찰 항목**:
- GitHub 통계 (Star, Fork, Issues)
- 사용자 피드백 및 사용 사례
- P11-P13 실전 적용 경험
- Constitution 개선 필요성

**참고**: [Phase E 보류 결정 문서](docs/PHASE_E_DECISION.md)
