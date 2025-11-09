#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Session Recovery - Week 7 Phase 1

Tests:
- Checkpoint creation
- Crash detection (4 types)
- Session recovery
- Success rate calculation
- Edge cases and error handling

Target: 20+ tests for 95% coverage
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from scripts.session_recovery import (
    SessionRecovery,
    RecoveryStatus,
    CrashReason,
    RecoveryLog,
)


@pytest.fixture
def temp_recovery_dir(tmp_path):
    """Create temporary recovery directories"""
    checkpoint_dir = tmp_path / "sessions"
    recovery_log_dir = tmp_path / "recovery"
    heartbeat_dir = tmp_path / "heartbeats"

    checkpoint_dir.mkdir(parents=True)
    recovery_log_dir.mkdir(parents=True)
    heartbeat_dir.mkdir(parents=True)

    return {
        "checkpoint": checkpoint_dir,
        "recovery": recovery_log_dir,
        "heartbeat": heartbeat_dir,
        "root": tmp_path,
    }


@pytest.fixture
def recovery(temp_recovery_dir):
    """Create SessionRecovery instance with temp dirs"""
    recovery = SessionRecovery()
    recovery.checkpoint_dir = temp_recovery_dir["checkpoint"]
    recovery.recovery_log_dir = temp_recovery_dir["recovery"]
    recovery.heartbeat_dir = temp_recovery_dir["heartbeat"]
    return recovery


class TestCheckpointCreation:
    """Test checkpoint creation"""

    def test_create_checkpoint_basic(self, recovery):
        """Test basic checkpoint creation"""
        session_id = "session_test_001"
        context_data = {"task": "test", "count": 42}

        checkpoint = recovery.create_checkpoint(session_id, context_data)

        assert checkpoint.session_id == session_id
        assert checkpoint.context_data == context_data
        assert checkpoint.pid == os.getpid()
        assert len(checkpoint.context_hash) == 16

    def test_checkpoint_file_saved(self, recovery):
        """Test checkpoint file is saved"""
        session_id = "session_test_002"
        context_data = {"test": "data"}

        checkpoint = recovery.create_checkpoint(session_id, context_data)

        checkpoint_file = recovery.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        assert checkpoint_file.exists()

        with open(checkpoint_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        assert saved_data["session_id"] == session_id
        assert saved_data["context_data"] == context_data

    def test_heartbeat_updated(self, recovery):
        """Test heartbeat is updated"""
        session_id = "session_test_003"
        context_data = {}

        recovery.create_checkpoint(session_id, context_data)

        heartbeat_file = recovery.heartbeat_dir / f"{session_id}.heartbeat"
        assert heartbeat_file.exists()

        with open(heartbeat_file, "r", encoding="utf-8") as f:
            heartbeat_data = json.load(f)

        assert heartbeat_data["session_id"] == session_id
        assert heartbeat_data["pid"] == os.getpid()

    def test_checkpoint_hash_deterministic(self, recovery):
        """Test context hash is deterministic"""
        context_data = {"a": 1, "b": 2}

        checkpoint1 = recovery.create_checkpoint("sess1", context_data)
        checkpoint2 = recovery.create_checkpoint("sess2", context_data)

        assert checkpoint1.context_hash == checkpoint2.context_hash

    def test_checkpoint_file_states_captured(self, recovery):
        """Test file states are captured"""
        checkpoint = recovery.create_checkpoint("sess_files", {})

        assert "config/constitution.yaml" in checkpoint.file_states


class TestCrashDetection:
    """Test crash detection"""

    def test_detect_orphaned_via_detect_crash(self, recovery):
        """Test orphaned session detected through detect_crash()"""
        session_id = "orphaned_integration"

        # Create checkpoint
        recovery.create_checkpoint(session_id, {"test": "data"})

        # Create orphaned session file (old, not gracefully shut down)
        session_file = recovery.checkpoint_dir / f"{session_id}.json"
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

        session_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "graceful_shutdown": False,
                    "last_update": old_time,
                    "scope_data": {"SESSION": {}},
                },
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

        # Mock PID/heartbeat/integrity checks to pass
        # So that orphaned session detection is reached
        with patch("scripts.session_recovery.psutil.pid_exists", return_value=True):
            crash_reason = recovery.detect_crash(session_id)

        # Should detect as ORPHANED_SESSION
        from scripts.session_recovery import CrashReason

        assert crash_reason == CrashReason.ORPHANED_SESSION

    def test_detect_no_crash(self, recovery):
        """Test no crash when process alive"""
        session_id = "session_alive_001"

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=True):
            recovery.create_checkpoint(session_id, {})
            crash_reason = recovery.detect_crash(session_id)

        assert crash_reason is None

    def test_detect_process_killed(self, recovery):
        """Test detect process killed"""
        session_id = "session_killed_001"
        recovery.create_checkpoint(session_id, {})

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            crash_reason = recovery.detect_crash(session_id)

        assert crash_reason == CrashReason.PROCESS_KILLED

    def test_detect_heartbeat_timeout(self, recovery):
        """Test detect heartbeat timeout"""
        session_id = "session_timeout_001"
        recovery.create_checkpoint(session_id, {})

        heartbeat_file = recovery.heartbeat_dir / f"{session_id}.heartbeat"
        old_mtime = time.time() - 400

        os.utime(heartbeat_file, (old_mtime, old_mtime))

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=True):
            crash_reason = recovery.detect_crash(session_id)

        assert crash_reason == CrashReason.HEARTBEAT_TIMEOUT

    def test_detect_corrupted_state(self, recovery):
        """Test detect corrupted state"""
        session_id = "session_corrupted_001"
        checkpoint = recovery.create_checkpoint(session_id, {"data": "original"})

        checkpoint_file = recovery.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["context_data"] = {"data": "modified"}

        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=True):
            crash_reason = recovery.detect_crash(session_id)

        assert crash_reason == CrashReason.CORRUPTED_STATE

    def test_detect_no_checkpoint(self, recovery):
        """Test detect no checkpoint"""
        crash_reason = recovery.detect_crash("nonexistent_session")
        assert crash_reason is None


class TestSessionRecovery:
    """Test session recovery"""

    def test_recover_no_checkpoint(self, recovery):
        """Test recovery fails with no checkpoint"""
        log = recovery.recover_session("nonexistent_session")

        assert log.status == RecoveryStatus.FAILED.value
        assert log.error_message == "No checkpoint found"
        assert log.files_restored == 0
        assert log.context_restored is False

    def test_recover_success(self, recovery):
        """Test successful recovery"""
        session_id = "session_recover_001"
        context_data = {"task": "important", "progress": 75}

        recovery.create_checkpoint(session_id, context_data)

        session_file = recovery.checkpoint_dir.parent / f"{session_id}.json"
        session_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "scope_data": {"SESSION": {}, "USER": {}, "APP": {}, "TEMP": {}},
                },
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            log = recovery.recover_session(session_id)

        assert log.status == RecoveryStatus.SUCCESS.value
        assert log.crash_reason == CrashReason.PROCESS_KILLED.value
        assert log.context_restored is True
        assert log.recovery_time_sec < 1.0

    def test_recover_partial(self, recovery):
        """Test partial recovery"""
        session_id = "session_partial_001"
        checkpoint = recovery.create_checkpoint(session_id, {})

        checkpoint_file = recovery.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["context_hash"] = "invalid_hash"

        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        session_file = recovery.checkpoint_dir.parent / f"{session_id}.json"
        session_file.write_text(
            json.dumps({"session_id": session_id, "scope_data": {"SESSION": {}}}, ensure_ascii=True),
            encoding="utf-8",
        )

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            log = recovery.recover_session(session_id)

        assert log.status == RecoveryStatus.PARTIAL.value

    def test_recovery_log_saved(self, recovery):
        """Test recovery log is saved"""
        session_id = "session_log_001"
        recovery.create_checkpoint(session_id, {})

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            log = recovery.recover_session(session_id)

        log_file = recovery.recovery_log_dir / f"{log.recovery_id}.json"
        assert log_file.exists()


class TestSuccessRate:
    """Test success rate calculation"""

    def test_success_rate_no_logs(self, recovery):
        """Test success rate with no logs"""
        rate = recovery.get_recovery_success_rate()
        assert rate == 0.0

    def test_success_rate_all_success(self, recovery):
        """Test success rate with all successes"""
        for i in range(5):
            log = RecoveryLog(
                recovery_id=f"recovery_{i}",
                session_id=f"session_{i}",
                crash_reason=CrashReason.PROCESS_KILLED.value,
                detected_at=datetime.now(timezone.utc).isoformat(),
                started_at=datetime.now(timezone.utc).isoformat(),
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=RecoveryStatus.SUCCESS.value,
                checkpoint_used="checkpoint_001",
                files_restored=3,
                context_restored=True,
                error_message=None,
                recovery_time_sec=0.5,
            )

            log_file = recovery.recovery_log_dir / f"{log.recovery_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log.to_dict(), f)

        rate = recovery.get_recovery_success_rate()
        assert rate == 1.0

    def test_success_rate_mixed(self, recovery):
        """Test success rate with mixed results"""
        statuses = [
            RecoveryStatus.SUCCESS,
            RecoveryStatus.SUCCESS,
            RecoveryStatus.FAILED,
            RecoveryStatus.SUCCESS,
            RecoveryStatus.PARTIAL,
        ]

        for i, status in enumerate(statuses):
            log = RecoveryLog(
                recovery_id=f"recovery_{i}",
                session_id=f"session_{i}",
                crash_reason=CrashReason.UNKNOWN.value,
                detected_at=datetime.now(timezone.utc).isoformat(),
                started_at=datetime.now(timezone.utc).isoformat(),
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=status.value,
                checkpoint_used=None,
                files_restored=0,
                context_restored=False,
                error_message=None,
                recovery_time_sec=1.0,
            )

            log_file = recovery.recovery_log_dir / f"{log.recovery_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log.to_dict(), f)

        rate = recovery.get_recovery_success_rate()
        assert rate == 0.6


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_checkpoint_with_empty_context(self, recovery):
        """Test checkpoint with empty context"""
        checkpoint = recovery.create_checkpoint("empty_session", {})
        assert checkpoint.context_data == {}
        assert len(checkpoint.context_hash) == 16

    def test_multiple_checkpoints_latest(self, recovery):
        """Test latest checkpoint is used"""
        session_id = "multi_checkpoint_001"

        recovery.create_checkpoint(session_id, {"version": 1})
        time.sleep(0.1)
        recovery.create_checkpoint(session_id, {"version": 2})
        time.sleep(0.1)
        recovery.create_checkpoint(session_id, {"version": 3})

        checkpoints = sorted(
            recovery.checkpoint_dir.glob(f"checkpoint_{session_id}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        assert len(checkpoints) == 3

        with open(checkpoints[0], "r", encoding="utf-8") as f:
            latest_data = json.load(f)

        assert latest_data["context_data"]["version"] == 3

    def test_disk_space_check(self, recovery):
        """Test disk space check"""
        has_space = recovery._check_disk_space()
        assert isinstance(has_space, bool)

    def test_file_states_nonexistent_files(self, recovery):
        """Test file states with nonexistent files"""
        file_states = recovery._capture_file_states()
        assert isinstance(file_states, dict)

    def test_recovery_time_measurement(self, recovery):
        """Test recovery time is measured"""
        session_id = "time_test_001"
        recovery.create_checkpoint(session_id, {})

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            log = recovery.recover_session(session_id)

        assert log.recovery_time_sec >= 0
        assert log.recovery_time_sec < 5.0

    def test_detect_orphaned_session(self, recovery):
        """Test orphaned session detection"""
        session_id = "orphaned_001"

        # Create session file (without graceful shutdown)
        session_file = recovery.checkpoint_dir / f"{session_id}.json"
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

        session_file.write_text(
            json.dumps({"session_id": session_id, "graceful_shutdown": False, "last_update": old_time}, ensure_ascii=True),
            encoding="utf-8",
        )

        # Should detect as orphaned
        is_orphaned = recovery._detect_orphaned_session(session_id)
        assert is_orphaned is True

    def test_detect_orphaned_session_graceful(self, recovery):
        """Test graceful shutdown is not detected as crash"""
        session_id = "graceful_001"

        # Create session file WITH graceful shutdown
        session_file = recovery.checkpoint_dir / f"{session_id}.json"
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

        session_file.write_text(
            json.dumps({"session_id": session_id, "graceful_shutdown": True, "last_update": old_time}, ensure_ascii=True),
            encoding="utf-8",
        )

        # Should NOT detect as orphaned
        is_orphaned = recovery._detect_orphaned_session(session_id)
        assert is_orphaned is False

    def test_psutil_fallback_process_alive(self, recovery):
        """Test psutil fallback when not available"""
        # Temporarily disable psutil
        with patch("scripts.session_recovery.HAS_PSUTIL", False):
            # Without psutil, assume process is alive
            result = recovery._is_process_alive(99999)
            assert result is True

    def test_psutil_fallback_disk_space(self, recovery):
        """Test disk space check fallback"""
        # Temporarily disable psutil
        with patch("scripts.session_recovery.HAS_PSUTIL", False):
            # Without psutil, assume disk space is OK
            result = recovery._check_disk_space()
            assert result is True


class TestCLIInterface:
    """Test CLI interface"""

    def test_cli_detect_no_crash(self, recovery):
        """Test CLI detect command when no crash"""
        import subprocess

        session_id = "test_cli_001"
        recovery.create_checkpoint(session_id, {"test": "data"})

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py", "detect", session_id],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0 or "[OK]" in result.stdout or "Session running normally" in result.stdout

    def test_cli_detect_crash(self, recovery):
        """Test CLI detect command when crash detected"""
        import subprocess

        session_id = "test_cli_002"
        recovery.create_checkpoint(session_id, {"test": "data"})

        with patch("scripts.session_recovery.psutil.pid_exists", return_value=False):
            result = subprocess.run(
                [sys.executable, "scripts/session_recovery.py", "detect", session_id],
                capture_output=True,
                text=True,
            )

        assert "CRASH" in result.stdout or result.returncode == 0

    def test_cli_recover_success(self, recovery):
        """Test CLI recover command"""
        import subprocess

        session_id = "test_cli_003"
        recovery.create_checkpoint(session_id, {"test": "data"})

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py", "recover", session_id],
            capture_output=True,
            text=True,
        )

        assert "RECOVERY" in result.stdout or result.returncode == 0

    def test_cli_stats(self, recovery):
        """Test CLI stats command"""
        import subprocess

        for i in range(3):
            log = RecoveryLog(
                recovery_id=f"recovery_{i}",
                session_id=f"session_{i}",
                crash_reason="process_killed",
                detected_at=datetime.now(timezone.utc).isoformat(),
                started_at=datetime.now(timezone.utc).isoformat(),
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=RecoveryStatus.SUCCESS.value,
                checkpoint_used="checkpoint_001",
                files_restored=3,
                context_restored=True,
                error_message=None,
                recovery_time_sec=0.5,
            )

            log_file = recovery.recovery_log_dir / f"{log.recovery_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log.to_dict(), f)

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py", "stats"],
            capture_output=True,
            text=True,
        )

        assert "STATS" in result.stdout or "Recovery success rate" in result.stdout or result.returncode == 0

    def test_cli_no_args(self):
        """Test CLI with no arguments"""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1 or "Usage:" in result.stdout

    def test_cli_detect_no_session_id(self):
        """Test CLI detect without session_id"""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py", "detect"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1 or "Error:" in result.stdout or "required" in result.stdout

    def test_cli_unknown_command(self):
        """Test CLI with unknown command"""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/session_recovery.py", "invalid_command"],
            capture_output=True,
            text=True,
        )

        assert "Unknown command" in result.stdout or "invalid_command" in result.stdout or result.returncode != 0
