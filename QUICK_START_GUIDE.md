# 빠른 시작 가이드 (Quick Start Guide)

새 프로젝트를 1분 안에 시작하는 4가지 방법

## 🚀 방법 1: 자동 스크립트 (추천! ⭐)

**가장 쉽고 빠릅니다 - 단 1분!**

### Windows
```bash
cd C:\Users\user\Documents\GitHub\dev-rules-starter-kit

# 방법 A: 배치 파일 사용
new-project.bat my-new-app

# 방법 B: Python 스크립트 직접 실행
python scripts/init_new_project.py my-new-app
```

### Linux/Mac
```bash
cd ~/Documents/GitHub/dev-rules-starter-kit

python scripts/init_new_project.py my-new-app
```

### 옵션
```bash
# 다른 위치에 생성
python scripts/init_new_project.py blog-app --path D:/Projects

# 최소 설정 (가벼움)
python scripts/init_new_project.py api-server --minimal

# 전체 설정 (모든 도구)
python scripts/init_new_project.py enterprise-app --full
```

### 자동으로 해주는 것
- ✅ 폴더 구조 생성 (src/, tests/, scripts/, config/)
- ✅ 필수 파일 복사 (constitution.yaml, .gitignore, CLAUDE.md)
- ✅ Python 가상환경 생성 (.venv)
- ✅ 의존성 자동 설치 (Flask, PyYAML, Ruff)
- ✅ 간소화된 Constitution 설정 (Level 1)
- ✅ Git 초기화 및 첫 커밋
- ✅ 샘플 Flask 웹앱 생성
- ✅ README.md 생성

### 다음 단계
```bash
cd my-new-app
.venv\Scripts\activate  # Windows
python src/app.py
# http://localhost:5000 방문
```

---

## 📦 방법 2: ZIP 템플릿

**USB로 이동 가능, 팀 공유 가능**

### 1. ZIP 템플릿 생성 (한 번만)
```bash
cd dev-rules-starter-kit
python scripts/create_template_zip.py
# → project-template.zip 생성됨 (37KB)
```

### 2. 새 프로젝트 시작 (매번)
```bash
# ZIP 압축 풀기
unzip project-template.zip

# 폴더 이름 변경
mv project-template my-new-app
cd my-new-app

# 설정 수정
notepad config/constitution.yaml  # project: "my-new-app"
notepad .env                      # PROJECT_NAME=my-new-app

# Python 환경 설정
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Git 초기화
git init
git add .
git commit -m "feat: initialize my-new-app"
```

### 장점
- ✅ 인터넷 없이 사용 가능
- ✅ USB에 저장 가능
- ✅ 팀원에게 공유 가능
- ✅ 간단한 압축 파일 (37KB)

---

## 📁 방법 3: 템플릿 폴더 복사

**가장 빠름 (30초)**

### 1. 템플릿 준비 (한 번만)
```bash
# my-awesome-app을 템플릿으로 보관
cd C:\Users\user\Documents\GitHub
move my-awesome-app project-template
```

### 2. 새 프로젝트 시작 (매번)
```bash
# Windows
xcopy project-template my-new-app /E /I
cd my-new-app

# Linux/Mac
cp -r project-template my-new-app
cd my-new-app

# 설정 수정
notepad config/constitution.yaml  # project name
notepad .env                      # PROJECT_NAME
notepad README.md                 # 프로젝트 설명

# .venv는 재생성
rmdir /S /Q .venv  # Windows
rm -rf .venv       # Linux/Mac

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Git 재초기화
rmdir /S /Q .git   # Windows
rm -rf .git        # Linux/Mac

git init
git checkout -b main
git add .
git commit -m "feat: initialize my-new-app"
```

### 장점
- ✅ 가장 빠름
- ✅ 로컬에서 즉시 사용

### 단점
- ⚠️ 수동 수정 필요

---

## 🎨 방법 4: Git Clone (GitHub 사용 시)

**협업 팀에게 좋음**

### 1. 템플릿 저장소 만들기 (한 번만)
```bash
cd my-awesome-app
git remote add origin https://github.com/yourusername/constitution-template.git
git push -u origin main
```

### 2. 새 프로젝트 시작 (매번)
```bash
# Clone
git clone https://github.com/yourusername/constitution-template.git my-new-app
cd my-new-app

# 원격 저장소 변경
git remote remove origin
git remote add origin https://github.com/yourusername/my-new-app.git

# 설정 수정
notepad config/constitution.yaml
notepad .env

# Python 환경
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Push
git push -u origin main
```

---

## 📊 방법 비교

| 방법 | 시간 | 자동화 | 이동성 | 난이도 |
|-----|------|--------|--------|--------|
| **자동 스크립트** | 1분 | 100% | 로컬 | ⭐ 매우 쉬움 |
| **ZIP 템플릿** | 2분 | 50% | USB 가능 | ⭐⭐ 쉬움 |
| **폴더 복사** | 30초 | 10% | 로컬 | ⭐⭐⭐ 보통 |
| **Git Clone** | 2분 | 50% | 온라인 | ⭐⭐ 쉬움 |

---

## ✅ 추천

### 1인 개발자 (혼자 작업)
→ **방법 1: 자동 스크립트** 또는 **방법 2: ZIP 템플릿**

### 팀 개발 (2-5명)
→ **방법 4: Git Clone** (공유 쉬움)

### 프리랜서 (여러 프로젝트)
→ **방법 1: 자동 스크립트** (가장 빠름)

### 오프라인 환경
→ **방법 2: ZIP 템플릿** (USB 이동)

---

## 🎯 실전 예제

### 시나리오 1: 급하게 프로토타입 만들기
```bash
# 1분 안에
python scripts/init_new_project.py quick-prototype
cd quick-prototype
.venv\Scripts\activate
python src/app.py
# 끝! 코딩 시작
```

### 시나리오 2: 클라이언트 미팅용 데모
```bash
# ZIP 템플릿 활용
unzip project-template.zip
mv project-template client-demo
cd client-demo
# ... 설정 후 개발
```

### 시나리오 3: 팀 프로젝트 시작
```bash
# Git 템플릿 사용
git clone https://github.com/team/template.git new-project
cd new-project
# ... 설정 후 협업
```

---

## 🆘 문제 해결

### "python not found"
```bash
# Python 경로 확인
where python
# 또는 전체 경로 사용
C:\Python313\python.exe scripts/init_new_project.py my-app
```

### "Permission denied"
```bash
# 관리자 권한으로 실행
# 또는 다른 폴더에 생성
python scripts/init_new_project.py my-app --path C:/Projects
```

### ZIP 압축이 안 풀려요
```bash
# Windows 내장 압축 해제 사용
# 또는 7-Zip, WinRAR 사용
```

---

## 📚 다음 단계

프로젝트 생성 후:
1. [README.md](README.md) - 프로젝트 구조 이해
2. [CLAUDE.md](CLAUDE.md) - AI 개발 가이드
3. [config/constitution.yaml](config/constitution.yaml) - 규칙 커스터마이징

질문이 있으면:
- GitHub Issues
- 팀 채널
- 문서 확인

---

**Happy Coding! 🚀**
