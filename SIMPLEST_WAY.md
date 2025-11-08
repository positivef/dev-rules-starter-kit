# 가장 간단한 방법 - 환경변수 설정 없이!

## 🎯 방법 1: ZIP 파일만 사용 (가장 추천!)

환경변수 설정 **전혀 필요 없음!**

### Step 1: ZIP 파일 위치 확인
```
C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip
```

### Step 2: 원하는 곳에 복사
```bash
# 예시 1: D드라이브로 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip D:\

# 예시 2: 바탕화면으로 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip C:\Users\user\Desktop\

# 예시 3: USB로 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip E:\
```

### Step 3: 압축 해제
```bash
# PowerShell에서 압축 해제
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"

# 또는 우클릭 → 압축 풀기
```

### Step 4: 폴더명 변경 후 시작
```bash
# 이름 변경
move project-template my-awesome-app

# 프로젝트 시작
cd my-awesome-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 🎯 방법 2: 배치 파일 전체 경로 사용

환경변수 설정 **필요 없음!**

```bash
# 어디서든 전체 경로로 실행
C:\Users\user\Documents\GitHub\dev-rules-starter-kit\new-enterprise-anywhere.bat my-project

# D드라이브에 생성하고 싶으면
C:\Users\user\Documents\GitHub\dev-rules-starter-kit\new-enterprise-anywhere.bat my-project D:\Projects
```

## 🎯 방법 3: 바로가기 만들기

환경변수 대신 **바로가기 사용!**

1. `new-enterprise-anywhere.bat` 우클릭
2. "보내기" → "바탕 화면에 바로가기 만들기"
3. 바로가기 더블클릭으로 실행

## ❌ 환경변수가 필요한 경우 (선택사항)

**오직 이럴 때만 필요:**
```bash
# 짧은 명령어로 어디서든 실행하고 싶을 때만
new-enterprise-anywhere my-project  # 이렇게 쓰고 싶으면 PATH 추가 필요
```

대부분의 경우 필요 없음!

## 📊 결론

| 추천도 | 방법 | 환경변수 | 난이도 |
|-------|------|---------|--------|
| ⭐⭐⭐⭐⭐ | ZIP 복사 | ❌ 불필요 | 매우 쉬움 |
| ⭐⭐⭐⭐ | 전체 경로 사용 | ❌ 불필요 | 쉬움 |
| ⭐⭐⭐ | 바로가기 | ❌ 불필요 | 쉬움 |
| ⭐⭐ | PATH 추가 | ✅ 필요 | 복잡 |

## 🎯 한 줄 요약

**ZIP 파일만 복사해서 압축 풀면 끝! 환경변수 설정 필요 없음!**

```bash
# 이것만 기억하세요
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip .
```
