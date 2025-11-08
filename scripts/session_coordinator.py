"""Session Coordinator - Multi-AI session coordination system.

Constitutional Compliance:
- P2: Evidence-Based (all coordination actions logged)
- P6: Quality Gates (performance monitoring)
- P8: Test-First Development (comprehensive test coverage)
- P10: Windows UTF-8 (encoding handled)

Purpose:
    Central coordination hub for multiple AI sessions working on the same project.
    Manages session registration, heartbeat monitoring, dead session detection,
    and task distribution across sessions.

Features:
    - Session registration/deregistration by role (frontend/backend/testing/assistant)
    - Heartbeat monitoring (30-second intervals)
    - Dead session detection (>2 minutes without heartbeat)
    - Task distribution and load balancing
    - Session role management and querying
    - Integration with session_recovery.py for crash recovery

Usage:
    # Register session
    coordinator = SessionCoordinator()
    coordinator.register_session("session1", role="frontend", agent_id="claude_code_1")

    # Update heartbeat
    coordinator.update_heartbeat("session1")

    # Check active sessions
    active = coordinator.get_active_sessions()

    # Detect dead sessions
    dead = coordinator.detect_dead_sessions()

    # Assign task
    assigned_to = coordinator.assign_task("FEAT-2025-11-04-01", preferred_role="backend")

Related:
    - session_recovery.py: Crash detection and recovery (Phase 1)
    - shared_context_manager.py: Context sharing (Phase 2)
    - agent_sync.py: File lock coordination
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
SHARED_CONTEXT_DIR = Path(__file__).resolve().parent.parent / "RUNS" / "context"
SHARED_CONTEXT_FILE = SHARED_CONTEXT_DIR / "shared_context.json"
HEARTBEAT_INTERVAL = 30  # seconds
DEAD_SESSION_THRESHOLD = 120  # seconds (2 minutes)


@dataclass
class Session:
    """Represents an active AI session."""

    session_id: str
    agent_id: str
    role: str  # frontend/backend/testing/assistant
    status: str  # active/idle/dead
    registered_at: datetime
    last_heartbeat: datetime
    current_task: Optional[str] = None
    locked_files: List[str] = None

    def __post_init__(self):
        if self.locked_files is None:
            self.locked_files = []

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        data = asdict(self)
        data["registered_at"] = self.registered_at.isoformat()
        data["last_heartbeat"] = self.last_heartbeat.isoformat()
        return data

    @staticmethod
    def from_dict(data: Dict) -> Session:
        """Create Session from dict."""
        return Session(
            session_id=data["session_id"],
            agent_id=data["agent_id"],
            role=data["role"],
            status=data["status"],
            registered_at=datetime.fromisoformat(data["registered_at"]),
            last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
            current_task=data.get("current_task"),
            locked_files=data.get("locked_files", []),
        )


@dataclass
class CoordinationStats:
    """Statistics for session coordination."""

    total_sessions: int
    active_sessions: int
    dead_sessions: int
    tasks_assigned: int
    conflicts_detected: int
    average_session_duration_minutes: float


class SessionCoordinator:
    """Coordinates multiple AI sessions working on the same project."""

    def __init__(self, context_dir: Path = SHARED_CONTEXT_DIR):
        self.context_dir = context_dir
        self.context_file = context_dir / "shared_context.json"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # Initialize shared context if not exists
        if not self.context_file.exists():
            self._initialize_context()

        self.stats = {
            "tasks_assigned": 0,
            "conflicts_detected": 0,
        }

    def _initialize_context(self):
        """Initialize shared context file."""
        initial_context = {
            "project": "dev-rules-starter-kit",
            "version": "2.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "sessions": [],
            "shared_knowledge": {
                "active_feature": None,
                "constitution_version": "1.0.0",
                "adoption_level": 2,
                "recent_commits": [],
                "open_conflicts": [],
            },
            "context_versions": [],
        }
        self._write_context(initial_context)
        logger.info("Initialized shared context")

    def _read_context(self) -> Dict:
        """Read shared context from file."""
        try:
            return json.loads(self.context_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Failed to read context, reinitializing")
            self._initialize_context()
            return self._read_context()

    def _write_context(self, context: Dict):
        """Write shared context to file."""
        context["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.context_file.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")

    def register_session(self, session_id: str, role: str, agent_id: str) -> bool:
        """Register a new session.

        Args:
            session_id: Unique session identifier
            role: Session role (frontend/backend/testing/assistant)
            agent_id: Agent identifier (e.g., claude_code_1)

        Returns:
            True if registration successful, False if session already exists
        """
        context = self._read_context()

        # Check if session already exists
        for session in context["sessions"]:
            if session["session_id"] == session_id:
                logger.warning(f"Session {session_id} already registered")
                return False

        # Create new session
        now = datetime.now(timezone.utc)
        new_session = Session(
            session_id=session_id,
            agent_id=agent_id,
            role=role,
            status="active",
            registered_at=now,
            last_heartbeat=now,
        )

        context["sessions"].append(new_session.to_dict())
        self._write_context(context)

        logger.info(f"Registered session: {session_id} (role: {role})")
        return True

    def deregister_session(self, session_id: str) -> bool:
        """Deregister a session (graceful shutdown).

        Args:
            session_id: Session to deregister

        Returns:
            True if deregistration successful, False if session not found
        """
        context = self._read_context()

        # Find and remove session
        sessions = context["sessions"]
        for i, session in enumerate(sessions):
            if session["session_id"] == session_id:
                sessions.pop(i)
                self._write_context(context)
                logger.info(f"Deregistered session: {session_id}")
                return True

        logger.warning(f"Session {session_id} not found for deregistration")
        return False

    def update_heartbeat(self, session_id: str) -> bool:
        """Update session heartbeat timestamp.

        Args:
            session_id: Session to update

        Returns:
            True if update successful, False if session not found
        """
        context = self._read_context()

        # Find and update session
        for session in context["sessions"]:
            if session["session_id"] == session_id:
                session["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
                session["status"] = "active"
                self._write_context(context)
                return True

        logger.warning(f"Session {session_id} not found for heartbeat update")
        return False

    def detect_dead_sessions(self) -> List[str]:
        """Detect sessions that haven't sent heartbeat in >2 minutes.

        Returns:
            List of dead session IDs
        """
        context = self._read_context()
        now = datetime.now(timezone.utc)
        threshold = timedelta(seconds=DEAD_SESSION_THRESHOLD)
        dead_sessions = []

        for session in context["sessions"]:
            last_heartbeat = datetime.fromisoformat(session["last_heartbeat"])
            if now - last_heartbeat > threshold:
                session["status"] = "dead"
                dead_sessions.append(session["session_id"])

        if dead_sessions:
            self._write_context(context)
            logger.warning(f"Detected {len(dead_sessions)} dead sessions: {dead_sessions}")

        return dead_sessions

    def get_active_sessions(self) -> List[Session]:
        """Get all active sessions.

        Returns:
            List of active Session objects
        """
        context = self._read_context()
        now = datetime.now(timezone.utc)
        threshold = timedelta(seconds=DEAD_SESSION_THRESHOLD)
        active = []

        for session_data in context["sessions"]:
            last_heartbeat = datetime.fromisoformat(session_data["last_heartbeat"])
            if now - last_heartbeat <= threshold:
                session = Session.from_dict(session_data)
                active.append(session)

        return active

    def get_session_by_role(self, role: str) -> Optional[Session]:
        """Get first active session with specified role.

        Args:
            role: Session role to find (frontend/backend/testing/assistant)

        Returns:
            Session object if found, None otherwise
        """
        active_sessions = self.get_active_sessions()
        for session in active_sessions:
            if session.role == role:
                return session
        return None

    def assign_task(self, task_id: str, preferred_role: Optional[str] = None) -> Optional[str]:
        """Assign task to an available session.

        Args:
            task_id: Task identifier (e.g., FEAT-2025-11-04-01)
            preferred_role: Preferred session role (optional)

        Returns:
            Session ID that task was assigned to, None if no available session
        """
        context = self._read_context()
        active_sessions = self.get_active_sessions()

        if not active_sessions:
            logger.warning("No active sessions available for task assignment")
            return None

        # Try preferred role first
        if preferred_role:
            for session in active_sessions:
                if session.role == preferred_role and session.current_task is None:
                    # Assign task
                    for s in context["sessions"]:
                        if s["session_id"] == session.session_id:
                            s["current_task"] = task_id
                            self._write_context(context)
                            self.stats["tasks_assigned"] += 1
                            logger.info(f"Assigned task {task_id} to {session.session_id} (role: {preferred_role})")
                            return session.session_id

        # No preferred role or preferred role unavailable, assign to any idle session
        for session in active_sessions:
            if session.current_task is None:
                for s in context["sessions"]:
                    if s["session_id"] == session.session_id:
                        s["current_task"] = task_id
                        self._write_context(context)
                        self.stats["tasks_assigned"] += 1
                        logger.info(f"Assigned task {task_id} to {session.session_id} (role: {session.role})")
                        return session.session_id

        logger.warning(f"All sessions busy, cannot assign task {task_id}")
        return None

    def update_session_task(self, session_id: str, task_id: Optional[str]) -> bool:
        """Update current task for a session.

        Args:
            session_id: Session to update
            task_id: New task ID, or None to clear task

        Returns:
            True if update successful, False if session not found
        """
        context = self._read_context()

        for session in context["sessions"]:
            if session["session_id"] == session_id:
                session["current_task"] = task_id
                self._write_context(context)
                logger.info(f"Updated task for {session_id}: {task_id}")
                return True

        return False

    def update_session_locks(self, session_id: str, locked_files: List[str]) -> bool:
        """Update locked files for a session.

        Args:
            session_id: Session to update
            locked_files: List of file paths currently locked

        Returns:
            True if update successful, False if session not found
        """
        context = self._read_context()

        for session in context["sessions"]:
            if session["session_id"] == session_id:
                session["locked_files"] = locked_files
                self._write_context(context)
                return True

        return False

    def get_statistics(self) -> CoordinationStats:
        """Get coordination statistics.

        Returns:
            CoordinationStats object with current statistics
        """
        context = self._read_context()
        active_sessions = self.get_active_sessions()
        dead_sessions = self.detect_dead_sessions()

        # Calculate average session duration
        total_duration = timedelta()
        session_count = 0
        now = datetime.now(timezone.utc)

        for session_data in context["sessions"]:
            registered_at = datetime.fromisoformat(session_data["registered_at"])
            total_duration += now - registered_at
            session_count += 1

        avg_duration = total_duration.total_seconds() / 60 / session_count if session_count > 0 else 0.0

        return CoordinationStats(
            total_sessions=len(context["sessions"]),
            active_sessions=len(active_sessions),
            dead_sessions=len(dead_sessions),
            tasks_assigned=self.stats["tasks_assigned"],
            conflicts_detected=self.stats["conflicts_detected"],
            average_session_duration_minutes=avg_duration,
        )


def main():
    """CLI interface for session coordinator."""
    import argparse

    parser = argparse.ArgumentParser(description="Session Coordinator")
    parser.add_argument("--register", action="store_true", help="Register new session")
    parser.add_argument("--deregister", action="store_true", help="Deregister session")
    parser.add_argument("--heartbeat", action="store_true", help="Update heartbeat")
    parser.add_argument("--status", action="store_true", help="Show coordination status")
    parser.add_argument("--detect-dead", action="store_true", help="Detect dead sessions")
    parser.add_argument("--session-id", type=str, help="Session identifier")
    parser.add_argument("--role", type=str, help="Session role (frontend/backend/testing/assistant)")
    parser.add_argument("--agent-id", type=str, help="Agent identifier")

    args = parser.parse_args()

    coordinator = SessionCoordinator()

    if args.register:
        if not all([args.session_id, args.role, args.agent_id]):
            print("[ERROR] --register requires --session-id, --role, and --agent-id")
            return
        success = coordinator.register_session(args.session_id, args.role, args.agent_id)
        print(f"[OK] Registered: {success}")

    elif args.deregister:
        if not args.session_id:
            print("[ERROR] --deregister requires --session-id")
            return
        success = coordinator.deregister_session(args.session_id)
        print(f"[OK] Deregistered: {success}")

    elif args.heartbeat:
        if not args.session_id:
            print("[ERROR] --heartbeat requires --session-id")
            return
        success = coordinator.update_heartbeat(args.session_id)
        print(f"[OK] Heartbeat updated: {success}")

    elif args.detect_dead:
        dead = coordinator.detect_dead_sessions()
        print(f"[DEAD SESSIONS] {len(dead)}")
        for session_id in dead:
            print(f"  - {session_id}")

    elif args.status:
        stats = coordinator.get_statistics()
        active = coordinator.get_active_sessions()

        print("\n=== Session Coordination Status ===")
        print(f"Total sessions: {stats.total_sessions}")
        print(f"Active sessions: {stats.active_sessions}")
        print(f"Dead sessions: {stats.dead_sessions}")
        print(f"Tasks assigned: {stats.tasks_assigned}")
        print(f"Average duration: {stats.average_session_duration_minutes:.1f} minutes")

        if active:
            print("\n=== Active Sessions ===")
            for session in active:
                print(f"\n{session.session_id}")
                print(f"  Role: {session.role}")
                print(f"  Agent: {session.agent_id}")
                print(f"  Status: {session.status}")
                print(f"  Task: {session.current_task or 'None'}")
                print(f"  Locked files: {len(session.locked_files)}")
                print(f"  Last heartbeat: {session.last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
