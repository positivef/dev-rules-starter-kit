# Testing Strategy

**Dev Rules Starter Kit의 Hybrid Testing 전략**

## Overview

이 프로젝트는 **Hybrid Testing Strategy**를 사용합니다:
- **Integration Tests**: End-to-end 기능 검증
- **Unit Tests**: Function-level 검증 및 coverage 측정

각 테스트 유형은 고유한 목적과 가치를 가지며, 함께 사용할 때 최대 효과를 발휘합니다.

## Test Suite Composition

```
전체 테스트: ~852개
├─ Integration Tests: ~760개 (subprocess-based)
│  ├─ Purpose: Real-world functionality validation
│  ├─ Method: subprocess.run() execution
│  ├─ Coverage: Minimal (subprocess limitation)
│  └─ Value: End-to-end verification ★★★★★
│
└─ Unit Tests: 92개 (import-based)
   ├─ Purpose: Function-level validation
   ├─ Method: Direct function imports
   ├─ Coverage: 5% (measurable)
   └─ Value: Fast feedback, precise metrics ★★★★☆

Combined Value: ★★★★★ (최고)
```

## Integration Tests (~760 tests)

### 목적
- 실제 프로세스 실행 검증
- CLI 명령어 동작 확인
- End-to-end 기능 테스트

### 방법
```python
# subprocess를 통한 실행
result = subprocess.run(
    ["python", "scripts/task_executor.py", "TASKS/test.yaml"],
    capture_output=True,
    text=True
)
assert result.returncode == 0
```

### 특징
- ✅ **Real-world validation**: 실제 사용 시나리오 검증
- ✅ **Comprehensive**: 전체 시스템 동작 확인
- ❌ **No coverage**: subprocess는 coverage 측정 불가
- ⚠️ **Slower**: 프로세스 생성 오버헤드 (~20초)

### 사용 시기
- CLI 명령어 테스트
- 전체 워크플로우 검증
- 실제 파일 시스템 작업 검증
- 환경 변수 및 설정 테스트

### 예시
```python
def test_task_executor_runs_successfully():
    """TaskExecutor가 YAML 계약서를 실행한다"""
    result = subprocess.run(
        ["python", "scripts/task_executor.py", "TASKS/example.yaml"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
```

## Unit Tests (92 tests)

### 목적
- Function-level 검증
- Code coverage 측정
- 빠른 피드백 루프

### 방법
```python
# Direct import를 통한 테스트
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from task_executor import plan_hash, sha256_file

def test_plan_hash_consistent():
    contract = {"task_id": "TEST-001"}
    hash1 = plan_hash(contract)
    hash2 = plan_hash(contract)
    assert hash1 == hash2
```

### 특징
- ✅ **Coverage measurement**: pytest-cov로 측정 가능
- ✅ **Fast**: 함수 직접 호출 (~7.71초 for 92 tests)
- ✅ **Precise**: 특정 함수/클래스만 테스트
- ⚠️ **Limited scope**: 통합 동작 검증 불가

### 사용 시기
- 순수 함수 테스트
- 데이터 변환 로직 검증
- 알고리즘 정확성 확인
- Coverage 개선

### 예시
```python
def test_sha256_file_with_text_content(tmp_path):
    """SHA256 파일 해시가 일관성 있게 계산된다"""
    from task_executor import sha256_file

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")

    hash1 = sha256_file(test_file)
    hash2 = sha256_file(test_file)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 = 64 hex chars
```

## Coverage Strategy

### 현재 달성 (Phase 4)
```
Total Coverage: 5% (883/18,219 lines)

Core Modules:
├─ task_executor.py: 46% (203/445 lines)
│  └─ 52 tests covering 19/21 functions
├─ constitutional_validator.py: 90% (150/167 lines)
│  └─ 18 tests covering compliance validation
└─ deep_analyzer.py: 56% (113/203 lines)
   └─ 22 tests covering SOLID/security/hallucination checks

Execution Time: 7.71s (fast feedback)
Pass Rate: 100% (92/92 tests)
```

### Coverage Philosophy

**P15 Convergence 원칙 적용**:
```
"Good Enough" > "Perfect"

5% deep coverage on critical files
>
15% shallow coverage across all files

ROI: 4시간 투자 → 27배 개선 (0.18% → 5%)
```

### Coverage Goals

| Module Type | Target Coverage | Rationale |
|-------------|----------------|-----------|
| **Core Executors** | 40-50% | 핵심 실행 로직 검증 |
| **Validators** | 80-90% | 품질 게이트 정확성 |
| **Analyzers** | 50-60% | 분석 알고리즘 검증 |
| **Utilities** | 20-30% | 보조 기능만 검증 |
| **Scripts** | 5-10% | CLI wrapper, 낮은 우선순위 |

### Why Not 100% Coverage?

1. **ROI Diminishing Returns**: 15% → 30% = 25시간 추가 필요
2. **P15 Convergence**: "충분히 좋음"에서 멈춤
3. **Integration Tests Sufficiency**: 760개 테스트가 실제 동작 보장
4. **Maintenance Cost**: 과도한 테스트는 리팩토링 비용 증가

## Running Tests

### Integration Tests Only
```bash
# 전체 integration tests
pytest tests/ -v

# 특정 파일
pytest tests/test_task_executor_integration.py -v

# 특정 테스트
pytest tests/ -k "test_executor" -v

# 병렬 실행 (빠름)
pytest tests/ -n auto
```

### Unit Tests Only
```bash
# 전체 unit tests
pytest tests/unit/ -v

# Coverage와 함께
pytest tests/unit/ --cov=scripts --cov-report=term-missing

# HTML report 생성
pytest tests/unit/ --cov=scripts --cov-report=html

# JSON report (CI/CD용)
pytest tests/unit/ --cov=scripts --cov-report=json
```

### All Tests (Hybrid)
```bash
# 전체 테스트 + coverage
pytest tests/ --cov=scripts --cov-report=term --cov-report=html

# CI/CD 권장 명령어
pytest tests/ -v --cov=scripts --cov-report=term --cov-report=json --cov-report=html

# 빠른 실패 (첫 에러에서 중단)
pytest tests/ -x

# 실패한 테스트만 재실행
pytest tests/ --lf
```

## Writing Tests

### Integration Test Template
```python
"""Integration tests for [module_name]

Tests the complete workflow using subprocess execution.
"""
import subprocess
from pathlib import Path

def test_module_executes_successfully():
    """[Module]이 정상적으로 실행된다"""
    result = subprocess.run(
        ["python", "scripts/module.py", "--args"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "expected_output" in result.stdout
    assert "ERROR" not in result.stderr
```

### Unit Test Template
```python
"""Unit tests for [module_name]

Tests individual functions with direct imports for coverage.
"""
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest
from module_name import function_to_test

class TestFunctionName:
    """Test [function_name] function"""

    def test_basic_functionality(self):
        """기본 동작이 정확하다"""
        result = function_to_test(input_data)
        assert result == expected_output

    def test_edge_case(self):
        """경계 조건을 올바르게 처리한다"""
        result = function_to_test(edge_case_input)
        assert result == expected_edge_output

    def test_error_handling(self):
        """에러 상황을 적절히 처리한다"""
        with pytest.raises(ExpectedError):
            function_to_test(invalid_input)
```

## Test Organization

```
tests/
├─ unit/                          # Unit tests (import-based)
│  ├─ test_task_executor.py      # task_executor.py functions
│  ├─ test_constitutional_validator.py
│  ├─ test_deep_analyzer.py
│  └─ helpers/                    # Test utilities
│     ├─ fixtures.py
│     └─ mocks.py
│
├─ integration/                   # Integration tests (subprocess-based)
│  ├─ test_task_executor_integration.py
│  ├─ test_pipeline_integration.py
│  └─ test_end_to_end.py
│
├─ conftest.py                    # Shared fixtures
└─ pytest.ini                     # Pytest configuration
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        pytest tests/ -v \
          --cov=scripts \
          --cov-report=term \
          --cov-report=json \
          --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.json
        fail_ci_if_error: true
```

### Coverage Gates
```yaml
# .coveragerc
[run]
source = scripts/

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:

precision = 2
show_missing = True

[html]
directory = htmlcov
```

## Best Practices

### 1. Test Naming
```python
# Good: 설명적이고 명확한 이름
def test_plan_hash_consistent_for_same_contract():
    """동일한 계약서는 항상 같은 해시를 생성한다"""

# Bad: 모호한 이름
def test_hash():
    """테스트"""
```

### 2. Test Independence
```python
# Good: 각 테스트가 독립적
def test_function_a(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("data")
    assert function_a(file) == expected

def test_function_b(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("data")
    assert function_b(file) == expected

# Bad: 테스트 간 의존성
shared_state = {}

def test_setup():
    shared_state["data"] = "value"

def test_depends_on_setup():  # ❌ test_setup 먼저 실행 필요
    assert shared_state["data"] == "value"
```

### 3. Clear Assertions
```python
# Good: 명확한 assertion 메시지
def test_coverage_threshold():
    coverage = calculate_coverage()
    assert coverage >= 5.0, f"Coverage {coverage}% below 5% threshold"

# Bad: 불명확한 실패 메시지
def test_coverage():
    assert calculate_coverage() >= 5.0  # 왜 실패했는지 모름
```

### 4. Fixture Usage
```python
# Good: 재사용 가능한 fixtures
@pytest.fixture
def sample_contract():
    return {
        "task_id": "TEST-001",
        "title": "Test Task",
        "commands": [{"exec": ["echo", "test"]}]
    }

def test_with_contract(sample_contract):
    result = validate_contract(sample_contract)
    assert result is True

# Bad: 매번 중복 생성
def test_contract_1():
    contract = {"task_id": "TEST-001", ...}  # 중복

def test_contract_2():
    contract = {"task_id": "TEST-001", ...}  # 중복
```

## Troubleshooting

### Import Errors
```python
# Problem: ModuleNotFoundError: No module named 'task_executor'
# Solution: Add scripts to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
```

### Coverage Not Measured
```bash
# Problem: Coverage shows 0%
# Reason: Using subprocess (integration tests)

# Solution: Use unit tests with direct imports
pytest tests/unit/ --cov=scripts  # ✓ Works

# Integration tests won't show coverage
pytest tests/integration/ --cov=scripts  # Coverage = 0%
```

### Slow Tests
```bash
# Problem: Tests taking too long

# Solution 1: Run unit tests only
pytest tests/unit/ -v  # Fast (~7s)

# Solution 2: Parallel execution
pytest tests/ -n auto  # Use all CPU cores

# Solution 3: Run specific tests
pytest tests/unit/test_task_executor.py::TestPlanHash -v
```

## Metrics & Monitoring

### Current Metrics (Phase 4)
```
Test Count: 852 tests
├─ Integration: 760 tests
└─ Unit: 92 tests

Coverage: 5% (883/18,219 lines)

Execution Time:
├─ Unit tests: 7.71s
├─ Integration tests: ~20s
└─ Total: ~30s

Pass Rate: 100%
```

### Coverage Trends
```bash
# View coverage history
git log --oneline --grep="coverage" | head -10

# Compare coverage between commits
coverage json -o coverage_old.json
# ... make changes ...
coverage json -o coverage_new.json
diff coverage_old.json coverage_new.json
```

## Future Enhancements (Phase 5+)

### Considered for Phase 5
```
1. Mutation Testing
   - Tool: mutmut
   - Purpose: Test quality verification
   - ROI: To be evaluated

2. Performance Benchmarking
   - Tool: pytest-benchmark
   - Purpose: Regression detection
   - ROI: Medium

3. 30% Coverage Target
   - Additional: ~200 tests
   - Time: ~25 hours
   - ROI: To be evaluated (P15 Convergence)
```

### NOT Recommended
```
❌ 100% Coverage: ROI too low, P15 violation
❌ Snapshot Testing: Maintenance cost too high
❌ Visual Regression: Not applicable (CLI tool)
```

## Summary

**Hybrid Testing Strategy = Best of Both Worlds**

- **Integration Tests**: 실제 동작 보장 (760 tests)
- **Unit Tests**: 정확한 측정 가능 (92 tests)
- **Coverage**: 5% (critical files with deep coverage)
- **Execution**: <30s (빠른 피드백)
- **Philosophy**: P15 Convergence ("good enough" > "perfect")

---

**Last Updated**: 2025-11-01 (Phase 4 completion)
**Coverage**: 5% (883/18,219 lines)
**Test Count**: 852 tests (100% pass rate)
