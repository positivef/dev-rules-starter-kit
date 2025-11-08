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
