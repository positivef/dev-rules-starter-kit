# Implementation Plan: Simple CLI Calculator

**Created**: 2025-10-20
**Tech Stack**: Python 3.10+, argparse, pytest

## Phase -1: Constitutional Gates

### Article I: Library-First (Pass/Fail)
- [X] Feature designed as standalone library? **YES** - calculator module
- [X] Clear module boundaries? **YES** - calc lib + CLI wrapper

### Article II: CLI Interface (Pass/Fail)
- [X] CLI interface planned? **YES** - argparse-based CLI

### Article III: Test-First (Pass/Fail)
- [X] TDD workflow planned? **YES** - tests before implementation
- [X] Tests before implementation? **YES** - see tasks.md

### Article VII: Simplicity (Pass/Fail)
- [X] Using ≤3 projects? **YES** - 1 project only
- [X] No future-proofing? **YES** - MVP only
- [X] No speculative features? **YES** - basic operations only

### Article VIII: Anti-Abstraction (Pass/Fail)
- [X] Using framework directly? **YES** - argparse directly, no wrappers

### Article IX: SDD (Pass/Fail)
- [X] Spec exists and complete? **YES** - spec.md created
- [X] Tech choices justified? **YES** - Python standard library

**Result**: [PASS] ALL GATES PASS

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**:
- argparse (standard library)
- pytest (testing)

**Storage**: N/A (stateless)
**Testing**: pytest
**Target Platform**: Windows, Linux, macOS
**Performance Goals**: < 100ms per operation
**Constraints**: No external dependencies beyond pytest

## Project Structure

```
simple-calc/
├── src/
│   ├── __init__.py
│   ├── calculator.py      # Core calculator logic
│   └── cli.py             # CLI interface
├── tests/
│   ├── test_calculator.py # Unit tests for calculator
│   └── test_cli.py        # Integration tests for CLI
├── setup.py               # Package setup
└── README.md              # Usage documentation
```

## Data Model

### Calculator Class
```python
class Calculator:
    """Simple calculator with basic arithmetic operations."""

    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers."""

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract b from a."""

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers."""

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide a by b. Raises ValueError if b is zero."""
```

## CLI Interface

**Command Format**:
```bash
calc <operation> <num1> <num2>
```

**Operations**: add, subtract, multiply, divide

**Examples**:
```bash
calc add 5 3          # Output: Result: 8
calc divide 10 2      # Output: Result: 5.0
calc --help           # Show help text
```

## Error Handling

1. **Invalid Operation**: Show available operations
2. **Invalid Numbers**: Show "Error: Arguments must be numbers"
3. **Division by Zero**: Show "Error: Division by zero not allowed"
4. **Wrong Argument Count**: Show usage help

## Testing Strategy

### Unit Tests (test_calculator.py)
- Test each operation with valid inputs
- Test division by zero raises ValueError
- Test edge cases (negatives, decimals, large numbers)

### Integration Tests (test_cli.py)
- Test CLI with valid arguments
- Test CLI with invalid arguments
- Test help flag output
- Test error message formatting

## Implementation Phases

See tasks.md for detailed task breakdown:
1. **Setup**: Project structure, dependencies
2. **Tests**: Write tests first (TDD)
3. **Core**: Implement calculator logic
4. **CLI**: Implement command-line interface
5. **Polish**: Documentation, final testing

---

**Ready for**: `/speckit-tasks` or manual task breakdown
