"""Unit tests for Enhanced TDD Enforcer.

Tests for strict TDD enforcement with coverage tracking:
- File exemption logic
- Test file detection
- Coverage checking
- Violation logging
- Mode enforcement (warning vs blocking)

Constitutional Compliance:
- P8: Test-First Development (testing the enforcer)
- P2: Evidence-Based (verify logging works)
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from tdd_enforcer_enhanced import CoverageGap, EnhancedTDDEnforcer


class TestCoverageGap:
    """Tests for CoverageGap dataclass."""

    def test_coverage_gap_creation(self):
        """Test CoverageGap creation."""
        gap = CoverageGap(
            file_path="test.py",
            current_coverage=75.0,
            required_coverage=80.0,
            missing_lines=[10, 11, 12],
        )

        assert gap.file_path == "test.py"
        assert gap.current_coverage == 75.0
        assert gap.required_coverage == 80.0
        assert gap.missing_lines == [10, 11, 12]
        assert gap.gap == 5.0


class TestEnhancedTDDEnforcer:
    """Tests for EnhancedTDDEnforcer class."""

    def test_enforcer_initialization(self):
        """Test enforcer initialization with defaults."""
        enforcer = EnhancedTDDEnforcer()

        assert enforcer.min_coverage == 80.0
        assert enforcer.mode == "warning"
        assert enforcer.evidence_dir.name == "tdd-violations"

    def test_enforcer_custom_settings(self):
        """Test enforcer initialization with custom settings."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            custom_evidence = Path("custom_evidence")
            enforcer = EnhancedTDDEnforcer(
                min_coverage=90.0,
                mode="blocking",
                evidence_dir=custom_evidence,
            )

            assert enforcer.min_coverage == 90.0
            assert enforcer.mode == "blocking"
            assert enforcer.evidence_dir == custom_evidence
            assert custom_evidence.exists()

    def test_is_exempt_by_filename(self):
        """Test file exemption by filename pattern."""
        enforcer = EnhancedTDDEnforcer()

        assert enforcer.is_exempt(Path("__init__.py"))
        assert enforcer.is_exempt(Path("setup.py"))
        assert enforcer.is_exempt(Path("my_config.py"))
        assert not enforcer.is_exempt(Path("my_module.py"))

    def test_is_exempt_by_directory(self):
        """Test file exemption by directory."""
        enforcer = EnhancedTDDEnforcer()

        assert enforcer.is_exempt(Path("tests/test_foo.py"))
        assert enforcer.is_exempt(Path("docs/README.md"))
        assert enforcer.is_exempt(Path("RUNS/evidence/log.txt"))
        assert not enforcer.is_exempt(Path("scripts/my_module.py"))

    def test_find_test_file_existing(self):
        """Test finding existing test files."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create project structure
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            source_file = Path("scripts/my_module.py")
            source_file.write_text("# source", encoding="utf-8")

            test_file = Path("tests/unit/test_my_module.py")
            test_file.write_text("# test", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd())
            found_tests = enforcer.find_test_file(source_file)

            assert len(found_tests) > 0
            assert any("test_my_module.py" in str(t) for t in found_tests)

    def test_find_test_file_missing(self):
        """Test finding test files when none exist."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            source_file = Path("scripts/untested_module.py")
            source_file.write_text("# source", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd())
            found_tests = enforcer.find_test_file(source_file)

            # No actual test files exist
            assert all(not t.exists() for t in found_tests)

    def test_check_file_coverage_no_coverage_data(self):
        """Test coverage check when .coverage file doesn't exist."""
        enforcer = EnhancedTDDEnforcer()

        # Non-existent file
        coverage = enforcer.check_file_coverage(Path("nonexistent.py"))

        # Should return None when coverage data unavailable
        assert coverage is None

    def test_check_files_with_missing_tests(self):
        """Test checking files with missing tests."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            # Create source file without test
            source_file = Path("scripts/untested.py")
            source_file.write_text("def foo(): pass", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd())
            violations, coverage_gaps = enforcer.check_files([source_file])

            assert len(violations) == 1
            assert "untested.py" in violations[0]

    def test_check_files_exempt(self):
        """Test that exempt files are not checked."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd())

            # Exempt files
            init_file = Path("__init__.py")
            init_file.write_text("", encoding="utf-8")

            violations, coverage_gaps = enforcer.check_files([init_file])

            assert len(violations) == 0  # Exempt files don't generate violations

    def test_log_violations(self):
        """Test violation logging to evidence directory."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            evidence_dir = Path("evidence")
            enforcer = EnhancedTDDEnforcer(evidence_dir=evidence_dir)

            violations = ["Missing test for foo.py"]
            coverage_gaps = [
                CoverageGap(
                    file_path="bar.py",
                    current_coverage=70.0,
                    required_coverage=80.0,
                    missing_lines=[10, 11, 12],
                )
            ]

            log_file = enforcer.log_violations(violations, coverage_gaps)

            # Verify log file created
            assert log_file.exists()
            assert log_file.parent == evidence_dir

            # Verify log content
            log_data = json.loads(log_file.read_text(encoding="utf-8"))
            assert "timestamp" in log_data
            assert log_data["violations"]["missing_tests"] == violations
            assert len(log_data["violations"]["coverage_gaps"]) == 1
            assert log_data["summary"]["total_violations"] == 1

    def test_generate_report_no_violations(self):
        """Test report generation when no violations."""
        enforcer = EnhancedTDDEnforcer()
        report = enforcer.generate_report([], [])

        assert "[SUCCESS]" in report
        assert "All files have tests" in report

    def test_generate_report_with_violations(self):
        """Test report generation with violations."""
        enforcer = EnhancedTDDEnforcer()

        violations = ["Missing test for foo.py"]
        coverage_gaps = [
            CoverageGap(
                file_path="bar.py",
                current_coverage=70.0,
                required_coverage=80.0,
                missing_lines=[10, 11],
            )
        ]

        report = enforcer.generate_report(violations, coverage_gaps)

        assert "MISSING TESTS" in report
        assert "foo.py" in report
        assert "COVERAGE GAPS" in report
        assert "bar.py" in report
        assert "70.0%" in report

    def test_enforce_warning_mode(self):
        """Test enforce in warning mode (does not block)."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            # Create source file without test
            source_file = Path("scripts/untested.py")
            source_file.write_text("def foo(): pass", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd(), mode="warning")
            exit_code = enforcer.enforce([source_file])

            # Warning mode returns 0 even with violations
            assert exit_code == 0

    def test_enforce_blocking_mode(self):
        """Test enforce in blocking mode (blocks on violations)."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            # Create source file without test
            source_file = Path("scripts/untested.py")
            source_file.write_text("def foo(): pass", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd(), mode="blocking")
            exit_code = enforcer.enforce([source_file])

            # Blocking mode returns 1 with violations
            assert exit_code == 1

    def test_enforce_success(self):
        """Test enforce when all files have tests."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("scripts").mkdir()
            Path("tests/unit").mkdir(parents=True)

            # Create source file with test
            source_file = Path("scripts/tested.py")
            source_file.write_text("def foo(): pass", encoding="utf-8")

            test_file = Path("tests/unit/test_tested.py")
            test_file.write_text("def test_foo(): assert True", encoding="utf-8")

            enforcer = EnhancedTDDEnforcer(project_root=Path.cwd(), mode="blocking")
            exit_code = enforcer.enforce([source_file])

            # All checks pass
            assert exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
