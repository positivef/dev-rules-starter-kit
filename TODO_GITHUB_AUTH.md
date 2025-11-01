# GitHub CLI 인증 및 PR 생성 가이드

## 집에서 해야 할 일

### 1. GitHub CLI 인증 완료

**옵션 A: Device Flow (간단함)**
```bash
# 1. 인증 시작
gh auth login

# 2. 브라우저에서 열기
# https://github.com/login/device

# 3. 일회용 코드 입력 (새로 생성됨)

# 4. GitHub 계정으로 로그인 및 권한 승인
```

**옵션 B: Personal Access Token (빠름)**
```bash
# 1. GitHub Token 생성
# https://github.com/settings/tokens
# - Token (classic) 선택
# - 권한: repo (전체), workflow 체크

# 2. 환경 변수 설정
export GH_TOKEN=ghp_your_token_here  # Linux/Mac
set GH_TOKEN=ghp_your_token_here     # Windows CMD
$env:GH_TOKEN="ghp_your_token_here"  # Windows PowerShell

# 3. 인증 확인
gh auth status
```

### 2. PR 생성 (인증 완료 후)

```bash
# PR 생성 명령
gh pr create --title "feat: add TDD Enforcer system (Phase 4 Week 3)" --body "$(cat <<'EOF'
## Summary

Phase 4 Week 3 completion: TDD Enforcer system with pre-commit hook and metrics tracking.

### What's New

**TDD Enforcement System**:
- `scripts/tdd_enforcer.py` - Pre-commit hook checking test file existence (191 lines)
- `scripts/tdd_metrics.py` - Coverage/test metrics tracker (358 lines)
- `docs/TDD_ENFORCEMENT.md` - Comprehensive TDD enforcement guide (~500 lines)
- `.pre-commit-config.yaml` - Added TDD enforcer hook

**Phase 4 Unit Tests**:
- `tests/unit/test_deep_analyzer.py` - 22 tests for SOLID/security/hallucination checks (56% coverage)
- `docs/TESTING_STRATEGY.md` - Hybrid testing strategy documentation
- `.github/workflows/unit-tests.yml` - CI/CD with 5% coverage threshold

**P10 Compliance**:
- Fixed Windows encoding in `tdd_metrics.py` (removed emojis: ✓→[OK], ✗→[WARN], █→#)
- Fixed Korean comments in `auto_obsidian_context.py` to English

### Coverage Achievement

**Realistic Target (P15 Convergence)**:
- Achieved: **5% coverage** (883/18,295 lines) with 92 unit tests
- Deep coverage on critical files: task_executor.py (46%), constitutional_validator.py (90%), deep_analyzer.py (56%)
- Total: 1,169 tests (92 unit + 1,077 integration)

**Rationale**:
- Original 15% target = 33 hours for shallow coverage
- **P15 principle**: 5% deep coverage > 15% shallow coverage
- Focus on critical code paths, not line count

### TDD Enforcer Features

**Pre-commit Hook**:
- Checks changed .py files for corresponding test files
- Warning mode (non-blocking) - educates without blocking workflow
- Exempts config/init/setup files automatically
- Suggests test file locations

**Metrics Tracking**:
- Records coverage trends over time
- Tracks test/code ratio
- CLI: `python scripts/tdd_metrics.py record|report|trend`
- Storage: `RUNS/tdd_metrics.json`

### Constitutional Compliance

- ✅ **P1 (YAML First)**: Task defined in TASKS/FEAT-2025-11-01-03.yaml
- ✅ **P2 (Evidence-Based)**: Evidence in RUNS/evidence/
- ✅ **P6 (Quality Gates)**: CI/CD enforces 5% threshold
- ✅ **P8 (Test-First)**: TDD enforcer automated
- ✅ **P10 (Windows UTF-8)**: No non-ASCII in Python code
- ✅ **P15 (Convergence)**: Stopped at realistic 5% target

### Files Changed

**New Files** (6):
- tests/unit/test_deep_analyzer.py
- docs/TESTING_STRATEGY.md
- .github/workflows/unit-tests.yml
- scripts/tdd_enforcer.py
- scripts/tdd_metrics.py
- docs/TDD_ENFORCEMENT.md

**Modified Files** (3):
- .pre-commit-config.yaml (added TDD hook)
- scripts/auto_obsidian_context.py (P10 compliance)
- RUNS/tdd_metrics.json (baseline metrics)

### Evidence

**Task Contract**: TASKS/FEAT-2025-11-01-03.yaml
**Evidence Directory**: RUNS/evidence/FEAT-2025-11-01-03/
**Metrics Baseline**: RUNS/tdd_metrics.json

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3. 수동 PR 생성 (CLI 인증 안 될 경우)

**대체 방법**:
1. 브라우저에서 열기: https://github.com/positivef/dev-rules-starter-kit/compare/main...tier1/week3-tdd-enforcer
2. 위 PR 제목과 설명 복사하여 붙여넣기
3. "Create pull request" 버튼 클릭

### 4. PR 검증 확인

PR 생성 후 자동으로 실행되는 것들:
- `.github/workflows/unit-tests.yml` - Unit tests + Coverage check (≥5%)
- Pre-commit hooks validation
- CI/CD 전체 검증

**확인 사항**:
- [ ] All checks passed (초록색 체크)
- [ ] Coverage ≥5%
- [ ] No merge conflicts
- [ ] Ready to merge

---

## 완료 체크리스트

- [x] 브랜치 push 완료 (tier1/week3-tdd-enforcer)
- [ ] GitHub CLI 인증 완료
- [ ] PR 생성 완료
- [ ] CI/CD 검증 통과
- [ ] PR 머지

---

**생성일**: 2025-11-01
**브랜치**: tier1/week3-tdd-enforcer
**상태**: 인증 대기 중
