#!/usr/bin/env python3
"""
다중 업데이트 테스트
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_history_tracker import ObsidianHistoryTracker


def test_multiple_updates():
    print("[TEST] Multiple Updates Test")
    print("=" * 60)

    # 히스토리 트래커 초기화
    tracker = ObsidianHistoryTracker()

    # 테스트 파일 경로
    test_file = "개발일지/2025-10-29_히스토리_추적_테스트.md"

    print("\n[STEP 1] Current state check...")
    history = tracker.get_file_history(test_file)
    if history:
        print(f"  Current update count: {history['update_count']}")
    else:
        print("  No history found")
        return

    # 2차 업데이트
    print("\n[STEP 2] Second update...")
    time.sleep(0.5)
    record = tracker.track_update(test_file, action="second_update", metadata={"test": "update_2"})
    print(f"  Update #{record['update_number']} - {record['timestamp']}")

    # 3차 업데이트
    print("\n[STEP 3] Third update...")
    time.sleep(0.5)
    record = tracker.track_update(test_file, action="third_update", metadata={"test": "update_3"})
    print(f"  Update #{record['update_number']} - {record['timestamp']}")

    # 4차 업데이트
    print("\n[STEP 4] Fourth update...")
    time.sleep(0.5)
    record = tracker.track_update(test_file, action="fourth_update", metadata={"test": "update_4"})
    print(f"  Update #{record['update_number']} - {record['timestamp']}")

    # 최종 상태 확인
    print("\n[STEP 5] Final state check...")
    history = tracker.get_file_history(test_file)
    if history:
        print(f"  Total updates: {history['update_count']}")
        print(f"  First created: {history['first_created']}")
        print(f"  Last updated: {history['last_updated']}")

        print("\n  Recent update history:")
        for entry in history["history"][-5:]:
            print(f"    #{entry['update_number']}: {entry['action']} - {entry['timestamp']}")

    print("\n" + "=" * 60)
    print("[COMPLETE] Test completed!")
    print("File location: 개발일지/2025-10-29_히스토리_추적_테스트.md")
    print("Open in Obsidian to see the updated history section.")


if __name__ == "__main__":
    test_multiple_updates()
