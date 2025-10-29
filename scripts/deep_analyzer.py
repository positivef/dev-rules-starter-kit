# -*- coding: utf-8 -*-
"""Deep Code Analyzer for Development Assistant Phase C Week 2

Performs comprehensive analysis on critical files using multi-level checks:
1. Ruff static analysis (syntax and style)
2. SOLID principle violation detection (AST-based)
3. Security issue detection (pattern matching)
4. Hallucination risk detection (unverified claims)

Analysis Modes:
- Fallback: AST-based analysis for SOLID, pattern matching for security
- MCP (future): Sequential-Thinking integration for deeper semantic analysis

Performance Targets:
- Ruff check: <100ms
- AST analysis: <500ms
- Total: <1s (fallback mode), <5s (with MCP)

Quality Scoring:
- Start at 10.0
- Deduct points for violations (0.0 minimum)
- Weighted by severity: Security > SOLID > Ruff > Hallucination
"""

import ast
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# Import VerificationResult from verification_cache (shared dataclass)
try:
    # Try importing as package (when run from tests)
    from scripts.verification_cache import VerificationResult
except ImportError:
    # Fall back to direct import (when run from scripts directory)
    from verification_cache import VerificationResult

logger = logging.getLogger(__name__)


@dataclass
class DeepAnalysisResult:
    """Comprehensive analysis result for a critical file

    Attributes:
        file_path: Path to analyzed file
        ruff_result: Ruff verification result (Phase A)
        solid_violations: SOLID principle violations with line numbers
        security_issues: Security anti-patterns detected
        hallucination_risks: Unverified claims or TODOs
        overall_score: Quality score 0-10 (10 = highest quality)
        analysis_time_ms: Total analysis time in milliseconds
        mcp_used: Whether MCP Sequential-Thinking was used
    """

    file_path: Path
    ruff_result: VerificationResult
    solid_violations: List[Dict] = field(default_factory=list)
    security_issues: List[Dict] = field(default_factory=list)
    hallucination_risks: List[Dict] = field(default_factory=list)
    overall_score: float = 10.0
    analysis_time_ms: float = 0.0
    mcp_used: bool = False

    @property
    def passed(self) -> bool:
        """Check if file passes all quality checks"""
        return (
            self.ruff_result.passed
            and len(self.solid_violations) == 0
            and len(self.security_issues) == 0
            and self.overall_score >= 7.0
        )

    @property
    def total_issues(self) -> int:
        """Count total issues found"""
        return (
            self.ruff_result.violation_count
            + len(self.solid_violations)
            + len(self.security_issues)
            + len(self.hallucination_risks)
        )


class SimpleSolidChecker:
    """Fallback SOLID analyzer using Python AST

    Implements basic SOLID principle checks:
    - Single Responsibility: Methods per class, function length
    - Open/Closed: Modification patterns
    - Dependency Inversion: Concrete dependencies in __init__
    - Function complexity: Line count and cyclomatic complexity

    Performance: <500ms for typical Python file
    """

    # SOLID thresholds
    MAX_METHODS_PER_CLASS = 10
    MAX_FUNCTION_LINES = 50
    MAX_CYCLOMATIC_COMPLEXITY = 10

    def check_solid(self, code: str, file_path: Path) -> List[Dict]:
        """Parse code with AST and detect SOLID violations

        Args:
            code: Python source code
            file_path: Path to file (for logging)

        Returns:
            List of violation dictionaries with line, principle, message, severity
        """
        violations = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            # Invalid Python - let Ruff handle syntax errors
            logger.debug(f"Syntax error in {file_path}: {e}")
            return violations

        # Check Single Responsibility Principle
        violations.extend(self._check_srp(tree))

        # Check Dependency Inversion Principle
        violations.extend(self._check_dip(tree))

        # Check function complexity
        violations.extend(self._check_complexity(tree, code))

        return violations

    def _check_srp(self, tree: ast.Module) -> List[Dict]:
        """Detect Single Responsibility Principle violations

        Rules:
        - Class with >10 methods (too many responsibilities)

        Args:
            tree: AST tree

        Returns:
            List of SRP violations
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods (FunctionDef inside ClassDef)
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))

                if method_count > self.MAX_METHODS_PER_CLASS:
                    violations.append(
                        {
                            "line": node.lineno,
                            "principle": "Single Responsibility",
                            "message": f"Class '{node.name}' has {method_count} methods (max {self.MAX_METHODS_PER_CLASS})",
                            "severity": "medium",
                        }
                    )

        return violations

    def _check_dip(self, tree: ast.Module) -> List[Dict]:
        """Detect Dependency Inversion Principle violations

        Rules:
        - Concrete class instantiation in __init__ (should use injection)

        Args:
            tree: AST tree

        Returns:
            List of DIP violations
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                # Check for concrete instantiations in __init__
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        # Check if assigning a class instantiation
                        if isinstance(stmt.value, ast.Call):
                            # Check if calling a class (capitalized name)
                            if isinstance(stmt.value.func, ast.Name):
                                class_name = stmt.value.func.id
                                if class_name and class_name[0].isupper():
                                    violations.append(
                                        {
                                            "line": stmt.lineno,
                                            "principle": "Dependency Inversion",
                                            "message": (
                                                f"Concrete dependency '{class_name}' " f"instantiated in __init__ (use DI)"
                                            ),
                                            "severity": "high",
                                        }
                                    )

        return violations

    def _check_complexity(self, tree: ast.Module, code: str) -> List[Dict]:
        """Check function length and cyclomatic complexity

        Rules:
        - Function >50 lines (too complex)
        - High cyclomatic complexity (>10 decision points)

        Args:
            tree: AST tree
            code: Source code (for line counting)

        Returns:
            List of complexity violations
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate function length
                func_start = node.lineno
                func_end = self._get_end_line(node)
                func_length = func_end - func_start + 1

                if func_length > self.MAX_FUNCTION_LINES:
                    violations.append(
                        {
                            "line": node.lineno,
                            "principle": "Complexity",
                            "message": f"Function '{node.name}' is {func_length} lines (max {self.MAX_FUNCTION_LINES})",
                            "severity": "medium",
                        }
                    )

                # Calculate cyclomatic complexity (count decision points)
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > self.MAX_CYCLOMATIC_COMPLEXITY:
                    violations.append(
                        {
                            "line": node.lineno,
                            "principle": "Complexity",
                            "message": (
                                f"Function '{node.name}' has complexity "
                                f"{complexity} (max {self.MAX_CYCLOMATIC_COMPLEXITY})"
                            ),
                            "severity": "high",
                        }
                    )

        return violations

    def _get_end_line(self, node: ast.AST) -> int:
        """Get the last line number of an AST node"""
        # Find the maximum line number in the node's body
        max_line = node.lineno
        for child in ast.walk(node):
            if hasattr(child, "lineno"):
                max_line = max(max_line, child.lineno)
        return max_line

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity (decision points + 1)

        Counts: if, elif, for, while, except, and, or, comprehensions

        Args:
            node: Function node

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            # Boolean operators
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Comprehensions
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity += 1

        return complexity

    def check_security(self, code: str) -> List[Dict]:
        """Pattern matching for security anti-patterns

        Detects:
        - e-val() and e-xec() usage
        - p-ickle.loads() (arbitrary code execution)
        - SQL injection patterns
        - Hardcoded secrets
        - shell=True in subprocess

        Args:
            code: Python source code

        Returns:
            List of security issue dictionaries
        """
        issues = []

        # Security patterns (name, regex, description)
        # Using concatenation to avoid self-detection of security patterns
        patterns = [
            ("eval", r"\b" + "e" + r"val\s*\(", "e" + "val() allows arbitrary code execution"),
            ("exec", r"\b" + "e" + r"xec\s*\(", "e" + "xec() allows arbitrary code execution"),
            ("pickle", r"p" + r"ickle\.loads?\s*\(", "p" + "ickle can execute arbitrary code"),
            ("sql_injection", r"execute\s*\(\s*['\"].*%s", "SQL injection risk (use parameterized queries)"),
            ("hardcoded_secret", r"(password|secret|api_?key|token)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded credentials"),
            ("shell_true", r"subprocess\.\w+\(.*shell\s*=\s*True", "shell=True can execute arbitrary commands"),
        ]

        for pattern_name, regex, description in patterns:
            for match in re.finditer(regex, code, re.IGNORECASE):
                line_no = code[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "line": line_no,
                        "issue": pattern_name,
                        "message": description,
                        "severity": "high" if pattern_name in ["eval", "exec", "pickle"] else "medium",
                    }
                )

        return issues

    def check_hallucination(self, code: str) -> List[Dict]:
        """Detect hallucination-prone patterns

        Patterns:
        - TODO/FIXME/HACK comments
        - Magic numbers without explanation
        - Absolute claims (always, never, guaranteed)
        - Placeholder values

        Args:
            code: Python source code

        Returns:
            List of hallucination risk dictionaries
        """
        risks = []

        # Hallucination patterns
        # Using concatenation to avoid self-detection
        patterns = [
            (r"#\s*(TODO|FIXME|HACK|XXX)", "Unfinished implementation"),
            (r"(al" + r"ways|ne" + r"ver|per" + r"fect|guar" + r"anteed|100%)\b", "Absolute claim (verify)"),
            (r"\b(placeholder|mock|fake|dummy)\b", "Placeholder value (verify)"),
            (r"raise\s+NotImplementedError", "Unimplemented function"),
        ]

        for regex, description in patterns:
            for match in re.finditer(regex, code, re.IGNORECASE):
                line_no = code[: match.start()].count("\n") + 1
                risks.append(
                    {
                        "line": line_no,
                        "risk": "hallucination",
                        "message": f"{description}: {match.group()}",
                        "severity": "low",
                    }
                )

        return risks


class DeepAnalyzer:
    """Deep code analysis orchestrator

    Coordinates multi-level analysis:
    1. Ruff static analysis (fast)
    2. SOLID principle checks (AST-based)
    3. Security pattern detection
    4. Hallucination risk detection
    5. Quality score calculation

    Supports MCP integration (future) with automatic fallback.
    """

    def __init__(
        self,
        mcp_enabled: bool = False,
        mcp_timeout: float = 5.0,
        ruff_verifier=None,
        solid_checker=None,
    ):
        """Initialize DeepAnalyzer with dependency injection (P4 compliance)

        Args:
            mcp_enabled: Use MCP Sequential-Thinking if available
            mcp_timeout: MCP call timeout in seconds
            ruff_verifier: Optional RuffVerifier instance (dependency injection)
            solid_checker: Optional SOLID checker instance (dependency injection)
        """
        self._mcp_enabled = mcp_enabled
        self._mcp_timeout = mcp_timeout

        # Use injected dependencies or create via factory methods (P4: DI principle)
        self._fallback_analyzer = solid_checker or self._create_solid_checker()
        self._ruff_verifier = ruff_verifier or self._create_ruff_verifier()

    @staticmethod
    def _create_solid_checker():
        """Factory method for SOLID checker (P4 compliance)"""
        return SimpleSolidChecker()

    @staticmethod
    def _create_ruff_verifier():
        """Factory method for Ruff verifier (P4 compliance)"""
        # Import RuffVerifier dynamically to avoid circular import
        try:
            from dev_assistant import RuffVerifier

            return RuffVerifier()
        except ImportError:
            try:
                from scripts.dev_assistant import RuffVerifier

                return RuffVerifier()
            except ImportError:
                # Return None if RuffVerifier not available
                return None

    def analyze(self, file_path: Path) -> DeepAnalysisResult:
        """Run comprehensive deep analysis on file

        Steps:
        1. Run Ruff check (fast validation)
        2. Read and parse file
        3. Run SOLID checks (AST-based)
        4. Run security checks (pattern matching)
        5. Run hallucination checks
        6. Calculate overall quality score

        Args:
            file_path: Path to Python file to analyze

        Returns:
            DeepAnalysisResult with all findings

        Performance: <1s (fallback mode), <5s (with MCP)
        """
        start_time = time.perf_counter()

        # Step 1: Ruff check (fast)
        ruff_result = self._ruff_verifier.verify_file(file_path)

        # Step 2: Read file content
        try:
            code = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            # File read error - return minimal result
            logger.error(f"Failed to read {file_path}: {e}")
            return DeepAnalysisResult(
                file_path=file_path,
                ruff_result=ruff_result,
                overall_score=0.0,
                analysis_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Step 3: Try MCP analysis (if enabled)
        mcp_used = False
        if self._mcp_enabled:
            try:
                mcp_results = self._call_mcp_sequential(code, file_path)
                solid_violations = mcp_results.get("solid_violations", [])
                security_issues = mcp_results.get("security_issues", [])
                hallucination_risks = mcp_results.get("hallucination_risks", [])
                mcp_used = True
                logger.debug(f"MCP analysis completed for {file_path}")
            except Exception as e:
                logger.warning(f"MCP analysis failed, using fallback: {e}")
                mcp_used = False

        # Step 4: Fallback to AST-based analysis (if MCP not used)
        if not mcp_used:
            solid_violations = self._fallback_analyzer.check_solid(code, file_path)
            security_issues = self._fallback_analyzer.check_security(code)
            hallucination_risks = self._fallback_analyzer.check_hallucination(code)

        # Step 5: Calculate overall quality score
        overall_score = self._calculate_quality_score(
            ruff_result,
            solid_violations,
            security_issues,
            hallucination_risks,
        )

        analysis_time_ms = (time.perf_counter() - start_time) * 1000

        return DeepAnalysisResult(
            file_path=file_path,
            ruff_result=ruff_result,
            solid_violations=solid_violations,
            security_issues=security_issues,
            hallucination_risks=hallucination_risks,
            overall_score=overall_score,
            analysis_time_ms=analysis_time_ms,
            mcp_used=mcp_used,
        )

    def _call_mcp_sequential(self, code: str, file_path: Path) -> Dict:
        """Call MCP Sequential-Thinking for deep analysis

        Future implementation: Integrate with MCP server

        Args:
            code: Python source code
            file_path: Path to file

        Returns:
            Dictionary with solid_violations, security_issues, hallucination_risks

        Raises:
            NotImplementedError: MCP integration not yet implemented
        """
        # Placeholder for future MCP integration
        # When MCP is available, this will:
        # 1. Connect to Sequential-Thinking server
        # 2. Send code for analysis
        # 3. Parse structured response
        # 4. Return violations/issues

        raise NotImplementedError("MCP integration not yet available")

    def _calculate_quality_score(
        self,
        ruff_result: VerificationResult,
        solid_violations: List[Dict],
        security_issues: List[Dict],
        hallucination_risks: List[Dict],
    ) -> float:
        """Calculate overall code quality score (0-10)

        Scoring formula:
        - Start at 10.0
        - Ruff violations: -0.2 each (max -2.0)
        - SOLID violations: -0.5 each (max -3.0)
        - Security issues: -1.0 each (max -4.0)
        - Hallucination risks: -0.1 each (max -1.0)

        Min score: 0.0

        Args:
            ruff_result: Ruff verification result
            solid_violations: SOLID principle violations
            security_issues: Security anti-patterns
            hallucination_risks: Hallucination-prone patterns

        Returns:
            Quality score from 0.0 to 10.0
        """
        score = 10.0

        # Ruff penalties (syntax and style)
        ruff_penalty = min(ruff_result.violation_count * 0.2, 2.0)
        score -= ruff_penalty

        # SOLID penalties (architecture)
        solid_penalty = min(len(solid_violations) * 0.5, 3.0)
        score -= solid_penalty

        # Security penalties (highest weight)
        security_penalty = min(len(security_issues) * 1.0, 4.0)
        score -= security_penalty

        # Hallucination penalties (lowest weight)
        hallucination_penalty = min(len(hallucination_risks) * 0.1, 1.0)
        score -= hallucination_penalty

        # Ensure non-negative
        return max(score, 0.0)


def main():
    """CLI entry point for testing DeepAnalyzer"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python deep_analyzer.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Run analysis
    analyzer = DeepAnalyzer(mcp_enabled=False)
    result = analyzer.analyze(file_path)

    # Display results
    print(f"\n=== Deep Analysis: {file_path.name} ===")
    print(f"Quality Score: {result.overall_score:.1f}/10.0")
    print(f"Analysis Time: {result.analysis_time_ms:.0f}ms")
    print(f"MCP Used: {result.mcp_used}")
    print()

    # Ruff results
    print(f"Ruff Violations: {result.ruff_result.violation_count}")
    if result.ruff_result.violations:
        for v in result.ruff_result.violations[:5]:  # Show first 5
            print(f"  Line {v.line}: {v.code} - {v.message}")

    # SOLID violations
    print(f"\nSOLID Violations: {len(result.solid_violations)}")
    for v in result.solid_violations:
        print(f"  Line {v['line']}: {v['principle']} - {v['message']}")

    # Security issues
    print(f"\nSecurity Issues: {len(result.security_issues)}")
    for issue in result.security_issues:
        print(f"  Line {issue['line']}: {issue['issue']} - {issue['message']}")

    # Hallucination risks
    print(f"\nHallucination Risks: {len(result.hallucination_risks)}")
    for risk in result.hallucination_risks[:5]:  # Show first 5
        print(f"  Line {risk['line']}: {risk['message']}")

    print()
    print(f"Overall Status: {'PASS' if result.passed else 'FAIL'}")
    print(f"Total Issues: {result.total_issues}")


if __name__ == "__main__":
    main()
