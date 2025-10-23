# PromptCompressor + TaskExecutor 통합 계획

**생성일**: 2025-10-24
**목적**: 자동 프롬프트 압축을 통한 토큰 절감 (30-50%)

---

## 1. 통합 목표

### 핵심 가치
- **자동화**: 사용자 수동 개입 없이 프롬프트 압축
- **투명성**: 압축 전/후 통계 자동 기록
- **학습**: 성공 패턴 자동 학습 및 개선

### 성공 지표
- ✅ 토큰 30-50% 절감
- ✅ 사용자 개입 0%
- ✅ 압축 성공률 추적
- ✅ YAML 기반 설정 (P1 준수)

---

## 2. 통합 아키텍처

### 2.1 현재 구조

```
YAML Contract
    ↓
TaskExecutor.execute_contract()
    ↓
Commands Execution
    ↓
Evidence Collection
```

### 2.2 통합 후 구조

```
YAML Contract
    ↓
TaskExecutor.execute_contract()
    ↓
[NEW] Prompt Extraction & Compression
    ↓
Commands Execution (compressed prompts)
    ↓
[NEW] Compression Statistics
    ↓
Evidence Collection + Compression Report
```

---

## 3. YAML 계약서 확장

### 3.1 새로운 섹션: `prompt_optimization`

```yaml
task_id: FEAT-2025-10-24-02
title: Example Task with Prompt Compression

# NEW: Prompt optimization configuration
prompt_optimization:
  enabled: true
  compression_level: medium  # light, medium, aggressive
  auto_learn: true           # Learn from successful compressions
  report_path: RUNS/{task_id}/compression_report.json

# Existing: Commands with prompts
commands:
  - id: generate-code
    exec:
      cmd: python
      args:
        - scripts/ai_generator.py
        - --prompt
        - "Please implement the authentication feature for the web application with proper error handling"
    # AI 프롬프트가 포함된 명령어

# Existing: Evidence collection
evidence:
  - "RUNS/{task_id}/*.json"
```

### 3.2 하위 호환성

```yaml
# If prompt_optimization is not specified:
# - Compression disabled (backward compatible)
# - No changes to existing behavior
```

---

## 4. 구현 설계

### 4.1 핵심 함수

#### `extract_prompts(contract: dict) -> List[PromptLocation]`

```python
@dataclass
class PromptLocation:
    """Prompt location in YAML contract"""
    command_id: str
    arg_index: int
    original_prompt: str
    context: str  # --prompt, --message, etc.

def extract_prompts(contract: dict) -> List[PromptLocation]:
    """
    Extract AI prompts from YAML contract.

    Detection strategy:
    1. Look for --prompt, --message, -m flags
    2. Look for common AI-related arguments
    3. Heuristic: Long text (>50 chars) after AI flags

    Returns:
        List of prompt locations with context
    """
    prompts = []

    for cmd in contract.get("commands", []):
        args = cmd.get("exec", {}).get("args", [])

        for i, arg in enumerate(args):
            # Check if this is a prompt flag
            if arg in ["--prompt", "--message", "-m", "--text"]:
                # Next argument is the prompt
                if i + 1 < len(args):
                    prompts.append(PromptLocation(
                        command_id=cmd["id"],
                        arg_index=i + 1,
                        original_prompt=args[i + 1],
                        context=arg
                    ))

    return prompts
```

#### `apply_compression(contract: dict, config: dict) -> CompressionResult`

```python
def apply_compression(contract: dict, config: dict) -> dict:
    """
    Apply prompt compression to YAML contract.

    Args:
        contract: Original YAML contract
        config: Compression configuration

    Returns:
        Modified contract with compressed prompts
    """
    if not config.get("enabled", False):
        return contract, []

    compressor = PromptCompressor(
        compression_level=config.get("compression_level", "medium")
    )

    prompts = extract_prompts(contract)
    compression_stats = []

    # Compress each prompt
    for loc in prompts:
        result = compressor.compress(loc.original_prompt)

        # Replace in contract
        contract["commands"][loc.command_id]["exec"]["args"][loc.arg_index] = result.compressed

        # Track statistics
        compression_stats.append({
            "command_id": loc.command_id,
            "context": loc.context,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "savings_pct": result.savings_pct,
            "rules_applied": result.compression_rules
        })

    return contract, compression_stats
```

### 4.2 통합 지점

**파일**: `scripts/task_executor.py`
**함수**: `execute_contract(contract_path: str, mode: str = "execute")`

```python
def execute_contract(contract_path: str, mode: str = "execute"):
    """Execute task contract (MODIFIED)"""
    root = Path(".").resolve()
    contract = yaml.safe_load(Path(contract_path).read_text(encoding="utf-8"))

    # [NEW] Step 1.5: Prompt compression (after loading, before execution)
    compression_config = contract.get("prompt_optimization", {})
    if compression_config.get("enabled", False):
        contract, compression_stats = apply_compression(contract, compression_config)

        print(f"\n[COMPRESSION] Prompt optimization enabled")
        print(f"   Level: {compression_config.get('compression_level', 'medium')}")
        print(f"   Prompts compressed: {len(compression_stats)}")

        total_savings = sum(s["savings_pct"] for s in compression_stats) / len(compression_stats)
        print(f"   Average savings: {total_savings:.1f}%")

    # [EXISTING] Continue with normal execution
    task_id = contract["task_id"]
    runs_dir = root / "RUNS" / task_id
    # ... rest of the function
```

---

## 5. 테스트 계획

### 5.1 단위 테스트

```python
# tests/test_prompt_integration.py

class TestPromptExtraction:
    def test_extract_simple_prompt(self):
        contract = {
            "commands": [{
                "id": "cmd1",
                "exec": {
                    "cmd": "python",
                    "args": ["script.py", "--prompt", "Test prompt"]
                }
            }]
        }

        prompts = extract_prompts(contract)
        assert len(prompts) == 1
        assert prompts[0].original_prompt == "Test prompt"

    def test_extract_multiple_prompts(self):
        # Test multiple prompts in different commands

    def test_no_prompts(self):
        # Test contract without prompts


class TestCompressionApplication:
    def test_apply_compression_enabled(self):
        # Test compression when enabled

    def test_apply_compression_disabled(self):
        # Test backward compatibility

    def test_compression_statistics(self):
        # Test statistics collection
```

### 5.2 통합 테스트

```python
class TestTaskExecutorIntegration:
    def test_execute_with_compression(self):
        """Test full execution with prompt compression"""
        # Create test YAML with prompt_optimization
        # Execute task
        # Verify prompts were compressed
        # Verify statistics were recorded

    def test_backward_compatibility(self):
        """Test that old YAMLs still work"""
        # Use existing YAML without prompt_optimization
        # Should execute normally without compression
```

---

## 6. 문서 업데이트

### 6.1 YAML Template 업데이트

**파일**: `TASKS/TEMPLATE.yaml`

```yaml
# Add new section
prompt_optimization:
  enabled: false  # Set to true to enable
  compression_level: medium  # light, medium, aggressive
  auto_learn: true
  report_path: RUNS/{task_id}/compression_report.json
```

### 6.2 README 업데이트

**섹션 추가**: "Prompt Optimization"

```markdown
## Prompt Optimization (NEW)

Automatically compress AI prompts to reduce token usage by 30-50%.

### Enable in YAML

Add to your task contract:

prompt_optimization:
  enabled: true
  compression_level: medium  # light, medium, aggressive

### Results

- Automatic 30-50% token reduction
- Compression statistics in RUNS/{task_id}/compression_report.json
- Learning from successful compressions
```

---

## 7. 구현 체크리스트

### Phase 1: Core Integration (2시간)
- [ ] `extract_prompts()` 구현
- [ ] `apply_compression()` 구현
- [ ] `execute_contract()` 통합
- [ ] 압축 통계 수집

### Phase 2: Testing (1시간)
- [ ] 단위 테스트 작성 (8개)
- [ ] 통합 테스트 작성 (4개)
- [ ] 전체 테스트 통과 확인

### Phase 3: Documentation (30분)
- [ ] TEMPLATE.yaml 업데이트
- [ ] README 업데이트
- [ ] 통합 가이드 작성

---

## 8. 예상 효과

### 8.1 토큰 절감

**Before**:
```yaml
commands:
  - exec:
      args:
        - --prompt
        - "Please implement the authentication feature for the web application with proper error handling and validation"
# Token count: 18
```

**After** (자동 압축):
```yaml
# Internal transformation
args:
  - --prompt
  - "implement auth feature web app error handling val"
# Token count: 9
# Savings: 50%
```

### 8.2 비용 절감

**월간 사용 시나리오**:
- API 호출: 1,000회/월
- 평균 프롬프트: 100 tokens
- 압축률: 40%
- 토큰 가격: $0.01/1K tokens

**절감 효과**:
```
Before: 1,000 * 100 * $0.01/1K = $1.00/month
After:  1,000 * 60 * $0.01/1K = $0.60/month
Savings: $0.40/month (40%)
```

**연간**: $4.80 절감 (프로젝트 규모에 따라 $50-500)

---

## 9. 위험 및 완화

### 9.1 의미 유실 위험

**위험**: 압축 시 의미 왜곡
**완화**:
- 검증된 압축기 사용 (94.6% 정보 보존)
- 보수적 기본 설정 (medium level)
- 사용자 설정 가능 (light/medium/aggressive)

### 9.2 하위 호환성

**위험**: 기존 YAML 깨짐
**완화**:
- `prompt_optimization.enabled: false` 기본값
- 명시적 활성화 필요
- 기존 YAML은 변경 없음

### 9.3 성능 영향

**위험**: 압축으로 실행 시간 증가
**완화**:
- 압축 시간: <100ms (사전 컴파일 덕분)
- 전체 실행 시간 대비 무시 가능
- 토큰 절감 효과가 훨씬 큼

---

## 10. 다음 단계

1. ✅ **설계 완료** (this document)
2. ⏳ **구현 시작** (extract_prompts)
3. ⏳ **테스트 작성**
4. ⏳ **문서 업데이트**
5. ⏳ **커밋 및 배포**

---

**계획 완료**: 2025-10-24
**예상 구현 시간**: 2-3시간
**예상 ROI**: 300% (토큰 절감 + 자동화)
