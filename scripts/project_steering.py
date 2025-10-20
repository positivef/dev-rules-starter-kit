#!/usr/bin/env python3
"""
Project Steering System - cc-sdd Trust 8.3 pattern

Based on: /gotalab/cc-sdd /kiro:steering command
Purpose: Generate persistent project context for AI agents
Evidence: cc-sdd production usage (Trust 8.3)

Pattern:
  /kiro:steering → .kiro/steering/{product,tech,structure}.md

Our Implementation:
  python scripts/project_steering.py → dev-context/{product,tech,structure}.md

Features:
  - Analyzes tech stack from package.json/requirements.txt
  - Analyzes project structure (directories, file types)
  - Generates steering documents for AI context
  - Preserves custom content on updates (cc-sdd pattern)
  - Creates metadata.json for tracking
"""

import argparse
import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict


class ProjectSteering:
    """Generate project steering documents (cc-sdd pattern)"""

    def __init__(self, project_root: Path = None):
        """
        Initialize Project Steering generator

        Args:
            project_root: Project root directory (default: current directory)
        """
        self.root = project_root or Path(".")
        self.steering_dir = self.root / "dev-context"

    def generate(self, dry_run: bool = False) -> None:
        """
        Generate all steering documents

        Args:
            dry_run: Preview without writing files
        """
        # Create steering directory
        if not dry_run:
            self.steering_dir.mkdir(exist_ok=True)

        # Analyze project
        tech_stack = self.analyze_tech_stack()
        structure = self.analyze_project_structure()

        # Generate steering docs
        self._generate_tech_md(tech_stack, dry_run)
        self._generate_structure_md(structure, dry_run)
        self._generate_product_md(dry_run)
        self._generate_metadata(tech_stack, structure, dry_run)

        if dry_run:
            print("[DRY RUN] Preview complete. No files written.")
        else:
            print(f"[PASS] Steering documents generated in {self.steering_dir}")

    def analyze_tech_stack(self) -> Dict:
        """
        Analyze technology stack from package managers

        Returns:
            Dict with dependencies, devDependencies, package_manager
        """
        tech = {"dependencies": {}, "devDependencies": {}, "package_manager": None}

        # Check for Node.js project (package.json)
        package_json = self.root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
                tech["dependencies"] = data.get("dependencies", {})
                tech["devDependencies"] = data.get("devDependencies", {})
                tech["package_manager"] = "npm"
            except (json.JSONDecodeError, OSError) as e:
                warnings.warn(f"Failed to parse package.json: {e}")

        # Check for Python project (requirements.txt)
        requirements_txt = self.root / "requirements.txt"
        if requirements_txt.exists():
            try:
                lines = requirements_txt.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse requirement (e.g., "pytest>=7.0.0")
                        if ">=" in line:
                            pkg, version = line.split(">=")
                            tech["dependencies"][pkg.strip()] = f">={version.strip()}"
                        elif "==" in line:
                            pkg, version = line.split("==")
                            tech["dependencies"][pkg.strip()] = version.strip()
                        else:
                            tech["dependencies"][line] = "*"
                tech["package_manager"] = "pip"
            except Exception as e:
                warnings.warn(f"Failed to parse requirements.txt: {e}")

        # Warn if no package manager detected
        if tech["package_manager"] is None:
            warnings.warn("No package manager detected (no package.json or requirements.txt)")

        return tech

    def analyze_project_structure(self) -> Dict:
        """
        Analyze project directory structure

        Returns:
            Dict with directories, file_types, test_coverage
        """
        structure = {"directories": [], "file_types": set(), "has_tests": False}

        # Scan directories (max depth 2)
        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Ignore common non-source directories
                if item.name not in ["node_modules", "__pycache__", "dist", "build"]:
                    structure["directories"].append(item.name)

                # Check for test directory
                if item.name in ["tests", "test", "__tests__"]:
                    structure["has_tests"] = True

        # Scan file types
        for file in self.root.rglob("*"):
            if file.is_file() and not any(p in file.parts for p in ["node_modules", ".git", "__pycache__"]):
                if file.suffix:
                    structure["file_types"].add(file.suffix)

        # Warn if no tests
        if not structure["has_tests"]:
            warnings.warn("No test directory found (tests/, test/, or __tests__/)")

        structure["file_types"] = sorted(structure["file_types"])

        return structure

    def _generate_tech_md(self, tech_stack: Dict, dry_run: bool = False) -> None:
        """Generate tech.md steering document"""
        tech_md = self.steering_dir / "tech.md"

        # Read existing custom content if file exists
        custom_content = ""
        if tech_md.exists() and not dry_run:
            existing = tech_md.read_text(encoding="utf-8")
            # Extract custom sections (anything after "## Custom")
            if "## Custom" in existing:
                parts = existing.split("## Custom", 1)
                if len(parts) > 1:
                    custom_content = "\n\n## Custom" + parts[1]

        # Generate content
        content = f"""# Tech Stack

**Generated**: {datetime.now().isoformat()}
**Package Manager**: {tech_stack['package_manager'] or 'Unknown'}

## Dependencies

"""

        if tech_stack["dependencies"]:
            for pkg, version in tech_stack["dependencies"].items():
                content += f"- **{pkg}**: {version}\n"
        else:
            content += "*No dependencies detected*\n"

        content += "\n## Dev Dependencies\n\n"

        if tech_stack["devDependencies"]:
            for pkg, version in tech_stack["devDependencies"].items():
                content += f"- **{pkg}**: {version}\n"
        else:
            content += "*No dev dependencies detected*\n"

        # Append custom content (cc-sdd pattern: preserve user edits)
        if custom_content:
            content += custom_content

        if dry_run:
            print(f"[DRY RUN] Would create {tech_md}")
            print(content[:200] + "...")
        else:
            tech_md.write_text(content, encoding="utf-8")

    def _generate_structure_md(self, structure: Dict, dry_run: bool = False) -> None:
        """Generate structure.md steering document"""
        structure_md = self.steering_dir / "structure.md"

        # Read existing custom content
        custom_content = ""
        if structure_md.exists() and not dry_run:
            existing = structure_md.read_text(encoding="utf-8")
            if "## Custom" in existing:
                parts = existing.split("## Custom", 1)
                if len(parts) > 1:
                    custom_content = "\n\n## Custom" + parts[1]

        # Generate content
        content = f"""# Project Structure

**Generated**: {datetime.now().isoformat()}

## Directories

"""

        if structure["directories"]:
            for dir_name in sorted(structure["directories"]):
                content += f"- `{dir_name}/`\n"
        else:
            content += "*No directories detected*\n"

        content += "\n## File Types\n\n"

        if structure["file_types"]:
            for ext in structure["file_types"]:
                content += f"- `{ext}`\n"
        else:
            content += "*No file types detected*\n"

        content += "\n## Testing\n\n"
        content += f"**Has Tests**: {'Yes' if structure['has_tests'] else 'No'}\n"

        # Append custom content
        if custom_content:
            content += custom_content

        if dry_run:
            print(f"[DRY RUN] Would create {structure_md}")
            print(content[:200] + "...")
        else:
            structure_md.write_text(content, encoding="utf-8")

    def _generate_product_md(self, dry_run: bool = False) -> None:
        """Generate product.md template"""
        product_md = self.steering_dir / "product.md"

        # Don't overwrite if exists (user content)
        if product_md.exists():
            return

        # Get project name from package.json or directory name
        project_name = "Unknown Project"
        package_json = self.root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
                project_name = data.get("name", self.root.name)
            except (json.JSONDecodeError, OSError):
                project_name = self.root.name
        else:
            project_name = self.root.name

        content = f"""# Product Requirements

**Project**: {project_name}
**Created**: {datetime.now().isoformat()}

## Overview

*Describe the product vision and goals here.*

## User Stories

*Add user stories here.*

## Success Criteria

*Define measurable success criteria here.*

## Constraints

*Document technical or business constraints here.*

---

**Note**: This is a template. Edit this file to add your product requirements.
"""

        if dry_run:
            print(f"[DRY RUN] Would create {product_md}")
        else:
            product_md.write_text(content, encoding="utf-8")

    def _generate_metadata(self, tech_stack: Dict, structure: Dict, dry_run: bool = False) -> None:
        """Generate metadata.json for tracking"""
        metadata_file = self.steering_dir / "metadata.json"

        # Read existing metadata
        existing_metadata = {}
        if metadata_file.exists() and not dry_run:
            try:
                existing_metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Create/update metadata
        metadata = {
            "created_at": existing_metadata.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            "tech_stack": {
                "package_manager": tech_stack["package_manager"],
                "dependencies_count": len(tech_stack["dependencies"]),
                "devDependencies_count": len(tech_stack["devDependencies"]),
            },
            "project_structure": {
                "directories_count": len(structure["directories"]),
                "file_types_count": len(structure["file_types"]),
                "has_tests": structure["has_tests"],
            },
        }

        if dry_run:
            print(f"[DRY RUN] Would create {metadata_file}")
            print(json.dumps(metadata, indent=2))
        else:
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate project steering documents (cc-sdd pattern)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument(
        "--project-root", type=Path, default=Path("."), help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()

    # Generate steering documents
    steering = ProjectSteering(args.project_root)
    steering.generate(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
