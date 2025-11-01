#!/usr/bin/env python3
"""
Install Git hooks for automatic AI Agent Handoff
Ensures Constitution compliance through automation
"""

import os
import sys
import stat
from pathlib import Path


def create_pre_push_hook():
    """Create pre-push hook for automatic handoff generation"""
    hook_content = '''#!/usr/bin/env python3
"""
Pre-push hook: Automatic AI Agent Handoff Generation
Constitution Articles: P1, P2, P3, P7
"""

import subprocess
import sys
import os
from datetime import datetime

def main():
    print("=" * 50)
    print("AI AGENT HANDOFF PROTOCOL - PRE-PUSH HOOK")
    print("=" * 50)

    # Get agent name from git config or environment
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True
        )
        agent_name = result.stdout.strip() or "Unknown"
    except Exception:
        agent_name = os.getenv("AI_AGENT_NAME", "Unknown")

    print(f"Agent: {agent_name}")

    # Check for existing handoff report
    if not os.path.exists("HANDOFF_REPORT.md"):
        print("[WARNING] No HANDOFF_REPORT.md found")
        response = input("Create handoff report now? (y/n): ")

        if response.lower() == 'y':
            # Get last commit message for summary
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True, text=True
            )
            summary = result.stdout.strip()

            # Run tests
            print("Running tests...")
            test_result = subprocess.run(
                ["pytest", "tests/", "-q"],
                capture_output=True, text=True
            )
            test_status = "passed" if test_result.returncode == 0 else "failed"

            # Create handoff
            print("Generating handoff report...")
            subprocess.run([
                "python", "scripts/create_handoff_report.py",
                "--author", agent_name,
                "--summary", summary or "Work completed",
                "--test-results", f"Tests {test_status}",
                "--instructions", "Review and continue development"
            ])

            print("[OK] Handoff report generated")
        else:
            print("[SKIP] Push without handoff report")

    else:
        # Check if report is recent (within last hour)
        import time
        file_age = time.time() - os.path.getmtime("HANDOFF_REPORT.md")
        if file_age > 3600:  # 1 hour
            print(f"[WARNING] HANDOFF_REPORT.md is {int(file_age/3600)} hours old")
            print("Consider regenerating with latest changes")

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    return hook_content


def create_post_commit_hook():
    """Create post-commit hook for context synchronization"""
    hook_content = '''#!/usr/bin/env python3
"""
Post-commit hook: Update Agent Sync Board
"""

import subprocess
import os

def main():
    # Get agent name
    result = subprocess.run(
        ["git", "config", "user.name"],
        capture_output=True, text=True
    )
    agent_name = result.stdout.strip() or "Unknown"

    # Get commit hash
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True
    )
    commit_hash = result.stdout.strip()

    # Get context hash
    result = subprocess.run(
        ["python", "scripts/context_provider.py", "print-hash"],
        capture_output=True, text=True
    )
    context_hash = result.stdout.strip()

    # Update sync board
    subprocess.run([
        "python", "scripts/multi_agent_sync.py",
        "update-status", agent_name,
        f"Committed {commit_hash}",
        "--context-hash", context_hash
    ], capture_output=True)

    print(f"[SYNC] Agent board updated: {agent_name} @ {commit_hash[:8]}")
    return 0

if __name__ == "__main__":
    main()
'''
    return hook_content


def create_pre_commit_hook():
    """Create pre-commit hook for validation"""
    hook_content = '''#!/usr/bin/env python3
"""
Pre-commit hook: Validate handoff requirements
"""

import subprocess
import sys

def main():
    # Check for Constitution compliance
    print("[VALIDATE] Checking Constitution compliance...")

    # Run pre-execution guard
    result = subprocess.run(
        ["python", "scripts/pre_execution_guard.py"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("[ERROR] Pre-execution guard failed")
        print(result.stdout)
        return 1

    print("[OK] All checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    return hook_content


def install_hooks():
    """Install all Git hooks for Handoff Protocol"""
    git_dir = Path(".git")
    if not git_dir.exists():
        print("[ERROR] Not in a git repository")
        return False

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hooks = {
        "pre-push": create_pre_push_hook(),
        "post-commit": create_post_commit_hook(),
        "pre-commit": create_pre_commit_hook(),
    }

    for hook_name, hook_content in hooks.items():
        hook_path = hooks_dir / hook_name

        # Backup existing hook if it exists
        if hook_path.exists():
            backup_path = hooks_dir / f"{hook_name}.backup"
            hook_path.rename(backup_path)
            print(f"[BACKUP] Existing {hook_name} hook backed up to {backup_path}")

        # Write new hook
        hook_path.write_text(hook_content, encoding="utf-8")

        # Make executable (Unix-like systems)
        if os.name != "nt":  # Not Windows
            st = hook_path.stat()
            hook_path.chmod(st.st_mode | stat.S_IEXEC)

        print(f"[OK] Installed {hook_name} hook")

    return True


def uninstall_hooks():
    """Remove installed hooks and restore backups"""
    git_dir = Path(".git")
    if not git_dir.exists():
        print("[ERROR] Not in a git repository")
        return False

    hooks_dir = git_dir / "hooks"
    hook_names = ["pre-push", "post-commit", "pre-commit"]

    for hook_name in hook_names:
        hook_path = hooks_dir / hook_name
        backup_path = hooks_dir / f"{hook_name}.backup"

        if hook_path.exists():
            hook_path.unlink()
            print(f"[OK] Removed {hook_name} hook")

        if backup_path.exists():
            backup_path.rename(hook_path)
            print(f"[OK] Restored original {hook_name} hook")

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Install/Uninstall Git hooks for AI Agent Handoff Protocol")
    parser.add_argument("action", choices=["install", "uninstall"], help="Action to perform")
    parser.add_argument("--force", action="store_true", help="Force installation even if hooks exist")

    args = parser.parse_args()

    if args.action == "install":
        success = install_hooks()
        if success:
            print("\n" + "=" * 50)
            print("GIT HOOKS INSTALLED SUCCESSFULLY")
            print("=" * 50)
            print("\nHandoff Protocol hooks are now active:")
            print("- pre-commit: Validates Constitution compliance")
            print("- post-commit: Updates agent sync board")
            print("- pre-push: Generates handoff report if needed")
            print("\nTo test: git commit -m 'test' && git push")
    else:
        success = uninstall_hooks()
        if success:
            print("\n[OK] Git hooks uninstalled")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
