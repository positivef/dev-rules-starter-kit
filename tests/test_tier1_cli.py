"""Tests for Tier 1 Unified CLI.

Test Coverage:
- All commands (spec, tdd, tag, status, disable, enable)
- Feature flag integration
- Emergency controls
- Option handling

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from scripts.tier1_cli import cli


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
                    "enabled": True,
                    "coverage_threshold": 85.0,
                    "strict_mode": False,
                },
                "tag_tracer": {
                    "enabled": True,
                    "chain_validation": True,
                    "auto_tag_suggestion": True,
                },
            },
            "mitigation": {
                "quick_mode": {
                    "enabled": True,
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
    """Reset FeatureFlags singleton between tests."""
    from scripts.feature_flags import FeatureFlags

    FeatureFlags._instance = None
    FeatureFlags._config = None
    yield
    FeatureFlags._instance = None
    FeatureFlags._config = None


@pytest.fixture
def runner() -> CliRunner:
    """Create Click CLI test runner.

    Returns:
        CliRunner: Click test runner.
    """
    return CliRunner()


class TestSpecCommand:
    """Test 'spec' command."""

    def test_spec_basic(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test basic spec command execution."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["spec", "Add user auth"])

        assert result.exit_code == 0
        assert "[INFO] Creating SPEC for: Add user auth" in result.output
        assert "[INFO] Template: feature" in result.output
        assert "[INFO] Quick mode: False" in result.output

    def test_spec_with_template(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test spec command with template option."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["spec", "Fix login bug", "-t", "bugfix"])

        assert result.exit_code == 0
        assert "[INFO] Template: bugfix" in result.output

    def test_spec_quick_mode(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test spec command with quick mode."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["spec", "Refactor auth", "-q"])

        assert result.exit_code == 0
        assert "[INFO] Quick mode: True" in result.output


class TestTddCommand:
    """Test 'tdd' command."""

    def test_tdd_basic(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test basic tdd command execution."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tdd"])

        assert result.exit_code == 0
        assert "[INFO] Coverage threshold: 85.0%" in result.output
        assert "[INFO] Strict mode: False" in result.output

    def test_tdd_with_threshold(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tdd command with custom threshold."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tdd", "--threshold", "90"])

        assert result.exit_code == 0
        assert "[INFO] Coverage threshold: 90.0%" in result.output

    def test_tdd_strict_mode(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tdd command with strict mode."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tdd", "--strict"])

        assert result.exit_code == 0
        assert "[INFO] Strict mode: True" in result.output

    def test_tdd_quick_mode(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tdd command with quick mode."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tdd", "-q"])

        assert result.exit_code == 0
        assert "[INFO] Quick mode: True" in result.output


class TestTagCommand:
    """Test 'tag' command."""

    def test_tag_single_tag(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tag command with single @TAG."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tag", "@REQ-001"])

        assert result.exit_code == 0
        assert "[INFO] Tracing @TAG chain: @REQ-001" in result.output

    def test_tag_multiple_tags(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tag command with multiple @TAGs."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tag", "@REQ-001", "@IMPL-001"])

        assert result.exit_code == 0
        assert "[INFO] Tracing @TAG chain: @REQ-001 @IMPL-001" in result.output

    def test_tag_suggest_mode(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test tag command with auto-suggest."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["tag", "--suggest"])

        assert result.exit_code == 0
        assert "[INFO] Auto-suggest: True" in result.output


class TestStatusCommand:
    """Test 'status' command."""

    def test_status_basic(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test basic status command."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "Tier 1 Integration Status" in result.output
        assert "spec_builder: [ENABLED]" in result.output
        assert "tdd_enforcer: [ENABLED]" in result.output
        assert "tag_tracer: [ENABLED]" in result.output

    def test_status_verbose(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test status command with verbose flag."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["status", "-v"])

        assert result.exit_code == 0
        assert "Configuration Details:" in result.output
        assert "coverage_threshold: 85.0" in result.output


class TestDisableCommand:
    """Test 'disable' command."""

    def test_disable_all(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test emergency disable all features."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["disable", "all"])

        assert result.exit_code == 0
        assert "[EMERGENCY]" in result.output
        assert "All Tier 1 features disabled" in result.output

    def test_disable_individual_tool(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test individual tool disable (not fully implemented)."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["disable", "spec_builder"])

        assert result.exit_code == 0
        assert "[NOT_IMPLEMENTED]" in result.output


class TestEnableCommand:
    """Test 'enable' command."""

    def test_enable_all(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test emergency enable all features."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        # First disable
        runner.invoke(cli, ["disable", "all"])

        # Then enable
        result = runner.invoke(cli, ["enable", "all"])

        assert result.exit_code == 0
        assert "[RECOVERY]" in result.output
        assert "All Tier 1 features re-enabled" in result.output

    def test_enable_individual_tool(self, runner: CliRunner, reset_singleton, monkeypatch, temp_config):
        """Test individual tool enable (not fully implemented)."""
        from scripts.feature_flags import FeatureFlags

        monkeypatch.setattr(FeatureFlags, "_config_path", temp_config)

        result = runner.invoke(cli, ["enable", "spec_builder"])

        assert result.exit_code == 0
        assert "[NOT_IMPLEMENTED]" in result.output


class TestCLIVersion:
    """Test CLI version and help."""

    def test_cli_version(self, runner: CliRunner):
        """Test --version flag."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "tier1_cli, version 1.0.0" in result.output

    def test_cli_help(self, runner: CliRunner):
        """Test --help flag."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Tier 1 Integration Tools" in result.output
        assert "spec" in result.output
        assert "tdd" in result.output
        assert "tag" in result.output
        assert "status" in result.output

    def test_spec_help(self, runner: CliRunner):
        """Test spec command help."""
        result = runner.invoke(cli, ["spec", "--help"])

        assert result.exit_code == 0
        assert "Create SPEC and YAML contract" in result.output

    def test_tdd_help(self, runner: CliRunner):
        """Test tdd command help."""
        result = runner.invoke(cli, ["tdd", "--help"])

        assert result.exit_code == 0
        assert "Enforce TDD coverage gate" in result.output

    def test_tag_help(self, runner: CliRunner):
        """Test tag command help."""
        result = runner.invoke(cli, ["tag", "--help"])

        assert result.exit_code == 0
        assert "Trace @TAG chains" in result.output

    def test_status_help(self, runner: CliRunner):
        """Test status command help."""
        result = runner.invoke(cli, ["status", "--help"])

        assert result.exit_code == 0
        assert "Display feature flag status" in result.output

    def test_disable_help(self, runner: CliRunner):
        """Test disable command help."""
        result = runner.invoke(cli, ["disable", "--help"])

        assert result.exit_code == 0
        assert "Disable a Tier 1 tool" in result.output

    def test_enable_help(self, runner: CliRunner):
        """Test enable command help."""
        result = runner.invoke(cli, ["enable", "--help"])

        assert result.exit_code == 0
        assert "Enable a Tier 1 tool" in result.output
