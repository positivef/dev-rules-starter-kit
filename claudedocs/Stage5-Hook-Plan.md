# Stage 5 (Hook) 계획서 - VibeCoding Enhanced

**생성 일시**: 2025-11-07
**프로젝트**: Dev Rules Starter Kit
**현재 Stage**: Stage 5 (Hook - 시작)
**이전 Stage**: Stage 4 (System - 완료)

---

## 🎯 STICC Context

### Situation (상황)

**Stage 4 완료 상태**:
- ✅ 4개 자동화 도구 구현 완료
  - Auto-Improver (Constitution 위반 검사)
  - Constitution Dashboard (시각화)
  - Auto Test Generator (테스트 자동 생성)
  - Auto Doc Updater (문서 자동 갱신)
- ✅ 90% 자동화 달성
- ✅ 실행 속도 5.1초 (충분히 빠름)

**현재 문제점**:
- 도구들이 독립 실행 → **수동 트리거 필요**
- 개발자가 기억해야 함 → **휴먼 에러 가능**
- Git 워크플로우와 분리 → **통합 안 됨**
- CI/CD 없음 → **자동 검증 누락 가능**

**VibeCoding 단계**:
- Stage 1-3 (Insight/MVP/Feedback): 완료
- Stage 4 (System): 완료
- **Stage 5 (Hook)**: ← 현재
- Stage 6 (Scale): 미래

### Task (작업)

**핵심 목표**: "개발자가 의식하지 않아도 Constitution이 강제되는 시스템"

**구체적 작업**:
1. **Git Hooks 구현**
   - Pre-commit: Ruff, P4/P5 검증
   - Commit-msg: Conventional Commits (P9)
   - Post-commit: Obsidian 동기화 (P3)

2. **CI/CD 통합**
   - GitHub Actions: 전체 Constitution 검증
   - PR 게이트: P6 Quality Gate 통과 필수
   - 자동 테스트: P8 커버리지 검증

3. **Workflow 자동화**
   - YAML 계약서 자동 생성 (P1)
   - 증거 자동 수집 (P2)
   - 일일 대시보드 업데이트

4. **통합 CLI**
   - `dev` 명령어 하나로 모든 도구 실행
   - 컨텍스트 인지 (어떤 검증 필요한지 자동 판단)

### Intent (의도)

**명시적 목표**:
- 100% Constitution 준수율 (현재 90%)
- Zero-touch 자동화 (수동 개입 제거)
- Stage 5 완료 → Stage 6 진입

**암묵적 목표**:
- 개발자 경험 개선 (마찰 최소화)
- 신뢰할 수 있는 시스템 (항상 작동)
- 다른 프로젝트에 적용 가능한 템플릿

**비목표** (하지 않을 것):
- 완벽한 에러 방지 (80% 면 충분, P15)
- 모든 엣지 케이스 처리 (점진적 개선)
- 복잡한 설정 요구 (간단해야 함)

### Concerns (우려사항)

**기술적 우려**:
1. **Git Hooks 성능**
   - Pre-commit이 너무 느리면: 개발자가 우회 시도
   - 목표: <3초 (체감 가능한 수준)
   - 완화: 증분 검증 (변경된 파일만)

2. **CI/CD 복잡도**
   - GitHub Actions 러닝 커브
   - 다른 CI 플랫폼 지원 (GitLab, Bitbucket)
   - 완화: 간단한 템플릿 제공, 점진적 채택

3. **Hook 무시 가능성**
   - `git commit --no-verify` 사용
   - 완화: CI에서 2차 검증, 강제는 안 함

4. **윈도우 호환성**
   - Bash 스크립트 vs Windows
   - 완화: Python 스크립트 우선 (크로스 플랫폼)

**조직적 우려**:
1. **채택 저항**
   - "또 규칙 추가?" 반발
   - 완화: 선택적 채택 (Level 0-3)

2. **기존 워크플로우 방해**
   - 이미 작동하는 시스템 변경
   - 완화: 기존 hooks 보존, 점진적 추가

3. **유지보수 부담**
   - Hook 스크립트 업데이트
   - 완화: 자동 업데이트 메커니즘

### Calibration (검증점)

**단기 (1주)**:
- ✅ Stage 5 계획 수립 (이 문서)
- ⏳ Pre-commit hook 구현 및 테스트
- ⏳ 기본 CI/CD 설정 (GitHub Actions)

**중기 (2주)**:
- ⏳ 전체 Hook 시스템 완성
- ⏳ 실제 프로젝트 적용 테스트
- ⏳ 문서화 완료

**장기 (1개월)**:
- ⏳ Stage 5 완료 선언
- ⏳ Stage 6 (Scale) 진입 준비
- ⏳ 커뮤니티 피드백 수집

---

## 🏗️ Hook 시스템 아키텍처

### Layer 구조 (7-Layer 확장)

```
Layer 1: Constitution (config/constitution.yaml)
    ↓
Layer 2: Execution (task_executor.py)
    ↓
Layer 3: Analysis (auto_improver.py, deep_analyzer.py)
    ↓
Layer 4: Optimization (verification_cache.py)
    ↓
Layer 5: Evidence (RUNS/evidence/)
    ↓
Layer 6: Knowledge (obsidian_bridge.py)
    ↓
Layer 7: Visualization (streamlit_app.py)
    ↓
[NEW] Layer 8: Hooks (Git + CI/CD) ← Stage 5
```

### Hook 트리거 맵

| 이벤트 | Hook | 실행 도구 | Constitution 조항 | 시간 제한 |
|--------|------|-----------|-------------------|-----------|
| **git add** | pre-commit | Ruff, P4/P5 검증 | P4, P5, P10 | <3초 |
| **git commit** | commit-msg | Conventional Commits | P9 | <0.5초 |
| **git commit 완료** | post-commit | Obsidian 동기화 | P3 | <2초 |
| **git push** | pre-push | 전체 테스트 | P8 | <30초 |
| **PR 생성** | CI (GitHub Actions) | 전체 Constitution | P1-P16 | <5분 |
| **PR 병합** | CI | 문서 자동 배포 | P3 | <2분 |
| **파일 변경 감지** | Watch 모드 | Auto-Improver | P4, P5, P7 | 백그라운드 |

---

## 📋 구현 계획 (3단계)

### Phase 1: Git Hooks (1주) - 우선순위 HIGH

**목표**: 로컬 개발 환경에 Constitution 강제

**구현**:
1. **Pre-commit Hook**
   ```python
   # .husky/pre-commit 또는 .git/hooks/pre-commit

   #!/usr/bin/env python3
   # 1. 변경된 파일만 Ruff 검사 (P10)
   # 2. P4 (SOLID) 간단 검증 (eval() 사용 금지 등)
   # 3. P5 (Security) 기본 검증 (secrets 커밋 방지)
   # 4. 3초 이내 완료 (성능 중요)
   ```

2. **Commit-msg Hook**
   ```python
   # .husky/commit-msg

   #!/usr/bin/env python3
   # 1. Conventional Commits 형식 검증 (P9)
   # 2. 0.5초 이내 완료
   ```

3. **Post-commit Hook**
   ```python
   # .husky/post-commit

   #!/usr/bin/env python3
   # 1. Obsidian 자동 동기화 (P3)
   # 2. 3개 이상 파일 변경 시만 실행
   # 3. 백그라운드 실행 (개발자 대기 불필요)
   ```

**테스트**:
- ✅ Windows/Linux/Mac 모두 작동
- ✅ 성능 목표 달성 (<3초)
- ✅ `--no-verify` 우회 가능 (강제 아님)

**완료 조건**:
- Pre-commit 3초 이내
- Commit-msg 0.5초 이내
- Post-commit 백그라운드 작동
- 문서화 완료 (설치 가이드)

### Phase 2: CI/CD 통합 (1주) - 우선순위 MEDIUM

**목표**: PR/Push 시 자동 검증

**구현**:
1. **GitHub Actions Workflow**
   ```yaml
   # .github/workflows/constitution-check.yml

   name: Constitution Check

   on:
     pull_request:
       branches: [main, master]
     push:
       branches: [tier1/*, tier2/*]

   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout
         - name: Setup Python
         - name: Install dependencies
         - name: Run Constitution Validator
         - name: Run Tests (P8)
         - name: Quality Gate (P6)
         - name: Upload Reports
   ```

2. **PR Gate**
   - 모든 Constitution 조항 검증
   - P6 Quality Gate 통과 필수
   - 실패 시 PR 병합 차단

3. **자동 댓글**
   - PR에 검증 결과 요약
   - 위반 사항 자동 리포트

**완료 조건**:
- GitHub Actions 작동
- PR 게이트 설정 완료
- 5분 이내 실행
- 다른 CI 플랫폼 가이드 (선택)

### Phase 3: Workflow 자동화 (1주) - 우선순위 LOW

**목표**: 반복 작업 완전 제거

**구현**:
1. **통합 CLI (`dev` 명령어)**
   ```bash
   dev check        # 전체 검증
   dev commit       # Constitution 준수 커밋
   dev pr           # PR 자동 생성 (검증 포함)
   dev sync         # Obsidian 수동 동기화
   dev stats        # 대시보드 업데이트
   ```

2. **컨텍스트 인지 실행**
   - 변경된 파일 기반 검증 범위 결정
   - 불필요한 검증 자동 스킵

3. **Watch 모드**
   ```bash
   dev watch        # 파일 변경 감지 → 자동 검증
   ```

**완료 조건**:
- CLI 도구 완성
- 사용자 가이드 작성
- 실제 사용 테스트

---

## 📐 설계 원칙

### 1. 속도 우선 (Performance First)

**원칙**: Hook이 느리면 개발자가 우회함

**구현**:
- Pre-commit: 변경된 파일만 검증
- 캐싱 적극 활용 (verification_cache.py)
- 병렬 실행 (가능한 경우)
- 시간 초과 시 경고만 (차단 안 함)

**측정**:
- 매 실행 시간 로깅
- 3초 초과 시 최적화 트리거

### 2. 점진적 채택 (Progressive Enhancement)

**원칙**: 강제 말고 선택

**레벨**:
- **Level 0**: Hook 없음 (기존 방식)
- **Level 1**: Pre-commit만 (Ruff + P9)
- **Level 2**: + CI/CD (자동 검증)
- **Level 3**: + Workflow CLI (완전 자동화)

**마이그레이션**:
```bash
# Level 0 → 1
./scripts/install_hooks.py --level 1

# Level 1 → 2
./scripts/setup_ci.py --platform github

# Level 2 → 3
pip install dev-rules-cli
```

### 3. 우회 가능 (Escape Hatch)

**원칙**: 긴급 상황 대비

**허용**:
- `git commit --no-verify` (pre-commit 우회)
- `SKIP_CONSTITUTION=1` (환경변수)
- CI에서 2차 검증 (우회해도 결국 잡힘)

**로깅**:
- 우회 횟수 추적
- 남용 시 알림 (강제는 아님)

### 4. 실패해도 안전 (Fail-Safe)

**원칙**: Hook 에러로 개발 중단 방지

**구현**:
```python
try:
    run_constitution_check()
except Exception as e:
    log_error(e)
    # 경고만 출력, 커밋은 허용
    print(f"[WARNING] Hook failed: {e}")
    print("[WARNING] Commit allowed, but please fix")
    sys.exit(0)  # 성공 코드 반환
```

---

## 🗺️ 불확실성 지도 (Uncertainty Map)

### Least Confident (가장 불확실한 부분)

1. **"Pre-commit이 3초 이내 완료 가능한가?"**
   - 근거: 없음 (추정)
   - 실제: 파일 수에 따라 5-10초 걸릴 수 있음
   - 완화: 변경된 파일만 검증, 캐싱
   - 검증: 실제 프로젝트에서 측정 필요

2. **"개발자가 Hook을 받아들일까?"**
   - 근거: 설문조사 없음
   - 실제: "또 귀찮은 규칙" 반발 가능
   - 완화: 선택적 채택, 우회 허용
   - 검증: 소수 팀원 파일럿 테스트

3. **"CI가 5분 이내 완료 가능한가?"**
   - 근거: 없음 (추정)
   - 실제: 테스트 수에 따라 10-20분 걸릴 수 있음
   - 완화: 병렬 실행, 선택적 테스트
   - 검증: GitHub Actions 실제 실행 측정

4. **"Hook이 정말 Constitution 준수율을 높일까?"**
   - 근거: 논리적 추론 (자동화 → 높은 준수율)
   - 실제: 우회 가능하므로 효과 제한적일 수 있음
   - 측정: 준수율 before/after 비교 필요
   - 기준: 현재 90% → 목표 95%+

### Oversimplified (과도하게 단순화된 부분)

1. **"모든 Hook이 독립적으로 작동"**
   - 단순화: Pre/Post commit 간 의존성 무시
   - 실제: Post-commit이 pre-commit 결과 참조 필요
   - 영향: 상태 공유 메커니즘 필요

2. **"CI는 항상 신뢰할 수 있다"**
   - 단순화: GitHub Actions 장애 가능성 무시
   - 실제: 네트워크, 서비스 장애 발생
   - 영향: 로컬 Hook이 최후 방어선

3. **"3초 이내면 개발자가 기다린다"**
   - 단순화: 개인차 무시
   - 실제: 1초 vs 3초 체감 차이 큼
   - 영향: 1초 목표가 더 안전

4. **"Conventional Commits를 모두가 이해한다"**
   - 단순화: 학습 곡선 무시
   - 실제: 처음 접하면 혼란
   - 영향: 에러 메시지에 예시 필요

### Opinion-Changing Questions (판단을 바꿀 수 있는 질문)

1. **"Hook이 실제로 개발 속도를 늦추는가?"**
   - 측정 방법: 커밋 빈도 before/after
   - 임계값: 커밋 시간 10% 이상 증가 시 재검토
   - 대안: Hook 간소화 또는 비활성화

2. **"개발자가 Hook을 우회하는 비율이 20% 이상인가?"**
   - 측정 방법: `--no-verify` 사용 로그
   - 임계값: 20% 이상이면 Hook 설계 재검토
   - 대안: 왜 우회하는지 인터뷰, 개선

3. **"CI 실패율이 80% 이상인가?"**
   - 측정 방법: GitHub Actions 성공/실패 비율
   - 임계값: 80% 실패면 너무 엄격
   - 대안: Quality Gate 기준 완화

4. **"Hook 설치에 30분 이상 걸리는가?"**
   - 측정 방법: 신규 팀원 온보딩 시간
   - 임계값: 30분 초과면 복잡도 과다
   - 대안: 자동 설치 스크립트, 클라우드 환경

5. **"Stage 5 완료에 1개월 이상 걸리는가?"**
   - 측정 방법: 실제 개발 시간
   - 임계값: 1개월 초과면 범위 과다
   - 대안: Phase 1만 구현, 2/3은 선택

---

## 📊 성공 지표 (Success Metrics)

### 정량적 지표

| 지표 | Before (Stage 4) | Target (Stage 5) | 측정 방법 |
|------|------------------|------------------|-----------|
| **Constitution 준수율** | 90% | 95%+ | 위반 건수/총 커밋 |
| **수동 개입 횟수** | 주 5회 | 주 1회 | 로그 분석 |
| **Pre-commit 시간** | N/A | <3초 | 실행 시간 측정 |
| **CI 실행 시간** | N/A | <5분 | GitHub Actions |
| **Hook 우회율** | N/A | <20% | `--no-verify` 사용 |

### 정성적 지표

- ✅ **개발자 만족도**: "Hook이 도움 된다" >60%
- ✅ **채택율**: 새 프로젝트 50% 이상 Hook 사용
- ✅ **유지보수성**: Hook 업데이트 <30분/월
- ✅ **문서 품질**: 신규 팀원이 30분 내 설정 가능

---

## 🎯 다음 즉시 작업 (Next Actions)

### 1. Pre-commit Hook 구현 (우선순위 1)

**파일**: `.husky/pre-commit` 또는 `.git/hooks/pre-commit`

**기능**:
- Ruff 검사 (P10 인코딩 포함)
- P4 기본 검증 (eval 금지 등)
- P5 시크릿 감지 (간단 패턴)

**시간**: 2-3시간

### 2. Commit-msg Hook 구현 (우선순위 1)

**파일**: `.husky/commit-msg`

**기능**:
- Conventional Commits 검증 (P9)
- 에러 메시지에 예시 포함

**시간**: 1시간

### 3. Post-commit Hook 구현 (우선순위 2)

**파일**: `.husky/post-commit`

**기능**:
- Obsidian 자동 동기화 (P3)
- 백그라운드 실행

**시간**: 1-2시간

### 4. 통합 테스트

**방법**:
- 실제 커밋 시나리오 10개
- Windows/Linux 양쪽 테스트
- 성능 측정

**시간**: 2시간

---

## 📚 참고 문서

**현재 프로젝트**:
- `config/constitution.yaml` - Constitution 전문
- `CLAUDE.md` - 빠른 참조
- `claudedocs/Stage4-Completion-Report.md` - Stage 4 완료 보고서

**외부 참조**:
- [Husky](https://typicode.github.io/husky/) - Git Hooks 관리
- [Conventional Commits](https://www.conventionalcommits.org/) - P9 표준
- [GitHub Actions](https://docs.github.com/en/actions) - CI/CD

---

**작성자**: AI (Claude) with VibeCoding Enhanced
**검증 상태**: STICC Context 기반 계획
**신뢰도**: MEDIUM (실행 전 검증 필요)
**다음 검증**: Pre-commit Hook 실제 구현 및 성능 측정

---

## 🎬 시작 준비 완료

**Stage 5 목표**: "Zero-touch Constitution 강제"

**첫 번째 작업**: Pre-commit Hook 구현

**예상 완료**: 1주일 (Phase 1)

**사용자 확인 필요**:
1. Git Hooks 설치 방식 (Husky vs 직접)
2. CI 플랫폼 (GitHub Actions vs 기타)
3. 우선순위 변경 여부

진행할까요?
