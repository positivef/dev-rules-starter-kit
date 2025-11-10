# Encoding Policy - P10 Windows UTF-8 Compliance

## Rule: ASCII-Only in Python Code

### ✅ ALLOWED (ASCII)
```python
# English comments
"""English docstrings"""
variable_name = "English strings"
log_message = "[OK] Success"
```

### ❌ PROHIBITED (Non-ASCII)
```python
# 한글 주석 ← BLOCKED
"""한글 docstring""" ← BLOCKED
이모지 = "✅" ← BLOCKED
```

## Exception: UI/i18n Files

**Allowed locations for non-ASCII**:
- `i18n/*.json` - Internationalization files
- `locale/*.po` - Translation files
- `*.md` - Documentation (Markdown)
- Git commit messages

**NOT allowed**:
- `*.py` - Python source code
- `*.yaml` - Configuration files (use English keys)
- `*.sh` - Shell scripts

## Git Configuration

### .gitattributes (MANDATORY)
```
# Prevent UTF-8 corruption in Python files
*.py text eol=lf encoding=UTF-8
*.pyi text eol=lf encoding=UTF-8
```

### Git Settings
```bash
# DO NOT use autocrlf=true with UTF-8 files
git config core.autocrlf false  # Or use .gitattributes

# Force UTF-8 encoding
git config core.quotepath false
git config i18n.commitencoding utf-8
git config i18n.logoutputencoding utf-8
```

## Why This Policy?

**Problem**: Windows cp949 encoding crashes on emojis/Korean
**Solution**: ASCII-only in code + UTF-8 in data files
**Benefit**: Cross-platform compatibility (Windows/Linux/Mac)

## Migration Guide

### For Existing Korean Comments
```python
# Before
def calculate():
    """가격을 계산합니다"""  # ← Will be blocked by P10
    
# After (Option 1: Translate)
def calculate():
    """Calculate the price"""
    
# After (Option 2: External i18n)
def calculate():
    """See i18n/ko.json for description"""
```

### For UI Strings
```python
# Before (inline Korean)
st.title("헌법 준수 대시보드")  # ← Blocked

# After (i18n structure)
import json
MESSAGES = json.load(open("i18n/ko.json", "r", encoding="utf-8"))
st.title(MESSAGES["dashboard_title"])
```

---

**Last Updated**: 2025-11-08
**Owner**: Constitution Guard (P10)
**Status**: ENFORCED via pre-commit hooks
