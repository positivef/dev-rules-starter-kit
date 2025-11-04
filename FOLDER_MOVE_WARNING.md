# ⚠️ 폴더 이동 시 주의사항

## 🚫 문제: 가상환경 설치 후 폴더 이동

### 왜 문제가 되나요?
Python 가상환경(.venv)은 **절대 경로**를 내부에 저장합니다.
```
예시:
.venv/Scripts/activate 파일 내부:
VIRTUAL_ENV="C:\Projects\my-project\.venv"  # 절대 경로!
```

폴더를 이동하면 이 경로가 깨져서 가상환경이 작동하지 않습니다.

## ✅ 올바른 순서

### 방법 1: 이동 먼저, 설치 나중에 (권장) ✨
```bash
# 1. 압축 해제
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"

# 2. 폴더 이름 변경 및 최종 위치로 이동 (먼저!)
move project-template D:\MyProjects\my-awesome-app
cd D:\MyProjects\my-awesome-app

# 3. 이동 완료 후 가상환경 생성
python -m venv .venv
.venv\Scripts\activate

# 4. 패키지 설치
pip install -r requirements.txt
```

### 방법 2: 원하는 위치에서 바로 압축 해제
```bash
# 1. 먼저 원하는 위치로 이동
cd D:\MyProjects

# 2. ZIP 파일 복사
copy C:\Users\user\Documents\GitHub\dev-rules-starter-kit\project-template-enterprise.zip .

# 3. 압축 해제
powershell -Command "Expand-Archive project-template-enterprise.zip . -Force"

# 4. 폴더 이름 변경
move project-template my-awesome-app
cd my-awesome-app

# 5. 가상환경 생성 및 설치
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 🔧 이미 설치한 후 이동해야 한다면?

### 해결책: 가상환경 재생성
```bash
# 1. 폴더 이동
move C:\old-location\my-project D:\new-location\my-project
cd D:\new-location\my-project

# 2. 기존 가상환경 삭제
rmdir /s /q .venv

# 3. 새로 가상환경 생성
python -m venv .venv
.venv\Scripts\activate

# 4. 패키지 재설치
pip install -r requirements.txt
```

## 📊 비교표

| 시나리오 | 결과 | 해결책 |
|---------|------|--------|
| 이동 → 설치 | ✅ 정상 작동 | 권장 방법 |
| 설치 → 이동 | ❌ 가상환경 깨짐 | 재설치 필요 |
| 설치 → 복사 | ❌ 가상환경 깨짐 | 새 위치에서 재설치 |

## 💡 Pro Tips

### 1. 프로젝트 템플릿 관리
```bash
# 템플릿은 여러 곳에서 사용 가능
C:\Templates\project-template-enterprise.zip  # 원본 보관

# 새 프로젝트마다
copy C:\Templates\project-template-enterprise.zip D:\Project1\
copy C:\Templates\project-template-enterprise.zip E:\Project2\
# 각 위치에서 압축 해제 후 설치
```

### 2. 이동 가능한 구조 만들기
```bash
# requirements.txt는 이동 가능!
# .venv만 재생성하면 됨

프로젝트 구조:
my-project/
├── scripts/           # ✅ 이동 가능
├── dashboards/        # ✅ 이동 가능
├── src/              # ✅ 이동 가능
├── requirements.txt   # ✅ 이동 가능
└── .venv/            # ❌ 이동 불가 (재생성 필요)
```

### 3. Git으로 관리하는 경우
```bash
# .gitignore에 .venv 포함 (기본 포함됨)
# 다른 PC에서 clone 후:
git clone <repository>
cd my-project
python -m venv .venv        # 각 PC에서 생성
.venv\Scripts\activate
pip install -r requirements.txt  # 동일한 패키지 설치
```

## ⚠️ 흔한 실수들

### ❌ 잘못된 방법
```bash
# USB에서 가상환경 설치 후 PC로 복사
E:\my-project\.venv\  # USB에서 설치
copy E:\my-project C:\  # PC로 복사 → 가상환경 깨짐!
```

### ✅ 올바른 방법
```bash
# USB에는 소스코드만, PC에서 가상환경 생성
copy E:\my-project C:\  # 소스코드만 복사
cd C:\my-project
python -m venv .venv    # PC에서 새로 생성
.venv\Scripts\activate
pip install -r requirements.txt
```

## 🎯 한 줄 요약

> **"폴더 최종 위치 정한 후 → 가상환경 생성 → 패키지 설치"**

순서만 지키면 아무 문제 없습니다!

## 📝 체크리스트

폴더 이동 시:
- [ ] 최종 위치 결정
- [ ] 폴더 이동/이름 변경 완료
- [ ] 기존 .venv 삭제 (있다면)
- [ ] python -m venv .venv (새로 생성)
- [ ] .venv\Scripts\activate
- [ ] pip install -r requirements.txt
- [ ] python src\app.py (테스트)

---
**기억하세요**: requirements.txt만 있으면 어디서든 같은 환경을 재현할 수 있습니다!
