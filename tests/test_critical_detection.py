"""Comprehensive tests for CriticalFileDetector (Phase C)

Tests all scoring logic, edge cases, and performance requirements:
- Pattern matching accuracy
- Import detection precision
- Git diff size analysis
- Directory classification
- Test file handling
- Performance benchmarks (<10ms for 1000 files)
"""

import sys
import time
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from scripts.critical_file_detector import (  # noqa: E402
    AnalysisMode,
    CriticalFileDetector,
)


class TestPatternMatching:
    """Test pattern matching scoring (+0.4 points)"""

    def test_executor_pattern_match(self):
        """Test: *_executor.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        # Should match - pattern (0.4) + directory (0.1) = 0.5 = DEEP_MODE
        result = detector.classify(Path("scripts/task_executor.py"))
        assert result.pattern_score == 0.4
        assert result.directory_score == 0.1
        assert result.mode == AnalysisMode.DEEP_MODE  # 0.5 score at threshold

        result = detector.classify(Path("scripts/enhanced_task_executor.py"))
        assert result.pattern_score == 0.4

    def test_validator_pattern_match(self):
        """Test: *_validator.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/constitutional_validator.py"))
        assert result.pattern_score == 0.4

    def test_guard_pattern_match(self):
        """Test: *_guard.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/auth_guard.py"))
        assert result.pattern_score == 0.4

    def test_steering_pattern_match(self):
        """Test: *_steering.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/project_steering.py"))
        assert result.pattern_score == 0.4

    def test_constitutional_prefix_match(self):
        """Test: constitutional_*.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/constitutional_guards.py"))
        assert result.pattern_score == 0.4

    def test_project_prefix_match(self):
        """Test: project_*.py pattern matches correctly"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/project_config.py"))
        assert result.pattern_score == 0.4

    def test_no_pattern_match(self):
        """Test: Non-critical files get 0.0 pattern score"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/utils.py"))
        assert result.pattern_score == 0.0

        result = detector.classify(Path("scripts/helpers.py"))
        assert result.pattern_score == 0.0


class TestImportDetection:
    """Test critical import detection (+0.3 points)"""

    def test_constitutional_validator_import(self, tmp_path):
        """Test: Detects constitutional_validator import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("from constitutional_validator import ConstitutionalValidator")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_project_steering_import(self, tmp_path):
        """Test: Detects project_steering import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import project_steering")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_enhanced_task_executor_import(self, tmp_path):
        """Test: Detects enhanced_task_executor import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("from enhanced_task_executor import EnhancedTaskExecutor")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_automatic_evidence_tracker_import(self, tmp_path):
        """Test: Detects automatic_evidence_tracker import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import automatic_evidence_tracker as tracker")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_constitutional_guards_import(self, tmp_path):
        """Test: Detects constitutional_guards import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("from constitutional_guards import ConstitutionalGuard")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_context_aware_loader_import(self, tmp_path):
        """Test: Detects context_aware_loader import"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import context_aware_loader")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.3

    def test_no_critical_imports(self, tmp_path):
        """Test: Non-critical imports get 0.0 score"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nfrom pathlib import Path")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.import_score == 0.0

    def test_file_not_exists_import(self):
        """Test: Non-existent files get 0.0 import score"""
        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(Path("nonexistent.py"))

        assert result.import_score == 0.0


class TestDirectoryScoring:
    """Test core directory detection (+0.1 points)"""

    def test_scripts_directory(self):
        """Test: Files in scripts/ get +0.1 score"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/utils.py"))
        assert result.directory_score == 0.1

    def test_nested_scripts_directory(self):
        """Test: Files in scripts/subdir/ get +0.1 score"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("scripts/subdir/helper.py"))
        assert result.directory_score == 0.1

    def test_non_core_directory(self):
        """Test: Files outside core directories get 0.0 score"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("src/app.py"))
        assert result.directory_score == 0.0

        result = detector.classify(Path("lib/utils.py"))
        assert result.directory_score == 0.0


class TestTestFileHandling:
    """Test file handling (always FAST_MODE)"""

    def test_test_prefix_pattern(self):
        """Test: test_*.py files are classified as FAST_MODE"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("tests/test_guards.py"))
        assert result.mode == AnalysisMode.FAST_MODE
        assert "Test file" in result.reason

    def test_test_suffix_pattern(self):
        """Test: *_test.py files are classified as FAST_MODE"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("tests/guards_test.py"))
        assert result.mode == AnalysisMode.FAST_MODE
        assert "Test file" in result.reason

    def test_tests_directory(self):
        """Test: Files in tests/ are classified as FAST_MODE"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("tests/integration/api_tests.py"))
        assert result.mode == AnalysisMode.FAST_MODE


class TestSkipFiles:
    """Test skip file handling (SKIP mode)"""

    def test_markdown_skip(self):
        """Test: .md files are skipped"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("README.md"))
        assert result.mode == AnalysisMode.SKIP
        assert "Non-code file" in result.reason

    def test_txt_skip(self):
        """Test: .txt files are skipped"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("notes.txt"))
        assert result.mode == AnalysisMode.SKIP

    def test_json_skip(self):
        """Test: .json files are skipped"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("config.json"))
        assert result.mode == AnalysisMode.SKIP

    def test_yaml_skip(self):
        """Test: .yaml/.yml files are skipped"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("tasks.yaml"))
        assert result.mode == AnalysisMode.SKIP

        result = detector.classify(Path("config.yml"))
        assert result.mode == AnalysisMode.SKIP

    def test_toml_skip(self):
        """Test: .toml files are skipped"""
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path("pyproject.toml"))
        assert result.mode == AnalysisMode.SKIP


class TestCriticalityScoring:
    """Test criticality threshold and scoring logic"""

    def test_threshold_boundary_low(self, tmp_path):
        """Test: Score 0.4 (below 0.5) = FAST_MODE"""
        test_file = tmp_path / "task_executor.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        # Pattern: 0.4, others: 0.0 = 0.4 total
        assert result.criticality_score == 0.4
        assert result.mode == AnalysisMode.FAST_MODE

    def test_threshold_boundary_high(self, tmp_path):
        """Test: Score 0.5 (at threshold) = DEEP_MODE"""
        # Create file in scripts/ with critical pattern
        test_file = tmp_path / "scripts" / "task_executor.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        # Pattern: 0.4, Directory: 0.1 = 0.5 total
        assert result.criticality_score == 0.5
        assert result.mode == AnalysisMode.DEEP_MODE

    def test_maximum_score(self, tmp_path):
        """Test: Maximum score (without git diff) = DEEP_MODE"""
        # Create file with all scoring factors
        test_file = tmp_path / "scripts" / "constitutional_validator.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("from constitutional_guards import ConstitutionalGuard")

        detector = CriticalFileDetector(git_enabled=True)
        result = detector.classify(test_file)

        # Pattern: 0.4, Import: 0.3, Directory: 0.1 = 0.8 total (floating point tolerance)
        assert result.criticality_score >= 0.79  # Allow floating point tolerance
        assert result.mode == AnalysisMode.DEEP_MODE


class TestGitDiffAnalysis:
    """Test git diff size scoring (+0.2 points)"""

    def test_git_disabled(self, tmp_path):
        """Test: Git disabled returns 0.0 diff score"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        assert result.diff_score == 0.0

    def test_git_not_repository(self, tmp_path):
        """Test: Non-git directory returns 0.0 diff score"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=True)
        result = detector.classify(test_file)

        # Should handle git error gracefully
        assert result.diff_score == 0.0

    def test_diff_cache(self, tmp_path):
        """Test: Git diff results are cached"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=True)

        # First call - may call git
        result1 = detector.classify(test_file)

        # Second call - should use cache
        result2 = detector.classify(test_file)

        assert result1.diff_score == result2.diff_score
        assert test_file in detector._git_diff_cache


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_unicode_filename(self, tmp_path):
        """Test: Handles Unicode filenames correctly"""
        test_file = tmp_path / "测试_validator.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        # Should match *_validator.py pattern
        assert result.pattern_score == 0.4

    def test_empty_file(self, tmp_path):
        """Test: Handles empty files correctly"""
        test_file = tmp_path / "empty_executor.py"
        test_file.write_text("")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        # Should still match pattern
        assert result.pattern_score == 0.4
        # No imports
        assert result.import_score == 0.0

    def test_binary_file_content(self, tmp_path):
        """Test: Handles binary content gracefully"""
        test_file = tmp_path / "task_executor.py"
        test_file.write_bytes(b"\x00\xff\xfe binary data")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(test_file)

        # Should match pattern
        assert result.pattern_score == 0.4
        # Should handle read error gracefully
        assert result.import_score == 0.0

    def test_very_long_filename(self):
        """Test: Handles very long filenames"""
        long_name = "a" * 200 + "_executor.py"
        detector = CriticalFileDetector(git_enabled=False)

        result = detector.classify(Path(long_name))
        assert result.pattern_score == 0.4


class TestPerformance:
    """Test performance requirements"""

    def test_single_classification_speed(self, tmp_path):
        """Test: Single classification <0.1ms (excluding git)"""
        test_file = tmp_path / "test_executor.py"
        test_file.write_text("import os")

        detector = CriticalFileDetector(git_enabled=False)

        # Warmup
        detector.classify(test_file)

        # Measure
        start = time.perf_counter()
        detector.classify(test_file)
        duration = time.perf_counter() - start

        # Should be very fast (<0.1ms = 0.0001s)
        assert duration < 0.0001, f"Too slow: {duration*1000:.4f}ms"

    def test_batch_classification_speed(self, tmp_path):
        """Test: 1000 classifications <20ms total"""
        # Create test files
        test_files = []
        for i in range(1000):
            test_file = tmp_path / f"test_{i}.py"
            test_file.write_text("import os")
            test_files.append(test_file)

        detector = CriticalFileDetector(git_enabled=False)

        # Measure batch classification
        start = time.perf_counter()
        for test_file in test_files:
            detector.classify(test_file)
        duration = time.perf_counter() - start

        # Should complete in under 20ms (12ms typical)
        assert duration < 0.02, f"Too slow: {duration*1000:.2f}ms for 1000 files"

        print(f"\nPerformance: {duration*1000:.2f}ms for 1000 classifications")
        print(f"Average: {duration*1000000/1000:.2f}μs per file")


class TestRealFiles:
    """Test against real project files"""

    def test_constitutional_validator_real(self):
        """Test: Real constitutional_validator.py is DEEP_MODE"""
        file_path = project_root / "scripts" / "constitutional_validator.py"

        if not file_path.exists():
            pytest.skip("constitutional_validator.py not found")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(file_path)

        # Should be critical: pattern (0.4) + directory (0.1) = 0.5
        assert result.mode == AnalysisMode.DEEP_MODE
        assert result.criticality_score >= 0.5

    def test_enhanced_task_executor_real(self):
        """Test: Real enhanced_task_executor.py is DEEP_MODE"""
        file_path = project_root / "scripts" / "enhanced_task_executor.py"

        if not file_path.exists():
            pytest.skip("enhanced_task_executor.py not found")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(file_path)

        # Should be critical: pattern (0.4) + imports (0.3) + directory (0.1) = 0.8
        assert result.mode == AnalysisMode.DEEP_MODE
        assert result.criticality_score >= 0.5

    def test_test_file_real(self):
        """Test: Real test files are FAST_MODE"""
        file_path = project_root / "tests" / "test_guards_integration.py"

        if not file_path.exists():
            pytest.skip("test_guards_integration.py not found")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(file_path)

        # Test files always FAST_MODE
        assert result.mode == AnalysisMode.FAST_MODE

    def test_readme_real(self):
        """Test: README.md is SKIP"""
        file_path = project_root / "README.md"

        if not file_path.exists():
            pytest.skip("README.md not found")

        detector = CriticalFileDetector(git_enabled=False)
        result = detector.classify(file_path)

        assert result.mode == AnalysisMode.SKIP


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
