"""Configuration Preset Manager for Tier 1 Integration System.

Simplifies configuration management with pre-defined presets.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class PresetManager:
    """Manages configuration presets for simplified setup."""

    def __init__(self, presets_path: Optional[Path] = None, config_path: Optional[Path] = None):
        """Initialize preset manager.

        Args:
            presets_path: Path to presets.yaml file.
            config_path: Path to feature_flags.yaml file.
        """
        self.presets_path = presets_path or Path("config/presets.yaml")
        self.config_path = config_path or Path("config/feature_flags.yaml")
        self.presets = self._load_presets()

    def _load_presets(self) -> Dict:
        """Load presets from YAML file."""
        if not self.presets_path.exists():
            return {}

        with open(self.presets_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("presets", {})

    def list_presets(self) -> List[Dict]:
        """List all available presets.

        Returns:
            List of preset information.
        """
        result = []
        for key, preset in self.presets.items():
            result.append(
                {
                    "key": key,
                    "name": preset.get("name", key),
                    "description": preset.get("description", ""),
                }
            )
        return result

    def apply_preset(self, preset_name: str) -> bool:
        """Apply a preset configuration.

        Args:
            preset_name: Name of the preset to apply.

        Returns:
            True if successful, False otherwise.
        """
        if preset_name not in self.presets:
            print(f"[ERROR] Preset '{preset_name}' not found")
            return False

        preset = self.presets[preset_name]
        settings = preset.get("settings", {})

        # Backup current config
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix(".yaml.backup")
            shutil.copy2(self.config_path, backup_path)
            print(f"[INFO] Backed up current config to {backup_path}")

        # Apply preset settings
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(settings, f, default_flow_style=False)

            print(f"[SUCCESS] Applied preset: {preset['name']}")
            print(f"[INFO] Description: {preset.get('description', '')}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to apply preset: {e}")
            return False

    def get_preset_details(self, preset_name: str) -> Optional[Dict]:
        """Get detailed information about a preset.

        Args:
            preset_name: Name of the preset.

        Returns:
            Preset details or None if not found.
        """
        return self.presets.get(preset_name)

    def recommend_preset(self) -> str:
        """Recommend a preset based on user experience.

        Returns:
            Recommended preset name.
        """
        # Check if config exists and has been used
        if not self.config_path.exists():
            return "beginner"

        # Check current settings
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Analyze current configuration
            coverage_threshold = (
                config.get("tier1_integration", {}).get("tools", {}).get("tdd_enforcer", {}).get("coverage_threshold", 0)
            )

            parallel_enabled = config.get("tier1_integration", {}).get("parallel_processing", {}).get("enabled", False)

            if coverage_threshold >= 90 and parallel_enabled:
                return "advanced"
            elif coverage_threshold >= 80:
                return "standard"
            else:
                return "beginner"

        except Exception:
            return "beginner"


def main():
    """CLI for preset management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage configuration presets")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    subparsers.add_parser("list", help="List available presets")

    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply a preset")
    apply_parser.add_argument("preset", help="Preset name to apply")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show preset details")
    show_parser.add_argument("preset", help="Preset name to show")

    # Recommend command
    subparsers.add_parser("recommend", help="Get preset recommendation")

    args = parser.parse_args()

    manager = PresetManager()

    if args.command == "list":
        presets = manager.list_presets()
        print("\nAvailable Presets:")
        print("-" * 60)
        for preset in presets:
            print(f"  {preset['key']:12} - {preset['name']:20} {preset['description']}")
        print()

    elif args.command == "apply":
        success = manager.apply_preset(args.preset)
        if not success:
            print("\nAvailable presets:")
            for preset in manager.list_presets():
                print(f"  - {preset['key']}")

    elif args.command == "show":
        details = manager.get_preset_details(args.preset)
        if details:
            print(f"\nPreset: {details.get('name', args.preset)}")
            print(f"Description: {details.get('description', '')}")
            print("\nSettings:")
            print(yaml.dump(details.get("settings", {}), default_flow_style=False))
        else:
            print(f"Preset '{args.preset}' not found")

    elif args.command == "recommend":
        recommended = manager.recommend_preset()
        preset = manager.get_preset_details(recommended)
        print(f"\nRecommended preset: {preset.get('name', recommended)}")
        print(f"Description: {preset.get('description', '')}")
        print("\nApply with: python scripts/preset_manager.py apply " + recommended)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
