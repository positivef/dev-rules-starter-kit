#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze commit message quality

Provides educational feedback on commit message quality after committing.
Can be called from post-commit hook or run manually.
"""

import subprocess
import sys
import re
from pathlib import Path


def get_last_commit_message() -> str:
    """Get the last commit message"""
    result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()


def analyze_message(message: str) -> dict:
    """Analyze message using prompt feedback system"""
    script_dir = Path(__file__).parent

    result = subprocess.run(
        ["python", str(script_dir / "prompt_feedback_cli.py"), message, "--format", "brief"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )

    if result.returncode == 0 and result.stdout:
        # Parse score
        score_match = re.search(r"Score:\s*(\d+)/100", result.stdout)
        clarity_match = re.search(r"Clarity:\s*(\d+)/100", result.stdout)

        return {
            "success": True,
            "overall_score": int(score_match.group(1)) if score_match else 0,
            "clarity_score": int(clarity_match.group(1)) if clarity_match else 0,
            "output": result.stdout,
        }

    return {"success": False}


def print_feedback(analysis: dict):
    """Print educational feedback"""
    if not analysis.get("success"):
        return

    score = analysis["overall_score"]

    print("\n" + "=" * 60)
    print("Commit Message Quality Analysis")
    print("=" * 60)
    print(f"Overall Score: {score}/100", end="")

    if score >= 85:
        print(" - Excellent!")
        print("\nYour commit message is clear, specific, and contextual.")
    elif score >= 70:
        print(" - Good")
        print("\nYour commit message is clear and provides adequate context.")
    elif score >= 55:
        print(" - Acceptable")
        print("\nConsider adding more context about WHY the change was made.")
    else:
        print(" - Needs Improvement")
        print("\nTips for better commit messages:")
        print("  - Be specific about what changed")
        print("  - Explain WHY, not just WHAT")
        print("  - Include relevant file paths or function names")
        print("  - Use conventional commit format (feat:, fix:, docs:, etc.)")

    print("\nUse '/improve-prompt' command in Claude Code for suggestions.")
    print("=" * 60 + "\n")


def main():
    """Main execution"""
    # Get commit message
    message = get_last_commit_message()

    # Skip for merge/revert commits or very short messages
    if message.startswith(("Merge ", "Revert ")) or len(message) < 10:
        return 0

    # Analyze
    analysis = analyze_message(message)

    # Print feedback
    print_feedback(analysis)

    return 0


if __name__ == "__main__":
    sys.exit(main())
