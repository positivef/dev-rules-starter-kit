#!/usr/bin/env python3
"""
고급 SessionManager 통합 테스트
- TaskExecutor 훅 테스트
- 세션 분석 도구 테스트
"""

import pytest
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.session_manager import SessionManager, StateScope
from scripts.task_executor_session_hook import TaskExecutorSessionHook
from scripts.session_analyzer import SessionAnalyzer


@pytest.mark.skip(reason="Session state management needs refactoring for test isolation")
def test_task_executor_hook():
    """TaskExecutor 훅 통합 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] TaskExecutor SessionManager Hook")
    print("=" * 60)

    # 새로운 세션으로 시작
    SessionManager._instance = None
    session = SessionManager.get_instance()
    session.start(resume_last=False)

    # 훅 생성 (이미 생성된 SessionManager 인스턴스를 사용)
    hook = TaskExecutorSessionHook()

    # 훅 활성화 확인
    assert hook.enabled, "SessionManager 훅이 활성화되어야 함"
    print("[OK] 훅 활성화 확인")

    # 1. 작업 시작 테스트
    print("\n1. 작업 시작 기록 테스트")
    test_task = {"task_id": "TEST-2025-10-26-01", "title": "통합 테스트 작업", "_file_path": "TASKS/TEST-2025-10-26-01.yaml"}

    hook.on_task_start(test_task)

    # 세션에서 작업 정보 확인
    current_task = session.get("current_task", StateScope.SESSION)
    assert current_task is not None, "현재 작업이 기록되어야 함"
    assert current_task["task_id"] == "TEST-2025-10-26-01"
    assert current_task["status"] == "running"
    print(f"  [OK] 작업 시작 기록: {current_task['task_id']}")

    # 2. 명령 실행 기록 테스트
    print("\n2. 명령 실행 기록 테스트")
    hook.on_command_execute(["python", "test.py"], result_code=0, stdout="Test output", stderr="")

    command_log = session.get("command_log", StateScope.TEMP, [])
    assert len(command_log) > 0, "명령 로그가 기록되어야 함"
    assert command_log[-1]["command"] == "python test.py"
    print(f"  [OK] 명령 기록: {command_log[-1]['command']}")

    # 3. 작업 성공 완료 테스트
    print("\n3. 작업 성공 완료 테스트")
    hook.on_task_complete(test_task, success=True, execution_time=5.5)

    # 완료 상태 확인
    current_task = session.get("current_task", StateScope.SESSION)
    assert current_task["status"] == "success"
    assert current_task["execution_time"] == 5.5
    print(f"  [OK] 작업 성공 기록: {current_task['status']}")

    # 통계 확인
    stats = session.get("execution_stats", StateScope.USER, {})
    assert stats["total_executions"] == 1
    assert stats["successful"] == 1
    print(f"  [OK] 통계 업데이트: 성공 {stats['successful']}회")

    # 4. 작업 실패 테스트
    print("\n4. 작업 실패 테스트")
    failed_task = {"task_id": "TEST-2025-10-26-02", "title": "실패할 작업"}

    hook.on_task_start(failed_task)
    hook.on_task_complete(failed_task, success=False, execution_time=2.3, error_msg="Test error: Something went wrong")

    # 실패 기록 확인
    failed_tasks = session.get("failed_tasks", StateScope.SESSION, {})
    assert "TEST-2025-10-26-02" in failed_tasks
    assert "Test error" in failed_tasks["TEST-2025-10-26-02"]["error"]
    print("  [OK] 작업 실패 기록됨")

    # 5. 실행 요약 테스트
    print("\n5. 실행 요약 테스트")
    summary = hook.get_execution_summary()
    print(f"  총 실행: {summary['total_executions']}")
    print(f"  성공: {summary['successful']}")
    print(f"  실패: {summary['failed']}")
    print(f"  성공률: {summary['success_rate']:.1f}%")
    print(f"  평균 실행 시간: {summary['avg_execution_time']:.2f}초")

    assert summary["total_executions"] == 2
    assert summary["successful"] == 1
    assert summary["failed"] == 1
    assert summary["success_rate"] == 50.0
    print("  [OK] 실행 요약 정확함")

    # 체크포인트 생성
    session.checkpoint()

    print("\n" + "=" * 60)
    print("[SUCCESS] TaskExecutor 훅 테스트 완료!")
    print("=" * 60)

    return True


def test_session_analyzer():
    """세션 분석 도구 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] Session Analyzer")
    print("=" * 60)

    # 분석기 생성
    analyzer = SessionAnalyzer()

    # 세션 로드
    print("\n1. 세션 데이터 로드")
    session_count = analyzer.load_sessions(days=30)
    print(f"  로드된 세션: {session_count}개")

    if session_count == 0:
        print("  [INFO] 분석할 세션이 없음 - 샘플 데이터 생성")
        create_sample_sessions()
        session_count = analyzer.load_sessions(days=30)
        print(f"  재로드된 세션: {session_count}개")

    # 작업 패턴 분석
    print("\n2. 작업 패턴 분석")
    task_patterns = analyzer.analyze_task_patterns()

    print(f"  고유 작업 수: {task_patterns['total_unique_tasks']}")
    print(f"  실패한 작업 유형: {task_patterns['total_failed_tasks']}")

    if task_patterns["most_frequent_tasks"]:
        print("  자주 실행한 작업:")
        for task, count in task_patterns["most_frequent_tasks"][:3]:
            print(f"    - {task}: {count}회")

    # 생산성 분석
    print("\n3. 생산성 패턴 분석")
    productivity = analyzer.analyze_productivity()

    print(f"  총 세션 수: {productivity['total_sessions']}")
    print(f"  평균 세션 시간: {productivity['avg_session_duration_minutes']:.0f}분")

    if productivity["peak_hours"]:
        peak_hours_str = ", ".join([f"{h[0]}시" for h in productivity["peak_hours"][:3]])
        print(f"  가장 활동적인 시간: {peak_hours_str}")

    # 에러 패턴 분석
    print("\n4. 에러 패턴 분석")
    error_patterns = analyzer.analyze_error_patterns()

    print(f"  고유 에러 유형: {error_patterns['total_unique_errors']}")
    print(f"  총 에러 횟수: {error_patterns['total_errors']}")

    if error_patterns["common_errors"]:
        print("  자주 발생한 에러:")
        for error, count in error_patterns["common_errors"][:2]:
            error_short = error[:50] + "..." if len(error) > 50 else error
            print(f"    - {error_short}: {count}회")

    # 통계 계산
    print("\n5. 전체 실행 통계")
    stats = analyzer.get_execution_stats()

    print(f"  총 작업: {stats['total_tasks']}")
    print(f"  성공: {stats['successful_tasks']}")
    print(f"  실패: {stats['failed_tasks']}")
    print(f"  성공률: {stats['success_rate']:.1f}%")
    print(f"  총 실행 시간: {stats['total_execution_hours']:.2f}시간")

    # 전체 분석 실행
    print("\n6. 전체 분석 및 통찰 생성")
    results = analyzer.analyze_all(days=30)
    insights = results.get("insights", {})

    if insights.get("positive_patterns"):
        print("  [긍정적 패턴]")
        for pattern in insights["positive_patterns"][:2]:
            print(f"    - {pattern}")

    if insights.get("warnings"):
        print("  [주의사항]")
        for warning in insights["warnings"][:2]:
            print(f"    - {warning}")

    if insights.get("recommendations"):
        print("  [개선 제안]")
        for rec in insights["recommendations"][:2]:
            print(f"    - {rec}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Session Analyzer 테스트 완료!")
    print("=" * 60)

    return True


def create_sample_sessions():
    """테스트용 샘플 세션 생성"""
    print("  샘플 세션 데이터 생성 중...")

    session = SessionManager.get_instance()
    session.start(resume_last=False)

    # 여러 작업 시뮬레이션
    tasks = [
        ("FEAT-2025-10-26-01", "기능 개발", True, 45.5),
        ("TEST-2025-10-26-01", "테스트 실행", True, 12.3),
        ("FIX-2025-10-26-01", "버그 수정", False, 8.7),
        ("FEAT-2025-10-26-02", "다른 기능", True, 67.2),
        ("TEST-2025-10-26-02", "테스트 실행", False, 15.1),
    ]

    for task_id, title, success, exec_time in tasks:
        # 작업 시작
        session.set(
            "current_task",
            {"task_id": task_id, "title": title, "status": "running", "started_at": datetime.now(timezone.utc).isoformat()},
            StateScope.SESSION,
        )

        # 작업 완료
        if success:
            completed = session.get("completed_tasks", StateScope.SESSION, [])
            completed.append(task_id)
            session.set("completed_tasks", completed, StateScope.SESSION)
        else:
            failed = session.get("failed_tasks", StateScope.SESSION, {})
            failed[task_id] = {"error": f"Sample error for {task_id}", "timestamp": datetime.now(timezone.utc).isoformat()}
            session.set("failed_tasks", failed, StateScope.SESSION)

        # 통계 업데이트
        stats = session.get("execution_stats", StateScope.USER, {})
        stats["total_executions"] = stats.get("total_executions", 0) + 1
        if success:
            stats["successful"] = stats.get("successful", 0) + 1
        else:
            stats["failed"] = stats.get("failed", 0) + 1
        stats["total_time"] = stats.get("total_time", 0) + exec_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        session.set("execution_stats", stats, StateScope.USER)

    # 명령 로그 추가
    command_log = [
        {"command": "python scripts/test.py", "exit_code": 0, "timestamp": datetime.now(timezone.utc).isoformat()},
        {"command": "pytest tests/", "exit_code": 0, "timestamp": datetime.now(timezone.utc).isoformat()},
        {"command": "ruff check", "exit_code": 1, "timestamp": datetime.now(timezone.utc).isoformat()},
    ]
    session.set("command_log", command_log, StateScope.TEMP)

    # 체크포인트 생성
    session.checkpoint()
    print("  샘플 데이터 생성 완료")


def run_integration_demo():
    """통합 데모 실행"""
    print("\n" + "=" * 70)
    print(" " * 20 + "SessionManager 고급 통합 데모")
    print("=" * 70)

    # 훅 생성 및 시뮬레이션
    hook = TaskExecutorSessionHook()

    # 실제 작업 시뮬레이션
    print("\n[DEMO] 실제 TaskExecutor 작업 시뮬레이션")

    tasks = [
        {
            "task_id": "FEAT-2025-10-26-AUTH",
            "title": "인증 시스템 구현",
            "success": True,
            "time": 120.5,
            "commands": [("python", "scripts/auth.py", 0), ("pytest", "tests/test_auth.py", 0)],
        },
        {
            "task_id": "FIX-2025-10-26-DB",
            "title": "데이터베이스 연결 버그 수정",
            "success": False,
            "time": 45.3,
            "error": "Connection timeout: Database server not responding",
            "commands": [("python", "scripts/db_fix.py", 1)],
        },
        {
            "task_id": "TEST-2025-10-26-E2E",
            "title": "E2E 테스트 실행",
            "success": True,
            "time": 180.7,
            "commands": [("npm", "test:e2e", 0)],
        },
    ]

    for task_info in tasks:
        print(f"\n실행: {task_info['title']}")

        # 작업 시작
        task_data = {"task_id": task_info["task_id"], "title": task_info["title"]}
        hook.on_task_start(task_data)

        # 명령 실행
        for cmd, script, code in task_info.get("commands", []):
            hook.on_command_execute([cmd, script], code)
            print(f"  명령: {cmd} {script} -> {'성공' if code == 0 else '실패'}")

        # 작업 완료
        time.sleep(0.1)  # 시뮬레이션 지연
        hook.on_task_complete(
            task_data, success=task_info["success"], execution_time=task_info["time"], error_msg=task_info.get("error")
        )

        result = "성공" if task_info["success"] else "실패"
        print(f"  결과: {result} ({task_info['time']:.1f}초)")

    # 최종 요약
    print("\n" + "-" * 60)
    summary = hook.get_execution_summary()
    print("[최종 실행 요약]")
    print(f"총 작업: {summary['total_executions']}")
    print(f"성공: {summary['successful']} ({summary['success_rate']:.1f}%)")
    print(f"실패: {summary['failed']}")
    print(f"평균 실행 시간: {summary['avg_execution_time']:.1f}초")
    print(f"총 실행 시간: {summary['total_time']:.1f}초")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SessionManager 고급 통합 테스트")
    parser.add_argument("--demo", action="store_true", help="통합 데모 실행")
    parser.add_argument("--analyze", action="store_true", help="세션 분석만 실행")

    args = parser.parse_args()

    if args.demo:
        run_integration_demo()
    elif args.analyze:
        test_session_analyzer()
    else:
        # 전체 테스트 실행
        test_task_executor_hook()
        test_session_analyzer()
        print("\n[FINAL] 모든 고급 통합 테스트 성공!")
