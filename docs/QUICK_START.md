---
title: "Quick Start - 5분 시작 가이드"
description: "5분 안에 Constitution의 핵심 3가지 체험: Git 표준화, 코드 품질, YAML 계약서"
audience:
  - "처음 시작하는 개발자"
  - "Constitution 초보자"
  - "평가 단계 사용자"
estimated_time: "5분 (1분+2분+2분)"
difficulty: "Beginner"
prerequisites:
  - "Git 기본 이해"
  - "Python 환경 (Level 1+용)"
related_docs:
  - "ADOPTION_GUIDE.md"
  - "NORTH_STAR.md"
  - "TRADEOFF_ANALYSIS.md"
  - "CLAUDE.md"
  - "MIGRATION_GUIDE.md"
tags:
  - "quickstart"
  - "beginner"
  - "onboarding"
  - "5-minutes"
  - "first-time"
last_updated: "2025-11-04"
version: "1.0.0"
steps:
  - "1분: Git Commit 표준화"
  - "2분: 코드 품질 체크"
  - "2분: 첫 YAML 계약서"
next_step: "ADOPTION_GUIDE.md (Level 1 Light Setup)"
---

# Quick Start - 5분 시작 가이드

**목표**: 5분 안에 Constitution 시스템 체험하기
**대상**: 처음 시작하는 개발자
**소요 시간**: 5분 (1분+2분+2분)

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

EOF

# 2. 실행
python scripts/task_executor.py TASKS/MY-FIRST-TASK.yaml

# ✅ 완료! 자동 증거 수집됨
```

**효과**:
- 작업 자동 문서화
- 재현 가능한 프로세스
- Knowledge Asset 시작

---

## 🎉 5분 완료! 다음 단계는?

### 📚 See Also

**5분 체험 후 다음**:
- **[ADOPTION_GUIDE.md](ADOPTION_GUIDE.md)** - Level 0-3 단계별 채택 (5분 → 1주 → 1개월)

**더 깊이 이해하기**:
- **[NORTH_STAR.md](../NORTH_STAR.md)** - 왜 Constitution인가? (철학 이해)
- **[TRADEOFF_ANALYSIS.md](TRADEOFF_ANALYSIS.md)** - 부작용은 없나? (현실적 기대치)

**실전 적용**:
- **[CLAUDE.md](../CLAUDE.md)** - 일상 개발 명령어 (매일 참조)
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - 기존 프로젝트 적용 (팀 도입)

**고급 활용** (나중에):
- **[MULTI_SESSION_GUIDE.md](MULTI_SESSION_GUIDE.md)** - 멀티 AI 세션 협업

---

**마지막 업데이트**: 2025-11-04
**다음 단계**: Level 1 Light Setup (1주)
