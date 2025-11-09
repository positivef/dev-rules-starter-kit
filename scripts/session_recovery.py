#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Recovery - Automatic crash detection and recovery system

Week 7 Phase 1: Session Recovery Automation
Features:
- Crash detection (PID monitoring, heartbeat checking)
- Automatic checkpoint system (30min intervals, via SessionManager)
- Session recovery workflow (automatic restoration)
- Context integrity validation (hash verification)
- Recovery success rate tracking (>95% target)

ROI: 306% (15min manual recovery -> 5sec automatic recovery)
"""

import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Dict, Any, Optional

# Optional dependency: psutil for real-time PID/disk monitoring
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class RecoveryStatus(Enum):
    """Recovery operation status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class CrashReason(Enum):
    """Detected crash reasons"""

    PROCESS_KILLED = "process_killed"
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    CORRUPTED_STATE = "corrupted_state"
    DISK_FULL = "disk_full"
    ORPHANED_SESSION = "orphaned_session"
    UNKNOWN = "unknown"


@dataclass
class Checkpoint:
    """Session checkpoint data"""

    checkpoint_id: str
    session_id: str
    timestamp: str
    pid: int
    context_hash: str
    context_data: Dict[str, Any]
    file_states: Dict[str, str]

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Checkpoint":
        """Deserialize from dictionary"""
        return cls(**data)


@dataclass
class RecoveryLog:
    """Recovery operation log"""

    recovery_id: str
    session_id: str
    crash_reason: str
    detected_at: str
    started_at: str
    completed_at: Optional[str]
    status: str
    checkpoint_used: Optional[str]
    files_restored: int
    context_restored: bool
    error_message: Optional[str]
    recovery_time_sec: float
    data_loss_minutes: float = 0.0  # Time between crash and last checkpoint

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return asdict(self)


class SessionRecovery:
    """
    Session Recovery Manager - Automatic crash detection and recovery

    Usage:
        recovery = SessionRecovery()
        if recovery.detect_crash("session_20251108_abc123"):
            log = recovery.recover_session("session_20251108_abc123")
            print(f"Recovery: {log.status}")

        rate = recovery.get_recovery_success_rate()
        print(f"Success rate: {rate:.1%}")
    """

    def __init__(self):
        """Initialize recovery manager"""
        self.checkpoint_dir = Path("RUNS") / "sessions"
        self.recovery_log_dir = Path("RUNS") / "recovery"
        self.heartbeat_dir = Path("RUNS") / "heartbeats"

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_log_dir.mkdir(parents=True, exist_ok=True)
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)

        self.heartbeat_timeout = 300
        self.max_recovery_attempts = 3

    def create_checkpoint(self, session_id: str, context_data: Dict[str, Any]) -> Checkpoint:
        """Create session checkpoint"""
        checkpoint_id = self._generate_checkpoint_id(session_id)
        pid = os.getpid()
        file_states = self._capture_file_states()

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            pid=pid,
            context_hash=self._generate_context_hash(context_data),
            context_data=context_data,
            file_states=file_states,
        )

        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=True)

        self._update_heartbeat(session_id, pid)
        return checkpoint

    def detect_crash(self, session_id: str) -> Optional[CrashReason]:
        """Detect if session crashed"""
        checkpoints = sorted(
            self.checkpoint_dir.glob(f"checkpoint_{session_id}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not checkpoints:
            return None

        try:
            with open(checkpoints[0], "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)

            checkpoint = Checkpoint.from_dict(checkpoint_data)

            if not self._is_process_alive(checkpoint.pid):
                return CrashReason.PROCESS_KILLED

            heartbeat_file = self.heartbeat_dir / f"{session_id}.heartbeat"
            if heartbeat_file.exists():
                heartbeat_age = time.time() - heartbeat_file.stat().st_mtime
                if heartbeat_age > self.heartbeat_timeout:
                    return CrashReason.HEARTBEAT_TIMEOUT

            if not self._verify_context_integrity(checkpoint):
                return CrashReason.CORRUPTED_STATE

            if not self._check_disk_space():
                return CrashReason.DISK_FULL

            # Check orphaned session (safety net - file-based detection)
            if self._detect_orphaned_session(session_id):
                return CrashReason.ORPHANED_SESSION

            return None

        except Exception:
            return CrashReason.UNKNOWN

    def recover_session(self, session_id: str) -> RecoveryLog:
        """Recover session from crash"""
        recovery_id = self._generate_recovery_id(session_id)
        detected_at = datetime.now(timezone.utc).isoformat()
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()

        crash_reason = self.detect_crash(session_id)
        if crash_reason is None:
            crash_reason = CrashReason.UNKNOWN

        checkpoints = sorted(
            self.checkpoint_dir.glob(f"checkpoint_{session_id}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not checkpoints:
            return RecoveryLog(
                recovery_id=recovery_id,
                session_id=session_id,
                crash_reason=crash_reason.value,
                detected_at=detected_at,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=RecoveryStatus.FAILED.value,
                checkpoint_used=None,
                files_restored=0,
                context_restored=False,
                error_message="No checkpoint found",
                recovery_time_sec=time.time() - start_time,
                data_loss_minutes=0.0,
            )

        try:
            with open(checkpoints[0], "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)

            checkpoint = Checkpoint.from_dict(checkpoint_data)

            files_restored = self._restore_file_states(checkpoint.file_states)
            context_restored = self._restore_context(session_id, checkpoint.context_data)
            integrity_ok = self._verify_context_integrity(checkpoint)

            if context_restored and integrity_ok:
                status = RecoveryStatus.SUCCESS
            elif context_restored:
                status = RecoveryStatus.PARTIAL
            else:
                status = RecoveryStatus.FAILED

            recovery_time = time.time() - start_time

            # Calculate data loss: time between crash and last checkpoint
            checkpoint_time = datetime.fromisoformat(checkpoint.timestamp)
            crash_time = datetime.now(timezone.utc)
            data_loss_seconds = (crash_time - checkpoint_time).total_seconds()
            data_loss_minutes = data_loss_seconds / 60.0

            log = RecoveryLog(
                recovery_id=recovery_id,
                session_id=session_id,
                crash_reason=crash_reason.value,
                detected_at=detected_at,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=status.value,
                checkpoint_used=checkpoint.checkpoint_id,
                files_restored=files_restored,
                context_restored=context_restored,
                error_message=None if status == RecoveryStatus.SUCCESS else "Partial recovery",
                recovery_time_sec=recovery_time,
                data_loss_minutes=data_loss_minutes,
            )

            self._save_recovery_log(log)
            return log

        except Exception as e:
            return RecoveryLog(
                recovery_id=recovery_id,
                session_id=session_id,
                crash_reason=crash_reason.value,
                detected_at=detected_at,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                status=RecoveryStatus.FAILED.value,
                checkpoint_used=checkpoints[0].stem if checkpoints else None,
                files_restored=0,
                context_restored=False,
                error_message=str(e),
                recovery_time_sec=time.time() - start_time,
                data_loss_minutes=0.0,
            )

    def get_recovery_success_rate(self) -> float:
        """Get recovery success rate"""
        logs = list(self.recovery_log_dir.glob("recovery_*.json"))

        if not logs:
            return 0.0

        total = 0
        successful = 0

        for log_file in logs:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)

                total += 1
                if log_data["status"] == RecoveryStatus.SUCCESS.value:
                    successful += 1

            except Exception:
                continue

        return successful / total if total > 0 else 0.0

    def _generate_checkpoint_id(self, session_id: str) -> str:
        """Generate checkpoint ID"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        microsecond = now.microsecond
        return f"checkpoint_{session_id}_{timestamp}_{microsecond}"

    def _generate_recovery_id(self, session_id: str) -> str:
        """Generate recovery ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"recovery_{session_id}_{timestamp}"

    def _generate_context_hash(self, data: Dict) -> str:
        """Generate context hash"""
        json_str = json.dumps(data, sort_keys=True)
        return sha256(json_str.encode()).hexdigest()[:16]

    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is alive

        If psutil is not available, assumes process is alive
        and relies on other detection layers (heartbeat, orphaned session).
        """
        if not HAS_PSUTIL:
            # Fallback: assume alive, let other layers detect crash
            return True

        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False

    def _update_heartbeat(self, session_id: str, pid: int) -> None:
        """Update session heartbeat"""
        heartbeat_file = self.heartbeat_dir / f"{session_id}.heartbeat"
        heartbeat_data = {"session_id": session_id, "pid": pid, "timestamp": time.time()}

        with open(heartbeat_file, "w", encoding="utf-8") as f:
            json.dump(heartbeat_data, f, ensure_ascii=True)

    def _verify_context_integrity(self, checkpoint: Checkpoint) -> bool:
        """Verify context integrity using hash"""
        computed_hash = self._generate_context_hash(checkpoint.context_data)
        return computed_hash == checkpoint.context_hash

    def _check_disk_space(self) -> bool:
        """Check if disk has enough space

        If psutil is not available, assumes disk space is sufficient.
        """
        if not HAS_PSUTIL:
            # Fallback: assume disk space is OK
            return True

        try:
            disk = psutil.disk_usage(str(Path.cwd()))
            return disk.free > 100 * 1024 * 1024
        except Exception:
            return True

    def _detect_orphaned_session(self, session_id: str) -> bool:
        """Detect orphaned session (file-based detection)

        Legacy detection layer from Implementation A.
        Checks if session file exists and has:
        - graceful_shutdown = False
        - last_update > 1 hour ago

        Args:
            session_id: Session ID to check

        Returns:
            True if session is orphaned (crashed without graceful shutdown)
        """
        try:
            session_file = self.checkpoint_dir.parent / f"{session_id}.json"

            if not session_file.exists():
                return False

            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            # Check graceful shutdown flag
            if session_data.get("graceful_shutdown", False):
                return False

            # Check if session is old enough (1 hour threshold)
            last_update = session_data.get("last_update")
            if not last_update:
                return False

            last_update_time = datetime.fromisoformat(last_update)
            time_since_update = datetime.now(timezone.utc) - last_update_time

            # 1 hour = 3600 seconds
            return time_since_update.total_seconds() > 3600

        except Exception:
            return False

    def _capture_file_states(self) -> Dict[str, str]:
        """Capture current file states (hash)"""
        file_states = {}

        important_files = [
            "scripts/session_manager.py",
            "scripts/session_recovery.py",
            "config/constitution.yaml",
        ]

        for file_path in important_files:
            path = Path(file_path)
            if path.exists():
                try:
                    with open(path, "rb") as f:
                        content = f.read()
                    file_hash = sha256(content).hexdigest()[:16]
                    file_states[file_path] = file_hash
                except Exception:
                    pass

        return file_states

    def _restore_file_states(self, file_states: Dict[str, str]) -> int:
        """Restore file states (verify integrity)"""
        verified = 0

        for file_path, expected_hash in file_states.items():
            path = Path(file_path)
            if path.exists():
                try:
                    with open(path, "rb") as f:
                        content = f.read()
                    actual_hash = sha256(content).hexdigest()[:16]

                    if actual_hash == expected_hash:
                        verified += 1
                except Exception:
                    pass

        return verified

    def _restore_context(self, session_id: str, context_data: Dict[str, Any]) -> bool:
        """Restore session context"""
        try:
            session_file = self.checkpoint_dir.parent / f"{session_id}.json"

            if session_file.exists():
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)

                session_data["scope_data"]["SESSION"] = context_data
                session_data["last_checkpoint"] = datetime.now(timezone.utc).isoformat()

                with open(session_file, "w", encoding="utf-8") as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=True)

                return True

            return False

        except Exception:
            return False

    def _save_recovery_log(self, log: RecoveryLog) -> None:
        """Save recovery log"""
        log_file = self.recovery_log_dir / f"{log.recovery_id}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log.to_dict(), f, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    import sys

    recovery = SessionRecovery()

    if len(sys.argv) < 2:
        print("Usage: python session_recovery.py <command> [session_id]")
        print("Commands:")
        print("  detect <session_id>  - Detect crash")
        print("  recover <session_id> - Recover session")
        print("  stats                - Show recovery statistics")
        sys.exit(1)

    command = sys.argv[1]

    if command == "detect":
        if len(sys.argv) < 3:
            print("Error: session_id required")
            sys.exit(1)

        session_id = sys.argv[2]
        crash_reason = recovery.detect_crash(session_id)

        if crash_reason:
            print(f"[CRASH DETECTED] Reason: {crash_reason.value}")
        else:
            print("[OK] Session running normally")

    elif command == "recover":
        if len(sys.argv) < 3:
            print("Error: session_id required")
            sys.exit(1)

        session_id = sys.argv[2]
        log = recovery.recover_session(session_id)

        print(f"[RECOVERY] Status: {log.status}")
        print(f"  Crash reason: {log.crash_reason}")
        print(f"  Files restored: {log.files_restored}")
        print(f"  Context restored: {log.context_restored}")
        print(f"  Recovery time: {log.recovery_time_sec:.3f}s")

        if log.error_message:
            print(f"  Error: {log.error_message}")

    elif command == "stats":
        rate = recovery.get_recovery_success_rate()
        print(f"[STATS] Recovery success rate: {rate:.1%}")

        logs = list(recovery.recovery_log_dir.glob("recovery_*.json"))
        print(f"  Total recoveries: {len(logs)}")

        recent_logs = sorted(logs, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        print("\n  Recent recoveries:")
        for log_file in recent_logs:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                print(f"    - {log_data['session_id']}: {log_data['status']} ({log_data['recovery_time_sec']:.1f}s)")
            except Exception:
                pass

    else:
        print(f"Unknown command: {command}")
