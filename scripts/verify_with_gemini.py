"""
Gemini API를 사용한 v1.1.0 크로스 검증
Trust Score 8.0+ 패턴 적용 정확성 및 버그 탐지
"""

import os
from pathlib import Path
import google.generativeai as genai


def read_file(filepath: Path) -> str:
    """파일 읽기"""
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        return f"[ERROR reading {filepath}: {e}]"


def analyze_with_gemini(api_key: str):
    """Gemini로 v1.1.0 검증"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # 분석할 파일들
    root = Path(__file__).parent.parent
    files = {
        "enhanced_task_executor.py": root / "scripts" / "enhanced_task_executor.py",
        "project_steering.py": root / "scripts" / "project_steering.py",
        "constitutional_guards.py": root / "scripts" / "constitutional_guards.py",
        "automatic_evidence_tracker.py": root / "scripts" / "automatic_evidence_tracker.py",
        "context_aware_loader.py": root / "scripts" / "context_aware_loader.py",
    }

    # 코드 읽기
    code_contents = {}
    for name, path in files.items():
        code_contents[name] = read_file(path)

    # Gemini 분석 프롬프트
    prompt = f"""Analyze this Evidence-Based Development framework (v1.1.0) for production readiness.

**Context**:
- Integrates Trust Score 8.0+ validated patterns
- 71/71 tests passing (100%)
- Implements:
  - Project Steering (cc-sdd 8.3)
  - Guard Clauses (Hexagon 7.6)
  - Automatic Evidence (GrowthBook 8.0)
  - Context-Aware Loader (Plaesy/cc-sdd 8.3)
- Goal: 50-60% workflow improvement

**Files to Analyze**:

1. enhanced_task_executor.py (v1.1.0 integration):
```python
{code_contents['enhanced_task_executor.py'][:3000]}
... [truncated for brevity]
```

2. project_steering.py:
```python
{code_contents['project_steering.py'][:2000]}
```

3. constitutional_guards.py:
```python
{code_contents['constitutional_guards.py'][:2000]}
```

4. automatic_evidence_tracker.py:
```python
{code_contents['automatic_evidence_tracker.py'][:2000]}
```

5. context_aware_loader.py:
```python
{code_contents['context_aware_loader.py'][:2000]}
```

**Analysis Tasks**:

1. **Trust Score Pattern Validation**:
   - Is cc-sdd Trust 8.3 pattern correctly applied in project_steering.py and context_aware_loader.py?
   - Is Hexagon Trust 7.6 guard clause pattern properly implemented?
   - Is GrowthBook Trust 8.0 evidence tracking pattern accurate?

2. **Integration Logic Verification**:
   - Is enhanced_task_executor.py integrating all 4 components correctly?
   - Are there initialization order issues?
   - Are there state management conflicts?

3. **Bug Detection**:
   - Null pointer exceptions?
   - Race conditions?
   - Resource leaks?
   - Edge cases not covered by tests?

4. **Performance Concerns**:
   - O(n²) algorithms?
   - Memory leaks?
   - Unnecessary blocking operations?

5. **Security Issues**:
   - Path traversal vulnerabilities?
   - Injection risks?
   - Insecure defaults?

**Output Format**:
```markdown
# Gemini Analysis Report - v1.1.0

## Overall Assessment
[PRODUCTION READY / NEEDS WORK / CRITICAL ISSUES]

## Trust Score Pattern Validation
### cc-sdd (Trust 8.3)
- [OK] Correct / [FAIL] Issues: [details]

### Hexagon (Trust 7.6)
- [OK] Correct / [FAIL] Issues: [details]

### GrowthBook (Trust 8.0)
- [OK] Correct / [FAIL] Issues: [details]

## Critical Bugs (Must Fix)
[List with file:line]

## Security Issues
[List with severity]

## Performance Concerns
[List with impact estimate]

## Untested Edge Cases
[List with test recommendations]

## Integration Issues
[List with solutions]

## Recommendations
[Priority-ranked action items]
```

**Focus**: Be thorough but concise. Flag only real issues, not style preferences."""

    print("🤖 Gemini 분석 시작...")
    print(f"[STATUS] 분석 대상: {len(files)} 파일")
    print("⏳ 처리 중...\n")

    try:
        response = model.generate_content(prompt)
        report = response.text

        # 리포트 저장
        output_file = root / "reports" / "gemini_verification_v1.1.0.md"
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(report, encoding="utf-8")

        print("[OK] 분석 완료!")
        print(f"[INFO] 리포트: {output_file}\n")
        print("=" * 60)
        print(report)
        print("=" * 60)

        return report

    except Exception as e:
        print(f"[FAIL] 오류 발생: {e}")
        return None


def main():
    """메인 실행"""
    print("\n" + "=" * 60)
    print("Gemini API v1.1.0 검증 스크립트")
    print("=" * 60 + "\n")

    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] 오류: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("Windows: set GEMINI_API_KEY=your_api_key_here")
        print("또는 .env 파일에 추가\n")
        return

    analyze_with_gemini(api_key)


if __name__ == "__main__":
    main()
