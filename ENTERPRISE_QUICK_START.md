# Enterprise Template 빠른 시작 가이드

## 1. ZIP 파일로 새 프로젝트 시작 (5분)

### Step 1: 프로젝트 폴더 생성
```bash
# 원하는 위치로 이동
cd C:\Users\user\Documents\GitHub

# 새 프로젝트 폴더 생성
mkdir my-enterprise-app
cd my-enterprise-app
```

### Step 2: Enterprise ZIP 압축 해제
```bash
# Enterprise ZIP 파일 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip .

# 압축 해제
# Windows: 우클릭 → "압축 풀기"
# 또는 PowerShell:
Expand-Archive -Path project-template-enterprise.zip -DestinationPath .

# 폴더명 변경
move project-template my-enterprise-app
cd my-enterprise-app
```

### Step 3: 프로젝트 설정 커스터마이징
```bash
# 1. Constitution 수정
notepad config\constitution.yaml
# project: "my-enterprise-app" 로 변경

# 2. 환경변수 설정
notepad .env
# PROJECT_NAME=my-enterprise-app 로 변경
# OBSIDIAN_VAULT_PATH=C:/Users/user/Documents/ObsidianVault
```

### Step 4: Python 환경 설정
```bash
# Python 가상환경 생성
python -m venv .venv

# 활성화
.venv\Scripts\activate

# 의존성 설치 (Enterprise 전체 패키지)
pip install -r requirements.txt
```

### Step 5: Git 초기화
```bash
git init
git add .
git commit -m "feat: initialize enterprise project with Constitution framework"
```

### Step 6: 실행 테스트
```bash
# Flask 웹앱 실행
python src/app.py
# http://localhost:5000 접속

# Streamlit 대시보드 실행
streamlit run dashboards/constitution_dashboard.py
# http://localhost:8501 접속

# CLI 도구 테스트
python src/cli/main.py --help
```

## 2. 배치 파일로 자동 설정 (1분)

### 한 줄 명령어로 Enterprise 프로젝트 생성
```bash
# dev-rules-starter-kit 폴더에서
python scripts/init_new_project.py my-enterprise-app --full

# 또는 배치 파일 사용
new-enterprise-project.bat my-enterprise-app
```

## 3. Enterprise 기능 활용하기

### 🎯 핵심 도구 사용법

#### 1. Task Executor (YAML 기반 실행)
```yaml
# TASKS/my-feature.yaml
task_id: "FEAT-2024-11-01"
title: "새 기능 개발"
commands:
  - exec: ["python", "scripts/deep_analyzer.py"]
  - exec: ["pytest", "tests/"]
```

```bash
# 실행
python scripts/task_executor.py TASKS/my-feature.yaml
```

#### 2. 성능 최적화 도구
```bash
# 코드 분석 (SOLID, 보안, 환각 체크)
python scripts/deep_analyzer.py

# 캐시 최적화
python scripts/smart_cache_manager.py

# 병렬 실행
python scripts/enhanced_task_executor_v2.py TASKS/parallel-tasks.yaml
```

#### 3. 대시보드 모니터링
```bash
# Session 모니터링
streamlit run dashboards/session_dashboard.py --server.port 8501

# Lock 상태 모니터링
streamlit run dashboards/lock_dashboard.py --server.port 8502

# Constitution 준수 모니터링
streamlit run dashboards/constitution_dashboard.py --server.port 8503
```

#### 4. Obsidian 지식관리
```bash
# 자동 동기화 설정
python scripts/install_obsidian_auto_sync.py

# 수동 동기화
python scripts/obsidian_bridge.py sync
```

## 4. Enterprise 전용 워크플로우

### 🚀 Multi-Agent 협업 (3-4 AI 세션)
```bash
# Agent 1: Frontend
python scripts/agent_sync.py --agent frontend --acquire

# Agent 2: Backend
python scripts/agent_sync.py --agent backend --acquire

# Agent 3: Testing
python scripts/agent_sync.py --agent testing --acquire

# 상태 모니터링
python scripts/agent_sync_status.py
streamlit run scripts/lock_dashboard_streamlit.py
```

### 📊 전체 시스템 분석
```bash
# Constitutional 검증
python scripts/constitutional_validator.py --strict

# 팀 통계 집계
python scripts/team_stats_aggregator.py

# Critical 파일 감지
python scripts/critical_file_detector.py
```

### 🔧 자동화 설정
```bash
# Pre-commit hooks 설치
pre-commit install

# Code review hook 설치
python scripts/install_code_review_hook.py

# TDD 강제
python scripts/tdd_enforcer.py --enable
```

## 5. 프로젝트 구조

```
my-enterprise-app/
├── config/
│   └── constitution.yaml     # 프로젝트 규칙 (커스터마이징 필수)
├── scripts/                  # 136개 도구 (모두 포함)
│   ├── task_executor.py
│   ├── deep_analyzer.py
│   ├── obsidian_bridge.py
│   └── ... (133개 더)
├── dashboards/               # 8개 대시보드
│   ├── constitution_dashboard.py
│   ├── session_dashboard.py
│   └── lock_dashboard.py
├── src/
│   ├── app.py               # Flask 웹앱
│   └── cli/
│       └── main.py          # CLI 도구
├── tests/                   # 테스트
├── TASKS/                   # YAML contracts
├── RUNS/                    # 실행 증거
├── .env                     # 환경 설정 (수정 필수)
├── requirements.txt         # 모든 의존성
└── README.md               # 프로젝트 문서
```

## 6. 첫 번째 작업 시작

### Option A: 간단한 Flask 웹앱
```bash
python src/app.py
# http://localhost:5000
```

### Option B: YAML Contract 실행
```bash
# TASKS 폴더에 YAML 생성
echo "task_id: TEST-001" > TASKS/test.yaml
echo "title: First test" >> TASKS/test.yaml

# 실행
python scripts/task_executor.py TASKS/test.yaml
```

### Option C: 대시보드로 모니터링
```bash
streamlit run dashboards/constitution_dashboard.py
# 브라우저에서 프로젝트 상태 확인
```

## 7. Enterprise 특별 기능

### 🎯 136개 스크립트 중 주요 도구:

#### 실행 & 자동화
- `task_executor.py` - YAML 기반 실행
- `enhanced_task_executor_v2.py` - 병렬 실행
- `multi_agent_sync.py` - 다중 AI 협업
- `auto_setup.py` - 자동 환경 설정

#### 분석 & 최적화
- `deep_analyzer.py` - 코드 품질 분석
- `critical_file_detector.py` - 핵심 파일 감지
- `convergence_monitor.py` - 성능 수렴 체크
- `performance_optimizer.py` - 성능 최적화

#### 지식 관리
- `obsidian_bridge.py` - Obsidian 동기화
- `context_provider.py` - 컨텍스트 관리
- `session_manager.py` - 세션 상태 관리

#### AI 지원
- `ai_auto_recovery.py` - AI 자동 복구
- `prompt_engineering_coach.py` - 프롬프트 최적화
- `codex_auto_init.py` - Codex 통합

## 8. 팁 & 트릭

### 빠른 시작
```bash
# 1줄로 모든 대시보드 실행
python dashboards/run_dashboard.py

# 병렬로 모든 테스트 실행
python scripts/parallel_processor.py --tests

# 전체 프로젝트 분석
python scripts/deep_analyzer.py --full
```

### 문제 해결
```bash
# Constitutional 위반 체크
python scripts/constitutional_validator.py

# 세션 복구
python scripts/session_manager.py restore

# AI 자동 복구
python scripts/ai_auto_recovery.py
```

## 9. 실제 사용 예시

### 새 기능 개발 워크플로우
```bash
# 1. Feature branch 생성
git checkout -b feature/awesome-feature

# 2. YAML contract 작성
cat > TASKS/awesome-feature.yaml << EOF
task_id: "FEAT-$(date +%Y%m%d)"
title: "Awesome feature implementation"
gates:
  - type: "constitutional"
    articles: ["P4", "P5", "P8"]
commands:
  - exec: ["python", "scripts/test_generator.py", "src/awesome.py"]
  - exec: ["python", "scripts/deep_analyzer.py", "src/awesome.py"]
  - exec: ["pytest", "tests/test_awesome.py"]
EOF

# 3. 실행
python scripts/task_executor.py TASKS/awesome-feature.yaml

# 4. 모니터링
streamlit run dashboards/session_dashboard.py

# 5. 커밋
git add .
git commit -m "feat: implement awesome feature with full validation"
```

## 10. 다음 단계

1. **프로젝트별 커스터마이징**
   - `config/constitution.yaml` 수정
   - `.env` 환경변수 설정
   - 불필요한 스크립트 제거 (선택적)

2. **팀 설정**
   - Git repository 생성
   - CI/CD 파이프라인 설정
   - 팀원 교육

3. **프로덕션 준비**
   - requirements.txt 최적화
   - Docker 컨테이너화
   - 배포 스크립트 작성

---

Enterprise 템플릿은 즉시 사용 가능한 완전한 개발 환경입니다!
모든 도구가 포함되어 있으므로 바로 개발을 시작할 수 있습니다.
