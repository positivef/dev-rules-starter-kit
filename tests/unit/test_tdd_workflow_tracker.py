"""Unit tests for TDD Workflow Tracker.

Tests for TDD workflow compliance tracking:
- Git commit history analysis
- TDD compliance detection
- Developer scoring
- Team reporting
- Violation logging

Constitutional Compliance:
- P8: Test-First Development (testing the tracker)
- P2: Evidence-Based (verify logging works)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from tdd_workflow_tracker import CommitAnalysis, TDDWorkflowTracker


class TestCommitAnalysis:
    """Tests for CommitAnalysis dataclass."""

    def test_commit_analysis_creation(self):
        """Test CommitAnalysis creation."""
        timestamp = datetime.now()
        analysis = CommitAnalysis(
            commit_hash="abc123",
            author="John Doe",
            timestamp=timestamp,
            files_changed=["test.py", "src.py"],
            is_tdd_compliant=True,
        )

        assert analysis.commit_hash == "abc123"
        assert analysis.author == "John Doe"
        assert analysis.timestamp == timestamp
        assert analysis.files_changed == ["test.py", "src.py"]
        assert analysis.is_tdd_compliant is True
        assert analysis.violation_reason is None

    def test_commit_analysis_with_violation(self):
        """Test CommitAnalysis with violation reason."""
        analysis = CommitAnalysis(
            commit_hash="abc123",
            author="John Doe",
            timestamp=datetime.now(),
            files_changed=["src.py"],
            is_tdd_compliant=False,
            violation_reason="No test file",
        )

        assert analysis.is_tdd_compliant is False
        assert analysis.violation_reason == "No test file"


class TestTDDWorkflowTracker:
    """Tests for TDDWorkflowTracker class."""

    def test_tracker_initialization(self):
        """Test tracker initialization with defaults."""
        tracker = TDDWorkflowTracker()

        assert tracker.project_root is not None
        assert tracker.evidence_dir.name == "tdd-violations"

    def test_tracker_custom_settings(self):
        """Test tracker initialization with custom settings."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            project_root = Path.cwd()
            evidence_dir = project_root / "custom_evidence"

            tracker = TDDWorkflowTracker(
                project_root=project_root,
                evidence_dir=evidence_dir,
            )

            assert tracker.project_root == project_root
            assert tracker.evidence_dir == evidence_dir
            assert evidence_dir.exists()

    def test_is_test_file(self):
        """Test test file detection."""
        tracker = TDDWorkflowTracker()

        assert tracker._is_test_file("tests/test_foo.py")
        assert tracker._is_test_file("test_bar.py")
        assert tracker._is_test_file("foo_test.py")
        assert not tracker._is_test_file("foo.py")
        assert not tracker._is_test_file("README.md")

    def test_is_source_file(self):
        """Test source file detection."""
        tracker = TDDWorkflowTracker()

        assert tracker._is_source_file("scripts/foo.py")
        assert tracker._is_source_file("src/bar.py")
        assert not tracker._is_source_file("docs/guide.py")
        assert not tracker._is_source_file("examples/demo.py")
        assert not tracker._is_source_file("README.md")

    def test_analyze_commit_only_tests(self):
        """Test commit with only test files (compliant)."""
        tracker = TDDWorkflowTracker()

        commit = {
            "hash": "abc123",
            "author": "John Doe",
            "timestamp": datetime.now(),
            "files": ["tests/test_foo.py", "tests/test_bar.py"],
        }

        analysis = tracker.analyze_commit_tdd_compliance(commit)

        assert analysis.is_tdd_compliant is True
        assert analysis.violation_reason is None

    def test_analyze_commit_only_source(self):
        """Test commit with only source files (violation)."""
        tracker = TDDWorkflowTracker()

        commit = {
            "hash": "abc123",
            "author": "John Doe",
            "timestamp": datetime.now(),
            "files": ["scripts/foo.py", "scripts/bar.py"],
        }

        analysis = tracker.analyze_commit_tdd_compliance(commit)

        assert analysis.is_tdd_compliant is False
        assert "without corresponding test files" in analysis.violation_reason

    def test_analyze_commit_both_test_and_source(self):
        """Test commit with both test and source files (lenient: compliant)."""
        tracker = TDDWorkflowTracker()

        commit = {
            "hash": "abc123",
            "author": "John Doe",
            "timestamp": datetime.now(),
            "files": ["tests/test_foo.py", "scripts/foo.py"],
        }

        analysis = tracker.analyze_commit_tdd_compliance(commit)

        assert analysis.is_tdd_compliant is True

    def test_analyze_commit_no_python_files(self):
        """Test commit with no Python files (not applicable)."""
        tracker = TDDWorkflowTracker()

        commit = {
            "hash": "abc123",
            "author": "John Doe",
            "timestamp": datetime.now(),
            "files": ["README.md", "docs/guide.md"],
        }

        analysis = tracker.analyze_commit_tdd_compliance(commit)

        assert analysis.is_tdd_compliant is True  # Not applicable

    @patch("subprocess.run")
    def test_get_commit_history(self, mock_run):
        """Test getting commit history from git."""
        tracker = TDDWorkflowTracker()

        # Mock git log output
        mock_output = """abc123|John Doe|2025-11-02 10:00:00 +0000
tests/test_foo.py

def456|Jane Smith|2025-11-01 15:30:00 +0000
scripts/bar.py
tests/test_bar.py
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output,
        )

        commits = tracker.get_commit_history(days=7)

        assert len(commits) == 2
        assert commits[0]["hash"] == "abc123"
        assert commits[0]["author"] == "John Doe"
        assert len(commits[0]["files"]) == 1
        assert commits[1]["hash"] == "def456"
        assert len(commits[1]["files"]) == 2

    @patch("subprocess.run")
    def test_get_commit_history_empty(self, mock_run):
        """Test getting commit history when no commits."""
        tracker = TDDWorkflowTracker()

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
        )

        commits = tracker.get_commit_history(days=7)

        assert len(commits) == 0

    @patch("subprocess.run")
    def test_get_commit_history_error(self, mock_run):
        """Test getting commit history when git fails."""
        tracker = TDDWorkflowTracker()

        mock_run.side_effect = Exception("Git error")

        commits = tracker.get_commit_history(days=7)

        assert len(commits) == 0

    @patch.object(TDDWorkflowTracker, "get_commit_history")
    def test_calculate_developer_score_no_commits(self, mock_get_commits):
        """Test developer score with no commits."""
        tracker = TDDWorkflowTracker()
        mock_get_commits.return_value = []

        score = tracker.calculate_developer_score("John Doe", days=7)

        assert score["developer"] == "John Doe"
        assert score["total_commits"] == 0
        assert score["compliant_commits"] == 0
        assert score["compliance_rate"] == 0.0

    @patch.object(TDDWorkflowTracker, "get_commit_history")
    def test_calculate_developer_score(self, mock_get_commits):
        """Test developer score calculation."""
        tracker = TDDWorkflowTracker()

        # Mock commits: 2 compliant, 1 violation
        mock_get_commits.return_value = [
            {
                "hash": "abc123",
                "author": "John Doe",
                "timestamp": datetime.now(),
                "files": ["tests/test_foo.py"],
            },
            {
                "hash": "def456",
                "author": "John Doe",
                "timestamp": datetime.now(),
                "files": ["scripts/bar.py"],  # Violation
            },
            {
                "hash": "ghi789",
                "author": "John Doe",
                "timestamp": datetime.now(),
                "files": ["tests/test_baz.py", "scripts/baz.py"],
            },
        ]

        score = tracker.calculate_developer_score("John Doe", days=7)

        assert score["developer"] == "John Doe"
        assert score["total_commits"] == 3
        assert score["compliant_commits"] == 2
        assert score["compliance_rate"] == pytest.approx(66.67, rel=0.1)
        assert len(score["violations"]) == 1

    @patch.object(TDDWorkflowTracker, "get_commit_history")
    def test_generate_team_report_empty(self, mock_get_commits):
        """Test team report with no commits."""
        tracker = TDDWorkflowTracker()
        mock_get_commits.return_value = []

        report = tracker.generate_team_report(days=7)

        assert report["period_days"] == 7
        assert report["total_commits"] == 0
        assert report["team_compliance_rate"] == 0.0

    @patch.object(TDDWorkflowTracker, "get_commit_history")
    def test_generate_team_report(self, mock_get_commits):
        """Test team report generation."""
        tracker = TDDWorkflowTracker()

        # Mock commits from 2 developers
        mock_get_commits.return_value = [
            {
                "hash": "abc123",
                "author": "John Doe",
                "timestamp": datetime.now(),
                "files": ["tests/test_foo.py"],
            },
            {
                "hash": "def456",
                "author": "Jane Smith",
                "timestamp": datetime.now(),
                "files": ["scripts/bar.py"],  # Violation
            },
            {
                "hash": "ghi789",
                "author": "John Doe",
                "timestamp": datetime.now(),
                "files": ["tests/test_baz.py"],
            },
        ]

        report = tracker.generate_team_report(days=7)

        assert report["period_days"] == 7
        assert report["total_commits"] == 3
        assert "John Doe" in report["developers"]
        assert "Jane Smith" in report["developers"]
        assert report["developers"]["John Doe"]["commits"] == 2
        assert report["developers"]["John Doe"]["compliant"] == 2
        assert report["team_compliance_rate"] == pytest.approx(66.67, rel=0.1)

    def test_log_violations(self):
        """Test violation logging."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            evidence_dir = Path("evidence")
            tracker = TDDWorkflowTracker(evidence_dir=evidence_dir)

            violations = [
                CommitAnalysis(
                    commit_hash="abc123",
                    author="John Doe",
                    timestamp=datetime.now(),
                    files_changed=["scripts/foo.py"],
                    is_tdd_compliant=False,
                    violation_reason="No test file",
                )
            ]

            log_file = tracker.log_violations(violations)

            assert log_file.exists()
            assert log_file.parent == evidence_dir

            # Verify log content
            log_data = json.loads(log_file.read_text(encoding="utf-8"))
            assert "timestamp" in log_data
            assert len(log_data["violations"]) == 1
            assert log_data["violations"][0]["author"] == "John Doe"
            assert log_data["summary"]["total_violations"] == 1

    @patch.object(TDDWorkflowTracker, "generate_team_report")
    def test_generate_report_weekly(self, mock_report):
        """Test weekly report generation."""
        tracker = TDDWorkflowTracker()

        mock_report.return_value = {
            "period_days": 7,
            "total_commits": 10,
            "team_compliance_rate": 85.0,
            "developers": {
                "John Doe": {"commits": 6, "compliant": 5, "compliance_rate": 83.33},
                "Jane Smith": {"commits": 4, "compliant": 4, "compliance_rate": 100.0},
            },
        }

        report = tracker.generate_report("weekly")

        assert "WEEKLY" in report
        assert "Last 7 days" in report
        assert "Total Commits: 10" in report
        assert "Team Compliance Rate: 85.0%" in report
        assert "John Doe" in report
        assert "Jane Smith" in report
        assert "[GOOD]" in report  # 85% is good

    @patch.object(TDDWorkflowTracker, "generate_team_report")
    def test_generate_report_monthly(self, mock_report):
        """Test monthly report generation."""
        tracker = TDDWorkflowTracker()

        mock_report.return_value = {
            "period_days": 30,
            "total_commits": 50,
            "team_compliance_rate": 96.0,
            "developers": {},
        }

        report = tracker.generate_report("monthly")

        assert "MONTHLY" in report
        assert "Last 30 days" in report
        assert "96.0%" in report
        assert "[EXCELLENT]" in report  # 96% is excellent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
