#!/usr/bin/env python3
"""
옵시디언 히스토리 추적 실제 테스트
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_bridge import ObsidianBridge


def test_live():
    print("[TEST] 옵시디언 히스토리 추적 실제 테스트")
    print("=" * 60)

    # 1. ObsidianBridge 초기화
    print("\n[STEP 1] ObsidianBridge 초기화...")
    bridge = ObsidianBridge()
    print(f"[OK] Vault Path: {bridge.vault_path}")

    if not bridge.vault_path.exists():
        print(f"[ERROR] Vault path does not exist: {bridge.vault_path}")
        return

    # 2. 히스토리 트래커 확인
    print("\n[STEP 2] 히스토리 트래커 확인...")
    if bridge.history_tracker:
        print("[OK] History tracker initialized")
    else:
        print("[WARNING] History tracker not initialized")
        return

    # 3. 테스트 devlog 생성
    print("\n[STEP 3] 테스트 devlog 생성...")

    task_contract = {
        "task_id": "TEST-HISTORY-001",
        "title": "히스토리 추적 테스트",
        "description": "옵시디언 히스토리 추적 기능 실제 테스트",
        "type": "test",
        "priority": "high",
        "tags": ["test", "history"],
        "acceptance_criteria": ["히스토리 추적 동작 확인", "문서 내 히스토리 섹션 생성 확인", "업데이트 카운트 증가 확인"],
        "commands": [],
        "gates": [],
    }

    execution_result = {"status": "success", "duration": 1.23, "evidence_hashes": {}, "git_commits": []}

    # devlog 생성
    try:
        devlog_path = bridge.create_devlog(task_contract, execution_result)
        print(f"[OK] Devlog created: {devlog_path}")

        # 파일이 실제로 생성되었는지 확인
        if devlog_path.exists():
            print(f"[OK] File exists: {devlog_path}")

            # 파일 내용 읽기
            content = devlog_path.read_text(encoding="utf-8")

            # 히스토리 섹션이 있는지 확인
            if "<!-- HISTORY_START -->" in content:
                print("[OK] History section found in document")

                # 히스토리 내용 출력
                start = content.find("<!-- HISTORY_START -->")
                end = content.find("<!-- HISTORY_END -->") + len("<!-- HISTORY_END -->")
                history_section = content[start:end]

                print("\n[HISTORY SECTION]")
                print("-" * 60)
                print(history_section)
                print("-" * 60)
            else:
                print("[WARNING] History section not found in document")

        else:
            print(f"[ERROR] File not created: {devlog_path}")

    except Exception as e:
        print(f"[ERROR] Failed to create devlog: {e}")
        import traceback

        traceback.print_exc()
        return

    # 4. 히스토리 조회
    print("\n[STEP 4] 히스토리 조회...")
    try:
        relative_path = devlog_path.relative_to(bridge.vault_path).as_posix()
        history = bridge.history_tracker.get_file_history(relative_path)

        if history:
            print("[OK] History found:")
            print(f"  - First Created: {history['first_created']}")
            print(f"  - Last Updated: {history['last_updated']}")
            print(f"  - Update Count: {history['update_count']}")
            print(f"  - History Entries: {len(history['history'])}")

            for i, entry in enumerate(history["history"], 1):
                print(f"\n  Update #{i}:")
                print(f"    - Timestamp: {entry['timestamp']}")
                print(f"    - Action: {entry['action']}")
                print(f"    - Hash: {entry['hash']}")
        else:
            print("[WARNING] No history found")

    except Exception as e:
        print(f"[ERROR] Failed to retrieve history: {e}")

    # 5. 두 번째 업데이트 테스트
    print("\n[STEP 5] 두 번째 업데이트 테스트...")
    try:
        import time

        time.sleep(0.5)  # 약간의 시간 대기

        # 파일 내용 수정
        content = devlog_path.read_text(encoding="utf-8")
        content += "\n\n## 추가 내용\n\n두 번째 업데이트 테스트\n"
        devlog_path.write_text(content, encoding="utf-8")

        # 히스토리 업데이트
        bridge.history_tracker.track_update(relative_path, action="manual_update", metadata={"test": "second_update"})

        # 업데이트된 히스토리 확인
        history = bridge.history_tracker.get_file_history(relative_path)
        print("[OK] Updated history:")
        print(f"  - Update Count: {history['update_count']}")
        print(f"  - Latest Action: {history['history'][-1]['action']}")

    except Exception as e:
        print(f"[ERROR] Failed second update: {e}")

    # 6. 최근 업데이트 목록 확인
    print("\n[STEP 6] 최근 업데이트 목록 확인...")
    try:
        recent = bridge.history_tracker.get_recent_updates(limit=5)
        print(f"[OK] Recent updates ({len(recent)}):")

        for update in recent:
            print(f"  - {update['timestamp']} - {update['file_path']} ({update['action']})")

    except Exception as e:
        print(f"[ERROR] Failed to get recent updates: {e}")

    print("\n" + "=" * 60)
    print("[COMPLETE] 테스트 완료!")
    print(f"\n생성된 파일 위치: {devlog_path}")
    print("옵시디언에서 파일을 열어서 히스토리 섹션을 확인하세요.")


if __name__ == "__main__":
    test_live()
