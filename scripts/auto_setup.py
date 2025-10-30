"""자동 환경 설정 및 Agent 구성 도구.

이 스크립트는 Dev Rules 시스템을 처음 사용할 때 필요한 모든 설정을 자동으로 수행합니다.
"""

import json
import subprocess
import sys
from pathlib import Path


class AutoSetup:
    """자동 설정 관리자."""

    def __init__(self):
        """초기화."""
        self.project_root = Path.cwd()
        self.config_dir = self.project_root / ".agent_configs"
        self.supported_agents = ["claude", "cursor", "aider", "codex", "copilot"]

    def run(self):
        """전체 설정 프로세스 실행."""
        print("=" * 50)
        print("  Dev Rules 자동 설정 시작")
        print("=" * 50)
        print()

        # 1. 환경 확인
        self.check_environment()

        # 2. 디렉토리 구조 생성
        self.create_directories()

        # 3. Agent 설정 파일 생성
        self.create_agent_configs()

        # 4. 환경 변수 설정
        self.setup_environment()

        # 5. 의존성 확인
        self.check_dependencies()

        # 6. 초기 테스트
        self.run_initial_tests()

        print()
        print("✅ 설정 완료!")
        print()
        self.print_next_steps()

    def check_environment(self):
        """환경 확인."""
        print("[1/6] 환경 확인 중...")

        # Python 버전 확인
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"⚠️  Python {version.major}.{version.minor} 감지됨")
            print("   Python 3.8 이상을 권장합니다.")
        else:
            print(f"✓ Python {version.major}.{version.minor} 확인")

        # Git 확인
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("✓ Git 설치 확인")
        except Exception:
            print("⚠️  Git이 설치되어 있지 않습니다.")

    def create_directories(self):
        """필요한 디렉토리 생성."""
        print("[2/6] 디렉토리 구조 생성 중...")

        directories = [
            self.config_dir,
            self.project_root / "tests",
            self.project_root / "scripts",
            self.project_root / "docs",
            self.project_root / "evidence",
            self.project_root / "SPEC",
            self.project_root / "claudedocs",
            self.project_root / "web" / "static",
            self.project_root / "web" / "templates",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"✓ {len(directories)}개 디렉토리 생성 완료")

    def create_agent_configs(self):
        """Agent별 설정 파일 생성."""
        print("[3/6] Agent 설정 파일 생성 중...")

        # Claude 설정
        claude_config = {
            "agent": "claude",
            "version": "latest",
            "dev_rules": {
                "enabled": True,
                "base_path": str(self.project_root),
                "tools": {
                    "tdd": {
                        "command": "python scripts/tier1_cli.py tdd --strict",
                        "description": "TDD 강제 실행",
                        "shortcut": "tdd",
                    },
                    "test": {
                        "command": "python scripts/incremental_test_runner.py",
                        "description": "증분 테스트 실행",
                        "shortcut": "test",
                    },
                    "parallel_test": {
                        "command": "python scripts/selective_parallel_runner.py",
                        "description": "선택적 병렬 테스트",
                        "shortcut": "ptest",
                    },
                    "tag": {"command": "python scripts/simple_tag_system.py", "description": "TAG 관리", "shortcut": "tag"},
                    "cache": {
                        "command": "python scripts/smart_cache_manager.py",
                        "description": "캐시 관리",
                        "shortcut": "cache",
                    },
                    "clean": {
                        "command": "python scripts/evidence_cleaner.py",
                        "description": "증거 파일 정리",
                        "shortcut": "clean",
                    },
                },
            },
            "workflow": {
                "development": [
                    "1. PRD 분석 → SPEC 생성",
                    "2. 테스트 작성 (TDD)",
                    "3. 구현 코드 작성",
                    "4. 증분 테스트 실행",
                    "5. 커버리지 체크 (85%+)",
                    "6. TAG 추가 및 동기화",
                ],
                "shortcuts": {"quick_tdd": "tdd && test", "full_test": "test && ptest", "cleanup": "clean && cache clear"},
            },
            "preferences": {
                "coverage_threshold": 85,
                "test_first": True,
                "auto_tag": True,
                "cache_config": True,
                "evidence_retention_days": 7,
            },
        }

        # Cursor 설정
        cursor_config = {
            "agent": "cursor",
            "version": "latest",
            "dev_rules": {
                "enabled": True,
                "base_path": str(self.project_root),
                "integration": {"type": "inline", "auto_suggest": True},
                "tools": claude_config["dev_rules"]["tools"],  # 동일한 도구 사용
            },
            "cursor_specific": {"auto_complete": True, "inline_hints": True, "test_on_save": False},
        }

        # Aider 설정
        aider_config = {
            "agent": "aider",
            "version": "latest",
            "dev_rules": {
                "enabled": True,
                "base_path": str(self.project_root),
                "git_integration": True,
                "auto_commit": False,
                "tools": claude_config["dev_rules"]["tools"],
            },
            "aider_specific": {"model": "gpt-4", "edit_format": "whole", "auto_test": True},
        }

        # Codex 설정
        codex_config = {
            "agent": "codex",
            "version": "latest",
            "dev_rules": {
                "enabled": True,
                "base_path": str(self.project_root),
                "optimization_focus": "algorithm",
                "tools": claude_config["dev_rules"]["tools"],
            },
        }

        # GitHub Copilot 설정
        copilot_config = {
            "agent": "github_copilot",
            "version": "latest",
            "dev_rules": {
                "enabled": True,
                "base_path": str(self.project_root),
                "suggestion_mode": "auto",
                "tools": claude_config["dev_rules"]["tools"],
            },
        }

        # 설정 파일 저장
        configs = {
            "claude": claude_config,
            "cursor": cursor_config,
            "aider": aider_config,
            "codex": codex_config,
            "copilot": copilot_config,
        }

        for agent_name, config in configs.items():
            config_file = self.config_dir / f"{agent_name}_config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✓ {agent_name}_config.json 생성")

    def setup_environment(self):
        """환경 변수 설정."""
        print("[4/6] 환경 변수 설정 중...")

        env_content = f"""# Dev Rules System Environment Variables
DEV_RULES_PATH={self.project_root}
DEV_RULES_MODE=hybrid
PYTHONPATH={self.project_root};$PYTHONPATH

# Agent Settings
CLAUDE_ENABLED=true
CODEX_ENABLED=true
CURSOR_ENABLED=true
AIDER_ENABLED=true
COPILOT_ENABLED=true

# Web UI Settings
WEB_UI_PORT=8000
WEB_UI_HOST=0.0.0.0

# Development Settings
TDD_STRICT=true
COVERAGE_THRESHOLD=85
EVIDENCE_RETENTION_DAYS=7
CACHE_CONFIG_ONLY=true

# Performance Settings
PARALLEL_TEST_THRESHOLD=50
INCREMENTAL_TEST=true
SMART_CACHE=true
"""

        env_file = self.project_root / ".env"
        with open(env_file, "w") as f:
            f.write(env_content)

        print("✓ .env 파일 생성")

        # .gitignore 업데이트
        gitignore_additions = """
# Dev Rules System
.agent_configs/
evidence/
.env
*.cache
*.pyc
__pycache__/
venv/
.pytest_cache/
.coverage
htmlcov/
"""

        gitignore_file = self.project_root / ".gitignore"
        if gitignore_file.exists():
            with open(gitignore_file, "a") as f:
                f.write(gitignore_additions)
        else:
            with open(gitignore_file, "w") as f:
                f.write(gitignore_additions)

        print("✓ .gitignore 업데이트")

    def check_dependencies(self):
        """의존성 확인 및 설치."""
        print("[5/6] 의존성 확인 중...")

        required_packages = ["fastapi", "uvicorn", "websockets", "pyyaml", "pytest", "pytest-cov", "pytest-xdist", "click"]

        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)

        if missing:
            print(f"⚠️  누락된 패키지: {', '.join(missing)}")
            response = input("설치하시겠습니까? (y/n): ")
            if response.lower() == "y":
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
                print("✓ 패키지 설치 완료")
        else:
            print("✓ 모든 의존성 확인")

    def run_initial_tests(self):
        """초기 테스트 실행."""
        print("[6/6] 시스템 테스트 중...")

        # tier1_cli 도구 테스트
        try:
            result = subprocess.run([sys.executable, "scripts/tier1_cli.py", "--help"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ tier1_cli 정상 작동")
            else:
                print("⚠️  tier1_cli 실행 오류")
        except Exception as e:
            print(f"⚠️  테스트 실패: {e}")

    def print_next_steps(self):
        """다음 단계 안내."""
        print("=" * 50)
        print("  설정 완료! 다음 단계:")
        print("=" * 50)
        print()
        print("1. 시스템 시작:")
        print("   Windows: launch.bat")
        print("   Mac/Linux: ./launch.sh")
        print()
        print("2. 모드 선택:")
        print("   - CLI 모드: Agent가 직접 사용")
        print("   - Web UI: 브라우저에서 제어")
        print("   - Hybrid: 두 방식 동시 사용")
        print()
        print("3. Claude Code에서 사용:")
        print('   claude "이 프로젝트의 Dev Rules 시스템을 사용합니다"')
        print()
        print("4. 웹 대시보드:")
        print("   http://localhost:8000")
        print()
        print("자세한 내용은 docs/QUICKSTART.md 참조")


if __name__ == "__main__":
    setup = AutoSetup()
    setup.run()
