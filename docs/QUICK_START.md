# Quick Start - 5분 시작 가이드

**목표**: 5분 안에 Constitution 시스템 체험하기
**대상**: 처음 시작하는 개발자

## ⚡ 1분: Git Commit 표준화

```bash
# 1. 현재 브랜치 확인
git status && git branch

# 2. Conventional Commits 형식으로 커밋
git commit -m "feat: add login feature"
git commit -m "fix: resolve null pointer"
git commit -m "docs: update README"

# ✅ 완료! 이것만으로도 즉시 효과
```

**효과**:
- Git log가 읽기 쉬워짐
- Semantic Release 자동화 준비
- 팀 커뮤니케이션 개선

## ⚡ 2분: 코드 품질 체크

```bash
# 1. Virtual environment 활성화
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Ruff 설치 (아직 안 했다면)
pip install ruff

# 3. 코드 체크
ruff check scripts/

# 4. 자동 수정
ruff check --fix scripts/

# ✅ 완료! 코드 품질 즉시 향상
```

**효과**:
- 버그 조기 발견
- 코드 스타일 일관성
- 자동 수정으로 시간 절감

## ⚡ 2분: 첫 YAML 계약서

```bash
# 1. 간단한 YAML 작성
cat > TASKS/MY-FIRST-TASK.yaml << EOF
task_id: "MY-FIRST-TASK"
title: "첫 번째 작업"
commands:
  - exec: ["echo", "Hello Constitution!"]
