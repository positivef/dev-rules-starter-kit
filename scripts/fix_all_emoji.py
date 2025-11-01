#!/usr/bin/env python3
"""Fix all emoji in Python files for Windows UTF-8 compliance (P10)"""

from pathlib import Path

# Emoji replacement mapping
EMOJI_REPLACEMENTS = {
    "✅": "[OK]",
    "❌": "[FAIL]",
    "⚠️": "[WARN]",
    "🚀": "[DEPLOY]",
    "📝": "[LOG]",
    "🔍": "[INFO]",
    "📄": "[INFO]",
    "🔄": "[SYNC]",
    "📊": "[STATUS]",
    "📚": "[HELP]",
    "🎯": "[TASK]",
    "🔥": "[CRITICAL]",
    "💡": "[TIP]",
    "⏰": "[TIME]",
    "✨": "[SUCCESS]",
    "🐛": "[BUG]",
    "🎉": "[COMPLETE]",
}


def fix_emoji_in_file(file_path: Path) -> int:
    """Replace all emoji in a file with ASCII alternatives"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        count = 0

        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                count += content.count(replacement) - original.count(replacement)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return count

        return 0
    except Exception as e:
        print(f"[ERROR] Failed to fix {file_path}: {e}")
        return 0


def main():
    """Fix all Python files in scripts directory"""
    scripts_dir = Path("scripts")
    total_fixed = 0
    files_fixed = 0

    print("[INFO] Fixing emoji in Python files...")
    print("=" * 60)

    for py_file in scripts_dir.glob("*.py"):
        if py_file.name == "fix_all_emoji.py":
            continue  # Skip self

        count = fix_emoji_in_file(py_file)
        if count > 0:
            print(f"[OK] {py_file.name}: {count} emoji replaced")
            total_fixed += count
            files_fixed += 1

    print("=" * 60)
    print(f"[COMPLETE] {total_fixed} emoji fixed in {files_fixed} files")

    return 0 if total_fixed > 0 else 1


if __name__ == "__main__":
    exit(main())
