# DeepAnalyzer User Guide

**Quick Reference for Phase C Week 2 Deep Code Analysis**

## What is DeepAnalyzer?

DeepAnalyzer performs comprehensive code analysis on critical Python files, detecting:
- SOLID principle violations (architecture issues)
- Security anti-patterns (eval, hardcoded secrets, etc.)
- Hallucination risks (TODOs, unverified claims)
- Code complexity issues (long functions, high cyclomatic complexity)

## Quick Start

### Command Line Usage

```bash
# Analyze a single file
python scripts/deep_analyzer.py path/to/file.py

# Validate performance
python scripts/validate_deep_analyzer.py
```

### Programmatic Usage

```python
from scripts.deep_analyzer import DeepAnalyzer
from pathlib import Path

# Create analyzer
analyzer = DeepAnalyzer(mcp_enabled=False)

# Analyze file
result = analyzer.analyze(Path("my_file.py"))

# Check results
print(f"Quality Score: {result.overall_score:.1f}/10.0")
print(f"SOLID Violations: {len(result.solid_violations)}")
print(f"Security Issues: {len(result.security_issues)}")
print(f"Pass Status: {result.passed}")
```

## Understanding Results

### Quality Score (0-10)

**Score Ranges**:
- 9.0-10.0: Excellent code quality
- 7.0-8.9: Good, minor improvements needed
- 5.0-6.9: Fair, several issues to address
- 3.0-4.9: Poor, significant refactoring needed
- 0.0-2.9: Critical issues, requires immediate attention

**Scoring Formula**:
- Start at 10.0
- Ruff violations: -0.2 each (max -2.0)
- SOLID violations: -0.5 each (max -3.0)
- Security issues: -1.0 each (max -4.0)
- Hallucination risks: -0.1 each (max -1.0)

### SOLID Violations

**Single Responsibility Principle (SRP)**:
```python
# Violation: Class with >10 methods
class GodClass:
    def method1(self): pass
    def method2(self): pass
    # ... 11+ methods total

# Fix: Split into focused classes
class UserValidator:
    def validate(self): pass

class UserPersistence:
    def save(self): pass
```

**Dependency Inversion Principle (DIP)**:
```python
# Violation: Concrete dependency in __init__
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete class

# Fix: Use dependency injection
class UserService:
    def __init__(self, db: Database):  # Interface/Protocol
        self.db = db
```

**Complexity Violations**:
```python
# Violation: Long function (>50 lines)
def process_data(data):
    # ... 60 lines of code ...
    pass

# Fix: Extract smaller functions
def process_data(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    return save_data(transformed)
```

### Security Issues

**High Severity**:
- `eval()`: Arbitrary code execution
- `exec()`: Arbitrary code execution
- `pickle.loads()`: Deserialization attacks

**Medium Severity**:
- SQL injection patterns: `execute("... %s")`
- Hardcoded secrets: `api_key = "sk-1234"`
- `shell=True`: Command injection

**Examples**:
```python
# Security Issue: eval
user_input = request.get("data")
result = eval(user_input)  # Dangerous!

# Fix: Use safe alternatives
import ast
result = ast.literal_eval(user_input)  # Only literals

# Security Issue: Hardcoded secret
api_key = "your-secret-key-here"  # Never commit secrets!

# Fix: Use environment variables
import os
api_key = os.environ.get("API_KEY")
```

### Hallucination Risks

**Low Severity Indicators**:
- TODO/FIXME comments
- Absolute claims (always, never, guaranteed)
- Placeholder values (mock, fake, dummy)
- NotImplementedError

**Examples**:
```python
# Hallucination Risk: TODO
def process_data(data):
    # TODO: implement validation
    return data

# Fix: Implement or document properly
def process_data(data):
    """Process data with validation."""
    if not data:
        raise ValueError("Empty data")
    return data

# Hallucination Risk: Absolute claim
def calculate(x):
    # This function always succeeds
    return x * 2

# Fix: Be accurate
def calculate(x):
    """Multiply x by 2. Raises TypeError if x is not numeric."""
    return x * 2
```

## Integration with Dev Assistant

DeepAnalyzer automatically runs when dev_assistant detects a critical file (criticality score ≥0.5).

**Automatic Triggers**:
- Files matching critical patterns (`*_executor.py`, `*_validator.py`)
- Files with critical imports (constitutional_validator, etc.)
- Files with large changes (>100 lines in git diff)
- Files in core directories (scripts/)

**Example Output**:
```
[VERIFY] Running analysis (🔍 DEEP)...
[DEEP MODE] Running comprehensive analysis for enhanced_task_executor.py
[DEEP] Quality score: 7.0/10.0
[DEEP] SOLID violations: 9
  • Line 69: Single Responsibility - Class has 13 methods (max 10)
  • Line 88: Dependency Inversion - Concrete dependency instantiated
[DEEP] Security issues: 0
[DEEP] Hallucination risks: 0
```

## Performance Characteristics

**Expected Performance**:
- Small files (<100 lines): <100ms
- Medium files (200-400 lines): <150ms
- Large files (500+ lines): <200ms
- Complex files (1000+ lines): <500ms

**Performance Tips**:
1. DeepAnalyzer is fast - don't worry about overhead
2. Results are cached by dev_assistant
3. Use FAST_MODE for non-critical files (automatic)

## Troubleshooting

### "Quality score too low"
**Cause**: Multiple violations detected
**Fix**: Address highest severity issues first (Security > SOLID > Ruff)

### "Too many SOLID violations"
**Cause**: Large class with many responsibilities
**Fix**: Refactor into smaller, focused classes

### "Analysis takes too long"
**Cause**: Very large file (>2000 lines)
**Fix**: Consider splitting file or using FAST_MODE

### "False positive detections"
**Cause**: Pattern matching limitations
**Fix**: Report issue or wait for MCP integration for semantic analysis

## Advanced Usage

### Custom Thresholds

```python
from scripts.deep_analyzer import SimpleSolidChecker

# Customize thresholds
checker = SimpleSolidChecker()
checker.MAX_METHODS_PER_CLASS = 15  # Default: 10
checker.MAX_FUNCTION_LINES = 75     # Default: 50
checker.MAX_CYCLOMATIC_COMPLEXITY = 15  # Default: 10
```

### Filtering Results

```python
result = analyzer.analyze(Path("file.py"))

# Get only high severity issues
high_severity = [
    v for v in result.solid_violations
    if v["severity"] == "high"
]

# Get security issues only
security = result.security_issues

# Get specific SOLID principles
srp_violations = [
    v for v in result.solid_violations
    if v["principle"] == "Single Responsibility"
]
```

### Batch Analysis

```python
from pathlib import Path

analyzer = DeepAnalyzer(mcp_enabled=False)
results = []

for file_path in Path("scripts").glob("*.py"):
    result = analyzer.analyze(file_path)
    results.append((file_path.name, result.overall_score))

# Sort by quality score
results.sort(key=lambda x: x[1])
print("Lowest quality files:")
for name, score in results[:5]:
    print(f"  {name}: {score:.1f}/10.0")
```

## Best Practices

### 1. Run Before Committing
```bash
# Analyze changed files
git diff --name-only | grep "\.py$" | xargs -I {} python scripts/deep_analyzer.py {}
```

### 2. Set Quality Gates
```python
result = analyzer.analyze(file_path)
if result.overall_score < 7.0:
    raise ValueError(f"Quality score too low: {result.overall_score:.1f}")
```

### 3. Focus on High-Impact Issues
Priority order:
1. Security issues (immediate fix)
2. High severity SOLID violations (refactor soon)
3. Ruff violations (fix when convenient)
4. Hallucination risks (document or implement)

### 4. Incremental Improvement
Don't try to fix everything at once:
1. Fix all security issues
2. Address critical SOLID violations
3. Clean up Ruff violations
4. Document or implement TODOs

## Future Enhancements

**MCP Integration (Coming Soon)**:
```python
# When MCP Sequential-Thinking is available
analyzer = DeepAnalyzer(mcp_enabled=True, mcp_timeout=5.0)
result = analyzer.analyze(file_path)

if result.mcp_used:
    print("Deep semantic analysis performed")
else:
    print("Fallback AST analysis used")
```

**Benefits of MCP**:
- Deeper semantic understanding
- Cross-file dependency analysis
- More accurate SOLID violations
- Context-aware security checks

## FAQ

**Q: Why is my quality score low even with no Ruff errors?**
A: Quality score includes SOLID violations, security issues, and other factors beyond syntax.

**Q: How do I improve my quality score?**
A: Focus on security issues first (highest impact), then SOLID violations, then style.

**Q: Is DeepAnalyzer slow?**
A: No, average analysis time is ~70ms, much faster than the 5s target.

**Q: Can I disable certain checks?**
A: Currently no, but you can filter results programmatically after analysis.

**Q: What's the difference between FAST_MODE and DEEP_MODE?**
A: FAST_MODE uses only Ruff (~50ms), DEEP_MODE adds SOLID/security/hallucination checks (~70ms).

**Q: When should I use DeepAnalyzer vs Ruff?**
A: DeepAnalyzer is automatically used for critical files. For quick checks, use Ruff directly.

## Support

For issues or questions:
1. Check test suite: `pytest tests/test_deep_analyzer.py -v`
2. Run validation: `python scripts/validate_deep_analyzer.py`
3. Review implementation: `PHASE_C_WEEK_2_IMPLEMENTATION.md`

## Summary

DeepAnalyzer provides comprehensive code analysis with:
- ✅ Fast performance (<100ms average)
- ✅ Multiple analysis levels (SOLID, security, hallucination)
- ✅ Clear quality scoring (0-10 scale)
- ✅ Actionable violations with line numbers
- ✅ Seamless integration with dev_assistant

Use it to maintain high code quality and catch issues before they become problems.
