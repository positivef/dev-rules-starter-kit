#!/usr/bin/env python3
"""
Create Ultimate Template Package with Multiple Levels
최고 성능을 위한 완벽한 템플릿 패키지 생성

4개 레벨:
1. Essential (32KB) - 최소 기능
2. Standard (60KB) - 기본 + Streamlit
3. Professional (200KB) - 핵심 분석 도구 포함
4. Enterprise (500KB) - 모든 기능 포함

Usage:
    python scripts/create_ultimate_templates.py
"""

import zipfile
import os
from pathlib import Path
import json

class TemplateLevel:
    """Template configuration for each level"""

    ESSENTIAL = {
        "name": "essential",
        "desc": "Minimal setup for quick start",
        "scripts": [
            "task_executor.py",
            "session_manager.py",
            "context_provider.py",
        ],
        "dashboards": [],
        "extras": []
    }

    STANDARD = {
        "name": "standard",
        "desc": "Flask + Streamlit dashboards",
        "scripts": [
            "task_executor.py",
            "session_manager.py",
            "context_provider.py",
        ],
        "dashboards": [
            "streamlit_app.py",
            "scripts/session_dashboard.py",
            "scripts/lock_dashboard_streamlit.py",
        ],
        "extras": []
    }

    PROFESSIONAL = {
        "name": "professional",
        "desc": "Core analysis + optimization tools",
        "scripts": [
            # Core execution
            "task_executor.py",
            "enhanced_task_executor_v2.py",
            "session_manager.py",
            "context_provider.py",

            # Analysis & validation
            "deep_analyzer.py",
            "constitutional_validator.py",
            "team_stats_aggregator.py",
            "critical_file_detector.py",

            # Performance
            "verification_cache.py",
            "worker_pool.py",
            "smart_cache_manager.py",

            # Obsidian
            "obsidian_bridge.py",
            "auto_sync_obsidian.py",

            # Testing
            "tdd_enforcer.py",
            "test_generator.py",
        ],
        "dashboards": [
            "streamlit_app.py",
            "scripts/session_dashboard.py",
            "scripts/lock_dashboard_streamlit.py",
        ],
        "extras": [
            "tier1_cli.py",
            "dev_rules_cli.py",
        ]
    }

    ENTERPRISE = {
        "name": "enterprise",
        "desc": "Complete system with all 135 tools",
        "scripts": "ALL",  # Special flag for all scripts
        "dashboards": "ALL",
        "extras": "ALL"
    }


def create_requirements(level):
    """Generate requirements.txt based on level"""

    base = """# Core
PyYAML==6.0.3
ruff==0.14.3
"""

    if level in ["essential"]:
        return base + """# Web
Flask==3.1.2
"""

    if level in ["standard", "professional"]:
        return base + """# Web & Dashboard
Flask==3.1.2
streamlit==1.39.0
pandas==2.2.3
plotly==5.24.1
psutil==5.9.8
watchdog==4.0.2
"""

    if level == "enterprise":
        return base + """# Complete Stack
Flask==3.1.2
streamlit==1.39.0
pandas==2.2.3
plotly==5.24.1
psutil==5.9.8
watchdog==4.0.2
jsonschema==4.22.0
pre-commit==3.7.1
pytest==8.2.0
pytest-cov==5.0.0
pytest-benchmark==4.0.0
rich==13.7.1
typer==0.9.0
"""


def create_readme(level, config):
    """Generate level-specific README"""

    return f"""# Project Template - {level.upper()}

**Level**: {level.capitalize()}
**Description**: {config['desc']}

## Included Tools

### Scripts ({len(config['scripts'])} tools)
{chr(10).join('- ' + s for s in config['scripts'][:10]) if isinstance(config['scripts'], list) else '- All 135+ scripts included'}

### Dashboards ({len(config['dashboards'])} apps)
{chr(10).join('- ' + d for d in config['dashboards']) if isinstance(config['dashboards'], list) else '- All dashboards included'}

## Quick Start

1. Extract ZIP
2. Rename folder to your project name
3. Edit config/constitution.yaml (project name)
4. Edit .env (PROJECT_NAME)
5. Setup Python environment:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate  # Windows
   pip install -r requirements.txt
   ```
6. Initialize Git:
   ```bash
   git init
   git add .
   git commit -m "feat: initialize project"
   ```

## Performance Features

{'✓ Basic execution' if level == 'essential' else ''}
{'✓ Basic execution + Dashboards' if level == 'standard' else ''}
{'✓ Code analysis + Optimization + Obsidian' if level == 'professional' else ''}
{'✓ Complete enterprise stack (135+ tools)' if level == 'enterprise' else ''}

## Recommended For

{'- Quick prototypes\n- Simple projects\n- Learning' if level == 'essential' else ''}
{'- Small teams\n- Web apps with monitoring\n- Standard projects' if level == 'standard' else ''}
{'- Professional development\n- Performance critical\n- Knowledge management' if level == 'professional' else ''}
{'- Large teams\n- Enterprise projects\n- Maximum capabilities' if level == 'enterprise' else ''}

Built with Constitution Framework
"""


def create_template_zip(level_config, level_name):
    """Create ZIP for specific level"""

    starter_kit = Path(__file__).parent.parent
    my_awesome_app = starter_kit.parent / "my-awesome-app"
    output_zip = starter_kit / f"project-template-{level_name}.zip"

    print(f"\n{'='*50}")
    print(f"Creating {level_name.upper()} template: {output_zip}")
    print(f"Description: {level_config['desc']}")
    print(f"{'='*50}")

    file_count = 0

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:

        # 1. Config files (all levels)
        config_files = [
            "config/constitution.yaml",
            ".gitignore",
        ]

        for file_path in config_files:
            src = starter_kit / file_path
            if src.exists():
                zipf.write(src, f"project-template/{file_path}")
                print(f"  + {file_path}")
                file_count += 1

        # 2. Scripts based on level
        scripts = level_config['scripts']
        if scripts == "ALL":
            # Include all Python scripts
            scripts_dir = starter_kit / "scripts"
            for script in scripts_dir.glob("*.py"):
                if script.is_file():
                    rel_path = script.relative_to(starter_kit)
                    zipf.write(script, f"project-template/{rel_path}")
                    file_count += 1
            print(f"  + ALL scripts ({file_count-2} files)")
        else:
            # Include specific scripts
            for script_name in scripts:
                src = starter_kit / "scripts" / script_name
                if src.exists():
                    zipf.write(src, f"project-template/scripts/{script_name}")
                    print(f"  + scripts/{script_name}")
                    file_count += 1

        # 3. Dashboards based on level
        if level_config['dashboards']:
            dashboards = level_config['dashboards']
            if dashboards == "ALL":
                # Include all dashboards
                for dashboard_path in ["streamlit_app.py",
                                      "scripts/session_dashboard.py",
                                      "scripts/lock_dashboard_streamlit.py"]:
                    src = starter_kit / dashboard_path
                    if src.exists():
                        dst = f"dashboards/{Path(dashboard_path).name}"
                        zipf.write(src, f"project-template/{dst}")
                        file_count += 1
                print(f"  + ALL dashboards")
            else:
                # Include specific dashboards
                for dashboard_path in dashboards:
                    src = starter_kit / dashboard_path
                    if src.exists():
                        dst = f"dashboards/{Path(dashboard_path).name}"
                        zipf.write(src, f"project-template/{dst}")
                        print(f"  + {dst}")
                        file_count += 1

        # 4. Flask app (from my-awesome-app if exists)
        if my_awesome_app.exists():
            app_files = {
                "src/app.py": "src/app.py",
                "src/cli/main.py": "src/cli/main.py",
                "tests/test_app.py": "tests/test_app.py",
            }
            for src_path, dst_path in app_files.items():
                src = my_awesome_app / src_path
                if src.exists():
                    zipf.write(src, f"project-template/{dst_path}")
                    print(f"  + {dst_path}")
                    file_count += 1

        # 5. Requirements.txt
        req_content = create_requirements(level_name)
        zipf.writestr("project-template/requirements.txt", req_content)
        print(f"  + requirements.txt")
        file_count += 1

        # 6. .env
        env_content = f"""PROJECT_NAME=your-project
PROJECT_TYPE={level_name}
OBSIDIAN_ENABLED={'true' if level_name in ['professional', 'enterprise'] else 'false'}
DEBUG=true
"""
        zipf.writestr("project-template/.env", env_content)
        print(f"  + .env")
        file_count += 1

        # 7. README
        readme = create_readme(level_name, level_config)
        zipf.writestr("project-template/README.md", readme)
        print(f"  + README.md")
        file_count += 1

    size_kb = os.path.getsize(output_zip) / 1024
    print(f"\n✓ Created: {output_zip.name}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Files: {file_count}")

    return output_zip, size_kb, file_count


def create_all_templates():
    """Create all template levels"""

    levels = [
        (TemplateLevel.ESSENTIAL, "essential"),
        (TemplateLevel.STANDARD, "standard"),
        (TemplateLevel.PROFESSIONAL, "professional"),
        (TemplateLevel.ENTERPRISE, "enterprise"),
    ]

    results = []

    print("\n" + "="*70)
    print("CREATING ULTIMATE TEMPLATE PACKAGE")
    print("="*70)

    for config, name in levels:
        try:
            zip_path, size, count = create_template_zip(config, name)
            results.append({
                "level": name,
                "path": zip_path,
                "size_kb": size,
                "file_count": count
            })
        except Exception as e:
            print(f"Error creating {name}: {e}")

    # Summary
    print("\n" + "="*70)
    print("TEMPLATE PACKAGE COMPLETE!")
    print("="*70)
    print("\n📦 Generated Templates:\n")

    for r in results:
        print(f"  {r['level'].upper():12} - {r['size_kb']:6.1f} KB - {r['file_count']:3} files")

    print("\n🚀 Usage:")
    print("  1. Choose your level based on project needs")
    print("  2. Extract the corresponding ZIP")
    print("  3. Start developing!\n")

    print("📊 Recommendations:")
    print("  - Solo/Learning    → essential")
    print("  - Small team       → standard")
    print("  - Professional     → professional")
    print("  - Enterprise       → enterprise\n")

    # Create comparison chart
    chart = """
╔════════════════╦═══════════╦══════════╦════════════╦════════════╗
║ Feature        ║ Essential ║ Standard ║ Pro        ║ Enterprise ║
╠════════════════╬═══════════╬══════════╬════════════╬════════════╣
║ Flask          ║ ✓         ║ ✓        ║ ✓          ║ ✓          ║
║ Streamlit      ║           ║ ✓        ║ ✓          ║ ✓          ║
║ Code Analysis  ║           ║          ║ ✓          ║ ✓          ║
║ Optimization   ║           ║          ║ ✓          ║ ✓          ║
║ Obsidian       ║           ║          ║ ✓          ║ ✓          ║
║ TDD Tools      ║           ║          ║ ✓          ║ ✓          ║
║ All 135 Tools  ║           ║          ║            ║ ✓          ║
╚════════════════╩═══════════╩══════════╩════════════╩════════════╝
"""
    print(chart)

    return results


if __name__ == "__main__":
    create_all_templates()