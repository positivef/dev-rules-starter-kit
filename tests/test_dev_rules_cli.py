#!/usr/bin/env python3
"""
Tests for dev-rules CLI

Purpose: Verify unified CLI functionality

Constitutional Compliance:
- [P3] Test-First Development
- [P5] Windows UTF-8: No emoji in code
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from click.testing import CliRunner
from dev_rules_cli import cli


class TestTaskCommands:
    """Test task management commands"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_task_list_command(self):
        """Test task list command"""
        result = self.runner.invoke(cli, ["task", "list"])
        assert result.exit_code == 0
        # Should show available tasks or message

    def test_task_list_verbose(self):
        """Test task list with verbose flag"""
        result = self.runner.invoke(cli, ["task", "list", "--verbose"])
        assert result.exit_code == 0

    def test_task_plan_nonexistent(self):
        """Test planning nonexistent task"""
        result = self.runner.invoke(cli, ["task", "plan", "NONEXISTENT-TASK"])
        assert result.exit_code == 1
        # Check stderr or output for error message
        if result.output:
            assert "not found" in result.output.lower() or "error" in result.output.lower()


class TestPromptCommands:
    """Test prompt compression commands"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_prompt_compress_basic(self):
        """Test basic prompt compression"""
        result = self.runner.invoke(cli, ["prompt", "compress", "Please implement authentication feature"])
        assert result.exit_code == 0
        assert "OUTPUT" in result.output or "Compressed" in result.output
        assert "SAVINGS" in result.output or "Savings" in result.output

    def test_prompt_compress_json(self):
        """Test prompt compression with JSON output"""
        result = self.runner.invoke(cli, ["prompt", "compress", "Test prompt", "--json"])
        assert result.exit_code == 0

        # Should be valid JSON
        import json

        output = json.loads(result.output)
        assert "original" in output
        assert "compressed" in output
        assert "savings_pct" in output

    def test_prompt_compress_levels(self):
        """Test different compression levels"""
        levels = ["light", "medium", "aggressive"]

        for level in levels:
            result = self.runner.invoke(cli, ["prompt", "compress", "Test prompt", "--level", level])
            assert result.exit_code == 0

    def test_prompt_stats(self):
        """Test prompt statistics"""
        result = self.runner.invoke(cli, ["prompt", "info"])
        assert result.exit_code == 0
        assert "Statistics" in result.output or "Compression" in result.output

    def test_prompt_demo(self):
        """Test prompt compression demo"""
        result = self.runner.invoke(cli, ["prompt", "demo"])
        assert result.exit_code == 0
        assert "Demo" in result.output or "DEMO" in result.output
        assert "Example" in result.output or "EXAMPLE" in result.output


class TestCLIBasics:
    """Test basic CLI functionality"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        """Test version command"""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.1.0" in result.output

    def test_help(self):
        """Test help command"""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "dev-rules" in result.output.lower() or "dev rules" in result.output.lower()
        assert "task" in result.output.lower()
        assert "prompt" in result.output.lower()

    def test_task_help(self):
        """Test task subcommand help"""
        result = self.runner.invoke(cli, ["task", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output.lower()
        assert "plan" in result.output.lower()
        assert "list" in result.output.lower()

    def test_prompt_help(self):
        """Test prompt subcommand help"""
        result = self.runner.invoke(cli, ["prompt", "--help"])
        assert result.exit_code == 0
        assert "compress" in result.output.lower()
        assert "info" in result.output.lower()
        assert "demo" in result.output.lower()


class TestErrorHandling:
    """Test error handling"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_invalid_command(self):
        """Test invalid command"""
        result = self.runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

    def test_invalid_subcommand(self):
        """Test invalid subcommand"""
        result = self.runner.invoke(cli, ["task", "invalid"])
        assert result.exit_code != 0

    def test_missing_argument(self):
        """Test missing required argument"""
        result = self.runner.invoke(cli, ["task", "run"])
        assert result.exit_code != 0

    def test_invalid_compression_level(self):
        """Test invalid compression level"""
        result = self.runner.invoke(cli, ["prompt", "compress", "test", "--level", "invalid"])
        assert result.exit_code != 0


class TestIntegration:
    """Integration tests"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_compress_saves_tokens(self):
        """Test that compression actually saves tokens"""
        long_prompt = "Please make sure that you implement the authentication feature for the web application"
        result = self.runner.invoke(cli, ["prompt", "compress", long_prompt, "--json"])

        assert result.exit_code == 0

        import json

        output = json.loads(result.output)
        assert output["compressed_tokens"] < output["original_tokens"]
        assert output["savings_pct"] > 0

    def test_multiple_compressions(self):
        """Test multiple consecutive compressions"""
        prompts = [
            "Please implement feature A",
            "Please implement feature B",
            "Please implement feature C",
        ]

        for prompt in prompts:
            result = self.runner.invoke(cli, ["prompt", "compress", prompt])
            assert result.exit_code == 0
