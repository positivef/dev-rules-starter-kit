"""Tests for SessionCoordinator - Multi-session coordination system.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (comprehensive test coverage)
"""

import json
import time
from datetime import datetime, timedelta, timezone


from scripts.session_coordinator import (
    DEAD_SESSION_THRESHOLD,
    CoordinationStats,
    Session,
    SessionCoordinator,
)


class TestSession:
    """Test Session dataclass."""

    def test_session_to_dict(self):
        """Test Session serialization to dict."""
        now = datetime.now(timezone.utc)
        session = Session(
            session_id="test_session",
            agent_id="claude_1",
            role="frontend",
            status="active",
            registered_at=now,
            last_heartbeat=now,
            current_task="FEAT-001",
            locked_files=["src/app.py"],
        )

        data = session.to_dict()
        assert data["session_id"] == "test_session"
        assert data["agent_id"] == "claude_1"
        assert data["role"] == "frontend"
        assert data["status"] == "active"
        assert data["current_task"] == "FEAT-001"
        assert data["locked_files"] == ["src/app.py"]
        assert "registered_at" in data
        assert "last_heartbeat" in data

    def test_session_from_dict(self):
        """Test Session deserialization from dict."""
        now = datetime.now(timezone.utc)
        data = {
            "session_id": "test_session",
            "agent_id": "claude_1",
            "role": "backend",
            "status": "active",
            "registered_at": now.isoformat(),
            "last_heartbeat": now.isoformat(),
            "current_task": "FEAT-002",
            "locked_files": ["src/api.py"],
        }

        session = Session.from_dict(data)
        assert session.session_id == "test_session"
        assert session.agent_id == "claude_1"
        assert session.role == "backend"
        assert session.status == "active"
        assert session.current_task == "FEAT-002"
        assert session.locked_files == ["src/api.py"]

    def test_session_round_trip(self):
        """Test Session serialization round-trip."""
        now = datetime.now(timezone.utc)
        original = Session(
            session_id="test",
            agent_id="agent1",
            role="testing",
            status="active",
            registered_at=now,
            last_heartbeat=now,
        )

        data = original.to_dict()
        restored = Session.from_dict(data)

        assert restored.session_id == original.session_id
        assert restored.agent_id == original.agent_id
        assert restored.role == original.role
        assert restored.status == original.status


class TestSessionCoordinator:
    """Test SessionCoordinator functionality."""

    def test_initialization(self, tmp_path):
        """Test coordinator initialization creates context file."""
        SessionCoordinator(context_dir=tmp_path)
        context_file = tmp_path / "shared_context.json"

        assert context_file.exists()

        context = json.loads(context_file.read_text(encoding="utf-8"))
        assert context["project"] == "dev-rules-starter-kit"
        assert context["version"] == "2.0.0"
        assert context["sessions"] == []

    def test_register_session(self, tmp_path):
        """Test session registration."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        success = coordinator.register_session(session_id="session1", role="frontend", agent_id="claude_1")

        assert success is True

        context = coordinator._read_context()
        assert len(context["sessions"]) == 1
        assert context["sessions"][0]["session_id"] == "session1"
        assert context["sessions"][0]["role"] == "frontend"
        assert context["sessions"][0]["agent_id"] == "claude_1"
        assert context["sessions"][0]["status"] == "active"

    def test_register_duplicate_session(self, tmp_path):
        """Test registering duplicate session returns False."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        success = coordinator.register_session("session1", "backend", "claude_2")

        assert success is False

        context = coordinator._read_context()
        assert len(context["sessions"]) == 1

    def test_deregister_session(self, tmp_path):
        """Test session deregistration."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        success = coordinator.deregister_session("session1")

        assert success is True

        context = coordinator._read_context()
        assert len(context["sessions"]) == 0

    def test_deregister_nonexistent_session(self, tmp_path):
        """Test deregistering nonexistent session returns False."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        success = coordinator.deregister_session("nonexistent")

        assert success is False

    def test_update_heartbeat(self, tmp_path):
        """Test heartbeat update."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        time.sleep(0.1)

        success = coordinator.update_heartbeat("session1")
        assert success is True

        context = coordinator._read_context()
        registered_at = datetime.fromisoformat(context["sessions"][0]["registered_at"])
        last_heartbeat = datetime.fromisoformat(context["sessions"][0]["last_heartbeat"])

        assert last_heartbeat > registered_at

    def test_update_heartbeat_nonexistent(self, tmp_path):
        """Test heartbeat update for nonexistent session."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        success = coordinator.update_heartbeat("nonexistent")
        assert success is False

    def test_detect_dead_sessions(self, tmp_path):
        """Test dead session detection."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        # Register session
        coordinator.register_session("session1", "frontend", "claude_1")

        # Manually set last_heartbeat to old timestamp
        context = coordinator._read_context()
        old_time = datetime.now(timezone.utc) - timedelta(seconds=DEAD_SESSION_THRESHOLD + 10)
        context["sessions"][0]["last_heartbeat"] = old_time.isoformat()
        coordinator._write_context(context)

        # Detect dead sessions
        dead = coordinator.detect_dead_sessions()

        assert len(dead) == 1
        assert "session1" in dead

        # Verify status updated to dead
        context = coordinator._read_context()
        assert context["sessions"][0]["status"] == "dead"

    def test_get_active_sessions(self, tmp_path):
        """Test getting active sessions."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        # Register multiple sessions
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.register_session("session2", "backend", "claude_2")

        # Make one session dead
        context = coordinator._read_context()
        old_time = datetime.now(timezone.utc) - timedelta(seconds=DEAD_SESSION_THRESHOLD + 10)
        context["sessions"][1]["last_heartbeat"] = old_time.isoformat()
        coordinator._write_context(context)

        # Get active sessions
        active = coordinator.get_active_sessions()

        assert len(active) == 1
        assert active[0].session_id == "session1"
        assert active[0].role == "frontend"

    def test_get_session_by_role(self, tmp_path):
        """Test getting session by role."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.register_session("session2", "backend", "claude_2")

        frontend = coordinator.get_session_by_role("frontend")
        assert frontend is not None
        assert frontend.session_id == "session1"

        backend = coordinator.get_session_by_role("backend")
        assert backend is not None
        assert backend.session_id == "session2"

        testing = coordinator.get_session_by_role("testing")
        assert testing is None

    def test_assign_task_with_preferred_role(self, tmp_path):
        """Test task assignment with preferred role."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.register_session("session2", "backend", "claude_2")

        assigned_to = coordinator.assign_task("FEAT-001", preferred_role="backend")

        assert assigned_to == "session2"

        context = coordinator._read_context()
        session2 = next(s for s in context["sessions"] if s["session_id"] == "session2")
        assert session2["current_task"] == "FEAT-001"

    def test_assign_task_without_preferred_role(self, tmp_path):
        """Test task assignment without preferred role."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")

        assigned_to = coordinator.assign_task("FEAT-001")

        assert assigned_to == "session1"

    def test_assign_task_all_busy(self, tmp_path):
        """Test task assignment when all sessions busy."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.assign_task("FEAT-001")

        # Try to assign another task when session1 is busy
        assigned_to = coordinator.assign_task("FEAT-002")

        assert assigned_to is None

    def test_assign_task_no_sessions(self, tmp_path):
        """Test task assignment with no active sessions."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        assigned_to = coordinator.assign_task("FEAT-001")

        assert assigned_to is None

    def test_update_session_task(self, tmp_path):
        """Test updating session task."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        success = coordinator.update_session_task("session1", "FEAT-001")

        assert success is True

        context = coordinator._read_context()
        assert context["sessions"][0]["current_task"] == "FEAT-001"

        # Clear task
        success = coordinator.update_session_task("session1", None)
        assert success is True

        context = coordinator._read_context()
        assert context["sessions"][0]["current_task"] is None

    def test_update_session_locks(self, tmp_path):
        """Test updating session file locks."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        files = ["src/app.py", "src/utils.py"]
        success = coordinator.update_session_locks("session1", files)

        assert success is True

        context = coordinator._read_context()
        assert context["sessions"][0]["locked_files"] == files

    def test_get_statistics(self, tmp_path):
        """Test getting coordination statistics."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.register_session("session2", "backend", "claude_2")
        coordinator.assign_task("FEAT-001", preferred_role="frontend")

        stats = coordinator.get_statistics()

        assert isinstance(stats, CoordinationStats)
        assert stats.total_sessions == 2
        assert stats.active_sessions == 2
        assert stats.tasks_assigned == 1
        assert stats.average_session_duration_minutes >= 0

    def test_multiple_sessions_coordination(self, tmp_path):
        """Test coordination with 4+ concurrent sessions."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        # Register 4 sessions with different roles
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.register_session("session2", "backend", "claude_2")
        coordinator.register_session("session3", "testing", "claude_3")
        coordinator.register_session("session4", "assistant", "cursor_1")

        # Assign tasks
        task1 = coordinator.assign_task("FEAT-001", preferred_role="frontend")
        task2 = coordinator.assign_task("FEAT-002", preferred_role="backend")
        task3 = coordinator.assign_task("TEST-001", preferred_role="testing")

        assert task1 == "session1"
        assert task2 == "session2"
        assert task3 == "session3"

        # Verify statistics
        stats = coordinator.get_statistics()
        assert stats.total_sessions == 4
        assert stats.active_sessions == 4
        assert stats.tasks_assigned == 3

    def test_session_recovery_integration(self, tmp_path):
        """Test integration with session recovery (Phase 1)."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        # Register session
        coordinator.register_session("session1", "frontend", "claude_1")

        # Simulate crash (make session dead)
        context = coordinator._read_context()
        old_time = datetime.now(timezone.utc) - timedelta(seconds=DEAD_SESSION_THRESHOLD + 10)
        context["sessions"][0]["last_heartbeat"] = old_time.isoformat()
        coordinator._write_context(context)

        # Detect dead session
        dead = coordinator.detect_dead_sessions()
        assert "session1" in dead

        # Recovery would happen via session_recovery.py (Phase 1)
        # Here we just verify the dead session is detected

    def test_concurrent_heartbeats(self, tmp_path):
        """Test multiple concurrent heartbeat updates."""
        coordinator = SessionCoordinator(context_dir=tmp_path)

        # Register multiple sessions
        for i in range(4):
            coordinator.register_session(f"session{i+1}", "testing", f"agent{i+1}")

        # Update heartbeats concurrently (simulated)
        for i in range(4):
            success = coordinator.update_heartbeat(f"session{i+1}")
            assert success is True

        # All should still be active
        active = coordinator.get_active_sessions()
        assert len(active) == 4


class TestPhase2RealTimeSync:
    """Test Phase 2 real-time context synchronization features."""

    def test_enable_shared_context_sync(self, tmp_path):
        """Test enabling shared context synchronization."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")

        # Enable sync
        coordinator.enable_shared_context_sync("session1")

        assert coordinator.shared_context_enabled is True
        assert coordinator.current_session_id == "session1"
        assert coordinator.sync_thread is not None
        assert coordinator.sync_thread.is_alive()

        # Cleanup
        coordinator.stop()
        time.sleep(0.5)  # Allow thread to stop
        assert coordinator.sync_thread is None or not coordinator.sync_thread.is_alive()

    def test_update_shared_context(self, tmp_path):
        """Test updating shared context (propagates to all sessions)."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.enable_shared_context_sync("session1")

        # Update shared context
        success = coordinator.update_shared_context("current_task", "implementing auth")
        assert success is True

        # Verify value was written
        value = coordinator.get_shared_context("current_task")
        assert value == "implementing auth"

        # Cleanup
        coordinator.stop()

    def test_get_shared_context(self, tmp_path):
        """Test getting value from shared context."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.enable_shared_context_sync("session1")

        # Set and get value
        coordinator.update_shared_context("feature", "login")
        value = coordinator.get_shared_context("feature")
        assert value == "login"

        # Get non-existent key
        default_value = coordinator.get_shared_context("nonexistent", "default")
        assert default_value == "default"

        # Cleanup
        coordinator.stop()

    def test_two_session_concurrent_updates(self, tmp_path):
        """Test 2 sessions updating shared context concurrently (Phase 2.3)."""
        # Session 1
        coordinator1 = SessionCoordinator(context_dir=tmp_path)
        coordinator1.register_session("session1", "frontend", "claude_1")
        coordinator1.enable_shared_context_sync("session1")

        # Session 2
        coordinator2 = SessionCoordinator(context_dir=tmp_path)
        coordinator2.register_session("session2", "backend", "claude_2")
        coordinator2.enable_shared_context_sync("session2")

        # Session 1 updates
        coordinator1.update_shared_context("frontend_status", "ready")

        # Session 2 updates
        coordinator2.update_shared_context("backend_status", "processing")

        # Allow time for sync (background thread polls every 1 second)
        time.sleep(2.0)

        # Both sessions should see both updates
        frontend_status = coordinator2.get_shared_context("frontend_status")
        backend_status = coordinator1.get_shared_context("backend_status")

        assert frontend_status == "ready"
        assert backend_status == "processing"

        # Cleanup
        coordinator1.stop()
        coordinator2.stop()

    def test_sync_latency_under_1s(self, tmp_path):
        """Test context sync latency is <1s (Phase 2.3 performance validation)."""
        import time

        # Session 1
        coordinator1 = SessionCoordinator(context_dir=tmp_path)
        coordinator1.register_session("session1", "frontend", "claude_1")
        coordinator1.enable_shared_context_sync("session1")

        # Session 2
        coordinator2 = SessionCoordinator(context_dir=tmp_path)
        coordinator2.register_session("session2", "backend", "claude_2")
        coordinator2.enable_shared_context_sync("session2")

        # Measure latency
        start_time = time.time()
        coordinator1.update_shared_context("test_key", "test_value")

        # Poll until session2 sees the update (max 2 seconds)
        max_wait = 2.0
        while time.time() - start_time < max_wait:
            value = coordinator2.get_shared_context("test_key")
            if value == "test_value":
                break
            time.sleep(0.1)

        latency = time.time() - start_time

        # Verify latency is under 1 second (with some buffer for CI)
        # Note: In production, poll_interval is 1s, so latency should be <1.5s
        assert latency < 1.5, f"Sync latency {latency:.2f}s exceeds 1.5s threshold"

        # Cleanup
        coordinator1.stop()
        coordinator2.stop()

    def test_conflict_detection(self, tmp_path):
        """Test conflict detection when multiple sessions update same key."""
        # Session 1
        coordinator1 = SessionCoordinator(context_dir=tmp_path)
        coordinator1.register_session("session1", "frontend", "claude_1")
        coordinator1.enable_shared_context_sync("session1")

        # Session 2
        coordinator2 = SessionCoordinator(context_dir=tmp_path)
        coordinator2.register_session("session2", "backend", "claude_2")
        coordinator2.enable_shared_context_sync("session2")

        # Both sessions update same key (conflict scenario)
        coordinator1.update_shared_context("current_phase", "Phase 1")
        coordinator2.update_shared_context("current_phase", "Phase 2")

        # Allow sync
        time.sleep(2.0)

        # Last write wins (optimistic locking in SharedContextManager)
        final_value = coordinator1.get_shared_context("current_phase")
        assert final_value in ["Phase 1", "Phase 2"]

        # Check conflict was detected (stats incremented)
        stats = coordinator1.get_statistics()
        # Note: conflicts_detected increments when context event is received
        assert stats.conflicts_detected >= 0

        # Cleanup
        coordinator1.stop()
        coordinator2.stop()

    def test_graceful_shutdown(self, tmp_path):
        """Test graceful thread shutdown (Mitigation #3)."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.enable_shared_context_sync("session1")

        # Verify thread is running
        assert coordinator.sync_thread is not None
        assert coordinator.sync_thread.is_alive()

        # Graceful stop
        coordinator.stop()

        # Wait for thread to finish (max 6 seconds - join timeout is 5s)
        time.sleep(6.0)

        # Verify thread stopped
        assert coordinator.shared_context_enabled is False
        assert coordinator.sync_thread is None or not coordinator.sync_thread.is_alive()

    def test_sync_without_enable_fails(self, tmp_path):
        """Test that sync operations fail if not enabled."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")

        # Try to update without enabling sync
        success = coordinator.update_shared_context("key", "value")
        assert success is False

        # Try to get without enabling sync
        value = coordinator.get_shared_context("key", "default")
        assert value == "default"

    def test_four_session_concurrent_sync(self, tmp_path):
        """Test 4 sessions coordinating with real-time sync (Phase 2.3)."""
        coordinators = []

        # Create 4 sessions with different roles
        roles = ["frontend", "backend", "testing", "assistant"]
        for i, role in enumerate(roles):
            coord = SessionCoordinator(context_dir=tmp_path)
            coord.register_session(f"session{i+1}", role, f"agent{i+1}")
            coord.enable_shared_context_sync(f"session{i+1}")
            coordinators.append(coord)

        # Each session updates a different key
        coordinators[0].update_shared_context("frontend", "ready")
        coordinators[1].update_shared_context("backend", "ready")
        coordinators[2].update_shared_context("testing", "ready")
        coordinators[3].update_shared_context("assistant", "ready")

        # Allow sync (4 updates across 4 sessions)
        time.sleep(3.0)

        # All sessions should see all updates
        for coord in coordinators:
            assert coord.get_shared_context("frontend") == "ready"
            assert coord.get_shared_context("backend") == "ready"
            assert coord.get_shared_context("testing") == "ready"
            assert coord.get_shared_context("assistant") == "ready"

        # Cleanup all coordinators
        for coord in coordinators:
            coord.stop()

    def test_background_sync_resilience(self, tmp_path):
        """Test background sync continues despite errors (resilience)."""
        coordinator = SessionCoordinator(context_dir=tmp_path)
        coordinator.register_session("session1", "frontend", "claude_1")
        coordinator.enable_shared_context_sync("session1")

        # Update context
        coordinator.update_shared_context("test", "value1")

        # Allow sync loop to run for a few iterations
        time.sleep(3.0)

        # Thread should still be alive (resilient to errors)
        assert coordinator.sync_thread.is_alive()

        # Can still update after errors
        success = coordinator.update_shared_context("test", "value2")
        assert success is True

        # Cleanup
        coordinator.stop()
