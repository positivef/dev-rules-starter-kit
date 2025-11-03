# Multi-AI Session Guide - 동시 협업 워크플로우

**Use Case**: 1명 개발자 + 3-4 AI 세션 동시 작업
**목표**: 세션 간 충돌 방지 및 효율적 협업

## 🤖 실제 사용 환경

**개발자**: 1명 (You)

**AI 워커들**:
- **Session 1 (Claude)**: Frontend UI 개발
- **Session 2 (Claude)**: Backend API
- **Session 3 (Claude)**: 테스트 작성
- **Session 4 (Cursor/Copilot)**: 실시간 코드 어시스트

**핵심**: 모두 같은 Constitution을 따라야 함!

## 🔧 Setup for Multi-Session

### 1. Project-Level Configuration (All Sessions)

```bash
# .constitution-config.yaml이 모든 세션의 기준
cat .constitution-config.yaml

# Key settings:
# - adoption.level: 2 (모든 세션 동일)
# - lock_config: true (세션별 변경 금지)
# - sessions.max_concurrent: 4
```

### 2. Session Initialization (Each AI Session)

```bash
# 각 AI 세션 시작 시 실행
python scripts/context_provider.py init
python scripts/session_manager.py start

# agent_sync.py가 자동으로 세션 등록
python scripts/agent_sync_status.py  # 현재 활성 세션 확인
```

### 3. Session Coordination

**Agent Sync System** (이미 구현됨):

```bash
# 세션 간 파일 잠금 확인
python scripts/agent_sync_status.py --files src/auth.py

# 출력 예시:
# src/auth.py
#   - Locked by: Session2_Backend
#   - Since: 2025-11-03 10:30
#   - Conflict: Yes (Session1도 편집 시도)
```

**Conflict Prevention**:
- agent_sync.py가 자동으로 파일 잠금 관리
- 동시 편집 시도 시 경고
- 한 세션이 완료할 때까지 대기

## 📋 Multi-Session Workflow Example

### Scenario: 인증 시스템 구현

**Session 1 (Frontend - Claude)**:

```bash
# TASKS/FEAT-20251103-01-frontend.yaml
task_id: "FEAT-20251103-01-frontend"
title: "Login UI 구현"
commands:
  - exec: ["npm", "run", "dev"]
gates:
  - type: "constitutional"
    articles: ["P4", "P8"]

python scripts/task_executor.py TASKS/FEAT-20251103-01-frontend.yaml
```

**Session 2 (Backend - Claude)**:

```bash
# TASKS/FEAT-20251103-01-backend.yaml
task_id: "FEAT-20251103-01-backend"
title: "Auth API 구현"
commands:
  - exec: ["python", "-m", "pytest", "tests/test_auth.py"]
gates:
  - type: "constitutional"
    articles: ["P4", "P5", "P8"]

python scripts/task_executor.py TASKS/FEAT-20251103-01-backend.yaml
```

**Session 3 (Testing - Claude)**:

```bash
# TASKS/FEAT-20251103-01-testing.yaml
task_id: "FEAT-20251103-01-testing"
title: "인증 통합 테스트"
commands:
  - exec: ["pytest", "tests/integration/"]
gates:
  - type: "constitutional"
    articles: ["P8"]

python scripts/task_executor.py TASKS/FEAT-20251103-01-testing.yaml
```

**Session 4 (Assistant - Cursor/Copilot)**:

```bash
# 실시간 코드 어시스트 (YAML 불필요)
# 3줄 이하 수정이므로 Level 2에서도 OK
git commit -m "fix(auth): correct typo in validation"
```

## 🔄 Context Sharing Between Sessions

### Shared State File

```bash
# RUNS/context/shared_state.json
{
  "project": "Dev Rules Starter Kit",
  "constitution_version": "1.0.0",
  "adoption_level": 2,
  "active_sessions": [
    {
      "id": "session1_frontend",
      "role": "frontend",
      "status": "active",
      "current_task": "FEAT-20251103-01-frontend"
    },
    {
      "id": "session2_backend",
      "role": "backend",
      "status": "active",
      "current_task": "FEAT-20251103-01-backend"
    }
  ],
  "locked_files": [
    "src/auth.py",
    "tests/test_auth.py"
  ]
}
```

### Reading Shared Context (Each Session)

```bash
# 세션 시작 시 자동 로드
python scripts/context_aware_loader.py --resume

# 수동 확인
python scripts/context_provider.py get-context
```

## ⚠️ Common Multi-Session Pitfalls

### 1. Conflicting Changes

**문제**: Session 1과 2가 같은 파일 동시 수정

**해결**: agent_sync.py 자동 잠금

```bash
# Before editing:
python scripts/agent_sync_status.py --agent session1 --files src/auth.py

# If locked:
# [BLOCKED] src/auth.py is locked by session2
# Wait for session2 to finish
```

### 2. Inconsistent Adoption Levels

**문제**: Session 1은 Level 3, Session 2는 Level 1

**해결**: .constitution-config.yaml의 lock_config: true

```yaml
adoption:
  level: 2  # All sessions forced to this
  lock_config: true  # Sessions cannot override
```

### 3. Lost Context

**문제**: Session 2가 Session 1의 작업을 모름

**해결**: Shared context + Evidence

```bash
# Session 2 reads Session 1's evidence:
ls RUNS/evidence/FEAT-20251103-01-frontend/

# Session 2 sees what Session 1 did:
cat RUNS/evidence/FEAT-20251103-01-frontend/execution_log.txt
```

## ✅ Best Practices for Multi-Session

### 1. Session Specialization

- **Frontend Session**: UI components, styling, user interactions
- **Backend Session**: API, database, business logic
- **Testing Session**: Test generation, integration tests
- **Assistant Session**: Quick fixes, typo corrections, real-time help

### 2. Communication Protocol

```bash
# Session 1 finishes task:
python scripts/task_executor.py TASKS/frontend.yaml
# → Evidence generated to RUNS/evidence/

# Session 2 starts dependent task:
python scripts/task_executor.py TASKS/backend.yaml
# → Reads Session 1's evidence for context
```

### 3. Checkpoint Synchronization

```bash
# Every 30 minutes, all sessions:
python scripts/session_manager.py save

# Before major changes:
python scripts/session_manager.py checkpoint "before-auth-refactor"
```

### 4. Conflict Resolution Strategy

```
Session tries to edit file
    ↓
Is file locked?
    ├─ No → Acquire lock via agent_sync
    │       Do work
    │       Release lock
    │
    └─ Yes → Check lock owner
            ↓
            Same feature?
            ├─ Yes → Coordinate: Split work
            └─ No → Wait or edit different file
```

## 🎯 Multi-Session Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Conflict Rate | <5% | Locked file conflicts per day |
| Context Sync | <3 seconds | Time to update shared_state.json |
| Session Consistency | 100% | All sessions on same adoption level |
| Evidence Sharing | >95% | Sessions reading others' evidence |

## 🚀 Advanced: Session Orchestration

### Parallel Task Execution

```bash
# Terminal 1: Frontend session
python scripts/task_executor.py TASKS/frontend.yaml &

# Terminal 2: Backend session
python scripts/task_executor.py TASKS/backend.yaml &

# Terminal 3: Testing session
python scripts/task_executor.py TASKS/testing.yaml &

# Monitor all:
python scripts/lock_dashboard_streamlit.py  # Real-time dashboard
```

### Session Handoff

```bash
# Session 1 completes Phase 1:
python scripts/task_executor.py TASKS/phase1.yaml
python scripts/session_manager.py save
python scripts/obsidian_bridge.py sync  # Knowledge base update

# Session 2 picks up Phase 2:
python scripts/context_aware_loader.py --resume
# → Automatically loads Phase 1 context
python scripts/task_executor.py TASKS/phase2.yaml
```

## 📚 Related Files

- **.constitution-config.yaml**: Project-level settings (all sessions)
- **scripts/agent_sync.py**: File locking and conflict detection
- **scripts/agent_sync_status.py**: Check lock status
- **scripts/lock_dashboard_streamlit.py**: Real-time session dashboard
- **RUNS/context/shared_state.json**: Shared context across sessions
- **dev-context/agent_sync_state.json**: Agent lock state

## 🔍 Troubleshooting Multi-Session Issues

```bash
# Issue: Session can't acquire lock
python scripts/agent_sync_status.py
# → See which session holds the lock
# → Wait or ask that session to commit

# Issue: Inconsistent context
python scripts/context_provider.py diagnose
# → Checks context hash consistency

# Issue: Too many conflicts
python scripts/lock_dashboard.py --agent all --conflicts
# → Shows conflict patterns
# → Suggests work distribution

# Issue: Lost session state
python scripts/session_manager.py restore --session <id>
# → Restores from last checkpoint
```

## 📊 Performance Tuning

### Reduce Lock Contention

```python
# config/multi_session.yaml
lock_strategy:
  timeout_seconds: 30  # Wait 30s before giving up
  retry_interval: 5    # Check every 5s
  auto_release: 300    # Auto-release after 5min inactivity
```

### Optimize Context Sync

```python
# config/context_sync.yaml
sync_strategy:
  interval_seconds: 60  # Sync every minute
  incremental: true     # Only sync changes
  compression: true     # Compress large contexts
```

---

## 📚 See Also

**필수 참고 문서**:
- **[CLAUDE.md](../CLAUDE.md)** - 일상 개발 명령어 및 기본 워크플로우
- **[ADOPTION_GUIDE.md](ADOPTION_GUIDE.md)** - Level 2-3 채택 필수 (멀티 세션은 Level 2+에서 권장)

**고급 활용**:
- **[SESSION_MANAGEMENT_GUIDE.md](SESSION_MANAGEMENT_GUIDE.md)** - 세션 상태 관리 및 체크포인트 상세
- **[TRADEOFF_ANALYSIS.md](TRADEOFF_ANALYSIS.md)** - 멀티 세션 충돌 방지 전략 (부작용 #2)

**마이그레이션 팀**:
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - 기존 프로젝트에 멀티 세션 도입 시 주의사항

**빠른 시작**:
- **[QUICK_START.md](QUICK_START.md)** - 단일 세션부터 시작 추천

---

**마지막 업데이트**: 2025-11-04
**대상 독자**: 1 개발자 + 3-4 AI 세션 운영자
**소요 시간**: 30분 (Setup) + 20분 (첫 멀티 세션)
