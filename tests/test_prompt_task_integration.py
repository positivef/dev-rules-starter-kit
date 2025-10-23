#!/usr/bin/env python3
"""
Tests for PromptCompressor + TaskExecutor Integration

Purpose: Verify automatic prompt compression in YAML tasks

Constitutional Compliance:
- [P3] Test-First Development
- [P6] Observability
"""

from pathlib import Path
import sys
import json
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_task_integration import (
    extract_prompts,
    apply_compression,
    save_compression_report,
)


class TestPromptExtraction:
    """Test prompt extraction from YAML contracts"""

    def test_extract_simple_prompt(self):
        """Test extraction of single prompt"""
        contract = {
            "commands": [
                {
                    "id": "cmd1",
                    "exec": {"cmd": "python", "args": ["script.py", "--prompt", "Test prompt"]},
                }
            ]
        }

        prompts = extract_prompts(contract)

        assert len(prompts) == 1
        assert prompts[0].command_id == "cmd1"
        assert prompts[0].original_prompt == "Test prompt"
        assert prompts[0].context == "--prompt"
        assert prompts[0].arg_index == 2

    def test_extract_multiple_prompts(self):
        """Test extraction of multiple prompts from different commands"""
        contract = {
            "commands": [
                {"id": "cmd1", "exec": {"args": ["--prompt", "First prompt"]}},
                {"id": "cmd2", "exec": {"args": ["--message", "Second prompt"]}},
                {"id": "cmd3", "exec": {"args": ["-m", "Third prompt"]}},
            ]
        }

        prompts = extract_prompts(contract)

        assert len(prompts) == 3
        assert prompts[0].original_prompt == "First prompt"
        assert prompts[1].original_prompt == "Second prompt"
        assert prompts[2].original_prompt == "Third prompt"

    def test_extract_no_prompts(self):
        """Test contract without prompts"""
        contract = {"commands": [{"id": "cmd1", "exec": {"args": ["script.py", "--output", "file.txt"]}}]}

        prompts = extract_prompts(contract)

        assert len(prompts) == 0

    def test_extract_with_various_flags(self):
        """Test extraction with different prompt flag variations"""
        contract = {
            "commands": [
                {"id": "cmd1", "exec": {"args": ["--text", "Text prompt"]}},
                {"id": "cmd2", "exec": {"args": ["--input", "Input prompt"]}},
                {"id": "cmd3", "exec": {"args": ["--query", "Query prompt"]}},
            ]
        }

        prompts = extract_prompts(contract)

        assert len(prompts) == 3
        contexts = [p.context for p in prompts]
        assert "--text" in contexts
        assert "--input" in contexts
        assert "--query" in contexts

    def test_extract_skips_flag_after_flag(self):
        """Test that extraction skips when flag follows another flag"""
        contract = {"commands": [{"id": "cmd1", "exec": {"args": ["--prompt", "--verbose", "actual prompt"]}}]}

        prompts = extract_prompts(contract)

        # Should skip --verbose and not treat it as a prompt
        assert len(prompts) == 0


class TestCompressionApplication:
    """Test compression application to contracts"""

    def test_apply_compression_enabled(self):
        """Test compression when enabled"""
        contract = {
            "commands": [
                {
                    "id": "cmd1",
                    "exec": {
                        "args": [
                            "script.py",
                            "--prompt",
                            "Please implement the authentication feature for the application",
                        ]
                    },
                }
            ]
        }

        config = {"enabled": True, "compression_level": "medium"}

        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 1
        assert stats[0]["command_id"] == "cmd1"
        assert stats[0]["original_tokens"] > stats[0]["compressed_tokens"]
        assert stats[0]["savings_pct"] > 0

        # Verify contract was actually modified
        compressed_prompt = modified_contract["commands"][0]["exec"]["args"][2]
        original_prompt = "Please implement the authentication feature for the application"
        assert compressed_prompt != original_prompt
        assert len(compressed_prompt) < len(original_prompt)

    def test_apply_compression_disabled(self):
        """Test that compression is skipped when disabled"""
        contract = {"commands": [{"id": "cmd1", "exec": {"args": ["--prompt", "Test prompt"]}}]}

        config = {"enabled": False}

        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 0
        assert modified_contract == contract  # Should be unchanged

    def test_apply_compression_multiple_prompts(self):
        """Test compression of multiple prompts"""
        contract = {
            "commands": [
                {"id": "cmd1", "exec": {"args": ["--prompt", "Please implement authentication feature"]}},
                {"id": "cmd2", "exec": {"args": ["--message", "Please create database schema"]}},
            ]
        }

        config = {"enabled": True, "compression_level": "medium"}

        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 2
        assert all(s["savings_pct"] > 0 for s in stats)

    def test_apply_compression_with_levels(self):
        """Test different compression levels"""
        for level in ["light", "medium", "aggressive"]:
            # Create fresh contract for each level
            contract = {
                "commands": [
                    {
                        "id": "cmd1",
                        "exec": {"args": ["--prompt", "Please implement the authentication feature for the application"]},
                    }
                ]
            }

            config = {"enabled": True, "compression_level": level}
            modified_contract, stats = apply_compression(contract, config)

            assert len(stats) == 1
            assert stats[0]["savings_pct"] > 0

    def test_backward_compatibility(self):
        """Test that contracts without prompt_optimization work unchanged"""
        contract = {"commands": [{"id": "cmd1", "exec": {"args": ["script.py"]}}]}

        config = {}  # No prompt_optimization section

        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 0
        assert modified_contract == contract


class TestCompressionReportSaving:
    """Test compression report generation"""

    def test_save_compression_report(self):
        """Test that compression report is saved correctly"""
        stats = [
            {
                "command_id": "cmd1",
                "context": "--prompt",
                "original_tokens": 20,
                "compressed_tokens": 12,
                "savings_pct": 40.0,
                "rules_applied": 3,
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = f"{tmpdir}/RUNS/{{task_id}}/compression_report.json"
            task_id = "TEST-2025-10-24-01"

            save_compression_report(stats, report_path, task_id)

            # Verify file exists
            actual_path = Path(tmpdir) / "RUNS" / task_id / "compression_report.json"
            assert actual_path.exists()

            # Verify content
            with open(actual_path, "r", encoding="utf-8") as f:
                report = json.load(f)

            assert report["task_id"] == task_id
            assert report["summary"]["prompts_compressed"] == 1
            assert report["summary"]["total_original_tokens"] == 20
            assert report["summary"]["total_compressed_tokens"] == 12
            assert report["summary"]["total_tokens_saved"] == 8
            assert report["summary"]["average_savings_pct"] == 40.0
            assert len(report["details"]) == 1

    def test_save_report_creates_directory(self):
        """Test that report directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = f"{tmpdir}/nested/path/RUNS/{{task_id}}/report.json"
            task_id = "TEST-01"
            stats = [{"command_id": "cmd1", "original_tokens": 10, "compressed_tokens": 5, "savings_pct": 50.0}]

            save_compression_report(stats, report_path, task_id)

            actual_path = Path(tmpdir) / "nested" / "path" / "RUNS" / task_id / "report.json"
            assert actual_path.exists()


class TestIntegration:
    """Integration tests for full workflow"""

    def test_full_compression_workflow(self):
        """Test complete workflow: extract -> compress -> save"""
        contract = {
            "task_id": "FEAT-2025-10-24-01",
            "commands": [
                {
                    "id": "generate-docs",
                    "exec": {
                        "args": [
                            "python",
                            "generator.py",
                            "--prompt",
                            "Please create comprehensive documentation for the authentication system",
                        ]
                    },
                }
            ],
            "prompt_optimization": {"enabled": True, "compression_level": "medium"},
        }

        # Step 1: Extract prompts
        prompts = extract_prompts(contract)
        assert len(prompts) == 1

        # Step 2: Apply compression
        config = contract["prompt_optimization"]
        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 1
        assert stats[0]["savings_pct"] > 0

        # Step 3: Save report
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = f"{tmpdir}/compression_report.json"
            save_compression_report(stats, report_path, contract["task_id"])

            assert Path(tmpdir, "compression_report.json").exists()

    def test_no_prompts_workflow(self):
        """Test workflow when no prompts are present"""
        contract = {
            "commands": [{"id": "cmd1", "exec": {"args": ["python", "script.py", "--output", "file.txt"]}}],
            "prompt_optimization": {"enabled": True},
        }

        prompts = extract_prompts(contract)
        assert len(prompts) == 0

        config = contract["prompt_optimization"]
        modified_contract, stats = apply_compression(contract, config)

        assert len(stats) == 0
        assert modified_contract == contract

    def test_compression_preserves_other_args(self):
        """Test that compression only modifies prompt args, not other args"""
        contract = {
            "commands": [
                {
                    "id": "cmd1",
                    "exec": {
                        "args": [
                            "python",
                            "script.py",
                            "--output",
                            "file.txt",
                            "--prompt",
                            "Please implement feature",
                            "--verbose",
                        ]
                    },
                }
            ]
        }

        config = {"enabled": True, "compression_level": "medium"}

        modified_contract, stats = apply_compression(contract, config)

        args = modified_contract["commands"][0]["exec"]["args"]

        # Verify other args are unchanged
        assert args[0] == "python"
        assert args[1] == "script.py"
        assert args[2] == "--output"
        assert args[3] == "file.txt"
        assert args[4] == "--prompt"
        # args[5] should be compressed prompt
        assert args[6] == "--verbose"
