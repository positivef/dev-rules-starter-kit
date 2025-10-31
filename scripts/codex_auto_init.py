#!/usr/bin/env python3
"""
Codex CLI Auto-Initialization
Automatically runs when Codex session starts
"""

import os
import sys
import subprocess
from pathlib import Path

# Mark as Codex environment
os.environ["CODEX_CLI"] = "1"

# Create .codex directory if not exists
codex_dir = Path(".codex")
codex_dir.mkdir(exist_ok=True)


class CodexSession:
    """Codex session with automatic handoff protocol"""

    def __init__(self):
        """Initialize Codex session with handoff"""
        self.agent_name = "Codex"
        self.handoff_file = Path("HANDOFF_REPORT.md")
        self.instructions = None

        # Run auto-init
        self._auto_init()

    def _auto_init(self):
        """Run automatic initialization"""
        print("=" * 60)
        print("  CODEX CLI - AUTO INITIALIZATION")
        print("=" * 60)

        # Import agent_auto_init
        sys.path.insert(0, "scripts")
        from agent_auto_init import codex_init

        # Run initialization
        codex_init()

        # Store instructions if found
        if self.handoff_file.exists():
            content = self.handoff_file.read_text(encoding="utf-8")
            if "## 6. Instructions" in content:
                start = content.index("## 6. Instructions")
                end = content.index("##", start + 1) if "##" in content[start + 1 :] else len(content)
                self.instructions = content[start:end].strip()

    def create_handoff(self, summary: str, instructions: str, test_results: str = "Tests passed"):
        """Create handoff report for next agent"""
        cmd = [
            "python",
            "scripts/create_handoff_report.py",
            "--author",
            self.agent_name,
            "--summary",
            summary,
            "--test-results",
            test_results,
            "--instructions",
            instructions,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Handoff created successfully")
        else:
            print(f"[FAIL] Handoff creation failed: {result.stderr}")

    def get_context_hash(self):
        """Get current context hash"""
        result = subprocess.run(["python", "scripts/context_provider.py", "print-hash"], capture_output=True, text=True)
        return result.stdout.strip()

    def update_status(self, status: str):
        """Update agent sync board"""
        subprocess.run(
            [
                "python",
                "scripts/multi_agent_sync.py",
                "update-status",
                self.agent_name,
                status,
                "--context-hash",
                self.get_context_hash(),
            ]
        )

    def get_instructions(self):
        """Get instructions from handoff"""
        return self.instructions


# Auto-execute when imported
_codex_session = CodexSession()


# Export convenience functions
def create_handoff(summary, instructions, test_results="Tests passed"):
    """Quick handoff creation"""
    return _codex_session.create_handoff(summary, instructions, test_results)


def get_context_hash():
    """Get context hash"""
    return _codex_session.get_context_hash()


def get_instructions():
    """Get current instructions"""
    return _codex_session.get_instructions()


def update_status(status):
    """Update status"""
    return _codex_session.update_status(status)


# If running directly
if __name__ == "__main__":
    print("\n[OK] Codex session initialized!")
    print("\nAvailable functions:")
    print("  - create_handoff(summary, instructions)")
    print("  - get_context_hash()")
    print("  - get_instructions()")
    print("  - update_status(status)")

    if _codex_session.instructions:
        print("\n[TASK] Current Task:")
        print(_codex_session.instructions)
