"""Interactive Setup Wizard for Tier 1 Integration System.

Provides guided setup experience for new users.
"""

import sys
from pathlib import Path
from typing import Dict

import yaml


class SetupWizard:
    """Interactive setup wizard for easy onboarding."""

    def __init__(self):
        """Initialize setup wizard."""
        self.config = {}
        self.preset_manager = None

    def welcome(self) -> None:
        """Display welcome message."""
        print("\n" + "=" * 60)
        print(" Welcome to Tier 1 Integration System Setup Wizard")
        print("=" * 60)
        print("\nThis wizard will help you configure the system for your needs.")
        print("Press Ctrl+C at any time to exit.\n")

    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question.

        Args:
            question: Question to ask.
            default: Default answer.

        Returns:
            User's answer as boolean.
        """
        default_str = "Y/n" if default else "y/N"
        while True:
            answer = input(f"{question} [{default_str}]: ").strip().lower()
            if answer == "":
                return default
            elif answer in ["y", "yes"]:
                return True
            elif answer in ["n", "no"]:
                return False
            else:
                print("Please answer 'yes' or 'no' (or y/n)")

    def ask_choice(self, question: str, choices: Dict[str, str], default: str = None) -> str:
        """Ask user to choose from options.

        Args:
            question: Question to ask.
            choices: Dictionary of choice_key -> description.
            default: Default choice key.

        Returns:
            Selected choice key.
        """
        print(f"\n{question}")
        for i, (key, desc) in enumerate(choices.items(), 1):
            marker = " (default)" if key == default else ""
            print(f"  {i}. {desc}{marker}")

        while True:
            answer = input(f"\nSelect option [1-{len(choices)}]: ").strip()
            if answer == "" and default:
                return default

            try:
                idx = int(answer) - 1
                if 0 <= idx < len(choices):
                    return list(choices.keys())[idx]
            except ValueError:
                pass

            print(f"Please enter a number between 1 and {len(choices)}")

    def ask_number(self, question: str, min_val: int, max_val: int, default: int) -> int:
        """Ask for a numeric value.

        Args:
            question: Question to ask.
            min_val: Minimum value.
            max_val: Maximum value.
            default: Default value.

        Returns:
            User's numeric choice.
        """
        while True:
            answer = input(f"{question} [{default}]: ").strip()
            if answer == "":
                return default

            try:
                value = int(answer)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")

    def setup_experience_level(self) -> str:
        """Setup based on user experience level.

        Returns:
            Selected preset name.
        """
        choices = {
            "beginner": "New to the system (Recommended for first-time users)",
            "standard": "Some experience with similar tools",
            "advanced": "Expert user, need all features",
            "minimal": "Just want to try it out quickly",
        }

        level = self.ask_choice("What's your experience level with development tools?", choices, default="beginner")

        print(f"\n✓ Selected: {choices[level]}")
        return level

    def setup_project_type(self) -> Dict:
        """Setup based on project type.

        Returns:
            Configuration adjustments.
        """
        choices = {
            "web": "Web application (React, Vue, etc.)",
            "api": "API/Backend service",
            "cli": "Command-line tool",
            "library": "Shared library/package",
            "fullstack": "Full-stack application",
        }

        project_type = self.ask_choice("What type of project are you working on?", choices)

        # Adjust configuration based on project type
        adjustments = {
            "web": {
                "tdd_threshold": 70,  # Lower for UI components
                "enable_ui_tags": True,
            },
            "api": {
                "tdd_threshold": 90,  # Higher for APIs
                "enable_api_tags": True,
            },
            "cli": {
                "tdd_threshold": 85,
                "enable_cli_features": True,
            },
            "library": {
                "tdd_threshold": 95,  # Highest for libraries
                "strict_mode": True,
            },
            "fullstack": {
                "tdd_threshold": 80,
                "enable_all_features": True,
            },
        }

        print(f"\n✓ Project type: {choices[project_type]}")
        return adjustments.get(project_type, {})

    def setup_team_size(self) -> Dict:
        """Setup based on team size.

        Returns:
            Configuration adjustments.
        """
        choices = {
            "solo": "Just me",
            "small": "2-5 developers",
            "medium": "6-20 developers",
            "large": "20+ developers",
        }

        team_size = self.ask_choice("How large is your team?", choices)

        adjustments = {
            "solo": {
                "notifications": False,
                "strict_tags": False,
            },
            "small": {
                "notifications": True,
                "strict_tags": False,
            },
            "medium": {
                "notifications": True,
                "strict_tags": True,
                "parallel_workers": 4,
            },
            "large": {
                "notifications": True,
                "strict_tags": True,
                "parallel_workers": 8,
                "require_reviews": True,
            },
        }

        print(f"\n✓ Team size: {choices[team_size]}")
        return adjustments.get(team_size, {})

    def setup_features(self) -> Dict:
        """Setup individual features.

        Returns:
            Feature configuration.
        """
        print("\n" + "-" * 40)
        print("Feature Configuration")
        print("-" * 40)

        features = {}

        # TDD Enforcement
        if self.ask_yes_no("\nEnable Test-Driven Development enforcement?", default=True):
            threshold = self.ask_number("Minimum test coverage percentage", min_val=0, max_val=100, default=85)
            features["tdd_enabled"] = True
            features["tdd_threshold"] = threshold
        else:
            features["tdd_enabled"] = False

        # Parallel Processing
        if self.ask_yes_no("\nEnable parallel processing for better performance?", default=True):
            import multiprocessing

            max_workers = multiprocessing.cpu_count()
            workers = self.ask_number(
                f"Number of parallel workers (you have {max_workers} cores)",
                min_val=1,
                max_val=max_workers * 2,
                default=max_workers,
            )
            features["parallel_enabled"] = True
            features["parallel_workers"] = workers
        else:
            features["parallel_enabled"] = False

        # Notifications
        if self.ask_yes_no("\nEnable notifications for important events?", default=False):
            features["notifications_enabled"] = True
            print("Note: You'll need to configure Slack webhook or email settings later")
        else:
            features["notifications_enabled"] = False

        return features

    def apply_configuration(self, preset: str, adjustments: Dict) -> bool:
        """Apply the selected configuration.

        Args:
            preset: Base preset name.
            adjustments: Configuration adjustments.

        Returns:
            True if successful.
        """
        try:
            # Load preset
            from preset_manager import PresetManager

            self.preset_manager = PresetManager()

            # Apply base preset
            if not self.preset_manager.apply_preset(preset):
                print("[ERROR] Failed to apply preset")
                return False

            # Apply adjustments
            config_path = Path("config/feature_flags.yaml")
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Apply all adjustments
            for key, value in adjustments.items():
                if "tdd_threshold" in key:
                    config["tier1_integration"]["tools"]["tdd_enforcer"]["coverage_threshold"] = value
                elif "parallel_workers" in key:
                    config["tier1_integration"]["parallel_processing"]["max_workers"] = value
                elif "parallel_enabled" in key:
                    config["tier1_integration"]["parallel_processing"]["enabled"] = value
                elif "notifications_enabled" in key:
                    if "notifications" not in config["tier1_integration"]:
                        config["tier1_integration"]["notifications"] = {}
                    config["tier1_integration"]["notifications"]["enabled"] = value

            # Save adjusted configuration
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, default_flow_style=False)

            return True

        except Exception as e:
            print(f"[ERROR] Configuration failed: {e}")
            return False

    def create_shortcuts(self) -> None:
        """Create convenient shortcuts for common commands."""
        print("\n" + "-" * 40)
        print("Creating shortcuts...")
        print("-" * 40)

        shortcuts = {
            "tier1": "python scripts/tier1_cli.py",
            "test": "python scripts/test_runner.py --quick",
            "test-all": "python scripts/test_runner.py --all",
            "preset": "python scripts/preset_manager.py",
            "status": "python scripts/tier1_cli.py status",
        }

        # Create shortcuts based on OS
        if sys.platform == "win32":
            # Windows batch files
            for name, command in shortcuts.items():
                bat_file = Path(f"{name}.bat")
                bat_file.write_text(f"@echo off\n{command} %*\n")
                print(f"  Created: {name}.bat")
        else:
            # Unix shell scripts
            for name, command in shortcuts.items():
                sh_file = Path(f"{name}.sh")
                sh_file.write_text(f'#!/bin/bash\n{command} "$@"\n')
                sh_file.chmod(0o755)
                print(f"  Created: {name}.sh")

    def display_next_steps(self) -> None:
        """Display next steps for the user."""
        print("\n" + "=" * 60)
        print(" Setup Complete! 🎉")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test your setup:")
        print("   python scripts/tier1_cli.py status")
        print("\n2. Create your first SPEC:")
        print("   python scripts/tier1_cli.py spec 'My new feature'")
        print("\n3. Run tests:")
        print("   python scripts/test_runner.py --quick")
        print("\n4. View all commands:")
        print("   python scripts/tier1_cli.py --help")
        print("\nFor more help, see docs/README.md")
        print("\nHappy coding! 🚀\n")

    def run(self) -> bool:
        """Run the setup wizard.

        Returns:
            True if setup completed successfully.
        """
        try:
            self.welcome()

            # Step 1: Experience level (determines base preset)
            preset = self.setup_experience_level()

            # Step 2: Project type
            project_adjustments = self.setup_project_type()

            # Step 3: Team size
            team_adjustments = self.setup_team_size()

            # Step 4: Individual features
            feature_adjustments = self.setup_features()

            # Combine all adjustments
            all_adjustments = {**project_adjustments, **team_adjustments, **feature_adjustments}

            # Step 5: Apply configuration
            print("\n" + "-" * 40)
            print("Applying configuration...")
            print("-" * 40)

            if self.apply_configuration(preset, all_adjustments):
                print("✓ Configuration applied successfully")
            else:
                print("✗ Configuration failed")
                return False

            # Step 6: Create shortcuts
            if self.ask_yes_no("\nCreate command shortcuts for easier access?", default=True):
                self.create_shortcuts()

            # Step 7: Display next steps
            self.display_next_steps()

            return True

        except KeyboardInterrupt:
            print("\n\n[INFO] Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\n[ERROR] Setup failed: {e}")
            return False


def main():
    """Run the setup wizard."""
    wizard = SetupWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
