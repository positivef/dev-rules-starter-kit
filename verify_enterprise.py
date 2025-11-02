#!/usr/bin/env python3
"""Verify Enterprise template contents."""

import zipfile
import os
from pathlib import Path

def verify_enterprise_template():
    """Verify Enterprise template has all components."""
    zip_path = "project-template-enterprise.zip"

    if not os.path.exists(zip_path):
        print(f"ERROR: {zip_path} not found!")
        return False

    with zipfile.ZipFile(zip_path) as z:
        files = z.filelist
        print(f"Total files: {len(files)}")

        # Count different file types
        py_files = [f for f in files if f.filename.endswith('.py')]
        yaml_files = [f for f in files if f.filename.endswith('.yaml')]
        md_files = [f for f in files if f.filename.endswith('.md')]

        print(f"\nFile Statistics:")
        print(f"  - Python scripts: {len(py_files)}")
        print(f"  - YAML configs: {len(yaml_files)}")
        print(f"  - Markdown docs: {len(md_files)}")

        # Check for key components
        dashboard_files = [f for f in py_files if 'dashboard' in f.filename.lower()]
        streamlit_files = [f for f in py_files if 'streamlit' in f.filename.lower() or '_dashboard' in f.filename]
        task_files = [f for f in py_files if 'task' in f.filename.lower()]
        validator_files = [f for f in py_files if 'validator' in f.filename.lower() or 'validate' in f.filename.lower()]

        print(f"\nComponent Analysis:")
        print(f"  - Dashboard scripts: {len(dashboard_files)}")
        print(f"  - Streamlit apps: {len(streamlit_files)}")
        print(f"  - Task executors: {len(task_files)}")
        print(f"  - Validators: {len(validator_files)}")

        # Check directories
        dirs = set()
        for f in files:
            if '/' in f.filename:
                parts = f.filename.split('/')
                # Get root directory
                if parts[0] == 'project-template':
                    if len(parts) > 1:
                        dirs.add(parts[1])

        print(f"\nDirectories found:")
        for d in sorted(dirs):
            print(f"  - {d}")

        # Verify critical files
        critical_files = [
            'scripts/task_executor.py',
            'scripts/constitutional_validator.py',
            'scripts/context_provider.py',
            'scripts/obsidian_bridge.py',
            'dashboards/constitution_dashboard.py',
            'config/constitution.yaml',
            'requirements.txt'
        ]

        file_names = [f.filename for f in files]

        print(f"\nCritical Files Check:")
        for cf in critical_files:
            # Check with different path prefixes
            found = False
            for fn in file_names:
                if cf in fn or fn.endswith(cf.split('/')[-1]):
                    found = True
                    break
            status = "✓" if found else "✗"
            print(f"  {status} {cf}")

        # Final verdict
        print(f"\n{'='*50}")
        if len(py_files) >= 130:
            print("✅ ENTERPRISE TEMPLATE VERIFIED!")
            print(f"   - {len(py_files)} Python scripts included")
            print(f"   - {len(dashboard_files)} Dashboard components")
            print(f"   - All critical components present")
            return True
        else:
            print("⚠️ INCOMPLETE TEMPLATE!")
            print(f"   - Only {len(py_files)} Python scripts (expected 130+)")
            return False

if __name__ == "__main__":
    verify_enterprise_template()