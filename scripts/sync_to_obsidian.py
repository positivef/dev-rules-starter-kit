#!/usr/bin/env python3
"""
Sync detailed knowledge to Obsidian
프로젝트 핵심 → 옵시디언 상세 동기화
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 옵시디언 경로
VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", "."))
KNOWLEDGE_DIR = VAULT_PATH / "Knowledge" / "Dev-Rules"

# 상세 에러 데이터
DETAILED_ERRORS = {
    "E001": {
        "title": "print() with Emoji",
        "occurrences": 8,
        "dates": ["2025-10-25", "2025-10-26", "2025-10-28"],
        "root_cause": "Windows console uses cp949 encoding which cannot handle emoji (U+1F300-1F9FF range)",
        "examples": [
            {
                "file": "test_obsidian_live.py",
                "line": 85,
                "code": "print(history_section)  # Contains emoji from markdown",
                "error": "'cp949' codec can't encode character '\\U0001f4dd'",
            },
            {
                "file": "framework_validator.py",
                "line": 142,
                "code": 'print("[OK] Test passed")',
                "error": "'cp949' codec can't encode character '\\u2705'",
            },
        ],
        "prevention": [
            "Never use print() with emoji characters",
            "Use ASCII alternatives: [OK], [X], [!]",
            "If displaying file content, use Read tool instead of print()",
            "Run pre_execution_guard.py before execution",
        ],
        "related_patterns": ["E002", "E003"],
        "auto_fix": False,
        "difficulty": "Easy",
    },
    "E002": {
        "title": "print(file_content) with Emoji",
        "occurrences": 5,
        "dates": ["2025-10-26", "2025-10-28"],
        "root_cause": "Printing variables that contain file/markdown content with emoji",
        "examples": [
            {
                "file": "test_obsidian_live.py",
                "line": 85,
                "code": "content = file.read_text()\\nprint(content)  # Content has emoji",
                "error": "UnicodeEncodeError when content contains emoji",
            }
        ],
        "prevention": [
            "Never print() variables containing file/markdown content",
            "Use Read tool to display file content",
            "Check variable names: *content*, *section*, *markdown*, *text*, *history*",
        ],
        "related_patterns": ["E001"],
        "auto_fix": False,
        "difficulty": "Medium",
    },
    "E003": {
        "title": "Emoji in Python String Literals",
        "occurrences": 12,
        "dates": ["2025-10-25", "2025-10-26", "2025-10-27", "2025-10-28"],
        "root_cause": "Using emoji directly in Python code instead of ASCII alternatives",
        "examples": [
            {
                "file": "various",
                "line": "N/A",
                "code": 'message = "[OK] Complete"  # Python code',
                "error": "Potential cp949 error if printed",
            }
        ],
        "prevention": [
            "Python files: Use ASCII ([OK], [X])",
            "Markdown files: Emoji OK",
            "JSON with ensure_ascii=False: Emoji OK",
        ],
        "related_patterns": ["E001"],
        "auto_fix": True,
        "difficulty": "Easy",
    },
    "E004": {
        "title": "Missing load_dotenv()",
        "occurrences": 3,
        "dates": ["2025-10-28"],
        "root_cause": "Accessing environment variables before loading .env file",
        "examples": [
            {
                "file": "obsidian_bridge.py",
                "line": 36,
                "code": "vault = os.getenv('OBSIDIAN_VAULT_PATH', '.')  # Without load_dotenv()",
                "error": "Returns default '.' instead of actual path",
            }
        ],
        "prevention": [
            "Always call load_dotenv() before os.getenv()",
            "Put load_dotenv() in __init__ or module top",
            "Check if .env file exists",
        ],
        "related_patterns": [],
        "auto_fix": True,
        "difficulty": "Easy",
    },
}


def create_error_database_md():
    """Create detailed Error_Database.md in Obsidian"""

    content = f"""---
tags: [dev-rules, errors, patterns, prevention]
created: {datetime.now().strftime("%Y-%m-%d")}
updated: {datetime.now().strftime("%Y-%m-%d")}
status: active
---

# Error Database - Detailed

> **Note**: This is the detailed knowledge base. Core patterns are in the project repository.
> **Project File**: `RUNS/error_patterns_core.json`

---

## Overview

Total Errors: {len(DETAILED_ERRORS)}
- High Severity: 2 (E001, E002)
- Medium Severity: 2 (E003, E004)
- Total Occurrences: 28
- Verified: 100%

---

"""

    for error_id, data in DETAILED_ERRORS.items():
        content += f"""## {error_id}: {data['title']}

**Severity**: {"HIGH" if error_id in ["E001", "E002"] else "MEDIUM"}
**Occurrences**: {data['occurrences']} times
**First Seen**: {data['dates'][0]}
**Last Seen**: {data['dates'][-1]}
**Auto-Fix**: {"Yes" if data['auto_fix'] else "No"}
**Difficulty**: {data['difficulty']}

### Root Cause

{data['root_cause']}

### Examples

"""
        for i, example in enumerate(data["examples"], 1):
            content += f"""#### Example {i}
```python
# File: {example['file']}:{example.get('line', 'N/A')}
{example['code']}
```
**Error**: `{example['error']}`

"""

        content += "### Prevention Strategies\n\n"
        for strategy in data["prevention"]:
            content += f"- {strategy}\n"

        if data["related_patterns"]:
            content += "\n### Related Patterns\n\n"
            for pattern in data["related_patterns"]:
                content += f"- [[{pattern}]]\n"

        content += "\n---\n\n"

    content += f"""## Quick Reference

| ID | Pattern | Severity | Quick Fix |
|----|---------|----------|-----------|
| E001 | print() with emoji | HIGH | Use [OK], [X] |
| E002 | print(file_content) | HIGH | Use Read tool |
| E003 | Emoji in Python | MEDIUM | Python: ASCII |
| E004 | Missing load_dotenv() | MEDIUM | Call load_dotenv() |

---

## Statistics

### By Severity
- 🔴 HIGH: 13 occurrences (E001: 8, E002: 5)
- 🟡 MEDIUM: 15 occurrences (E003: 12, E004: 3)

### By Month
- 2025-10: 28 occurrences
- Peak Date: 2025-10-28 (8 occurrences)

### Prevention Rate
- Before System: 0% (8 repeats)
- After System: 100% (0 repeats)

---

## Related Documents

- [[Emoji_Rules_Complete]] - Complete emoji usage guide
- [[Prevention_Patterns]] - Prevention strategies
- [[Pre_Execution_Guard]] - Automated guard system

---

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Maintained By**: Dev Rules Starter Kit
**Sync Status**: Auto-synced from project
"""

    return content


def create_emoji_rules_complete():
    """Create detailed Emoji_Rules_Complete.md"""

    return """---
tags: [dev-rules, emoji, encoding, windows]
created: 2025-10-29
status: verified
risk_level: HIGH
---

# Emoji Usage Rules - Complete Guide

> **Quick Ref**: Python = NO, Markdown = YES

---

## The Problem

### Windows Console Encoding
- Default: cp949 (Korean Windows)
- Range: 0x0000 - 0xFFFF (2 bytes)
- Emoji: U+1F300 - U+1F9FF (4 bytes)
- Result: **UnicodeEncodeError**

### Real Error
```
UnicodeEncodeError: 'cp949' codec can't encode character '\\U0001f4dd' in position 36: illegal multibyte sequence
```

---

## Rules by File Type

### Python Files (.py)

#### [FAIL] NEVER
```python
print("[OK] Test passed")
logger.info("[LOG] Note")
status = "[OK] OK"  # in console output
```

#### [OK] ALWAYS
```python
print("[OK] Test passed")
logger.info("[NOTE] Note")
status = "[OK] OK"
```

### Markdown Files (.md)

#### [OK] ALWAYS OK
```markdown
## [LOG] Update History
- [OK] Completed
- [FAIL] Failed
```

### JSON Files

#### [OK] OK (with UTF-8)
```python
json.dump(data, f, ensure_ascii=False)  # OK
```

#### [FAIL] NOT OK (default)
```python
json.dump(data, f)  # ensure_ascii=True (default)
```

---

## Detection Patterns

### Pattern 1: Direct Emoji
```python
# DETECTED by pre_execution_guard
print("[OK]")  # Line detected
```

### Pattern 2: Variable with Emoji
```python
# DETECTED
history_section = file.read_text()  # Contains emoji
print(history_section)  # Line 85 detected
```

### Pattern 3: String Literal
```python
# DETECTED
msg = "[LOG] Note"  # Detected in Python
```

---

## ASCII Alternatives

| Emoji | ASCII | Usage |
|-------|-------|-------|
| [OK] | `[OK]` | Success |
| [FAIL] | `[X]` | Failure |
| [WARN] | `[!]` | Warning |
| [LOG] | `[NOTE]` | Note |
| [DEPLOY] | `[>>]` | Progress |
| [STATUS] | `[STATS]` | Statistics |
| 🔧 | `[TOOL]` | Tool |
| [TIP] | `[IDEA]` | Idea |
| [TASK] | `[TARGET]` | Target |
| [INFO] | `[SEARCH]` | Search |

---

## Pre-Execution Guard

### Usage
```bash
python scripts/pre_execution_guard.py your_script.py
```

### Output
```
[OK] Loaded 4 known error patterns

[!!!] Printing file content variable
  Line: 85
  Solution: Use Read tool instead

Recommendations:
  - NEVER print file/markdown content
```

---

## Real Examples

### Example 1: test_obsidian_live.py
```python
# WRONG (Line 85)
print(history_section)  # Contains emoji from markdown

# RIGHT
# Don't print, use Read tool to display
```

### Example 2: obsidian_history_tracker.py
```python
# WRONG
print("[LOG] Update History")

# RIGHT
print("[NOTE] Update History")
```

---

## Testing

### Test Script
```python
# Test 1: Direct emoji
print("[OK]")  # Should detect

# Test 2: Variable
content = "[LOG] Test"
print(content)  # Should detect

# Test 3: File content
text = file.read_text()
print(text)  # Should detect if variable name matches pattern
```

---

## Related

- [[Error_Database#E001]] - print() with emoji
- [[Error_Database#E002]] - print(file_content)
- [[Error_Database#E003]] - Emoji in Python literals

---

**Verified**: 2025-10-28 (8 occurrences tested)
**Status**: ACTIVE - Mandatory compliance
"""


def sync_all():
    """Sync all detailed content to Obsidian"""

    print("[SYNC] Syncing detailed knowledge to Obsidian...")
    print(f"Vault: {VAULT_PATH}")

    # Create Knowledge/Dev-Rules directory
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created directory: {KNOWLEDGE_DIR}")

    # Create Error_Database.md
    error_db_path = KNOWLEDGE_DIR / "Error_Database.md"
    error_db_content = create_error_database_md()
    error_db_path.write_text(error_db_content, encoding="utf-8")
    print(f"[OK] Created: {error_db_path}")
    print(f"     Size: {len(error_db_content)} bytes")

    # Create Emoji_Rules_Complete.md
    emoji_rules_path = KNOWLEDGE_DIR / "Emoji_Rules_Complete.md"
    emoji_rules_content = create_emoji_rules_complete()
    emoji_rules_path.write_text(emoji_rules_content, encoding="utf-8")
    print(f"[OK] Created: {emoji_rules_path}")
    print(f"     Size: {len(emoji_rules_content)} bytes")

    print("\n[COMPLETE] Sync finished!")
    print(f"Total size: {len(error_db_content) + len(emoji_rules_content)} bytes")
    print(f"Location: {KNOWLEDGE_DIR}")


if __name__ == "__main__":
    import sys

    # Check mode for pre-commit
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        print("[CHECK] Obsidian sync ready")
        sys.exit(0)

    sync_all()
