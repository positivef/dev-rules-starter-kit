#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_history_tracker import ObsidianHistoryTracker

print("[DEBUG] Creating tracker...")
tracker = ObsidianHistoryTracker()

print(f"Vault path: {tracker.vault_path}")
print(f"Vault exists: {tracker.vault_path.exists()}")
print(f"History dir: {tracker.history_dir}")
print(f"History dir exists: {tracker.history_dir.exists()}")
print(f"History index: {tracker.history_index}")
print(f"History index exists: {tracker.history_index.exists()}")

if tracker.history_index.exists():
    print("\n[INDEX CONTENT]")
    content = tracker.history_index.read_text(encoding="utf-8")
    print(content[:500])

file_path = "개발일지/2025-10-29_히스토리_추적_테스트.md"
test_file = tracker.vault_path / file_path

print("\n[TEST FILE]")
print(f"Looking for: {test_file}")
print(f"File exists: {test_file.exists()}")

# 히스토리 조회
history = tracker.get_file_history(file_path)
print("\n[HISTORY]")
if history:
    print(f"Found! Update count: {history['update_count']}")
else:
    print("Not found")

# 인덱스 파일 직접 읽기
print("\n[RAW INDEX]")
index_data = tracker._load_history_index()
print(f"Total files in index: {len(index_data)}")
for key in index_data.keys():
    print(f"  - {key}")
