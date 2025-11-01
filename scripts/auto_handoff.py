#!/usr/bin/env python3
"""
Simplified Auto Handoff System
Automatically tracks work and creates handoff when needed
"""

import os
import json
import atexit
import subprocess
from pathlib import Path
from datetime import datetime


class AutoHandoff:
    """Automatic handoff creation on session end"""

    def __init__(self):
        self.session_file = Path("RUNS/context/current_session.json")
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        self.agent = self.detect_agent()
        self.start_time = datetime.now()
        self.work_items = []

        # Register cleanup on exit
        atexit.register(self.on_exit)

        # Load existing session if exists
        self.load_session()

        print(f"[LOG] Auto-handoff enabled for {self.agent}")
        print("   Work will be automatically saved on exit")

    def detect_agent(self):
        """Detect current agent"""
        if os.getenv("CLAUDE_CODE"):
            return "Claude"
        elif os.getenv("CODEX_CLI"):
            return "Codex"
        elif os.getenv("GEMINI_AI"):
            return "Gemini"
        return "Unknown"

    def add_work(self, description: str):
        """Add work item to track"""
        self.work_items.append({"time": datetime.now().isoformat(), "description": description})
        self.save_session()
        print(f"[OK] Tracked: {description}")

    def save_session(self):
        """Save current session state"""
        session_data = {
            "agent": self.agent,
            "start": self.start_time.isoformat(),
            "last_update": datetime.now().isoformat(),
            "work_items": self.work_items,
        }
        self.session_file.write_text(json.dumps(session_data, indent=2), encoding="utf-8")

    def load_session(self):
        """Load existing session if available"""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text(encoding="utf-8"))
                self.work_items = data.get("work_items", [])
                print(f"📂 Loaded {len(self.work_items)} existing work items")
            except Exception:
                pass

    def on_exit(self):
        """Create handoff on session exit"""
        if not self.work_items:
            return

        print("\n" + "=" * 60)
        print("🤖 AUTO-HANDOFF: Session ending, creating handoff...")

        # Generate summary
        summary = f"Completed {len(self.work_items)} tasks:\n"
        for item in self.work_items[-5:]:  # Last 5 items
            summary += f"- {item['description']}\n"

        # Check for uncommitted changes
        git_status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout

        if git_status.strip():
            print("[WARN]  Uncommitted changes detected!")
            commit = input("Commit changes before handoff? (y/n): ")
            if commit.lower() == "y":
                message = input("Commit message: ")
                subprocess.run(["git", "add", "."])
                subprocess.run(["git", "commit", "-m", message])

        # Get instructions for next agent
        print("\n[LOG] Creating handoff report...")
        instructions = input("Instructions for next agent (or Enter to skip): ")
        if not instructions:
            instructions = "Review completed work and continue development"

        # Create handoff
        cmd = [
            "python",
            "scripts/create_handoff_report.py",
            "--author",
            self.agent,
            "--summary",
            summary,
            "--test-results",
            "See git log for test results",
            "--instructions",
            instructions,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Handoff report created successfully!")

            # Clear session file
            self.session_file.unlink(missing_ok=True)
        else:
            print("[FAIL] Failed to create handoff report")

        print("=" * 60)


# Global instance
_auto_handoff = None


def init_auto_handoff():
    """Initialize auto handoff system"""
    global _auto_handoff
    if _auto_handoff is None:
        _auto_handoff = AutoHandoff()
    return _auto_handoff


def track(description: str):
    """Track work item"""
    handoff = init_auto_handoff()
    handoff.add_work(description)


def manual_handoff(instructions: str = "Continue development"):
    """Manually trigger handoff"""
    handoff = init_auto_handoff()

    summary = f"Completed {len(handoff.work_items)} tasks"
    if handoff.work_items:
        summary += ":\n" + "\n".join(f"- {item['description']}" for item in handoff.work_items[-5:])

    cmd = [
        "python",
        "scripts/create_handoff_report.py",
        "--author",
        handoff.agent,
        "--summary",
        summary,
        "--test-results",
        "See logs",
        "--instructions",
        instructions,
    ]

    subprocess.run(cmd)
    print("[OK] Manual handoff created")


# Auto-initialize on import
init_auto_handoff()


if __name__ == "__main__":
    print("\n📋 Auto Handoff System Active")
    print("\nUsage in your code:")
    print("  from auto_handoff import track")
    print("  track('Implemented user authentication')")
    print("  track('Fixed bug in payment module')")
    print("\nHandoff will be created automatically on exit!")

    # Example usage
    track("System initialized")

    # Demo work
    response = input("\nAdd some work items? (y/n): ")
    if response.lower() == "y":
        while True:
            work = input("Work description (or Enter to finish): ")
            if not work:
                break
            track(work)

    print("\n[OK] All work tracked. Handoff will be created on exit.")
