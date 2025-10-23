import argparse
import glob
import os
import subprocess
import sys

import shutil
from pathlib import Path

# 기본 설정
DEFAULT_PROJECT_NAME = "PROJECT_NAME"
FILES_TO_REPLACE_CONTENT = [
    "README.md",
    "DEVELOPMENT_RULES.md",
    "TASKS/TEMPLATE.yaml",
]


def copy_scaffold_files(framework: str | None):
    """템플릿 파일을 프로젝트 루트에 복사합니다."""
    print("\n[SCAFFOLD] Scaffolding project files...")

    template_dirs = ["general"]
    if framework:
        framework_dir = Path("templates") / framework
        if framework_dir.is_dir():
            template_dirs.append(framework)
            print(f"   - Framework detected: {framework}")
        else:
            print(f"   - [WARN] Framework '{framework}' not found. Skipping.", file=sys.stderr)

    for dir_name in template_dirs:
        source_dir = Path("templates") / dir_name
        for item in source_dir.iterdir():
            dest_path = Path(".") / item.name
            try:
                if item.is_dir():
                    shutil.copytree(item, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_path)
                print(f"   - Created/Updated {dest_path}")
            except Exception as e:
                print(f"   - [WARN] Could not copy {item}: {e}", file=sys.stderr)


def run_command(command, description):
    """주어진 명령어를 실행하고 결과를 출력합니다."""
    print(f"\n[EXEC] {description}")
    cmd_display = command if isinstance(command, str) else " ".join(command)
    try:
        subprocess.run(
            command,
            check=True,
            shell=isinstance(command, str),
            text=True,
            capture_output=True,
        )
        print(f"[SUCCESS] {description}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd_display}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        missing = command if isinstance(command, str) else command[0]
        print(f"[ERROR] Command not found: {missing}", file=sys.stderr)
        print("Please ensure the command is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)


def replace_project_name(project_name):
    """프로젝트 내 파일들의 플레이스홀더를 새 프로젝트 이름으로 교체합니다."""
    print(f"[REPLACE] Updating placeholders to '{project_name}'...")

    files_to_scan = FILES_TO_REPLACE_CONTENT
    all_markdown_files = glob.glob("**/*.md", recursive=True)
    files_to_scan.extend(all_markdown_files)

    for filename in files_to_scan:
        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()

                if DEFAULT_PROJECT_NAME in content:
                    new_content = content.replace(DEFAULT_PROJECT_NAME, project_name)
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"  - Updated {filename}")

            except Exception as e:
                print(f"  - [WARN] Could not process {filename}: {e}", file=sys.stderr)


def create_checkpoint():
    """Create a rollback checkpoint using git stash"""
    try:
        print("\n[CHECKPOINT] Creating checkpoint (git stash)...")
        subprocess.run(
            ["git", "stash", "push", "-u", "-m", "dev-rules-setup-checkpoint"], check=True, capture_output=True, text=True
        )
        print("   Checkpoint created successfully")
        return True
    except subprocess.CalledProcessError:
        print("   [WARN] No git repository or nothing to stash", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("   [WARN] Git not found in PATH", file=sys.stderr)
        return False


def rollback_checkpoint():
    """Rollback to checkpoint using git stash pop"""
    try:
        print("\n[ROLLBACK] Rolling back to checkpoint...")
        subprocess.run(["git", "stash", "pop"], check=True, capture_output=True, text=True)
        print("   Rollback completed")
    except subprocess.CalledProcessError as e:
        print(f"   [WARN] Rollback failed: {e}", file=sys.stderr)


def main():
    """스크립트의 메인 실행 함수입니다."""
    parser = argparse.ArgumentParser(description="A cross-platform setup script for the dev-rules-starter-kit.")
    parser.add_argument(
        "--project-name",
        required=True,
        help="The name of the new project (e.g., 'MyAwesomeProject').",
    )
    parser.add_argument("--framework", default=None, help="Optional: The framework to scaffold for (e.g., 'fastapi').")
    args = parser.parse_args()

    print("=============================================")
    print("[SETUP] Dev Rules Starter Kit Setup Initializing")
    print("=============================================")

    # Create checkpoint before starting
    checkpoint_created = create_checkpoint()

    try:
        # 1. 프로젝트 이름 변경
        replace_project_name(args.project_name)

        # 2. 스캐폴딩 파일 복사
        copy_scaffold_files(args.framework)

        # 3. 의존성 설치
        run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python dependencies...")

        # 4. pre-commit 훅 설정
        run_command(f"{sys.executable} -m pre_commit install", "Installing pre-commit hooks...")
        run_command(
            f"{sys.executable} -m pre_commit install --hook-type commit-msg", "Installing commit-msg hook for commitlint..."
        )

        print("\n======================================")
        print("[SUCCESS] Dev Rules v2.0 Setup Complete!")
        print("Automated rule enforcement is now active.")
        print("======================================")

    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}", file=sys.stderr)
        if checkpoint_created:
            rollback_checkpoint()
        sys.exit(1)


if __name__ == "__main__":
    main()
