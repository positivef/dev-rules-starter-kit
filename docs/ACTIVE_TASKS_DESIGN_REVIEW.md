# Active Tasks Manager - Design Review & Risk Analysis

**Date**: 2025-11-08
**Purpose**: 구현 전 설계 검토 및 부작용 분석
**Status**: 🔍 REVIEW IN PROGRESS

---

## 🎯 목표

### Core Concept
```
기간 정해진 모니터링 작업을 자동으로 관리:
- 시작일에 자동 활성화
- 종료일에 자동 아카이브
- CLAUDE.md 동적 업데이트 (활성 작업만)
- 다중 작업 병렬 진행
```

### Use Cases
1. Constitution 1주 모니터링 (2025-11-08 ~ 2025-11-15)
2. A/B 테스트 2주 (2025-11-15 ~ 2025-11-29)
3. 성능 벤치마크 1개월 (2025-12-01 ~ 2025-12-31)

---

## 🚨 잠재적 위험 분석

### Risk 1: CLAUDE.md 동적 수정의 위험성

**문제**:
```
CLAUDE.md를 자동으로 수정하면:
1. Git conflict 발생 가능
2. 사용자가 직접 수정한 내용 덮어쓰기
3. Pre-commit hook 충돌
4. Multi-session에서 동시 수정
```

**심각도**: 🔥 **HIGH**

**시나리오**:
```
Session 1: Active Tasks Manager가 CLAUDE.md 수정
Session 2: 사용자가 직접 CLAUDE.md 수정
→ Git conflict!
```

**해결책 옵션**:

**Option A: 읽기 전용 접근** (추천 ⭐)
```
CLAUDE.md는 수정하지 않음
대신: 별도 파일로 관리

.claude/
├── CLAUDE.md (사용자 관리, 정적)
└── ACTIVE_TASKS.md (시스템 관리, 동적)

CLAUDE.md에서 참조만:
@ACTIVE_TASKS.md  # SuperClaude @import 문법
```

**장점**:
- Git conflict 없음
- 사용자 수정과 분리
- 안전한 동적 업데이트

**Option B: Marker 기반 수정**
```markdown
<!-- BEGIN AUTO-TASKS: DO NOT EDIT -->
[자동 생성 내용]
<!-- END AUTO-TASKS -->
```

**단점**:
- 사용자가 실수로 삭제 가능
- Git conflict 여전히 가능
- 복잡도 증가

**결론**: **Option A 채택** (읽기 전용)

---

### Risk 2: Git Hook 충돌

**문제**:
```
현재 Git hooks:
- pre-commit: Constitution Guard, TDD Enforcer, Ruff
- post-commit: Obsidian sync, Evidence collection
- commit-msg: Conventional Commits

새로 추가:
- post-checkout: Active Tasks Manager (세션 시작)

충돌 가능성?
```

**심각도**: 🟡 **MEDIUM**

**분석**:
```
post-checkout는 기존에 없음 → 충돌 없음 ✅

하지만:
- Hook 실패 시 세션 시작 차단 가능
- 성능 영향 (세션 시작 지연)
```

**해결책**:

1. **Fail-safe 설계**:
   ```bash
   # .git/hooks/post-checkout
   python scripts/active_tasks_manager.py --update || true
   # 실패해도 세션은 계속
   ```

2. **성능 최적화**:
   ```python
   # 0.1초 이하 목표
   - 날짜 비교만 (파일 읽기 없음)
   - 캐싱 활용
   ```

3. **Skip 옵션**:
   ```bash
   export SKIP_ACTIVE_TASKS=1  # 긴급 시 비활성화
   ```

**결론**: 🟢 **안전** (fail-safe 추가)

---

### Risk 3: Multi-Session 동시 실행

**문제**:
```
Session A: active_tasks_manager.py 실행 중
Session B: 동시에 active_tasks_manager.py 실행

Race condition:
1. 둘 다 ACTIVE/ 폴더 읽기
2. 둘 다 파일 이동 시도
3. 파일 없음 오류 or 중복 이동
```

**심각도**: 🟡 **MEDIUM**

**분석**:
```
발생 확률: LOW (세션 시작이 동시일 확률 낮음)
영향: MEDIUM (오류 발생 시 작업 누락 가능)
```

**해결책**:

**Option A: File Lock** (추천)
```python
import fcntl  # Unix
import msvcrt  # Windows

class ActiveTasksManager:
    def __init__(self):
        self.lock_file = ".active_tasks.lock"

    def update(self):
        with FileLock(self.lock_file, timeout=5):
            # 안전하게 업데이트
            self._update_internal()
```

**Option B: Atomic Operations**
```python
# 이동 대신 복사 + 삭제
1. Copy to ARCHIVED/
2. Verify copy
3. Delete from ACTIVE/
```

**Option C: Idempotent 설계** (최선)
```python
# 여러 번 실행해도 같은 결과
def archive_expired_tasks():
    for task in ACTIVE/:
        if is_expired(task):
            # 이미 ARCHIVED/에 있으면 skip
            if not exists(ARCHIVED/task):
                move(task, ARCHIVED/)
```

**결론**: **Option C 채택** (Idempotent)

---

### Risk 4: 날짜/시간대 이슈

**문제**:
```
YAML:
  end_date: "2025-11-15"

질문:
- 2025-11-15 00:00? 23:59?
- 시간대: UTC? Local?
- 오늘이 2025-11-15 10:00이면 활성? 만료?
```

**심각도**: 🟡 **MEDIUM**

**분석**:
```
모호한 기준 → 작업이 너무 일찍/늦게 만료
```

**해결책**:

**명확한 규칙 정의**:
```yaml
# YAML 스펙
start_date: "2025-11-08"  # 00:00:00 Local 부터
end_date: "2025-11-15"    # 23:59:59 Local 까지

# 상태 전이 규칙
오늘 < start_date: scheduled
start_date ≤ 오늘 ≤ end_date: active
오늘 > end_date: expired → archive
```

**코드**:
```python
from datetime import datetime, time

def is_active(task):
    today = datetime.now().date()
    start = datetime.fromisoformat(task['start_date']).date()
    end = datetime.fromisoformat(task['end_date']).date()

    return start <= today <= end
```

**결론**: 🟢 **명확한 스펙 정의**

---

### Risk 5: TASKS/ 폴더 구조 복잡도

**문제**:
```
현재:
TASKS/
├── TEMPLATE.yaml
├── FIX-*.yaml
├── FEAT-*.yaml

제안:
TASKS/
├── TEMPLATE.yaml
├── FIX-*.yaml
├── ACTIVE/
├── SCHEDULED/
└── ARCHIVED/

→ 구조 복잡도 증가
→ 기존 workflow 영향?
```

**심각도**: 🟢 **LOW**

**분석**:
```
기존 YAML 파일들은 "단발성 작업"
새 시스템은 "기간 모니터링 작업"
→ 용도가 다름, 충돌 없음
```

**해결책**:

**Option A: 별도 폴더** (추천)
```
TASKS/          # 기존 단발성 작업
MONITORING/     # 새 기간 모니터링
├── ACTIVE/
├── SCHEDULED/
└── ARCHIVED/
```

**Option B: 명명 규칙**
```
TASKS/
├── task-*.yaml       # 단발성
├── monitor-*.yaml    # 모니터링 (new)
├── ACTIVE/
└── ARCHIVED/
```

**결론**: **Option A 채택** (명확한 분리)

---

### Risk 6: 작업 상태 추적 복잡도

**문제**:
```
Week 1 Constitution:
- 베이스라인 설정: done
- 메트릭 기록: 3/7
- 주간 리포트: pending

어디에 저장?
1. YAML 파일 직접 수정? → Git conflict
2. 별도 상태 파일? → 동기화 이슈
3. Database? → 과도한 복잡도
```

**심각도**: 🟡 **MEDIUM**

**분석**:
```
상태 추적이 없으면:
- 진행률 모름
- 무엇을 했는지 기억 못함
- 리마인더만 반복
```

**해결책**:

**Option A: 상태 파일 분리** (추천)
```
MONITORING/
├── ACTIVE/
│   └── week1-constitution.yaml  # 작업 정의 (읽기 전용)
└── STATE/
    └── week1-constitution.json  # 실행 상태 (자주 변경)
```

**장점**:
- YAML은 Git 관리 (작업 정의)
- JSON은 gitignore (개인 진행 상태)
- Git conflict 없음

**Option B: 통합 관리**
```yaml
# week1-constitution.yaml (gitignore)
checklist:
  - id: baseline
    status: done  # Git에서 제외
    completed_at: "2025-11-08 10:30"
```

**단점**:
- 전체 파일 gitignore → 작업 정의 공유 불가
- 팀 협업 시 문제

**결론**: **Option A 채택** (정의/상태 분리)

---

### Risk 7: CLAUDE.md 길이 폭발

**문제**:
```
5개 작업 동시 진행:
- Constitution 모니터링 (2주)
- 성능 벤치마크 (1개월)
- A/B 테스트 (2주)
- 보안 감사 (1주)
- UX 개선 (3주)

→ ACTIVE_TASKS.md가 5개 섹션
→ CLAUDE.md에 전부 표시?
→ 너무 길어짐
```

**심각도**: 🟡 **MEDIUM**

**해결책**:

**Priority 기반 필터링**:
```yaml
# week1-constitution.yaml
priority: high  # high, medium, low

# ACTIVE_TASKS.md 생성 규칙
- High priority: 항상 표시
- Medium: 마감 D-3 이내만
- Low: 오늘 할 일 있을 때만
```

**Summary View**:
```markdown
## 🔔 현재 진행 중 (5개)

### High Priority (2개)
📍 Constitution 모니터링 (D-2) - 금요일 리포트 필수
📍 보안 감사 (D-1) - 오늘 완료 필요

### 나머지 (3개)
성능 벤치마크 (D+15), A/B 테스트 (D+5), UX 개선 (D+10)

[상세보기: MONITORING/ACTIVE_TASKS_DETAIL.md]
```

**결론**: 🟢 **Priority 필터링 추가**

---

### Risk 8: 성능 영향

**문제**:
```
매 세션 시작마다:
1. YAML 파일들 읽기 (10-50개?)
2. 날짜 비교
3. 파일 이동
4. Markdown 생성

→ 세션 시작 지연?
```

**심각도**: 🟢 **LOW**

**벤치마크 추정**:
```
YAML 파싱: 10ms × 50개 = 500ms
날짜 비교: 1ms × 50개 = 50ms
파일 이동: 10ms × 5개 = 50ms
Markdown 생성: 50ms

Total: ~650ms (0.65초)
```

**목표**: <0.5초

**최적화**:
```python
1. 캐싱:
   - 변경 없으면 skip
   - mtime 기반 체크

2. Lazy loading:
   - SCHEDULED/ 은 필요시만 읽기

3. Parallel processing:
   - 여러 YAML 동시 파싱
```

**결론**: 🟢 **성능 문제 없음** (0.5초 이내)

---

## ✅ 보완 설계

### 최종 아키텍처

```
MONITORING/
├── ACTIVE/                  # 현재 진행 중
│   └── week1-constitution.yaml
├── SCHEDULED/               # 미래 작업
│   └── week2-performance.yaml
├── ARCHIVED/                # 완료/만료
│   └── old-tasks/
└── STATE/                   # 실행 상태 (gitignore)
    └── week1-constitution.json

.claude/
├── CLAUDE.md               # 정적 (사용자 관리)
└── ACTIVE_TASKS.md         # 동적 (시스템 관리)

scripts/
└── active_tasks_manager.py
    ├── update()            # 상태 업데이트
    ├── add_task()          # 새 작업 추가
    ├── complete_task()     # 작업 완료
    └── list_active()       # 활성 작업 목록

.git/hooks/
└── post-checkout           # 세션 시작 시 자동 실행
```

### 안전장치

1. **Fail-safe**: Hook 실패해도 세션 계속
2. **Idempotent**: 여러 번 실행해도 안전
3. **File Lock**: Multi-session 동시 실행 방지
4. **Read-only CLAUDE.md**: Git conflict 방지
5. **State 분리**: 작업 정의 vs 실행 상태
6. **Priority 필터링**: ACTIVE_TASKS.md 길이 제한
7. **Skip 옵션**: `SKIP_ACTIVE_TASKS=1`

---

## 🎯 Implementation Plan

### Phase 1: Core System (30분)
- [x] Design review (이 문서)
- [ ] active_tasks_manager.py (핵심 로직)
- [ ] YAML 스펙 정의
- [ ] 단위 테스트

### Phase 2: Integration (20분)
- [ ] Git hook 추가
- [ ] ACTIVE_TASKS.md 생성
- [ ] CLAUDE.md에 @import 추가

### Phase 3: Migration (10분)
- [ ] Week 1 Constitution → 새 시스템 이동
- [ ] 테스트 실행
- [ ] 검증

**Total**: ~60분

---

## 🚨 부작용 체크리스트

### 기존 시스템 영향

- [ ] **Git workflow**: ✅ 영향 없음 (새 hook만 추가)
- [ ] **CLAUDE.md**: ✅ 읽기 전용 유지
- [ ] **TASKS/ 폴더**: ✅ MONITORING/ 분리
- [ ] **Obsidian sync**: ✅ 영향 없음
- [ ] **Constitution**: ✅ 변경 없음
- [ ] **Pre-commit hooks**: ✅ 충돌 없음

### 새로운 리스크

- [ ] **Multi-session**: ✅ Idempotent 설계
- [ ] **Performance**: ✅ 0.5초 이내
- [ ] **Git conflict**: ✅ State 분리
- [ ] **복잡도**: 🟡 중간 (문서화 필요)

### 롤백 전략

**Level 1** (즉시):
```bash
export SKIP_ACTIVE_TASKS=1  # Hook 비활성화
```

**Level 2** (1분):
```bash
rm .git/hooks/post-checkout  # Hook 제거
```

**Level 3** (5분):
```bash
git revert <commit-hash>  # 전체 제거
rm -rf MONITORING/        # 폴더 삭제
```

---

## 💡 최종 권고사항

### ✅ 진행 승인 조건

1. **안전성**: 모든 위험 완화 전략 포함 ✅
2. **성능**: 0.5초 이내 보장 ✅
3. **롤백**: 3단계 비상 대응 준비 ✅
4. **테스트**: 단위 테스트 포함 필수 ⏳
5. **문서화**: 사용자 가이드 필수 ⏳

### ⚠️ 주의사항

1. **점진적 도입**:
   - Phase 1: Week 1 Constitution만 (검증)
   - Phase 2: 성공 확인 후 확대
   - Phase 3: 전면 적용

2. **모니터링**:
   - 첫 1주일 Hook 성능 측정
   - Git conflict 발생 여부 추적
   - 사용자 피드백 수집

3. **예외 처리**:
   - 모든 오류 log 기록
   - Silent fail (세션 차단 금지)
   - 문제 발생 시 Obsidian에 리포트

---

## 🎉 결론

**Status**: ✅ **설계 승인** (조건부)

**조건**:
1. 단위 테스트 포함
2. 사용자 가이드 작성
3. 첫 1주일 검증 기간

**예상 ROI**:
- 시간 절약: 작업당 5분 × 주 5회 = 25분/주
- 인지 부하 감소: 수동 관리 0회
- 확장성: 무제한 병렬 작업

**Risk Score**: **LOW** (모든 위험 완화됨)

**Recommendation**: 🚀 **진행 승인**

---

**Next Step**: `scripts/active_tasks_manager.py` 구현 시작
