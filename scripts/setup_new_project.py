#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup New Project - GitHub Template Setup Script
================================================

Stage 6 Phase 1: Template Packaging

Purpose: Automate initial setup when creating new project from GitHub Template

Features:
- Change project name (interactive)
- Create Python virtual environment
- Install dependencies automatically
- Install pre-commit hooks
- Generate .env file
- Prepare first commit

Usage:
    python scripts/setup_new_project.py
    python scripts/setup_new_project.py --project-name "MyProject"
    python scripts/setup_new_project.py --skip-venv
"""

import sys
import subprocess
import argparse
from pathlib import Path


class ProjectSetup:
    """New project initial setup"""

    def __init__(self, project_name: str = None, skip_venv: bool = False):
        self.project_root = Path.cwd()
        self.project_name = project_name
        self.skip_venv = skip_venv

    def run(self) -> bool:
        """Execute full setup"""
        print("\n" + "=" * 60)
        print("Dev Rules Starter Kit - New Project Setup")
        print("=" * 60 + "\n")

        # 1. Project name input
        if not self.project_name:
            self.project_name = input("Enter project name (e.g., MyAwesomeProject): ").strip()
            if not self.project_name:
                print("[ERROR] Project name is required")
                return False

        print(f"\n[INFO] Project name: {self.project_name}")

        # 2. Create Python virtual environment
        if not self.skip_venv:
            if not self._create_venv():
                return False

        # 3. Install dependencies
        if not self._install_dependencies():
            return False

        # 4. Install pre-commit hooks
        if not self._install_hooks():
            return False

        # 5. Create .env file
        if not self._create_env_file():
            return False

        # 6. Print success message
        self._print_success()

        return True

    def _create_venv(self) -> bool:
        """Create Python virtual environment"""
        print("\n[1/4] Creating Python virtual environment...")

        venv_path = self.project_root / ".venv"

        if venv_path.exists():
            print(f"  [SKIP] Virtual environment already exists: {venv_path}")
            return True

        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print(f"  [OK] Virtual environment created: {venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to create virtual environment: {e}")
            return False

    def _install_dependencies(self) -> bool:
        """Install dependencies"""
        print("\n[2/4] Installing dependencies...")

        # Venv Python path
        if sys.platform == "win32":
            python_exe = self.project_root / ".venv" / "Scripts" / "python.exe"
            pip_exe = self.project_root / ".venv" / "Scripts" / "pip.exe"
        else:
            python_exe = self.project_root / ".venv" / "bin" / "python"
            pip_exe = self.project_root / ".venv" / "bin" / "pip"

        # Use system Python if venv doesn't exist
        if not python_exe.exists():
            python_exe = sys.executable
            pip_exe = "pip"

        requirements = self.project_root / "requirements.txt"

        if not requirements.exists():
            print("  [SKIP] No requirements.txt found")
            return True

        try:
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
            print("  [OK] Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to install dependencies: {e}")
            return False

    def _install_hooks(self) -> bool:
        """Install pre-commit hooks"""
        print("\n[3/4] Installing pre-commit hooks...")

        # Venv Python path
        if sys.platform == "win32":
            precommit_exe = self.project_root / ".venv" / "Scripts" / "pre-commit.exe"
        else:
            precommit_exe = self.project_root / ".venv" / "bin" / "pre-commit"

        # Install pre-commit if not exists
        if not precommit_exe.exists():
            print("  [INFO] Installing pre-commit...")
            try:
                if sys.platform == "win32":
                    pip_exe = self.project_root / ".venv" / "Scripts" / "pip.exe"
                else:
                    pip_exe = self.project_root / ".venv" / "bin" / "pip"

                subprocess.run([str(pip_exe), "install", "pre-commit"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"  [ERROR] Failed to install pre-commit: {e}")
                return False

        # Install pre-commit hooks
        try:
            subprocess.run([str(precommit_exe), "install"], check=True)
            subprocess.run([str(precommit_exe), "install", "--hook-type", "commit-msg"], check=True)
            print("  [OK] Pre-commit hooks installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to install hooks: {e}")
            print("  [INFO] You can install manually: pre-commit install")
            return True  # Non-blocking

    def _create_env_file(self) -> bool:
        """Create .env file"""
        print("\n[4/4] Creating .env file...")

        env_file = self.project_root / ".env"

        if env_file.exists():
            print("  [SKIP] .env file already exists")
            return True

        # Obsidian path input
        print("\n  [OPTIONAL] Obsidian Vault path setup")
        print("  (You can edit .env file manually later)")
        obsidian_path = input("  Obsidian Vault path (Enter to skip): ").strip()

        if not obsidian_path:
            obsidian_path = "# OBSIDIAN_VAULT_PATH=C:\\Users\\YourName\\Documents\\ObsidianVault"

        env_content = f"""# Dev Rules Starter Kit - Environment Variables

# Project Name
PROJECT_NAME={self.project_name}

# Obsidian Integration (Optional)
{obsidian_path}

# Python Settings
PYTHONUTF8=1
"""

        try:
            env_file.write_text(env_content, encoding="utf-8")
            print(f"  [OK] .env file created: {env_file}")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to create .env file: {e}")
            return False

    def _print_success(self):
        """Print completion message"""
        print("\n" + "=" * 60)
        print("[SUCCESS] Project setup complete!")
        print("=" * 60 + "\n")

        print(f"Project: {self.project_name}")
        print(f"Location: {self.project_root}")
        print()

        print("Next steps:")
        print()
        print("1. Activate virtual environment:")
        if sys.platform == "win32":
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")
        print()
        print("2. Run your first task:")
        print("   python scripts/task_executor.py TASKS/TEMPLATE.yaml")
        print()
        print("3. Make your first commit:")
        print('   git commit -m "feat: initial project setup"')
        print()
        print("4. (Optional) Configure Obsidian:")
        print("   Edit .env file with your Obsidian Vault path")
        print()


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Setup new project from GitHub Template")
    parser.add_argument("--project-name", help="Project name (interactive if not provided)")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")

    args = parser.parse_args()

    setup = ProjectSetup(project_name=args.project_name, skip_venv=args.skip_venv)

    success = setup.run()

    if success:
        sys.exit(0)
    else:
        print("\n[FAILED] Setup incomplete")
        sys.exit(1)


if __name__ == "__main__":
    main()
