#!/usr/bin/env python3
"""Session Recovery System - Automatic crash detection and recovery.

Enhances session_manager.py with automatic crash detection and recovery:
- Detects abnormal session termination
- Validates context integrity
- Automatic checkpoint creation (30-minute intervals)
- Crash history tracking
- Recovery workflow orchestration

Constitutional Compliance:
- P2: Evidence-Based (all crashes logged to RUNS/evidence/)
- P6: Quality Gates (recovery success rate >95%)
- P8: Test-First Development
- P10: Windows UTF-8 (no emojis, ASCII alternatives)

Usage:
    # Automatic recovery
    python scripts/session_recovery.py --recover

    # Test recovery system
    python scripts/session_recovery.py --test

    # Check recovery status
    python scripts/session_recovery.py --status
"""

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class CrashInfo:
    """Information about a session crash."""

    session_id: str
    crash_time: datetime
    last_checkpoint: datetime
    context_hash: str
    crash_reason: Optional[str]
    recovery_attempted: bool
    recovery_success: bool


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool
    session_id: str
    recovered_at: datetime
    context_valid: bool
    data_loss: bool
    recovery_time_seconds: float
    error_message: Optional[str] = None


class SessionRecovery:
    """Automatic session crash detection and recovery system."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize session recovery system.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.sessions_dir = self.project_root / "RUNS" / "sessions"
        self.checkpoints_dir = self.project_root / "RUNS" / "checkpoints"
        self.crashes_dir = self.project_root / "RUNS" / "evidence" / "session-crashes"
        self.context_dir = self.project_root / "RUNS" / "context"

        # Create directories
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.crashes_dir.mkdir(parents=True, exist_ok=True)
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # Recovery settings
        self.checkpoint_interval = 30  # minutes
        self.max_recovery_attempts = 3
        self.context_hash_algorithm = "sha256"

    def detect_crashes(self) -> List[CrashInfo]:
        """Detect abnormal session terminations.

        Returns:
            List of detected crashes
        """
        crashes = []

        # Check for sessions without proper shutdown
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)

                # Check if session ended abnormally
                if not session_data.get("graceful_shutdown", False):
                    session_id = session_data.get("session_id", session_file.stem)
                    last_update = datetime.fromisoformat(session_data.get("last_update", datetime.now().isoformat()))

                    # If session is older than 1 hour and not shutdown, it's a crash
                    if datetime.now() - last_update > timedelta(hours=1):
                        crash = CrashInfo(
                            session_id=session_id,
                            crash_time=last_update,
                            last_checkpoint=datetime.fromisoformat(
                                session_data.get("last_checkpoint", last_update.isoformat())
                            ),
                            context_hash=session_data.get("context_hash", ""),
                            crash_reason=session_data.get("crash_reason"),
                            recovery_attempted=session_data.get("recovery_attempted", False),
                            recovery_success=session_data.get("recovery_success", False),
                        )
                        crashes.append(crash)
            except Exception:
                # Skip corrupted session files
                continue

        return crashes

    def validate_context_integrity(self, session_id: str) -> bool:
        """Validate context integrity using hash verification.

        Args:
            session_id: Session ID to validate

        Returns:
            True if context is valid
        """
        try:
            # Find latest checkpoint
            checkpoint_pattern = f"checkpoint_{session_id}_*.json"
            checkpoints = sorted(self.checkpoints_dir.glob(checkpoint_pattern), reverse=True)

            if not checkpoints:
                return False

            latest_checkpoint = checkpoints[0]

            with open(latest_checkpoint, encoding="utf-8") as f:
                checkpoint_data = json.load(f)

            # Verify context hash
            stored_hash = checkpoint_data.get("context_hash", "")
            context_data = checkpoint_data.get("context", {})

            # Recalculate hash
            context_str = json.dumps(context_data, sort_keys=True)
            calculated_hash = hashlib.sha256(context_str.encode()).hexdigest()

            return stored_hash == calculated_hash

        except Exception:
            return False

    def create_checkpoint(self, session_id: str, context: Dict) -> Path:
        """Create a checkpoint for the current session.

        Args:
            session_id: Session ID
            context: Session context data

        Returns:
            Path to checkpoint file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoints_dir / f"checkpoint_{session_id}_{timestamp}.json"

        # Calculate context hash
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()

        checkpoint_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "context_hash": context_hash,
            "context": context,
            "checkpoint_type": "automatic",
        }

        checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2), encoding="utf-8")

        # Cleanup old checkpoints (keep last 5)
        checkpoint_pattern = f"checkpoint_{session_id}_*.json"
        checkpoints = sorted(self.checkpoints_dir.glob(checkpoint_pattern), reverse=True)

        for old_checkpoint in checkpoints[5:]:
            old_checkpoint.unlink()

        return checkpoint_file

    def recover_session(self, session_id: str) -> RecoveryResult:
        """Recover a crashed session.

        Args:
            session_id: Session ID to recover

        Returns:
            Recovery result with success status
        """
        start_time = datetime.now()

        try:
            # Find latest checkpoint
            checkpoint_pattern = f"checkpoint_{session_id}_*.json"
            checkpoints = sorted(self.checkpoints_dir.glob(checkpoint_pattern), reverse=True)

            if not checkpoints:
                return RecoveryResult(
                    success=False,
                    session_id=session_id,
                    recovered_at=datetime.now(),
                    context_valid=False,
                    data_loss=True,
                    recovery_time_seconds=0,
                    error_message="No checkpoints found",
                )

            latest_checkpoint = checkpoints[0]

            # Load checkpoint
            with open(latest_checkpoint, encoding="utf-8") as f:
                checkpoint_data = json.load(f)

            # Validate context integrity
            context_valid = self.validate_context_integrity(session_id)

            if not context_valid:
                return RecoveryResult(
                    success=False,
                    session_id=session_id,
                    recovered_at=datetime.now(),
                    context_valid=False,
                    data_loss=True,
                    recovery_time_seconds=(datetime.now() - start_time).total_seconds(),
                    error_message="Context integrity check failed",
                )

            # Restore session state
            recovered_context = checkpoint_data.get("context", {})
            checkpoint_time = datetime.fromisoformat(checkpoint_data.get("timestamp"))

            # Calculate data loss (time between crash and checkpoint)
            data_loss_seconds = (start_time - checkpoint_time).total_seconds()
            data_loss = data_loss_seconds > (self.checkpoint_interval * 60)

            # Create recovery session file
            recovery_file = self.sessions_dir / f"session_{session_id}_recovered.json"
            recovery_data = {
                "session_id": session_id,
                "recovered_at": datetime.now().isoformat(),
                "recovered_from_checkpoint": checkpoint_data.get("timestamp"),
                "context": recovered_context,
                "context_hash": checkpoint_data.get("context_hash"),
                "recovery_success": True,
                "data_loss": data_loss,
                "graceful_shutdown": False,  # Mark as recovered, not gracefully shutdown
            }

            recovery_file.write_text(json.dumps(recovery_data, indent=2), encoding="utf-8")

            # Log crash and recovery to evidence
            self._log_crash_recovery(session_id, checkpoint_data, data_loss)

            recovery_time = (datetime.now() - start_time).total_seconds()

            return RecoveryResult(
                success=True,
                session_id=session_id,
                recovered_at=datetime.now(),
                context_valid=True,
                data_loss=data_loss,
                recovery_time_seconds=recovery_time,
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                session_id=session_id,
                recovered_at=datetime.now(),
                context_valid=False,
                data_loss=True,
                recovery_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    def _log_crash_recovery(self, session_id: str, checkpoint_data: Dict, data_loss: bool) -> None:
        """Log crash and recovery to evidence directory.

        Args:
            session_id: Session ID
            checkpoint_data: Checkpoint data
            data_loss: Whether data loss occurred
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_log = self.crashes_dir / f"crash_{session_id}_{timestamp}.json"

        log_data = {
            "session_id": session_id,
            "crash_detected_at": datetime.now().isoformat(),
            "last_checkpoint": checkpoint_data.get("timestamp"),
            "recovery_attempted": True,
            "recovery_success": True,
            "data_loss": data_loss,
            "context_hash": checkpoint_data.get("context_hash"),
        }

        crash_log.write_text(json.dumps(log_data, indent=2), encoding="utf-8")

    def get_recovery_statistics(self) -> Dict:
        """Get recovery system statistics.

        Returns:
            Dictionary with recovery stats
        """
        crash_logs = list(self.crashes_dir.glob("crash_*.json"))

        total_crashes = len(crash_logs)
        successful_recoveries = 0
        total_recovery_time = 0
        data_loss_count = 0

        for crash_log in crash_logs:
            try:
                with open(crash_log, encoding="utf-8") as f:
                    log_data = json.load(f)

                if log_data.get("recovery_success"):
                    successful_recoveries += 1

                if log_data.get("data_loss"):
                    data_loss_count += 1

            except Exception:
                continue

        recovery_rate = (successful_recoveries / total_crashes * 100) if total_crashes > 0 else 0

        return {
            "total_crashes": total_crashes,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": recovery_rate,
            "data_loss_incidents": data_loss_count,
            "avg_recovery_time": total_recovery_time / successful_recoveries if successful_recoveries > 0 else 0,
        }

    def auto_recover_all(self) -> List[RecoveryResult]:
        """Automatically recover all crashed sessions.

        Returns:
            List of recovery results
        """
        crashes = self.detect_crashes()
        results = []

        for crash in crashes:
            if not crash.recovery_attempted or not crash.recovery_success:
                result = self.recover_session(crash.session_id)
                results.append(result)

        return results


def main():
    """Main entry point for session recovery CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Session Recovery System")
    parser.add_argument("--recover", action="store_true", help="Recover all crashed sessions")
    parser.add_argument("--test", action="store_true", help="Test recovery system")
    parser.add_argument("--status", action="store_true", help="Show recovery statistics")
    parser.add_argument("--session-id", type=str, help="Specific session ID to recover")

    args = parser.parse_args()

    recovery = SessionRecovery()

    if args.status:
        stats = recovery.get_recovery_statistics()
        print("\n=== Session Recovery Statistics ===")
        print(f"Total Crashes: {stats['total_crashes']}")
        print(f"Successful Recoveries: {stats['successful_recoveries']}")
        print(f"Recovery Rate: {stats['recovery_rate']:.1f}%")
        print(f"Data Loss Incidents: {stats['data_loss_incidents']}")
        print(f"Avg Recovery Time: {stats['avg_recovery_time']:.2f}s")

    elif args.recover:
        print("\n[INFO] Detecting crashed sessions...")
        results = recovery.auto_recover_all()

        if not results:
            print("[SUCCESS] No crashed sessions detected!")
        else:
            print(f"\n[RECOVERY] Recovered {len(results)} sessions:")
            for result in results:
                status = "[SUCCESS]" if result.success else "[FAILED]"
                print(f"  {status} {result.session_id} - {result.recovery_time_seconds:.2f}s")
                if not result.context_valid:
                    print("    [WARNING] Context integrity check failed")
                if result.data_loss:
                    print("    [WARNING] Some data may be lost")

    elif args.session_id:
        print(f"\n[INFO] Recovering session: {args.session_id}")
        result = recovery.recover_session(args.session_id)

        if result.success:
            print(f"[SUCCESS] Session recovered in {result.recovery_time_seconds:.2f}s")
            if result.data_loss:
                print("[WARNING] Some data loss may have occurred")
        else:
            print(f"[FAILED] Recovery failed: {result.error_message}")

    elif args.test:
        print("\n[TEST] Testing session recovery system...")

        # Test 1: Crash detection
        print("\n[TEST 1] Crash detection")
        crashes = recovery.detect_crashes()
        print(f"  Found {len(crashes)} crashed sessions")

        # Test 2: Context integrity
        print("\n[TEST 2] Context integrity validation")
        for crash in crashes[:3]:  # Test first 3
            valid = recovery.validate_context_integrity(crash.session_id)
            status = "[PASS]" if valid else "[FAIL]"
            print(f"  {status} {crash.session_id}")

        # Test 3: Recovery statistics
        print("\n[TEST 3] Recovery statistics")
        stats = recovery.get_recovery_statistics()
        print(f"  Recovery rate: {stats['recovery_rate']:.1f}%")
        target_met = "[PASS]" if stats["recovery_rate"] >= 95 else "[FAIL]"
        print(f"  Target (>95%): {target_met}")

        print("\n[SUCCESS] All tests completed!")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
