"""Feature Flag System for Tier 1 Integration.

This module provides granular control over Tier 1 features with emergency
disable capability. Implements singleton pattern for configuration caching.

Compliance:
- P1: YAML-First (reads from config/feature_flags.yaml)
- P4: SOLID principles (SRP, dependency injection)
- P5: Security (no secrets, safe file operations)
- P10: Windows encoding (UTF-8 explicit, no emojis)

Example:
    >>> flags = FeatureFlags()
    >>> if flags.is_enabled("tier1_integration.tools.spec_builder"):
    ...     print("SpecBuilder is enabled")
    >>> flags.emergency_disable()
    >>> print(flags.is_enabled("tier1_integration.tools.spec_builder"))
    False
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class FeatureFlags:
    """Singleton feature flag manager for Tier 1 integration.

    Provides hierarchical feature control with emergency disable capability.
    Configuration is cached for performance.

    Attributes:
        _instance: Singleton instance (class variable).
        _config: Cached configuration dictionary.
        _config_path: Path to feature_flags.yaml.
    """

    _instance: Optional["FeatureFlags"] = None
    _config: Optional[Dict[str, Any]] = None
    _config_path: Path = Path(__file__).parent.parent / "config" / "feature_flags.yaml"

    def __new__(cls) -> "FeatureFlags":
        """Create or return singleton instance.

        Returns:
            FeatureFlags: Singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Dict[str, Any]: Configuration dictionary.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If config file is invalid YAML.
        """
        if not cls._config_path.exists():
            raise FileNotFoundError(f"Feature flag config not found: {cls._config_path}")

        with open(cls._config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config is None:
            raise ValueError(f"Empty feature flag config: {cls._config_path}")

        return config

    @classmethod
    def _save_config(cls) -> None:
        """Save current configuration to YAML file.

        Raises:
            PermissionError: If config file is not writable.
        """
        if cls._config is None:
            return

        with open(cls._config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cls._config, f, default_flow_style=False, sort_keys=False)

    def is_enabled(self, feature_path: str) -> bool:
        """Check if a feature is enabled.

        Supports hierarchical paths with dot notation.
        Emergency disable overrides all individual settings.

        Args:
            feature_path: Dot-separated path (e.g., "tier1_integration.tools.spec_builder").

        Returns:
            bool: True if feature is enabled, False otherwise.

        Example:
            >>> flags = FeatureFlags()
            >>> flags.is_enabled("tier1_integration.tools.spec_builder")
            True
            >>> flags.is_enabled("tier1_integration.tools.spec_builder.quick_mode_available")
            True
        """
        if self._config is None:
            return False

        # Check emergency disable first
        emergency = self._config.get("tier1_integration", {}).get("emergency", {})
        if emergency.get("disable_all_tier1", False):
            return False

        # Navigate configuration path
        parts = feature_path.split(".")
        current: Any = self._config

        for part in parts:
            if not isinstance(current, dict):
                return False
            current = current.get(part)
            if current is None:
                return False

        # If we reached a boolean value, return it
        if isinstance(current, bool):
            return current

        # If we reached a dict, check for 'enabled' key
        if isinstance(current, dict):
            return current.get("enabled", False)

        return False

    def emergency_disable(self) -> None:
        """Immediately disable all Tier 1 features.

        Sets emergency.disable_all_tier1 to True and records timestamp.
        This provides 1-minute rollback capability without code deletion.

        Example:
            >>> flags = FeatureFlags()
            >>> flags.emergency_disable()
            >>> print("[EMERGENCY] All Tier 1 features disabled")
        """
        if self._config is None:
            return

        emergency = self._config.setdefault("tier1_integration", {}).setdefault("emergency", {})
        emergency["disable_all_tier1"] = True
        emergency["last_emergency_datetime"] = datetime.now().isoformat()

        self._save_config()

    def emergency_enable(self) -> None:
        """Re-enable all Tier 1 features after emergency disable.

        Sets emergency.disable_all_tier1 to False.

        Example:
            >>> flags = FeatureFlags()
            >>> flags.emergency_enable()
            >>> print("[RECOVERY] Tier 1 features re-enabled")
        """
        if self._config is None:
            return

        emergency = self._config.setdefault("tier1_integration", {}).setdefault("emergency", {})
        emergency["disable_all_tier1"] = False

        self._save_config()

    def get_config(self, config_path: str) -> Any:
        """Get configuration value at specified path.

        Args:
            config_path: Dot-separated path to config value.

        Returns:
            Any: Configuration value, or None if not found.

        Example:
            >>> flags = FeatureFlags()
            >>> threshold = flags.get_config("tier1_integration.tools.tdd_enforcer.coverage_threshold")
            >>> print(threshold)
            85.0
        """
        if self._config is None:
            return None

        parts = config_path.split(".")
        current: Any = self._config

        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None

        return current

    def reload(self) -> None:
        """Reload configuration from YAML file.

        Use this to pick up external config changes without restarting.

        Example:
            >>> flags = FeatureFlags()
            >>> flags.reload()
            >>> print("[OK] Configuration reloaded")
        """
        self.__class__._config = self._load_config()
