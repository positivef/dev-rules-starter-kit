#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate existing Obsidian devlog files to new date folder structure

Phase C: Consolidate scattered files into date folders with topic grouping
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Import from auto_sync_obsidian
sys.path.insert(0, str(Path(__file__).parent))
from auto_sync_obsidian import extract_topic_from_commit


def scan_existing_files(devlog_dir: Path) -> List[Path]:
    """Scan for existing devlog files (not in date folders)

    Returns:
        List of file paths to migrate
    """
    files = []

    if not devlog_dir.exists():
        return files

    for item in devlog_dir.iterdir():
        # Skip date folders (YYYY-MM-DD format)
        if item.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", item.name):
            continue

        # Skip MOC file
        if item.name.endswith("-MOC.md"):
            continue

        # Include markdown files with date prefix
        if item.is_file() and item.suffix == ".md":
            if re.match(r"\d{4}-\d{2}-\d{2}", item.name):
                files.append(item)

    return files


def parse_filename(filename: str) -> Tuple[str, str]:
    """Parse filename to extract date and topic

    Examples:
        "2025-10-31_test-add-Q1-2026-test-infrastructure.md"
        -> ("2025-10-31", "test-add-Q1-2026-test-infrastructure")
    """
    # Remove .md extension
    name = filename.replace(".md", "")

    # Extract date (YYYY-MM-DD)
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    if not date_match:
        return None, None

    date = date_match.group(1)

    # Extract rest as title
    rest = name[len(date) :].lstrip("_-")

    return date, rest


def extract_topic_from_filename(title: str) -> str:
    """Extract topic from old filename format

    Uses same logic as extract_topic_from_commit but adapted for filenames
    """
    # Simulate as commit message for consistency
    commit_msg = title.replace("-", " ")

    return extract_topic_from_commit(commit_msg)


def group_files_by_date_and_topic(files: List[Path]) -> Dict[Tuple[str, str], List[Path]]:
    """Group files by (date, topic)

    Returns:
        {(date, topic): [file1, file2, ...]}
    """
    groups = defaultdict(list)

    for file in files:
        date, title = parse_filename(file.name)

        if not date:
            print(f"[SKIP] Cannot parse date from: {file.name}")
            continue

        topic = extract_topic_from_filename(title)

        groups[(date, topic)].append(file)

    return groups


def extract_time_from_content(content: str) -> str:
    """Try to extract time from content, or use default"""
    # Look for timestamp patterns
    # Common patterns in devlog: "커밋 해시", "작업 시간", etc.

    # Default to unknown time
    return "00:00"


def consolidate_files(vault_path: Path, groups: Dict[Tuple[str, str], List[Path]], dry_run: bool = False) -> None:
    """Consolidate grouped files into new structure

    Args:
        vault_path: Path to Obsidian vault
        groups: Grouped files by (date, topic)
        dry_run: If True, only show what would be done
    """
    devlog_dir = vault_path / "개발일지"
    backup_dir = vault_path / "개발일지" / "_backup_old_structure"

    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    for (date, topic), files in sorted(groups.items()):
        print(f"\n[GROUP] {date} / {topic}")
        print(f"  Files to consolidate: {len(files)}")

        # Create date folder
        date_folder = devlog_dir / date

        if not dry_run:
            date_folder.mkdir(parents=True, exist_ok=True)

        # Target file
        target_file = date_folder / f"{topic}.md"

        # Sort files by name (chronological order usually)
        sorted_files = sorted(files, key=lambda f: f.name)

        if dry_run:
            print(f"  Would create: {target_file.relative_to(vault_path)}")
            for f in sorted_files:
                print(f"    <- {f.name}")
        else:
            # Check if target already exists
            if target_file.exists():
                print("  [EXISTS] Target file already exists, appending...")
                consolidated_content = target_file.read_text(encoding="utf-8")
            else:
                print("  [CREATE] Creating new consolidated file...")
                # Use first file's content as base
                first_content = sorted_files[0].read_text(encoding="utf-8")
                consolidated_content = first_content

                # Move first file to backup
                backup_file = backup_dir / sorted_files[0].name
                sorted_files[0].rename(backup_file)
                print(f"    [BACKUP] {sorted_files[0].name}")

                sorted_files = sorted_files[1:]

            # Append remaining files
            for file in sorted_files:
                content = file.read_text(encoding="utf-8")

                # Add separator and content
                consolidated_content += f"\n\n---\n\n{content}"

                # Move to backup
                backup_file = backup_dir / file.name
                file.rename(backup_file)
                print(f"    [BACKUP] {file.name}")

            # Write consolidated file
            target_file.write_text(consolidated_content, encoding="utf-8")
            print(f"  [DONE] Consolidated {len(files)} files into {topic}.md")


def main():
    """Main execution"""
    # Load environment
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")

    if not obsidian_path:
        print("[ERROR] OBSIDIAN_VAULT_PATH not set")
        return 1

    vault_path = Path(obsidian_path)
    devlog_dir = vault_path / "개발일지"

    if not devlog_dir.exists():
        print(f"[ERROR] Devlog directory not found: {devlog_dir}")
        return 1

    # Scan existing files
    print("[SCAN] Scanning existing devlog files...")
    files = scan_existing_files(devlog_dir)
    print(f"[FOUND] {len(files)} files to potentially migrate")

    if not files:
        print("[INFO] No files to migrate")
        return 0

    # Group by date and topic
    print("\n[GROUP] Grouping files by date and topic...")
    groups = group_files_by_date_and_topic(files)
    print(f"[GROUPS] {len(groups)} groups found")

    # Show groups
    print("\n[PREVIEW] Migration plan:")
    for (date, topic), file_list in sorted(groups.items()):
        print(f"  {date}/{topic}.md ← {len(file_list)} files")

    # Ask for confirmation
    dry_run = "--dry-run" in sys.argv
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv

    if dry_run:
        print("\n[DRY-RUN] Would perform above migrations")
        consolidate_files(vault_path, groups, dry_run=True)
    elif auto_yes:
        print("\n[MIGRATE] Starting migration (auto-confirmed)...")
        consolidate_files(vault_path, groups, dry_run=False)
        print("\n[SUCCESS] Migration completed!")
        print("[BACKUP] Old files backed up to: 개발일지/_backup_old_structure/")
    else:
        response = input("\n[CONFIRM] Proceed with migration? (yes/no): ")
        if response.lower() in ["yes", "y"]:
            print("\n[MIGRATE] Starting migration...")
            consolidate_files(vault_path, groups, dry_run=False)
            print("\n[SUCCESS] Migration completed!")
            print("[BACKUP] Old files backed up to: 개발일지/_backup_old_structure/")
        else:
            print("[CANCELLED] Migration cancelled")

    return 0


if __name__ == "__main__":
    sys.exit(main())
