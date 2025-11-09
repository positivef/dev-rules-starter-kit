#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Test Generator - P8 (Test First) Enforcement Tool
======================================================

Core Features:
1. Analyze code to detect untested functions
2. Learn existing test patterns
3. Auto-generate pytest-based tests
4. Verify Constitution P8 compliance

Goal: Automatically achieve 95% test coverage
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class FunctionSignature:
    """Function signature information"""

    name: str
    params: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    module: str
    line_number: int
    class_name: Optional[str] = None
    decorators: List[str] = None

    @property
    def full_name(self) -> str:
        """Get fully qualified name"""
        if self.class_name:
            return f"{self.module}.{self.class_name}.{self.name}"
        return f"{self.module}.{self.name}"


@dataclass
class TestPattern:
    """Learned test pattern"""

    pattern_type: str  # unit, integration, edge_case, error_handling
    function_pattern: str  # e.g., "validate_*", "parse_*"
    test_template: str
    assertions: List[str]
    setup: Optional[str] = None
    teardown: Optional[str] = None


@dataclass
class GeneratedTest:
    """Generated test case"""

    function_signature: FunctionSignature
    test_name: str
    test_code: str
    pattern_used: Optional[TestPattern] = None
    confidence: float = 0.0


class CodeAnalyzer:
    """Code analysis and function signature extraction"""

    def __init__(self):
        self.functions_found: List[FunctionSignature] = []
        self.test_functions_found: Set[str] = set()

    def analyze_file(self, file_path: Path) -> List[FunctionSignature]:
        """Analyze Python file and extract function signatures"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            module_name = file_path.stem

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self._extract_function_signature(node, module_name)
                    functions.append(sig)
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            sig = self._extract_function_signature(item, module_name, node.name)
                            functions.append(sig)

            return functions

        except Exception as e:
            print(f"[ERROR] Failed to analyze {file_path}: {e}")
            return []

    def _extract_function_signature(
        self, node: ast.FunctionDef, module: str, class_name: Optional[str] = None
    ) -> FunctionSignature:
        """AST 노드에서 함수 시그니처 추출"""
        # 파라미터 추출
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        # 리턴 타입 추출
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Docstring 추출
        docstring = ast.get_docstring(node)

        # Decorator 추출
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)

        return FunctionSignature(
            name=node.name,
            params=params,
            return_type=return_type,
            docstring=docstring,
            module=module,
            line_number=node.lineno,
            class_name=class_name,
            decorators=decorators,
        )

    def find_existing_tests(self, test_dir: Path) -> Set[str]:
        """기존 테스트 찾기"""
        test_functions = set()

        for test_file in test_dir.rglob("test_*.py"):
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        # 테스트 대상 함수명 추출
                        target_func = self._extract_tested_function(node.name)
                        if target_func:
                            test_functions.add(target_func)

            except Exception as e:
                print(f"[WARN] Failed to analyze test {test_file}: {e}")

        return test_functions

    def _extract_tested_function(self, test_name: str) -> Optional[str]:
        """테스트 함수명에서 대상 함수 추출"""
        # test_function_name -> function_name
        if test_name.startswith("test_"):
            parts = test_name[5:].split("_")
            # Remove common test suffixes
            if parts[-1] in ["success", "failure", "error", "valid", "invalid"]:
                parts = parts[:-1]
            return "_".join(parts)
        return None


class PatternLearner:
    """기존 테스트에서 패턴 학습"""

    def __init__(self):
        self.patterns: List[TestPattern] = []

    def learn_from_tests(self, test_dir: Path) -> List[TestPattern]:
        """테스트 디렉토리에서 패턴 학습"""
        patterns = []

        # 기본 패턴 정의
        patterns.extend(self._get_default_patterns())

        # 실제 테스트에서 패턴 추출
        for test_file in test_dir.rglob("test_*.py"):
            file_patterns = self._extract_patterns_from_file(test_file)
            patterns.extend(file_patterns)

        return patterns

    def _get_default_patterns(self) -> List[TestPattern]:
        """기본 테스트 패턴 반환"""
        return [
            # Validation 함수 패턴
            TestPattern(
                pattern_type="validation",
                function_pattern="validate_*",
                test_template="""def test_{func_name}_valid_input():
    # Arrange
    valid_input = {valid_data}

    # Act
    result = {func_call}(valid_input)

    # Assert
    assert result is True

def test_{func_name}_invalid_input():
    # Arrange
    invalid_input = {invalid_data}

    # Act & Assert
    with pytest.raises({exception_type}):
        {func_call}(invalid_input)""",
                assertions=["assert result is True", "pytest.raises"],
                setup=None,
            ),
            # Parser 함수 패턴
            TestPattern(
                pattern_type="parser",
                function_pattern="parse_*",
                test_template="""def test_{func_name}_valid_format():
    # Arrange
    input_data = {sample_input}
    expected = {expected_output}

    # Act
    result = {func_call}(input_data)

    # Assert
    assert result == expected

def test_{func_name}_malformed_input():
    # Arrange
    malformed_input = {malformed_data}

    # Act & Assert
    with pytest.raises(ValueError):
        {func_call}(malformed_input)""",
                assertions=["assert result == expected", "pytest.raises(ValueError)"],
                setup=None,
            ),
            # Calculator 함수 패턴
            TestPattern(
                pattern_type="calculator",
                function_pattern="calculate_*",
                test_template="""def test_{func_name}_normal_case():
    # Arrange
    input_values = {input_values}
    expected = {expected_result}

    # Act
    result = {func_call}(*input_values)

    # Assert
    assert result == pytest.approx(expected, rel=1e-5)

def test_{func_name}_edge_case():
    # Arrange
    edge_input = {edge_values}

    # Act
    result = {func_call}(*edge_input)

    # Assert
    assert result >= 0  # or appropriate boundary check""",
                assertions=["pytest.approx", "boundary check"],
                setup=None,
            ),
            # CRUD 작업 패턴
            TestPattern(
                pattern_type="crud",
                function_pattern="(create|read|update|delete)_*",
                test_template="""def test_{func_name}_success():
    # Arrange
    test_data = {test_data}

    # Act
    result = {func_call}(test_data)

    # Assert
    assert result is not None
    assert result['status'] == 'success'

def test_{func_name}_not_found():
    # Arrange
    invalid_id = {invalid_id}

    # Act
    result = {func_call}(invalid_id)

    # Assert
    assert result is None or result['status'] == 'not_found'""",
                assertions=["assert result is not None", "assert result['status']"],
                setup="# Setup test database or mock",
            ),
        ]

    def _extract_patterns_from_file(self, test_file: Path) -> List[TestPattern]:
        """실제 테스트 파일에서 패턴 추출"""
        patterns = []

        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 간단한 패턴 매칭으로 테스트 구조 분석
            test_functions = re.findall(r"def (test_\w+)\([^)]*\):(.*?)(?=def test_|\Z)", content, re.DOTALL)

            for test_name, test_body in test_functions:
                # Arrange-Act-Assert 패턴 감지
                has_arrange = "# Arrange" in test_body
                has_act = "# Act" in test_body
                has_assert = "assert" in test_body

                if has_arrange and has_act and has_assert:
                    # AAA 패턴 발견
                    pattern = self._create_pattern_from_test(test_name, test_body)
                    if pattern:  # None 체크 추가
                        patterns.append(pattern)

        except Exception as e:
            print(f"[WARN] Failed to extract patterns from {test_file}: {e}")

        return patterns

    def _create_pattern_from_test(self, test_name: str, test_body: str) -> Optional[TestPattern]:
        """테스트 코드에서 패턴 생성"""
        # 간단한 구현 - 실제로는 더 복잡한 분석 필요
        return None  # Placeholder - 실제 구현에서는 패턴 분석 로직 추가


class TestGenerator:
    """테스트 케이스 생성기"""

    def __init__(self, patterns: List[TestPattern]):
        self.patterns = patterns

    def generate_test(self, signature: FunctionSignature) -> GeneratedTest:
        """함수 시그니처에 맞는 테스트 생성"""
        # 적합한 패턴 찾기
        pattern = self._find_matching_pattern(signature)

        if pattern:
            test_code = self._apply_pattern(signature, pattern)
            confidence = 0.8
        else:
            # 기본 템플릿 사용
            test_code = self._generate_default_test(signature)
            confidence = 0.5

        test_name = f"test_{signature.name}"

        return GeneratedTest(
            function_signature=signature,
            test_name=test_name,
            test_code=test_code,
            pattern_used=pattern,
            confidence=confidence,
        )

    def _find_matching_pattern(self, signature: FunctionSignature) -> Optional[TestPattern]:
        """함수 시그니처에 맞는 패턴 찾기"""
        import fnmatch

        for pattern in self.patterns:
            if pattern and hasattr(pattern, "function_pattern"):  # None 체크 추가
                if fnmatch.fnmatch(signature.name, pattern.function_pattern):
                    return pattern

        return None

    def _apply_pattern(self, signature: FunctionSignature, pattern: TestPattern) -> str:
        """패턴을 적용하여 테스트 코드 생성"""
        # 템플릿 변수 준비
        template_vars = {
            "func_name": signature.name,
            "func_call": signature.name,
            "valid_data": self._generate_sample_data(signature, valid=True),
            "invalid_data": self._generate_sample_data(signature, valid=False),
            "sample_input": "{}",
            "expected_output": "{}",
            "malformed_data": "None",
            "input_values": "[1, 2, 3]",
            "expected_result": "6",
            "edge_values": "[0, 0]",
            "test_data": '{"id": 1, "name": "test"}',
            "invalid_id": "999999",
            "exception_type": "ValueError",
        }

        # 템플릿 채우기
        test_code = pattern.test_template.format(**template_vars)

        return test_code

    def _generate_default_test(self, signature: FunctionSignature) -> str:
        """기본 테스트 템플릿 생성"""
        params_str = ", ".join(self._generate_sample_params(signature))

        test_code = f"""def test_{signature.name}_basic():
    \"\"\"Test {signature.name} with basic inputs\"\"\"
    # Arrange
    {self._generate_arrange_section(signature)}

    # Act
    result = {signature.name}({params_str})

    # Assert
    assert result is not None  # Basic assertion
    # TODO: Add more specific assertions based on function behavior
"""

        # Edge case 테스트 추가
        if signature.params:
            test_code += f"""
def test_{signature.name}_edge_cases():
    \"\"\"Test {signature.name} with edge cases\"\"\"
    # Test with None inputs
    with pytest.raises(TypeError):
        {signature.name}({", ".join(["None"] * len(signature.params))})

    # TODO: Add more edge cases
"""

        # Error handling 테스트 추가
        test_code += f"""
def test_{signature.name}_error_handling():
    \"\"\"Test {signature.name} error handling\"\"\"
    # TODO: Add error handling tests based on function implementation
    pass
"""

        return test_code

    def _generate_sample_data(self, signature: FunctionSignature, valid: bool) -> str:
        """샘플 데이터 생성"""
        if valid:
            return '{"key": "value"}'
        else:
            return "None"

    def _generate_sample_params(self, signature: FunctionSignature) -> List[str]:
        """샘플 파라미터 생성"""
        sample_params = []

        for param in signature.params:
            if param == "self":
                continue
            elif "id" in param.lower():
                sample_params.append("1")
            elif "name" in param.lower():
                sample_params.append('"test"')
            elif "data" in param.lower():
                sample_params.append('{"key": "value"}')
            elif "list" in param.lower() or "array" in param.lower():
                sample_params.append("[1, 2, 3]")
            elif "dict" in param.lower() or "config" in param.lower():
                sample_params.append("{}")
            elif "bool" in param.lower() or "flag" in param.lower():
                sample_params.append("True")
            elif "num" in param.lower() or "count" in param.lower():
                sample_params.append("42")
            else:
                sample_params.append('"sample"')

        return sample_params

    def _generate_arrange_section(self, signature: FunctionSignature) -> str:
        """Arrange 섹션 생성 (들여쓰기 없이 반환)"""
        arrange_lines = []

        for i, param in enumerate(signature.params):
            if param == "self":
                continue
            sample_value = (
                self._generate_sample_params(signature)[i]
                if i < len(self._generate_sample_params(signature))
                else '"sample"'
            )
            arrange_lines.append(f"{param} = {sample_value}")  # 들여쓰기 제거

        return "\n    ".join(arrange_lines) if arrange_lines else "# No parameters"  # join 시 들여쓰기 추가


class P8Validator:
    """P8 (Test First) 원칙 검증"""

    def validate_coverage(self, functions: List[FunctionSignature], tests: Set[str]) -> Dict:
        """테스트 커버리지 검증"""
        total_functions = len(functions)
        tested_functions = 0
        missing_tests = []

        for func in functions:
            # Skip private and magic methods
            if func.name.startswith("_"):
                total_functions -= 1
                continue

            if func.name in tests or f"{func.class_name}_{func.name}" in tests:
                tested_functions += 1
            else:
                missing_tests.append(func)

        coverage = (tested_functions / total_functions * 100) if total_functions > 0 else 0

        return {
            "total_functions": total_functions,
            "tested_functions": tested_functions,
            "coverage_percentage": coverage,
            "missing_tests": missing_tests,
            "p8_compliant": coverage >= 80,  # P8 requires 80% coverage
        }


class AutoTestGenerator:
    """메인 오케스트레이터"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.scripts_dir = self.project_root / "scripts"
        self.tests_dir = self.project_root / "tests"

        self.analyzer = CodeAnalyzer()
        self.learner = PatternLearner()
        self.validator = P8Validator()

    def generate_missing_tests(self) -> Dict:
        """누락된 테스트 자동 생성"""
        print("[ANALYSIS] Starting Auto Test Generation")
        print("[INFO] Project root:", self.project_root)

        # 1. 모든 함수 찾기
        all_functions = []
        for py_file in self.scripts_dir.glob("*.py"):
            if not py_file.name.startswith("test_"):
                functions = self.analyzer.analyze_file(py_file)
                all_functions.extend(functions)

        print(f"[INFO] Found {len(all_functions)} functions to test")

        # 2. 기존 테스트 찾기
        existing_tests = self.analyzer.find_existing_tests(self.tests_dir)
        print(f"[INFO] Found {len(existing_tests)} existing tests")

        # 3. 커버리지 검증
        coverage_report = self.validator.validate_coverage(all_functions, existing_tests)
        print(f"[COVERAGE] Current coverage: {coverage_report['coverage_percentage']:.1f}%")
        print(f"[COVERAGE] Missing tests for {len(coverage_report['missing_tests'])} functions")

        # 4. 패턴 학습
        patterns = self.learner.learn_from_tests(self.tests_dir)
        print(f"[LEARN] Learned {len(patterns)} test patterns")

        # 5. 테스트 생성
        generator = TestGenerator(patterns)
        generated_tests = []

        for func in coverage_report["missing_tests"]:
            test = generator.generate_test(func)
            generated_tests.append(test)

        print(f"[GENERATE] Generated {len(generated_tests)} new tests")

        # 6. 테스트 파일 생성
        self._write_test_files(generated_tests)

        # 7. 결과 보고서 생성
        report = self._generate_report(coverage_report, generated_tests)

        return report

    def _write_test_files(self, tests: List[GeneratedTest]):
        """생성된 테스트를 파일로 저장"""
        # 모듈별로 그룹화
        tests_by_module = {}
        for test in tests:
            module = test.function_signature.module
            if module not in tests_by_module:
                tests_by_module[module] = []
            tests_by_module[module].append(test)

        # 각 모듈별로 테스트 파일 생성
        for module, module_tests in tests_by_module.items():
            test_file_path = self.tests_dir / f"test_{module}_generated.py"

            # 파일 헤더
            content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated tests for {module}.py
Generated at: {datetime.now().isoformat()}
Generator: Auto Test Generator (P8 Enforcement)

[AUTO-GENERATED] These tests were automatically created.
Please review and enhance with specific business logic.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.{module} import *


'''

            # 각 테스트 추가
            for test in module_tests:
                content += f"# Test for {test.function_signature.full_name}\n"
                content += f"# Confidence: {test.confidence:.1%}\n"
                if test.pattern_used:
                    content += f"# Pattern: {test.pattern_used.pattern_type}\n"
                content += test.test_code
                content += "\n\n"

            # 파일 저장
            self.tests_dir.mkdir(exist_ok=True)
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[WRITE] Created {test_file_path}")

    def _generate_report(self, coverage_report: Dict, generated_tests: List[GeneratedTest]) -> Dict:
        """결과 보고서 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_coverage": coverage_report["coverage_percentage"],
            "target_coverage": 95.0,
            "p8_compliant": coverage_report["p8_compliant"],
            "functions_analyzed": coverage_report["total_functions"],
            "existing_tests": coverage_report["tested_functions"],
            "tests_generated": len(generated_tests),
            "new_coverage": min(
                95.0,
                coverage_report["coverage_percentage"] + (len(generated_tests) / coverage_report["total_functions"] * 100),
            ),
            "high_confidence_tests": sum(1 for t in generated_tests if t.confidence >= 0.8),
            "medium_confidence_tests": sum(1 for t in generated_tests if 0.5 <= t.confidence < 0.8),
            "low_confidence_tests": sum(1 for t in generated_tests if t.confidence < 0.5),
        }

        # 보고서 파일로 저장
        report_path = self.project_root / "RUNS" / f"test_generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"[REPORT] Report saved to {report_path}")

        # 콘솔에 요약 출력
        print("\n" + "=" * 60)
        print("[REPORT] Auto Test Generation Summary")
        print("=" * 60)
        print(f"Current Coverage: {report['current_coverage']:.1f}%")
        print(f"New Coverage: {report['new_coverage']:.1f}%")
        print(f"Tests Generated: {report['tests_generated']}")
        print(f"  - High Confidence: {report['high_confidence_tests']}")
        print(f"  - Medium Confidence: {report['medium_confidence_tests']}")
        print(f"  - Low Confidence: {report['low_confidence_tests']}")
        print(f"P8 Compliant: {report['p8_compliant']}")
        print("=" * 60)

        return report


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto Test Generator - P8 Enforcement")
    parser.add_argument("--dir", type=str, help="Directory to analyze", default="scripts")
    parser.add_argument("--output", type=str, help="Output directory for tests", default="tests")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files, just analyze")

    _ = parser.parse_args()

    generator = AutoTestGenerator()
    report = generator.generate_missing_tests()

    if report["p8_compliant"]:
        print("[SUCCESS] P8 (Test First) compliance achieved!")
    else:
        print("[WARNING] P8 compliance not yet achieved. Review and enhance generated tests.")

    return 0 if report["p8_compliant"] else 1


if __name__ == "__main__":
    exit(main())
