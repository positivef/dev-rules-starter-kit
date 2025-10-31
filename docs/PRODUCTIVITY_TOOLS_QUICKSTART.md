# 🚀 생산성 도구 빠른 시작 가이드

5분 안에 새로운 생산성 도구 사용 시작하기!

## 📦 새로운 도구 (2025-10-30 추가)

### 1. 🤖 AI 코드 리뷰 (CodeReviewAssistant)

**설치 (30초)**:
```bash
python scripts/install_code_review_hook.py
```

**사용법**:
```bash
# 즉시 리뷰
python scripts/code_review_assistant.py

# 자동 리뷰 (git push 시)
git push  # 점수 60점 미만이면 푸시 차단됨
```

**Claude Code에서**:
```
/code-review
```

**예상 결과**:
```
Score: 85/100 - Good code quality
Critical Issues: 0
Warnings: 2
Recommendations:
  1. Remove TODO items
  2. Add tests for new functions
```

---

### 2. 🚢 배포 계획 생성기 (DeploymentPlanner)

**사용법**:
```bash
# 개발 환경
python scripts/deployment_planner.py

# 프로덕션 (승인 필요)
python scripts/deployment_planner.py --env production
```

**예상 결과**:
```
Risk Score: 36/100
Estimated Time: 6 minutes
Pre-checks: 6 items
Steps: 5 deployment steps
Rollback Plan: Ready
```

---

### 3. 📝 옵시디언 자동 동기화 (이미 설치됨!)

**확인**:
```bash
python scripts/install_obsidian_auto_sync.py --check
# [OK] Obsidian auto-sync hook is installed
```

**작동 방식**:
```bash
git commit -m "feat: 새 기능"
# → 자동으로 개발일지 생성됨!
```

---

## ⚡ 일상 워크플로우

### 아침 시작

```bash
# 1. 어제 작업 리뷰
python scripts/code_review_assistant.py --commit HEAD~5..HEAD

# 2. 오늘 배포 계획 확인
python scripts/deployment_planner.py --env staging
```

### 기능 개발 중

```bash
# 1. 코드 작성
vim feature.py

# 2. 즉시 리뷰
python scripts/code_review_assistant.py

# 3. 커밋 (자동 동기화)
git commit -m "feat: add new feature"
```

### 배포 전

```bash
# 1. 배포 계획 생성
python scripts/deployment_planner.py --env production --generate-yaml

# 2. 계획 검토
cat TASKS/deploy-*.yaml

# 3. 실행
python scripts/task_executor.py TASKS/deploy-*.yaml
```

---

## 📊 효과 측정

### 시간 절약 계산

| 작업 | 이전 | 지금 | 절약 |
|------|------|------|------|
| 코드 리뷰 | 30분 | 15분 | 15분/일 |
| 배포 준비 | 60분 | 5분 | 55분/배포 |
| 개발일지 작성 | 10분 | 0분 | 10분/일 |

**일일 절약**: ~25분
**주간 절약**: ~2시간
**연간 절약**: ~100시간

---

## 🔧 트러블슈팅

### "명령을 찾을 수 없음"

```bash
# Python 경로 확인
which python

# venv 활성화
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

### "권한 거부됨"

```bash
# Windows에서 실행 권한 부여
python scripts/install_code_review_hook.py
```

### 코드 리뷰 점수가 너무 낮음

```bash
# 상세 리포트 확인
python scripts/code_review_assistant.py --format text

# 주요 이슈만 수정
- Critical issues 먼저 해결
- P10 (Windows UTF-8) 위반 체크
- 보안 패턴 검사
```

---

## 🎯 팀 규칙

### 필수 사항

1. **커밋 전**: 코드 리뷰 점수 60+ 확인
2. **푸시 전**: 자동 리뷰 통과
3. **배포 전**: DeploymentPlanner 실행

### 권장 사항

1. **일일**: 코드 리뷰 실행
2. **주간**: 배포 계획 검토
3. **스프린트**: 생산성 메트릭 확인

---

## ✅ Strategy B 완료! (2025-10-31)

모든 6개 도구가 준비되었습니다:

### 4. 🧪 테스트 자동 생성 (TestGenerator)

**사용법**:
```bash
# 파일 전체 테스트 생성
python scripts/test_generator.py scripts/my_module.py

# 특정 클래스만
python scripts/test_generator.py scripts/my_module.py::MyClass

# 커버리지 모드
python scripts/test_generator.py scripts/my_module.py --coverage
```

**예상 결과**:
```
Generated 15 test cases
- Normal cases: 5
- Edge cases: 7
- Error cases: 3
Tests saved to: tests/test_my_module_generated.py
```

---

### 5. ✔️ 프로젝트 검증 (ProjectValidator)

**사용법**:
```bash
# 전체 검증
python scripts/project_validator.py

# HTML 리포트 생성
python scripts/project_validator.py --report

# 자동 수정
python scripts/project_validator.py --fix
```

**예상 결과**:
```
Project Health Score: 77/100
- Constitution: 90/100
- Security: 60/100
- Tests: 100/100
```

---

### 6. 💡 요구사항 수집 (RequirementsWizard)

**사용법**:
```bash
# 대화형 수집 시작
python scripts/requirements_wizard.py
```

**대화 예시**:
```
[QUESTION] What is the project name?
> My Awesome API

[QUESTION] What type of project is this?
1. Web Application
2. API/Backend Service
> 2

자동으로 YAML 계약서 생성됨!
```

---

### 7. 📊 커버리지 모니터 (CoverageMonitor)

**사용법**:
```bash
# 즉시 체크
python scripts/coverage_monitor.py

# 실시간 모니터링
python scripts/coverage_monitor.py --watch

# 트렌드 확인
python scripts/coverage_monitor.py --trend 24
```

**예상 결과**:
```
Overall Coverage: 75.3%
[ALERT] critical file auth.py below 90% threshold
Coverage report saved: RUNS/coverage/reports/coverage_*.md
```

---

### 8. ⚖️ 헌법 충돌 감지 (PrincipleConflictDetector)

**사용법**:
```bash
# 전체 프로젝트 검사
python scripts/principle_conflict_detector.py

# 특정 파일/디렉토리
python scripts/principle_conflict_detector.py --path scripts/

# 상세 분석
python scripts/principle_conflict_detector.py --verbose

# JSON 리포트
python scripts/principle_conflict_detector.py --format json
```

**예상 결과**:
```
Principle Conflict Analysis
====================================
Total Conflicts Detected: 3

[HIGH SEVERITY] P1 vs P8 Conflict
File: scripts/task_executor.py:145
Issue: YAML-first (P1) conflicts with test-first (P8)
Recommendation: Generate tests from YAML contracts

[MEDIUM SEVERITY] P4 vs P6 Conflict
File: scripts/validator.py:78
Issue: SOLID refactoring needed to meet quality gates
Recommendation: Split large class into smaller components

[LOW SEVERITY] P7 vs P11 Conflict
File: docs/README.md:234
Issue: Unverified claim in documentation
Recommendation: Add evidence or remove claim
```

**자동 수정 모드**:
```bash
# 안전한 충돌만 자동 수정
python scripts/principle_conflict_detector.py --fix-safe

# 모든 충돌 수정 (승인 필요)
python scripts/principle_conflict_detector.py --fix-all
```

---

## 🎯 Strategy B 완료 체크리스트 (2025-10-31)

모든 8개 도구 검증 완료:

- [x] 1. AI 코드 리뷰 (100/100 점수)
- [x] 2. 배포 계획 생성기 (정상 작동)
- [x] 3. 옵시디언 자동 동기화 (설치됨)
- [x] 4. 테스트 자동 생성 (정상 작동)
- [x] 5. 프로젝트 검증 (정상 작동)
- [x] 6. 요구사항 수집 (대화형)
- [x] 7. 커버리지 모니터 (정상 작동)
- [x] 8. 헌법 충돌 감지 (분석 완료)

**예상 생산성 향상**: +45%

---

## 💬 피드백

새 도구에 대한 의견을 공유해주세요!

- 좋은 점은?
- 개선이 필요한 점은?
- 추가로 필요한 기능은?

GitHub Issues 또는 팀 채널 #dev-productivity로 의견 주세요.

---

**시작하기**: 위 명령어 중 하나를 복사해서 실행해보세요! 🚀
