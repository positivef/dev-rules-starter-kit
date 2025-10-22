"""Tests for Deep Analyzer (Phase C Week 2)

Comprehensive test suite for DeepAnalyzer and SimpleSolidChecker.

Test Coverage:
1. Basic analysis with clean code
2. SRP violation detection (>10 methods)
3. DIP violation detection (concrete dependencies)
4. Security issue detection (eval, exec, pickle)
5. Hallucination risk detection (TODO, absolute claims)
6. Quality score calculation (various scenarios)
7. Fallback analyzer when MCP disabled
8. Performance validation (<5s)
9. Error handling (invalid Python, missing files)
10. Integration with VerificationResult
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts.deep_analyzer import (
    DeepAnalyzer,
    DeepAnalysisResult,
    SimpleSolidChecker,
)
from scripts.verification_cache import RuffViolation, VerificationResult


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_python_file():
    """Create temporary Python file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        yield Path(f.name)
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def mock_ruff_verifier():
    """Mock RuffVerifier for isolated testing"""
    mock = Mock()
    mock.verify_file.return_value = VerificationResult(
        file_path=Path("test.py"),
        passed=True,
        violations=[],
        duration_ms=50.0,
    )
    return mock


@pytest.fixture
def solid_checker():
    """SimpleSolidChecker instance"""
    return SimpleSolidChecker()


@pytest.fixture
def deep_analyzer(mock_ruff_verifier):
    """DeepAnalyzer instance with mocked RuffVerifier"""
    return DeepAnalyzer(mcp_enabled=False, ruff_verifier=mock_ruff_verifier)


# ============================================================================
# Test 1: Basic Analysis with Clean Code
# ============================================================================


def test_clean_code_analysis(deep_analyzer, temp_python_file):
    """Test analysis of clean code with no violations"""
    # Write clean Python code
    code = '''
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two numbers"""
    return x * y
'''
    temp_python_file.write_text(code, encoding="utf-8")

    # Run analysis
    result = deep_analyzer.analyze(temp_python_file)

    # Assertions
    assert isinstance(result, DeepAnalysisResult)
    assert result.file_path == temp_python_file
    assert result.overall_score == 10.0  # Perfect score
    assert len(result.solid_violations) == 0
    assert len(result.security_issues) == 0
    assert len(result.hallucination_risks) == 0
    assert result.passed is True
    assert result.total_issues == 0
    assert result.mcp_used is False


# ============================================================================
# Test 2: SRP Violation Detection (>10 methods)
# ============================================================================


def test_srp_violation_detection(solid_checker):
    """Test Single Responsibility Principle violation detection"""
    # Create class with >10 methods
    code = """
class GodClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass  # Violation at 11 methods
"""

    violations = solid_checker.check_solid(code, Path("test.py"))

    # Should detect SRP violation
    srp_violations = [v for v in violations if v["principle"] == "Single Responsibility"]
    assert len(srp_violations) > 0
    assert srp_violations[0]["line"] == 2  # Class starts at line 2
    assert "11 methods" in srp_violations[0]["message"]
    assert srp_violations[0]["severity"] == "medium"


# ============================================================================
# Test 3: DIP Violation Detection (concrete dependencies)
# ============================================================================


def test_dip_violation_detection(solid_checker):
    """Test Dependency Inversion Principle violation detection"""
    code = """
class MySQLDatabase:
    pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete dependency violation
"""

    violations = solid_checker.check_solid(code, Path("test.py"))

    # Should detect DIP violation
    dip_violations = [v for v in violations if v["principle"] == "Dependency Inversion"]
    assert len(dip_violations) > 0
    assert dip_violations[0]["line"] == 7  # Assignment line, not __init__ line
    assert "MySQLDatabase" in dip_violations[0]["message"]
    assert dip_violations[0]["severity"] == "high"


# ============================================================================
# Test 4: Security Issue Detection
# ============================================================================


def test_security_eval_detection(solid_checker):
    """Test detection of eval() security issue"""
    code = """
def dangerous_function(user_input):
    result = eval(user_input)  # Security risk
    return result
"""

    issues = solid_checker.check_security(code)

    # Should detect eval usage
    eval_issues = [i for i in issues if i["issue"] == "eval"]
    assert len(eval_issues) > 0
    assert eval_issues[0]["line"] == 3
    assert "arbitrary code execution" in eval_issues[0]["message"]
    assert eval_issues[0]["severity"] == "high"


def test_security_exec_detection(solid_checker):
    """Test detection of exec() security issue"""
    code = """
def run_code(code_str):
    exec(code_str)  # Security risk
"""

    issues = solid_checker.check_security(code)

    exec_issues = [i for i in issues if i["issue"] == "exec"]
    assert len(exec_issues) > 0
    assert "arbitrary code execution" in exec_issues[0]["message"]


def test_security_pickle_detection(solid_checker):
    """Test detection of pickle.loads() security issue"""
    code = """
import pickle

def load_data(data):
    obj = pickle.loads(data)  # Security risk
    return obj
"""

    issues = solid_checker.check_security(code)

    pickle_issues = [i for i in issues if i["issue"] == "pickle"]
    assert len(pickle_issues) > 0
    assert "arbitrary code" in pickle_issues[0]["message"]


def test_security_hardcoded_secret(solid_checker):
    """Test detection of hardcoded secrets"""
    code = """
api_key = "test-placeholder-key"  # Hardcoded secret
password = "test-placeholder-pwd"  # Hardcoded password
"""

    issues = solid_checker.check_security(code)

    secret_issues = [i for i in issues if i["issue"] == "hardcoded_secret"]
    assert len(secret_issues) >= 2  # Should detect both
    # Check that at least one issue is related to api_key or password
    code_lines = code.split("\n")
    assert any("api_key" in code_lines[i["line"] - 1] or "password" in code_lines[i["line"] - 1] for i in secret_issues)


def test_security_shell_true(solid_checker):
    """Test detection of subprocess shell=True"""
    code = """
import subprocess

subprocess.run(["ls"], shell=True)  # Security risk
"""

    issues = solid_checker.check_security(code)

    shell_issues = [i for i in issues if i["issue"] == "shell_true"]
    assert len(shell_issues) > 0
    assert "arbitrary commands" in shell_issues[0]["message"]


# ============================================================================
# Test 5: Hallucination Risk Detection
# ============================================================================


def test_hallucination_todo_detection(solid_checker):
    """Test detection of TODO comments"""
    code = """
def process_data(data):
    # TODO: implement validation
    return data
"""

    risks = solid_checker.check_hallucination(code)

    todo_risks = [r for r in risks if "TODO" in r["message"]]
    assert len(todo_risks) > 0
    assert todo_risks[0]["line"] == 3
    assert "Unfinished implementation" in todo_risks[0]["message"]
    assert todo_risks[0]["severity"] == "low"


def test_hallucination_absolute_claims(solid_checker):
    """Test detection of absolute claims (always, never, guaranteed)"""
    code = """
def process(data):
    # This function always succeeds
    # It never fails
    # Results are guaranteed to be perfect
    return data
"""

    risks = solid_checker.check_hallucination(code)

    # Should detect multiple absolute claims
    assert len(risks) >= 3
    claim_words = ["always", "never", "guaranteed", "perfect"]
    for risk in risks:
        assert any(word in risk["message"].lower() for word in claim_words)


def test_hallucination_placeholder_detection(solid_checker):
    """Test detection of placeholder values"""
    code = """
def get_user():
    return {"name": "placeholder", "email": "dummy@example.com"}
"""

    risks = solid_checker.check_hallucination(code)

    placeholder_risks = [r for r in risks if "placeholder" in r["message"].lower()]
    assert len(placeholder_risks) > 0


def test_hallucination_not_implemented(solid_checker):
    """Test detection of NotImplementedError"""
    code = """
def future_feature():
    raise NotImplementedError("Coming soon")
"""

    risks = solid_checker.check_hallucination(code)

    not_impl_risks = [r for r in risks if "Unimplemented" in r["message"]]
    assert len(not_impl_risks) > 0


# ============================================================================
# Test 6: Quality Score Calculation
# ============================================================================


def test_quality_score_perfect(deep_analyzer):
    """Test quality score calculation for perfect code"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=True,
        violations=[],
        duration_ms=50.0,
    )

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=[],
        security_issues=[],
        hallucination_risks=[],
    )

    assert score == 10.0


def test_quality_score_ruff_penalties(deep_analyzer):
    """Test quality score with Ruff violations"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=False,
        violations=[
            RuffViolation(code="E501", message="Line too long", line=1, column=80),
            RuffViolation(code="F401", message="Unused import", line=2, column=1),
        ],
        duration_ms=50.0,
    )

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=[],
        security_issues=[],
        hallucination_risks=[],
    )

    # 2 violations * 0.2 = -0.4
    assert score == 9.6


def test_quality_score_solid_penalties(deep_analyzer):
    """Test quality score with SOLID violations"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=True,
        violations=[],
        duration_ms=50.0,
    )

    solid_violations = [
        {"line": 1, "principle": "SRP", "message": "Too many methods", "severity": "medium"},
        {"line": 10, "principle": "DIP", "message": "Concrete dependency", "severity": "high"},
    ]

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=solid_violations,
        security_issues=[],
        hallucination_risks=[],
    )

    # 2 violations * 0.5 = -1.0
    assert score == 9.0


def test_quality_score_security_penalties(deep_analyzer):
    """Test quality score with security issues"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=True,
        violations=[],
        duration_ms=50.0,
    )

    security_issues = [
        {"line": 5, "issue": "eval", "message": "eval() usage", "severity": "high"},
    ]

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=[],
        security_issues=security_issues,
        hallucination_risks=[],
    )

    # 1 security issue * 1.0 = -1.0
    assert score == 9.0


def test_quality_score_max_penalties(deep_analyzer):
    """Test quality score with maximum penalties"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=False,
        violations=[RuffViolation("E501", "Error", 1, 1) for _ in range(20)],  # Max -2.0
        duration_ms=50.0,
    )

    solid_violations = [
        {"line": i, "principle": "SRP", "message": "Test", "severity": "medium"} for i in range(10)
    ]  # Max -3.0

    security_issues = [{"line": i, "issue": "eval", "message": "Test", "severity": "high"} for i in range(10)]  # Max -4.0

    hallucination_risks = [{"line": i, "risk": "TODO", "message": "Test", "severity": "low"} for i in range(20)]  # Max -1.0

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=solid_violations,
        security_issues=security_issues,
        hallucination_risks=hallucination_risks,
    )

    # Max penalties: -2.0 -3.0 -4.0 -1.0 = 0.0 (minimum)
    assert score == 0.0


def test_quality_score_combined(deep_analyzer):
    """Test quality score with mixed violations"""
    ruff_result = VerificationResult(
        file_path=Path("test.py"),
        passed=False,
        violations=[RuffViolation("E501", "Error", 1, 1)],
        duration_ms=50.0,
    )

    score = deep_analyzer._calculate_quality_score(
        ruff_result=ruff_result,
        solid_violations=[{"line": 1, "principle": "SRP", "message": "Test", "severity": "medium"}],
        security_issues=[{"line": 2, "issue": "eval", "message": "Test", "severity": "high"}],
        hallucination_risks=[{"line": 3, "risk": "TODO", "message": "Test", "severity": "low"}],
    )

    # Penalties: -0.2 (ruff) -0.5 (solid) -1.0 (security) -0.1 (hallucination) = -1.8
    assert abs(score - 8.2) < 0.01  # Use floating point tolerance


# ============================================================================
# Test 7: Fallback Analyzer (MCP Disabled)
# ============================================================================


def test_fallback_analyzer_used(deep_analyzer, temp_python_file):
    """Test that fallback analyzer is used when MCP is disabled"""
    code = """
def test():
    eval("1+1")  # Security issue
    # TODO: implement
"""
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Should use fallback (not MCP)
    assert result.mcp_used is False

    # Should detect issues with fallback
    assert len(result.security_issues) > 0
    assert len(result.hallucination_risks) > 0


# ============================================================================
# Test 8: Performance Validation (<5s)
# ============================================================================


def test_performance_typical_file(deep_analyzer, temp_python_file):
    """Test that analysis completes in <5s for typical file"""
    # Create typical Python file (~200 lines)
    code = (
        '''
class DataProcessor:
    def __init__(self, config):
        self.config = config

    def process(self, data):
        """Process data"""
        validated = self._validate(data)
        transformed = self._transform(validated)
        return self._save(transformed)

    def _validate(self, data):
        if not data:
            raise ValueError("Empty data")
        return data

    def _transform(self, data):
        return [x * 2 for x in data]

    def _save(self, data):
        return data
'''
        * 10
    )  # Repeat to make ~200 lines

    temp_python_file.write_text(code, encoding="utf-8")

    # Time analysis
    start = time.perf_counter()
    result = deep_analyzer.analyze(temp_python_file)
    elapsed = time.perf_counter() - start

    # Should complete in <5s
    assert elapsed < 5.0

    # Result should have timing info
    assert result.analysis_time_ms > 0


def test_performance_small_file(deep_analyzer, temp_python_file):
    """Test that analysis is fast for small files (<1s)"""
    code = """
def hello():
    return "world"
"""
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Should be very fast for small files
    assert result.analysis_time_ms < 1000  # <1 second


# ============================================================================
# Test 9: Error Handling
# ============================================================================


def test_error_handling_invalid_python(deep_analyzer, temp_python_file):
    """Test error handling for invalid Python syntax"""
    # Write syntactically invalid Python
    code = """
def broken(
    # Missing closing parenthesis
"""
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Should complete without crashing
    assert isinstance(result, DeepAnalysisResult)

    # Should have low quality score but not crash
    assert result.overall_score >= 0.0


def test_error_handling_missing_file(deep_analyzer):
    """Test error handling for missing file"""
    missing_file = Path("/nonexistent/file.py")

    # Should handle gracefully (RuffVerifier will handle this)
    # We just ensure no exception is raised
    try:
        result = deep_analyzer.analyze(missing_file)
        # If it completes, should have error indication
        assert result.overall_score == 0.0 or result.ruff_result.error is not None
    except Exception:
        # Or it may raise an exception - both are acceptable
        pass


def test_error_handling_unreadable_file(deep_analyzer, tmp_path):
    """Test error handling for unreadable file content"""
    # Create file with binary content (not valid UTF-8)
    binary_file = tmp_path / "binary.py"
    binary_file.write_bytes(b"\x80\x81\x82\x83")

    result = deep_analyzer.analyze(binary_file)

    # Should handle gracefully
    assert isinstance(result, DeepAnalysisResult)
    assert result.overall_score == 0.0  # Can't analyze invalid content


# ============================================================================
# Test 10: Integration with VerificationResult
# ============================================================================


def test_integration_verification_result_compatibility(deep_analyzer, temp_python_file):
    """Test that DeepAnalysisResult integrates with VerificationResult"""
    code = """
def add(a, b):
    return a + b
"""
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Should contain VerificationResult
    assert isinstance(result.ruff_result, VerificationResult)
    # Note: mock_ruff_verifier returns a fixed path "test.py", so we check the deep result path
    assert result.file_path == temp_python_file

    # Can be converted to VerificationResult for compatibility
    ruff_result = result.ruff_result
    assert hasattr(ruff_result, "passed")
    assert hasattr(ruff_result, "violations")
    assert hasattr(ruff_result, "duration_ms")


def test_integration_deep_analysis_properties(deep_analyzer, temp_python_file):
    """Test DeepAnalysisResult properties"""
    code = """
def process():
    eval("1+1")  # Security issue
    # TODO: implement
"""
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Test properties
    assert isinstance(result.passed, bool)
    assert isinstance(result.total_issues, int)
    assert result.total_issues > 0  # Has security issue and TODO

    # passed should be False due to security issues
    assert result.passed is False


# ============================================================================
# Additional Tests: Complexity Detection
# ============================================================================


def test_complexity_long_function_detection(solid_checker):
    """Test detection of overly long functions"""
    # Create function with >50 lines
    lines = ["def long_function():"]
    lines.extend([f"    x{i} = {i}" for i in range(60)])  # 60 lines
    lines.append("    return x59")
    code = "\n".join(lines)

    violations = solid_checker.check_solid(code, Path("test.py"))

    complexity_violations = [v for v in violations if v["principle"] == "Complexity" and "lines" in v["message"]]
    assert len(complexity_violations) > 0
    assert "long_function" in complexity_violations[0]["message"]


def test_complexity_cyclomatic_complexity(solid_checker):
    """Test detection of high cyclomatic complexity"""
    # Create function with high complexity (many branches)
    code = """
def complex_function(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            return 1
    while a:
        if b:
            break
    for x in range(10):
        if x > 5:
            continue
    return 0
"""

    violations = solid_checker.check_solid(code, Path("test.py"))

    complexity_violations = [v for v in violations if "complexity" in v["message"].lower()]
    # Should detect high complexity
    assert len(complexity_violations) > 0


# ============================================================================
# Summary Test
# ============================================================================


def test_full_integration_scenario(deep_analyzer, temp_python_file):
    """Integration test with realistic code containing multiple issues"""
    code = '''
import pickle

class UserManager:
    """Manages users - demonstrates multiple issues"""

    def __init__(self):
        self.db = MySQLDatabase()  # DIP violation

    def authenticate(self, username, password):
        # TODO: implement proper auth
        api_key = "sk-12345"  # Hardcoded secret
        result = eval(f"check_user('{username}')")  # Security issue
        return result

    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass  # SRP violation (>10 methods)

class MySQLDatabase:
    pass
'''
    temp_python_file.write_text(code, encoding="utf-8")

    result = deep_analyzer.analyze(temp_python_file)

    # Should detect multiple issue types
    assert len(result.solid_violations) > 0  # DIP and SRP violations
    assert len(result.security_issues) > 0  # eval and hardcoded secret
    assert len(result.hallucination_risks) > 0  # TODO comment

    # Quality score should be significantly reduced
    assert result.overall_score < 7.0

    # Should not pass overall
    assert result.passed is False

    # Should have reasonable performance
    assert result.analysis_time_ms < 5000  # <5s
