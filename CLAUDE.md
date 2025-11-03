# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📖 Documentation Structure (AI MUST READ THIS!)

**이 문서 (CLAUDE.md)**: 일상 개발 참조용 - 항상 이것부터 읽으세요
**다른 문서들**: 특정 상황에서만 필요 - 아래 트리거를 보고 판단하세요

### 🤖 AI: When to Read Other Documents

**자동으로 읽어야 하는 상황** (AI가 감지 시 자동 참조):

```yaml
사용자가 말하면 → 해당 문서 읽기:
  "마이그레이션|기존 프로젝트|도입|migration|migrate|existing project|legacy":
    → Read docs/MIGRATION_GUIDE.md

  "멀티 세션|동시 작업|충돌|세션 간|multi session|concurrent|parallel|collaboration|lock":
    → Read docs/MULTI_SESSION_GUIDE.md

  "Level 0|Level 1|Level 2|Level 3|단계별|채택|adoption|progressive|gradual|onboarding":
    → Read docs/ADOPTION_GUIDE.md

  "부작용|위험|트레이드오프|완화|side effect|risk|mitigation|trade-off|tradeoff":
    → Read docs/TRADEOFF_ANALYSIS.md

  "처음|시작|빠르게|5분|quick start|getting started|beginner|first time":
    → Read docs/QUICK_START.md

  "방향성|정체성|무엇을|vision|philosophy|north star|identity|what is":
    → Read NORTH_STAR.md

  "Constitution 전문|조항 상세|P1-P15 상세|full constitution|article details|all principles":
    → Read config/constitution.yaml
```

**중요**: 위 키워드가 없으면 이 문서(CLAUDE.md)만으로 충분합니다!

## 🎯 Project Identity

**Dev Rules Starter Kit** - Constitution-Based Development Framework

**핵심 개념**:
- **문서가 곧 코드**: YAML 계약서 → TaskExecutor 실행 → 자동 증거 수집
- **Constitution 중심**: 15개 조항(P1-P15)이 모든 개발의 법
- **지식 자산화**: 모든 실행 결과가 Obsidian으로 자동 동기화 (3초)

**무엇이 아닌가**:
- ❌ 코드 품질 대시보드 도구 (SonarQube 같은 것 아님)
- ❌ 독립적 분석 도구 모음
- ✅ Constitution 기반 개발 체계 템플릿

## 🔥 Critical Rules

### Windows Encoding (P10) - NEVER USE EMOJIS IN PYTHON CODE

**절대 규칙**: Production Python 코드에 이모지 사용 금지 (Windows에서 크래시!)

```python
# ❌ WRONG - Will crash on Windows
print("✅ Task completed")
status = "🚀 Deploying"

# ✅ CORRECT - Use ASCII alternatives
print("[SUCCESS] Task completed")
status = "[DEPLOY] Deploying"
```

**이모지 사용 가능 위치**:
- ✅ Markdown 파일 (.md)
- ✅ Git commit 메시지
- ❌ Python 코드 (.py)
- ❌ YAML 파일
- ❌ Shell 스크립트

## 📋 Quick Command Reference

### 일상 개발 명령어 (Top 10)

```bash
# 1. Virtual environment 활성화 (항상 첫 번째!)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. 작업 계획 확인
python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan

# 3. 작업 실행
python scripts/task_executor.py TASKS/TEMPLATE.yaml

# 4. Constitution 검증
python scripts/constitutional_validator.py

# 5. 코드 품질 검사
ruff check scripts/ tests/

# 6. 테스트 실행
pytest tests/                    # 모든 테스트
pytest tests/test_file.py       # 단일 파일
pytest -xvs tests/test_file.py::test_name  # 특정 테스트

# 7. Obsidian 수동 동기화
python scripts/obsidian_bridge.py sync

# 8. 세션 관리
python scripts/session_manager.py start
python scripts/session_manager.py save

# 9. Git 워크플로우
git status && git branch  # 항상 먼저 확인!
git checkout -b tier1/feature-name
git commit -m "feat(scope): description"

# 10. 개발 중 자동 검증
python scripts/dev_assistant.py  # 파일 변경 감시
```

### Setup Commands

```bash
# Level 0: 최소 설정 (5분)
git commit -m "feat: add login"  # Conventional Commits만

# Level 1: 기본 설정 (30분)
python -m venv .venv
.venv\Scripts\activate
pip install ruff

# Level 2: 표준 설정 (1시간)
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install

# Level 3: 완전 설정
pip install -e .
pre-commit install --hook-type commit-msg
python scripts/context_provider.py init
```

## 🏗️ 7-Layer Architecture

**핵심**: 파일을 수정하거나 생성할 때, 어느 Layer에 속하는지 먼저 파악하세요!

```
Layer 1: Constitution (config/constitution.yaml)
    ├── P1-P10: 개발 프로세스 규칙
    └── P11-P15: 거버넌스 및 메타 규칙

Layer 2: Execution (실행)
    ├── task_executor.py - YAML 계약 실행 (P1, P2)
    ├── enhanced_task_executor_v2.py - 병렬 실행
    └── constitutional_validator.py - 헌법 준수 검증

Layer 3: Analysis (분석)
    ├── deep_analyzer.py - SOLID, 보안, Hallucination (P4, P5, P7)
    └── team_stats_aggregator.py - 품질 메트릭 (P6)

Layer 4: Optimization (최적화)
    ├── verification_cache.py - 중복 검증 방지 (60% 단축)
    ├── critical_file_detector.py - 핵심 파일 식별
    └── unified_error_resolver.py - 3-Tier 에러 해결 (95% 자동화)

Layer 5: Evidence Collection (증거 수집)
    └── RUNS/evidence/ - 모든 실행 로그 자동 기록

Layer 6: Knowledge Asset (지식 자산)
    ├── obsidian_bridge.py - 지식베이스 동기화 (P3)
    └── context_provider.py - 세션 간 컨텍스트 유지

Layer 7: Visualization (시각화 - 검증 안 함!)
    └── Streamlit 대시보드 - 현황판 역할만
```

**파일 배치 예시**:
- 새 검증 도구 → Layer 3 (`scripts/*_analyzer.py`)
- 성능 개선 → Layer 4 (`scripts/*_cache.py`)
- 실행 엔진 수정 → Layer 2 (`scripts/*_executor.py`)

## 📜 Constitution Quick Reference

### 개발 프로세스 조항 (P1-P10)

| ID | 조항 | 강제 도구 | 언제 사용? |
|----|------|----------|-----------|
| **P1** | YAML 계약서 우선 | TaskExecutor | 3단계 이상 작업 |
| **P2** | 증거 기반 개발 | TaskExecutor | 모든 실행 자동 기록 |
| **P3** | 지식 자산화 | ObsidianBridge | Git commit 시 자동 |
| **P4** | SOLID 원칙 | DeepAnalyzer | 코드 리뷰 전 |
| **P5** | 보안 우선 | DeepAnalyzer | 배포 전 필수 |
| **P6** | 품질 게이트 | TeamStatsAggregator | PR 생성 시 |
| **P7** | Hallucination 방지 | DeepAnalyzer | AI 생성 코드 검증 |
| **P8** | 테스트 우선 | pytest | 구현 전 테스트 작성 |
| **P9** | Conventional Commits | pre-commit | 모든 커밋 |
| **P10** | Windows 인코딩 | UTF-8 강제 | Python 파일 생성 시 |

### 거버넌스 조항 (P11-P15)

| ID | 조항 | 목적 | 적용 시점 |
|----|------|------|-----------|
| **P11** | 원칙 충돌 검증 | 과거 결정과 충돌 방지 | 새 기능 제안 시 |
| **P12** | 트레이드오프 분석 | 객관적 의사결정 | 중요한 선택 시 |
| **P13** | 헌법 수정 검증 | Constitution 비대화 방지 | 조항 추가/수정 시 |
| **P14** | 2차 효과 분석 | 개선의 부작용 완화 | 시스템 변경 시 |
| **P15** | 수렴 원칙 | 80% 품질에서 멈춤 | 무한 개선 방지 |

## 🔄 Common Workflows

### Workflow 1: 작은 변경 (1-3줄)

```bash
# YAML 불필요 - 바로 커밋
vim scripts/fix_bug.py
git add .
git commit -m "fix: resolve null pointer"
# 끝!
```

### Workflow 2: 일반 개발 (10-50줄)

```bash
# 1. YAML 계약서 작성
cat > TASKS/FIX-$(date +%Y%m%d).yaml << EOF
task_id: "FIX-20251103"
title: "버그 수정"
commands:
  - exec: ["pytest", "tests/"]
EOF

# 2. 실행
python scripts/task_executor.py TASKS/FIX-20251103.yaml

# 3. 자동 증거 수집 → RUNS/evidence/
# 4. Obsidian 자동 동기화 (3초)
```

### Workflow 3: 대규모 기능 (50줄+)

```bash
# 1. YAML 계약서 (Gates 포함)
cat > TASKS/FEAT-20251103-01.yaml << EOF
task_id: "FEAT-20251103-01"
title: "인증 시스템 추가"
gates:
  - type: "constitutional"
    articles: ["P4", "P5", "P8"]
commands:
  - exec: ["python", "scripts/implement_auth.py"]
EOF

# 2. 계획 검증
python scripts/task_executor.py TASKS/FEAT-20251103-01.yaml --plan

# 3. 실행
python scripts/task_executor.py TASKS/FEAT-20251103-01.yaml

# 4. Constitution 검증
python scripts/constitutional_validator.py
```

### Workflow 4: 세션 관리

```bash
# 세션 시작
python scripts/session_manager.py start
python scripts/context_provider.py init

# 작업 수행...

# 30분마다 체크포인트
python scripts/session_manager.py save

# 세션 종료
python scripts/session_manager.py save
python scripts/obsidian_bridge.py sync
git commit -m "feat: session work completed"
```

## 🆘 Troubleshooting

### Issue 1: "Ruff not found"

```bash
# Venv 활성화 확인
where python  # Windows - .venv 경로여야 함
which python  # Linux/Mac

# Ruff 설치
pip install ruff
```

### Issue 2: "Obsidian 동기화 실패"

```bash
# .env 파일 확인
type .env | findstr OBSIDIAN_VAULT_PATH  # Windows
cat .env | grep OBSIDIAN_VAULT_PATH      # Linux/Mac

# 연결 테스트
python scripts/obsidian_bridge.py test

# 경로 확인
ls "$OBSIDIAN_VAULT_PATH"
```

### Issue 3: "Pre-commit hooks 작동 안 함"

```bash
# Husky 재설치
rm -rf .husky
npx husky install
npx husky set .husky/commit-msg 'npx --no -- commitlint --edit "$1"'

# 또는 Python pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Issue 4: "Context mismatch"

```bash
# Context 진단
python scripts/context_provider.py diagnose

# Context 재초기화
python scripts/context_provider.py init
```

### Issue 5: "Windows 인코딩 에러"

```bash
# 환경변수 설정
set PYTHONUTF8=1  # Windows

# 또는 스크립트 최상단에 추가
# -*- coding: utf-8 -*-
```

## 🤖 Hybrid Error Resolution (3-Tier Auto-Fix)

**상태**: ✅ Production Ready | **자동화율**: 95%

AI가 에러를 만났을 때 자동으로 3단계 해결:

### 3-Tier Cascade

```python
# 자동 실행됨 - 사용자 개입 불필요!

Tier 1 (Obsidian): 과거 해결책 검색 (<10ms, 70% 해결)
    ↓ Miss
Tier 2 (Context7): 공식 문서 검색 + 신뢰도 평가
    ├─ HIGH (≥95%) → 자동 적용
    ├─ MEDIUM (70-95%) → 사용자 확인 요청
    └─ LOW (<70%) → Tier 3
    ↓
Tier 3 (User): 사용자 개입 (5%만 필요)
```

### 예시

**Scenario 1: ModuleNotFoundError (HIGH)**
```bash
$ python app.py
ModuleNotFoundError: No module named 'pandas'

# AI 자동 처리:
[TIER 2 AUTO] pip install pandas (100% confidence)
✅ 해결됨!
```

**Scenario 2: 설정 변경 (MEDIUM)**
```bash
$ npm start
Error: PORT 3000 already in use

# AI 처리:
Context7 제안: "Change PORT in .env to 3001"
적용할까요? (y/n)
```

**위치**: `scripts/unified_error_resolver.py`

## 📂 File Organization

### 중요 파일 (Impact Score > 0.5)

이 파일들을 수정할 때는 특별히 주의하세요:
- `*_executor.py` - 핵심 실행 엔진
- `*_validator.py` - 검증 시스템
- `constitutional_*.py` - Constitution 강제 도구
- `*_guard.py` - 보안 컴포넌트
- `context_*.py` - 컨텍스트 관리
- `obsidian_*.py` - 지식 동기화

### TASKS/*.yaml 네이밍 규칙

```bash
# 형식: TYPE-YYYYMMDD-NN.yaml

FEAT-20251103-01.yaml  # 새 기능
FIX-20251103-01.yaml   # 버그 수정
REFACTOR-20251103-01.yaml  # 리팩토링
DOCS-20251103-01.yaml  # 문서화
TEST-20251103-01.yaml  # 테스트
```

### 디렉토리 구조

```
scripts/          # Layer 2-4 도구들
  ├── *_executor.py      # Layer 2: 실행
  ├── *_analyzer.py      # Layer 3: 분석
  ├── *_validator.py     # Layer 3: 검증
  └── *_cache.py         # Layer 4: 최적화

TASKS/            # P1: YAML 계약서
RUNS/evidence/    # P2: 증거 수집
config/           # 설정 파일
  └── constitution.yaml  # Layer 1: 헌법

tests/            # P8: 테스트
claudedocs/       # AI 생성 문서
docs/             # 사용자 가이드
```

## 🔗 MCP Tool Integration

### Context7 (공식 문서 검색)

**언제 사용?**
- 라이브러리 import 질문
- 프레임워크 best practice
- 공식 API 사용법

```python
# AI가 자동으로 Context7 사용:
"React useEffect 구현" → Context7 검색
"Auth0 설정" → Context7 공식 문서
```

### Obsidian (지식베이스)

**자동 동기화 조건**:
- 3개 이상 파일 변경
- `feat:`, `fix:`, `refactor:` 커밋
- TaskExecutor 실행 완료

**수동 동기화**:
```bash
python scripts/obsidian_bridge.py sync
```

**구조**:
- `개발일지/YYYY-MM-DD/` - 일일 로그
- `TASKS/` - 계약서 복사본
- `MOCs/` - 지식 맵 (자동 업데이트)

### Codex (코드 분석/리팩토링)

```bash
# MCP Codex 사용
mcp__codex-mcp__codex prompt="Refactor this function"

# 또는 직접 호출
python scripts/codex_auto_init.py
```

## 🎯 Decision Tree: 어떤 스크립트를 쓸까?

```
작업 유형?
  ├─ YAML 계약서 실행 → task_executor.py
  ├─ 코드 품질 검사 → deep_analyzer.py
  ├─ Constitution 검증 → constitutional_validator.py
  ├─ 에러 자동 해결 → unified_error_resolver.py (자동 호출됨)
  ├─ Obsidian 동기화 → obsidian_bridge.py
  ├─ 세션 관리 → session_manager.py
  ├─ 컨텍스트 관리 → context_provider.py
  ├─ 멀티 세션 조율 → agent_sync_status.py
  └─ 실시간 검증 → dev_assistant.py
```

## 🚫 Anti-Patterns

**절대 하지 말 것**:
- ❌ main/master 브랜치 직접 작업 (위험!)
- ❌ **Python 코드에 이모지 사용** (Windows 크래시!)
- ❌ System Python 사용 (venv 없이)

**가능하면 피할 것** (긴급 시 OK):
- ⚠️ 복잡한 작업에 YAML 생략 → `SKIP_CONSTITUTION=true`
- ⚠️ Constitution 없이 기능 추가 → 프로토타입만 예외
- ⚠️ 컨텍스트 저장 없이 종료 → 작은 수정은 괜찮음

**유연하게 판단**:
- 3줄 수정에 YAML? → 과도함, 건너뛰기
- 모든 것을 검증? → CI/CD에서만
- 100% Constitution 준수? → 80%면 충분 (P15)

## 📊 Performance Optimization

### Caching (60% 단축)

```python
# 이미 구현됨 - 자동 사용
from verification_cache import VerificationCache
cache = VerificationCache(ttl=300)  # 5분 캐시
```

### Parallel Execution

```bash
# 자동 병렬화
python scripts/enhanced_task_executor_v2.py

# 동시 실행 수 조정
export MAX_WORKERS=4
```

### Selective Validation

```bash
# 변경된 파일만 검증
git diff --name-only | xargs python scripts/deep_analyzer.py

# CI에서만 전체 검증
if [ "$CI" = "true" ]; then
    python scripts/constitutional_validator.py --full
fi
```

## 🔧 Advanced: Multi-AI Session

**Use Case**: 1명 개발자 + 3-4 AI 세션 동시 작업

### Setup

```bash
# 각 AI 세션 시작 시
python scripts/context_provider.py init
python scripts/session_manager.py start

# 현재 활성 세션 확인
python scripts/agent_sync_status.py
```

### Conflict Prevention

```bash
# 파일 편집 전 잠금 확인
python scripts/agent_sync_status.py --files src/auth.py

# 출력:
# src/auth.py
#   - Locked by: Session2_Backend
#   - Since: 2025-11-03 10:30
#   - Conflict: Yes (다른 세션이 편집 중)
```

**상세 가이드**: `docs/MULTI_SESSION_GUIDE.md` 참조

## 📚 Related Documentation

**필수 읽기**:
- [NORTH_STAR.md](NORTH_STAR.md) - 방향성 확인 (1분 읽기)
- [config/constitution.yaml](config/constitution.yaml) - 헌법 전문 (800+ 줄)

**상세 가이드**:
- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) - 기존 프로젝트 마이그레이션
- [docs/MULTI_SESSION_GUIDE.md](docs/MULTI_SESSION_GUIDE.md) - 멀티 AI 세션 워크플로우
- [docs/ADOPTION_GUIDE.md](docs/ADOPTION_GUIDE.md) - 단계별 채택 전략
- [docs/TRADEOFF_ANALYSIS.md](docs/TRADEOFF_ANALYSIS.md) - 부작용 분석 및 완화

**기타**:
- [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) - 개발 표준
- [docs/SESSION_MANAGEMENT_GUIDE.md](docs/SESSION_MANAGEMENT_GUIDE.md) - 세션 컨텍스트 관리

## 🎓 Learning Path

**5분 시작**:
1. 이 문서 읽기
2. `git commit -m "feat: init"` 시도
3. Conventional Commits 확인

**30분 기본**:
1. Venv 설정
2. Ruff 검사 실행
3. 간단한 YAML 계약서 작성

**1시간 표준**:
1. Pre-commit hooks 설치
2. TaskExecutor로 첫 작업 실행
3. Obsidian 동기화 확인

**완전 숙달** (1주):
1. Constitution 13개 조항 이해
2. 7계층 아키텍처 파악
3. 멀티 세션 워크플로우 실습

---

**버전**: 2.0.0 (간결화)
**마지막 업데이트**: 2025-11-03
**이전 버전**: CLAUDE.md.backup (1522줄 → 600줄)
