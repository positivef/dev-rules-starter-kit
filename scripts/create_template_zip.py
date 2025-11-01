#!/usr/bin/env python3
"""
Create ZIP template for easy project distribution

Usage:
    python scripts/create_template_zip.py
"""

import zipfile
import os
from pathlib import Path


def create_template_zip():
    """Create a ZIP template from my-awesome-app"""

    starter_kit = Path(__file__).parent.parent
    output_zip = starter_kit / "project-template.zip"

    # Files to include
    template_files = {
        "config/": ["constitution.yaml"],
        "scripts/": [
            "task_executor.py",
            "session_manager.py",
            "context_provider.py",
        ],
        "src/": ["app.py"],
        "src/cli/": ["main.py"],
        "tests/": ["test_app.py"],
        "": [".gitignore", ".env", "README.md", "requirements.txt"],
    }

    print(f"Creating template ZIP: {output_zip}")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for dir_path, files in template_files.items():
            for file in files:
                src = starter_kit / dir_path / file
                if src.exists():
                    arcname = f"project-template/{dir_path}{file}"
                    zipf.write(src, arcname)
                    print(f"  Added: {arcname}")

        # Add README for template
        readme_content = """# Project Template

## Quick Start

1. Extract this ZIP
2. Rename `project-template` to your project name
3. Edit config/constitution.yaml (change project name)
4. Edit .env (change PROJECT_NAME)
5. Create virtual environment:
   ```
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
6. Initialize Git:
   ```
   git init
   git add .
   git commit -m "feat: initialize project"
   ```

Done! Start developing.
"""
        zipf.writestr("project-template/TEMPLATE_README.txt", readme_content)

    print(f"\nSUCCESS! Template created: {output_zip}")
    print(f"Size: {os.path.getsize(output_zip) / 1024:.1f} KB")
    print("\nYou can:")
    print("  - Copy this ZIP to USB")
    print("  - Share with team")
    print("  - Extract anywhere to start new project")


if __name__ == "__main__":
    create_template_zip()
