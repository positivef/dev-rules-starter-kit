# SMART EMOJI RULE - Windows P10 Compliance

## Core Principle: Context-Aware Emoji Restriction

**"오류가 발생하는 곳에서만 이모지를 금지한다"**

---

## [CRITICAL] NEVER Use Emojis - 절대 금지 영역

### 1. Python Files (.py)
```python
# [X] NEVER in Python code
print("❌ Failed")          # UnicodeEncodeError
return "✅ Success"         # UnicodeEncodeError
logger.info("🚨 Alert")     # UnicodeEncodeError

# [O] ALWAYS use ASCII alternatives
print("[X] Failed")
return "[OK] Success"
logger.info("[ALERT] Alert")
```

### 2. Console Output / Logging
- print() statements
- logger outputs
- console.log equivalents
- Terminal/CLI outputs

### 3. File Operations without encoding
```python
# [X] DANGEROUS
with open("file.txt", "r") as f:  # System default (cp949)
    content = f.read()

# [O] SAFE
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

---

## [ALLOWED] Safe to Use Emojis - 허용 영역

### 1. Markdown Documentation (.md)
```markdown
# ✅ This is OK in .md files
- 🎯 Target achieved
- ⚡ Performance improved
```
**Reason**: Markdown files are saved as UTF-8 by default

### 2. JSON with UTF-8
```json
{
  "status": "✅ Complete",
  "warning": "⚠️ Check this"
}
```
**Condition**: Must use `ensure_ascii=False` when dumping

### 3. HTML/Web Content
```html
<div>✅ Success message</div>
```
**Reason**: Browsers handle UTF-8 correctly

### 4. Comments in Code (Sometimes)
```python
# ✅ This might work in comments (but avoid for consistency)
```
**Warning**: Can still cause issues in some editors

---

## Decision Matrix

| File Type | Emojis Allowed? | Risk Level | Alternative |
|-----------|----------------|------------|-------------|
| **.py files** | ❌ **NEVER** | HIGH | Use ASCII: [OK], [X], [!] |
| **Console output** | ❌ **NEVER** | HIGH | Use text: PASS, FAIL, WARN |
| **.md files** | ✅ OK | LOW | Can use emojis |
| **.json (UTF-8)** | ✅ OK | LOW | Can use emojis |
| **Web/HTML** | ✅ OK | NONE | Can use emojis |
| **Git commits** | ⚠️ AVOID | MEDIUM | Use conventional: feat:, fix: |
| **.yaml/.yml** | ⚠️ AVOID | MEDIUM | Use ASCII to be safe |

---

## Better Alternatives

### 방안 1: Environment Variable (시스템 레벨 해결)
```bash
# Windows에서 Python UTF-8 강제
set PYTHONIOENCODING=utf-8
# 또는
python -X utf8 script.py
```
**장점**: 근본적 해결
**단점**: 모든 환경에서 설정 필요

### 방안 2: Encoding Wrapper
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
**장점**: 스크립트 레벨 해결
**단점**: 모든 파일에 추가 필요

### 방안 3: ASCII Art (추천)
```python
# Visual indicators without Unicode
INDICATORS = {
    'success': '[OK]',
    'failure': '[X]',
    'warning': '[!]',
    'info': '[i]',
    'target': '[>>]',
    'check': '[v]',
}
```
**장점**: 100% 호환성
**단점**: 시각적 효과 감소

---

## Enforcement Rules

### Pre-commit Check
```python
def check_python_files_for_emojis(filepath):
    """Python 파일에서만 이모지 체크"""
    if not filepath.endswith('.py'):
        return True  # Non-Python files are OK

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for emojis in Python files
    for char in content:
        if ord(char) > 0x1F300:  # Emoji range
            return False
    return True
```

### Quick Reference

```
Python Code:     NO EMOJIS  -> Use [OK], [X], [!]
Console Output:  NO EMOJIS  -> Use text markers
Markdown Docs:   EMOJIS OK  -> Feel free to use
JSON/Web:        EMOJIS OK  -> UTF-8 safe zones
```

---

## Final Rule

**"Python 코드와 콘솔 출력에서만 이모지를 금지한다"**

This is the optimal balance between:
- Safety (no encoding errors)
- Usability (docs can be visual)
- Consistency (clear rules)

Remember: When in doubt, use ASCII!
