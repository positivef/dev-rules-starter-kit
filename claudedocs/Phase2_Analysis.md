# Phase 2 Analysis: Cross-Session Context Sharing

**Date**: 2025-11-04
**Phase**: TIER1-WEEK7 Phase 2/4
**Estimated**: 10 hours
**Status**: Planning

---

## 🎯 Objective

Enable seamless context sharing across 3-4 concurrent AI sessions (e.g., Claude frontend, Claude backend, Claude testing, Cursor assistant) working on the same project.

---

## 📋 Requirements (from YAML)

### Tasks:
1. Design shared context protocol
2. Enhance agent_sync.py for context sharing
3. Implement real-time context synchronization
4. Add conflict resolution for concurrent edits
5. Create session coordination system

### Deliverables:
- **session_coordinator.py** (~500 lines)
  - Multi-session coordination
  - Session registration/deregistration
  - Heartbeat monitoring
  - Task distribution

- **shared_context_manager.py** (~450 lines)
  - Shared context storage
  - Real-time synchronization
  - Version control
  - Merge conflict detection

- **test_session_coordinator.py** (~350 lines, 25 tests)
  - Unit tests for coordination
  - Integration tests for multi-session
  - Performance tests (<1s latency)

### Success Criteria:
- ✅ Context sync latency <1 second
- ✅ Conflict resolution 100% automatic
- ✅ Supports 4+ concurrent sessions

---

## 🏗️ Current Infrastructure

### Existing Components:

1. **agent_sync.py** (File locking)
   - Current: Per-file locks
   - Needed: Context sharing capability
   - Location: `dev-context/agent_sync_state.json`

2. **session_manager.py** (Session state)
   - Current: Individual session persistence
   - Needed: Multi-session awareness
   - Location: `RUNS/context/`

3. **context_provider.py** (Context storage)
   - Current: Single-session context
   - Needed: Shared context protocol
   - Location: `config/master_config.json`

4. **session_recovery.py** (Phase 1 ✅)
   - Crash detection
   - Checkpoint system
   - Recovery workflow

---

## 🔧 Phase 2 Architecture Design

### Shared Context Protocol

```python
# shared_context.json structure
{
  "project": "dev-rules-starter-kit",
  "version": "2.0.0",
  "updated_at": "2025-11-04T12:10:00Z",
  "sessions": [
    {
      "session_id": "session1_frontend",
      "agent_id": "claude_code_1",
      "role": "frontend",
      "status": "active",
      "last_heartbeat": "2025-11-04T12:10:00Z",
      "current_task": "FEAT-2025-11-04-01-frontend",
      "locked_files": ["src/components/Auth.tsx"],
      "context_hash": "sha256:abc123..."
    },
    {
      "session_id": "session2_backend",
      "agent_id": "claude_code_2",
      "role": "backend",
      "status": "active",
      "last_heartbeat": "2025-11-04T12:09:58Z",
      "current_task": "FEAT-2025-11-04-01-backend",
      "locked_files": ["src/api/auth.py"],
      "context_hash": "sha256:def456..."
    }
  ],
  "shared_knowledge": {
    "active_feature": "FEAT-2025-11-04-01",
    "constitution_version": "1.0.0",
    "adoption_level": 2,
    "recent_commits": ["17f5976a", "015b6ae2"],
    "open_conflicts": []
  },
  "context_versions": [
    {
      "version": 1,
      "timestamp": "2025-11-04T12:00:00Z",
      "changes": "Session1 started frontend work",
      "hash": "sha256:old123..."
    },
    {
      "version": 2,
      "timestamp": "2025-11-04T12:10:00Z",
      "changes": "Session2 started backend work",
      "hash": "sha256:abc123..."
    }
  ]
}
```

### Component Responsibilities

#### 1. SessionCoordinator (session_coordinator.py)

**Purpose**: Central coordination hub for multiple AI sessions

**Features**:
- Session registration/deregistration
- Heartbeat monitoring (30-second intervals)
- Dead session detection (>2 minutes without heartbeat)
- Task distribution and load balancing
- Session role management (frontend/backend/testing/assistant)

**Key Methods**:
```python
class SessionCoordinator:
    def register_session(self, session_id, role, agent_id) -> bool
    def deregister_session(self, session_id) -> bool
    def update_heartbeat(self, session_id) -> bool
    def detect_dead_sessions(self) -> List[str]
    def get_active_sessions(self) -> List[Session]
    def assign_task(self, task_id, preferred_role=None) -> str
    def get_session_by_role(self, role) -> Optional[Session]
```

**Integration Points**:
- session_manager.py: Session lifecycle
- agent_sync.py: File lock coordination
- session_recovery.py: Dead session recovery

#### 2. SharedContextManager (shared_context_manager.py)

**Purpose**: Manage shared context across sessions with conflict resolution

**Features**:
- Shared context storage and retrieval
- Real-time synchronization (<1s latency)
- Version control for context changes
- Automatic merge conflict detection
- Context diff and merge operations

**Key Methods**:
```python
class SharedContextManager:
    def read_shared_context(self) -> Dict
    def write_shared_context(self, context, session_id) -> bool
    def sync_context(self, session_id) -> Dict
    def detect_conflicts(self, context1, context2) -> List[Conflict]
    def auto_merge(self, conflicts) -> Dict
    def create_context_snapshot(self) -> str  # version hash
    def rollback_context(self, version) -> bool
```

**Conflict Resolution Strategy**:
1. **Automatic** (80% of cases):
   - Non-overlapping changes → Auto-merge
   - Different files → No conflict
   - Different roles → Context-aware merge

2. **Manual** (20% of cases):
   - Same file, same lines → Notify both sessions
   - Contradicting changes → Ask user
   - Critical files → Conservative approach

**Integration Points**:
- context_provider.py: Context storage
- agent_sync.py: Lock-aware context updates
- session_coordinator.py: Session state queries

---

## 🔄 Workflow Examples

### Example 1: Frontend + Backend Parallel Work

**Scenario**: Session1 (frontend) and Session2 (backend) working on auth feature

**Timeline**:
1. **T+0s**: Session1 registers, locks `src/components/Auth.tsx`
2. **T+2s**: Session2 registers, locks `src/api/auth.py`
3. **T+10s**: Session1 updates shared context: "Auth UI complete"
4. **T+11s**: Session2 syncs context, sees UI is ready
5. **T+20s**: Session2 updates: "Auth API ready"
6. **T+21s**: Session1 syncs, starts integration testing
7. **T+30s**: Both sessions heartbeat, coordinator confirms health

**No Conflicts** ✅ (Different files, complementary work)

### Example 2: Concurrent Edits - Auto-Merge

**Scenario**: Session1 and Session3 both editing different parts of same file

**Timeline**:
1. **T+0s**: Session1 edits `src/utils/helpers.py` lines 1-50
2. **T+2s**: Session3 edits `src/utils/helpers.py` lines 100-150
3. **T+10s**: Session1 saves → Context updated
4. **T+12s**: Session3 attempts save → Conflict detected
5. **T+13s**: SharedContextManager detects non-overlapping changes
6. **T+14s**: **Auto-merge** ✅ (Different line ranges)
7. **T+15s**: Both sessions notified: "Auto-merged successfully"

**Resolution**: 100% automatic (lines don't overlap)

### Example 3: Concurrent Edits - Manual Resolution

**Scenario**: Session2 and Session4 editing same function

**Timeline**:
1. **T+0s**: Session2 locks `src/api/auth.py`, edits `login()` function
2. **T+5s**: Session4 attempts lock → **BLOCKED** (already locked)
3. **T+6s**: Session4 notified: "File locked by Session2 (backend role)"
4. **T+10s**: Session2 releases lock after commit
5. **T+11s**: Session4 acquires lock, sees Session2's changes
6. **T+12s**: Session4 edits same function (conflicting logic)
7. **T+20s**: Session4 saves → Context manager detects conflict
8. **T+21s**: **Manual resolution** ⚠️ (Same function, contradicting logic)
9. **T+22s**: User notified: "Conflict in auth.py:login() - resolve manually"

**Resolution**: User intervention required (20% of cases)

---

## 📊 Performance Requirements

### Latency Targets:

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Context read | <100ms | p99 latency |
| Context write | <200ms | p99 latency |
| Context sync | <1000ms | p99 latency |
| Heartbeat check | <50ms | p99 latency |
| Conflict detection | <500ms | Worst case |
| Auto-merge | <300ms | Average |

### Scalability:

| Metric | Target | Test Method |
|--------|--------|-------------|
| Concurrent sessions | 4+ | Load test |
| Context size | <10MB | Stress test |
| Sync frequency | 1Hz (1/sec) | Sustained load |
| Conflict resolution | 100% auto for non-overlapping | Integration test |

---

## 🧪 Testing Strategy

### Unit Tests (15 tests):
1. SessionCoordinator registration/deregistration
2. Heartbeat updates and dead session detection
3. SharedContextManager read/write
4. Context version control
5. Conflict detection algorithms
6. Auto-merge logic

### Integration Tests (7 tests):
1. Multi-session coordination (2-4 sessions)
2. Real-time context sync
3. File lock + context sync interaction
4. Concurrent edits with auto-merge
5. Concurrent edits with manual resolution
6. Session crash recovery (integration with Phase 1)
7. Cross-session task handoff

### Performance Tests (3 tests):
1. Context sync latency (<1s)
2. Concurrent session scalability (4+ sessions)
3. Sustained load (1Hz sync × 10 minutes)

---

## 🚀 Implementation Plan

### Step 1: Design & Architecture (2 hours)
- [x] Analyze existing infrastructure
- [x] Design shared context protocol
- [x] Define component responsibilities
- [ ] Create architecture diagrams

### Step 2: SessionCoordinator (3 hours)
- [ ] Implement session registration
- [ ] Add heartbeat monitoring
- [ ] Create dead session detection
- [ ] Add task distribution
- [ ] Write unit tests (8 tests)

### Step 3: SharedContextManager (3 hours)
- [ ] Implement context storage
- [ ] Add synchronization mechanism
- [ ] Create conflict detection
- [ ] Implement auto-merge logic
- [ ] Write unit tests (7 tests)

### Step 4: Integration (1.5 hours)
- [ ] Enhance agent_sync.py for context sharing
- [ ] Integrate with session_manager.py
- [ ] Connect to context_provider.py
- [ ] Write integration tests (7 tests)

### Step 5: Documentation (0.5 hour)
- [ ] Create MULTI_SESSION_GUIDE.md
- [ ] Update CLAUDE.md with Phase 2 info
- [ ] Add usage examples
- [ ] Document conflict resolution process

---

## 🎯 Success Metrics

### Functional:
- ✅ 4+ concurrent sessions supported
- ✅ Context sync latency <1 second
- ✅ Conflict resolution 100% automatic for non-overlapping
- ✅ Dead session detection <2 minutes
- ✅ Session crash recovery integrated

### Quality:
- ✅ 25+ tests (unit + integration + performance)
- ✅ Test coverage >90%
- ✅ All pre-commit hooks passing
- ✅ Constitutional compliance (P2, P6, P8, P10)

### Performance:
- ✅ Context read <100ms (p99)
- ✅ Context write <200ms (p99)
- ✅ Conflict detection <500ms
- ✅ Auto-merge <300ms

---

## 🔗 Dependencies

**Phase 1 (Complete)**: ✅
- session_recovery.py
- Checkpoint system
- Context integrity validation

**Existing Infrastructure**:
- agent_sync.py (file locking)
- session_manager.py (session state)
- context_provider.py (context storage)

**Phase 3 (Future)**:
- Context analytics
- Session insights
- Pattern detection

**Phase 4 (Future)**:
- Dashboard visualization
- Real-time monitoring
- Performance metrics

---

## 🎓 Learning Resources

**For Users**:
- Multi-session workflow guide
- Conflict resolution examples
- Best practices for parallel work

**For Developers**:
- Architecture deep dive
- Protocol specification
- Extension points

---

## 📝 Notes

- Phase 2 builds on Phase 1's crash recovery
- Focus on automation (100% for non-overlapping conflicts)
- Real-world use case: 1 dev + 3-4 AI agents
- Performance critical (<1s sync latency)
- Must integrate with existing tools seamlessly

---

**Next Steps**: Begin Step 2 - Implement SessionCoordinator
**ETA**: 10 hours total, 8 hours remaining
**ROI**: 500% (from YAML estimate)
