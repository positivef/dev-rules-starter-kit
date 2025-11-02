# 어디서든 Enterprise 프로젝트 시작하기

## 방법 1: ZIP 파일 복사 (가장 쉬움) 🎯

### Step 1: 원하는 위치로 이동
```bash
# 예: D 드라이브의 Projects 폴더
cd D:\Projects

# 또는 바탕화면
cd C:\Users\user\Desktop
```

### Step 2: Enterprise ZIP 복사
```bash
# ZIP 파일 복사
copy "C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip" .
```

### Step 3: 압축 해제 및 이름 변경
```bash
# PowerShell에서 압축 해제
powershell -Command "Expand-Archive -Path project-template-enterprise.zip -DestinationPath . -Force"

# 폴더 이름 변경
move project-template my-new-project
cd my-new-project
```

### Step 4: 프로젝트 설정
```bash
# Python 환경 설정
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Git 초기화
git init
git add .
git commit -m "feat: initialize enterprise project"
```

## 방법 2: 배치 파일 경로 지정 실행 📂

### 어디서든 배치 파일 실행
```bash
# 현재 위치에서 배치 파일 실행 (전체 경로 사용)
C:\Users\user\Documents\GitHub\dev-rules-starter-kit\new-enterprise-project.bat my-project

# 프로젝트가 ..\my-project에 생성됨
```

## 방법 3: 개선된 배치 파일 (경로 선택 가능) 🚀

### new-enterprise-anywhere.bat
```batch
@echo off
REM Enterprise 프로젝트를 원하는 위치에 생성

if "%1"=="" (
    echo Usage: new-enterprise-anywhere.bat PROJECT_NAME [TARGET_PATH]
    echo Example: new-enterprise-anywhere.bat my-app D:\Projects
    exit /b 1
)

set PROJECT_NAME=%1
set TARGET_PATH=%2

REM 경로가 지정되지 않으면 현재 폴더 사용
if "%TARGET_PATH%"=="" (
    set TARGET_PATH=%cd%
)

set STARTER_KIT=C:\Users\user\Documents\GitHub\dev-rules-starter-kit
set TEMPLATE_ZIP=%STARTER_KIT%\project-template-enterprise.zip

echo ===============================================
echo Creating Enterprise Project: %PROJECT_NAME%
echo Location: %TARGET_PATH%\%PROJECT_NAME%
echo ===============================================

REM 1. 타겟 폴더로 이동
cd /d "%TARGET_PATH%"

REM 2. 프로젝트 폴더 생성
echo [1/6] Creating project folder...
if exist "%PROJECT_NAME%" (
    echo ERROR: Project folder already exists!
    exit /b 1
)
mkdir "%PROJECT_NAME%"
cd "%PROJECT_NAME%"

REM 3. 템플릿 복사
echo [2/6] Copying Enterprise template...
copy "%TEMPLATE_ZIP%" . >nul 2>&1

REM 4. 압축 해제
echo [3/6] Extracting template...
powershell -NoProfile -Command "Expand-Archive -Path project-template-enterprise.zip -DestinationPath . -Force"
del project-template-enterprise.zip

REM 5. 폴더 구조 정리
echo [4/6] Organizing project structure...
xcopy /E /I /Y project-template\* . >nul 2>&1
rmdir /S /Q project-template

REM 6. 설정 업데이트
echo [5/6] Updating configuration...
powershell -NoProfile -Command "(Get-Content config\constitution.yaml) -replace 'project: \".*\"', 'project: \"%PROJECT_NAME%\"' | Set-Content config\constitution.yaml"
powershell -NoProfile -Command "(Get-Content .env) -replace 'PROJECT_NAME=.*', 'PROJECT_NAME=%PROJECT_NAME%' | Set-Content .env"

REM 7. Python 환경 설정
echo [6/6] Setting up Python environment...
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Git 초기화
git init >nul 2>&1
git add . >nul 2>&1
git commit -m "feat: initialize %PROJECT_NAME% with Enterprise Constitution framework" >nul 2>&1

echo.
echo ===============================================
echo SUCCESS! Enterprise project created!
echo Location: %TARGET_PATH%\%PROJECT_NAME%
echo ===============================================
echo.
echo Next steps:
echo   1. cd %TARGET_PATH%\%PROJECT_NAME%
echo   2. .venv\Scripts\activate
echo   3. python src\app.py
echo ===============================================
```

## 방법 4: Python 스크립트로 어디서든 생성 🐍

### 어디서든 실행 가능한 Python 명령
```bash
# 현재 폴더에 생성
python C:\Users\user\Documents\GitHub\dev-rules-starter-kit\scripts\init_new_project.py my-project . --full

# D:\Projects에 생성
python C:\Users\user\Documents\GitHub\dev-rules-starter-kit\scripts\init_new_project.py my-project D:\Projects --full

# 바탕화면에 생성
python C:\Users\user\Documents\GitHub\dev-rules-starter-kit\scripts\init_new_project.py my-project C:\Users\user\Desktop --full
```

## 방법 5: 시스템 PATH에 추가 (고급) ⚙️

### 어디서든 명령어로 실행하기

1. **배치 파일을 PATH에 추가**
```bash
# 시스템 환경 변수에 추가
setx PATH "%PATH%;C:\Users\user\Documents\GitHub\dev-rules-starter-kit"
```

2. **이제 어디서든 실행 가능**
```bash
# 어디서든
new-enterprise-project.bat my-project
```

## 🎯 추천 워크플로우

### 가장 실용적인 방법
```bash
# 1. 작업하고 싶은 폴더로 이동
cd D:\MyWorkspace

# 2. ZIP 파일 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip .

# 3. 압축 해제
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"

# 4. 이름 변경 및 시작
move project-template my-awesome-project
cd my-awesome-project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 5. 즉시 개발 시작!
python src\app.py
```

## 💡 팁

1. **USB/클라우드 저장**: ZIP 파일을 USB나 클라우드에 저장해두면 어디서든 사용 가능
2. **네트워크 드라이브**: 팀과 공유하려면 네트워크 드라이브에 ZIP 저장
3. **바로가기 생성**: 자주 사용하는 위치에 배치 파일 바로가기 생성

## 📦 필요한 파일

Enterprise 프로젝트를 어디서든 시작하려면 이 파일만 있으면 됩니다:
- `project-template-enterprise.zip` (492KB)

이 하나의 ZIP 파일에 136개 Python 스크립트와 8개 대시보드가 모두 포함되어 있습니다!