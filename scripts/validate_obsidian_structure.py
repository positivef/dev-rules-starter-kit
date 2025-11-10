#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate and Fix Obsidian Devlog Structure

Enforces OBSIDIAN_SYNC_RULES.md structure:
- CORRECT: 개발일지/YYYY-MM-DD/Topic.md
- WRONG: 개발일지/YYYY-MM-DD_Topic.md
- WRONG: 개발일지/Topic.md

Usage:
    python scripts/validate_obsidian_structure.py --check
    python scripts/validate_obsidian_structure.py --fix
    python scripts/validate_obsidian_structure.py --report
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import shutil


def get_vault_path() -> Path:
    """Get Obsidian vault path from environment"""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not vault_path:
        raise ValueError("OBSIDIAN_VAULT_PATH not set in .env")

    return Path(vault_path) / "개발일지"


def validate_structure(devlog_path: Path) -> Dict[str, List[Path]]:
    """Validate devlog structure and categorize files

    Returns:
        {
            "correct": [files in YYYY-MM-DD/Topic.md],
            "wrong_root": [files in root: YYYY-MM-DD_Topic.md],
            "wrong_no_date": [files without date folder],
            "old_backup": [files in _backup_old_structure]
        }
    """
    results = {"correct": [], "wrong_root": [], "wrong_no_date": [], "old_backup": []}

    if not devlog_path.exists():
        print(f"[ERROR] Devlog path not found: {devlog_path}")
        return results

    # Scan all markdown files
    for item in devlog_path.rglob("*.md"):
        relative = item.relative_to(devlog_path)
        parts = relative.parts

        # Skip backup folder
        if "_backup_old_structure" in parts:
            results["old_backup"].append(item)
            continue

        # Skip MOC file
        if item.name == "개발일지-MOC.md":
            results["correct"].append(item)
            continue

        # Check structure
        if len(parts) == 2:
            # Format: YYYY-MM-DD/Topic.md
            date_folder = parts[0]
            if re.match(r"\d{4}-\d{2}-\d{2}", date_folder):
                results["correct"].append(item)
            else:
                results["wrong_no_date"].append(item)
        elif len(parts) == 1:
            # Format: YYYY-MM-DD_Topic.md (wrong - in root)
            if re.match(r"\d{4}-\d{2}-\d{2}_", item.name):
                results["wrong_root"].append(item)
            else:
                results["wrong_no_date"].append(item)
        else:
            # Nested deeper than expected
            results["wrong_no_date"].append(item)

    return results


def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename like '2025-11-02_Topic.md'

    Returns:
        Date string (YYYY-MM-DD) or current date if not found
    """
    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return match.group(1)
    else:
        # Fallback to current date
        return datetime.now().strftime("%Y-%m-%d")


def fix_structure(devlog_path: Path, results: Dict[str, List[Path]], dry_run: bool = True) -> int:
    """Fix wrong structure by moving files to correct location

    Args:
        devlog_path: Root devlog directory
        results: Validation results from validate_structure()
        dry_run: If True, only print what would be done

    Returns:
        Number of files fixed
    """
    fixed_count = 0

    # Fix wrong_root files (YYYY-MM-DD_Topic.md → YYYY-MM-DD/Topic.md)
    for file_path in results["wrong_root"]:
        date_str = extract_date_from_filename(file_path.name)
        topic_name = file_path.name.replace(f"{date_str}_", "")

        # Create target directory
        target_dir = devlog_path / date_str
        target_path = target_dir / topic_name

        if dry_run:
            print("[DRY-RUN] Would move:")
            print(f"  FROM: {file_path.relative_to(devlog_path)}")
            print(f"  TO:   {target_path.relative_to(devlog_path)}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

            # Check if target already exists
            if target_path.exists():
                print(f"[SKIP] Target exists: {target_path.relative_to(devlog_path)}")
                # Backup to old structure
                backup_dir = devlog_path / "_backup_old_structure"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / file_path.name
                shutil.move(str(file_path), str(backup_path))
                print(f"[BACKUP] Moved to: {backup_path.relative_to(devlog_path)}")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"[FIXED] Moved to: {target_path.relative_to(devlog_path)}")

        fixed_count += 1

    # Fix wrong_no_date files (Topic.md → YYYY-MM-DD/Topic.md)
    for file_path in results["wrong_no_date"]:
        # Try to extract date from file content (YAML frontmatter)
        date_str = extract_date_from_yaml(file_path)
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        topic_name = file_path.name

        # Create target directory
        target_dir = devlog_path / date_str
        target_path = target_dir / topic_name

        if dry_run:
            print("[DRY-RUN] Would move:")
            print(f"  FROM: {file_path.relative_to(devlog_path)}")
            print(f"  TO:   {target_path.relative_to(devlog_path)}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

            if target_path.exists():
                print(f"[SKIP] Target exists: {target_path.relative_to(devlog_path)}")
                # Backup
                backup_dir = devlog_path / "_backup_old_structure"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / file_path.name
                shutil.move(str(file_path), str(backup_path))
                print(f"[BACKUP] Moved to: {backup_path.relative_to(devlog_path)}")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"[FIXED] Moved to: {target_path.relative_to(devlog_path)}")

        fixed_count += 1

    return fixed_count


def extract_date_from_yaml(file_path: Path) -> str:
    """Extract date from YAML frontmatter in markdown file

    Returns:
        Date string (YYYY-MM-DD) or empty string if not found
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        # Look for YAML frontmatter
        if content.startswith("---"):
            yaml_end = content.find("---", 3)
            if yaml_end > 0:
                yaml_section = content[3:yaml_end]
                # Extract date field
                match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", yaml_section)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"[WARN] Could not read {file_path.name}: {e}")

    return ""


def generate_report(results: Dict[str, List[Path]]) -> None:
    """Generate structure validation report"""
    total = sum(len(files) for files in results.values())

    print("\n" + "=" * 70)
    print("OBSIDIAN DEVLOG STRUCTURE VALIDATION REPORT")
    print("=" * 70)

    print(f"\nTotal files: {total}")
    print(f"  Correct structure: {len(results['correct'])} ({len(results['correct'])/total*100:.1f}%)")
    print(f"  Wrong (in root): {len(results['wrong_root'])}")
    print(f"  Wrong (no date): {len(results['wrong_no_date'])}")
    print(f"  Old backup: {len(results['old_backup'])}")

    if results["wrong_root"]:
        print("\n[ISSUE] Files in root (should be in date folder):")
        for f in results["wrong_root"][:5]:
            print(f"  - {f.name}")
        if len(results["wrong_root"]) > 5:
            print(f"  ... and {len(results['wrong_root']) - 5} more")

    if results["wrong_no_date"]:
        print("\n[ISSUE] Files without date folder:")
        for f in results["wrong_no_date"][:5]:
            print(f"  - {f.name}")
        if len(results["wrong_no_date"]) > 5:
            print(f"  ... and {len(results['wrong_no_date']) - 5} more")

    if results["correct"]:
        print(f"\n[OK] {len(results['correct'])} files follow correct structure")

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if results["wrong_root"] or results["wrong_no_date"]:
        print("\n1. Run with --fix to automatically fix structure:")
        print("   python scripts/validate_obsidian_structure.py --fix")
        print("\n2. Files will be moved to correct date folders")
        print("3. Duplicates will be backed up to _backup_old_structure/")
    else:
        print("\n[SUCCESS] All files follow correct structure!")
        print("No action needed.")

    print("\n")


def main():
    """Main execution"""
    import sys

    # Parse arguments
    check_only = "--check" in sys.argv
    fix_mode = "--fix" in sys.argv
    report_mode = "--report" in sys.argv
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv

    if not (check_only or fix_mode or report_mode):
        # Default to report
        report_mode = True

    try:
        devlog_path = get_vault_path()
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("Set OBSIDIAN_VAULT_PATH in .env file")
        return 1

    print(f"[INFO] Validating Obsidian devlog structure: {devlog_path}")

    # Validate structure
    results = validate_structure(devlog_path)

    if report_mode or check_only:
        generate_report(results)

    if fix_mode:
        print("\n[FIX MODE] Fixing structure violations...")

        if not auto_yes:
            print("Running in DRY-RUN mode first...\n")
            # Dry run first
            fix_structure(devlog_path, results, dry_run=True)
            print("\n" + "=" * 70)
            print("Use --yes to skip confirmation")
            return 0

        print("\n[EXECUTING] Fixing structure...\n")
        fixed = fix_structure(devlog_path, results, dry_run=False)
        print(f"\n[SUCCESS] Fixed {fixed} files")

    # Return exit code
    if results["wrong_root"] or results["wrong_no_date"]:
        return 1  # Structure violations found
    else:
        return 0  # All correct


if __name__ == "__main__":
    import sys

    sys.exit(main())
