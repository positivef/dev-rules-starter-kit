"""Unit tests for Session Recovery System.

Tests for automatic crash detection and recovery:
- Crash detection via session state
- Context integrity validation
- Checkpoint creation and cleanup
- Session recovery workflow
- Recovery statistics calculation
- CLI interface

Constitutional Compliance:
- P8: Test-First Development (testing the recovery system)
- P2: Evidence-Based (verify recovery works)
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session_recovery import CrashInfo, RecoveryResult, SessionRecovery


class TestCrashInfo:
    """Tests for CrashInfo dataclass."""

    def test_crash_info_creation(self):
        """Test CrashInfo creation."""
        crash = CrashInfo(
            session_id="test_session",
            crash_time=datetime.now(),
            last_checkpoint=datetime.now() - timedelta(minutes=30),
            context_hash="abc123",
            crash_reason="Power failure",
            recovery_attempted=False,
            recovery_success=False,
        )

        assert crash.session_id == "test_session"
        assert crash.context_hash == "abc123"
        assert crash.crash_reason == "Power failure"
        assert crash.recovery_attempted is False
        assert crash.recovery_success is False


class TestRecoveryResult:
    """Tests for RecoveryResult dataclass."""

    def test_recovery_result_success(self):
        """Test RecoveryResult creation for success."""
        result = RecoveryResult(
            success=True,
            session_id="test_session",
            recovered_at=datetime.now(),
            context_valid=True,
            data_loss=False,
            recovery_time_seconds=2.5,
        )

        assert result.success is True
        assert result.context_valid is True
        assert result.data_loss is False
        assert result.recovery_time_seconds == 2.5
        assert result.error_message is None


class TestSessionRecovery:
    """Tests for SessionRecovery class."""

    def test_initialization(self, tmp_path):
        """Test SessionRecovery initialization."""
        recovery = SessionRecovery(tmp_path)

        assert recovery.project_root == tmp_path
        assert recovery.sessions_dir.exists()
        assert recovery.checkpoints_dir.exists()
        assert recovery.crashes_dir.exists()
        assert recovery.context_dir.exists()
        assert recovery.checkpoint_interval == 30
        assert recovery.max_recovery_attempts == 3

    def test_detect_crashes_no_crashes(self, tmp_path):
        """Test crash detection with no crashes."""
        recovery = SessionRecovery(tmp_path)

        # Create session with graceful shutdown
        session_file = recovery.sessions_dir / "session_test1.json"
        session_data = {
            "session_id": "test1",
            "graceful_shutdown": True,
            "last_update": datetime.now().isoformat(),
        }
        session_file.write_text(json.dumps(session_data), encoding="utf-8")

        crashes = recovery.detect_crashes()
        assert len(crashes) == 0

    def test_detect_crashes_single_crash(self, tmp_path):
        """Test crash detection with single crash."""
        recovery = SessionRecovery(tmp_path)

        # Create session without graceful shutdown, older than 1 hour
        session_file = recovery.sessions_dir / "session_test2.json"
        crash_time = datetime.now() - timedelta(hours=2)
        session_data = {
            "session_id": "test2",
            "graceful_shutdown": False,
            "last_update": crash_time.isoformat(),
            "context_hash": "hash123",
        }
        session_file.write_text(json.dumps(session_data), encoding="utf-8")

        crashes = recovery.detect_crashes()
        assert len(crashes) == 1
        assert crashes[0].session_id == "test2"
        assert crashes[0].context_hash == "hash123"

    def test_detect_crashes_multiple_crashes(self, tmp_path):
        """Test crash detection with multiple crashes."""
        recovery = SessionRecovery(tmp_path)

        # Create 3 crashed sessions
        for i in range(3):
            session_file = recovery.sessions_dir / f"session_test{i}.json"
            crash_time = datetime.now() - timedelta(hours=2 + i)
            session_data = {
                "session_id": f"test{i}",
                "graceful_shutdown": False,
                "last_update": crash_time.isoformat(),
            }
            session_file.write_text(json.dumps(session_data), encoding="utf-8")

        crashes = recovery.detect_crashes()
        assert len(crashes) == 3

    def test_detect_crashes_corrupted_file(self, tmp_path):
        """Test crash detection with corrupted session file."""
        recovery = SessionRecovery(tmp_path)

        # Create corrupted session file
        session_file = recovery.sessions_dir / "session_corrupted.json"
        session_file.write_text("not valid json", encoding="utf-8")

        # Should not crash, should skip corrupted file
        crashes = recovery.detect_crashes()
        assert len(crashes) == 0

    def test_validate_context_integrity_valid(self, tmp_path):
        """Test context integrity validation with valid hash."""
        recovery = SessionRecovery(tmp_path)

        # Create checkpoint with valid context
        context = {"key": "value", "data": [1, 2, 3]}
        recovery.create_checkpoint("test_session", context)

        # Validate should pass
        valid = recovery.validate_context_integrity("test_session")
        assert valid is True

    def test_validate_context_integrity_invalid(self, tmp_path):
        """Test context integrity validation with invalid hash."""
        recovery = SessionRecovery(tmp_path)

        # Create checkpoint
        context = {"key": "value"}
        checkpoint_file = recovery.create_checkpoint("test_session", context)

        # Manually corrupt the hash
        with open(checkpoint_file, encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        checkpoint_data["context_hash"] = "corrupted_hash"
        checkpoint_file.write_text(json.dumps(checkpoint_data), encoding="utf-8")

        # Validation should fail
        valid = recovery.validate_context_integrity("test_session")
        assert valid is False

    def test_validate_context_integrity_no_checkpoint(self, tmp_path):
        """Test context integrity validation with no checkpoint."""
        recovery = SessionRecovery(tmp_path)

        # No checkpoint exists
        valid = recovery.validate_context_integrity("nonexistent_session")
        assert valid is False

    def test_create_checkpoint(self, tmp_path):
        """Test checkpoint creation."""
        recovery = SessionRecovery(tmp_path)

        context = {"key": "value", "data": [1, 2, 3]}
        checkpoint_file = recovery.create_checkpoint("test_session", context)

        assert checkpoint_file.exists()

        # Load and verify
        with open(checkpoint_file, encoding="utf-8") as f:
            checkpoint_data = json.load(f)

        assert checkpoint_data["session_id"] == "test_session"
        assert checkpoint_data["context"] == context
        assert "context_hash" in checkpoint_data
        assert checkpoint_data["checkpoint_type"] == "automatic"

    def test_create_checkpoint_hash_correctness(self, tmp_path):
        """Test checkpoint hash calculation correctness."""
        import hashlib

        recovery = SessionRecovery(tmp_path)

        context = {"key": "value", "data": [1, 2, 3]}
        checkpoint_file = recovery.create_checkpoint("test_session", context)

        # Load checkpoint
        with open(checkpoint_file, encoding="utf-8") as f:
            checkpoint_data = json.load(f)

        # Manually calculate hash
        context_str = json.dumps(context, sort_keys=True)
        expected_hash = hashlib.sha256(context_str.encode()).hexdigest()

        assert checkpoint_data["context_hash"] == expected_hash

    def test_create_checkpoint_cleanup(self, tmp_path):
        """Test checkpoint cleanup keeps last 5 only."""
        recovery = SessionRecovery(tmp_path)

        context = {"key": "value"}

        # Create 7 checkpoints
        for i in range(7):
            recovery.create_checkpoint("test_session", context)

        # Should have only 5 checkpoints
        checkpoints = list(recovery.checkpoints_dir.glob("checkpoint_test_session_*.json"))
        assert len(checkpoints) == 5

    def test_recover_session_success(self, tmp_path):
        """Test successful session recovery."""
        recovery = SessionRecovery(tmp_path)

        # Create checkpoint
        context = {"key": "value", "data": [1, 2, 3]}
        recovery.create_checkpoint("test_session", context)

        # Recover
        result = recovery.recover_session("test_session")

        assert result.success is True
        assert result.context_valid is True
        assert result.session_id == "test_session"
        assert result.recovery_time_seconds > 0

        # Check recovery file created
        recovery_file = recovery.sessions_dir / "session_test_session_recovered.json"
        assert recovery_file.exists()

    def test_recover_session_no_checkpoint(self, tmp_path):
        """Test recovery failure with no checkpoint."""
        recovery = SessionRecovery(tmp_path)

        # No checkpoint exists
        result = recovery.recover_session("nonexistent_session")

        assert result.success is False
        assert result.context_valid is False
        assert result.data_loss is True
        assert result.error_message == "No checkpoints found"

    def test_recover_session_invalid_context(self, tmp_path):
        """Test recovery failure with invalid context."""
        recovery = SessionRecovery(tmp_path)

        # Create checkpoint
        context = {"key": "value"}
        checkpoint_file = recovery.create_checkpoint("test_session", context)

        # Corrupt the hash
        with open(checkpoint_file, encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        checkpoint_data["context_hash"] = "corrupted"
        checkpoint_file.write_text(json.dumps(checkpoint_data), encoding="utf-8")

        # Recovery should fail
        result = recovery.recover_session("test_session")

        assert result.success is False
        assert result.context_valid is False
        assert "integrity check failed" in result.error_message

    def test_recover_session_data_loss_detection(self, tmp_path):
        """Test data loss detection in recovery."""
        recovery = SessionRecovery(tmp_path)

        # Create old checkpoint (45 minutes ago, >30 min threshold)
        context = {"key": "value"}
        checkpoint_file = recovery.create_checkpoint("test_session", context)

        # Manually set checkpoint timestamp to 45 minutes ago
        with open(checkpoint_file, encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        old_time = datetime.now() - timedelta(minutes=45)
        checkpoint_data["timestamp"] = old_time.isoformat()
        checkpoint_file.write_text(json.dumps(checkpoint_data), encoding="utf-8")

        # Recover
        result = recovery.recover_session("test_session")

        assert result.success is True
        assert result.data_loss is True  # More than 30 minutes

    def test_recover_session_time_measurement(self, tmp_path):
        """Test recovery time measurement."""
        recovery = SessionRecovery(tmp_path)

        # Create checkpoint
        context = {"key": "value"}
        recovery.create_checkpoint("test_session", context)

        # Recover and check time
        result = recovery.recover_session("test_session")

        assert result.recovery_time_seconds > 0
        assert result.recovery_time_seconds < 5  # Should be fast

    def test_get_recovery_statistics_empty(self, tmp_path):
        """Test recovery statistics with no crashes."""
        recovery = SessionRecovery(tmp_path)

        stats = recovery.get_recovery_statistics()

        assert stats["total_crashes"] == 0
        assert stats["successful_recoveries"] == 0
        assert stats["recovery_rate"] == 0
        assert stats["data_loss_incidents"] == 0

    def test_get_recovery_statistics_with_crashes(self, tmp_path):
        """Test recovery statistics calculation."""
        recovery = SessionRecovery(tmp_path)

        # Create 3 crash logs
        for i in range(3):
            crash_log = recovery.crashes_dir / f"crash_test{i}_20251103_120000.json"
            log_data = {
                "session_id": f"test{i}",
                "recovery_success": i < 2,  # 2 successes, 1 failure
                "data_loss": i == 1,  # 1 with data loss
            }
            crash_log.write_text(json.dumps(log_data), encoding="utf-8")

        stats = recovery.get_recovery_statistics()

        assert stats["total_crashes"] == 3
        assert stats["successful_recoveries"] == 2
        assert abs(stats["recovery_rate"] - 66.67) < 0.1  # 2/3 * 100
        assert stats["data_loss_incidents"] == 1

    def test_auto_recover_all(self, tmp_path):
        """Test automatic recovery of all crashed sessions."""
        recovery = SessionRecovery(tmp_path)

        # Create 2 crashed sessions with checkpoints
        for i in range(2):
            session_id = f"test{i}"
            # Create checkpoint
            context = {"session": session_id}
            recovery.create_checkpoint(session_id, context)

            # Create crashed session
            session_file = recovery.sessions_dir / f"session_{session_id}.json"
            crash_time = datetime.now() - timedelta(hours=2)
            session_data = {
                "session_id": session_id,
                "graceful_shutdown": False,
                "last_update": crash_time.isoformat(),
                "recovery_attempted": False,
            }
            session_file.write_text(json.dumps(session_data), encoding="utf-8")

        # Auto-recover all
        results = recovery.auto_recover_all()

        assert len(results) == 2
        assert all(r.success for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
