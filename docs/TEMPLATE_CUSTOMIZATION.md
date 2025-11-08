# Template Customization Guide

**Stage 6 Phase 1**: GitHub Template 사용자를 위한 커스터마이징 가이드

**목적**: Template에서 생성한 프로젝트를 자신의 프로젝트로 완전히 변환하기

**소요 시간**: 10-30분 (자동화 스크립트 사용 시 5분)

---

## 빠른 시작 (자동)

```bash
# GitHub Template에서 생성한 저장소 Clone 후
cd my-new-project

# 자동 Setup script 실행
python scripts/setup_new_project.py

# 안내에 따라 프로젝트명, Obsidian 경로 입력
# → 모든 설정이 자동으로 완료됩니다!
```

**자동 처리**:
- ✅ 가상환경 생성
- ✅ 의존성 설치
- ✅ Pre-commit hooks 설치
- ✅ .env 파일 생성
- ✅ 프로젝트 준비 완료

---

## 수동 커스터마이징 (고급)

자동 스크립트가 작동하지 않거나 세밀한 조정이 필요한 경우:

### 필수 항목 (10단계 체크리스트)

#### 1. 프로젝트명 변경 ⭐

**파일**:
- [ ] `.env` - `PROJECT_NAME` 변수
- [ ] `package.json` - `name` 필드 (Semantic Release용)
- [ ] `pyproject.toml` - `[project].name` (선택사항)

```bash
# .env
PROJECT_NAME=MyAwesomeProject

# package.json
{
  "name": "my-awesome-project",
  ...
}
```

#### 2. Python 가상환경 생성

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

#### 3. 의존성 설치

```bash
# Python 패키지
pip install -r requirements.txt

# Node 패키지 (Semantic Release용, 선택사항)
npm install
```

#### 4. Pre-commit hooks 설치

```bash
# Pre-commit 설치
pip install pre-commit

# Hooks 설치
pre-commit install
pre-commit install --hook-type commit-msg
```

#### 5. Obsidian 경로 설정 (선택사항)

**파일**: `.env`

```bash
# Windows
OBSIDIAN_VAULT_PATH=C:\Users\YourName\Documents\ObsidianVault

# Linux/Mac
OBSIDIAN_VAULT_PATH=/Users/YourName/Documents/ObsidianVault
```

**테스트**:
```bash
python scripts/obsidian_bridge.py test
```

#### 6. Git 설정

```bash
# 기본 브랜치 확인
git branch -M main

# Remote 확인
git remote -v

# GitHub 저장소와 연결 확인
git push origin main
```

#### 7. GitHub Actions Secrets 설정

**Repository Settings** → **Secrets and variables** → **Actions**:

- [ ] `GITHUB_TOKEN` (자동 제공됨, 확인만)
- [ ] (선택) `NPM_TOKEN` (npm package 배포 시)

#### 8. README.md 수정

**변경 필요**:
- [ ] Badges URL (`positivef/dev-rules-starter-kit` → 본인 저장소)
- [ ] GitHub Template link
- [ ] 프로젝트 설명 (30초 소개 섹션)

**예시**:
```markdown
# My Awesome Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Template](https://img.shields.io/badge/GitHub-Template-green.svg)](https://github.com/YOUR_USERNAME/my-awesome-project/generate)

## 30초 소개

**My Awesome Project** - 간단한 한 줄 설명

- 주요 기능 1
- 주요 기능 2
- 주요 기능 3
```

#### 9. 첫 커밋 테스트

```bash
# 파일 변경
git add .

# 커밋 (Pre-commit hooks가 자동 실행됨)
git commit -m "feat: initial project customization"

# 출력 확인:
# - Constitution Guard ✅
# - Ruff Linter ✅
# - Commitlint ✅
# - Gitleaks ✅
```

#### 10. GitHub Actions 확인

```bash
# Push
git push origin main

# GitHub 페이지에서 Actions 탭 확인
# - Constitution Check ✅
# - Semantic Release (태그 자동 생성)
```

---

## Constitution 커스터마이징

**파일**: `config/constitution.yaml`

### 조항 추가하기

**사용 사례**: 프로젝트에 특화된 규칙 추가

**예시**: P17 조항 추가 (API 문서화)

```yaml
# config/constitution.yaml

articles:
  # ... 기존 P1-P16 ...

  - id: P17
    name: API Documentation First
    description: 모든 API는 문서를 먼저 작성한 후 구현
    category: process
    enforcement:
      - type: manual
        tool: code_review
    rationale: API 인터페이스 설계 단계에서 문제 발견
    examples:
      - good: "OpenAPI 스펙 작성 → 코드 생성"
      - bad: "코드 작성 → 나중에 문서화"
```

**주의**: P13 조항에 따라 Constitution 수정 시 검증 필요
- 최대 20개 조항 권장
- 기존 조항과 충돌하지 않는지 확인
- 실제로 강제 가능한지 확인

### 조항 비활성화하기

**사용 사례**: 프로젝트에 맞지 않는 조항 제거

**방법 1**: 주석 처리
```yaml
# config/constitution.yaml

articles:
  # P8 테스트 우선 (프로토타입 단계에서는 보류)
  # - id: P8
  #   name: Test-First Development
  #   ...
```

**방법 2**: `enabled: false` 플래그 추가
```yaml
- id: P8
  name: Test-First Development
  enabled: false  # 프로토타입 단계에서 비활성화
  ...
```

**CI/CD 워크플로우에서도 제거**:
```yaml
# .github/workflows/constitution-check.yml

# P8 Test Coverage job 주석 처리 또는 제거
# test-coverage:
#   ...
```

---

## 프레임워크별 커스터마이징

### FastAPI 프로젝트

```bash
# 추가 의존성
pip install fastapi uvicorn sqlalchemy alembic

# 프로젝트 구조
mkdir -p src/api src/models src/schemas
```

### React 프로젝트

```bash
# Create React App
npx create-react-app frontend

# 또는 Next.js
npx create-next-app@latest frontend
```

### Flask 프로젝트

```bash
# 추가 의존성
pip install flask flask-sqlalchemy flask-migrate

# 프로젝트 구조
mkdir -p src/routes src/models src/templates
```

---

## Cursor/Copilot 규칙 커스터마이징

### Cursor Rules

**파일**: `.cursor/rules/`

```bash
# 프로젝트 특화 규칙 추가
cp .cursor/rules/api.md.template .cursor/rules/api.md

# 내용 수정
vim .cursor/rules/api.md
```

### GitHub Copilot Instructions

**파일**: `.github/copilot-instructions.md`

```bash
# Template 복사
cp .github/copilot-instructions.md.template .github/copilot-instructions.md

# 프로젝트 context 추가
vim .github/copilot-instructions.md
```

---

## 문제 해결

### "Setup script가 실패해요"

```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# 가상환경 수동 생성
python -m venv .venv

# 의존성 수동 설치
.venv\Scripts\pip install -r requirements.txt  # Windows
```

### "Pre-commit hooks가 작동하지 않아요"

```bash
# Pre-commit 재설치
pip install --upgrade pre-commit
pre-commit clean
pre-commit install --install-hooks
```

### "Obsidian 동기화가 안 돼요"

```bash
# 경로 확인
echo $OBSIDIAN_VAULT_PATH

# 경로 존재 확인
ls -la "$OBSIDIAN_VAULT_PATH"

# .env 파일 재확인
cat .env | grep OBSIDIAN
```

### "GitHub Actions가 실패해요"

**원인 1**: Secrets 미설정
- GitHub Repository → Settings → Secrets 확인

**원인 2**: 기존 코드 이슈 (Ruff, Test Coverage)
- 로컬에서 먼저 수정: `ruff check .` → 수정 → commit

**원인 3**: Node.js 버전
- `.nvmrc` 확인 (Node 20 필요)

---

## 체크리스트 요약

### 필수 (5분)
- [ ] `python scripts/setup_new_project.py` 실행
- [ ] 프로젝트명 입력
- [ ] 가상환경 활성화
- [ ] 첫 커밋 테스트

### 권장 (10분)
- [ ] Obsidian 경로 설정
- [ ] README.md 30초 소개 수정
- [ ] GitHub Actions 확인

### 선택 (30분)
- [ ] Constitution 커스터마이징
- [ ] Cursor/Copilot 규칙 추가
- [ ] 프레임워크별 추가 설정

---

## 다음 단계

커스터마이징 완료 후:

1. **첫 작업 실행**
   ```bash
   python scripts/task_executor.py TASKS/TEMPLATE.yaml
   ```

2. **Constitution 이해**
   ```bash
   cat config/constitution.yaml
   cat NORTH_STAR.md
   ```

3. **개발 시작**
   ```bash
   # 작업 계약서 작성
   cat > TASKS/FEATURE-001.yaml << EOF
   task_id: "FEATURE-001"
   title: "첫 기능 개발"
   # ...
   EOF

   # 실행
   python scripts/task_executor.py TASKS/FEATURE-001.yaml
   ```

---

**작성자**: AI (Claude) with VibeCoding Enhanced
**프로젝트**: Dev Rules Starter Kit
**Stage**: 6 (Scale) - Phase 1 (Template Packaging)
**버전**: 1.0.0
**마지막 업데이트**: 2025-11-07
