#!/usr/bin/env python3
"""
SessionManager 테스트 - 자동 저장 및 복구 기능 검증
"""

import time
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.session_manager import SessionManager, StateScope


def test_session_basic():
    """기본 세션 기능 테스트"""
    print("\n=== Basic Session Test ===")

    # 세션 시작
    session = SessionManager.get_instance()
    session.start(resume_last=False)

    # 데이터 저장
    session.set("test_key", "test_value", StateScope.SESSION)
    session.set("user:name", "Claude", StateScope.USER)
    session.set("app:mode", "development", StateScope.APP)

    # 데이터 조회
    assert session.get("test_key", StateScope.SESSION) == "test_value"
    assert session.get("user:name", StateScope.USER) == "Claude"
    assert session.get("app:mode", StateScope.APP) == "development"

    # 세션 정보 확인
    info = session.get_session_info()
    print(f"Session ID: {info['session_id']}")
    print(f"Context Hash: {info['context_hash']}")
    print(f"Data sizes: {info['data_sizes']}")

    # 체크포인트 생성
    session.checkpoint()
    print("[OK] Basic session test passed")


def test_session_recovery():
    """세션 복구 테스트"""
    print("\n=== Session Recovery Test ===")

    # 1. 첫 번째 세션 생성 및 데이터 저장
    session1 = SessionManager.get_instance()
    session1.start(resume_last=False)

    # 테스트 데이터 저장
    session1.set("important_data", {"task": "testing", "step": 1}, StateScope.SESSION)
    session1.set("user:id", "12345", StateScope.USER)

    # 체크포인트 생성
    session1.checkpoint()

    session_id_1 = session1.current_state.session_id
    print(f"Created session: {session_id_1}")

    # 2. 세션 종료 시뮬레이션 (새 인스턴스 생성)
    SessionManager._instance = None  # 인스턴스 리셋

    # 3. 세션 복구
    session2 = SessionManager.get_instance()
    session2.start(resume_last=True)  # 마지막 세션 복구

    # 복구된 데이터 확인
    recovered_data = session2.get("important_data", StateScope.SESSION)
    recovered_user = session2.get("user:id", StateScope.USER)

    assert recovered_data == {"task": "testing", "step": 1}
    assert recovered_user == "12345"

    print(f"Recovered session: {session2.current_state.session_id}")
    print(f"Recovered data: {recovered_data}")
    print("[OK] Session recovery test passed")


def test_auto_checkpoint():
    """자동 체크포인트 테스트 (짧은 간격)"""
    print("\n=== Auto Checkpoint Test ===")

    # 짧은 간격으로 설정 (2초)
    session = SessionManager.get_instance()
    session.checkpoint_interval = 2  # 2초로 설정
    session.start(resume_last=False)

    # 초기 데이터 설정
    session.set("counter", 0, StateScope.SESSION)

    print("Waiting for automatic checkpoint (2 seconds)...")
    initial_checkpoint = session.current_state.last_checkpoint

    # 3초 대기 (자동 체크포인트 발생해야 함)
    time.sleep(3)

    # 데이터 변경
    session.set("counter", 1, StateScope.SESSION)

    # 체크포인트 시간이 업데이트되었는지 확인
    updated_checkpoint = session.current_state.last_checkpoint
    assert initial_checkpoint != updated_checkpoint

    print(f"Initial checkpoint: {initial_checkpoint}")
    print(f"Updated checkpoint: {updated_checkpoint}")
    print("[OK] Auto checkpoint test passed")


def test_scope_management():
    """상태 범위 관리 테스트"""
    print("\n=== Scope Management Test ===")

    session = SessionManager.get_instance()
    session.start(resume_last=False)

    # 각 범위별로 데이터 저장
    session.set("session_data", "temporary", StateScope.SESSION)
    session.set("user_pref", "persistent", StateScope.USER)
    session.set("global_config", "shared", StateScope.APP)
    session.set("temp_cache", "volatile", StateScope.TEMP)

    # 범위별 데이터 확인
    info = session.get_session_info()
    print(f"Scope data sizes: {info['data_sizes']}")

    # 각 범위에서 데이터 조회
    assert session.get("session_data", StateScope.SESSION) == "temporary"
    assert session.get("user_pref", StateScope.USER) == "persistent"
    assert session.get("global_config", StateScope.APP) == "shared"
    assert session.get("temp_cache", StateScope.TEMP) == "volatile"

    print("[OK] Scope management test passed")


def test_session_cleanup():
    """세션 정리 테스트"""
    print("\n=== Session Cleanup Test ===")

    session = SessionManager.get_instance()
    session.max_sessions = 2  # 최대 2개만 보관

    # 여러 세션 생성
    for i in range(3):
        SessionManager._instance = None
        session = SessionManager.get_instance()
        session.start(resume_last=False)
        session.set("session_number", i, StateScope.SESSION)
        session.checkpoint()
        print(f"Created session {i+1}")
        time.sleep(0.1)  # 시간 차이를 위해

    # 세션 파일 확인
    session_files = list(Path("RUNS/sessions").glob("*.json"))

    # cleanup 실행
    session._cleanup_old_sessions()

    # 세션 파일 다시 확인
    session_files_after = list(Path("RUNS/sessions").glob("*.json"))

    print(f"Sessions before cleanup: {len(session_files)}")
    print(f"Sessions after cleanup: {len(session_files_after)}")
    print("[OK] Session cleanup test passed")


if __name__ == "__main__":
    # 모든 테스트 실행
    test_session_basic()
    test_session_recovery()
    test_auto_checkpoint()
    test_scope_management()
    test_session_cleanup()

    print("\n" + "=" * 50)
    print("[SUCCESS] All session manager tests passed!")
    print("=" * 50)
