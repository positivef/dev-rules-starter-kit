#!/usr/bin/env python3
"""
최종 옵시디언 히스토리 추적 테스트
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_bridge import ObsidianBridge

print("[STEP 1] ObsidianBridge 초기화...")
bridge = ObsidianBridge()
print(f"Vault: {bridge.vault_path}")

print("\n[STEP 2] 테스트 devlog 생성...")
task_contract = {
    "task_id": "HISTORY-TEST-002",
    "title": "히스토리 추적 최종 테스트",
    "description": "옵시디언 히스토리 기능 최종 검증",
    "type": "test",
    "priority": "high",
    "tags": ["test", "history", "final"],
    "acceptance_criteria": ["첫 생성 시간 기록", "업데이트 시간 증가 확인", "히스토리 섹션 자동 생성"],
    "commands": [],
    "gates": [],
}

execution_result = {"status": "success", "duration": 1.5, "evidence_hashes": {}, "git_commits": []}

devlog_path = bridge.create_devlog(task_contract, execution_result)
print(f"Created: {devlog_path}")

print("\n[STEP 3] 히스토리 확인...")
if bridge.history_tracker:
    relative_path = devlog_path.relative_to(bridge.vault_path).as_posix()
    history = bridge.history_tracker.get_file_history(relative_path)
    if history:
        print(f"Update Count: {history['update_count']}")
        print(f"First Created: {history['first_created']}")

print("\n[STEP 4] 추가 업데이트 테스트...")
for i in range(2, 5):
    time.sleep(0.3)
    if bridge.history_tracker:
        bridge.history_tracker.track_update(relative_path, action=f"test_update_{i}", metadata={"iteration": i})
        print(f"  Update #{i} completed")

print("\n[STEP 5] 최종 상태...")
if bridge.history_tracker:
    history = bridge.history_tracker.get_file_history(relative_path)
    if history:
        print(f"Total Updates: {history['update_count']}")
        print(f"Last Updated: {history['last_updated']}")

print("\n[COMPLETE]")
print(f"File location: {devlog_path}")
print("Open in Obsidian to view the history section!")
