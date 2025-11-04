"""Tests for SharedContextManager - Shared context across sessions.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (comprehensive test coverage)
"""

import json
import time
from datetime import datetime, timezone


from scripts.shared_context_manager import (
    Conflict,
    ContextVersion,
    SharedContextManager,
)


class TestConflict:
    """Test Conflict dataclass."""

    def test_conflict_to_dict(self):
        """Test Conflict serialization."""
        conflict = Conflict(
            conflict_type="overlapping",
            path="shared_knowledge.active_feature",
            session1_value="FEAT-001",
            session2_value="FEAT-002",
            session1_id="session1",
            session2_id="session2",
            auto_resolvable=True,
        )

        data = conflict.to_dict()
        assert data["conflict_type"] == "overlapping"
        assert data["path"] == "shared_knowledge.active_feature"
        assert data["auto_resolvable"] is True


class TestContextVersion:
    """Test ContextVersion dataclass."""

    def test_version_to_dict(self):
        """Test ContextVersion serialization."""
        now = datetime.now(timezone.utc)
        version = ContextVersion(
            version=1,
            timestamp=now,
            session_id="session1",
            changes_description="Initial version",
            context_hash="abc123",
        )

        data = version.to_dict()
        assert data["version"] == 1
        assert data["session_id"] == "session1"
        assert "timestamp" in data

    def test_version_from_dict(self):
        """Test ContextVersion deserialization."""
        now = datetime.now(timezone.utc)
        data = {
            "version": 2,
            "timestamp": now.isoformat(),
            "session_id": "session2",
            "changes_description": "Update",
            "context_hash": "def456",
        }

        version = ContextVersion.from_dict(data)
        assert version.version == 2
        assert version.session_id == "session2"


class TestSharedContextManager:
    """Test SharedContextManager functionality."""

    def test_initialization(self, tmp_path):
        """Test manager initialization."""
        SharedContextManager(context_dir=tmp_path)
        context_file = tmp_path / "shared_context.json"

        assert context_file.exists()

        context = json.loads(context_file.read_text(encoding="utf-8"))
        assert context["project"] == "dev-rules-starter-kit"
        assert context["version"] == "2.0.0"

    def test_read_write_context(self, tmp_path):
        """Test basic read/write operations."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Read initial context
        context = manager.read_shared_context()
        assert context["sessions"] == []

        # Modify and write
        context["sessions"].append({"session_id": "test"})
        manager.write_shared_context(context, "session1", "Add test session")

        # Read back
        updated = manager.read_shared_context()
        assert len(updated["sessions"]) == 1

    def test_compute_hash(self, tmp_path):
        """Test context hash computation."""
        manager = SharedContextManager(context_dir=tmp_path)

        context1 = {"key": "value", "number": 42}
        context2 = {"key": "value", "number": 42}
        context3 = {"key": "different", "number": 42}

        hash1 = manager._compute_hash(context1)
        hash2 = manager._compute_hash(context2)
        hash3 = manager._compute_hash(context3)

        # Same content = same hash
        assert hash1 == hash2

        # Different content = different hash
        assert hash1 != hash3

    def test_version_snapshot(self, tmp_path):
        """Test version snapshot creation."""
        manager = SharedContextManager(context_dir=tmp_path)

        context = manager.read_shared_context()
        context["shared_knowledge"]["active_feature"] = "FEAT-001"
        manager.write_shared_context(context, "session1", "Add feature")

        # Check version created
        versions = manager.get_version_history()
        assert len(versions) == 1
        assert versions[0].session_id == "session1"
        assert versions[0].changes_description == "Add feature"

    def test_sync_context(self, tmp_path):
        """Test real-time context sync."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Update context
        context = manager.read_shared_context()
        context["shared_knowledge"]["recent_commits"] = ["abc123"]
        manager.write_shared_context(context, "session1", "Add commit")

        # Sync from another session
        synced = manager.sync_context("session2")

        assert synced["shared_knowledge"]["recent_commits"] == ["abc123"]

    def test_detect_conflicts_none(self, tmp_path):
        """Test conflict detection with no conflicts."""
        manager = SharedContextManager(context_dir=tmp_path)

        context1 = {"shared_knowledge": {"key1": "value1"}}
        context2 = {"shared_knowledge": {"key2": "value2"}}

        conflicts = manager.detect_conflicts(context1, context2, "s1", "s2")

        assert len(conflicts) == 0

    def test_detect_conflicts_overlapping(self, tmp_path):
        """Test conflict detection with overlapping changes."""
        manager = SharedContextManager(context_dir=tmp_path)

        context1 = {"shared_knowledge": {"active_feature": "FEAT-001"}}
        context2 = {"shared_knowledge": {"active_feature": "FEAT-002"}}

        conflicts = manager.detect_conflicts(context1, context2, "s1", "s2")

        assert len(conflicts) == 1
        assert conflicts[0].path == "shared_knowledge.active_feature"
        assert conflicts[0].session1_value == "FEAT-001"
        assert conflicts[0].session2_value == "FEAT-002"

    def test_detect_conflicts_list_merge(self, tmp_path):
        """Test conflict detection with mergeable lists."""
        manager = SharedContextManager(context_dir=tmp_path)

        context1 = {"shared_knowledge": {"recent_commits": ["abc123"]}}
        context2 = {"shared_knowledge": {"recent_commits": ["def456"]}}

        conflicts = manager.detect_conflicts(context1, context2, "s1", "s2")

        assert len(conflicts) == 1
        assert conflicts[0].auto_resolvable is True

    def test_auto_merge_lists(self, tmp_path):
        """Test auto-merge of list conflicts."""
        manager = SharedContextManager(context_dir=tmp_path)

        conflict = Conflict(
            conflict_type="overlapping",
            path="shared_knowledge.recent_commits",
            session1_value=["abc123"],
            session2_value=["def456"],
            session1_id="s1",
            session2_id="s2",
            auto_resolvable=True,
        )

        merged = manager.auto_merge([conflict])

        assert merged is not None
        commits = merged["shared_knowledge"]["recent_commits"]
        assert "abc123" in commits
        assert "def456" in commits

    def test_auto_merge_dicts(self, tmp_path):
        """Test auto-merge of dict conflicts."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Setup context with dict conflict
        context = manager.read_shared_context()
        context["shared_knowledge"]["test_dict"] = {"key1": "val1"}
        manager._write_context(context)

        conflict = Conflict(
            conflict_type="overlapping",
            path="shared_knowledge.test_dict",
            session1_value={"key1": "val1"},
            session2_value={"key2": "val2"},
            session1_id="s1",
            session2_id="s2",
            auto_resolvable=True,
        )

        merged = manager.auto_merge([conflict])

        assert merged is not None
        test_dict = merged["shared_knowledge"]["test_dict"]
        assert "key1" in test_dict
        assert "key2" in test_dict

    def test_auto_merge_fails_on_contradiction(self, tmp_path):
        """Test auto-merge fails for contradicting conflicts."""
        manager = SharedContextManager(context_dir=tmp_path)

        conflict = Conflict(
            conflict_type="contradiction",
            path="shared_knowledge.active_feature",
            session1_value="FEAT-001",
            session2_value="FEAT-002",
            session1_id="s1",
            session2_id="s2",
            auto_resolvable=False,
        )

        merged = manager.auto_merge([conflict])

        assert merged is None

    def test_create_snapshot(self, tmp_path):
        """Test snapshot creation."""
        manager = SharedContextManager(context_dir=tmp_path)

        context_hash = manager.create_context_snapshot()

        assert len(context_hash) == 64  # SHA-256 hex length

    def test_rollback_context(self, tmp_path):
        """Test context rollback."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Create version 1
        context = manager.read_shared_context()
        context["shared_knowledge"]["active_feature"] = "FEAT-001"
        manager.write_shared_context(context, "s1", "Add FEAT-001")

        # Create version 2
        context = manager.read_shared_context()
        context["shared_knowledge"]["active_feature"] = "FEAT-002"
        manager.write_shared_context(context, "s2", "Change to FEAT-002")

        # Rollback to version 1
        success = manager.rollback_context(1)
        assert success is True

        # Verify rollback
        context = manager.read_shared_context()
        assert context["shared_knowledge"]["active_feature"] == "FEAT-001"

    def test_rollback_invalid_version(self, tmp_path):
        """Test rollback to non-existent version."""
        manager = SharedContextManager(context_dir=tmp_path)

        success = manager.rollback_context(999)
        assert success is False

    def test_version_history(self, tmp_path):
        """Test version history retrieval."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Create multiple versions
        for i in range(3):
            context = manager.read_shared_context()
            context["shared_knowledge"]["counter"] = i
            manager.write_shared_context(context, f"session{i}", f"Update {i}")

        # Get history
        versions = manager.get_version_history()

        assert len(versions) == 3
        assert versions[0].version == 3  # Most recent first
        assert versions[2].version == 1  # Oldest last

    def test_validate_context_integrity(self, tmp_path):
        """Test context integrity validation."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Initially valid
        assert manager.validate_context_integrity() is True

        # Create version
        context = manager.read_shared_context()
        manager.write_shared_context(context, "s1", "Test")

        # Still valid
        assert manager.validate_context_integrity() is True

    def test_statistics(self, tmp_path):
        """Test statistics retrieval."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Create some versions
        context = manager.read_shared_context()
        manager.write_shared_context(context, "s1", "Test")

        stats = manager.get_statistics()

        assert "total_versions" in stats
        assert "current_hash" in stats
        assert "active_sessions" in stats
        assert stats["total_versions"] >= 1

    def test_concurrent_writes(self, tmp_path):
        """Test concurrent write handling."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Simulate concurrent writes
        context1 = manager.read_shared_context()
        context1["shared_knowledge"]["session1_data"] = "data1"

        context2 = manager.read_shared_context()
        context2["shared_knowledge"]["session2_data"] = "data2"

        # Both write
        manager.write_shared_context(context1, "s1", "Session 1 write")
        manager.write_shared_context(context2, "s2", "Session 2 write")

        # Later session wins (last write wins strategy)
        final = manager.read_shared_context()
        assert "session2_data" in final["shared_knowledge"]

    def test_performance_sync_latency(self, tmp_path):
        """Test sync latency is <1 second."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Measure sync time
        start = time.time()
        manager.sync_context("session1")
        latency = time.time() - start

        # Should be very fast (<1 second)
        assert latency < 1.0

    def test_max_version_history(self, tmp_path):
        """Test version history cleanup."""
        manager = SharedContextManager(context_dir=tmp_path)

        # Create more than MAX_VERSION_HISTORY versions
        for i in range(60):
            context = manager.read_shared_context()
            context["shared_knowledge"]["counter"] = i
            manager.write_shared_context(context, "s1", f"Update {i}")

        # Should keep only last 50
        versions = manager.get_version_history()
        assert len(versions) <= 50

    def test_integration_with_coordinator(self, tmp_path):
        """Test integration with SessionCoordinator."""
        from scripts.session_coordinator import SessionCoordinator

        coordinator = SessionCoordinator(context_dir=tmp_path)
        manager = SharedContextManager(context_dir=tmp_path)

        # Coordinator registers session
        coordinator.register_session("session1", "frontend", "claude_1")

        # Manager can read session info
        context = manager.read_shared_context()
        assert len(context["sessions"]) == 1
        assert context["sessions"][0]["session_id"] == "session1"
