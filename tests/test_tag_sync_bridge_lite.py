"""Tests for TAG Sync Bridge Lite.

Test Coverage:
- TAG note creation
- Obsidian note generation
- Hierarchical tag mapping
- Traceability map generation
- Synchronization workflow

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

from tag_extractor_lite import CodeTag
from tag_sync_bridge_lite import TagSyncBridgeLite


@pytest.fixture
def temp_vault():
    """Create temporary Obsidian vault."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "vault"
        vault_path.mkdir()
        yield vault_path


@pytest.fixture
def temp_project():
    """Create temporary project with @TAG annotations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Python file with @TAG
        py_file = project_root / "src" / "auth.py"
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text(
            '''"""Auth module.

@TAG[SPEC:auth-001]
"""

# @TAG[CODE:auth-001]
def validate_token():
    pass
''',
            encoding="utf-8",
        )

        # Create test file with @TAG
        test_file = project_root / "tests" / "test_auth.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            '''"""Test auth.

@TAG[TEST:auth-001]
"""

def test_auth():
    pass
''',
            encoding="utf-8",
        )

        yield project_root


@pytest.fixture
def sample_tag():
    """Create sample CodeTag."""
    return CodeTag(
        tag_type="SPEC",
        tag_id="auth-001",
        file_path=Path("src/auth.py"),
        line_number=15,
        context="# @TAG[SPEC:auth-001]\ndef validate_token():\n    pass",
    )


class TestInitialization:
    """Test TagSyncBridge initialization."""

    def test_init_creates_directories(self, temp_vault):
        """Test initialization creates required directories."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)

        # Check directories exist
        assert bridge.requirements_dir.exists()
        assert bridge.implementations_dir.exists()
        assert bridge.tests_dir.exists()
        assert bridge.docs_dir.exists()

    def test_init_with_project_root(self, temp_vault, temp_project):
        """Test initialization with project root."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)

        assert bridge.tag_extractor.project_root == temp_project


class TestTagNoteCreation:
    """Test TAG note creation."""

    def test_create_spec_note(self, temp_vault, sample_tag):
        """Test creating SPEC note."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        note_path = bridge.create_tag_note(sample_tag)

        # Check note created
        assert note_path.exists()
        assert note_path.parent == bridge.requirements_dir
        assert note_path.name == "REQ-AUTH-001.md"

        # Check content
        content = note_path.read_text(encoding="utf-8")
        assert "SPEC: AUTH-001" in content
        assert "auth.py:15" in content  # Cross-platform path check
        assert sample_tag.context in content

    def test_create_code_note(self, temp_vault):
        """Test creating CODE note."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="CODE",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=20,
            context="def validate_token():\n    pass",
        )

        note_path = bridge.create_tag_note(tag)

        assert note_path.exists()
        assert note_path.parent == bridge.implementations_dir
        assert note_path.name == "IMPL-AUTH-001.md"

    def test_create_test_note(self, temp_vault):
        """Test creating TEST note."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="TEST",
            tag_id="auth-001",
            file_path=Path("tests/test_auth.py"),
            line_number=10,
            context="def test_auth():\n    pass",
        )

        note_path = bridge.create_tag_note(tag)

        assert note_path.exists()
        assert note_path.parent == bridge.tests_dir
        assert note_path.name == "TEST-AUTH-001.md"

    def test_create_doc_note(self, temp_vault):
        """Test creating DOC note."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="DOC",
            tag_id="auth-001",
            file_path=Path("docs/auth.md"),
            line_number=5,
            context="# Auth Documentation",
        )

        note_path = bridge.create_tag_note(tag)

        assert note_path.exists()
        assert note_path.parent == bridge.docs_dir
        assert note_path.name == "DOC-AUTH-001.md"

    def test_update_existing_note(self, temp_vault, sample_tag):
        """Test updating existing TAG note."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)

        # Create initial note
        note_path = bridge.create_tag_note(sample_tag)

        # Create tag with different location
        updated_tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001",
            file_path=Path("src/middleware/auth.py"),
            line_number=30,
            context="# Different location",
        )

        # Update note
        updated_path = bridge.create_tag_note(updated_tag)

        assert updated_path == note_path
        updated_content = note_path.read_text(encoding="utf-8")

        # Check both locations are present (cross-platform)
        assert "auth.py:15" in updated_content
        assert "middleware" in updated_content and "auth.py:30" in updated_content


class TestHierarchicalTags:
    """Test hierarchical tag generation."""

    def test_generate_spec_tag(self, temp_vault):
        """Test generating SPEC hierarchical tag."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        hierarchical = bridge._generate_hierarchical_tag(tag)
        assert hierarchical == "req/auth-001"

    def test_generate_code_tag(self, temp_vault):
        """Test generating CODE hierarchical tag."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="CODE",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        hierarchical = bridge._generate_hierarchical_tag(tag)
        assert hierarchical == "impl/auth-001"

    def test_generate_test_tag(self, temp_vault):
        """Test generating TEST hierarchical tag."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        tag = CodeTag(
            tag_type="TEST",
            tag_id="auth-001",
            file_path=Path("tests/test_auth.py"),
            line_number=10,
            context="",
        )

        hierarchical = bridge._generate_hierarchical_tag(tag)
        assert hierarchical == "test/auth-001"


class TestSynchronization:
    """Test TAG synchronization."""

    def test_sync_all_tags(self, temp_vault, temp_project):
        """Test syncing all tags from project."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)
        created_notes = bridge.sync_all_tags()

        # Check notes were created
        assert len(created_notes["SPEC"]) > 0
        assert len(created_notes["CODE"]) > 0
        assert len(created_notes["TEST"]) > 0

    def test_sync_specific_tag_id(self, temp_vault, temp_project):
        """Test syncing specific TAG ID."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)
        created_notes = bridge.sync_all_tags(tag_id="auth-001")

        # Check only auth-001 tags were synced
        total_notes = sum(len(notes) for notes in created_notes.values())
        assert total_notes > 0

        # Verify note paths
        for notes in created_notes.values():
            for note in notes:
                assert "AUTH-001" in note.name.upper()

    def test_sync_empty_project(self, temp_vault):
        """Test syncing project with no tags."""
        empty_project = Path(tempfile.mkdtemp())
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=empty_project)
        created_notes = bridge.sync_all_tags()

        # No notes should be created
        total_notes = sum(len(notes) for notes in created_notes.values())
        assert total_notes == 0


class TestTraceabilityMap:
    """Test traceability map generation."""

    def test_generate_traceability_map(self, temp_vault, temp_project):
        """Test generating traceability map."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)
        map_path = bridge.generate_traceability_map("auth-001")

        assert map_path is not None
        assert map_path.exists()
        assert "auth-001-map.md" in map_path.name

        # Check content
        content = map_path.read_text(encoding="utf-8")
        assert "Traceability Map: AUTH-001" in content
        assert "SPEC" in content or "CODE" in content or "TEST" in content
        assert "mermaid" in content

    def test_generate_map_for_nonexistent_tag(self, temp_vault, temp_project):
        """Test generating map for non-existent TAG."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)
        map_path = bridge.generate_traceability_map("nonexistent")

        assert map_path is None

    def test_traceability_map_mermaid_diagram(self, temp_vault, temp_project):
        """Test Mermaid diagram in traceability map."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault, project_root=temp_project)
        map_path = bridge.generate_traceability_map("auth-001")

        content = map_path.read_text(encoding="utf-8")

        # Check Mermaid syntax
        assert "```mermaid" in content
        assert "graph TD" in content
        assert "```" in content


class TestPrintSummary:
    """Test summary printing."""

    def test_print_sync_summary(self, temp_vault, capsys):
        """Test printing synchronization summary."""
        bridge = TagSyncBridgeLite(vault_path=temp_vault)
        created_notes = {
            "SPEC": [Path("req1.md"), Path("req2.md")],
            "CODE": [Path("impl1.md")],
            "TEST": [],
            "DOC": [],
        }

        bridge.print_sync_summary(created_notes)

        captured = capsys.readouterr()
        assert "Synchronized 3 @TAG annotations" in captured.out
        assert "SPEC: 2 notes" in captured.out
        assert "CODE: 1 notes" in captured.out


class TestMainFunction:
    """Test CLI main function."""

    def test_main_sync_all(self, monkeypatch, temp_vault, temp_project):
        """Test main function syncing all tags."""
        monkeypatch.setattr("sys.argv", ["tag_sync_bridge_lite.py", "--vault-path", str(temp_vault)])

        original_init = TagSyncBridgeLite.__init__

        def mock_init(self, vault_path=None, project_root=None):
            original_init(self, vault_path, temp_project)

        monkeypatch.setattr(TagSyncBridgeLite, "__init__", mock_init)

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_tag_id(self, monkeypatch, temp_vault, temp_project):
        """Test main with specific TAG ID."""
        monkeypatch.setattr("sys.argv", ["tag_sync_bridge_lite.py", "--vault-path", str(temp_vault), "--tag-id", "auth-001"])

        original_init = TagSyncBridgeLite.__init__

        def mock_init(self, vault_path=None, project_root=None):
            original_init(self, vault_path, temp_project)

        monkeypatch.setattr(TagSyncBridgeLite, "__init__", mock_init)

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_generate_map(self, monkeypatch, temp_vault, temp_project):
        """Test main generating traceability map."""
        monkeypatch.setattr(
            "sys.argv", ["tag_sync_bridge_lite.py", "--vault-path", str(temp_vault), "--generate-map", "auth-001"]
        )

        original_init = TagSyncBridgeLite.__init__

        def mock_init(self, vault_path=None, project_root=None):
            original_init(self, vault_path, temp_project)

        monkeypatch.setattr(TagSyncBridgeLite, "__init__", mock_init)

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_nonexistent_vault(self, monkeypatch):
        """Test main with non-existent vault path."""
        monkeypatch.setattr("sys.argv", ["tag_sync_bridge_lite.py", "--vault-path", "/nonexistent/path"])

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_exception(self, monkeypatch, temp_vault, temp_project):
        """Test main with exception."""
        monkeypatch.setattr("sys.argv", ["tag_sync_bridge_lite.py", "--vault-path", str(temp_vault)])

        def mock_sync_error(self, tag_id=None):
            raise RuntimeError("Test error")

        monkeypatch.setattr(TagSyncBridgeLite, "sync_all_tags", mock_sync_error)

        original_init = TagSyncBridgeLite.__init__

        def mock_init(self, vault_path=None, project_root=None):
            original_init(self, vault_path, temp_project)

        monkeypatch.setattr(TagSyncBridgeLite, "__init__", mock_init)

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_feature_flag_disabled(self, monkeypatch):
        """Test main with feature flag disabled."""
        monkeypatch.setattr("sys.argv", ["tag_sync_bridge_lite.py"])

        # Mock FeatureFlags
        class MockFlags:
            def is_enabled(self, key):
                return False

        monkeypatch.setattr("tag_sync_bridge_lite.FeatureFlags", MockFlags)

        from tag_sync_bridge_lite import main

        exit_code = main()
        assert exit_code == 1
