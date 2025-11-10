"""Unit tests for Tag Conflict Resolver.

Tests for tag conflict detection and resolution:
- Conflict detection (missing, extra, mismatch)
- Resolution strategies (keep-both, prefer-local, prefer-remote)
- Conflict logging
- Batch resolution

Compliance:
- P8: Test First (unit tests for all features)
- P10: Windows UTF-8 (no emojis in test code)
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from tag_conflict_resolver import (
    TagConflict,
    ResolvedTags,
    TagConflictResolver,
)


class TestTagConflict:
    """Tests for TagConflict dataclass."""

    def test_tag_conflict_creation(self):
        """Test TagConflict dataclass creation."""
        conflict = TagConflict(
            file_path="test.yaml", dev_tags={"tag1", "tag2"}, obsidian_tags={"tag2", "tag3"}, conflict_type="mismatch"
        )

        assert conflict.file_path == "test.yaml"
        assert isinstance(conflict.dev_tags, list)  # Converted to list
        assert isinstance(conflict.obsidian_tags, list)
        assert conflict.conflict_type == "mismatch"

    def test_tag_conflict_set_conversion(self):
        """Test automatic set to list conversion."""
        conflict = TagConflict(
            file_path="test.yaml", dev_tags={"c", "a", "b"}, obsidian_tags={"z", "x", "y"}, conflict_type="mismatch"
        )

        # Should be sorted lists
        assert conflict.dev_tags == ["a", "b", "c"]
        assert conflict.obsidian_tags == ["x", "y", "z"]


class TestResolvedTags:
    """Tests for ResolvedTags dataclass."""

    def test_resolved_tags_creation(self):
        """Test ResolvedTags dataclass creation."""
        resolved = ResolvedTags(
            merged_tags={"tag1", "tag2", "tag3"}, strategy_used="keep-both", changes_made="Merged 2 dev + 2 obs = 3 total"
        )

        assert isinstance(resolved.merged_tags, list)  # Converted to list
        assert resolved.strategy_used == "keep-both"
        assert "Merged" in resolved.changes_made


class TestTagConflictResolver:
    """Tests for TagConflictResolver class."""

    def test_resolver_initialization(self):
        """Test resolver initialization with default path."""
        resolver = TagConflictResolver()
        assert resolver.conflict_log_dir == Path("RUNS/tag-conflicts")

    def test_resolver_custom_log_dir(self):
        """Test resolver initialization with custom path."""
        custom_path = Path("custom/path")
        resolver = TagConflictResolver(conflict_log_dir=custom_path)
        assert resolver.conflict_log_dir == custom_path

    def test_detect_no_conflict(self):
        """Test conflict detection when tags match."""
        resolver = TagConflictResolver()
        dev_tags = {"tag1", "tag2", "tag3"}
        obs_tags = {"tag1", "tag2", "tag3"}

        conflicts = resolver.detect_conflicts(dev_tags, obs_tags, "test.yaml")

        assert len(conflicts) == 0

    def test_detect_missing_in_obsidian(self):
        """Test conflict detection for tags missing in Obsidian."""
        resolver = TagConflictResolver()
        dev_tags = {"tag1", "tag2", "tag3"}
        obs_tags = {"tag1", "tag2"}  # Missing tag3

        conflicts = resolver.detect_conflicts(dev_tags, obs_tags, "test.yaml")

        # Should detect mismatch (both missing and extra)
        # But since there's no extra, should be just one conflict type
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == "missing_in_obsidian"

    def test_detect_extra_in_obsidian(self):
        """Test conflict detection for extra tags in Obsidian."""
        resolver = TagConflictResolver()
        dev_tags = {"tag1", "tag2"}
        obs_tags = {"tag1", "tag2", "tag3"}  # Extra tag3

        conflicts = resolver.detect_conflicts(dev_tags, obs_tags, "test.yaml")

        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == "extra_in_obsidian"

    def test_detect_mismatch(self):
        """Test conflict detection for tag mismatch."""
        resolver = TagConflictResolver()
        dev_tags = {"tag1", "tag2", "tag4"}
        obs_tags = {"tag1", "tag2", "tag3"}  # Different tag

        conflicts = resolver.detect_conflicts(dev_tags, obs_tags, "test.yaml")

        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == "mismatch"

    def test_resolve_keep_both(self):
        """Test conflict resolution with keep-both strategy."""
        resolver = TagConflictResolver()
        conflict = TagConflict(
            file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
        )

        resolution = resolver.resolve_conflict(conflict, strategy="keep-both")

        assert len(resolution.merged_tags) == 3
        assert set(resolution.merged_tags) == {"tag1", "tag2", "tag3"}
        assert resolution.strategy_used == "keep-both"
        assert "Merged" in resolution.changes_made

    def test_resolve_prefer_local(self):
        """Test conflict resolution with prefer-local strategy."""
        resolver = TagConflictResolver()
        conflict = TagConflict(
            file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
        )

        resolution = resolver.resolve_conflict(conflict, strategy="prefer-local")

        assert len(resolution.merged_tags) == 2
        assert set(resolution.merged_tags) == {"tag1", "tag2"}
        assert resolution.strategy_used == "prefer-local"
        assert "dev-rules tags" in resolution.changes_made

    def test_resolve_prefer_remote(self):
        """Test conflict resolution with prefer-remote strategy."""
        resolver = TagConflictResolver()
        conflict = TagConflict(
            file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
        )

        resolution = resolver.resolve_conflict(conflict, strategy="prefer-remote")

        assert len(resolution.merged_tags) == 2
        assert set(resolution.merged_tags) == {"tag2", "tag3"}
        assert resolution.strategy_used == "prefer-remote"
        assert "obsidian tags" in resolution.changes_made

    def test_resolve_invalid_strategy(self):
        """Test conflict resolution with invalid strategy."""
        resolver = TagConflictResolver()
        conflict = TagConflict(file_path="test.yaml", dev_tags=["tag1"], obsidian_tags=["tag2"], conflict_type="mismatch")

        with pytest.raises(ValueError, match="Unknown strategy"):
            resolver.resolve_conflict(conflict, strategy="invalid-strategy")

    def test_log_conflict(self):
        """Test conflict logging to file."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            resolver = TagConflictResolver(conflict_log_dir=Path("test_logs"))

            conflict = TagConflict(
                file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
            )

            log_file = resolver.log_conflict(conflict)

            # Verify log file exists
            assert log_file.exists()
            assert log_file.parent == Path("test_logs")

            # Verify log content
            log_data = json.loads(log_file.read_text(encoding="utf-8"))
            assert "timestamp" in log_data
            assert "conflict" in log_data
            assert log_data["conflict"]["file_path"] == "test.yaml"
            assert log_data["conflict"]["conflict_type"] == "mismatch"

    def test_log_conflict_with_resolution(self):
        """Test logging conflict with resolution details."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            resolver = TagConflictResolver(conflict_log_dir=Path("test_logs"))

            conflict = TagConflict(
                file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
            )

            resolution = resolver.resolve_conflict(conflict, strategy="keep-both")
            log_file = resolver.log_conflict(conflict, resolution)

            # Verify log content includes resolution
            log_data = json.loads(log_file.read_text(encoding="utf-8"))
            assert "resolution" in log_data
            assert log_data["resolution"]["strategy_used"] == "keep-both"
            assert len(log_data["resolution"]["merged_tags"]) == 3

    def test_batch_resolve_auto(self):
        """Test batch resolution with automatic strategy."""
        resolver = TagConflictResolver()

        conflicts = [
            TagConflict("file1.yaml", ["tag1"], ["tag2"], "mismatch"),
            TagConflict("file2.yaml", ["tag3"], ["tag4"], "mismatch"),
        ]

        resolutions = resolver.batch_resolve(conflicts, strategy="keep-both", interactive=False)

        assert len(resolutions) == 2
        assert all(r.strategy_used == "keep-both" for r in resolutions)

    @patch("builtins.input", side_effect=["1", "2"])  # Simulate user input
    def test_interactive_resolve(self, mock_input):
        """Test interactive conflict resolution."""
        resolver = TagConflictResolver()

        conflict = TagConflict(
            file_path="test.yaml", dev_tags=["tag1", "tag2"], obsidian_tags=["tag2", "tag3"], conflict_type="mismatch"
        )

        resolution = resolver.interactive_resolve(conflict)

        # User chose "1" (keep-both)
        assert resolution.strategy_used == "keep-both"
        assert len(resolution.merged_tags) == 3


class TestCLIIntegration:
    """Tests for CLI integration."""

    @patch.dict("os.environ", {"OBSIDIAN_VAULT_PATH": "/tmp/test_vault"})
    @patch("pathlib.Path.exists")
    def test_tag_sync_with_resolve_conflicts_flag(self, mock_exists):
        """Test tag-sync command with --resolve-conflicts flag."""
        from click.testing import CliRunner
        from tier1_cli import cli

        mock_exists.return_value = True

        runner = CliRunner()
        result = runner.invoke(cli, ["tag-sync", "--test", "--resolve-conflicts", "--strategy", "keep-both"])

        assert result.exit_code == 0
        assert "[CONFLICT-DETECTION]" in result.output or "[SUCCESS]" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
