"""Tests for TAG Tracer Lite.

Test Coverage:
- TAG pattern collection
- Chain building and validation
- Orphan TAG detection
- Report generation
- CLI integration

Compliance:
- P6: Quality gate (coverage >= 95%)
- P8: Test-first development
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tag_tracer_lite import TagTracerLite


@pytest.fixture
def temp_project():
    """Create temporary project directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create sample files with @TAG annotations
        # SPEC file
        spec_file = project_root / "docs" / "SPEC_AUTH.md"
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        spec_file.write_text(
            """# Authentication Specification

@TAG[SPEC:auth-001]

User authentication using JWT tokens.
""",
            encoding="utf-8",
        )

        # TEST file
        test_file = project_root / "tests" / "test_auth.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            '''"""Test authentication module.

@TAG[TEST:auth-001]
"""

def test_login():
    """Test login functionality."""
    # @TAG[CODE:auth-001]
    assert True
''',
            encoding="utf-8",
        )

        # CODE file
        code_file = project_root / "scripts" / "auth.py"
        code_file.parent.mkdir(parents=True, exist_ok=True)
        code_file.write_text(
            '''"""Authentication module.

@TAG[CODE:auth-001]
"""

def authenticate_user(username, password):
    """Authenticate user with credentials."""
    return True
''',
            encoding="utf-8",
        )

        # DOC file
        doc_file = project_root / "docs" / "AUTH_GUIDE.md"
        doc_file.write_text(
            """# Authentication Guide

@TAG[DOC:auth-001]

How to use the authentication system.
""",
            encoding="utf-8",
        )

        # Incomplete chain (missing TEST and DOC)
        incomplete_spec = project_root / "docs" / "SPEC_INCOMPLETE.md"
        incomplete_spec.write_text(
            """# Incomplete Feature

@TAG[SPEC:incomplete-001]

This feature has no tests.
""",
            encoding="utf-8",
        )

        incomplete_code = project_root / "scripts" / "incomplete.py"
        incomplete_code.write_text(
            '''"""Incomplete feature."""

# @TAG[CODE:incomplete-001]
def incomplete_feature():
    """Feature without tests."""
    pass
''',
            encoding="utf-8",
        )

        # Orphan TAG (only CODE)
        orphan_file = project_root / "scripts" / "orphan.py"
        orphan_file.write_text(
            '''"""Orphan code."""

# @TAG[CODE:orphan-001]
def orphan_function():
    """Code without SPEC or TEST."""
    pass
''',
            encoding="utf-8",
        )

        yield project_root


class TestTagCollection:
    """Test @TAG pattern collection."""

    def test_collect_all_tags(self, temp_project):
        """Test collecting all @TAG patterns."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Should find all TAG instances
        assert "SPEC:auth-001" in tags
        assert "TEST:auth-001" in tags
        assert "CODE:auth-001" in tags
        assert "DOC:auth-001" in tags
        assert "SPEC:incomplete-001" in tags
        assert "CODE:incomplete-001" in tags
        assert "CODE:orphan-001" in tags

    def test_tag_locations(self, temp_project):
        """Test TAG locations are correctly recorded."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Check SPEC TAG location
        assert len(tags["SPEC:auth-001"]) == 1
        assert "docs" in tags["SPEC:auth-001"][0]
        assert "SPEC_AUTH.md" in tags["SPEC:auth-001"][0]

    def test_multiple_tags_same_type(self, temp_project):
        """Test multiple TAGs of same type for same ID."""
        # Add second CODE TAG for auth-001
        code_file = temp_project / "scripts" / "user.py"
        code_file.write_text(
            '''"""User module."""

# @TAG[CODE:auth-001]
def get_user():
    """Get user."""
    pass
''',
            encoding="utf-8",
        )

        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Should have 3 CODE TAG locations for auth-001
        # (auth.py, user.py, test_auth.py inline comment)
        assert len(tags["CODE:auth-001"]) >= 2

    def test_skip_non_source_files(self, temp_project):
        """Test skipping non-source files."""
        # Create binary file
        binary_file = temp_project / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Should not fail on binary files
        assert isinstance(tags, dict)

    def test_skip_hidden_directories(self, temp_project):
        """Test skipping hidden directories."""
        # Create .git directory with TAG
        git_dir = temp_project / ".git" / "hooks"
        git_dir.mkdir(parents=True, exist_ok=True)
        hook_file = git_dir / "pre-commit.py"
        hook_file.write_text("# @TAG[CODE:git-001]", encoding="utf-8")

        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Should skip .git directory
        assert "CODE:git-001" not in tags

    def test_collect_handles_read_errors(self, temp_project):
        """Test collect_all_tags handles file read errors gracefully."""
        # Create file with invalid encoding
        bad_file = temp_project / "scripts" / "bad.py"
        bad_file.write_bytes(b"\x80\x81\x82# @TAG[CODE:bad-001]")

        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()

        # Should not crash, just skip unreadable files
        assert isinstance(tags, dict)


class TestChainBuilding:
    """Test TAG chain building."""

    def test_build_chains(self, temp_project):
        """Test building TAG chains."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()
        chains = tracer.build_chains(tags)

        # Should have 3 chains (auth-001, incomplete-001, orphan-001)
        assert len(chains) == 3

        # Find auth-001 chain
        auth_chain = next(c for c in chains if c["id"] == "auth-001")
        assert set(auth_chain["types"]) == {"SPEC", "TEST", "CODE", "DOC"}
        assert len(auth_chain["missing"]) == 0

    def test_chain_missing_types(self, temp_project):
        """Test identifying missing TAG types in chain."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()
        chains = tracer.build_chains(tags)

        # Find incomplete-001 chain
        incomplete_chain = next(c for c in chains if c["id"] == "incomplete-001")
        assert "SPEC" in incomplete_chain["types"]
        assert "CODE" in incomplete_chain["types"]
        assert "TEST" in incomplete_chain["missing"]
        assert "DOC" in incomplete_chain["missing"]

    def test_chain_locations(self, temp_project):
        """Test chain locations are preserved."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()
        chains = tracer.build_chains(tags)

        # Find auth-001 chain
        auth_chain = next(c for c in chains if c["id"] == "auth-001")
        assert "SPEC" in auth_chain["locations"]
        assert "TEST" in auth_chain["locations"]
        assert "CODE" in auth_chain["locations"]
        assert "DOC" in auth_chain["locations"]


class TestOrphanDetection:
    """Test orphan TAG detection."""

    def test_find_orphan_tags(self, temp_project):
        """Test finding orphan TAGs."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()
        chains = tracer.build_chains(tags)
        orphans = tracer.find_orphan_tags(chains)

        # Should find orphan-001
        assert "orphan-001" in orphans

    def test_no_orphans_for_complete_chain(self, temp_project):
        """Test complete chains are not marked as orphans."""
        tracer = TagTracerLite(project_root=temp_project)
        tags = tracer.collect_all_tags()
        chains = tracer.build_chains(tags)
        orphans = tracer.find_orphan_tags(chains)

        # auth-001 is complete, not orphan
        assert "auth-001" not in orphans


class TestVerification:
    """Test TAG chain verification."""

    def test_verify_all_chains(self, temp_project):
        """Test verifying all TAG chains."""
        tracer = TagTracerLite(project_root=temp_project)
        report = tracer.verify_tag_chain()

        assert report["total_chains"] == 3
        assert report["complete_chains"] == 1  # Only auth-001
        assert report["incomplete_chains"] == 2  # incomplete-001, orphan-001
        assert "orphan-001" in report["orphan_tags"]

    def test_verify_specific_chain(self, temp_project):
        """Test verifying specific TAG chain."""
        tracer = TagTracerLite(project_root=temp_project)
        report = tracer.verify_tag_chain(tag_id="auth-001")

        assert report["total_chains"] == 1
        assert report["complete_chains"] == 1
        assert len(report["chains"]) == 1
        assert report["chains"][0]["id"] == "auth-001"

    def test_verify_nonexistent_chain(self, temp_project):
        """Test verifying non-existent TAG chain."""
        tracer = TagTracerLite(project_root=temp_project)
        report = tracer.verify_tag_chain(tag_id="nonexistent")

        assert "error" in report

    def test_validate_complete_chain(self, temp_project):
        """Test validating complete TAG chain."""
        tracer = TagTracerLite(project_root=temp_project)
        is_valid = tracer.validate_chain("auth-001")

        assert is_valid is True

    def test_validate_incomplete_chain(self, temp_project):
        """Test validating incomplete TAG chain."""
        tracer = TagTracerLite(project_root=temp_project)
        is_valid = tracer.validate_chain("incomplete-001")

        assert is_valid is False

    def test_validate_nonexistent_chain(self, temp_project):
        """Test validating non-existent TAG chain."""
        tracer = TagTracerLite(project_root=temp_project)
        is_valid = tracer.validate_chain("nonexistent")

        assert is_valid is False


class TestReportGeneration:
    """Test report generation."""

    def test_print_report(self, temp_project, capsys):
        """Test printing verification report."""
        tracer = TagTracerLite(project_root=temp_project)
        tracer.verify_tag_chain()

        captured = capsys.readouterr()
        assert "TAG Chain Verification Report" in captured.out
        assert "Total TAG instances" in captured.out
        assert "Complete chains: 1" in captured.out
        assert "Incomplete chains: 2" in captured.out

    def test_print_orphan_warning(self, temp_project, capsys):
        """Test orphan TAG warning in report."""
        tracer = TagTracerLite(project_root=temp_project)
        tracer.verify_tag_chain()

        captured = capsys.readouterr()
        assert "[WARN] Orphan TAGs" in captured.out
        assert "orphan-001" in captured.out

    def test_print_incomplete_warning(self, temp_project, capsys):
        """Test incomplete chain warning in report."""
        tracer = TagTracerLite(project_root=temp_project)
        tracer.verify_tag_chain()

        captured = capsys.readouterr()
        assert "[WARN] Incomplete chains" in captured.out
        assert "incomplete-001" in captured.out


class TestMainFunction:
    """Test CLI main function."""

    def test_main_success(self, monkeypatch, temp_project):
        """Test successful main execution."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py"])

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_tag_id(self, monkeypatch, temp_project):
        """Test main with specific TAG ID."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py", "--tag-id", "auth-001"])

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_validate_complete_chain(self, monkeypatch, temp_project):
        """Test main with validation for complete chain."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py", "--validate", "--tag-id", "auth-001"])

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_validate_incomplete_chain(self, monkeypatch, temp_project):
        """Test main with validation for incomplete chain."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py", "--validate", "--tag-id", "incomplete-001"])

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 1  # Should fail validation

    def test_main_validate_all_with_incomplete(self, monkeypatch, temp_project):
        """Test main with validation for all chains (has incomplete)."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py", "--validate"])

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 1  # Should fail validation

    def test_main_with_exception(self, monkeypatch, temp_project):
        """Test main function with exception."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py"])

        def mock_verify_error(self, tag_id=None):
            raise RuntimeError("Test error")

        monkeypatch.setattr(TagTracerLite, "verify_tag_chain", mock_verify_error)

        original_init = TagTracerLite.__init__

        def mock_init(self, project_root=None):
            original_init(self, temp_project)

        monkeypatch.setattr(TagTracerLite, "__init__", mock_init)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_feature_flag_disabled(self, monkeypatch, temp_project):
        """Test main with feature flag disabled."""
        monkeypatch.setattr("sys.argv", ["tag_tracer_lite.py"])

        # Mock FeatureFlags
        class MockFlags:
            def is_enabled(self, key):
                return False

        monkeypatch.setattr("tag_tracer_lite.FeatureFlags", MockFlags)

        from tag_tracer_lite import main

        exit_code = main()
        assert exit_code == 1
