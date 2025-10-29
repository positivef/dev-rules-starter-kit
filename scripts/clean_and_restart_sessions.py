#!/usr/bin/env python3
"""
세션 파일 정리 및 재시작 스크립트
모든 기존 세션을 백업하고 새로운 세션으로 시작
"""

import shutil
from pathlib import Path
from datetime import datetime


def clean_sessions():
    """모든 세션 파일을 백업하고 정리"""

    session_dir = Path("RUNS/sessions")
    backup_dir = Path("RUNS/sessions_backup")

    print("=" * 60)
    print("Session Clean and Restart")
    print("=" * 60)

    if not session_dir.exists():
        print("No session directory found")
        session_dir.mkdir(parents=True, exist_ok=True)
        return

    # 기존 세션 파일 카운트
    session_files = list(session_dir.glob("*.json"))
    print(f"\nFound {len(session_files)} session files")

    if session_files:
        # 백업 디렉토리 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)

        print(f"Creating backup at: {backup_path}")

        # 모든 파일 백업
        for file in session_files:
            try:
                shutil.copy2(file, backup_path / file.name)
                print(f"  Backed up: {file.name}")
            except Exception as e:
                print(f"  Failed to backup {file.name}: {e}")

        # 원본 파일 삭제
        print("\nCleaning session files...")
        for file in session_files:
            try:
                file.unlink()
                print(f"  Removed: {file.name}")
            except Exception as e:
                print(f"  Failed to remove {file.name}: {e}")

    # execution 관련 파일도 정리
    for pattern in ["*execution*.json", "*.backup.json"]:
        for file in session_dir.glob(pattern):
            try:
                file.unlink()
                print(f"  Removed: {file.name}")
            except:
                pass

    print("\n" + "=" * 60)
    print("Session cleanup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start fresh with new sessions")
    print("2. Run dashboard: streamlit run scripts/session_dashboard.py")
    print(f"3. Old sessions backed up to: {backup_dir}")


def test_new_session():
    """새로운 세션 생성 테스트"""

    print("\n" + "=" * 60)
    print("Testing New Session Creation")
    print("=" * 60)

    try:
        from session_manager import SessionManager, StateScope

        # 싱글톤 리셋
        SessionManager._instance = None

        # 새로운 세션 시작
        manager = SessionManager.get_instance()
        manager.start(resume_last=False)

        # 테스트 데이터 (ASCII만 사용)
        manager.set("test_key", "test_value", StateScope.SESSION)
        manager.set("app_name", "SessionManager", StateScope.APP)
        manager.set("user_id", "user_001", StateScope.USER)

        # 체크포인트
        manager.checkpoint()

        print("New session created successfully!")
        print(f"Session ID: {manager.session_id}")

        # 정리
        manager._cleanup()

        return True

    except Exception as e:
        print(f"Failed to create new session: {e}")
        return False


def main():
    """메인 함수"""

    # 1. 세션 정리
    clean_sessions()

    # 2. 새 세션 테스트
    success = test_new_session()

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] System is ready!")
        print("=" * 60)
        print("\nYou can now run the dashboard without errors:")
        print("  streamlit run scripts/session_dashboard.py")
        print("\nOr use the launcher:")
        print("  run_dashboard.bat")
    else:
        print("\n[FAIL] Could not create new session")
        print("Check SessionManager installation")

    return success


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
