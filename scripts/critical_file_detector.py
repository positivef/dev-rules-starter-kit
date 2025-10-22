"""Critical File Detector for Development Assistant Phase C

Implements smart detection to classify files as FAST_MODE or DEEP_MODE:
- FAST_MODE: <200ms, Ruff static analysis only
- DEEP_MODE: 2-5s, Full MCP analysis with semantic understanding

Criticality scoring system (0.0-1.0):
- Pattern match (*_executor.py, *_validator.py): +0.4
- Critical import (constitutional_validator, etc.): +0.3
- Large change (>100 lines in git diff): +0.2
- Core directory (scripts/, not tests/): +0.1
- Threshold: >=0.5 → DEEP_MODE

Performance: <0.01ms per classification (excluding git diff)
"""

import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Set


class AnalysisMode(Enum):
    """Analysis mode classification"""

    FAST_MODE = "fast"  # <200ms, Ruff only
    DEEP_MODE = "deep"  # 2-5s, MCP analysis
    SKIP = "skip"  # No analysis needed


@dataclass
class FileClassification:
    """Result of file criticality classification

    Attributes:
        file_path: Path to the analyzed file
        mode: Recommended analysis mode (FAST/DEEP/SKIP)
        criticality_score: Final score (0.0-1.0)
        pattern_score: Score from filename pattern matching
        import_score: Score from critical import detection
        diff_score: Score from git diff size
        directory_score: Score from directory location
        reason: Human-readable explanation
    """

    file_path: Path
    mode: AnalysisMode
    criticality_score: float
    pattern_score: float
    import_score: float
    diff_score: float
    directory_score: float
    reason: str

    def __str__(self) -> str:
        """Format classification result for display"""
        return f"{self.file_path.name}: {self.mode.value.upper()} " f"(score={self.criticality_score:.2f}) - {self.reason}"


class CriticalFileDetector:
    """Detects critical files requiring deep MCP analysis

    Implements a scoring system to classify files into analysis modes:
    - FAST_MODE: Simple changes, Ruff static analysis only
    - DEEP_MODE: Critical files, full MCP semantic analysis
    - SKIP: Config files, documentation, etc.

    Performance optimized: <0.01ms per classification (cached git diffs)
    """

    # Pattern matching: +0.4 points
    CRITICAL_PATTERNS: Set[str] = {
        "*_executor.py",
        "*_validator.py",
        "*_guard.py",
        "*_steering.py",
        "constitutional_*.py",
        "project_*.py",
    }

    # Import detection: +0.3 points
    CRITICAL_IMPORTS: Set[str] = {
        "constitutional_validator",
        "project_steering",
        "enhanced_task_executor",
        "automatic_evidence_tracker",
        "constitutional_guards",
        "context_aware_loader",
    }

    # Test file patterns (always FAST_MODE)
    TEST_PATTERNS: Set[str] = {"*_test.py", "test_*.py"}

    # Skip file extensions
    SKIP_EXTENSIONS: Set[str] = {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}

    # Core directories: +0.1 points
    CORE_DIRECTORIES: Set[str] = {"scripts"}

    # Git diff threshold: >100 lines → +0.2 points
    LARGE_CHANGE_THRESHOLD: int = 100

    # Criticality threshold: >=0.5 → DEEP_MODE
    CRITICALITY_THRESHOLD: float = 0.5

    def __init__(self, git_enabled: bool = True):
        """Initialize detector

        Args:
            git_enabled: Enable git diff analysis (disable for testing)
        """
        self.git_enabled = git_enabled
        self._git_diff_cache: dict[Path, int] = {}

    def classify(self, file_path: Path) -> FileClassification:
        """Classify file criticality and determine analysis mode

        Args:
            file_path: Path to file to classify

        Returns:
            FileClassification with mode and scoring breakdown

        Performance: <0.01ms (excluding git diff subprocess call)
        """
        # Guard clause: Skip non-Python files
        if file_path.suffix in self.SKIP_EXTENSIONS:
            return self._create_skip_classification(file_path, "Non-code file (docs/config)")

        # Guard clause: Test files always use FAST_MODE
        if self._is_test_file(file_path):
            return self._create_fast_classification(file_path, scores={}, reason="Test file (fast validation only)")

        # Calculate criticality scores
        pattern_score = self._check_pattern_match(file_path)
        import_score = self._check_critical_imports(file_path)
        diff_score = self._check_git_diff_size(file_path)
        directory_score = self._check_core_directory(file_path)

        # Aggregate scores
        total_score = self._calculate_criticality(pattern_score, import_score, diff_score, directory_score)

        scores = {
            "pattern_score": pattern_score,
            "import_score": import_score,
            "diff_score": diff_score,
            "directory_score": directory_score,
        }

        # Determine mode based on threshold
        if total_score >= self.CRITICALITY_THRESHOLD:
            return self._create_deep_classification(file_path, scores, total_score)
        else:
            return self._create_fast_classification(file_path, scores)

    def _check_pattern_match(self, file_path: Path) -> float:
        """Check if filename matches critical patterns

        Args:
            file_path: Path to check

        Returns:
            0.4 if matches critical pattern, 0.0 otherwise
        """
        filename = file_path.name

        for pattern in self.CRITICAL_PATTERNS:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace(".py", r"\.py")
            if re.match(regex_pattern, filename):
                return 0.4

        return 0.0

    def _check_critical_imports(self, file_path: Path) -> float:
        """Check for critical module imports in file

        Args:
            file_path: Path to check

        Returns:
            0.3 if contains critical imports, 0.0 otherwise
        """
        if not file_path.exists():
            return 0.0

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for any critical imports
            for import_name in self.CRITICAL_IMPORTS:
                # Match: from X import Y, import X, import X as Y
                import_patterns = [
                    rf"from\s+{import_name}\s+import",
                    rf"import\s+{import_name}(?:\s+as|\s*,|\s*$)",
                ]

                for pattern in import_patterns:
                    if re.search(pattern, content):
                        return 0.3

        except (OSError, UnicodeDecodeError):
            # File read error, skip import analysis
            pass

        return 0.0

    def _check_git_diff_size(self, file_path: Path) -> float:
        """Check git diff size for file changes

        Args:
            file_path: Path to check

        Returns:
            0.2 if >100 lines changed, 0.0 otherwise

        Performance: <50ms (subprocess call, cached)
        """
        if not self.git_enabled:
            return 0.0

        # Check cache
        if file_path in self._git_diff_cache:
            lines_changed = self._git_diff_cache[file_path]
            return 0.2 if lines_changed > self.LARGE_CHANGE_THRESHOLD else 0.0

        # Run git diff
        try:
            result = subprocess.run(
                ["git", "diff", "--numstat", "HEAD", str(file_path)],
                capture_output=True,
                text=True,
                timeout=1.0,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse: "added\tdeleted\tfilename"
                parts = result.stdout.strip().split("\t")
                if len(parts) >= 2:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    deleted = int(parts[1]) if parts[1] != "-" else 0
                    total_changes = added + deleted

                    # Cache result
                    self._git_diff_cache[file_path] = total_changes

                    return 0.2 if total_changes > self.LARGE_CHANGE_THRESHOLD else 0.0

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
            # Git not available or error - skip diff analysis
            pass

        # Cache zero result
        self._git_diff_cache[file_path] = 0
        return 0.0

    def _check_core_directory(self, file_path: Path) -> float:
        """Check if file is in core directory

        Args:
            file_path: Path to check

        Returns:
            0.1 if in core directory (scripts/), 0.0 otherwise
        """
        # Check if any parent directory matches core directories
        for parent in file_path.parents:
            if parent.name in self.CORE_DIRECTORIES:
                return 0.1

        return 0.0

    def _calculate_criticality(
        self,
        pattern_score: float,
        import_score: float,
        diff_score: float,
        directory_score: float,
    ) -> float:
        """Calculate final criticality score

        Args:
            pattern_score: Score from pattern matching (0.0-0.4)
            import_score: Score from import detection (0.0-0.3)
            diff_score: Score from git diff size (0.0-0.2)
            directory_score: Score from directory location (0.0-0.1)

        Returns:
            Total criticality score (0.0-1.0)
        """
        return pattern_score + import_score + diff_score + directory_score

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file

        Args:
            file_path: Path to check

        Returns:
            True if test file, False otherwise
        """
        filename = file_path.name

        # Check test patterns
        for pattern in self.TEST_PATTERNS:
            regex_pattern = pattern.replace("*", ".*").replace(".py", r"\.py")
            if re.match(regex_pattern, filename):
                return True

        # Check if in tests/ directory
        for parent in file_path.parents:
            if parent.name == "tests":
                return True

        return False

    def _create_deep_classification(
        self, file_path: Path, scores: dict[str, float], total_score: float
    ) -> FileClassification:
        """Create DEEP_MODE classification

        Args:
            file_path: Path to file
            scores: Score breakdown
            total_score: Final criticality score

        Returns:
            FileClassification for DEEP_MODE
        """
        reasons = []
        if scores["pattern_score"] > 0:
            reasons.append("critical pattern")
        if scores["import_score"] > 0:
            reasons.append("critical imports")
        if scores["diff_score"] > 0:
            reasons.append("large changes")
        if scores["directory_score"] > 0:
            reasons.append("core directory")

        reason = f"Critical file ({', '.join(reasons)})"

        return FileClassification(
            file_path=file_path,
            mode=AnalysisMode.DEEP_MODE,
            criticality_score=total_score,
            pattern_score=scores["pattern_score"],
            import_score=scores["import_score"],
            diff_score=scores["diff_score"],
            directory_score=scores["directory_score"],
            reason=reason,
        )

    def _create_fast_classification(
        self, file_path: Path, scores: dict[str, float], reason: Optional[str] = None
    ) -> FileClassification:
        """Create FAST_MODE classification

        Args:
            file_path: Path to file
            scores: Score breakdown
            reason: Optional custom reason

        Returns:
            FileClassification for FAST_MODE
        """
        total_score = sum(scores.values()) if scores else 0.0
        default_reason = "Standard file (fast analysis sufficient)"

        return FileClassification(
            file_path=file_path,
            mode=AnalysisMode.FAST_MODE,
            criticality_score=total_score,
            pattern_score=scores.get("pattern_score", 0.0),
            import_score=scores.get("import_score", 0.0),
            diff_score=scores.get("diff_score", 0.0),
            directory_score=scores.get("directory_score", 0.0),
            reason=reason or default_reason,
        )

    def _create_skip_classification(self, file_path: Path, reason: str) -> FileClassification:
        """Create SKIP classification

        Args:
            file_path: Path to file
            reason: Reason for skipping

        Returns:
            FileClassification for SKIP
        """
        return FileClassification(
            file_path=file_path,
            mode=AnalysisMode.SKIP,
            criticality_score=0.0,
            pattern_score=0.0,
            import_score=0.0,
            diff_score=0.0,
            directory_score=0.0,
            reason=reason,
        )


def main():
    """CLI entry point for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python critical_file_detector.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    detector = CriticalFileDetector()

    classification = detector.classify(file_path)
    print(classification)
    print("\nScore breakdown:")
    print(f"  Pattern:   {classification.pattern_score:.2f}")
    print(f"  Imports:   {classification.import_score:.2f}")
    print(f"  Diff size: {classification.diff_score:.2f}")
    print(f"  Directory: {classification.directory_score:.2f}")
    print(f"  TOTAL:     {classification.criticality_score:.2f}")


if __name__ == "__main__":
    main()
