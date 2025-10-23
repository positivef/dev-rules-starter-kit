"""
Test Project Steering System (cc-sdd Trust 8.3 pattern)

Based on: /gotalab/cc-sdd steering system
Pattern: /kiro:steering command
Validation: TDD-first approach
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
import sys


class TestProjectSteering:
    """Test project steering document generation (cc-sdd pattern)"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure for testing"""
        temp_dir = Path(tempfile.mkdtemp())

        # Create typical project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "tests").mkdir()
        (temp_dir / "docs").mkdir()

        # Create package.json (Node.js project)
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {"react": "^18.0.0", "typescript": "^5.0.0"},
            "devDependencies": {"jest": "^29.0.0", "eslint": "^8.0.0"},
        }
        with open(temp_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create some source files
        (temp_dir / "src" / "index.ts").write_text("export const hello = 'world';")
        (temp_dir / "tests" / "index.test.ts").write_text("test('hello', () => {});")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_steering_directory_creation(self, temp_project):
        """Test: Creates dev-context/ directory for steering docs"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        steering.generate()

        steering_dir = temp_project / "dev-context"
        assert steering_dir.exists()
        assert steering_dir.is_dir()

    def test_tech_stack_analysis(self, temp_project):
        """Test: Analyzes tech stack from package.json"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        tech = steering.analyze_tech_stack()

        # Should detect dependencies
        assert "react" in tech["dependencies"]
        assert "typescript" in tech["dependencies"]
        assert "jest" in tech["devDependencies"]
        assert "eslint" in tech["devDependencies"]

        # Should detect package manager
        assert tech["package_manager"] == "npm"

    def test_project_structure_analysis(self, temp_project):
        """Test: Analyzes project structure"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        structure = steering.analyze_project_structure()

        # Should detect directories
        assert "src" in structure["directories"]
        assert "tests" in structure["directories"]
        assert "docs" in structure["directories"]

        # Should detect file types
        assert ".ts" in structure["file_types"]

    def test_tech_md_generation(self, temp_project):
        """Test: Generates tech.md steering document"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        steering.generate()

        tech_md = temp_project / "dev-context" / "tech.md"
        assert tech_md.exists()

        content = tech_md.read_text()
        assert "# Tech Stack" in content
        assert "react" in content.lower()
        assert "typescript" in content.lower()
        assert "jest" in content.lower()

    def test_structure_md_generation(self, temp_project):
        """Test: Generates structure.md steering document"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        steering.generate()

        structure_md = temp_project / "dev-context" / "structure.md"
        assert structure_md.exists()

        content = structure_md.read_text()
        assert "# Project Structure" in content
        assert "src/" in content
        assert "tests/" in content

    def test_product_md_template(self, temp_project):
        """Test: Creates product.md template"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        steering.generate()

        product_md = temp_project / "dev-context" / "product.md"
        assert product_md.exists()

        content = product_md.read_text()
        assert "# Product Requirements" in content
        assert "test-project" in content

    def test_steering_update_preserves_custom_content(self, temp_project):
        """Test: Updates steering without losing custom content (cc-sdd pattern)"""
        from scripts.project_steering import ProjectSteering

        # First generation
        steering = ProjectSteering(temp_project)
        steering.generate()

        # Add custom content
        tech_md = temp_project / "dev-context" / "tech.md"
        original_content = tech_md.read_text()
        custom_section = "\n\n## Custom Notes\n\nThis is my custom note."
        tech_md.write_text(original_content + custom_section)

        # Second generation (update)
        steering.generate()

        # Custom content should be preserved
        updated_content = tech_md.read_text()
        assert "Custom Notes" in updated_content
        assert "This is my custom note" in updated_content

    def test_steering_metadata_json(self, temp_project):
        """Test: Creates metadata.json for steering docs"""
        from scripts.project_steering import ProjectSteering

        steering = ProjectSteering(temp_project)
        steering.generate()

        metadata = temp_project / "dev-context" / "metadata.json"
        assert metadata.exists()

        data = json.loads(metadata.read_text())
        assert "created_at" in data
        assert "updated_at" in data
        assert "tech_stack" in data
        assert "project_structure" in data

    def test_python_project_detection(self):
        """Test: Detects Python projects (requirements.txt)"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create Python project
            (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\nrequests>=2.28.0")
            (temp_dir / "src").mkdir()
            (temp_dir / "tests").mkdir()

            from scripts.project_steering import ProjectSteering

            steering = ProjectSteering(temp_dir)
            tech = steering.analyze_tech_stack()

            assert tech["package_manager"] == "pip"
            assert "pytest" in tech["dependencies"]
            assert "requests" in tech["dependencies"]
        finally:
            shutil.rmtree(temp_dir)


class TestSteeringCLI:
    """Test CLI interface for steering generation"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure for testing"""
        temp_dir = Path(tempfile.mkdtemp())

        # Create typical project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "package.json").write_text('{"name": "test"}')

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_cli_help(self):
        """Test: CLI shows help message"""
        import subprocess

        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "scripts/project_steering.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )

        assert result.returncode == 0
        assert "Generate project steering documents" in result.stdout

    def test_cli_dry_run(self, temp_project):
        """Test: CLI dry-run mode (preview without writing)"""
        import subprocess
        import sys

        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / "scripts" / "project_steering.py"

        result = subprocess.run(
            [sys.executable, str(script_path), "--dry-run", "--project-root", str(temp_project)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "[DRY RUN]" in result.stdout

        # Should not create files in dry-run
        steering_dir = temp_project / "dev-context"
        assert not steering_dir.exists()


class TestSteeringValidation:
    """Test steering document validation (Quality Gates)"""

    def test_missing_dependencies_warning(self):
        """Test: Warns if no package manager detected"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Empty project (no package.json or requirements.txt)
            (temp_dir / "src").mkdir()

            from scripts.project_steering import ProjectSteering

            steering = ProjectSteering(temp_dir)

            with pytest.warns(UserWarning, match="No package manager detected"):
                steering.generate()
        finally:
            shutil.rmtree(temp_dir)

    def test_missing_tests_warning(self):
        """Test: Warns if no test directory found"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Project without tests/
            (temp_dir / "src").mkdir()
            (temp_dir / "package.json").write_text('{"name": "test"}')

            from scripts.project_steering import ProjectSteering

            steering = ProjectSteering(temp_dir)

            with pytest.warns(UserWarning, match="No test directory found"):
                steering.generate()
        finally:
            shutil.rmtree(temp_dir)
