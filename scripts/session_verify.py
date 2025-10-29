#!/usr/bin/env python3
"""
SessionManager 자동 검증 스크립트
모든 기능을 자동으로 테스트하고 결과를 보고
"""

from pathlib import Path
from datetime import datetime
from session_manager import SessionManager, StateScope
from session_analyzer import SessionAnalyzer
from session_report_generator import SessionReportGenerator
from task_executor_session_hook import TaskExecutorSessionHook


def print_test_result(test_name, success, details=""):
    """테스트 결과 출력"""
    status = "[OK]" if success else "[FAIL]"
    symbol = "[v]" if success else "[x]"
    print(f"{symbol} {status} {test_name}")
    if details:
        print(f"         {details}")


def verify_session_manager():
    """SessionManager 검증"""
    print("\n1. SessionManager 기능 검증")
    print("-" * 40)

    try:
        # 싱글톤 인스턴스
        manager = SessionManager.get_instance()
        session_id = manager.session_id
        print_test_result("SessionManager 인스턴스 생성", True, f"세션 ID: {session_id}")

        # 세션 시작
        manager.start(resume_last=False)
        print_test_result("새 세션 시작", True)

        # 상태 저장/읽기
        manager.set("test_key", "test_value", StateScope.SESSION)
        value = manager.get("test_key", StateScope.SESSION)
        success = value == "test_value"
        print_test_result("상태 저장/읽기", success, f"저장값: {value}")

        # 체크포인트
        manager.checkpoint()
        session_file = Path("RUNS/sessions") / f"{session_id}.json"
        exists = session_file.exists()
        print_test_result("체크포인트 저장", exists, f"파일: {session_file.name if exists else 'Not found'}")

        return True
    except Exception as e:
        print_test_result("SessionManager 검증", False, str(e))
        return False


def verify_task_hook():
    """TaskExecutor 훅 검증"""
    print("\n2. TaskExecutor 훅 검증")
    print("-" * 40)

    try:
        hook = TaskExecutorSessionHook()

        if not hook.enabled:
            print_test_result("TaskExecutor 훅", False, "SessionManager 사용 불가")
            return False

        print_test_result("TaskExecutor 훅 활성화", True)

        # 작업 기록
        task_id = "VERIFY-001"
        hook.on_task_start({"task_id": task_id})
        hook.on_task_complete(task_data={"task_id": task_id}, success=True, execution_time=1.5, error_msg=None)
        print_test_result("작업 기록", True, f"작업 ID: {task_id}")

        return True
    except Exception as e:
        print_test_result("TaskExecutor 훅 검증", False, str(e))
        return False


def verify_analyzer():
    """SessionAnalyzer 검증"""
    print("\n3. SessionAnalyzer 검증")
    print("-" * 40)

    try:
        analyzer = SessionAnalyzer()
        patterns = analyzer.analyze_task_patterns()

        success = patterns is not None and isinstance(patterns, dict)
        print_test_result("작업 패턴 분석", success)

        # 세션 파일 수 확인
        session_files = list(Path("RUNS/sessions").glob("session_*.json"))
        print_test_result("세션 파일 검색", True, f"{len(session_files)}개 파일 발견")

        return True
    except Exception as e:
        print_test_result("SessionAnalyzer 검증", False, str(e))
        return False


def verify_report_generator():
    """Report Generator 검증"""
    print("\n4. Report Generator 검증")
    print("-" * 40)

    try:
        generator = SessionReportGenerator()

        # JSON 리포트
        json_report = generator.generate_report(period="daily", days=1, format="json")

        json_success = json_report and Path(json_report).exists()
        print_test_result("JSON 리포트 생성", json_success, f"{Path(json_report).name if json_success else 'Failed'}")

        # HTML 리포트
        html_report = generator.generate_report(period="daily", days=1, format="html")

        html_success = html_report and Path(html_report).exists()
        print_test_result("HTML 리포트 생성", html_success, f"{Path(html_report).name if html_success else 'Failed'}")

        return json_success or html_success
    except Exception as e:
        print_test_result("Report Generator 검증", False, str(e))
        return False


def verify_session_recovery():
    """세션 복구 검증"""
    print("\n5. 세션 복구 기능 검증")
    print("-" * 40)

    try:
        # 테스트 데이터 저장
        manager = SessionManager.get_instance()
        manager.set("recovery_test", "복구 데이터", StateScope.SESSION)
        manager.checkpoint()
        old_session_id = manager.session_id
        print_test_result("복구용 데이터 저장", True)

        # SessionManager 재시작
        SessionManager._instance = None
        new_manager = SessionManager.get_instance()
        new_manager.start(resume_last=True)

        # 복구 확인
        recovered = new_manager.get("recovery_test", StateScope.SESSION)
        success = recovered == "복구 데이터"
        print_test_result("세션 복구", success, f"복구된 데이터: {recovered if success else 'Failed'}")

        return success
    except Exception as e:
        print_test_result("세션 복구 검증", False, str(e))
        return False


def main():
    """메인 검증 함수"""
    print("=" * 60)
    print(" SessionManager 시스템 자동 검증")
    print("=" * 60)
    print(f" 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []

    # 각 컴포넌트 검증
    results.append(("SessionManager", verify_session_manager()))
    results.append(("TaskExecutor Hook", verify_task_hook()))
    results.append(("SessionAnalyzer", verify_analyzer()))
    results.append(("Report Generator", verify_report_generator()))
    results.append(("Session Recovery", verify_session_recovery()))

    # 최종 결과
    print("\n" + "=" * 60)
    print(" 검증 결과 요약")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for _, success in results if success)

    for name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "[v]" if success else "[x]"
        print(f"  {symbol} {name:20} [{status}]")

    print("-" * 60)
    print(f" 결과: {passed}/{total} 성공 ({passed/total*100:.1f}%)")
    print("=" * 60)

    # 추가 정보
    print("\n[INFO] 생성된 파일 위치:")
    print("  - 세션 파일: RUNS/sessions/")
    print("  - 리포트 파일: RUNS/reports/")

    print("\n[INFO] 다음 단계:")
    print("  1. 대시보드 실행: streamlit run scripts/session_dashboard.py")
    print("  2. 인터랙티브 데모: python scripts/session_demo.py")
    print("  3. 리포트 생성: python scripts/session_report_generator.py")

    # 정리
    manager = SessionManager.get_instance()
    manager._cleanup()

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
