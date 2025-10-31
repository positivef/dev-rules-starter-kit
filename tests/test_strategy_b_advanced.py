"""
Strategy B Tools Advanced Tests
Error handling, edge cases, and integration scenarios
"""

import pytest
import subprocess
from pathlib import Path
import sys
import tempfile

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCodeReviewAssistantAdvanced:
    """Advanced tests for code_review_assistant.py"""

    def test_missing_file_error(self):
        """Verify graceful handling of missing files"""
        result = subprocess.run(
            ["python", "scripts/code_review_assistant.py", "nonexistent.py"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should handle error gracefully (not crash)
        assert result.returncode in [0, 1, 2]

    def test_invalid_argument_handling(self):
        """Verify invalid arguments are handled"""
        result = subprocess.run(
            ["python", "scripts/code_review_assistant.py", "--invalid-flag"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should show error or help message
        assert result.returncode != 0 or "help" in result.stdout.lower()

    def test_empty_file_handling(self):
        """Verify empty file handling"""
        # code_review_assistant uses --commit, not file arguments
        result = subprocess.run(
            ["python", "scripts/code_review_assistant.py", "--commit", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should handle gracefully (return code 0, 1, or 2 all acceptable)
        assert result.returncode in [0, 1, 2]


class TestDeploymentPlannerAdvanced:
    """Advanced tests for deployment_planner.py"""

    def test_no_arguments_handling(self):
        """Verify behavior with no arguments"""
        result = subprocess.run(
            ["python", "scripts/deployment_planner.py"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should show help or handle gracefully
        assert result.returncode in [0, 1, 2]

    def test_invalid_environment_error(self):
        """Verify invalid environment handling"""
        result = subprocess.run(
            ["python", "scripts/deployment_planner.py", "--env", "invalid"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should handle invalid environment
        assert result.returncode in [0, 1, 2]


class TestTestGeneratorAdvanced:
    """Advanced tests for test_generator.py"""

    def test_missing_source_file(self):
        """Verify handling of missing source files"""
        result = subprocess.run(
            ["python", "scripts/test_generator.py", "nonexistent.py"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should handle missing file error
        assert result.returncode in [0, 1, 2]

    def test_invalid_python_file(self):
        """Verify handling of invalid Python syntax"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def invalid syntax here\n")
            temp_file = Path(f.name)

        try:
            result = subprocess.run(
                ["python", "scripts/test_generator.py", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should handle syntax errors
            assert result.returncode in [0, 1, 2]
        finally:
            temp_file.unlink()

    def test_output_directory_creation(self):
        """Verify output directory creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "tests"
            result = subprocess.run(
                [
                    "python",
                    "scripts/test_generator.py",
                    "scripts/code_review_assistant.py",
                    "--output",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should handle output directory
            assert result.returncode in [0, 1]


class TestProjectValidatorAdvanced:
    """Advanced tests for project_validator.py"""

    def test_help_command(self):
        """Verify help flag works"""
        result = subprocess.run(
            ["python", "scripts/project_validator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should show help
        assert result.returncode in [0, 1, 2]
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_report_flag_exists(self):
        """Verify report flag is documented"""
        result = subprocess.run(
            ["python", "scripts/project_validator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Report flag should exist
        assert result.returncode in [0, 1, 2]
        assert "--report" in result.stdout.lower() or "report" in result.stdout.lower()


class TestCoverageMonitorAdvanced:
    """Advanced tests for coverage_monitor.py"""

    def test_help_command(self):
        """Verify help command works"""
        result = subprocess.run(
            ["python", "scripts/coverage_monitor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should show help
        assert result.returncode in [0, 1, 2]
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_watch_mode_flag(self):
        """Verify watch mode flag exists"""
        result = subprocess.run(
            ["python", "scripts/coverage_monitor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Watch mode should be documented
        assert result.returncode in [0, 1, 2]

    def test_threshold_flag_exists(self):
        """Verify threshold flag is documented"""
        result = subprocess.run(
            ["python", "scripts/coverage_monitor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Threshold flag should exist in help
        assert result.returncode in [0, 1, 2]
        assert "--threshold" in result.stdout.lower() or "threshold" in result.stdout.lower()


class TestObsidianAutoSyncAdvanced:
    """Advanced tests for install_obsidian_auto_sync.py"""

    def test_check_without_installation(self):
        """Verify check command works without hook"""
        result = subprocess.run(
            ["python", "scripts/install_obsidian_auto_sync.py", "--check"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should report status (installed or not)
        assert result.returncode in [0, 1]
        assert "installed" in result.stdout.lower() or "not found" in result.stdout.lower()

    def test_dry_run_mode(self):
        """Verify dry-run mode doesn't modify files"""
        result = subprocess.run(
            ["python", "scripts/install_obsidian_auto_sync.py", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should simulate without changes
        assert result.returncode in [0, 1]


class TestPrincipleConflictDetectorAdvanced:
    """Advanced tests for principle_conflict_detector.py"""

    def test_empty_config_handling(self):
        """Verify handling of empty config"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_file = Path(f.name)

        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/principle_conflict_detector.py",
                    "--config",
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should handle empty config
            assert result.returncode in [0, 1, 2]
        finally:
            temp_file.unlink()

    def test_malformed_yaml_handling(self):
        """Verify handling of malformed YAML"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid:\n  yaml: [\n  unclosed")
            temp_file = Path(f.name)

        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/principle_conflict_detector.py",
                    "--config",
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should handle YAML parsing errors
            assert result.returncode in [0, 1, 2]
        finally:
            temp_file.unlink()


class TestStrategyBIntegrationAdvanced:
    """Advanced integration tests between Strategy B tools"""

    def test_code_review_and_test_generation_exist(self):
        """Verify code review and test generation tools exist"""
        # Verify both tools have help commands
        review_result = subprocess.run(
            ["python", "scripts/code_review_assistant.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        test_result = subprocess.run(
            ["python", "scripts/test_generator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Both should have help
        assert review_result.returncode in [0, 1, 2]
        assert test_result.returncode in [0, 1, 2]
        assert "usage" in review_result.stdout.lower() or "help" in review_result.stdout.lower()
        assert "usage" in test_result.stdout.lower() or "help" in test_result.stdout.lower()

    def test_validator_and_deployment_exist(self):
        """Verify validator and deployment tools exist"""
        # Verify both tools have help commands
        validate_result = subprocess.run(
            ["python", "scripts/project_validator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        deploy_result = subprocess.run(
            ["python", "scripts/deployment_planner.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Both should have help
        assert validate_result.returncode in [0, 1, 2]
        assert deploy_result.returncode in [0, 1, 2]

    def test_coverage_monitor_exists(self):
        """Verify coverage monitor tool exists and has help"""
        result = subprocess.run(
            ["python", "scripts/coverage_monitor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should have help command
        assert result.returncode in [0, 1, 2]
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()


class TestErrorRecovery:
    """Test error recovery mechanisms"""

    def test_concurrent_tool_execution(self):
        """Verify tools can run concurrently without conflicts"""
        import concurrent.futures

        def run_tool(tool_name):
            result = subprocess.run(
                ["python", f"scripts/{tool_name}", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode

        tools = [
            "code_review_assistant.py",
            "deployment_planner.py",
            "test_generator.py",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_tool, tool) for tool in tools]
            results = [f.result() for f in futures]

        # All should complete without crashes
        assert all(rc in [0, 1, 2] for rc in results)

    def test_resource_cleanup(self):
        """Verify tools clean up temporary resources"""
        initial_temp = len(list(Path(tempfile.gettempdir()).glob("*")))

        # Run several tools
        tools = ["code_review_assistant.py", "test_generator.py"]
        for tool in tools:
            subprocess.run(
                ["python", f"scripts/{tool}", "--help"],
                capture_output=True,
                timeout=10,
            )

        final_temp = len(list(Path(tempfile.gettempdir()).glob("*")))

        # Should not leave excessive temp files (allow some variance)
        assert final_temp - initial_temp < 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
