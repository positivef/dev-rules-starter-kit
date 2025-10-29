"""Evidence File Cleaner - Manage excessive evidence accumulation.

This solves the 31,000+ evidence files problem. Instead of keeping
everything forever, we maintain only recent and important evidence.
"""

import argparse
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EvidenceCleaner:
    """Clean up excessive evidence files intelligently."""

    # Evidence retention policies
    RETENTION_DAYS = {
        "critical": 30,  # Keep critical evidence for 30 days
        "normal": 7,  # Keep normal evidence for 7 days
        "verbose": 1,  # Keep verbose/debug evidence for 1 day
    }

    # File patterns to identify evidence types
    EVIDENCE_PATTERNS = {
        "evidence": "evidence_*",
        "test_results": "*_test_results_*",
        "coverage": "*_coverage_*",
        "trace": "*_trace_*",
        "debug": "*_debug_*",
        "log": "*.log",
    }

    def __init__(self, evidence_dirs: Optional[List[Path]] = None):
        """Initialize evidence cleaner.

        Args:
            evidence_dirs: Directories containing evidence files.
        """
        self.evidence_dirs = evidence_dirs or [
            Path("evidence"),
            Path("test_evidence"),
            Path("coverage_reports"),
            Path(".evidence_cache"),
        ]
        self.stats: Dict[str, int] = {
            "files_found": 0,
            "files_deleted": 0,
            "space_freed_mb": 0,
            "files_kept": 0,
        }

    def scan_evidence_files(self) -> Dict[str, List[Path]]:
        """Scan for evidence files across all directories.

        Returns:
            Dictionary of evidence type to file paths.
        """
        evidence_files: Dict[str, List[Path]] = {
            "critical": [],
            "normal": [],
            "verbose": [],
        }

        for evidence_dir in self.evidence_dirs:
            if not evidence_dir.exists():
                continue

            for pattern_name, pattern in self.EVIDENCE_PATTERNS.items():
                for file_path in evidence_dir.glob(pattern):
                    if file_path.is_file():
                        self.stats["files_found"] += 1
                        category = self._categorize_file(file_path, pattern_name)
                        evidence_files[category].append(file_path)

        return evidence_files

    def _categorize_file(self, file_path: Path, pattern_name: str) -> str:
        """Categorize evidence file by importance.

        Args:
            file_path: Path to evidence file.
            pattern_name: Pattern that matched.

        Returns:
            Category: 'critical', 'normal', or 'verbose'.
        """
        # Critical: Test failures, coverage drops
        if "FAIL" in file_path.name or "ERROR" in file_path.name:
            return "critical"

        if pattern_name in ["coverage"] and self._is_coverage_drop(file_path):
            return "critical"

        # Verbose: Debug, trace, detailed logs
        if pattern_name in ["debug", "trace", "log"]:
            return "verbose"

        # Normal: Everything else
        return "normal"

    def _is_coverage_drop(self, file_path: Path) -> bool:
        """Check if coverage file shows a drop.

        Args:
            file_path: Path to coverage file.

        Returns:
            True if coverage dropped.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Simple heuristic: check for coverage below 80%
                if "coverage" in content.lower():
                    import re

                    match = re.search(r"(\d+(?:\.\d+)?)\s*%", content)
                    if match:
                        coverage = float(match.group(1))
                        return coverage < 80.0
        except Exception:
            pass
        return False

    def clean_by_age(self, dry_run: bool = True) -> Tuple[int, float]:
        """Clean evidence files based on retention policy.

        Args:
            dry_run: If True, only show what would be deleted.

        Returns:
            Tuple of (files_deleted, space_freed_mb).
        """
        evidence_files = self.scan_evidence_files()
        now = datetime.now()
        files_to_delete: List[Path] = []
        total_size = 0

        for category, files in evidence_files.items():
            retention_days = self.RETENTION_DAYS[category]
            cutoff_date = now - timedelta(days=retention_days)

            for file_path in files:
                try:
                    # Check file age
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        files_to_delete.append(file_path)
                        total_size += file_path.stat().st_size
                    else:
                        self.stats["files_kept"] += 1

                except Exception as e:
                    print(f"[WARN] Could not check {file_path}: {e}")

        # Delete or report
        if dry_run:
            print(f"\n[DRY RUN] Would delete {len(files_to_delete)} files")
            print(f"[DRY RUN] Would free {total_size / (1024*1024):.1f} MB")

            # Show sample of files to be deleted
            if files_to_delete:
                print("\n[DRY RUN] Sample files to delete:")
                for file in files_to_delete[:10]:
                    age_days = (now - datetime.fromtimestamp(file.stat().st_mtime)).days
                    print(f"  - {file.name} (age: {age_days} days)")
                if len(files_to_delete) > 10:
                    print(f"  ... and {len(files_to_delete) - 10} more files")
        else:
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    self.stats["files_deleted"] += 1
                except Exception as e:
                    print(f"[ERROR] Could not delete {file_path}: {e}")

        self.stats["space_freed_mb"] = total_size / (1024 * 1024)
        return len(files_to_delete), self.stats["space_freed_mb"]

    def clean_by_limit(self, max_files: int = 100, dry_run: bool = True) -> Tuple[int, float]:
        """Keep only the most recent N files.

        Args:
            max_files: Maximum number of files to keep.
            dry_run: If True, only show what would be deleted.

        Returns:
            Tuple of (files_deleted, space_freed_mb).
        """
        all_files: List[Tuple[Path, float]] = []

        # Collect all evidence files with timestamps
        for evidence_dir in self.evidence_dirs:
            if not evidence_dir.exists():
                continue

            for pattern in self.EVIDENCE_PATTERNS.values():
                for file_path in evidence_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            mtime = file_path.stat().st_mtime
                            all_files.append((file_path, mtime))
                        except Exception:
                            pass

        # Sort by modification time (newest first)
        all_files.sort(key=lambda x: x[1], reverse=True)

        # Determine files to delete
        files_to_keep = all_files[:max_files]
        files_to_delete = all_files[max_files:]

        total_size = sum(f[0].stat().st_size for f in files_to_delete if f[0].exists())

        if dry_run:
            print(f"\n[DRY RUN] Would keep {len(files_to_keep)} most recent files")
            print(f"[DRY RUN] Would delete {len(files_to_delete)} older files")
            print(f"[DRY RUN] Would free {total_size / (1024*1024):.1f} MB")
        else:
            for file_path, _ in files_to_delete:
                try:
                    file_path.unlink()
                    self.stats["files_deleted"] += 1
                except Exception as e:
                    print(f"[ERROR] Could not delete {file_path}: {e}")

        self.stats["space_freed_mb"] = total_size / (1024 * 1024)
        return len(files_to_delete), self.stats["space_freed_mb"]

    def archive_old_evidence(self, archive_dir: Path, days_old: int = 7) -> int:
        """Archive old evidence files instead of deleting.

        Args:
            archive_dir: Directory to move old files to.
            days_old: Files older than this are archived.

        Returns:
            Number of files archived.
        """
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived = 0
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_old)

        for evidence_dir in self.evidence_dirs:
            if not evidence_dir.exists():
                continue

            for pattern in self.EVIDENCE_PATTERNS.values():
                for file_path in evidence_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if mtime < cutoff_date:
                                # Create archive subdirectory by date
                                date_dir = archive_dir / mtime.strftime("%Y-%m-%d")
                                date_dir.mkdir(exist_ok=True)

                                # Move file to archive
                                dest = date_dir / file_path.name
                                shutil.move(str(file_path), str(dest))
                                archived += 1

                        except Exception as e:
                            print(f"[ERROR] Could not archive {file_path}: {e}")

        print(f"[INFO] Archived {archived} files to {archive_dir}")
        return archived

    def show_statistics(self) -> None:
        """Display cleaning statistics."""
        print("\n" + "=" * 60)
        print("Evidence Cleaning Statistics")
        print("=" * 60)
        print(f"Files found: {self.stats['files_found']}")
        print(f"Files kept: {self.stats['files_kept']}")
        print(f"Files deleted: {self.stats['files_deleted']}")
        print(f"Space freed: {self.stats['space_freed_mb']:.1f} MB")

        # Show directory sizes
        print("\nEvidence Directory Sizes:")
        for evidence_dir in self.evidence_dirs:
            if evidence_dir.exists():
                size = sum(f.stat().st_size for f in evidence_dir.rglob("*") if f.is_file())
                count = len(list(evidence_dir.rglob("*")))
                print(f"  {evidence_dir}: {count} files, {size / (1024*1024):.1f} MB")

    def create_retention_config(self) -> None:
        """Create a retention configuration file."""
        config = {
            "retention_policies": self.RETENTION_DAYS,
            "evidence_directories": [str(d) for d in self.evidence_dirs],
            "max_files_limit": 100,
            "archive_after_days": 7,
            "auto_clean_enabled": False,
        }

        config_path = Path("config/evidence_retention.json")
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"[INFO] Created retention config: {config_path}")


def main():
    """CLI for evidence cleaning."""
    parser = argparse.ArgumentParser(description="Clean up excessive evidence files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--by-age", action="store_true", help="Clean files based on age/retention policy")
    parser.add_argument("--by-limit", type=int, metavar="N", help="Keep only N most recent files")
    parser.add_argument("--archive", type=str, metavar="DIR", help="Archive old files to directory instead of deleting")
    parser.add_argument("--create-config", action="store_true", help="Create retention configuration file")

    args = parser.parse_args()

    cleaner = EvidenceCleaner()

    if args.create_config:
        cleaner.create_retention_config()
        return

    if args.archive:
        archived = cleaner.archive_old_evidence(Path(args.archive))
        print(f"[SUCCESS] Archived {archived} files")

    elif args.by_age:
        deleted, freed = cleaner.clean_by_age(dry_run=args.dry_run)
        if not args.dry_run:
            print(f"[SUCCESS] Deleted {deleted} files, freed {freed:.1f} MB")

    elif args.by_limit:
        deleted, freed = cleaner.clean_by_limit(max_files=args.by_limit, dry_run=args.dry_run)
        if not args.dry_run:
            print(f"[SUCCESS] Deleted {deleted} files, freed {freed:.1f} MB")

    else:
        # Default: show statistics
        evidence_files = cleaner.scan_evidence_files()
        total = sum(len(files) for files in evidence_files.values())
        print(f"\n[INFO] Found {total} evidence files")
        print(f"  Critical: {len(evidence_files['critical'])} files")
        print(f"  Normal: {len(evidence_files['normal'])} files")
        print(f"  Verbose: {len(evidence_files['verbose'])} files")

    cleaner.show_statistics()


if __name__ == "__main__":
    main()
