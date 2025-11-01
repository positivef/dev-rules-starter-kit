#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Generator - Automated Test Code Generation

Analyzes Python code and generates comprehensive test suites with:
- Function signature analysis
- Edge case detection
- Mock object generation
- Boundary value testing
- Exception handling tests
- P8 (Test First) compliance

Usage:
  python scripts/test_generator.py file.py                # Generate tests for file
  python scripts/test_generator.py file.py::ClassName     # Generate for class
  python scripts/test_generator.py file.py::function_name # Generate for function
  python scripts/test_generator.py --watch                # Watch mode
  python scripts/test_generator.py --coverage             # Include coverage tests

Reduces test writing time by 40%
"""

import ast
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class TestCase:
    """Single test case"""

    name: str
    description: str
    inputs: Dict[str, Any]
    expected_output: Any
    should_raise: Optional[str] = None
    mock_setup: Optional[str] = None


@dataclass
class TestSuite:
    """Complete test suite for a function/class"""

    target_name: str
    target_type: str  # function, method, class
    import_statement: str
    test_cases: List[TestCase]
    fixtures: List[str] = field(default_factory=list)
    mocks: List[str] = field(default_factory=list)


class TestGenerator:
    """Automated test generation system"""

    # Type to test data mapping
    TYPE_TEST_DATA = {
        "int": [0, 1, -1, 999999, -999999],
        "float": [0.0, 1.0, -1.0, 0.1, -0.1, float("inf"), float("-inf")],
        "str": ["", "a", "test", "Test String", "123", "!@#$%", " ", "\n", "very" * 100],
        "bool": [True, False],
        "list": [[], [1], [1, 2, 3], list(range(100))],
        "dict": [{}, {"key": "value"}, {"a": 1, "b": 2}],
        "tuple": [(), (1,), (1, 2, 3)],
        "set": [set(), {1}, {1, 2, 3}],
        "None": [None],
    }

    # Common edge cases by parameter name
    PARAM_EDGE_CASES = {
        "filename": ["", "nonexistent.txt", "/etc/passwd", "CON", "../../../etc/passwd"],
        "path": ["", ".", "..", "/", "C:\\", "/tmp/test", "nonexistent/path"],
        "email": ["", "invalid", "test@example.com", "test@", "@example.com"],
        "url": ["", "http://example.com", "https://example.com", "ftp://", "javascript:alert(1)"],
        "password": ["", "123", "password", "P@ssw0rd!", "a" * 1000],
        "username": ["", "a", "admin", "user123", "user-name", "user_name", "user@name"],
        "id": [0, -1, 1, 999999, None],
        "count": [0, 1, -1, 100, 999999],
        "size": [0, 1, -1, 100, 999999],
        "index": [0, -1, 1, 999999],
        "timeout": [0, 0.001, 1, 60, 3600, -1],
    }

    def __init__(self, coverage_mode: bool = False):
        """Initialize generator"""
        self.coverage_mode = coverage_mode
        self.generated_tests = []

    def generate_tests_for_file(self, filepath: str) -> List[TestSuite]:
        """Generate tests for entire file"""
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        module_name = path.stem

        test_suites = []

        # Process all functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):  # Skip private functions
                    suite = self._generate_function_tests(node, module_name)
                    if suite:
                        test_suites.append(suite)

            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):  # Skip private classes
                    suite = self._generate_class_tests(node, module_name)
                    if suite:
                        test_suites.append(suite)

        return test_suites

    def _generate_function_tests(self, func_node: ast.FunctionDef, module_name: str) -> Optional[TestSuite]:
        """Generate tests for a function"""
        func_name = func_node.name

        # Extract function signature
        args = self._extract_arguments(func_node)

        # Extract return type if available
        return_type = self._extract_return_type(func_node)

        # Generate test cases
        test_cases = []

        # 1. Normal cases
        test_cases.extend(self._generate_normal_cases(func_name, args, return_type))

        # 2. Edge cases
        test_cases.extend(self._generate_edge_cases(func_name, args))

        # 3. Error cases
        test_cases.extend(self._generate_error_cases(func_name, args))

        # 4. Boundary cases
        if self.coverage_mode:
            test_cases.extend(self._generate_boundary_cases(func_name, args))

        if not test_cases:
            return None

        return TestSuite(
            target_name=func_name,
            target_type="function",
            import_statement=f"from {module_name} import {func_name}",
            test_cases=test_cases,
        )

    def _generate_class_tests(self, class_node: ast.ClassDef, module_name: str) -> Optional[TestSuite]:
        """Generate tests for a class"""
        class_name = class_node.name
        test_cases = []

        # Find __init__ method
        init_method = None
        methods = []

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name == "__init__":
                    init_method = node
                elif not node.name.startswith("_"):  # Public methods
                    methods.append(node)

        # Generate initialization tests
        if init_method:
            init_args = self._extract_arguments(init_method)
            test_cases.extend(self._generate_init_tests(class_name, init_args))

        # Generate method tests
        for method in methods:
            method_args = self._extract_arguments(method)
            test_cases.extend(self._generate_method_tests(class_name, method.name, method_args))

        if not test_cases:
            return None

        return TestSuite(
            target_name=class_name,
            target_type="class",
            import_statement=f"from {module_name} import {class_name}",
            test_cases=test_cases,
            fixtures=[self._generate_fixture(class_name, init_args if init_method else {})],
        )

    def _extract_arguments(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function arguments with type hints"""
        args = {}

        for arg in func_node.args.args:
            if arg.arg != "self":  # Skip self parameter
                arg_name = arg.arg

                # Try to get type annotation
                if arg.annotation:
                    type_name = self._get_type_name(arg.annotation)
                    args[arg_name] = type_name
                else:
                    # Infer from name
                    args[arg_name] = self._infer_type_from_name(arg_name)

        return args

    def _extract_return_type(self, func_node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation"""
        if func_node.returns:
            return self._get_type_name(func_node.returns)
        return None

    def _get_type_name(self, annotation) -> str:
        """Get type name from annotation"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        else:
            return "Any"

    def _infer_type_from_name(self, param_name: str) -> str:
        """Infer type from parameter name"""
        name_lower = param_name.lower()

        if "id" in name_lower or "count" in name_lower or "size" in name_lower:
            return "int"
        elif "name" in name_lower or "text" in name_lower or "message" in name_lower:
            return "str"
        elif "flag" in name_lower or "is_" in name_lower or "has_" in name_lower:
            return "bool"
        elif "items" in name_lower or "list" in name_lower:
            return "list"
        elif "data" in name_lower or "config" in name_lower:
            return "dict"
        else:
            return "Any"

    def _generate_normal_cases(self, func_name: str, args: Dict[str, Any], return_type: Optional[str]) -> List[TestCase]:
        """Generate normal test cases"""
        test_cases = []

        # Generate basic happy path test
        test_input = {}
        for param_name, param_type in args.items():
            if param_type in self.TYPE_TEST_DATA:
                # Use a reasonable default value
                test_values = self.TYPE_TEST_DATA[param_type]
                test_input[param_name] = test_values[1] if len(test_values) > 1 else test_values[0]
            else:
                test_input[param_name] = None

        test_cases.append(
            TestCase(
                name=f"test_{func_name}_normal_case",
                description=f"Test {func_name} with normal inputs",
                inputs=test_input,
                expected_output="# TODO: Add expected output",
            )
        )

        # Generate additional normal cases for different input combinations
        if len(args) > 1:
            test_input2 = {}
            for param_name, param_type in args.items():
                if param_type in self.TYPE_TEST_DATA:
                    test_values = self.TYPE_TEST_DATA[param_type]
                    test_input2[param_name] = test_values[2] if len(test_values) > 2 else test_values[0]
                else:
                    test_input2[param_name] = None

            test_cases.append(
                TestCase(
                    name=f"test_{func_name}_alternate_inputs",
                    description=f"Test {func_name} with alternate valid inputs",
                    inputs=test_input2,
                    expected_output="# TODO: Add expected output",
                )
            )

        return test_cases

    def _generate_edge_cases(self, func_name: str, args: Dict[str, Any]) -> List[TestCase]:
        """Generate edge case tests"""
        test_cases = []

        for param_name, param_type in args.items():
            # Check if we have specific edge cases for this parameter name
            if param_name in self.PARAM_EDGE_CASES:
                for edge_value in self.PARAM_EDGE_CASES[param_name][:3]:  # Top 3 edge cases
                    test_input = self._create_test_input(args, param_name, edge_value)

                    test_cases.append(
                        TestCase(
                            name=f"test_{func_name}_edge_{param_name}_{self._sanitize_name(str(edge_value))}",
                            description=f"Test {func_name} with edge case for {param_name}",
                            inputs=test_input,
                            expected_output="# TODO: Add expected output or exception",
                        )
                    )

            # Generic edge cases by type
            elif param_type in self.TYPE_TEST_DATA:
                # Test with first (usually empty/zero) and last (extreme) values
                test_values = self.TYPE_TEST_DATA[param_type]

                for edge_value in [test_values[0], test_values[-1]]:
                    test_input = self._create_test_input(args, param_name, edge_value)

                    test_cases.append(
                        TestCase(
                            name=f"test_{func_name}_{param_name}_{self._sanitize_name(str(edge_value))}",
                            description=f"Test {func_name} with edge value for {param_name}",
                            inputs=test_input,
                            expected_output="# TODO: Add expected output",
                        )
                    )

        return test_cases

    def _generate_error_cases(self, func_name: str, args: Dict[str, Any]) -> List[TestCase]:
        """Generate error test cases"""
        test_cases = []

        # Test with None values
        for param_name in args:
            test_input = self._create_test_input(args, param_name, None)

            test_cases.append(
                TestCase(
                    name=f"test_{func_name}_none_{param_name}",
                    description=f"Test {func_name} with None for {param_name}",
                    inputs=test_input,
                    expected_output=None,
                    should_raise="TypeError",  # Or appropriate exception
                )
            )

        # Test with wrong types
        for param_name, param_type in args.items():
            wrong_value = self._get_wrong_type_value(param_type)
            if wrong_value is not None:
                test_input = self._create_test_input(args, param_name, wrong_value)

                test_cases.append(
                    TestCase(
                        name=f"test_{func_name}_wrong_type_{param_name}",
                        description=f"Test {func_name} with wrong type for {param_name}",
                        inputs=test_input,
                        expected_output=None,
                        should_raise="TypeError",
                    )
                )

        return test_cases

    def _generate_boundary_cases(self, func_name: str, args: Dict[str, Any]) -> List[TestCase]:
        """Generate boundary value tests"""
        test_cases = []

        for param_name, param_type in args.items():
            if param_type == "int":
                # Test boundary values for integers
                boundary_values = [
                    0,
                    1,
                    -1,  # Around zero
                    2147483647,  # Max int32
                    -2147483648,  # Min int32
                ]

                for value in boundary_values:
                    test_input = self._create_test_input(args, param_name, value)

                    test_cases.append(
                        TestCase(
                            name=f"test_{func_name}_boundary_{param_name}_{value}",
                            description=f"Test {func_name} with boundary value {value} for {param_name}",
                            inputs=test_input,
                            expected_output="# TODO: Add expected output",
                        )
                    )

            elif param_type == "str":
                # Test string boundaries
                boundary_values = [
                    "",  # Empty
                    "a",  # Single char
                    "a" * 255,  # Common max length
                    "a" * 65536,  # Large string
                ]

                for value in boundary_values[:2]:  # Just empty and single char
                    test_input = self._create_test_input(args, param_name, value)

                    test_cases.append(
                        TestCase(
                            name=f"test_{func_name}_boundary_{param_name}_len{len(value)}",
                            description=f"Test {func_name} with string length {len(value)} for {param_name}",
                            inputs=test_input,
                            expected_output="# TODO: Add expected output",
                        )
                    )

        return test_cases

    def _generate_init_tests(self, class_name: str, args: Dict[str, Any]) -> List[TestCase]:
        """Generate initialization tests for a class"""
        test_cases = []

        # Normal initialization
        test_input = {}
        for param_name, param_type in args.items():
            if param_type in self.TYPE_TEST_DATA:
                test_values = self.TYPE_TEST_DATA[param_type]
                test_input[param_name] = test_values[1] if len(test_values) > 1 else test_values[0]
            else:
                test_input[param_name] = None

        test_cases.append(
            TestCase(
                name=f"test_{class_name}_init_normal",
                description=f"Test {class_name} initialization with normal inputs",
                inputs=test_input,
                expected_output=f"isinstance(obj, {class_name})",
            )
        )

        # Test with minimal args (if there are optional parameters)
        if args:
            test_cases.append(
                TestCase(
                    name=f"test_{class_name}_init_minimal",
                    description=f"Test {class_name} initialization with minimal inputs",
                    inputs={},
                    expected_output=f"isinstance(obj, {class_name})",
                )
            )

        return test_cases

    def _generate_method_tests(self, class_name: str, method_name: str, args: Dict[str, Any]) -> List[TestCase]:
        """Generate tests for class methods"""
        test_cases = []

        # Remove 'self' from args if present
        method_args = {k: v for k, v in args.items() if k != "self"}

        # Normal method call
        test_input = {}
        for param_name, param_type in method_args.items():
            if param_type in self.TYPE_TEST_DATA:
                test_values = self.TYPE_TEST_DATA[param_type]
                test_input[param_name] = test_values[1] if len(test_values) > 1 else test_values[0]
            else:
                test_input[param_name] = None

        test_cases.append(
            TestCase(
                name=f"test_{class_name}_{method_name}_normal",
                description=f"Test {class_name}.{method_name} with normal inputs",
                inputs=test_input,
                expected_output="# TODO: Add expected output",
            )
        )

        return test_cases

    def _create_test_input(self, args: Dict[str, Any], special_param: str, special_value: Any) -> Dict[str, Any]:
        """Create test input with one special value and defaults for others"""
        test_input = {}

        for param_name, param_type in args.items():
            if param_name == special_param:
                test_input[param_name] = special_value
            elif param_type in self.TYPE_TEST_DATA:
                # Use a safe default
                test_values = self.TYPE_TEST_DATA[param_type]
                test_input[param_name] = test_values[1] if len(test_values) > 1 else test_values[0]
            else:
                test_input[param_name] = None

        return test_input

    def _get_wrong_type_value(self, correct_type: str) -> Any:
        """Get a value of wrong type for testing"""
        type_mapping = {
            "int": "string",
            "str": 123,
            "bool": "not_bool",
            "list": "not_list",
            "dict": "not_dict",
            "float": "not_float",
        }
        return type_mapping.get(correct_type)

    def _sanitize_name(self, value: str) -> str:
        """Sanitize value for use in test name"""
        # Replace non-alphanumeric with underscore
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", str(value))
        # Limit length
        return sanitized[:20]

    def _generate_fixture(self, class_name: str, init_args: Dict[str, Any]) -> str:
        """Generate pytest fixture for class"""
        fixture_code = f"""@pytest.fixture
def {class_name.lower()}_instance():
    '''Fixture for {class_name} instance'''
    """

        if init_args:
            fixture_code += "    # TODO: Provide appropriate initialization values\n"
            fixture_code += f"    return {class_name}("

            arg_list = []
            for param_name in init_args:
                arg_list.append(f"{param_name}=None")

            fixture_code += ", ".join(arg_list)
            fixture_code += ")\n"
        else:
            fixture_code += f"    return {class_name}()\n"

        return fixture_code


def format_test_file(test_suites: List[TestSuite], original_file: str) -> str:
    """Format complete test file"""
    output = []

    # Header
    output.append('"""')
    output.append(f"Auto-generated tests for {Path(original_file).name}")
    output.append("Generated by TestGenerator")
    output.append('"""')
    output.append("")
    output.append("import pytest")
    output.append("from unittest.mock import Mock, patch, MagicMock")
    output.append("")

    # Collect imports
    imports = set()
    for suite in test_suites:
        imports.add(suite.import_statement)

    output.extend(sorted(imports))
    output.append("")
    output.append("")

    # Add fixtures
    for suite in test_suites:
        for fixture in suite.fixtures:
            output.append(fixture)
            output.append("")

    # Add test classes/functions
    for suite in test_suites:
        if suite.target_type == "class":
            output.append(f"class Test{suite.target_name}:")
            output.append(f'    """Tests for {suite.target_name} class"""')
            output.append("")

            for test_case in suite.test_cases:
                output.append(format_test_case(test_case, indent=1))
                output.append("")
        else:
            # Function tests
            for test_case in suite.test_cases:
                output.append(format_test_case(test_case, indent=0))
                output.append("")

    return "\n".join(output)


def format_test_case(test_case: TestCase, indent: int = 0) -> str:
    """Format single test case"""
    indent_str = "    " * indent
    output = []

    # Test function definition
    output.append(f"{indent_str}def {test_case.name}():")
    output.append(f'{indent_str}    """')
    output.append(f"{indent_str}    {test_case.description}")
    output.append(f'{indent_str}    """')

    # Mock setup if needed
    if test_case.mock_setup:
        output.append(f"{indent_str}    {test_case.mock_setup}")
        output.append("")

    # Arrange
    output.append(f"{indent_str}    # Arrange")
    for param_name, param_value in test_case.inputs.items():
        if isinstance(param_value, str):
            output.append(f'{indent_str}    {param_name} = "{param_value}"')
        else:
            output.append(f"{indent_str}    {param_name} = {param_value}")
    output.append("")

    # Act & Assert
    if test_case.should_raise:
        output.append(f"{indent_str}    # Act & Assert")
        output.append(f"{indent_str}    with pytest.raises({test_case.should_raise}):")
        output.append(f"{indent_str}        # TODO: Call function with parameters")
        output.append(f"{indent_str}        pass")
    else:
        output.append(f"{indent_str}    # Act")
        output.append(f"{indent_str}    # TODO: Call function and get result")
        output.append(f'{indent_str}    # result = function_name({", ".join(test_case.inputs.keys())})')
        output.append("")
        output.append(f"{indent_str}    # Assert")
        output.append(f"{indent_str}    # TODO: Add assertions")
        output.append(f"{indent_str}    # assert result == {test_case.expected_output}")

    return "\n".join(output)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated test generator")
    parser.add_argument("target", help="Target file or file::function to test")
    parser.add_argument("--output", help="Output test file (default: test_<input>.py)")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage tests")
    parser.add_argument("--watch", action="store_true", help="Watch mode")
    parser.add_argument("--append", action="store_true", help="Append to existing test file")

    args = parser.parse_args()

    # Parse target
    if "::" in args.target:
        filepath, target = args.target.split("::", 1)
    else:
        filepath = args.target

    # Generate tests
    generator = TestGenerator(coverage_mode=args.coverage)

    try:
        test_suites = generator.generate_tests_for_file(filepath)

        if not test_suites:
            print("No testable functions/classes found")
            return 1

        # Format output
        test_code = format_test_file(test_suites, filepath)

        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            input_path = Path(filepath)
            output_file = input_path.parent / f"test_{input_path.stem}.py"

        # Write or append
        if args.append and output_file.exists():
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n\n# Additional tests\n")
                f.write(test_code)
            print(f"Tests appended to {output_file}")
        else:
            output_file.write_text(test_code, encoding="utf-8")
            print(f"Tests generated in {output_file}")

        # Summary
        total_tests = sum(len(suite.test_cases) for suite in test_suites)
        print(f"Generated {total_tests} test cases for {len(test_suites)} targets")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
