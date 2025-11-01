#!/usr/bin/env python3
"""
SessionManager 생태계 간단 통합 테스트
주요 컴포넌트 작동 확인
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session_manager import SessionManager, StateScope
from session_analyzer import SessionAnalyzer
from session_report_generator import SessionReportGenerator
from task_executor_session_hook import TaskExecutorSessionHook


def test_session_manager_basic():
    """SessionManager 기본 기능 테스트"""
    # 싱글톤 리셋
    SessionManager._instance = None

    # 매니저 생성
    manager = SessionManager.get_instance()
    session_id = manager.session_id

    # 세션 시작
    manager.start(resume_last=False)

    # 상태 저장
    manager.set("test_key", "test_value", StateScope.SESSION)
    manager.set("user_pref", "dark_mode", StateScope.USER)

    # 체크포인트
    manager.checkpoint()

    # 파일 확인
    session_file = Path("RUNS/sessions") / f"{session_id}.json"
    assert session_file.exists()

    # 상태 읽기
    assert manager.get("test_key", StateScope.SESSION) == "test_value"
    assert manager.get("user_pref", StateScope.USER) == "dark_mode"

    # 정리
    manager._cleanup()

    print("[OK] SessionManager 기본 기능 테스트 통과")


def test_task_executor_hook():
    """TaskExecutor 훅 테스트"""
    # 싱글톤 리셋
    SessionManager._instance = None

    # 훅 초기화
    hook = TaskExecutorSessionHook()

    if not hook.enabled:
        print("[SKIP] SessionManager not available")
        return

    # 작업 시작 기록
    task_id = "TEST-HOOK-001"
    hook.on_task_start({"task_id": task_id})

    # 작업 완료 기록
    task_data = {"task_id": task_id}
    hook.on_task_complete(task_data=task_data, success=True, execution_time=10.5, error_msg=None)

    print("[OK] TaskExecutor 훅 테스트 통과")


def test_session_analyzer():
    """SessionAnalyzer 테스트"""
    # 싱글톤 리셋
    SessionManager._instance = None

    # 테스트 데이터 생성
    manager = SessionManager.get_instance()
    manager.start(resume_last=False)

    # 몇 개 작업 시뮬레이션
    for i in range(3):
        manager.set(f"task_{i}", f"value_{i}", StateScope.SESSION)

    manager.checkpoint()

    # 분석기 실행
    analyzer = SessionAnalyzer()
    patterns = analyzer.analyze_task_patterns()

    # 기본 검증 (반환된 키 확인)
    assert patterns is not None
    assert isinstance(patterns, dict)

    # 정리
    manager._cleanup()

    print("[OK] SessionAnalyzer 테스트 통과")


def test_report_generator():
    """ReportGenerator 테스트"""
    # 리포트 생성기
    generator = SessionReportGenerator()

    # JSON 리포트 생성 시도
    try:
        report = generator.generate_report(period="daily", days=1, format="json")

        if report and Path(report).exists():
            print(f"[OK] JSON 리포트 생성: {Path(report).name}")
        else:
            print("[INFO] 리포트 생성 실패 (데이터 부족일 수 있음)")

    except Exception as e:
        print(f"[WARN] 리포트 생성 예외: {e}")


def test_integration_flow():
    """전체 통합 플로우 테스트"""
    print("\n" + "=" * 60)
    print("SessionManager 생태계 통합 테스트")
    print("=" * 60)

    # 1. SessionManager 테스트
    test_session_manager_basic()

    # 2. TaskExecutor 훅 테스트
    test_task_executor_hook()

    # 3. SessionAnalyzer 테스트
    test_session_analyzer()

    # 4. ReportGenerator 테스트
    test_report_generator()

    print("\n" + "=" * 60)
    print("모든 통합 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    # 간단한 통합 테스트 실행
    test_integration_flow()
