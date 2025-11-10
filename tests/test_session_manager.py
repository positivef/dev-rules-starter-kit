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


def test_graceful_shutdown_flag():
    """Graceful shutdown 플래그 테스트 (session_recovery 연동)"""
    print("\n=== Graceful Shutdown Flag Test ===")
    import json

    # 새 세션 생성
    SessionManager._instance = None
    session = SessionManager.get_instance()
    session.start(resume_last=False)

    session_id = session.current_state.session_id
    session_file = Path("RUNS/sessions") / f"{session_id}.json"

    # 데이터 저장 및 체크포인트
    session.set("test", "value", StateScope.SESSION)
    session.checkpoint()

    # graceful_shutdown이 False로 초기화되었는지 확인
    with open(session_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["graceful_shutdown"] is False
    print(f"Initial state: graceful_shutdown={data['graceful_shutdown']}")

    # 정상 종료 시뮬레이션 (cleanup 호출)
    session._cleanup()

    # graceful_shutdown이 True로 설정되었는지 확인
    with open(session_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["graceful_shutdown"] is True
    print(f"After cleanup: graceful_shutdown={data['graceful_shutdown']}")

    print("[OK] Graceful shutdown flag test passed")


def test_session_recovery_integration():
    """SessionManager와 SessionRecovery 통합 테스트"""
    print("\n=== Session Recovery Integration Test ===")
    import json
    from datetime import datetime, timezone, timedelta

    # session_recovery 임포트 (optional)
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.session_recovery import SessionRecovery
    except ImportError:
        print("[SKIP] session_recovery not available")
        return

    # 1. 정상 종료된 세션 생성
    SessionManager._instance = None
    session1 = SessionManager.get_instance()
    session1.start(resume_last=False)
    session1.set("data", "normal", StateScope.SESSION)
    session1.checkpoint()

    session1_id = session1.current_state.session_id

    # 정상 종료 (graceful_shutdown=True)
    session1._cleanup()

    # 2. 비정상 종료 시뮬레이션 (orphaned session)
    SessionManager._instance = None
    session2 = SessionManager.get_instance()
    session2.start(resume_last=False)
    session2.set("data", "crashed", StateScope.SESSION)
    session2.checkpoint()

    session2_id = session2.current_state.session_id
    session2_file = Path("RUNS/sessions") / f"{session2_id}.json"

    # 비정상 종료 시뮬레이션 (cleanup 안 함, graceful_shutdown=False)
    # last_update를 2시간 전으로 설정
    with open(session2_file, "r", encoding="utf-8") as f:
        session2_data = json.load(f)

    old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    session2_data["last_update"] = old_time
    session2_data["graceful_shutdown"] = False

    with open(session2_file, "w", encoding="utf-8") as f:
        json.dump(session2_data, f, indent=2, ensure_ascii=True)

    # 3. SessionRecovery로 orphaned session 감지
    recovery = SessionRecovery()

    # 정상 종료된 세션은 orphaned로 감지되지 않아야 함
    is_session1_orphaned = recovery._detect_orphaned_session(session1_id)
    assert is_session1_orphaned is False
    print(f"Session1 (normal shutdown): orphaned={is_session1_orphaned}")

    # 비정상 종료된 세션은 orphaned로 감지되어야 함
    is_session2_orphaned = recovery._detect_orphaned_session(session2_id)
    assert is_session2_orphaned is True
    print(f"Session2 (crashed, >1hr old): orphaned={is_session2_orphaned}")

    print("[OK] Session recovery integration test passed")


if __name__ == "__main__":
    # 모든 테스트 실행
    test_session_basic()
    test_session_recovery()
    test_auto_checkpoint()
    test_scope_management()
    test_session_cleanup()
    test_graceful_shutdown_flag()
    test_session_recovery_integration()

    print("\n" + "=" * 50)
    print("[SUCCESS] All session manager tests passed!")
    print("=" * 50)
