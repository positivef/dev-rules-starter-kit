#!/usr/bin/env python3
"""
New Project Initializer
Automatically creates a new project with Constitution Framework

Usage:
    python scripts/init_new_project.py my-new-app
    python scripts/init_new_project.py my-new-app --path C:/Projects
    python scripts/init_new_project.py my-new-app --minimal
    python scripts/init_new_project.py my-new-app --full
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_step(message):
    print(f"{Colors.BLUE}[*]{Colors.END} {message}")


def print_success(message):
    print(f"{Colors.GREEN}[OK]{Colors.END} {message}")


def print_warning(message):
    print(f"{Colors.YELLOW}[!]{Colors.END} {message}")


def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.END} {message}")


def run_command(cmd, cwd=None, capture=False):
    """Run shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd)
            return result.returncode == 0, ""
    except Exception as e:
        return False, str(e)


def create_project(project_name, target_path, preset="standard"):
    """Create new project with Constitution Framework"""

    # Get current script directory
    starter_kit = Path(__file__).parent.parent

    # Target project path
    project_path = Path(target_path) / project_name

    print(f"\n{Colors.BOLD}Creating new project: {project_name}{Colors.END}\n")

    # Check if project already exists
    if project_path.exists():
        print_error(f"Project already exists: {project_path}")
        return False

    # Step 1: Create directory structure
    print_step("Creating directory structure...")
    dirs = ["config", "scripts", "TASKS", "RUNS", "tests", "src", "src/cli"]
    for dir_name in dirs:
        (project_path / dir_name).mkdir(parents=True, exist_ok=True)
    print_success("Directories created")

    # Step 2: Copy essential files based on preset
    print_step(f"Copying files (preset: {preset})...")

    essential_files = {
        "config/constitution.yaml": "config/constitution.yaml",
        ".gitignore": ".gitignore",
        "CLAUDE.md": "CLAUDE.md",
    }

    essential_scripts = [
        "task_executor.py",
        "session_manager.py",
        "context_provider.py",
    ]

    if preset == "full":
        # Add more scripts for full preset
        essential_scripts.extend(
            [
                "constitutional_validator.py",
                "deep_analyzer.py",
                "obsidian_bridge.py",
            ]
        )

    # Copy config files
    for src, dst in essential_files.items():
        src_path = starter_kit / src
        dst_path = project_path / dst
        if src_path.exists():
            shutil.copy2(src_path, dst_path)

    # Copy scripts
    for script in essential_scripts:
        src_path = starter_kit / "scripts" / script
        dst_path = project_path / "scripts" / script
        if src_path.exists():
            shutil.copy2(src_path, dst_path)

    print_success(f"Files copied ({len(essential_scripts)} scripts)")

    # Step 3: Create simplified constitution.yaml
    print_step("Creating simplified constitution...")
    constitution_content = f"""# {project_name} - Constitution
# Solo Developer Setup - Level 1 (Light Mode)

constitution:
  project: "{project_name}"
  version: "1.0.0"
  developer_count: 1

adoption:
  level: 1  # Light mode
  lock_config: false

articles:
  P1_yaml_first:
    enabled: true
    threshold_lines: 10
  P4_solid:
    enabled: true
  P9_conventional_commits:
    enabled: true
  P10_windows_utf8:
    enabled: true

validation:
  enabled: true
  strict: false
  auto_fix: true

collaboration:
  enabled: false
"""
    (project_path / "config" / "constitution.yaml").write_text(constitution_content, encoding="utf-8")
    print_success("Constitution configured")

    # Step 4: Create .env file
    print_step("Creating .env file...")
    env_content = f"""PROJECT_NAME={project_name}
PROJECT_TYPE=webapp-cli
OBSIDIAN_ENABLED=false
DEBUG=true
"""
    (project_path / ".env").write_text(env_content, encoding="utf-8")
    print_success(".env created")

    # Step 5: Create README.md
    print_step("Creating README.md...")
    readme_content = f"""# {project_name}

**Framework**: Constitution-based Development (Level 1 - Light Mode)

## Quick Start

```bash
# Activate environment
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run app
python src/app.py
```

## Development Workflow

- Small changes (1-3 lines): `git commit -m "fix: ..."`
- Large changes (10+ lines): Use YAML contracts

## Commands

```bash
# Session management
python scripts/session_manager.py start
python scripts/session_manager.py save

# Code quality
ruff check src/
ruff format src/
```

Built with [Dev Rules Starter Kit](https://github.com/dev-rules-starter-kit)
"""
    (project_path / "README.md").write_text(readme_content, encoding="utf-8")
    print_success("README created")

    # Step 6: Create Python virtual environment
    print_step("Creating Python virtual environment...")
    success, _ = run_command("python -m venv .venv", cwd=project_path)
    if success:
        print_success("Virtual environment created")
    else:
        print_warning("Failed to create venv (install manually)")

    # Step 7: Install dependencies
    print_step("Installing dependencies...")
    pip_path = project_path / ".venv" / "Scripts" / "pip.exe" if os.name == "nt" else project_path / ".venv" / "bin" / "pip"

    if pip_path.exists():
        success, _ = run_command(f'"{pip_path}" install pyyaml ruff flask', cwd=project_path)
        if success:
            # Generate requirements.txt
            run_command(f'"{pip_path}" freeze > requirements.txt', cwd=project_path)
            print_success("Dependencies installed")
        else:
            print_warning("Failed to install dependencies (install manually)")

    # Step 8: Create sample Flask app
    print_step("Creating sample Flask app...")
    app_content = (
        """from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Welcome to """
        + project_name
        + """!</h1>
    <p>Constitution Framework - Ready for development</p>
    '''

@app.route('/api/status')
def status():
    return {"status": "ok", "project": \""""
        + project_name
        + """\"}

if __name__ == '__main__':
    print("[INFO] Starting """
        + project_name
        + """...")
    print("[INFO] http://localhost:5000")
    app.run(debug=True, port=5000)
"""
    )
    (project_path / "src" / "app.py").write_text(app_content, encoding="utf-8")
    print_success("Flask app created")

    # Step 9: Initialize Git
    print_step("Initializing Git repository...")
    success, _ = run_command("git init", cwd=project_path)
    if success:
        run_command("git checkout -b main", cwd=project_path)
        run_command("git add .", cwd=project_path)
        run_command(f'git commit -m "feat: initialize {project_name} with Constitution framework"', cwd=project_path)
        print_success("Git initialized and first commit created")
    else:
        print_warning("Git initialization failed (initialize manually)")

    # Final summary
    print(f"\n{Colors.GREEN}{Colors.BOLD}SUCCESS!{Colors.END} Project created: {project_path}\n")
    print(f"{Colors.BOLD}Next steps:{Colors.END}")
    print(f"  1. cd {project_path}")
    print("  2. .venv\\Scripts\\activate")
    print("  3. python src/app.py")
    print("  4. Visit http://localhost:5000\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create new project with Constitution Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/init_new_project.py my-new-app
  python scripts/init_new_project.py my-new-app --path C:/Projects
  python scripts/init_new_project.py my-new-app --minimal
  python scripts/init_new_project.py my-new-app --full
        """,
    )

    parser.add_argument("project_name", help="Name of the new project")
    parser.add_argument("--path", default=None, help="Target directory (default: ../)")
    parser.add_argument("--minimal", action="store_true", help="Minimal setup (fewer scripts)")
    parser.add_argument("--full", action="store_true", help="Full setup (all scripts)")

    args = parser.parse_args()

    # Determine preset
    if args.minimal:
        preset = "minimal"
    elif args.full:
        preset = "full"
    else:
        preset = "standard"

    # Determine target path
    if args.path:
        target_path = Path(args.path)
    else:
        # Default: parent directory of dev-rules-starter-kit
        target_path = Path(__file__).parent.parent.parent

    # Create project
    success = create_project(args.project_name, target_path, preset)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
