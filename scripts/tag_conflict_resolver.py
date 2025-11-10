"""Tag Conflict Resolver - Detect and resolve tag conflicts between dev-rules and Obsidian.

Features:
- Detect conflicts between YAML task tags and Obsidian note tags
- Three merge strategies: keep-both, prefer-local, prefer-remote
- Interactive conflict resolution UI
- Conflict logging for evidence (P2)

Compliance:
- P2: Evidence-Based (logs to RUNS/tag-conflicts/)
- P8: Test-First (unit tests required)
- P10: Windows UTF-8 (no emojis in code)

Usage:
    from tag_conflict_resolver import TagConflictResolver

    resolver = TagConflictResolver()
    conflicts = resolver.detect_conflicts(dev_tags, obs_tags)
    resolved = resolver.resolve_conflict(conflict, strategy="keep-both")
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Set, Literal


StrategyType = Literal["keep-both", "prefer-local", "prefer-remote"]


@dataclass
class TagConflict:
    """Represents a tag conflict between dev-rules and Obsidian.

    Attributes:
        file_path: Path to the file with conflict
        dev_tags: Tags from dev-rules YAML
        obsidian_tags: Tags from Obsidian note
        conflict_type: Type of conflict (missing, extra, mismatch)
    """

    file_path: str
    dev_tags: Set[str]
    obsidian_tags: Set[str]
    conflict_type: str

    def __post_init__(self):
        """Convert sets to sorted lists for JSON serialization."""
        if isinstance(self.dev_tags, set):
            self.dev_tags = sorted(list(self.dev_tags))
        if isinstance(self.obsidian_tags, set):
            self.obsidian_tags = sorted(list(self.obsidian_tags))


@dataclass
class ResolvedTags:
    """Result of conflict resolution.

    Attributes:
        merged_tags: Final set of tags after resolution
        strategy_used: Strategy that was applied
        changes_made: Description of what changed
    """

    merged_tags: Set[str]
    strategy_used: str
    changes_made: str

    def __post_init__(self):
        """Convert set to sorted list for JSON serialization."""
        if isinstance(self.merged_tags, set):
            self.merged_tags = sorted(list(self.merged_tags))


class TagConflictResolver:
    """Detect and resolve tag conflicts between dev-rules and Obsidian."""

    def __init__(self, conflict_log_dir: Path = None):
        """Initialize resolver.

        Args:
            conflict_log_dir: Directory to log conflicts (default: RUNS/tag-conflicts/)
        """
        self.conflict_log_dir = conflict_log_dir or Path("RUNS/tag-conflicts")
        self.conflict_log_dir.mkdir(parents=True, exist_ok=True)

    def detect_conflicts(self, dev_tags: Set[str], obsidian_tags: Set[str], file_path: str = "unknown") -> List[TagConflict]:
        """Detect tag conflicts between dev-rules and Obsidian.

        Args:
            dev_tags: Tags from dev-rules YAML
            obsidian_tags: Tags from Obsidian note
            file_path: Path to file being checked

        Returns:
            List of detected conflicts (empty if no conflicts)
        """
        conflicts = []

        # Check for missing tags (in dev but not in obsidian)
        missing_in_obsidian = dev_tags - obsidian_tags
        if missing_in_obsidian:
            conflicts.append(
                TagConflict(
                    file_path=file_path, dev_tags=dev_tags, obsidian_tags=obsidian_tags, conflict_type="missing_in_obsidian"
                )
            )

        # Check for extra tags (in obsidian but not in dev)
        extra_in_obsidian = obsidian_tags - dev_tags
        if extra_in_obsidian:
            conflicts.append(
                TagConflict(
                    file_path=file_path, dev_tags=dev_tags, obsidian_tags=obsidian_tags, conflict_type="extra_in_obsidian"
                )
            )

        # If both missing and extra, it's a mismatch
        if missing_in_obsidian and extra_in_obsidian:
            # Replace previous conflicts with single mismatch
            conflicts = [
                TagConflict(file_path=file_path, dev_tags=dev_tags, obsidian_tags=obsidian_tags, conflict_type="mismatch")
            ]

        return conflicts

    def resolve_conflict(self, conflict: TagConflict, strategy: StrategyType = "keep-both") -> ResolvedTags:
        """Resolve a tag conflict using specified strategy.

        Args:
            conflict: The conflict to resolve
            strategy: Resolution strategy (keep-both, prefer-local, prefer-remote)

        Returns:
            ResolvedTags with merged tags and resolution details
        """
        dev_tags = set(conflict.dev_tags) if isinstance(conflict.dev_tags, list) else conflict.dev_tags
        obs_tags = set(conflict.obsidian_tags) if isinstance(conflict.obsidian_tags, list) else conflict.obsidian_tags

        if strategy == "keep-both":
            merged = dev_tags | obs_tags
            changes = f"Merged {len(dev_tags)} dev tags + {len(obs_tags)} obsidian tags = {len(merged)} total"

        elif strategy == "prefer-local":
            merged = dev_tags
            changes = f"Used {len(dev_tags)} dev-rules tags, ignored {len(obs_tags - dev_tags)} obsidian-only tags"

        elif strategy == "prefer-remote":
            merged = obs_tags
            changes = f"Used {len(obs_tags)} obsidian tags, ignored {len(dev_tags - obs_tags)} dev-only tags"

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return ResolvedTags(merged_tags=merged, strategy_used=strategy, changes_made=changes)

    def log_conflict(self, conflict: TagConflict, resolution: ResolvedTags = None) -> Path:
        """Log conflict to file for evidence (P2).

        Args:
            conflict: The conflict to log
            resolution: Optional resolution details

        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.conflict_log_dir / f"conflict_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "conflict": {
                "file_path": conflict.file_path,
                "dev_tags": conflict.dev_tags,
                "obsidian_tags": conflict.obsidian_tags,
                "conflict_type": conflict.conflict_type,
            },
        }

        if resolution:
            log_data["resolution"] = {
                "merged_tags": resolution.merged_tags,
                "strategy_used": resolution.strategy_used,
                "changes_made": resolution.changes_made,
            }

        log_file.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
        return log_file

    def interactive_resolve(self, conflict: TagConflict) -> ResolvedTags:
        """Interactively resolve a conflict with user input.

        Args:
            conflict: The conflict to resolve

        Returns:
            ResolvedTags based on user choice
        """
        print(f"\n[CONFLICT] Tag conflict detected: {conflict.file_path}")
        print(f"  Conflict type: {conflict.conflict_type}")
        print(f"  Dev-rules tags: {conflict.dev_tags}")
        print(f"  Obsidian tags:  {conflict.obsidian_tags}")
        print("\nResolution strategies:")
        print("  1. keep-both      - Merge all tags from both sources")
        print("  2. prefer-local   - Use dev-rules tags only")
        print("  3. prefer-remote  - Use Obsidian tags only")

        while True:
            choice = input("\nChoose strategy (1/2/3): ").strip()

            if choice == "1":
                strategy = "keep-both"
                break
            elif choice == "2":
                strategy = "prefer-local"
                break
            elif choice == "3":
                strategy = "prefer-remote"
                break
            else:
                print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")

        resolution = self.resolve_conflict(conflict, strategy)
        print(f"\n[RESOLVED] {resolution.changes_made}")

        return resolution

    def batch_resolve(
        self, conflicts: List[TagConflict], strategy: StrategyType = "keep-both", interactive: bool = False
    ) -> List[ResolvedTags]:
        """Resolve multiple conflicts.

        Args:
            conflicts: List of conflicts to resolve
            strategy: Default strategy for non-interactive mode
            interactive: If True, prompt user for each conflict

        Returns:
            List of resolutions
        """
        resolutions = []

        for conflict in conflicts:
            if interactive:
                resolution = self.interactive_resolve(conflict)
            else:
                resolution = self.resolve_conflict(conflict, strategy)

            # Log conflict and resolution
            self.log_conflict(conflict, resolution)
            resolutions.append(resolution)

        return resolutions


if __name__ == "__main__":
    # Demo usage
    resolver = TagConflictResolver()

    # Example conflict
    dev_tags = {"domain/testing", "status/completed", "tier1"}
    obs_tags = {"domain/testing", "status/in-progress", "project/demo"}

    conflicts = resolver.detect_conflicts(dev_tags, obs_tags, "example.yaml")

    if conflicts:
        print(f"[INFO] Detected {len(conflicts)} conflict(s)")
        for conflict in conflicts:
            resolution = resolver.resolve_conflict(conflict, strategy="keep-both")
            log_file = resolver.log_conflict(conflict, resolution)
            print(f"[INFO] Logged to: {log_file}")
            print(f"[INFO] Merged tags: {resolution.merged_tags}")
    else:
        print("[INFO] No conflicts detected")
