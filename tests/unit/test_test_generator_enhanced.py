"""Unit tests for Enhanced Test Generator.

Tests for AST-based test generation:
- Function detection via AST
- Type hint extraction
- Test case suggestions
- Template generation
- Existing test detection

Constitutional Compliance:
- P8: Test-First Development (testing the generator)
- P2: Evidence-Based (verify generation works)
"""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from test_generator_enhanced import EnhancedTestGenerator, FunctionInfo


class TestFunctionInfo:
    """Tests for FunctionInfo dataclass."""

    def test_function_info_creation(self):
        """Test FunctionInfo creation."""
        func_info = FunctionInfo(
            name="test_func",
            args=["x", "y"],
            return_type="int",
            docstring="Test function",
            is_async=False,
            line_number=10,
            type_hints={"x": "int", "y": "str"},
        )

        assert func_info.name == "test_func"
        assert func_info.args == ["x", "y"]
        assert func_info.return_type == "int"
        assert func_info.docstring == "Test function"
        assert func_info.is_async is False
        assert func_info.line_number == 10
        assert func_info.type_hints == {"x": "int", "y": "str"}


class TestEnhancedTestGenerator:
    """Tests for EnhancedTestGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("test_module.py")
            source_file.write_text("def foo(): pass", encoding="utf-8")

            generator = EnhancedTestGenerator(source_file)

            assert generator.source_file == source_file
            assert generator.module_name == "test_module"
            assert generator.functions == []

    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("module.py")
            source_file.write_text(
                """
def add(x, y):
    \"\"\"Add two numbers.\"\"\"
    return x + y
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(source_file)
            functions = generator.analyze_source()

            assert len(functions) == 1
            assert functions[0].name == "add"
            assert functions[0].args == ["x", "y"]
            assert functions[0].docstring == "Add two numbers."

    def test_analyze_function_with_type_hints(self):
        """Test analyzing function with type hints."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("module.py")
            source_file.write_text(
                """
def add(x: int, y: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return x + y
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(source_file)
            functions = generator.analyze_source()

            assert len(functions) == 1
            func = functions[0]
            assert func.name == "add"
            assert func.type_hints == {"x": "int", "y": "int"}
            assert func.return_type == "int"

    def test_analyze_async_function(self):
        """Test analyzing async function."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("module.py")
            source_file.write_text(
                """
async def fetch_data():
    \"\"\"Fetch data asynchronously.\"\"\"
    return "data"
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(source_file)
            functions = generator.analyze_source()

            assert len(functions) == 1
            assert functions[0].is_async is True

    def test_analyze_skips_private_functions(self):
        """Test that private functions are skipped."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("module.py")
            source_file.write_text(
                """
def public_func():
    pass

def _private_func():
    pass

def __init__(self):
    pass
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(source_file)
            functions = generator.analyze_source()

            # Should include public_func and __init__, but not _private_func
            func_names = [f.name for f in functions]
            assert "public_func" in func_names
            assert "__init__" in func_names
            assert "_private_func" not in func_names

    def test_suggest_test_cases_basic(self):
        """Test basic test case suggestions."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="process",
            args=["data"],
            return_type=None,
            docstring="Process data",
            is_async=False,
            line_number=1,
            type_hints={},
        )

        suggestions = generator.suggest_test_cases(func)

        assert len(suggestions) > 0
        assert "test_process_basic" in suggestions
        assert "test_process_with_invalid_input" in suggestions

    def test_suggest_test_cases_with_int_type(self):
        """Test suggestions for int type hints."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="increment",
            args=["value"],
            return_type="int",
            docstring="Increment value",
            is_async=False,
            line_number=1,
            type_hints={"value": "int"},
        )

        suggestions = generator.suggest_test_cases(func)

        assert "test_increment_with_zero_value" in suggestions
        assert "test_increment_with_negative_value" in suggestions

    def test_suggest_test_cases_with_str_type(self):
        """Test suggestions for str type hints."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="uppercase",
            args=["text"],
            return_type="str",
            docstring="Convert to uppercase",
            is_async=False,
            line_number=1,
            type_hints={"text": "str"},
        )

        suggestions = generator.suggest_test_cases(func)

        assert "test_uppercase_with_empty_text" in suggestions

    def test_suggest_test_cases_with_bool_type(self):
        """Test suggestions for bool type hints."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="is_valid",
            args=["flag"],
            return_type="bool",
            docstring="Check if valid",
            is_async=False,
            line_number=1,
            type_hints={"flag": "bool"},
        )

        suggestions = generator.suggest_test_cases(func)

        assert "test_is_valid_with_true_flag" in suggestions
        assert "test_is_valid_with_false_flag" in suggestions
        assert "test_is_valid_returns_true" in suggestions
        assert "test_is_valid_returns_false" in suggestions

    def test_generate_test_skeleton(self):
        """Test test skeleton generation."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="add",
            args=["x", "y"],
            return_type="int",
            docstring="Add numbers",
            is_async=False,
            line_number=1,
            type_hints={"x": "int", "y": "int"},
        )

        skeleton = generator.generate_test_skeleton(func)

        assert "def test_add" in skeleton
        assert "# Arrange" in skeleton
        assert "# Act" in skeleton
        assert "# Assert" in skeleton
        assert "result = add(x, y)" in skeleton

    def test_generate_test_skeleton_async(self):
        """Test async test skeleton generation."""
        generator = EnhancedTestGenerator(Path("dummy.py"))

        func = FunctionInfo(
            name="fetch",
            args=[],
            return_type="str",
            docstring="Fetch data",
            is_async=True,
            line_number=1,
            type_hints={},
        )

        skeleton = generator.generate_test_skeleton(func)

        assert "async def test_fetch" in skeleton

    def test_detect_existing_tests(self):
        """Test detecting existing test functions."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            test_file = Path("test_module.py")
            test_file.write_text(
                """
def test_add():
    assert 1 + 1 == 2

def test_subtract():
    assert 2 - 1 == 1
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(Path("module.py"))
            existing = generator.detect_existing_tests(test_file)

            assert "test_add" in existing
            assert "test_subtract" in existing
            assert len(existing) == 2

    def test_detect_existing_tests_no_file(self):
        """Test detecting tests when file doesn't exist."""
        generator = EnhancedTestGenerator(Path("module.py"))
        existing = generator.detect_existing_tests(Path("nonexistent.py"))

        assert len(existing) == 0

    def test_generate_test_file(self):
        """Test complete test file generation."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            source_file = Path("module.py")
            source_file.write_text(
                """
def add(x: int, y: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return x + y

def multiply(x: int, y: int) -> int:
    \"\"\"Multiply two numbers.\"\"\"
    return x * y
""",
                encoding="utf-8",
            )

            generator = EnhancedTestGenerator(source_file)
            generator.analyze_source()

            test_content = generator.generate_test_file()

            assert "import pytest" in test_content
            assert "from module import" in test_content
            assert "class TestModule:" in test_content
            assert "def test_add" in test_content
            assert "def test_multiply" in test_content

    def test_generate_test_file_skips_existing(self):
        """Test that existing tests are skipped."""
        generator = EnhancedTestGenerator(Path("module.py"))
        generator.functions = [
            FunctionInfo(
                name="add",
                args=["x", "y"],
                return_type="int",
                docstring="Add",
                is_async=False,
                line_number=1,
                type_hints={"x": "int", "y": "int"},
            ),
            FunctionInfo(
                name="subtract",
                args=["x", "y"],
                return_type="int",
                docstring="Subtract",
                is_async=False,
                line_number=5,
                type_hints={"x": "int", "y": "int"},
            ),
        ]

        existing_tests = {"test_add"}
        test_content = generator.generate_test_file(existing_tests)

        # test_add should be skipped
        assert test_content.count("def test_add") == 0
        # test_subtract should be included
        assert "def test_subtract" in test_content

    def test_generate_creates_output_file(self):
        """Test that generate() creates output file."""
        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create source file
            source_file = Path("module.py")
            source_file.write_text(
                """
def add(x, y):
    return x + y
""",
                encoding="utf-8",
            )

            # Create tests directory
            Path("tests").mkdir()

            # Generate tests
            generator = EnhancedTestGenerator(source_file)
            output_file = generator.generate(Path("tests/test_module.py"))

            assert output_file is not None
            assert output_file.exists()
            assert "test_add" in output_file.read_text(encoding="utf-8")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
