#!/usr/bin/env python3
"""
Automatic Context Tracker for AI Agents
Tracks all development activities and auto-updates handoff context
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ContextTracker:
    """Automatically tracks and updates development context"""

    def __init__(self):
        self.context_file = Path("RUNS/context/current_context.json")
        self.context_file.parent.mkdir(parents=True, exist_ok=True)

        self.session_start = datetime.now()
        self.agent_name = self.detect_agent()
        self.activities = []
        self.modified_files = set()
        self.commands_executed = []
        self.test_results = {}

    def detect_agent(self) -> str:
        """Detect current AI agent"""
        if os.getenv("CLAUDE_CODE"):
            return "Claude"
        elif os.getenv("CODEX_CLI"):
            return "Codex"
        elif os.getenv("GEMINI_AI"):
            return "Gemini"
        return "Unknown"

    def track_file_change(self, filepath: str, change_type: str):
        """Track file modifications"""
        self.modified_files.add(filepath)
        self.activities.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "file_change",
                "file": filepath,
                "change": change_type,
                "agent": self.agent_name,
            }
        )
        self.save_context()

    def track_command(self, command: str, result: Optional[str] = None):
        """Track executed commands"""
        self.commands_executed.append(command)
        self.activities.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "command",
                "command": command,
                "result": result,
                "agent": self.agent_name,
            }
        )
        self.save_context()

    def track_test(self, test_name: str, passed: bool):
        """Track test results"""
        self.test_results[test_name] = passed
        self.activities.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "test",
                "test": test_name,
                "passed": passed,
                "agent": self.agent_name,
            }
        )
        self.save_context()

    def generate_summary(self) -> str:
        """Generate work summary from tracked activities"""
        summary = []

        # File changes summary
        if self.modified_files:
            summary.append(f"Modified {len(self.modified_files)} files:")
            for f in list(self.modified_files)[:5]:
                summary.append(f"  - {f}")
            if len(self.modified_files) > 5:
                summary.append(f"  ... and {len(self.modified_files) - 5} more")

        # Commands summary
        if self.commands_executed:
            summary.append(f"\nExecuted {len(self.commands_executed)} commands")

        # Test summary
        if self.test_results:
            passed = sum(1 for p in self.test_results.values() if p)
            total = len(self.test_results)
            summary.append(f"\nTests: {passed}/{total} passed")

        return "\n".join(summary) if summary else "No significant activities tracked"

    def save_context(self):
        """Save current context to file"""
        context = {
            "agent": self.agent_name,
            "session_start": self.session_start.isoformat(),
            "last_update": datetime.now().isoformat(),
            "modified_files": list(self.modified_files),
            "commands": self.commands_executed[-10:],  # Last 10 commands
            "test_results": self.test_results,
            "activities_count": len(self.activities),
            "summary": self.generate_summary(),
        }

        self.context_file.write_text(json.dumps(context, indent=2), encoding="utf-8")

    def auto_create_handoff(self, instructions: str = "Continue development"):
        """Automatically create handoff report with tracked context"""
        summary = self.generate_summary()

        # Get test results summary
        test_summary = "No tests run"
        if self.test_results:
            passed = sum(1 for p in self.test_results.values() if p)
            total = len(self.test_results)
            test_summary = f"{passed}/{total} tests passed"

        # Create handoff
        cmd = [
            "python",
            "scripts/create_handoff_report.py",
            "--author",
            self.agent_name,
            "--summary",
            summary,
            "--test-results",
            test_summary,
            "--instructions",
            instructions,
        ]

        subprocess.run(cmd, capture_output=True)
        print(f"[OK] Auto-created handoff at {datetime.now().strftime('%H:%M:%S')}")


class AutoContextFileWatcher(FileSystemEventHandler):
    """Watch file changes and auto-update context"""

    def __init__(self, tracker: ContextTracker):
        self.tracker = tracker
        self.ignore_patterns = {".git", "__pycache__", ".pytest_cache", "node_modules"}

    def should_track(self, path: str) -> bool:
        """Check if file should be tracked"""
        path_obj = Path(path)

        # Ignore certain directories
        for part in path_obj.parts:
            if part in self.ignore_patterns:
                return False

        # Track only code files
        return path_obj.suffix in {".py", ".js", ".ts", ".yaml", ".json", ".md"}

    def on_modified(self, event):
        if not event.is_directory and self.should_track(event.src_path):
            self.tracker.track_file_change(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory and self.should_track(event.src_path):
            self.tracker.track_file_change(event.src_path, "created")


class AutoContextManager:
    """Main context management system"""

    def __init__(self, auto_handoff_interval: int = 1800):  # 30 minutes
        self.tracker = ContextTracker()
        self.auto_handoff_interval = auto_handoff_interval
        self.last_handoff = time.time()
        self.observer = None

    def start_watching(self):
        """Start watching file system changes"""
        event_handler = AutoContextFileWatcher(self.tracker)
        self.observer = Observer()
        self.observer.schedule(event_handler, ".", recursive=True)
        self.observer.start()
        print(f"[INFO] Auto-context tracking started for {self.tracker.agent_name}")

    def check_auto_handoff(self):
        """Check if it's time for auto handoff"""
        if time.time() - self.last_handoff > self.auto_handoff_interval:
            print("\n[TIME] Auto-handoff time reached (30 minutes)")
            self.tracker.auto_create_handoff("Continue from auto-checkpoint")
            self.last_handoff = time.time()

    def run(self):
        """Run the auto-context manager"""
        self.start_watching()

        try:
            while True:
                time.sleep(60)  # Check every minute
                self.check_auto_handoff()
        except KeyboardInterrupt:
            self.observer.stop()
            print("\n👋 Auto-context tracking stopped")

            # Final handoff
            response = input("Create final handoff? (y/n): ")
            if response.lower() == "y":
                instructions = input("Instructions for next agent: ")
                self.tracker.auto_create_handoff(instructions)

        self.observer.join()


# Command wrapper for automatic tracking
def track_command(command: str):
    """Decorator to track command execution"""
    tracker = ContextTracker()
    tracker.track_command(command)
    return command


# Test tracking wrapper
def track_test(test_name: str):
    """Decorator to track test results"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = ContextTracker()
            try:
                result = func(*args, **kwargs)
                tracker.track_test(test_name, True)
                return result
            except Exception as e:
                tracker.track_test(test_name, False)
                raise e

        return wrapper

    return decorator


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto Context Tracker")
    parser.add_argument("--watch", action="store_true", help="Start file watching")
    parser.add_argument("--summary", action="store_true", help="Show current context summary")
    parser.add_argument("--handoff", action="store_true", help="Create handoff now")
    parser.add_argument("--track-command", help="Track a command execution")
    parser.add_argument("--agent", help="Set agent name", choices=["Claude", "Codex", "Gemini"])

    args = parser.parse_args()

    if args.agent:
        os.environ[f"{args.agent.upper()}_CODE"] = "1"

    tracker = ContextTracker()

    if args.summary:
        print(tracker.generate_summary())
    elif args.handoff:
        instructions = input("Instructions for next agent: ")
        tracker.auto_create_handoff(instructions)
    elif args.track_command:
        tracker.track_command(args.track_command)
        print(f"[OK] Tracked command: {args.track_command}")
    elif args.watch:
        manager = AutoContextManager()
        manager.run()
    else:
        print("Auto Context Tracker")
        print("Use --help for options")
