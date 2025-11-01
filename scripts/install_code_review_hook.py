#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install Code Review Assistant Git Hook

Installs pre-push hook to automatically review code before pushing.

Usage:
  python scripts/install_code_review_hook.py         # Install
  python scripts/install_code_review_hook.py --check # Check installation
  python scripts/install_code_review_hook.py --uninstall # Remove hook
"""

import sys
import os
import stat
from pathlib import Path


def get_git_hooks_dir() -> Path:
    """Get .git/hooks directory"""
    repo_root = Path(__file__).parent.parent
    hooks_dir = repo_root / ".git" / "hooks"

    if not hooks_dir.exists():
        raise RuntimeError("Not a git repository or .git/hooks not found")

    return hooks_dir


def install_pre_push_hook() -> bool:
    """Install pre-push hook for code review"""
    try:
        hooks_dir = get_git_hooks_dir()
        pre_push = hooks_dir / "pre-push"

        hook_content = """#!/bin/sh
# Code Review Assistant - Pre-push Hook
# Reviews code quality before pushing to remote

echo "Running AI Code Review..."

# Get the range of commits to push
while read local_ref local_sha remote_ref remote_sha
do
    if [ "$local_sha" != "0000000000000000000000000000000000000000" ]; then
        # Run code review on commits being pushed
        python scripts/code_review_assistant.py --commit "$local_sha" --quiet

        if [ $? -ne 0 ]; then
            echo ""
            echo "[ERROR] Code review failed. Issues must be addressed before pushing."
            echo "Run 'python scripts/code_review_assistant.py' for details."
            exit 1
        fi
    fi
done

echo "[SUCCESS] Code review passed!"
exit 0
"""

        # Write hook
        pre_push.write_text(hook_content, encoding="utf-8")

        # Make executable (Unix/Linux/Mac)
        if os.name != "nt":
            st = os.stat(pre_push)
            os.chmod(pre_push, st.st_mode | stat.S_IEXEC)

        print(f"[SUCCESS] Code review hook installed: {pre_push}")
        return True

    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
        return False


def check_installation() -> bool:
    """Check if code review hook is installed"""
    try:
        hooks_dir = get_git_hooks_dir()
        pre_push = hooks_dir / "pre-push"

        if not pre_push.exists():
            print("[NOT INSTALLED] pre-push hook not found")
            return False

        content = pre_push.read_text(encoding="utf-8")
        if "code_review_assistant.py" in content:
            print("[OK] Code review hook is installed")
            return True
        else:
            print("[NOT INSTALLED] pre-push exists but code review not configured")
            return False

    except Exception as e:
        print(f"[ERROR] Check failed: {e}")
        return False


def uninstall_hook() -> bool:
    """Remove code review hook"""
    try:
        hooks_dir = get_git_hooks_dir()
        pre_push = hooks_dir / "pre-push"

        if pre_push.exists():
            content = pre_push.read_text(encoding="utf-8")
            if "code_review_assistant.py" in content:
                pre_push.unlink()
                print("[SUCCESS] Code review hook removed")
            else:
                print("[INFO] Hook exists but not our code review hook")
        else:
            print("[INFO] No pre-push hook to remove")

        return True

    except Exception as e:
        print(f"[ERROR] Uninstallation failed: {e}")
        return False


def main():
    """Main execution"""
    args = sys.argv[1:]

    if "--check" in args:
        return 0 if check_installation() else 1

    if "--uninstall" in args:
        return 0 if uninstall_hook() else 1

    # Default: install
    print("Installing Code Review Assistant Hook...")
    print("=" * 50)

    success = install_pre_push_hook()

    if success:
        print("\n" + "=" * 50)
        print("[SUCCESS] Installation complete!")
        print("\nThe code review will run automatically before each push.")
        print("To test manually: python scripts/code_review_assistant.py")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
