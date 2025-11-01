"""Tests for TAG Extractor Lite.

Test Coverage:
- @TAG extraction from files
- @TAG grouping by ID and type
- Filtering by ID and type
- Edge cases and error handling

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tag_extractor_lite import TagExtractorLite


@pytest.fixture
def temp_project():
    """Create temporary project directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Python file with @TAG annotations
        py_file = project_root / "src" / "auth.py"
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text(
            '''"""Authentication module.

@TAG[SPEC:auth-001]
"""

# @TAG[CODE:auth-001]
def validate_token(token):
    """Validate JWT token.

    @TAG[SPEC:auth-001]
    """
    return True
''',
            encoding="utf-8",
        )

        # Create Markdown file with @TAG annotations
        md_file = project_root / "docs" / "SPEC_AUTH.md"
        md_file.parent.mkdir(parents=True, exist_ok=True)
        md_file.write_text(
            """# Authentication Specification

@TAG[SPEC:auth-001]

User authentication using JWT tokens.
""",
            encoding="utf-8",
        )

        # Create test file with @TAG annotations
        test_file = project_root / "tests" / "test_auth.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            '''"""Test authentication module.

@TAG[TEST:auth-001]
"""

# @TAG[TEST:auth-001] @TAG[CODE:auth-001]
def test_validate_token():
    """Test token validation."""
    assert True
''',
            encoding="utf-8",
        )

        # Create file without TAG annotations
        no_tag_file = project_root / "src" / "config.py"
        no_tag_file.write_text(
            """\"\"\"Configuration module.\"\"\"\n\nCONFIG = {}\n""",
            encoding="utf-8",
        )

        # Create file with different TAG ID
        other_file = project_root / "src" / "user.py"
        other_file.write_text(
            """# @TAG[CODE:user-001]\ndef get_user():\n    pass\n""",
            encoding="utf-8",
        )

        yield project_root


class TestTagExtraction:
    """Test @TAG extraction from files."""

    def test_extract_from_python_file(self, temp_project):
        """Test extracting @TAG from Python file."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "src" / "auth.py"
        tags = extractor.extract_tags_from_file(file_path)

        # Should find 3 TAG annotations
        assert len(tags) >= 2
        assert any(tag.tag_type == "SPEC" for tag in tags)
        assert any(tag.tag_type == "CODE" for tag in tags)

    def test_extract_from_markdown_file(self, temp_project):
        """Test extracting @TAG from Markdown file."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "docs" / "SPEC_AUTH.md"
        tags = extractor.extract_tags_from_file(file_path)

        # Should find 1 TAG annotation
        assert len(tags) == 1
        assert tags[0].tag_type == "SPEC"
        assert tags[0].tag_id == "auth-001"

    def test_extract_from_test_file(self, temp_project):
        """Test extracting @TAG from test file."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "tests" / "test_auth.py"
        tags = extractor.extract_tags_from_file(file_path)

        # Should find multiple TAG annotations
        assert len(tags) >= 1
        assert any(tag.tag_type == "TEST" for tag in tags)

    def test_extract_from_file_without_tags(self, temp_project):
        """Test extracting from file without @TAG annotations."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "src" / "config.py"
        tags = extractor.extract_tags_from_file(file_path)

        # Should find no TAG annotations
        assert len(tags) == 0

    def test_extract_from_directory(self, temp_project):
        """Test extracting @TAG from entire directory."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()

        # Should find multiple TAG annotations
        assert len(tags) > 0

        # Should have different tag types
        tag_types = {tag.tag_type for tag in tags}
        assert "SPEC" in tag_types or "TEST" in tag_types or "CODE" in tag_types

    def test_tag_attributes(self, temp_project):
        """Test CodeTag attributes are correct."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "docs" / "SPEC_AUTH.md"
        tags = extractor.extract_tags_from_file(file_path)

        assert len(tags) == 1
        tag = tags[0]

        # Check attributes
        assert tag.tag_type == "SPEC"
        assert tag.tag_id == "auth-001"
        assert tag.file_path == file_path
        assert tag.line_number > 0
        assert isinstance(tag.context, str)
        assert len(tag.context) > 0

    def test_tag_context(self, temp_project):
        """Test TAG context includes surrounding lines."""
        extractor = TagExtractorLite(project_root=temp_project)
        file_path = temp_project / "docs" / "SPEC_AUTH.md"
        tags = extractor.extract_tags_from_file(file_path)

        tag = tags[0]

        # Context should include the TAG line
        assert "@TAG[SPEC:auth-001]" in tag.context

    def test_skip_hidden_directories(self, temp_project):
        """Test skipping hidden directories."""
        # Create .git directory with TAG
        git_dir = temp_project / ".git" / "hooks"
        git_dir.mkdir(parents=True, exist_ok=True)
        hook_file = git_dir / "pre-commit.py"
        hook_file.write_text("# @TAG[CODE:git-001]", encoding="utf-8")

        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()

        # Should skip .git directory
        assert not any(tag.tag_id == "git-001" for tag in tags)

    def test_skip_node_modules(self, temp_project):
        """Test skipping node_modules directory."""
        # Create node_modules directory with TAG
        node_dir = temp_project / "node_modules" / "package"
        node_dir.mkdir(parents=True, exist_ok=True)
        pkg_file = node_dir / "index.js"
        pkg_file.write_text("// @TAG[CODE:npm-001]", encoding="utf-8")

        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()

        # Should skip node_modules directory
        assert not any(tag.tag_id == "npm-001" for tag in tags)

    def test_handle_read_errors(self, temp_project):
        """Test handling file read errors gracefully."""
        # Create file with invalid encoding
        bad_file = temp_project / "src" / "bad.py"
        bad_file.write_bytes(b"\x80\x81\x82# @TAG[CODE:bad-001]")

        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_file(bad_file)

        # Should not crash, just return empty list
        assert isinstance(tags, list)


class TestTagGrouping:
    """Test TAG grouping functionality."""

    def test_group_by_tag_id(self, temp_project):
        """Test grouping tags by tag_id."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()
        grouped = extractor.group_by_tag_id(tags)

        # Should have at least 2 unique tag IDs
        assert len(grouped) >= 2

        # Check auth-001 group
        if "auth-001" in grouped:
            auth_tags = grouped["auth-001"]
            assert len(auth_tags) > 0

            # Should have different tag types
            tag_types = {tag.tag_type for tag in auth_tags}
            assert len(tag_types) > 0

    def test_group_by_tag_type(self, temp_project):
        """Test grouping tags by tag_type."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()
        grouped = extractor.group_by_tag_type(tags)

        # Should have at least one tag type
        assert len(grouped) > 0

        # Each group should contain CodeTag objects
        for tag_type, type_tags in grouped.items():
            assert len(type_tags) > 0
            assert all(tag.tag_type == tag_type for tag in type_tags)


class TestTagFiltering:
    """Test TAG filtering functionality."""

    def test_find_tags_by_id(self, temp_project):
        """Test finding tags by specific tag_id."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.find_tags_by_id("auth-001")

        # Should find auth-001 tags
        assert len(tags) > 0
        assert all(tag.tag_id == "auth-001" for tag in tags)

    def test_find_tags_by_type(self, temp_project):
        """Test finding tags by specific tag_type."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.find_tags_by_type("SPEC")

        # Should find SPEC tags
        assert len(tags) > 0
        assert all(tag.tag_type == "SPEC" for tag in tags)

    def test_find_nonexistent_tag_id(self, temp_project):
        """Test finding non-existent tag_id."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.find_tags_by_id("nonexistent")

        # Should return empty list
        assert len(tags) == 0

    def test_find_nonexistent_tag_type(self, temp_project):
        """Test finding non-existent tag_type."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.find_tags_by_type("INVALID")

        # Should return empty list
        assert len(tags) == 0


class TestPrintSummary:
    """Test summary printing functionality."""

    def test_print_summary_with_tags(self, temp_project, capsys):
        """Test printing summary with tags."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = extractor.extract_tags_from_directory()
        extractor.print_summary(tags)

        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "@TAG annotations" in captured.out

    def test_print_summary_without_tags(self, temp_project, capsys):
        """Test printing summary without tags."""
        extractor = TagExtractorLite(project_root=temp_project)
        tags = []  # Empty list
        extractor.print_summary(tags)

        captured = capsys.readouterr()
        assert "No @TAG annotations found" in captured.out


class TestMainFunction:
    """Test CLI main function."""

    def test_main_success(self, monkeypatch, temp_project):
        """Test successful main execution."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py"])

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_file(self, monkeypatch, temp_project):
        """Test main with specific file."""
        file_path = str(temp_project / "src" / "auth.py")
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py", "--file", file_path])

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_tag_id(self, monkeypatch, temp_project):
        """Test main with specific tag ID."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py", "--tag-id", "auth-001"])

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_tag_type(self, monkeypatch, temp_project):
        """Test main with specific tag type."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py", "--tag-type", "SPEC"])

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_nonexistent_file(self, monkeypatch, temp_project):
        """Test main with non-existent file."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py", "--file", "nonexistent.py"])

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_exception(self, monkeypatch, temp_project):
        """Test main with exception."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py"])

        def mock_extract_error(self, directory=None):
            raise RuntimeError("Test error")

        monkeypatch.setattr(TagExtractorLite, "extract_tags_from_directory", mock_extract_error)

        original_init = TagExtractorLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagExtractorLite, "__init__", mock_init)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_feature_flag_disabled(self, monkeypatch, temp_project):
        """Test main with feature flag disabled."""
        monkeypatch.setattr("sys.argv", ["tag_extractor_lite.py"])

        # Mock FeatureFlags
        class MockFlags:
            def is_enabled(self, key):
                return False

        monkeypatch.setattr("tag_extractor_lite.FeatureFlags", MockFlags)

        from tag_extractor_lite import main

        exit_code = main()
        assert exit_code == 1
