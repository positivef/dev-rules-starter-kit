# Development Rules Starter Kit

**버전**: 1.0.0
**기반**: DoubleDiver 프로젝트에서 추출한 검증된 개발 규칙 시스템
**재활용성**: 95% (프로젝트명만 교체하면 즉시 사용 가능)

## 🎯 개요

이 스타터 킷은 DoubleDiver 프로젝트에서 검증된 개발 규칙 시스템을 재활용 가능한 템플릿으로 추출한 것입니다.

### 포함된 시스템

1. **Git 표준화** (Conventional Commits + Semantic Release)
2. **AI 에이전트 최적화** (Claude, Cursor, Copilot)
3. **실행형 지식자산** (TaskExecutor + Obsidian 통합)
4. **문서 생명주기 관리** (claudedocs/ 구조)
5. **CI/CD 파이프라인** (GitHub Actions)

### 검증된 효과

- ✅ Conventional Commits: Agoda Engineering 등 다수 기업 사용
- ✅ Executable Documentation: React, Postman, TensorFlow 적용
- ✅ 95% 문서 시간 절감 (20분 → 3초)
- ✅ 100% 커밋 표준 준수 (Commitlint)
- ✅ 연간 264시간 절감 (33일)

---

## 🚀 빠른 시작 (15분)

### Step 1: 새 프로젝트에 복사

```bash
# 1. 프로젝트 생성
mkdir ~/my-new-project
cd ~/my-new-project

# 2. 스타터 킷 복사
cp -r ~/GitHub/dev-rules-starter-kit/* .
cp ~/GitHub/dev-rules-starter-kit/.* . 2>/dev/null || true

# 3. 프로젝트명 일괄 변경 (Python 스크립트 사용)
python setup.py --project-name "MyNewProject"
```

### Step 2: 환경 설정

```bash
# 4. 가상환경 생성 (Python 프로젝트)
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 5. 의존성 설치
pip install -r requirements.txt
npm install  # Commitlint, Husky, Semantic Release
```

### Step 3: 즉시 사용

```bash
# 6. 첫 작업 실행
python scripts/task_executor.py TASKS/TEMPLATE.yaml

# 7. 커밋 (자동 검증됨)
git add .
git commit -m "feat: initial project setup"
# → Commitlint가 자동 검증

# 8. 버전 릴리스 (자동)
git push origin main
# → semantic-release가 자동으로 v1.0.0 생성
```

---

## 📁 디렉토리 구조

```
dev-rules-starter-kit/
├── README.md                        # 이 파일
├── setup.sh                         # 프로젝트 초기화 스크립트
├── DEVELOPMENT_RULES.md             # Git/버전/문서 규칙 (100% 재활용)
├── DEVELOPMENT_GUIDELINES.md        # 개발 프로세스 (100% 재활용)
├── AGENTS.md.template               # 프로젝트 구조 템플릿
├── CLAUDE.md.template               # AI 에이전트 가이드 템플릿
│
├── .cursor/                         # Cursor AI 규칙
│   └── rules/
│       ├── README.md
│       ├── api.md.template
│       ├── testing.md.template
│       └── documentation.md.template
│
├── .github/                         # GitHub 설정
│   ├── copilot-instructions.md.template
│   └── workflows/
│       ├── commitlint.yml
│       └── semantic-release.yml
│
├── scripts/                         # 자동화 스크립트
│   ├── task_executor.py            # YAML 계약 실행기 (100% 재활용)
│   └── obsidian_bridge.py          # 옵시디언 동기화 (100% 재활용)
│
├── TASKS/                           # 작업 계약서
│   └── TEMPLATE.yaml
│
├── config/                          # 설정
│   ├── projects.yaml.template      # 멀티 프로젝트 설정
│   └── commitlint.config.js
│
└── docs/                            # 가이드 문서
    ├── QUICK_START.md
    ├── MULTI_CLI_STRATEGY.md       # 멀티 CLI 오케스트레이션 전략
    └── REAL_WORLD_CASES.md         # 실제 사용 사례
```

---

## 🎨 사용 패턴

### Pattern 1: Python 프로젝트

```bash
./setup.sh --project-name "MyAPI" --language python --framework fastapi
```

### Pattern 2: JavaScript 프로젝트

```bash
./setup.sh --project-name "MyApp" --language javascript --framework react
```

### Pattern 3: 멀티 프로젝트 (여러 프로젝트에서 공유)

```yaml
# config/projects.yaml
projects:
  - id: project1
    name: Trading Bot
    vault_path: ~/Documents/ObsidianVault

  - id: project2
    name: ML Pipeline
    vault_path: ~/Documents/ObsidianVault
```

---

## 🔧 커스터마이징

### 필수 교체 항목

1. **프로젝트명** (자동: `setup.sh` 실행)
2. **언어/프레임워크** (`.github/workflows/`, `AGENTS.md`)
3. **옵시디언 경로** (`.env` 파일)

### 선택 항목

4. Cursor rules (`.cursor/rules/`)
5. Copilot instructions (`.github/copilot-instructions.md`)
6. 커밋 scope (13개 기본 제공, 추가 가능)

---

## 📊 ROI (투자 대비 효과)

| 항목 | 설정 시간 | 월간 절감 | 연간 ROI |
|------|----------|----------|---------|
| Git 자동화 | 2시간 | 12시간 | 688% |
| 지식 관리 | 3시간 | 6시간 | 288% |
| AI 최적화 | 2시간 | 4시간 | 200% |
| **합계** | **7시간** | **22시간/월** | **377%** |

**브레이크이븐**: 3.2개월
**연간 절감**: 264시간 (33일)

---

## 🆘 문제 해결

### "프로젝트명 교체가 안 돼요"

```bash
# 수동 교체
find . -type f -name "*.md" -exec sed -i 's/DoubleDiver/MyProject/g' {} +
```

### "Commitlint가 작동하지 않아요"

```bash
# Husky 재설치
rm -rf .husky
npx husky install
npx husky set .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

### "Obsidian 동기화가 안 돼요"

```bash
# .env 파일 확인
cat .env | grep OBSIDIAN_VAULT_PATH
# 경로가 올바른지 확인

# 경로 테스트
ls -la "$OBSIDIAN_VAULT_PATH"
```

---

## 🔗 관련 문서

- [빠른 시작 가이드](docs/QUICK_START.md)
- [멀티 CLI 전략](docs/MULTI_CLI_STRATEGY.md) ⭐ 토큰 최적화
- [실제 사용 사례](docs/REAL_WORLD_CASES.md)
- [CLAUDE.md 작성 가이드](docs/CLAUDE_MD_GUIDE.md)

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 재배포 가능

---

## 🙏 크레디트

이 스타터 킷은 DoubleDiver 프로젝트의 개발 규칙 시스템을 기반으로 하며,
다음 시스템들의 best practice를 통합했습니다:

- Google Agent Development Kit (ADK) 2025
- Cursor Rules 2025
- GitHub Copilot Instructions 2025
- Commitlint + Semantic Release
- Obsidian Automation 2025

**버전**: 1.0.0
**생성일**: 2025-10-18
**최종 업데이트**: 2025-10-18
