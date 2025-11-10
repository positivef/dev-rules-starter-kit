#!/usr/bin/env python3
"""Enhanced Test Generator - Automated test skeleton generation via AST analysis.

Analyzes Python source files to detect untested functions and generates
pytest-compatible test skeletons with type-hint based test cases.

Features:
- AST-based function detection
- Type hint analysis for test case suggestions
- Pytest template generation
- Integration with existing test files
- CLI interface for batch generation

Constitutional Compliance:
- P8: Test-First Development (generates tests to enforce TDD)
- P2: Evidence-Based (logs generation activity)

Usage:
    python scripts/test_generator_enhanced.py <source_file.py>
    python scripts/test_generator_enhanced.py --analyze <source_file.py>
    python scripts/test_generator_enhanced.py --output tests/test_output.py
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FunctionInfo:
    """Information about a function extracted from AST."""

    name: str
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    is_async: bool
    line_number: int
    type_hints: Dict[str, str]


class EnhancedTestGenerator:
    """Generate test skeletons from Python source files using AST analysis."""

    def __init__(self, source_file: Path):
        """Initialize test generator.

        Args:
            source_file: Path to Python source file to analyze
        """
        self.source_file = source_file
        self.module_name = source_file.stem
        self.functions: List[FunctionInfo] = []

    def analyze_source(self) -> List[FunctionInfo]:
        """Analyze source file using AST to extract function information.

        Returns:
            List of FunctionInfo objects for all functions in the file
        """
        source_code = self.source_file.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in {self.source_file}: {e}")
            return []

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private functions (but include __init__)
                if node.name.startswith("_") and node.name != "__init__":
                    continue

                # Extract function information
                func_info = self._extract_function_info(node)
                functions.append(func_info)

        self.functions = functions
        return functions

    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract detailed information from a function node.

        Args:
            node: AST FunctionDef node

        Returns:
            FunctionInfo object with extracted details
        """
        # Extract arguments
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        # Extract type hints
        type_hints = {}
        for arg in node.args.args:
            if arg.annotation:
                type_hints[arg.arg] = ast.unparse(arg.annotation)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Extract docstring
        docstring = ast.get_docstring(node)

        return FunctionInfo(
            name=node.name,
            args=args,
            return_type=return_type,
            docstring=docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            line_number=node.lineno,
            type_hints=type_hints,
        )

    def suggest_test_cases(self, func: FunctionInfo) -> List[str]:
        """Suggest test cases based on function signature and type hints.

        Args:
            func: FunctionInfo object

        Returns:
            List of suggested test case descriptions
        """
        test_cases = []

        # Basic test cases
        test_cases.append(f"test_{func.name}_basic")

        # Type-based test cases
        for arg_name, arg_type in func.type_hints.items():
            if "int" in arg_type.lower():
                test_cases.append(f"test_{func.name}_with_zero_{arg_name}")
                test_cases.append(f"test_{func.name}_with_negative_{arg_name}")
            elif "str" in arg_type.lower():
                test_cases.append(f"test_{func.name}_with_empty_{arg_name}")
            elif "list" in arg_type.lower() or "dict" in arg_type.lower():
                test_cases.append(f"test_{func.name}_with_empty_{arg_name}")
            elif "bool" in arg_type.lower():
                test_cases.append(f"test_{func.name}_with_true_{arg_name}")
                test_cases.append(f"test_{func.name}_with_false_{arg_name}")

        # Return type based tests
        if func.return_type:
            if "None" in func.return_type:
                test_cases.append(f"test_{func.name}_returns_none")
            elif "bool" in func.return_type.lower():
                test_cases.append(f"test_{func.name}_returns_true")
                test_cases.append(f"test_{func.name}_returns_false")

        # Error handling tests
        test_cases.append(f"test_{func.name}_with_invalid_input")

        # Limit to reasonable number
        return test_cases[:5]

    def generate_test_skeleton(self, func: FunctionInfo) -> str:
        """Generate pytest test skeleton for a function.

        Args:
            func: FunctionInfo object

        Returns:
            String containing pytest test code
        """
        lines = []

        # Generate test cases
        suggested_tests = self.suggest_test_cases(func)

        for test_case in suggested_tests:
            # Test function definition
            if func.is_async:
                lines.append(f"async def {test_case}():")
            else:
                lines.append(f"def {test_case}():")

            # Docstring
            lines.append(f'    """Test {func.name}."""')

            # TODO placeholder
            lines.append("    # TODO: Implement test")

            # Arrange section
            lines.append("    # Arrange")
            for arg in func.args:
                arg_type = func.type_hints.get(arg, "")
                if "int" in arg_type.lower():
                    lines.append(f"    {arg} = 0  # TODO: Set appropriate value")
                elif "str" in arg_type.lower():
                    lines.append(f'    {arg} = ""  # TODO: Set appropriate value')
                elif "list" in arg_type.lower():
                    lines.append(f"    {arg} = []  # TODO: Set appropriate value")
                elif "dict" in arg_type.lower():
                    lines.append(f"    {arg} = {{}}  # TODO: Set appropriate value")
                else:
                    lines.append(f"    {arg} = None  # TODO: Set appropriate value")

            # Act section
            lines.append("")
            lines.append("    # Act")
            if func.args:
                args_str = ", ".join(func.args)
                lines.append(f"    result = {func.name}({args_str})")
            else:
                lines.append(f"    result = {func.name}()")

            # Assert section
            lines.append("")
            lines.append("    # Assert")
            if func.return_type and "None" not in func.return_type:
                lines.append("    assert result is not None  # TODO: Add specific assertion")
            else:
                lines.append("    # TODO: Add assertions")

            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def generate_test_file(self, existing_tests: Optional[Set[str]] = None) -> str:
        """Generate complete test file with imports and test class.

        Args:
            existing_tests: Set of existing test function names to skip

        Returns:
            String containing complete test file
        """
        existing_tests = existing_tests or set()

        lines = []

        # File header
        lines.append(f'"""Unit tests for {self.module_name}."""')
        lines.append("")
        lines.append("import pytest")
        lines.append("")
        lines.append(f"from {self.module_name} import (")

        # Import all functions
        for func in self.functions:
            lines.append(f"    {func.name},")

        lines.append(")")
        lines.append("")
        lines.append("")

        # Test class
        class_name = "".join(word.capitalize() for word in self.module_name.split("_"))
        lines.append(f"class Test{class_name}:")
        lines.append(f'    """Tests for {self.module_name} module."""')
        lines.append("")

        # Generate tests for each function
        for func in self.functions:
            # Skip if tests already exist
            test_name = f"test_{func.name}"
            if test_name in existing_tests:
                continue

            # Generate test skeleton
            test_code = self.generate_test_skeleton(func)

            # Indent for class
            indented = "\n".join("    " + line if line else "" for line in test_code.split("\n"))
            lines.append(indented)

        # Main block
        lines.append("")
        lines.append("")
        lines.append('if __name__ == "__main__":')
        lines.append('    pytest.main([__file__, "-v"])')
        lines.append("")

        return "\n".join(lines)

    def detect_existing_tests(self, test_file: Path) -> Set[str]:
        """Detect existing test functions in a test file.

        Args:
            test_file: Path to existing test file

        Returns:
            Set of existing test function names
        """
        if not test_file.exists():
            return set()

        try:
            test_code = test_file.read_text(encoding="utf-8")
            tree = ast.parse(test_code)

            test_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_names.add(node.name)

            return test_names

        except Exception:
            return set()

    def generate(self, output_file: Optional[Path] = None) -> Path:
        """Generate test file for the source file.

        Args:
            output_file: Optional output path for test file

        Returns:
            Path to generated test file
        """
        # Analyze source
        self.analyze_source()

        if not self.functions:
            print(f"No testable functions found in {self.source_file}")
            return None

        # Determine output path
        if not output_file:
            test_name = f"test_{self.module_name}.py"
            output_file = self.source_file.parent.parent / "tests" / test_name

        # Check for existing tests
        existing_tests = self.detect_existing_tests(output_file)

        # Generate test file content
        test_content = self.generate_test_file(existing_tests)

        # Write to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(test_content, encoding="utf-8")

        print(f"Generated test file: {output_file}")
        print(f"Functions analyzed: {len(self.functions)}")
        print(f"Existing tests skipped: {len(existing_tests)}")

        return output_file


def main():
    """Main entry point for test generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Test Generator")
    parser.add_argument("source_file", help="Source Python file to analyze")
    parser.add_argument("--analyze", action="store_true", help="Analyze only, don't generate")
    parser.add_argument("--output", type=str, help="Output test file path")

    args = parser.parse_args()

    source_file = Path(args.source_file)
    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        sys.exit(1)

    generator = EnhancedTestGenerator(source_file)

    if args.analyze:
        # Analyze mode
        functions = generator.analyze_source()
        print(f"\nFound {len(functions)} testable functions:")
        for func in functions:
            print(f"  - {func.name}({', '.join(func.args)}) -> {func.return_type or 'None'}")
            suggestions = generator.suggest_test_cases(func)
            print(f"    Suggested tests: {len(suggestions)}")
    else:
        # Generate mode
        output_file = Path(args.output) if args.output else None
        generator.generate(output_file)


if __name__ == "__main__":
    main()
