# Quick Start Guide (15분 설정)

dev-rules-starter-kit을 새 프로젝트에 적용하는 완전한 가이드입니다.

---

## 📋 Prerequisites

- Git installed
- Python 3.8+ OR Node.js 16+ (depending on your project)
- 15 minutes of your time

---

## 🚀 Step 1: 프로젝트 생성 및 복사 (2분)

```bash
# 1. 새 프로젝트 디렉토리 생성
mkdir ~/my-new-project
cd ~/my-new-project

# 2. dev-rules-starter-kit 복사
cp -r ~/GitHub/dev-rules-starter-kit/* .
cp ~/GitHub/dev-rules-starter-kit/.* . 2>/dev/null || true

# 3. Git 초기화
git init
```

---

## 🔧 Step 2: 프로젝트 설정 (3분)

### Option A: 자동 설정 (권장)

```bash
# setup.sh 실행
chmod +x setup.sh
./setup.sh --project-name "MyNewProject" --language python --framework fastapi
```

### Option B: 수동 설정

```bash
# 1. 프로젝트명 치환
find . -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.py" \) \
  -exec sed -i 's/DoubleDiver/MyNewProject/g' {} +

# 2. .template 파일 활성화
for f in $(find . -name "*.template"); do
  cp "$f" "${f%.template}"
done

# 3. .env 파일 생성
cp .env.example .env
```

---

## 📦 Step 3: 의존성 설치 (5분)

### Python 프로젝트

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 개발 도구 설치 (Commitlint, Husky)
npm install  # package.json에서 commitlint, husky 설치
```

### JavaScript 프로젝트

```bash
# 1. 의존성 설치
npm install

# 2. Husky 설정
npx husky install

# 3. Commit hook 설정
npx husky set .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

---

## ⚙️ Step 4: 환경 설정 (2분)

### .env 파일 수정

```bash
# .env 파일 열기
vim .env  # 또는 선호하는 에디터 사용

# 필수 항목 설정:
PROJECT_NAME=MyNewProject
LANGUAGE=python  # 또는 javascript
FRAMEWORK=fastapi  # 또는 react, express, etc.

# 옵션: Obsidian 통합 (선택 사항)
OBSIDIAN_VAULT_PATH=~/Documents/ObsidianVault
OBSIDIAN_ENABLED=false  # 나중에 true로 변경 가능
```

---

## ✅ Step 5: 검증 (3분)

### 1. Commitlint 테스트

```bash
# 나쁜 커밋 메시지 (실패해야 함)
git add .
git commit -m "test"
# ❌ type must be one of [feat, fix, docs, ...]

# 좋은 커밋 메시지 (성공)
git commit -m "feat(setup): initial project setup with dev-rules-starter-kit"
# ✅ Commit successful
```

### 2. TaskExecutor 테스트

```bash
# 플랜 확인
python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan

# 출력 예시:
# === Execution Plan ===
# Task ID: FEAT-YYYY-MM-DD-01
# Title: Task title
# ...
# 🔐 Plan Hash: a1b2c3d4e5f6g7h8
```

### 3. 파일 구조 확인

```bash
tree -L 2 -a

# 예상 출력:
# .
# ├── .cursor/
# │   └── rules/
# ├── .github/
# │   └── workflows/
# ├── scripts/
# │   ├── task_executor.py
# │   └── obsidian_bridge.py
# ├── TASKS/
# │   └── TEMPLATE.yaml
# ├── DEVELOPMENT_RULES.md
# ├── CLAUDE.md
# └── setup.sh
```

---

## 🎯 Step 6: 첫 작업 실행 (Optional)

### 예제 작업 생성

```bash
# 1. TASKS/FEAT-2025-10-18-01.yaml 생성
cat > TASKS/FEAT-2025-10-18-01.yaml << 'EOF'
task_id: "FEAT-2025-10-18-01"
title: "Test TaskExecutor system"
project: "MyNewProject"
priority: "high"
type: "feature"
tags: [test, automation]

description: |
  Test the TaskExecutor system to verify it works correctly.

acceptance_criteria:
  - "TaskExecutor runs without errors"
  - "Provenance file is generated"
  - "Evidence is collected"

commands:
  - id: "01-test"
    exec:
      cmd: "echo"
      args: ["TaskExecutor working!"]

gates: []

evidence:
  - "TASKS/FEAT-2025-10-18-01.yaml"

provenance:
  evidence_sha256: {}
EOF

# 2. 실행
python scripts/task_executor.py TASKS/FEAT-2025-10-18-01.yaml

# 3. 결과 확인
cat RUNS/FEAT-2025-10-18-01/.state.json
cat RUNS/FEAT-2025-10-18-01/provenance.json
```

---

## 📚 Next Steps

### 1. 문서 커스터마이징

```bash
# 필수 수정 파일:
- CLAUDE.md           # AI 에이전트 가이드 (프로젝트 구조 반영)
- AGENTS.md           # 리포지토리 가이드라인
- DEVELOPMENT_RULES.md  # Git scope 추가/수정
- .cursor/rules/*.md  # Cursor AI 규칙 (도메인별)
- .github/copilot-instructions.md  # GitHub Copilot 컨텍스트
```

### 2. Git Scope 정의

`DEVELOPMENT_RULES.md`에서 프로젝트에 맞는 scope 정의:

```markdown
## Scope 정의

| Scope | 대상 모듈/영역 |
|-------|---------------|
| `api` | `src/api/*`, API 엔드포인트 |
| `db` | `src/database/*`, DB 관련 |
| `auth` | `src/auth/*`, 인증/인가 |
| `ui` | `src/components/*`, UI 컴포넌트 |
| `docs` | 문서 파일들 |
| `test` | `tests/*` |
| `deps` | `package.json`, `requirements.txt` |
```

### 3. CI/CD 설정 (Optional)

```bash
# GitHub Actions 활성화
# .github/workflows/commitlint.yml 이미 제공됨
# .github/workflows/semantic-release.yml 이미 제공됨

# Repository Settings:
# 1. GitHub → Settings → Secrets
# 2. Add: GH_TOKEN (GitHub Personal Access Token)
# 3. Enable: GitHub Actions in Settings → Actions
```

### 4. Obsidian 통합 (Optional)

```bash
# 1. Obsidian Vault 생성
# 2. .env에서 경로 설정
OBSIDIAN_VAULT_PATH=~/Documents/ObsidianVault
OBSIDIAN_ENABLED=true

# 3. 필수 폴더 생성
mkdir -p ~/Documents/ObsidianVault/{개발일지,TASKS,MOCs}

# 4. MOC 파일 생성
cat > ~/Documents/ObsidianVault/MOCs/MyNewProject_개발_지식맵.md << 'EOF'
---
project: MyNewProject
type: MOC
updated: 2025-10-18
---

# MyNewProject 개발 지식맵

## 프로젝트 개요
[설명 추가]

## 주요 작업
- [[FEAT-2025-10-18-01]]

## 개발일지
- [[2025-10-18_TaskExecutor_테스트]]
EOF
```

---

## 🆘 문제 해결

### "Commitlint가 작동하지 않아요"

```bash
# Husky 재설치
rm -rf .husky
npx husky install
npx husky set .husky/commit-msg 'npx --no -- commitlint --edit "$1"'

# 권한 확인
chmod +x .husky/commit-msg
```

### "TaskExecutor가 실행되지 않아요"

```bash
# Python 경로 확인
which python
python --version  # 3.8+ 필요

# 의존성 재설치
pip install -r requirements.txt

# 스크립트 권한 확인
chmod +x scripts/task_executor.py
```

### "setup.sh가 실행되지 않아요"

```bash
# Windows: Git Bash 사용
# 또는 수동 설정 (Step 2 - Option B 참조)

# 권한 확인
chmod +x setup.sh
```

---

## 📊 성공 지표

설정 완료 후 다음을 확인하세요:

- [ ] Commitlint가 잘못된 커밋 메시지를 거부함
- [ ] `python scripts/task_executor.py --help` 실행됨
- [ ] Git 커밋 시 자동 검증됨
- [ ] RUNS/ 폴더에 provenance 파일 생성됨
- [ ] (Optional) Obsidian에 개발일지 자동 생성됨

---

## 🔗 관련 문서

- [MULTI_CLI_STRATEGY.md](MULTI_CLI_STRATEGY.md) - Claude + Gemini + Codex 전략
- [REAL_WORLD_CASES.md](REAL_WORLD_CASES.md) - 실제 사용 사례
- [DEVELOPMENT_RULES.md](../DEVELOPMENT_RULES.md) - 전체 개발 규칙

---

**소요 시간**: 15분
**난이도**: ★☆☆☆☆ (초보자 가능)
**유지보수**: 분기별 업데이트 (3개월)
