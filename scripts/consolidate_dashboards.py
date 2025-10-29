#!/usr/bin/env python3
"""
Dashboard Consolidation Script

Consolidates all scattered dashboard files into a single organized structure.
Addresses the issue identified in PROJECT_INSPECTION_REPORT.md
"""

import shutil
from pathlib import Path
from datetime import datetime


class DashboardConsolidator:
    """Consolidates scattered dashboard files."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.archive_dir = self.project_root / "archive" / "old_dashboards"
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def analyze_dashboard_files(self):
        """Analyze all dashboard-related files."""
        dashboard_files = {
            "launchers": [],  # .bat, .ps1, .sh files
            "test_files": [],  # test_dashboard*.py files
            "main_scripts": [],  # Main dashboard Python files
            "web_files": [],  # HTML dashboard files
            "docs": [],  # Documentation files
            "screenshots": [],  # Screenshot files
            "other": [],
        }

        # Find all dashboard files
        patterns = ["*dashboard*", "*Dashboard*"]
        for pattern in patterns:
            for file in self.project_root.rglob(pattern):
                if file.is_file() and "archive" not in str(file):
                    relative_path = file.relative_to(self.project_root)

                    if file.suffix in [".bat", ".ps1", ".sh"]:
                        dashboard_files["launchers"].append(relative_path)
                    elif file.name.startswith("test_") and file.suffix == ".py":
                        dashboard_files["test_files"].append(relative_path)
                    elif file.suffix == ".py":
                        dashboard_files["main_scripts"].append(relative_path)
                    elif file.suffix == ".html":
                        dashboard_files["web_files"].append(relative_path)
                    elif file.suffix == ".md":
                        dashboard_files["docs"].append(relative_path)
                    elif file.suffix in [".png", ".jpg", ".jpeg"]:
                        dashboard_files["screenshots"].append(relative_path)
                    else:
                        dashboard_files["other"].append(relative_path)

        return dashboard_files

    def consolidate(self):
        """Perform the consolidation."""
        print("Dashboard Consolidation Report")
        print("=" * 60)

        # Analyze current state
        dashboard_files = self.analyze_dashboard_files()

        print("\nFound Dashboard Files:")
        print(f"  Launchers: {len(dashboard_files['launchers'])}")
        print(f"  Test files: {len(dashboard_files['test_files'])}")
        print(f"  Main scripts: {len(dashboard_files['main_scripts'])}")
        print(f"  Web files: {len(dashboard_files['web_files'])}")
        print(f"  Documentation: {len(dashboard_files['docs'])}")
        print(f"  Screenshots: {len(dashboard_files['screenshots'])}")
        print(f"  Other: {len(dashboard_files['other'])}")

        total = sum(len(files) for files in dashboard_files.values())
        print(f"\nTotal: {total} dashboard-related files")

        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive redundant files
        archived = []
        kept = []

        # Define files to keep (consolidation targets)
        files_to_keep = [
            Path("streamlit_app.py"),  # Main Streamlit app
            Path("scripts/session_dashboard.py"),  # Session-specific dashboard
            Path("web/integrated_dashboard_prod.html"),  # Production web dashboard
            Path("docs/DASHBOARD_IMPROVEMENT_ANALYSIS.md"),  # Important documentation
            Path("run_dashboard.bat"),  # Single launcher for Windows
        ]

        # Archive test files and screenshots
        for category in ["test_files", "screenshots"]:
            for file_path in dashboard_files[category]:
                src = self.project_root / file_path
                if src.exists():
                    dst = self.archive_dir / category / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(src), str(dst))
                        archived.append(file_path)
                        print(f"[ARCHIVED] {file_path}")
                    except Exception as e:
                        print(f"[ERROR] Could not archive {file_path}: {e}")

        # Archive redundant launchers (keep only one)
        launcher_to_keep = Path("run_dashboard.bat")
        for launcher in dashboard_files["launchers"]:
            if launcher != launcher_to_keep:
                src = self.project_root / launcher
                if src.exists():
                    dst = self.archive_dir / "launchers" / launcher
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(src), str(dst))
                        archived.append(launcher)
                        print(f"[ARCHIVED] {launcher}")
                    except Exception as e:
                        print(f"[ERROR] Could not archive {launcher}: {e}")

        # Create unified launcher script
        self._create_unified_launcher()

        # Create README for dashboard organization
        self._create_dashboard_readme()

        print("\n" + "=" * 60)
        print("Consolidation Summary:")
        print(f"  Files archived: {len(archived)}")
        print(f"  Files kept: {len(files_to_keep)}")
        print(f"  Archive location: {self.archive_dir}")
        print("\nConsolidation complete!")

    def _create_unified_launcher(self):
        """Create a unified launcher script."""
        launcher_content = """@echo off
REM Unified Dashboard Launcher
REM Consolidated from scattered dashboard files

echo ========================================
echo Dev Rules Starter Kit - Dashboard
echo ========================================
echo.
echo Select dashboard to launch:
echo   1. Streamlit Dashboard (Main)
echo   2. Session Dashboard
echo   3. Web Dashboard (HTML)
echo   4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Launching main Streamlit dashboard...
    python -X utf8 streamlit_app.py
) else if "%choice%"=="2" (
    echo Launching session dashboard...
    python -X utf8 scripts/session_dashboard.py
) else if "%choice%"=="3" (
    echo Opening web dashboard in browser...
    start web/integrated_dashboard_prod.html
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run again.
    exit /b 1
)
"""

        launcher_path = self.project_root / "launch_dashboard.bat"
        launcher_path.write_text(launcher_content)
        print(f"[CREATED] Unified launcher: {launcher_path}")

    def _create_dashboard_readme(self):
        """Create README explaining dashboard organization."""
        readme_content = f"""# Dashboard Organization

## Overview
This directory structure has been consolidated from {datetime.now().strftime("%Y-%m-%d")} to address scattered dashboard files.

## Active Dashboards

### 1. Main Streamlit Dashboard
- **File**: `streamlit_app.py`
- **Purpose**: Primary constitution compliance monitoring
- **Launch**: `python -X utf8 streamlit_app.py`
- **Port**: 8501

### 2. Session Dashboard
- **File**: `scripts/session_dashboard.py`
- **Purpose**: Session-specific metrics and tracking
- **Launch**: `python -X utf8 scripts/session_dashboard.py`
- **Port**: 8502 (if main is running)

### 3. Web Dashboard
- **File**: `web/integrated_dashboard_prod.html`
- **Purpose**: Static HTML dashboard for production
- **Launch**: Open in browser directly

## Unified Launcher
Use `launch_dashboard.bat` to select and launch any dashboard.

## Archived Files
Old test files, screenshots, and redundant launchers have been moved to:
`archive/old_dashboards/`

## Constitution Compliance
Per P7 (Hallucination Prevention), dashboards are:
- Read-only visualization tools (Layer 7)
- Not the main product focus
- Constitution enforcement remains primary goal

## Maintenance
- Do not create new dashboard files in root directory
- Place any new dashboard components in appropriate subdirectories
- Use the unified launcher for consistency
"""

        readme_path = self.project_root / "dashboards" / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(readme_content)
        print(f"[CREATED] Dashboard README: {readme_path}")


def main():
    """Run the consolidation."""
    consolidator = DashboardConsolidator()

    print("Dashboard Consolidation Tool")
    print("=" * 60)
    print("\nThis will consolidate scattered dashboard files.")
    print("Old files will be archived, not deleted.")

    response = input("\nProceed with consolidation? (y/n): ")
    if response.lower() == "y":
        consolidator.consolidate()
    else:
        print("Consolidation cancelled.")


if __name__ == "__main__":
    main()
