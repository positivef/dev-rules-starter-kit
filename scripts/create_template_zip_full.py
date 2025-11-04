#!/usr/bin/env python3
"""
Create FULL ZIP template with Streamlit dashboards

Includes:
- Flask web app
- CLI tools
- Streamlit dashboards (3개)
- All essential scripts
- Complete requirements

Usage:
    python scripts/create_template_zip_full.py
"""

import zipfile
import os
from pathlib import Path


def create_full_template_zip():
    """Create complete template with all features"""

    starter_kit = Path(__file__).parent.parent
    my_awesome_app = starter_kit.parent / "my-awesome-app"
    output_zip = starter_kit / "project-template-full.zip"

    print(f"Creating FULL template ZIP: {output_zip}")
    print("Including: Flask + Streamlit + Dashboards + All Tools\n")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Config files from dev-rules-starter-kit
        config_files = {
            "config/constitution.yaml": "config/constitution.yaml",
            ".gitignore": ".gitignore",
        }

        for src_path, dst_path in config_files.items():
            src = starter_kit / src_path
            if src.exists():
                zipf.write(src, f"project-template/{dst_path}")
                print(f"  [Config] {dst_path}")

        # 2. Essential scripts
        essential_scripts = [
            "task_executor.py",
            "session_manager.py",
            "context_provider.py",
        ]

        for script in essential_scripts:
            src = starter_kit / "scripts" / script
            if src.exists():
                zipf.write(src, f"project-template/scripts/{script}")
                print(f"  [Script] scripts/{script}")

        # 3. Streamlit Dashboards (핵심!)
        dashboard_files = {
            "streamlit_app.py": "dashboards/constitution_dashboard.py",
            "scripts/session_dashboard.py": "dashboards/session_dashboard.py",
            "scripts/lock_dashboard_streamlit.py": "dashboards/lock_dashboard.py",
        }

        print("\n  [Dashboards]")
        for src_path, dst_path in dashboard_files.items():
            src = starter_kit / src_path
            if src.exists():
                zipf.write(src, f"project-template/{dst_path}")
                print(f"    + {dst_path}")

        # 4. Flask app from my-awesome-app (if exists)
        if my_awesome_app.exists():
            app_files = {
                "src/app.py": "src/app.py",
                "src/cli/main.py": "src/cli/main.py",
                "tests/test_app.py": "tests/test_app.py",
            }

            print("\n  [Flask App]")
            for src_path, dst_path in app_files.items():
                src = my_awesome_app / src_path
                if src.exists():
                    zipf.write(src, f"project-template/{dst_path}")
                    print(f"    + {dst_path}")

        # 5. Create complete requirements.txt (핵심!)
        requirements_content = """# Web Framework
Flask==3.1.2

# Dashboard & Visualization
streamlit==1.39.0
pandas==2.2.3
plotly==5.24.1

# Constitution Framework
PyYAML==6.0.3
ruff==0.14.3

# Utilities
psutil==5.9.8
watchdog==4.0.2
"""
        zipf.writestr("project-template/requirements.txt", requirements_content)
        print("\n  [Requirements] requirements.txt (Flask + Streamlit + Dashboards)")

        # 6. Create .env
        env_content = """PROJECT_NAME=your-project
PROJECT_TYPE=webapp-cli-dashboard
OBSIDIAN_ENABLED=false
DEBUG=true

# Dashboard Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
"""
        zipf.writestr("project-template/.env", env_content)
        print("  [Config] .env")

        # 7. Create README.md
        readme_content = """# Your Project

**Framework**: Constitution-based Development (Level 1)
**Features**: Flask + Streamlit Dashboards + CLI

## Quick Start

### 1. Setup Environment
```bash
# Extract ZIP
unzip project-template-full.zip
mv project-template your-project
cd your-project

# Create folders
mkdir TASKS RUNS

# Python environment
python -m venv .venv
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Applications

#### Flask Web App
```bash
python src/app.py
# Visit: http://localhost:5000
```

#### Streamlit Dashboards
```bash
# Constitution Dashboard
streamlit run dashboards/constitution_dashboard.py
# Visit: http://localhost:8501

# Session Monitoring
streamlit run dashboards/session_dashboard.py

# Lock Status
streamlit run dashboards/lock_dashboard.py
```

#### CLI Tool
```bash
python src/cli/main.py --help
python src/cli/main.py --greet "World"
```

## Project Structure

```
your-project/
├── src/
│   ├── app.py              # Flask web server
│   └── cli/
│       └── main.py         # CLI tool
├── dashboards/             # Streamlit dashboards
│   ├── constitution_dashboard.py
│   ├── session_dashboard.py
│   └── lock_dashboard.py
├── scripts/                # Development tools
│   ├── task_executor.py
│   ├── session_manager.py
│   └── context_provider.py
├── tests/                  # Tests
├── config/                 # Configuration
│   └── constitution.yaml
└── requirements.txt        # Dependencies
```

## Development

- **Small changes**: `git commit -m "fix: ..."`
- **Large changes**: Use YAML contracts in `TASKS/`
- **Monitor progress**: Use Streamlit dashboards
- **Session management**: `python scripts/session_manager.py`

## Features

### Flask Web App
- Modern responsive UI
- RESTful API endpoints
- Hot reload in debug mode

### Streamlit Dashboards
- **Constitution Dashboard**: Monitor code quality & compliance
- **Session Dashboard**: Real-time session monitoring
- **Lock Dashboard**: File lock status (multi-session)

### Constitution Framework
- Level 1 (Light Mode) - Minimal rules
- YAML-based task execution
- Evidence-based development

Built with [Dev Rules Starter Kit](https://github.com/dev-rules-starter-kit)
"""
        zipf.writestr("project-template/README.md", readme_content)
        print("  [Docs] README.md")

        # 8. Create TEMPLATE_README.txt (사용 설명서)
        template_readme = """# Constitution Framework - FULL Template

이 템플릿은 다음을 포함합니다:

## 포함된 기능

1. **Flask Web App**
   - src/app.py: 웹 서버
   - 포트: 5000

2. **Streamlit Dashboards** (3개)
   - dashboards/constitution_dashboard.py: 품질 모니터링
   - dashboards/session_dashboard.py: 세션 추적
   - dashboards/lock_dashboard.py: 파일 잠금 상태
   - 포트: 8501

3. **CLI Tool**
   - src/cli/main.py: 명령줄 도구

4. **Development Tools**
   - scripts/task_executor.py: YAML 실행
   - scripts/session_manager.py: 세션 관리
   - scripts/context_provider.py: 컨텍스트 유지

## 빠른 시작 (5분)

```bash
# 1. 압축 해제
unzip project-template-full.zip
mv project-template my-project
cd my-project

# 2. 설정 수정
notepad config/constitution.yaml  # project name 변경
notepad .env                      # PROJECT_NAME 변경

# 3. Python 환경
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt

# 4. 폴더 생성
mkdir TASKS RUNS

# 5. Git 초기화
git init
git add .
git commit -m "feat: initialize project"

# 6. 실행!
python src/app.py  # Flask
# 또는
streamlit run dashboards/constitution_dashboard.py  # Dashboard
```

## 주요 명령어

```bash
# Web App
python src/app.py

# Dashboards
streamlit run dashboards/constitution_dashboard.py
streamlit run dashboards/session_dashboard.py
streamlit run dashboards/lock_dashboard.py

# CLI
python src/cli/main.py --help

# Development
python scripts/session_manager.py start
python scripts/task_executor.py TASKS/feature.yaml
```

## 크기: ~60KB (압축)
## 설치 후: ~150MB (with .venv)

Made with Constitution Framework
"""
        zipf.writestr("project-template/TEMPLATE_README.txt", template_readme)
        print("  [Docs] TEMPLATE_README.txt")

        # 9. Create dashboard launcher script
        launcher_content = """#!/usr/bin/env python3
\"\"\"Dashboard Launcher - Run all dashboards\"\"\"

import subprocess
import sys
from pathlib import Path

def main():
    dashboards_dir = Path(__file__).parent

    dashboards = [
        ("Constitution Dashboard", "constitution_dashboard.py", 8501),
        ("Session Dashboard", "session_dashboard.py", 8502),
        ("Lock Dashboard", "lock_dashboard.py", 8503),
    ]

    print("Available Dashboards:")
    for i, (name, file, port) in enumerate(dashboards, 1):
        print(f"  {i}. {name} (port {port})")

    choice = input("\\nSelect dashboard (1-3): ")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(dashboards):
            name, file, port = dashboards[idx]
            print(f"\\nLaunching {name}...")
            cmd = [sys.executable, "-m", "streamlit", "run",
                   str(dashboards_dir / file), "--server.port", str(port)]
            subprocess.run(cmd)
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    main()
"""
        zipf.writestr("project-template/dashboards/run_dashboard.py", launcher_content)
        print("  [Tool] dashboards/run_dashboard.py")

    print(f"\n{'='*50}")
    print(f"SUCCESS! FULL template created: {output_zip}")
    print(f"Size: {os.path.getsize(output_zip) / 1024:.1f} KB")
    print(f"{'='*50}\n")

    print("Includes:")
    print("  ✓ Flask Web App")
    print("  ✓ 3 Streamlit Dashboards")
    print("  ✓ CLI Tool")
    print("  ✓ Constitution Framework")
    print("  ✓ All requirements (streamlit, pandas, plotly)")
    print("\nYou can:")
    print("  - Copy to USB")
    print("  - Share with team")
    print("  - Extract and start developing immediately")


if __name__ == "__main__":
    create_full_template_zip()
