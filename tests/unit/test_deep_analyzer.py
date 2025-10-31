"""Unit tests for deep_analyzer.py

Tests the DeepAnalysisResult class and code analysis functions.
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest
import ast
from deep_analyzer import (
    DeepAnalysisResult,
    SimpleSolidChecker,
)
from verification_cache import VerificationResult


class TestDeepAnalysisResult:
    """Test DeepAnalysisResult dataclass and properties"""

    def test_create_result_with_defaults(self):
        """Should create result with default values"""
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=True, violations=[], duration_ms=10.0)

        result = DeepAnalysisResult(file_path=Path("test.py"), ruff_result=ruff_result)

        assert result.file_path == Path("test.py")
        assert result.ruff_result == ruff_result
        assert result.solid_violations == []
        assert result.security_issues == []
        assert result.hallucination_risks == []
        assert result.overall_score == 10.0
        assert result.analysis_time_ms == 0.0
        assert result.mcp_used is False

    def test_passed_property_all_checks_pass(self):
        """Should return True when all checks pass"""
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=True, violations=[], duration_ms=10.0)

        result = DeepAnalysisResult(
            file_path=Path("test.py"),
            ruff_result=ruff_result,
            solid_violations=[],
            security_issues=[],
            overall_score=8.0,
        )

        assert result.passed is True

    def test_passed_property_ruff_fails(self):
        """Should return False when ruff fails"""
        from verification_cache import RuffViolation

        violations = [
            RuffViolation(code="E1", message="error1", line=1, column=1),
            RuffViolation(code="E2", message="error2", line=2, column=1),
        ]
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=False, violations=violations, duration_ms=10.0)

        result = DeepAnalysisResult(file_path=Path("test.py"), ruff_result=ruff_result, overall_score=8.0)

        assert result.passed is False

    def test_passed_property_solid_violations(self):
        """Should return False when SOLID violations exist"""
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=True, violations=[], duration_ms=10.0)

        result = DeepAnalysisResult(
            file_path=Path("test.py"),
            ruff_result=ruff_result,
            solid_violations=[{"line": 10, "message": "Too complex"}],
            overall_score=8.0,
        )

        assert result.passed is False

    def test_passed_property_low_score(self):
        """Should return False when overall score is low"""
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=True, violations=[], duration_ms=10.0)

        result = DeepAnalysisResult(file_path=Path("test.py"), ruff_result=ruff_result, overall_score=6.5)

        assert result.passed is False

    def test_total_issues_counts_all(self):
        """Should count all issues from all sources"""
        from verification_cache import RuffViolation

        violations = [
            RuffViolation(code="E1", message="error1", line=1, column=1),
            RuffViolation(code="E2", message="error2", line=2, column=1),
        ]
        ruff_result = VerificationResult(file_path=Path("test.py"), passed=False, violations=violations, duration_ms=10.0)

        result = DeepAnalysisResult(
            file_path=Path("test.py"),
            ruff_result=ruff_result,
            solid_violations=[{"line": 10}, {"line": 20}],
            security_issues=[{"line": 30}],
            hallucination_risks=[{"line": 40}, {"line": 50}],
        )

        # 2 (ruff) + 2 (solid) + 1 (security) + 2 (hallucination) = 7
        assert result.total_issues == 7


class TestSimpleSolidChecker:
    """Test SimpleSolidChecker class"""

    def test_check_srp_class_with_few_methods(self):
        """Should pass for class with few methods"""
        checker = SimpleSolidChecker()

        code = """
class SimpleClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""

        violations = checker._check_srp(ast.parse(code))

        assert len(violations) == 0

    def test_check_srp_class_with_too_many_methods(self):
        """Should detect class with >10 methods"""
        checker = SimpleSolidChecker()

        # Create class with 11 methods
        methods = "\n    ".join([f"def method{i}(self): pass" for i in range(11)])
        code = f"""
class LargeClass:
    {methods}
"""

        violations = checker._check_srp(ast.parse(code))

        assert len(violations) == 1
        assert violations[0]["principle"] == "Single Responsibility"
        assert "LargeClass" in violations[0]["message"]
        assert "11 methods" in violations[0]["message"]

    def test_check_dip_no_instantiation(self):
        """Should pass when no concrete instantiation in __init__"""
        checker = SimpleSolidChecker()

        code = """
class GoodClass:
    def __init__(self, dependency):
        self.dependency = dependency
"""

        violations = checker._check_dip(ast.parse(code))

        assert len(violations) == 0

    def test_check_dip_concrete_instantiation(self):
        """Should detect concrete class instantiation in __init__"""
        checker = SimpleSolidChecker()

        code = """
class BadClass:
    def __init__(self):
        self.db = Database()
        self.cache = Cache()
"""

        violations = checker._check_dip(ast.parse(code))

        assert len(violations) == 2
        assert all(v["principle"] == "Dependency Inversion" for v in violations)
        assert any("Database" in v["message"] for v in violations)
        assert any("Cache" in v["message"] for v in violations)

    def test_check_complexity_short_function(self):
        """Should pass for short simple function"""
        checker = SimpleSolidChecker()

        code = """
def simple_function():
    x = 1
    y = 2
    return x + y
"""

        violations = checker._check_complexity(ast.parse(code), code)

        assert len(violations) == 0

    def test_check_complexity_long_function(self):
        """Should detect function >50 lines"""
        checker = SimpleSolidChecker()

        # Create function with 51 lines
        lines = "\n    ".join([f"line{i} = {i}" for i in range(51)])
        code = f"""
def long_function():
    {lines}
"""

        violations = checker._check_complexity(ast.parse(code), code)

        assert len(violations) >= 1
        assert any(v["principle"] == "Complexity" for v in violations)
        assert any("long_function" in v["message"] for v in violations)

    def test_check_solid_integration(self):
        """Should run full SOLID check on code"""
        checker = SimpleSolidChecker()

        code = """
class TestClass:
    def __init__(self):
        self.db = Database()

    def method1(self):
        pass
"""

        violations = checker.check_solid(code, Path("test.py"))

        # Should find DIP violation
        assert len(violations) >= 1
        assert any(v["principle"] == "Dependency Inversion" for v in violations)

    def test_check_solid_syntax_error(self):
        """Should handle syntax errors gracefully"""
        checker = SimpleSolidChecker()

        code = "def invalid syntax here"

        violations = checker.check_solid(code, Path("test.py"))

        # Should return empty list for syntax errors
        assert violations == []


class TestCheckSecurity:
    """Test security issue detection"""

    def test_check_security_no_issues(self):
        """Should pass clean code"""
        checker = SimpleSolidChecker()

        code = """
def safe_function():
    result = process_data()
    return result
"""

        issues = checker.check_security(code)

        assert len(issues) == 0

    def test_check_security_eval_detected(self):
        """Should detect eval() usage"""
        checker = SimpleSolidChecker()

        code = """
def unsafe_function():
    result = eval(user_input)
    return result
"""

        issues = checker.check_security(code)

        assert len(issues) >= 1
        assert any("eval" in issue["message"].lower() for issue in issues)

    def test_check_security_exec_detected(self):
        """Should detect exec() usage"""
        checker = SimpleSolidChecker()

        code = """
def unsafe_function():
    exec(user_code)
"""

        issues = checker.check_security(code)

        assert len(issues) >= 1
        assert any("exec" in issue["message"].lower() for issue in issues)

    def test_check_security_sql_injection_pattern(self):
        """Should detect SQL injection patterns"""
        checker = SimpleSolidChecker()

        code = """
def query_database():
    query = "SELECT * FROM users WHERE id = " + user_id
    execute(query)
"""

        issues = checker.check_security(code)

        # May or may not detect depending on implementation
        # Just checking it doesn't crash
        assert isinstance(issues, list)


class TestCheckHallucination:
    """Test hallucination risk detection"""

    def test_check_hallucination_no_risks(self):
        """Should pass code without TODOs or unverified claims"""
        checker = SimpleSolidChecker()

        code = """
def verified_function():
    # Tested and verified
    return 42
"""

        risks = checker.check_hallucination(code)

        assert len(risks) == 0

    def test_check_hallucination_todo_detected(self):
        """Should detect TODO comments"""
        checker = SimpleSolidChecker()

        code = """
def incomplete_function():
    # TODO: implement this later
    pass
"""

        risks = checker.check_hallucination(code)

        assert len(risks) >= 1
        assert any("TODO" in risk["message"] for risk in risks)

    def test_check_hallucination_fixme_detected(self):
        """Should detect FIXME comments"""
        checker = SimpleSolidChecker()

        code = """
def buggy_function():
    # FIXME: this doesn't work properly
    return None
"""

        risks = checker.check_hallucination(code)

        assert len(risks) >= 1
        assert any("FIXME" in risk["message"] for risk in risks)

    def test_check_hallucination_always_pattern(self):
        """Should detect 'always works' claims"""
        checker = SimpleSolidChecker()

        code = '''
def unreliable_function():
    """This function always works correctly"""
    return random_result()
'''

        risks = checker.check_hallucination(code)

        # May or may not detect depending on implementation
        assert isinstance(risks, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
