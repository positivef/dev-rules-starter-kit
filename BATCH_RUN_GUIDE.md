# 배치 파일 실행 가이드

## 방법 1: 명령 프롬프트 (CMD)에서 실행 (권장) ✅

### Step 1: CMD 열기
- Windows + R 키 누르기
- "cmd" 입력 후 Enter
- 또는 시작 메뉴에서 "명령 프롬프트" 검색

### Step 2: 폴더로 이동
```bash
cd C:\Users\user\Documents\GitHub\dev-rules-starter-kit
```

### Step 3: 배치 파일 실행
```bash
new-enterprise-project.bat my-awesome-app
```

## 방법 2: Windows 탐색기에서 실행 🖱️

### Option A: 더블클릭으로 실행 (프로젝트명 직접 입력)
1. Windows 탐색기에서 `dev-rules-starter-kit` 폴더 열기
2. `new-enterprise-project.bat` 파일 더블클릭
3. 검은 창이 열리면 프로젝트 이름 입력 (예: my-awesome-app)
4. Enter 키 누르기

### Option B: 우클릭 메뉴 사용
1. `new-enterprise-project.bat` 파일 우클릭
2. "관리자 권한으로 실행" 선택
3. 프로젝트 이름 입력

## 방법 3: PowerShell에서 실행 💙

### Step 1: PowerShell 열기
- Windows + X → Windows PowerShell 선택
- 또는 시작 메뉴에서 "PowerShell" 검색

### Step 2: 실행
```powershell
cd C:\Users\user\Documents\GitHub\dev-rules-starter-kit
.\new-enterprise-project.bat my-awesome-app
```

## 🚨 주의사항

### 파일 더블클릭 시 문제점:
- 프로젝트 이름을 미리 지정할 수 없음
- 창이 자동으로 닫혀서 결과를 볼 수 없을 수 있음
- 에러 발생 시 메시지를 놓칠 수 있음

### 권장하는 방법:
**CMD 또는 PowerShell에서 실행** - 전체 과정을 볼 수 있고 에러 확인 가능

---

## 💡 쉬운 방법: 바로가기 만들기

### 바탕화면 바로가기 생성:
1. `new-enterprise-project.bat` 우클릭
2. "보내기" → "바탕 화면에 바로 가기 만들기"
3. 바탕화면의 바로가기 우클릭 → "속성"
4. "대상" 끝에 프로젝트명 추가:
   ```
   C:\...\new-enterprise-project.bat my-project
   ```
5. 이제 바로가기 더블클릭으로 실행 가능

## 📝 실제 실행 예시

### CMD에서:
```
C:\Users\user> cd Documents\GitHub\dev-rules-starter-kit
C:\Users\user\Documents\GitHub\dev-rules-starter-kit> new-enterprise-project.bat my-killer-app

===============================================
Creating Enterprise Project: my-killer-app
===============================================
[1/6] Creating project folder...
[2/6] Copying Enterprise template...
[3/6] Extracting template...
[4/6] Organizing project structure...
[5/6] Updating project configuration...
[6/6] Setting up Python environment...

===============================================
SUCCESS! Enterprise project created: my-killer-app
===============================================
```

## 🔥 가장 빠른 방법 (복사-붙여넣기)

### Windows Terminal/CMD 열고:
```bash
# 이 3줄을 그대로 복사-붙여넣기
cd C:\Users\user\Documents\GitHub\dev-rules-starter-kit
new-enterprise-project.bat my-new-project
cd ..\my-new-project
```

끝! 프로젝트가 생성됩니다.