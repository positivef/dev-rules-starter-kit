"""
Register Korean encoding error patterns to Error Learning Database
Prevent recurring Unicode/encoding issues on Windows
"""

from error_learner import ErrorLearner

learner = ErrorLearner()

print("[STEP 1] Registering Korean encoding error patterns...")

# Pattern 1: UnicodeEncodeError with emoji
error_id_1 = learner.capture_error(
    error_type="UnicodeEncodeError",
    error_msg="'cp949' codec can't encode character '\\u2705' in position 0",
    context="Python print() or file write operations on Windows",
    solution=(
        "Replace all emoji with ASCII alternatives. "
        "Use [OK], [FAIL], [WARN] instead of emoji"
    ),
    tags=["encoding", "emoji", "windows", "cp949", "unicode"],
)
print(f"[OK] Emoji encoding error: {error_id_1}")

# Pattern 2: UnicodeEncodeError with Korean + emoji mixed
error_id_2 = learner.capture_error(
    error_type="UnicodeEncodeError",
    error_msg="'cp949' codec can't encode character in Korean text with emoji",
    context="Windows console output with mixed Korean and emoji",
    solution=(
        "1) Use UTF-8 encoding: open(file, encoding='utf-8') "
        "2) Remove emoji 3) Set PYTHONIOENCODING=utf-8"
    ),
    tags=["encoding", "korean", "emoji", "windows", "cp949"],
)
print(f"[OK] Korean+emoji error: {error_id_2}")

# Pattern 3: Git encoding issues
error_id_3 = learner.capture_error(
    error_type="UnicodeDecodeError",
    error_msg="Git diff shows garbled Korean characters",
    context="Git operations on Windows with Korean filenames/content",
    solution=(
        "git config --global core.quotepath false && "
        "git config --global i18n.commitencoding utf-8"
    ),
    tags=["git", "encoding", "korean", "windows"],
)
print(f"[OK] Git Korean encoding: {error_id_3}")

# Pattern 4: File write encoding
error_id_4 = learner.capture_error(
    error_type="UnicodeEncodeError",
    error_msg="Korean characters not saved correctly to file",
    context="File.write() without explicit encoding on Windows",
    solution='Always use encoding="utf-8": with open(file, "w", encoding="utf-8")',
    tags=["encoding", "korean", "file-io", "windows"],
)
print(f"[OK] File write encoding: {error_id_4}")

# Pattern 5: Bash heredoc with Korean
error_id_5 = learner.capture_error(
    error_type="UnicodeEncodeError",
    error_msg="Bash heredoc fails with Korean characters on Windows",
    context="Using cat << 'EOF' with Korean text in git bash",
    solution=(
        "Use Python Write tool instead of bash heredoc for Korean content. "
        "Or write to temp file with UTF-8 encoding first"
    ),
    tags=["bash", "encoding", "korean", "windows", "heredoc"],
)
print(f"[OK] Bash heredoc error: {error_id_5}")

# Statistics
stats = learner.get_stats()
print(f"\n[STATS] Total error patterns: {stats['total_unique_errors']}")
print(f"[STATS] Total occurrences: {stats['total_occurrences']}")

# Test regression prevention
print("\n[TEST] Testing regression prevention...")
risky_code = """
# Example risky code
print("작업 완료! ✅")  # Has emoji with Korean
with open("file.txt", "w") as f:  # No encoding specified
    f.write("한글 내용")
"""

warnings = learner.prevent_regression(risky_code)
if warnings:
    print(f"[WARN] Detected {len(warnings)} risky patterns:")
    for warning in warnings:
        print(f"  - {warning['pattern']}: {warning['message']}")
else:
    print("[OK] No risky patterns detected")

print("\n[SUCCESS] Korean encoding error patterns registered!")
print("Database file: .error_db.json")
