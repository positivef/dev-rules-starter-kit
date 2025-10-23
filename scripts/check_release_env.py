"""Semantic-release environment checker.

Performs lightweight diagnostics:
- Verifies that Node and npm are available.
- Ensures the active Node major version matches `.nvmrc` (if present).
- Confirms semantic-release devDependencies are declared and installed.

Usage:
    python scripts/check_release_env.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NVMRC = ROOT / ".nvmrc"
PACKAGE_JSON = ROOT / "package.json"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def get_node_version() -> tuple[bool, str]:
    proc = run(["node", "--version"])
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip()
    return True, proc.stdout.strip()


def parse_major(version: str) -> int | None:
    if not version:
        return None
    # node --version 출력은 v20.12.0 형태
    digits = version.lstrip("vV")
    try:
        return int(digits.split(".")[0])
    except (ValueError, IndexError):
        return None


def read_expected_node_major() -> int | None:
    if not NVMRC.exists():
        return None
    content = NVMRC.read_text(encoding="utf-8").strip()
    try:
        return int(content)
    except ValueError:
        return None


def check_semantic_release_deps() -> list[str]:
    if not PACKAGE_JSON.exists():
        return ["package.json not found"]

    try:
        package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Failed to parse package.json: {exc}"]

    dev_deps = package.get("devDependencies", {})
    required = [
        "semantic-release",
        "@semantic-release/changelog",
        "@semantic-release/commit-analyzer",
        "@semantic-release/git",
        "@semantic-release/github",
        "@semantic-release/release-notes-generator",
    ]

    missing = [dep for dep in required if dep not in dev_deps]
    if missing:
        return [
            "Missing devDependencies:",
            *[f"  - {dep}" for dep in missing],
        ]

    node_modules = ROOT / "node_modules"
    if not node_modules.exists():
        return [
            "`node_modules` directory is missing.",
            "  Run npm install --no-fund --no-audit to install dependencies.",
        ]

    return []


def main() -> int:
    issues: list[str] = []

    ok, version_output = get_node_version()
    if not ok:
        issues.append("Node.js is not installed or not on PATH.")
        if version_output:
            issues.append(f"  Details: {version_output}")
    else:
        detected_version = version_output
        detected_major = parse_major(detected_version)
        expected_major = read_expected_node_major()
        print(f"[OK] node --version → {detected_version}")
        if expected_major is not None and detected_major != expected_major:
            issues.append(f"Node major version mismatch: expected {expected_major}, detected {detected_major}.")
            issues.append("  Use `nvm use` or corepack to align with .nvmrc.")

    npm_proc = run(["npm", "--version"])
    if npm_proc.returncode != 0:
        issues.append("npm is unavailable. Verify Node installation.")
    else:
        print(f"[OK] npm --version → {npm_proc.stdout.strip()}")

    dep_issues = check_semantic_release_deps()
    if dep_issues:
        issues.extend(dep_issues)
    else:
        print("[OK] semantic-release devDependencies 확인 완료")

    if issues:
        print("\n[WARN] Release environment needs attention.")
        for line in issues:
            print(line)
        return 1

    print("\n[SUCCESS] Semantic-release 환경이 준비되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
