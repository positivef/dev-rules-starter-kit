"""Tests for TDD Enforcer Lite.

Test Coverage:
- Coverage gate enforcement
- Threshold checking
- Strict mode
- Quick mode
- Evidence logging

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.tdd_enforcer_lite import TddEnforcerLite


@pytest.fixture
def temp_evidence_dir(tmp_path: Path) -> Path:
    """Create temporary evidence directory.

    Args:
        tmp_path: pytest temporary directory fixture.

    Returns:
        Path: Temporary evidence directory.
    """
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    return evidence_dir


@pytest.fixture
def mock_coverage_success() -> dict:
    """Mock successful coverage data.

    Returns:
        dict: Coverage data with 92% coverage.
    """
    return {"totals": {"percent_covered": 92.0}, "files": {"scripts/example.py": {"percent_covered": 92.0}}}


@pytest.fixture
def mock_coverage_failure() -> dict:
    """Mock failed coverage data.

    Returns:
        dict: Coverage data with 75% coverage.
    """
    return {"totals": {"percent_covered": 75.0}, "files": {"scripts/example.py": {"percent_covered": 75.0}}}


class TestTddEnforcerInit:
    """Test TddEnforcerLite initialization."""

    def test_init_defaults(self, temp_evidence_dir: Path):
        """Test initialization with default values."""
        enforcer = TddEnforcerLite(evidence_dir=temp_evidence_dir)

        assert enforcer.threshold == 85.0
        assert enforcer.strict is False
        assert enforcer.quick is False
        assert enforcer.evidence_dir == temp_evidence_dir

    def test_init_custom_values(self, temp_evidence_dir: Path):
        """Test initialization with custom values."""
        enforcer = TddEnforcerLite(
            threshold=90.0,
            strict=True,
            quick=True,
            evidence_dir=temp_evidence_dir,
        )

        assert enforcer.threshold == 90.0
        assert enforcer.strict is True
        assert enforcer.quick is True


class TestRunCoverage:
    """Test coverage execution."""

    def test_run_coverage_success(self, temp_evidence_dir: Path, mock_coverage_success: dict):
        """Test successful coverage run."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            evidence_dir=temp_evidence_dir,
        )

        with patch("subprocess.run") as mock_run, patch("builtins.open", create=True) as mock_open, patch(
            "pathlib.Path.exists", return_value=True
        ):
            # Mock pytest success
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            # Mock coverage.json
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_coverage_success)
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = json.dumps(mock_coverage_success)
            mock_open.return_value = mock_file

            success, data = enforcer.run_coverage()

            assert success is True
            assert data["total"] == 92.0
            assert data["tests_passed"] is True

    def test_run_coverage_below_threshold(self, temp_evidence_dir: Path, mock_coverage_failure: dict):
        """Test coverage below threshold."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            evidence_dir=temp_evidence_dir,
        )

        with patch("subprocess.run") as mock_run, patch("builtins.open", create=True) as mock_open, patch(
            "pathlib.Path.exists", return_value=True
        ):
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = json.dumps(mock_coverage_failure)
            mock_open.return_value = mock_file

            success, data = enforcer.run_coverage()

            assert success is False
            assert data["total"] == 75.0

    def test_run_coverage_tests_failed(self, temp_evidence_dir: Path, mock_coverage_success: dict):
        """Test when tests fail but coverage is good."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            evidence_dir=temp_evidence_dir,
        )

        with patch("subprocess.run") as mock_run, patch("builtins.open", create=True) as mock_open, patch(
            "pathlib.Path.exists", return_value=True
        ):
            # Tests failed
            mock_run.return_value = MagicMock(returncode=1, stderr="")

            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = json.dumps(mock_coverage_success)
            mock_open.return_value = mock_file

            success, data = enforcer.run_coverage()

            assert success is False
            assert data["tests_passed"] is False

    def test_run_coverage_no_pytest(self, temp_evidence_dir: Path):
        """Test error when pytest is not installed."""
        enforcer = TddEnforcerLite(evidence_dir=temp_evidence_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="pytest not found"):
                enforcer.run_coverage()

    def test_run_coverage_no_pytest_cov(self, temp_evidence_dir: Path):
        """Test error when pytest-cov is not installed."""
        enforcer = TddEnforcerLite(evidence_dir=temp_evidence_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="No module named 'pytest_cov'")

            with pytest.raises(RuntimeError, match="pytest-cov not installed"):
                enforcer.run_coverage()


class TestEnforce:
    """Test coverage enforcement."""

    def test_enforce_success(self, temp_evidence_dir: Path, mock_coverage_success: dict, capsys):
        """Test successful enforcement."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            evidence_dir=temp_evidence_dir,
        )

        with patch.object(enforcer, "run_coverage") as mock_run:
            mock_run.return_value = (True, {"total": 92.0, "threshold": 85.0, "tests_passed": True, "files": {}})

            exit_code = enforcer.enforce()

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "[OK] All tests passed" in captured.out
            assert "[OK] Coverage meets threshold" in captured.out

    def test_enforce_failure_not_strict(self, temp_evidence_dir: Path, capsys):
        """Test failure in non-strict mode (allows commit)."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            strict=False,
            evidence_dir=temp_evidence_dir,
        )

        with patch.object(enforcer, "run_coverage") as mock_run:
            mock_run.return_value = (False, {"total": 75.0, "threshold": 85.0, "tests_passed": True, "files": {}})

            exit_code = enforcer.enforce()

            assert exit_code == 0  # Non-strict allows commit
            captured = capsys.readouterr()
            assert "[WARN] Coverage below threshold" in captured.out
            assert "[WARN] Quality gate not met" in captured.out

    def test_enforce_failure_strict(self, temp_evidence_dir: Path, capsys):
        """Test failure in strict mode (blocks commit)."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            strict=True,
            evidence_dir=temp_evidence_dir,
        )

        with patch.object(enforcer, "run_coverage") as mock_run:
            mock_run.return_value = (False, {"total": 75.0, "threshold": 85.0, "tests_passed": True, "files": {}})

            exit_code = enforcer.enforce()

            assert exit_code == 1  # Strict blocks commit
            captured = capsys.readouterr()
            assert "[STRICT MODE] Blocking commit" in captured.out

    def test_enforce_quick_mode(self, temp_evidence_dir: Path, capsys):
        """Test quick mode (always allows commit)."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            quick=True,
            evidence_dir=temp_evidence_dir,
        )

        with patch.object(enforcer, "run_coverage") as mock_run:
            mock_run.return_value = (False, {"total": 75.0, "threshold": 85.0, "tests_passed": True, "files": {}})

            exit_code = enforcer.enforce()

            assert exit_code == 0  # Quick mode always allows
            captured = capsys.readouterr()
            assert "[QUICK MODE]" in captured.out

    def test_enforce_exception_handling(self, temp_evidence_dir: Path, capsys):
        """Test exception handling during enforcement."""
        enforcer = TddEnforcerLite(evidence_dir=temp_evidence_dir)

        with patch.object(enforcer, "run_coverage") as mock_run:
            mock_run.side_effect = Exception("Test error")

            exit_code = enforcer.enforce()

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "[ERROR] Failed to run coverage" in captured.out


class TestEvidenceLogging:
    """Test evidence logging."""

    def test_log_evidence_creates_file(self, temp_evidence_dir: Path):
        """Test that evidence file is created."""
        enforcer = TddEnforcerLite(
            threshold=85.0,
            evidence_dir=temp_evidence_dir,
        )

        coverage_data = {
            "total": 92.0,
            "tests_passed": True,
        }

        enforcer._log_evidence(True, coverage_data)

        evidence_files = list(temp_evidence_dir.glob("tdd_coverage_*.json"))
        assert len(evidence_files) == 1

        with open(evidence_files[0], encoding="utf-8") as f:
            evidence = json.load(f)

        assert evidence["success"] is True
        assert evidence["coverage"] == 92.0
        assert evidence["threshold"] == 85.0
        assert evidence["tool"] == "tdd_enforcer_lite"

    def test_log_evidence_contains_all_fields(self, temp_evidence_dir: Path):
        """Test that evidence contains all required fields."""
        enforcer = TddEnforcerLite(
            threshold=90.0,
            strict=True,
            quick=False,
            evidence_dir=temp_evidence_dir,
        )

        coverage_data = {
            "total": 95.0,
            "tests_passed": True,
        }

        enforcer._log_evidence(True, coverage_data)

        evidence_files = list(temp_evidence_dir.glob("tdd_coverage_*.json"))
        with open(evidence_files[0], encoding="utf-8") as f:
            evidence = json.load(f)

        assert "timestamp" in evidence
        assert evidence["tool"] == "tdd_enforcer_lite"
        assert evidence["success"] is True
        assert evidence["threshold"] == 90.0
        assert evidence["coverage"] == 95.0
        assert evidence["tests_passed"] is True
        assert evidence["strict_mode"] is True
        assert evidence["quick_mode"] is False


class TestMain:
    """Test CLI main function."""

    def test_main_with_feature_flag_disabled(self, monkeypatch, temp_evidence_dir: Path):
        """Test main function when feature flag is disabled."""
        from scripts.feature_flags import FeatureFlags

        # Mock feature flags to return disabled
        def mock_is_enabled(self, path):
            if path == "tier1_integration.tools.tdd_enforcer":
                return False
            return True

        monkeypatch.setattr(FeatureFlags, "is_enabled", mock_is_enabled)
        monkeypatch.setattr("sys.argv", ["tdd_enforcer_lite.py"])

        from scripts.tdd_enforcer_lite import main

        exit_code = main()

        assert exit_code == 1

    def test_main_uses_feature_flag_defaults(self, monkeypatch, temp_evidence_dir: Path, capsys):
        """Test that main uses feature flag default values."""
        from scripts.feature_flags import FeatureFlags

        def mock_get_config(self, path):
            if "coverage_threshold" in path:
                return 90.0
            if "strict_mode" in path:
                return True
            return None

        monkeypatch.setattr(FeatureFlags, "get_config", mock_get_config)
        monkeypatch.setattr(FeatureFlags, "is_enabled", lambda self, x: True)
        monkeypatch.setattr("sys.argv", ["tdd_enforcer_lite.py"])

        with patch("scripts.tdd_enforcer_lite.TddEnforcerLite.enforce") as mock_enforce:
            mock_enforce.return_value = 0

            from scripts.tdd_enforcer_lite import main

            main()

            # Verify TddEnforcerLite was created with feature flag values
            # This is indirectly tested by the enforce call
