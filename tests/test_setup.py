
import unittest
from unittest.mock import patch
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add scripts directory to path to allow importing setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import setup

class TestSetupScript(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create dummy files and templates needed for the test
        Path("README.md").write_text("Project: PROJECT_NAME")
        Path("TASKS").mkdir()
        Path("TASKS/TEMPLATE.yaml").write_text("project: PROJECT_NAME")
        
        templates_path = Path("templates")
        (templates_path / "general").mkdir(parents=True)
        (templates_path / "fastapi").mkdir(parents=True)

        (templates_path / "general" / ".editorconfig").write_text("general_config")
        (templates_path / "fastapi" / "Dockerfile").write_text("fastapi_dockerfile")
        (templates_path / "fastapi" / ".editorconfig").write_text("fastapi_specific_config") # To test override

    def tearDown(self):
        """Clean up the temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('setup.run_command') # We don't want to run pip/pre-commit in tests
    def test_scaffolding_with_framework(self, mock_run_command):
        """Test that scaffolding copies general and framework-specific files."""
        # Arrange
        project_name = "MyTestApp"
        framework = "fastapi"
        sys.argv = ["setup.py", "--project-name", project_name, "--framework", framework]

        # Act
        setup.main()

        # Assert
        # 1. Check if placeholder was replaced
        readme_content = Path("README.md").read_text()
        self.assertIn(project_name, readme_content)

        # 2. Check if template files were copied
        self.assertTrue(Path("Dockerfile").exists())
        self.assertEqual(Path("Dockerfile").read_text(), "fastapi_dockerfile")

        # 3. Check that framework-specific file overrides general file
        self.assertTrue(Path(".editorconfig").exists())
        self.assertEqual(Path(".editorconfig").read_text(), "fastapi_specific_config")

    @patch('setup.run_command')
    def test_scaffolding_without_framework(self, mock_run_command):
        """Test that scaffolding copies only general files when no framework is specified."""
        # Arrange
        project_name = "MySimpleApp"
        sys.argv = ["setup.py", "--project-name", project_name]

        # Act
        setup.main()

        # Assert
        self.assertFalse(Path("Dockerfile").exists()) # Should not be copied
        self.assertTrue(Path(".editorconfig").exists())
        self.assertEqual(Path(".editorconfig").read_text(), "general_config")

if __name__ == '__main__':
    unittest.main()
