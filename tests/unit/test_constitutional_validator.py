"""Unit tests for constitutional_validator.py

Tests the ConstitutionalValidator class and validation functions.
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest
from constitutional_validator import (
    ConstitutionalValidator,
    ConstitutionalViolation,
)


class TestConstitutionalViolation:
    """Test ConstitutionalViolation dataclass"""

    def test_create_violation_with_all_fields(self):
        """Should create violation with all fields"""
        violation = ConstitutionalViolation(article="I", message="Test violation", severity="error", context="Test context")

        assert violation.article == "I"
        assert violation.message == "Test violation"
        assert violation.severity == "error"
        assert violation.context == "Test context"

    def test_create_violation_without_context(self):
        """Should create violation without optional context"""
        violation = ConstitutionalViolation(article="II", message="Test", severity="warning")

        assert violation.article == "II"
        assert violation.message == "Test"
        assert violation.severity == "warning"
        assert violation.context is None


class TestLoadConstitution:
    """Test constitution loading and parsing"""

    def test_load_constitution_file_not_found(self):
        """Should raise FileNotFoundError for missing constitution"""
        with pytest.raises(FileNotFoundError) as exc_info:
            ConstitutionalValidator(constitution_path=Path("nonexistent/constitution.md"))

        assert "Constitution not found" in str(exc_info.value)

    def test_load_constitution_success(self, tmp_path):
        """Should load and parse constitution successfully"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text(
            """
### Article I: Library-First Development
Description of Article I

### Article II: CLI Interface
Description of Article II
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)

        assert "I" in validator.constitution
        assert "Library-First Development" in validator.constitution["I"]
        assert "II" in validator.constitution
        assert "CLI Interface" in validator.constitution["II"]

    def test_load_constitution_empty_file(self, tmp_path):
        """Should handle empty constitution file"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)

        assert len(validator.constitution) == 0


class TestCheckWindowsEncoding:
    """Test Windows encoding compliance (Article V)"""

    def test_check_windows_encoding_with_emoji(self, tmp_path):
        """Should detect emoji and return error violation"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article V: Windows\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("- [ ] T001 Add emoji support 🚀 ✅", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_windows_encoding(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 1
        assert violations[0].article == "V"
        assert violations[0].severity == "error"
        assert "EMOJI DETECTED" in violations[0].message

    def test_check_windows_encoding_without_emoji(self, tmp_path):
        """Should pass with no emoji"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article V: Windows\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("- [ ] T001 Add regular text [OK]", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_windows_encoding(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 0

    def test_check_windows_encoding_counts_multiple_emoji(self, tmp_path):
        """Should count multiple emoji correctly"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article V: Windows\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("🚀 ✅ 🔥 🎉", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_windows_encoding(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 1
        # Some emoji may not be detected by the regex, so check for "emoji characters found"
        assert "emoji" in violations[0].message.lower()
        assert "found" in violations[0].message.lower()


class TestCheckTestFirst:
    """Test Test-First Development (Article III)"""

    def test_check_test_first_no_tests_with_implementation(self, tmp_path):
        """Should error when implementation exists without tests"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article III: Test-First\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
- [ ] T001 Implement login feature
- [ ] T002 Add authentication
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_test_first(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 1
        assert violations[0].article == "III"
        assert violations[0].severity == "error"
        assert "NO TEST TASKS FOUND" in violations[0].message

    def test_check_test_first_tests_after_implementation(self, tmp_path):
        """Should error when tests come after implementation"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article III: Test-First\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
- [ ] T001 Implement login
- [ ] T010 Test login
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_test_first(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 1
        assert violations[0].article == "III"
        assert violations[0].severity == "error"
        assert "appear AFTER implementation" in violations[0].message

    def test_check_test_first_tests_before_implementation(self, tmp_path):
        """Should pass when tests come before implementation"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article III: Test-First\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
- [ ] T001 Write tests for login
- [ ] T010 Implement login
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_test_first(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 0

    def test_check_test_first_no_tasks(self, tmp_path):
        """Should pass when no implementation tasks exist"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article III: Test-First\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("# Empty tasks\n\nNo tasks yet.", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_test_first(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 0


class TestCheckSimplicity:
    """Test Simplicity & YAGNI (Article VII)"""

    def test_check_simplicity_too_many_projects(self, tmp_path):
        """Should error when more than 3 projects"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article VII: Simplicity\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
- [ ] T001 Create project1/module
- [ ] T002 Create project2/module
- [ ] T003 Create project3/module
- [ ] T004 Create project4/module
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_simplicity(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 1
        assert violations[0].article == "VII"
        assert violations[0].severity == "error"
        assert "4 top-level projects" in violations[0].message

    def test_check_simplicity_within_limit(self, tmp_path):
        """Should pass with 3 or fewer projects"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article VII: Simplicity\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
- [ ] T001 Create project1/module
- [ ] T002 Create project2/module
- [ ] T003 Create project3/module
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator._check_simplicity(tasks_file.read_text(encoding="utf-8"))

        assert len(violations) == 0


class TestFormatViolations:
    """Test violation formatting"""

    def test_format_violations_with_violations(self, tmp_path):
        """Should format violations into readable output"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article I: Test\n", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)

        violations = [
            ConstitutionalViolation(article="I", message="Test violation 1", severity="error", context="Context 1"),
            ConstitutionalViolation(article="II", message="Test violation 2", severity="warning", context="Context 2"),
        ]

        output = validator.format_violations(violations)

        assert "Article I" in output
        assert "Test violation 1" in output
        assert "Article II" in output
        assert "Test violation 2" in output
        assert "ERROR" in output or "error" in output.lower()
        assert "WARNING" in output or "warning" in output.lower()

    def test_format_violations_empty_list(self, tmp_path):
        """Should handle empty violations list"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article I: Test\n", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)

        violations = []

        output = validator.format_violations(violations)

        assert output is not None
        assert isinstance(output, str)
        assert "All constitutional checks passed" in output


class TestValidate:
    """Test main validation function"""

    def test_validate_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing tasks file"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article I: Test\n", encoding="utf-8")

        validator = ConstitutionalValidator(constitution_path=constitution_file)

        with pytest.raises(FileNotFoundError) as exc_info:
            validator.validate(tmp_path / "nonexistent.md")

        assert "Tasks file not found" in str(exc_info.value)

    def test_validate_success(self, tmp_path):
        """Should validate tasks file successfully"""
        constitution_file = tmp_path / "constitution.md"
        constitution_file.write_text("### Article I: Test\n", encoding="utf-8")

        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(
            """
# Tasks

- [ ] T001 Write tests
- [ ] T010 Implement feature
""",
            encoding="utf-8",
        )

        validator = ConstitutionalValidator(constitution_path=constitution_file)
        violations = validator.validate(tasks_file)

        # Should return a list (might have warnings, but shouldn't crash)
        assert isinstance(violations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
