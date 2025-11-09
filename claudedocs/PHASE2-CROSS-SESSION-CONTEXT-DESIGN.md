# Phase 2: Cross-Session Context Sharing - Design Document

**Date**: 2025-11-09
**Status**: DESIGN
**Phase**: Week 7, Phase 2

---

## 1. Overview

Enable real-time context sharing across multiple AI sessions working on the same project.

### Goals
- Context sync latency <1 second
- 100% automatic conflict resolution
- Support 4+ concurrent sessions

### Existing Systems to Leverage
1. **agent_sync.py**: File-level locking (dev-context/agent_sync_state.json)
2. **session_manager.py**: Session state + checkpointing (RUNS/sessions/)
3. **context_provider.py**: Static context loading (master_config.json + .env)

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Session 1 (AI Agent A)                │
├─────────────────────────────────────────────────────────┤
│  session_manager.py │ → │ session_coordinator.py │     │
│         ↕              ↕              ↕                 │
│  SessionState    │ Context Events │ Shared Context     │
└─────────────┬───────────────┬──────────────────────────┘
              │               │
         ┌────▼───────────────▼─────┐
         │ shared_context_manager.py │ ← Central coordination layer
         │                            │
         │  - Shared context store    │
         │  - Event broadcasting      │
         │  - Conflict resolution     │
         └────┬───────────────┬───────┘
              │               │
┌─────────────▼───────────────▼──────────────────────────┐
│                   Session 2 (AI Agent B)                │
├─────────────────────────────────────────────────────────┤
│  session_manager.py │ → │ session_coordinator.py │     │
│         ↕              ↕              ↕                 │
│  SessionState    │ Context Events │ Shared Context     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Context Update Flow**:
   ```
   Session A updates context
   → session_coordinator.py notifies shared_context_manager
   → shared_context_manager validates + stores
   → Broadcasts to all active sessions
   → Session B receives update (<1s latency)
   ```

2. **Conflict Detection Flow**:
   ```
   Session A: Update key "current_task" to "auth"
   Session B: Update key "current_task" to "database" (concurrent)
   → shared_context_manager detects conflict
   → Applies resolution strategy (last-write-wins with merge)
   → Broadcasts resolved state to both sessions
   ```

---

## 3. Component Specifications

### 3.1 shared_context_manager.py (~450 lines)

**Purpose**: Central store for shared context across sessions

**Core Classes**:

```python
@dataclass
class ContextEvent:
    """Context change event"""
    event_id: str
    session_id: str
    timestamp: str
    event_type: str  # "update", "delete", "merge"
    key: str
    value: Any
    previous_value: Optional[Any]
    context_hash: str

@dataclass
class SharedContext:
    """Shared context state"""
    context_id: str
    created_at: str
    last_updated: str
    sessions: List[str]  # Active session IDs
    data: Dict[str, Any]  # Shared key-value store
    version: int  # Optimistic locking version
    event_log: List[ContextEvent]  # Audit trail

class SharedContextManager:
    """Manages shared context across sessions"""

    def __init__(self):
        self.storage_path = Path("RUNS/shared_context")
        self.context_file = self.storage_path / "shared_context.json"
        self.event_log_file = self.storage_path / "event_log.jsonl"

    def get_context(self, session_id: str) -> SharedContext:
        """Get current shared context for session"""

    def update_context(self, session_id: str, key: str, value: Any) -> ContextEvent:
        """Update shared context with conflict detection"""

    def subscribe(self, session_id: str) -> None:
        """Register session for context updates"""

    def unsubscribe(self, session_id: str) -> None:
        """Unregister session"""

    def get_pending_events(self, session_id: str, since_timestamp: str) -> List[ContextEvent]:
        """Get events since last poll (for sync)"""

    def resolve_conflict(self, event1: ContextEvent, event2: ContextEvent) -> ContextEvent:
        """Automatic conflict resolution"""
        # Strategy: Last-write-wins with intelligent merge for collections
```

**Storage Format** (RUNS/shared_context/shared_context.json):
```json
{
  "context_id": "ctx_20251109_001",
  "created_at": "2025-11-09T07:00:00Z",
  "last_updated": "2025-11-09T07:15:30Z",
  "sessions": ["session_001", "session_002", "session_003"],
  "data": {
    "current_phase": "Phase 2",
    "active_files": ["scripts/session_coordinator.py"],
    "completed_tasks": ["Phase 1"],
    "team_notes": "Implementing cross-session sync"
  },
  "version": 15
}
```

**Event Log Format** (event_log.jsonl - append-only):
```jsonlines
{"event_id":"evt_001","session_id":"session_001","timestamp":"2025-11-09T07:15:30Z","event_type":"update","key":"current_phase","value":"Phase 2","previous_value":"Phase 1","context_hash":"abc123"}
{"event_id":"evt_002","session_id":"session_002","timestamp":"2025-11-09T07:15:31Z","event_type":"update","key":"active_files","value":["scripts/session_coordinator.py"],"previous_value":[],"context_hash":"def456"}
```

---

### 3.2 session_coordinator.py (~500 lines)

**Purpose**: Coordination layer for individual sessions

**Core Classes**:

```python
@dataclass
class SessionInfo:
    """Session metadata"""
    session_id: str
    started_at: str
    last_heartbeat: str
    status: str  # "active", "idle", "crashed"
    current_task: Optional[str]
    assigned_files: List[str]

class SessionCoordinator:
    """Coordinates single session with shared context"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_manager = SessionManager.get_instance()
        self.shared_context = SharedContextManager()
        self.poll_interval = 1.0  # 1 second for <1s latency
        self.sync_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start coordination (subscribes to shared context)"""
        self.shared_context.subscribe(self.session_id)
        self._start_sync_thread()

    def stop(self) -> None:
        """Stop coordination (unsubscribes)"""
        self.shared_context.unsubscribe(self.session_id)
        self._stop_sync_thread()

    def update_shared(self, key: str, value: Any) -> None:
        """Update shared context (propagates to all sessions)"""
        event = self.shared_context.update_context(self.session_id, key, value)
        # Also update local session state
        self.session_manager.set(f"shared:{key}", value, StateScope.SESSION)

    def get_shared(self, key: str, default: Any = None) -> Any:
        """Get value from shared context"""
        context = self.shared_context.get_context(self.session_id)
        return context.data.get(key, default)

    def _sync_loop(self) -> None:
        """Background thread: poll for context updates"""
        last_sync = datetime.now(timezone.utc).isoformat()
        while not self.stop_event.is_set():
            time.sleep(self.poll_interval)

            # Get events since last sync
            events = self.shared_context.get_pending_events(self.session_id, last_sync)
            for event in events:
                self._handle_context_event(event)

            if events:
                last_sync = events[-1].timestamp

    def _handle_context_event(self, event: ContextEvent) -> None:
        """Handle incoming context update from other sessions"""
        # Skip self-generated events
        if event.session_id == self.session_id:
            return

        # Update local session state
        self.session_manager.set(f"shared:{event.key}", event.value, StateScope.SESSION)

        # Notify user (optional)
        print(f"[CONTEXT_UPDATE] {event.key} updated by {event.session_id}")

    def get_all_active_sessions(self) -> List[SessionInfo]:
        """Get list of all active sessions"""
        context = self.shared_context.get_context(self.session_id)
        sessions = []
        for session_id in context.sessions:
            # TODO: Load session metadata
            sessions.append(SessionInfo(...))
        return sessions
```

---

## 4. Conflict Resolution Strategy

### 4.1 Conflict Types

1. **Simple Value Conflict**:
   - Session A: `current_task = "auth"`
   - Session B: `current_task = "database"`
   - **Resolution**: Last-write-wins (based on timestamp)

2. **List Append Conflict**:
   - Session A: `active_files.append("auth.py")`
   - Session B: `active_files.append("db.py")`
   - **Resolution**: Merge both (union)

3. **Dict Merge Conflict**:
   - Session A: `team_notes["auth"] = "working"`
   - Session B: `team_notes["database"] = "done"`
   - **Resolution**: Deep merge

### 4.2 Resolution Algorithm

```python
def resolve_conflict(self, event1: ContextEvent, event2: ContextEvent) -> ContextEvent:
    """Intelligent conflict resolution"""

    # Same key updated by different sessions
    if event1.key != event2.key:
        return None  # No conflict

    # Strategy 1: Last-write-wins (default)
    if event1.timestamp > event2.timestamp:
        winner = event1
    else:
        winner = event2

    # Strategy 2: Smart merge for collections
    if isinstance(event1.value, list) and isinstance(event2.value, list):
        # Merge lists (union)
        merged = list(set(event1.value) | set(event2.value))
        return ContextEvent(
            event_id=f"merged_{event1.event_id}_{event2.event_id}",
            session_id="system",
            timestamp=max(event1.timestamp, event2.timestamp),
            event_type="merge",
            key=event1.key,
            value=merged,
            previous_value=event1.previous_value,
            context_hash=self._generate_hash(merged)
        )

    # Strategy 3: Deep merge for dicts
    if isinstance(event1.value, dict) and isinstance(event2.value, dict):
        merged = {**event1.value, **event2.value}
        return ContextEvent(..., value=merged, ...)

    return winner
```

---

## 5. Integration with Existing Systems

### 5.1 session_manager.py Integration

```python
# In session_manager.py, add shared context support

class SessionManager:
    def __init__(self):
        # ... existing code
        self.coordinator = None  # Will be set if multi-session enabled

    def enable_shared_context(self) -> None:
        """Enable cross-session context sharing"""
        from session_coordinator import SessionCoordinator
        self.coordinator = SessionCoordinator(self.session_id)
        self.coordinator.start()

    def set_shared(self, key: str, value: Any) -> None:
        """Set value in shared context (propagates to all sessions)"""
        if self.coordinator:
            self.coordinator.update_shared(key, value)
        else:
            # Fallback to local-only
            self.set(f"shared:{key}", value, StateScope.SESSION)
```

### 5.2 agent_sync.py Enhancement

Extend agent_sync.py to include context synchronization:

```python
# Add to agent_sync_state.json
{
  "agents": [...],
  "locks": [...],
  "shared_context_version": 15  # NEW: Track context version for fast change detection
}
```

---

## 6. Performance Considerations

### 6.1 Latency Targets

- **Context update propagation**: <500ms
- **Conflict detection**: <100ms
- **Polling interval**: 1s (configurable)

### 6.2 Optimization Strategies

1. **Version-based change detection**: Only send diffs, not full context
2. **Event batching**: Group multiple updates in single poll
3. **Local caching**: Cache shared context locally, poll for changes
4. **Atomic file operations**: Use temp file + rename for consistency

---

## 7. Testing Strategy

### 7.1 Unit Tests (test_shared_context_manager.py)

- Context CRUD operations
- Event logging
- Conflict detection
- Multi-session subscription

### 7.2 Integration Tests (test_session_coordinator.py)

- 2-session coordination
- 4-session coordination (target)
- Concurrent updates
- Automatic conflict resolution
- Session crash recovery

### 7.3 Performance Tests

- Latency measurement (update → receive)
- Throughput (events/second)
- Stress test (10+ concurrent sessions)

---

## 8. Success Criteria

- [ ] Context sync latency <1 second (average <500ms)
- [ ] 100% automatic conflict resolution (no manual intervention)
- [ ] Supports 4+ concurrent sessions
- [ ] Test coverage ≥85%
- [ ] No data loss on session crash
- [ ] Event log provides complete audit trail

---

## 9. Implementation Plan

**Phase 2.1** (3 hours):
- Implement `shared_context_manager.py`
- Create storage structure (RUNS/shared_context/)
- Write unit tests

**Phase 2.2** (4 hours):
- Implement `session_coordinator.py`
- Add sync thread + polling
- Integrate with session_manager.py

**Phase 2.3** (2 hours):
- Write integration tests (2-4 sessions)
- Test conflict resolution scenarios

**Phase 2.4** (1 hour):
- Performance tuning
- Documentation
- Commit and evidence collection

**Total**: 10 hours (matches YAML estimate)

---

## 10. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| File lock contention | Medium | Low | Use fine-grained locks per context key |
| Event log size growth | Low | Medium | Implement log rotation (keep last 1000 events) |
| Sync latency >1s | Low | Medium | Optimize polling, use file watchers if needed |
| Context corruption | Low | High | Atomic writes, backup before update |

---

## 11. Next Steps

1. Get approval for design
2. Create YAML task file (PHASE2-CROSS-SESSION-CONTEXT.yaml)
3. Implement Phase 2.1 (shared_context_manager.py)
4. Test and iterate

---

**Decision**: PENDING APPROVAL
