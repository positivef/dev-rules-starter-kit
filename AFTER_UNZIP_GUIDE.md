# 📦 압축 해제 후 사용 가이드

## 🚀 Quick Start (가장 빠른 시작)

### Step 1: 압축 해제
```bash
# ZIP 파일이 있는 곳에서
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"

# 압축 해제 후 폴더 구조
project-template/
├── scripts/          # 142개 Python 도구
├── dashboards/       # 8개 Streamlit 앱
├── config/           # Constitution 설정
├── src/              # Flask 웹 앱
├── tests/            # 테스트 파일
├── requirements.txt  # 필요한 패키지
└── .env              # 환경 설정
```

### Step 2: 폴더 이름 변경
```bash
# project-template을 원하는 이름으로 변경
move project-template my-awesome-project
cd my-awesome-project
```

### Step 3: Python 가상환경 설정
```bash
# Python 가상환경 생성
python -m venv .venv

# 가상환경 활성화
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

## 🎯 주요 기능 사용법

### 1. Flask 웹 애플리케이션 실행
```bash
# 가상환경 활성화 상태에서
python src\app.py

# 브라우저에서 http://localhost:5000 접속
```

### 2. Streamlit 대시보드 실행
```bash
# Constitution 대시보드
streamlit run dashboards\constitution_dashboard.py

# 세션 관리 대시보드
streamlit run dashboards\session_dashboard.py

# 성능 모니터링
streamlit run dashboards\performance_dashboard.py
```

### 3. Task 실행 시스템
```bash
# YAML 작업 생성
echo task_id: "TASK-001" > TASKS\my-task.yaml
echo title: "My First Task" >> TASKS\my-task.yaml
echo commands: >> TASKS\my-task.yaml
echo   - exec: ["echo", "Hello World"] >> TASKS\my-task.yaml

# Task 실행
python scripts\task_executor.py TASKS\my-task.yaml
```

### 4. 코드 분석 도구
```bash
# 코드 품질 분석
python scripts\deep_analyzer.py

# Constitutional 검증
python scripts\constitutional_validator.py

# 팀 통계 분석
python scripts\team_stats_aggregator.py
```

### 5. 세션 관리
```bash
# 세션 시작
python scripts\session_manager.py start

# 컨텍스트 초기화
python scripts\context_provider.py init

# 세션 저장
python scripts\session_manager.py save
```

## 📁 폴더별 용도

### `/scripts` - 142개 Python 도구
- **실행자**: task_executor.py, enhanced_task_executor_v2.py
- **분석기**: deep_analyzer.py, critical_file_detector.py
- **검증자**: constitutional_validator.py, principle_conflict_detector.py
- **세션관리**: session_manager.py, context_provider.py
- **기타 도구**: 130개+ 유틸리티

### `/dashboards` - 8개 Streamlit 앱
```bash
# 각 대시보드 실행법
streamlit run dashboards\constitution_dashboard.py    # Constitution 상태
streamlit run dashboards\session_dashboard.py         # 세션 관리
streamlit run dashboards\lock_dashboard_streamlit.py  # 잠금 상태
streamlit run dashboards\performance_dashboard.py     # 성능 모니터
streamlit run dashboards\quality_dashboard.py         # 품질 메트릭
streamlit run dashboards\task_dashboard.py           # 작업 상태
streamlit run dashboards\context_dashboard.py        # 컨텍스트
streamlit run dashboards\analytics_dashboard.py      # 종합 분석
```

### `/src` - Flask 웹 애플리케이션
```bash
# 웹 앱 실행
python src\app.py

# CLI 도구
python src\cli\main.py --help
```

### `/config` - 설정 파일
- `constitution.yaml` - Constitution 규칙 설정
- 프로젝트 설정 파일들

## 💡 일반적인 워크플로우

### 개발 시작
```bash
# 1. 가상환경 활성화
.venv\Scripts\activate

# 2. 세션 시작
python scripts\session_manager.py start

# 3. Flask 앱 실행
python src\app.py

# 4. 대시보드 실행 (별도 터미널)
streamlit run dashboards\constitution_dashboard.py
```

### 작업 자동화
```bash
# 1. YAML 작업 정의
notepad TASKS\new-feature.yaml

# 2. 작업 실행
python scripts\task_executor.py TASKS\new-feature.yaml

# 3. 검증
python scripts\constitutional_validator.py
```

### 코드 분석
```bash
# 1. 전체 분석
python scripts\deep_analyzer.py

# 2. 특정 파일 분석
python scripts\deep_analyzer.py src\app.py

# 3. 품질 메트릭
python scripts\team_stats_aggregator.py
```

## 🔧 문제 해결

### pip install 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 패키지 설치
pip install flask streamlit pandas plotly
```

### 가상환경 활성화 안 됨
```bash
# PowerShell 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 시도
.venv\Scripts\activate
```

### 포트 충돌 (5000 사용 중)
```bash
# 다른 포트로 실행
python src\app.py --port 5001

# 또는 .env 파일 수정
echo FLASK_PORT=5001 >> .env
```

## 📊 프로젝트 구조 활용

```
my-awesome-project/
├── .venv/            # 가상환경 (자동 생성됨)
├── TASKS/            # YAML 작업 정의
├── RUNS/             # 실행 기록
│   ├── evidence/     # 실행 증거
│   └── context/      # 세션 컨텍스트
├── scripts/          # 142개 도구
├── dashboards/       # 8개 대시보드
├── src/              # 메인 애플리케이션
├── tests/            # 테스트
└── config/           # 설정
```

## ✅ 체크리스트

압축 해제 후:
- [ ] 폴더 이름 변경
- [ ] 가상환경 생성 (.venv)
- [ ] 가상환경 활성화
- [ ] pip install -r requirements.txt
- [ ] python src\app.py 테스트
- [ ] streamlit run 테스트
- [ ] Git 초기화 (선택)

## 🎯 5분 내 시작하기

```bash
# 전체 과정 (복사해서 실행)
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"
move project-template my-project
cd my-project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\app.py
```

**끝! 이제 모든 기능을 사용할 수 있습니다!**
