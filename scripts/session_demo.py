#!/usr/bin/env python3
"""
SessionManager 데모 및 검증 스크립트
사용자가 직접 각 기능을 확인할 수 있는 인터랙티브 데모
"""

import time
import json
from pathlib import Path
from datetime import datetime
from session_manager import SessionManager, StateScope
from session_analyzer import SessionAnalyzer
from session_report_generator import SessionReportGenerator
from task_executor_session_hook import TaskExecutorSessionHook


def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def demo_session_manager():
    """SessionManager 기본 기능 데모"""
    print_header("1. SessionManager 기본 기능 테스트")

    # 싱글톤 인스턴스
    manager = SessionManager.get_instance()
    print("✓ SessionManager 인스턴스 생성됨")
    print(f"  - 세션 ID: {manager.session_id}")

    # 세션 시작
    manager.start(resume_last=False)  # 새로운 세션으로 시작
    print("✓ 새 세션 시작됨")

    # 상태 저장 테스트
    print("\n상태 저장 테스트:")

    # SESSION 스코프
    manager.set("current_task", "데모 실행 중", StateScope.SESSION)
    print("  - SESSION 스코프: current_task = '데모 실행 중'")

    # USER 스코프
    manager.set("user_name", "테스트 사용자", StateScope.USER)
    print("  - USER 스코프: user_name = '테스트 사용자'")

    # APP 스코프
    manager.set("app_version", "1.0.0", StateScope.APP)
    print("  - APP 스코프: app_version = '1.0.0'")

    # 상태 읽기 테스트
    print("\n상태 읽기 테스트:")
    task = manager.get("current_task", StateScope.SESSION)
    user = manager.get("user_name", StateScope.USER)
    version = manager.get("app_version", StateScope.APP)

    print(f"  - current_task: {task}")
    print(f"  - user_name: {user}")
    print(f"  - app_version: {version}")

    # 체크포인트 저장
    print("\n체크포인트 저장:")
    manager.checkpoint()

    # 세션 파일 확인
    session_file = Path("RUNS/sessions") / f"{manager.session_id}.json"
    if session_file.exists():
        print(f"✓ 세션 파일 생성됨: {session_file.name}")
        print(f"  - 파일 크기: {session_file.stat().st_size} bytes")
    else:
        print("✗ 세션 파일이 생성되지 않음")

    return manager


def demo_task_hook():
    """TaskExecutor 훅 데모"""
    print_header("2. TaskExecutor 훅 테스트")

    hook = TaskExecutorSessionHook()

    if not hook.enabled:
        print("✗ SessionManager를 사용할 수 없습니다")
        return

    print("✓ TaskExecutor 훅 활성화됨")

    # 작업 시뮬레이션
    tasks = [
        ("DEMO-001", True, 2.5),
        ("DEMO-002", True, 1.8),
        ("DEMO-003", False, 3.2),
    ]

    print("\n작업 실행 시뮬레이션:")
    for task_id, success, duration in tasks:
        # 작업 시작
        hook.on_task_start({"task_id": task_id})

        # 작업 수행 (시뮬레이션)
        time.sleep(0.5)

        # 작업 완료
        status = "성공" if success else "실패"
        hook.on_task_complete(
            task_data={"task_id": task_id},
            success=success,
            execution_time=duration,
            error_msg=None if success else "시뮬레이션 에러",
        )

        print(f"  - {task_id}: {status} ({duration:.1f}초)")

    print("\n✓ 3개 작업 기록 완료")


def demo_analyzer():
    """SessionAnalyzer 데모"""
    print_header("3. SessionAnalyzer 분석 테스트")

    analyzer = SessionAnalyzer()

    # 작업 패턴 분석
    patterns = analyzer.analyze_task_patterns()

    print("작업 패턴 분석 결과:")
    if patterns:
        for key, value in list(patterns.items())[:5]:  # 상위 5개만 표시
            print(f"  - {key}: {value}")
    else:
        print("  - 분석할 데이터가 없습니다")

    # 세션 파일 수 확인
    session_files = list(Path("RUNS/sessions").glob("session_*.json"))
    print(f"\n현재 저장된 세션 파일: {len(session_files)}개")

    if session_files:
        recent = max(session_files, key=lambda p: p.stat().st_mtime)
        print(f"  - 최근 세션: {recent.name}")
        print(f"  - 수정 시간: {datetime.fromtimestamp(recent.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")


def demo_report_generator():
    """Report Generator 데모"""
    print_header("4. Report Generator 테스트")

    generator = SessionReportGenerator()

    print("리포트 생성 중...")

    # JSON 리포트 생성
    json_report = generator.generate_report(period="daily", days=1, format="json")

    if json_report and Path(json_report).exists():
        print(f"✓ JSON 리포트 생성됨: {Path(json_report).name}")

        # 리포트 내용 일부 표시
        with open(json_report, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("\n리포트 요약:")
        if "analysis" in data and "execution_stats" in data["analysis"]:
            stats = data["analysis"]["execution_stats"]
            print(f"  - 총 작업 수: {stats.get('total_tasks', 0)}")
            print(f"  - 성공률: {stats.get('success_rate', 0):.1f}%")
            print(f"  - 평균 실행 시간: {stats.get('avg_execution_time', 0):.1f}초")
    else:
        print("✗ 리포트 생성 실패 (데이터 부족일 수 있음)")

    # HTML 리포트 생성
    html_report = generator.generate_report(period="daily", days=1, format="html")

    if html_report and Path(html_report).exists():
        print(f"✓ HTML 리포트 생성됨: {Path(html_report).name}")
        print(f"  - 브라우저에서 확인: file:///{Path(html_report).absolute()}")


def demo_session_recovery():
    """세션 복구 데모"""
    print_header("5. 세션 복구 테스트")

    # 현재 세션 정보 저장
    manager = SessionManager.get_instance()
    old_session_id = manager.session_id

    # 테스트 데이터 저장
    manager.set("test_before_crash", "복구될 데이터", StateScope.SESSION)
    manager.checkpoint()
    print("✓ 테스트 데이터 저장됨: 'test_before_crash' = '복구될 데이터'")

    # SessionManager 재시작 시뮬레이션
    print("\n프로그램 재시작 시뮬레이션...")
    SessionManager._instance = None

    # 새 인스턴스로 복구 시도
    new_manager = SessionManager.get_instance()
    new_manager.start(resume_last=True)  # 마지막 세션 복구

    # 복구 확인
    if hasattr(new_manager, "current_state") and new_manager.current_state:
        print("✓ 세션 복구 성공!")

        # 복구된 데이터 확인
        recovered_data = new_manager.get("test_before_crash", StateScope.SESSION)
        if recovered_data == "복구될 데이터":
            print(f"✓ 데이터 복구 확인: '{recovered_data}'")
        else:
            print("✗ 데이터 복구 실패")
    else:
        print("✗ 세션 복구 실패")


def interactive_menu():
    """인터랙티브 메뉴"""
    while True:
        print_header("SessionManager 데모 프로그램")
        print("""
1. SessionManager 기본 기능 테스트
2. TaskExecutor 훅 테스트
3. SessionAnalyzer 분석 테스트
4. Report Generator 테스트
5. 세션 복구 테스트
6. 전체 테스트 실행
7. Streamlit 대시보드 실행 명령 보기
0. 종료
        """)

        choice = input("선택하세요 (0-7): ").strip()

        if choice == "1":
            demo_session_manager()
        elif choice == "2":
            demo_task_hook()
        elif choice == "3":
            demo_analyzer()
        elif choice == "4":
            demo_report_generator()
        elif choice == "5":
            demo_session_recovery()
        elif choice == "6":
            # 전체 테스트 실행
            manager = demo_session_manager()
            demo_task_hook()
            demo_analyzer()
            demo_report_generator()
            demo_session_recovery()
            print_header("모든 테스트 완료!")
        elif choice == "7":
            print_header("Streamlit 대시보드 실행 방법")
            print("\n다른 터미널에서 다음 명령을 실행하세요:")
            print("\n  streamlit run scripts/session_dashboard.py")
            print("\n브라우저가 자동으로 열립니다 (http://localhost:8501)")
        elif choice == "0":
            print("\n종료합니다...")
            # 정리
            manager = SessionManager.get_instance()
            manager._cleanup()
            break
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

        input("\n계속하려면 Enter를 누르세요...")


def main():
    """메인 함수"""
    print_header("SessionManager 시스템 검증 데모")
    print("""
이 프로그램은 SessionManager 생태계의 모든 기능을 테스트합니다.
각 메뉴를 선택하여 기능을 확인할 수 있습니다.
    """)

    # 인터랙티브 메뉴 실행
    interactive_menu()


if __name__ == "__main__":
    main()
