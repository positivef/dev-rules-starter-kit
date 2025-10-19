"""Fix emoji in enhanced_task_executor.py for Windows cp949 compatibility"""

with open("scripts/enhanced_task_executor.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace all emoji with ASCII equivalents
replacements = {
    "⚠️": "[WARN]",
    "✅": "[PASS]",
    "❌": "[FAIL]",
    "📝": "[DOC]",
    "📎": "[ATTACH]",
    "⚡": "[PARALLEL]",
    "→": "->",
    "ℹ️": "[INFO]",
    "✓": "[PASS]",
    "✗": "[FAIL]",
}

for emoji, ascii_rep in replacements.items():
    content = content.replace(emoji, ascii_rep)

with open("scripts/enhanced_task_executor.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[PASS] All emoji replaced with ASCII equivalents")
