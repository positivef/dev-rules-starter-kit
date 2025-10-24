"""Tests for Feature Flag System.

Test Coverage:
- Singleton pattern
- Configuration loading
- Hierarchical feature checking
- Emergency disable/enable
- Configuration reload
- Error handling

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from scripts.feature_flags import FeatureFlags


@pytest.fixture
def temp_config(tmp_path: Path) -> Path:
    """Create temporary feature flag config for testing.

    Args:
        tmp_path: pytest temporary directory fixture.

    Returns:
        Path: Path to temporary config file.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "feature_flags.yaml"

    config = {
        "tier1_integration": {
            "enabled": True,
            "tools": {
                "spec_builder": {
                    "enabled": True,
                    "quick_mode_available": True,
                },
                "tdd_enforcer": {
                    "enabled": False,
                    "coverage_threshold": 85.0,
                },
            },
            "emergency": {
                "disable_all_tier1": False,
                "last_emergency_datetime": None,
            },
        }
    }

    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)

    return config_file


@pytest.fixture
def reset_singleton():
    """Reset FeatureFlags singleton between tests.

    Yields:
        None: Cleanup function.
    """
    # Reset singleton before test
    FeatureFlags._instance = None
    FeatureFlags._config = None

    yield

    # Reset singleton after test
    FeatureFlags._instance = None
    FeatureFlags._config = None


class TestFeatureFlagsSingleton:
    """Test singleton pattern implementation."""

    def test_singleton_pattern(self, reset_singleton):
        """Test that FeatureFlags implements singleton pattern."""
        flags1 = FeatureFlags()
        flags2 = FeatureFlags()

        assert flags1 is flags2
        assert id(flags1) == id(flags2)

    def test_singleton_config_cached(self, reset_singleton):
        """Test that configuration is cached in singleton."""
        flags1 = FeatureFlags()
        config1 = flags1._config

        flags2 = FeatureFlags()
        config2 = flags2._config

        assert config1 is config2


class TestConfigurationLoading:
    """Test configuration file loading."""

    def test_load_config_success(self, reset_singleton, monkeypatch):
        """Test successful configuration loading."""
        test_config = {
            "tier1_integration": {
                "enabled": True,
                "tools": {"spec_builder": {"enabled": True}},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.safe_dump(test_config, f)
            temp_path = Path(f.name)

        try:
            monkeypatch.setattr(FeatureFlags, "_config_path", temp_path)
            flags = FeatureFlags()

            assert flags._config is not None
            assert flags._config["tier1_integration"]["enabled"] is True
        finally:
            temp_path.unlink()

    def test_load_config_file_not_found(self, reset_singleton, monkeypatch):
        """Test error handling when config file doesn't exist."""
        monkeypatch.setattr(FeatureFlags, "_config_path", Path("/nonexistent/config.yaml"))

        with pytest.raises(FileNotFoundError, match="Feature flag config not found"):
            FeatureFlags()

    def test_load_config_empty_file(self, reset_singleton, monkeypatch):
        """Test error handling for empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            monkeypatch.setattr(FeatureFlags, "_config_path", temp_path)

            with pytest.raises(ValueError, match="Empty feature flag config"):
                FeatureFlags()
        finally:
            temp_path.unlink()


class TestIsEnabled:
    """Test feature flag checking."""

    def test_is_enabled_top_level(self, reset_singleton, monkeypatch, temp_config):
        """Test checking top-level feature flag."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        assert flags.is_enabled("tier1_integration") is True

    def test_is_enabled_nested_path(self, reset_singleton, monkeypatch, temp_config):
        """Test checking nested feature flag with dot notation."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        assert flags.is_enabled("tier1_integration.tools.spec_builder") is True
        assert flags.is_enabled("tier1_integration.tools.tdd_enforcer") is False

    def test_is_enabled_deep_nested_boolean(self, reset_singleton, monkeypatch, temp_config):
        """Test checking deeply nested boolean value."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        assert flags.is_enabled("tier1_integration.tools.spec_builder.quick_mode_available") is True

    def test_is_enabled_nonexistent_path(self, reset_singleton, monkeypatch, temp_config):
        """Test checking non-existent feature path returns False."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        assert flags.is_enabled("tier1_integration.nonexistent") is False
        assert flags.is_enabled("tier1_integration.tools.nonexistent") is False

    def test_is_enabled_with_emergency_disable(self, reset_singleton, monkeypatch, temp_config):
        """Test that emergency disable overrides all feature flags."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        # First verify feature is enabled
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is True

        # Manually set emergency disable
        flags._config["tier1_integration"]["emergency"]["disable_all_tier1"] = True

        # Now all features should be disabled
        assert flags.is_enabled("tier1_integration") is False
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is False


class TestEmergencyDisable:
    """Test emergency disable functionality."""

    def test_emergency_disable(self, reset_singleton, monkeypatch, temp_config):
        """Test emergency_disable sets flag and timestamp."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        # Verify initially enabled
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is True

        # Emergency disable
        flags.emergency_disable()

        # Verify disabled
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is False
        assert flags._config["tier1_integration"]["emergency"]["disable_all_tier1"] is True
        assert flags._config["tier1_integration"]["emergency"]["last_emergency_datetime"] is not None

    def test_emergency_enable(self, reset_singleton, monkeypatch, temp_config):
        """Test emergency_enable re-enables features."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        # First disable
        flags.emergency_disable()
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is False

        # Then re-enable
        flags.emergency_enable()
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is True
        assert flags._config["tier1_integration"]["emergency"]["disable_all_tier1"] is False


class TestGetConfig:
    """Test configuration value retrieval."""

    def test_get_config_simple_value(self, reset_singleton, monkeypatch, temp_config):
        """Test retrieving simple configuration value."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        threshold = flags.get_config("tier1_integration.tools.tdd_enforcer.coverage_threshold")
        assert threshold == 85.0

    def test_get_config_dict_value(self, reset_singleton, monkeypatch, temp_config):
        """Test retrieving dictionary configuration value."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        tools = flags.get_config("tier1_integration.tools")
        assert isinstance(tools, dict)
        assert "spec_builder" in tools
        assert "tdd_enforcer" in tools

    def test_get_config_nonexistent(self, reset_singleton, monkeypatch, temp_config):
        """Test retrieving non-existent config returns None."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        result = flags.get_config("tier1_integration.nonexistent")
        assert result is None


class TestReload:
    """Test configuration reload functionality."""

    def test_reload_config(self, reset_singleton, monkeypatch, temp_config):
        """Test reloading configuration from file."""
        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)
        flags = FeatureFlags()

        # Verify initial state
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is True

        # Modify config file
        with open(temp_config, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        config["tier1_integration"]["tools"]["spec_builder"]["enabled"] = False
        with open(temp_config, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f)

        # Reload and verify change
        flags.reload()
        assert flags.is_enabled("tier1_integration.tools.spec_builder") is False


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_is_enabled_with_none_config(self, reset_singleton):
        """Test is_enabled returns False when config is None."""
        flags = FeatureFlags.__new__(FeatureFlags)
        flags._config = None

        assert flags.is_enabled("tier1_integration") is False

    def test_emergency_disable_with_none_config(self, reset_singleton):
        """Test emergency_disable handles None config gracefully."""
        flags = FeatureFlags.__new__(FeatureFlags)
        flags._config = None

        # Should not raise exception
        flags.emergency_disable()

    def test_get_config_with_none_config(self, reset_singleton):
        """Test get_config returns None when config is None."""
        flags = FeatureFlags.__new__(FeatureFlags)
        flags._config = None

        assert flags.get_config("tier1_integration") is None
