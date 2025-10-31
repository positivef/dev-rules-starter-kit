#!/usr/bin/env python3
"""
AI Agent Auto Initialization System
Automatically reads HANDOFF_REPORT.md on session start
Supports Claude, Codex, Gemini
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


class AgentAutoInit:
    """Universal auto-initialization for all AI agents"""

    def __init__(self, agent_name: Optional[str] = None):
        """Initialize with agent detection"""
        self.agent_name = agent_name or self.detect_agent()
        self.handoff_file = Path("HANDOFF_REPORT.md")
        self.context_hash = None
        self.instructions = None

    def detect_agent(self) -> str:
        """Auto-detect which AI agent is running"""
        # Check environment variables
        if os.getenv("CLAUDE_CODE"):
            return "Claude"
        elif os.getenv("CODEX_CLI"):
            return "Codex"
        elif os.getenv("GEMINI_AI"):
            return "Gemini"

        # Check for specific files/markers
        if Path(".claude").exists():
            return "Claude"
        elif Path(".codex").exists():
            return "Codex"
        elif Path(".gemini").exists():
            return "Gemini"

        # Default
        return "Unknown"

    def display_banner(self):
        """Display initialization banner"""
        print("=" * 60)
        print("  AI AGENT HANDOFF PROTOCOL - AUTO INITIALIZATION")
        print(f"  Agent: {self.agent_name}")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def read_handoff_report(self) -> bool:
        """Read and display previous handoff report"""
        if not self.handoff_file.exists():
            print("\n[WARN] No HANDOFF_REPORT.md found")
            print("   Starting fresh session (no previous handoff)")
            return False

        print("\n[INFO] Reading previous handoff report...")
        print("-" * 50)

        with open(self.handoff_file, "r", encoding="utf-8") as f:
            content = f.read()

            # Extract key sections
            if "## 2. Summary of Work" in content:
                summary_start = content.index("## 2. Summary")
                summary_end = (
                    content.index("##", summary_start + 1) if "##" in content[summary_start + 1 :] else len(content)
                )
                summary = content[summary_start:summary_end].strip()
                print(f"\n{summary}")

            if "## 6. Instructions for Next Agent" in content:
                inst_start = content.index("## 6. Instructions")
                inst_end = content.index("##", inst_start + 1) if "##" in content[inst_start + 1 :] else len(content)
                self.instructions = content[inst_start:inst_end].strip()
                print(f"\n{self.instructions}")

            # Show metadata
            if "- **Latest Commit Hash:**" in content:
                for line in content.split("\n"):
                    if "Latest Commit Hash:" in line:
                        print(f"\n[INFO] {line.strip()}")
                    elif "Context Hash:" in line:
                        print(f"[INFO] {line.strip()}")

        print("-" * 50)
        return True

    def sync_context(self):
        """Synchronize context hash"""
        print("\n[SYNC] Synchronizing context...")

        try:
            result = subprocess.run(
                ["python", "scripts/context_provider.py", "print-hash"], capture_output=True, text=True, timeout=5
            )
            self.context_hash = result.stdout.strip()

            if self.context_hash and not self.context_hash.startswith("N/A"):
                print(f"[OK] Context hash: {self.context_hash[:16]}...")
            else:
                print("[WARN]  Could not retrieve context hash")
        except Exception as e:
            print(f"[WARN]  Context sync failed: {e}")

    def update_agent_board(self):
        """Update multi-agent sync board"""
        print("\n[STATUS] Updating agent sync board...")

        try:
            cmd = [
                "python",
                "scripts/multi_agent_sync.py",
                "update-status",
                self.agent_name,
                "Session initialized - ready to work",
            ]

            if self.context_hash:
                cmd.extend(["--context-hash", self.context_hash])

            subprocess.run(cmd, capture_output=True, timeout=5)
            print(f"[OK] Agent board updated: {self.agent_name} is active")
        except Exception as e:
            print(f"[WARN]  Agent board update failed: {e}")

    def check_uncommitted_changes(self):
        """Check for uncommitted git changes"""
        print("\n[INFO] Checking git status...")

        try:
            result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=5)

            if result.stdout.strip():
                print("[WARN]  Uncommitted changes detected:")
                for line in result.stdout.strip().split("\n")[:5]:
                    print(f"   {line}")
                if len(result.stdout.strip().split("\n")) > 5:
                    print("   ... and more")
            else:
                print("[OK] Working directory clean")
        except Exception:
            print("[WARN]  Could not check git status")

    def show_quick_commands(self):
        """Display agent-specific quick commands"""
        print("\n[HELP] Quick Commands:")
        print("-" * 50)

        if self.agent_name == "Claude":
            print("# View full report:     cat HANDOFF_REPORT.md")
            print("# Create new handoff:   python scripts/create_handoff_report.py --author Claude ...")
            print("# Check agent status:   python scripts/multi_agent_sync.py list")

        elif self.agent_name == "Codex":
            print("# View full report:     open('HANDOFF_REPORT.md').read()")
            print("# Create new handoff:   create_handoff('Codex', 'summary', 'instructions')")
            print("# Check context:        get_context_hash()")

        elif self.agent_name == "Gemini":
            print("# View full report:     handoff.view_report()")
            print("# Create new handoff:   handoff.create('summary', 'instructions')")
            print("# Update status:        handoff.update_status('working')")

        print("-" * 50)

    def run(self):
        """Execute full initialization sequence"""
        self.display_banner()

        # Core initialization steps
        handoff_exists = self.read_handoff_report()
        self.sync_context()
        self.update_agent_board()
        self.check_uncommitted_changes()

        # Show instructions if found
        if self.instructions:
            print("\n" + "=" * 60)
            print("[TASK] YOUR TASK:")
            print(self.instructions)
            print("=" * 60)

        self.show_quick_commands()

        print(f"\n[OK] {self.agent_name} initialization complete!")
        print("Ready to continue work.\n")

        return handoff_exists


# Agent-specific helper functions
def claude_init():
    """Claude-specific initialization"""
    init = AgentAutoInit("Claude")
    return init.run()


def codex_init():
    """Codex-specific initialization"""
    init = AgentAutoInit("Codex")
    return init.run()


def gemini_init():
    """Gemini-specific initialization"""
    init = AgentAutoInit("Gemini")
    return init.run()


# Auto-execute if running directly
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent Auto Initialization")
    parser.add_argument(
        "--agent", choices=["Claude", "Codex", "Gemini"], help="Specify agent name (auto-detect if not provided)"
    )
    parser.add_argument("--minimal", action="store_true", help="Minimal output mode")

    args = parser.parse_args()

    # Run initialization
    if args.agent:
        init = AgentAutoInit(args.agent)
    else:
        init = AgentAutoInit()

    init.run()
