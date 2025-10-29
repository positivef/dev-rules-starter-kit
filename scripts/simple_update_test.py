#!/usr/bin/env python3
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_history_tracker import ObsidianHistoryTracker

tracker = ObsidianHistoryTracker()
file_path = "개발일지/2025-10-29_히스토리_추적_테스트.md"

print("[UPDATE 2]")
time.sleep(0.3)
try:
    r2 = tracker.track_update(file_path, "second_update")
    print(f"  Update #{r2.get('update_number', 'N/A')}: {r2.get('action', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

print("[UPDATE 3]")
time.sleep(0.3)
try:
    r3 = tracker.track_update(file_path, "third_update")
    print(f"  Update #{r3.get('update_number', 'N/A')}: {r3.get('action', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

h = tracker.get_file_history(file_path)
if h:
    print(f"\n[FINAL] Total updates: {h['update_count']}")
else:
    print("\n[FINAL] No history found")
