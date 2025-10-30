#!/usr/bin/env python3
"""Tests for auto_sync_obsidian.py"""

import pytest
import subprocess
from unittest.mock import Mock, patch
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from auto_sync_obsidian import (
    get_last_commit_info,
    should_sync,
    categorize_work,
    extract_key_changes,
    generate_devlog_content,
)


class TestGitOperations:
    """Test Git information retrieval"""

    @patch("subprocess.run")
    def test_get_last_commit_info_success(self, mock_run):
        """Test getting commit info successfully"""
        # Mock git commands
        mock_run.side_effect = [
            Mock(stdout="feat: add new feature\n\nDetailed description", returncode=0),
            Mock(stdout="abc12345", returncode=0),
            Mock(stdout="file1.py\nfile2.py\nfile3.py", returncode=0),
            Mock(stdout="3 files changed, 100 insertions(+), 20 deletions(-)", returncode=0),
        ]

        result = get_last_commit_info()

        assert result is not None
        assert result["message"] == "feat: add new feature\n\nDetailed description"
        assert result["hash"] == "abc12345"
        assert len(result["files"]) == 3
        assert "file1.py" in result["files"]

    @patch("subprocess.run")
    def test_get_last_commit_info_failure(self, mock_run):
        """Test handling git command failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        result = get_last_commit_info()

        assert result is None


class TestSyncDecision:
    """Test sync decision logic"""

    def test_should_sync_many_files(self):
        """Test sync triggered by many file changes"""
        commit_info = {
            "files": ["file1.py", "file2.py", "file3.py", "file4.py"],
            "file_count": 4,
            "message": "feat: update",
        }

        result, reason = should_sync(commit_info)
        assert result is True

    def test_should_sync_feature(self):
        """Test sync triggered by feature commit"""
        commit_info = {"files": ["file1.py"], "file_count": 1, "message": "feat: add authentication"}

        result, reason = should_sync(commit_info)
        assert result is True

    def test_should_sync_fix(self):
        """Test sync triggered by fix commit"""
        commit_info = {"files": ["file1.py"], "file_count": 1, "message": "fix: resolve memory leak"}

        result, reason = should_sync(commit_info)
        assert result is True

    def test_should_not_sync_small_change(self):
        """Test sync not triggered by small changes"""
        commit_info = {"files": ["file1.py"], "file_count": 1, "message": "chore: update comment"}

        result, reason = should_sync(commit_info)
        assert result is False

    def test_should_sync_docs(self):
        """Test sync triggered by documentation"""
        commit_info = {"files": ["README.md"], "file_count": 1, "message": "docs: update readme"}

        result, reason = should_sync(commit_info)
        assert result is True  # Documentation work triggers sync


class TestWorkCategorization:
    """Test work categorization"""

    def test_categorize_work_feature(self):
        """Test categorizing feature work"""
        commit_info = {"message": "feat: add login system"}

        category = categorize_work(commit_info)

        assert category == "feature"

    def test_categorize_work_bugfix(self):
        """Test categorizing bugfix work"""
        commit_info = {"message": "fix: resolve memory leak"}

        category = categorize_work(commit_info)

        assert category == "bugfix"

    def test_categorize_work_general(self):
        """Test categorizing general work"""
        commit_info = {"message": "Update something"}

        category = categorize_work(commit_info)

        assert category == "general"

    def test_extract_key_changes(self):
        """Test extracting key changes"""
        commit_info = {
            "files": [
                "scripts/test.py",
                "tests/test_file.py",
                "README.md",
                "config.yaml",
            ]
        }

        changes = extract_key_changes(commit_info)

        assert len(changes) > 0
        assert any("스크립트" in change for change in changes)


class TestContentGeneration:
    """Test devlog content generation"""

    def test_generate_devlog_content(self):
        """Test generating devlog markdown content"""
        commit_info = {
            "message": "feat: add login system\n\nImplemented JWT authentication",
            "hash": "abc12345",
            "files": ["auth.py", "login.py", "test_auth.py"],
            "file_count": 3,
            "stats": "3 files changed, 150 insertions(+)",
        }

        content = generate_devlog_content(commit_info)

        assert "feat: add login system" in content
        assert "abc12345" in content
        assert "3" in content  # file count
        assert "feature" in content  # work type

    def test_generate_devlog_with_changes(self):
        """Test devlog includes key changes"""
        commit_info = {
            "message": "feat(api): add REST endpoints",
            "hash": "def45678",
            "files": ["scripts/api.py", "tests/test_api.py"],
            "file_count": 2,
            "stats": "2 files changed",
        }

        content = generate_devlog_content(commit_info)

        assert "스크립트" in content or "테스트" in content


class TestIntegration:
    """Integration tests"""

    @patch("subprocess.run")
    def test_full_sync_flow(self, mock_run):
        """Test full sync workflow"""
        # Mock git commands
        mock_run.side_effect = [
            Mock(stdout="feat: add feature\n", returncode=0),
            Mock(stdout="abc12345", returncode=0),
            Mock(stdout="file1.py\nfile2.py\nfile3.py\nfile4.py", returncode=0),
            Mock(stdout="4 files changed, 100 insertions(+)", returncode=0),
        ]

        # Should sync (4+ files)
        commit_info = get_last_commit_info()
        assert commit_info is not None
        assert len(commit_info["files"]) == 4

        result, reason = should_sync(commit_info)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
