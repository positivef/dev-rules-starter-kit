#!/usr/bin/env python3
"""
Session Simulator - 대시보드 테스트용 실시간 데이터 생성기

Features:
- 실시간으로 작업 시뮬레이션
- 성공/실패 랜덤 생성
- 다양한 작업 유형 테스트
- 실제와 유사한 패턴 생성

Usage:
    python scripts/session_simulator.py
    python scripts/session_simulator.py --tasks 10 --interval 5
"""

import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from session_manager import SessionManager
from task_executor_session_hook import TaskExecutorSessionHook


class SessionSimulator:
    """세션 데이터 시뮬레이터"""

    def __init__(self):
        """초기화"""
        self.session = SessionManager.get_instance()
        self.hook = TaskExecutorSessionHook()

        # 작업 템플릿
        self.task_templates = [
            ("FEAT", "새 기능 구현"),
            ("FIX", "버그 수정"),
            ("TEST", "테스트 실행"),
            ("DOCS", "문서 작성"),
            ("REFACTOR", "코드 리팩토링"),
            ("PERF", "성능 최적화"),
            ("STYLE", "코드 스타일 개선"),
            ("BUILD", "빌드 시스템 업데이트"),
        ]

        # 명령어 템플릿
        self.command_templates = [
            ("python", "scripts/test.py"),
            ("pytest", "tests/"),
            ("ruff", "check"),
            ("mypy", "."),
            ("git", "status"),
            ("npm", "test"),
            ("docker", "build"),
            ("make", "all"),
        ]

        # 에러 메시지 템플릿
        self.error_templates = [
            "Connection timeout: Server not responding",
            "Test failed: Expected value not found",
            "Build error: Dependency not satisfied",
            "Syntax error: Unexpected token",
            "Runtime error: Division by zero",
            "Permission denied: Access restricted",
            "File not found: Path does not exist",
            "Memory error: Out of memory",
        ]

    def generate_task_id(self) -> str:
        """작업 ID 생성"""
        task_type = random.choice([t[0] for t in self.task_templates])
        date_str = datetime.now().strftime("%Y-%m-%d")
        random_num = random.randint(1, 99)
        return f"{task_type}-{date_str}-{random_num:02d}"

    def simulate_task(self) -> Dict[str, Any]:
        """작업 시뮬레이션"""
        # 작업 선택
        task_type, task_title = random.choice(self.task_templates)
        task_id = self.generate_task_id()

        # 작업 데이터
        task_data = {"task_id": task_id, "title": f"{task_title} - {random.randint(1, 100)}", "_simulated": True}

        print(f"\n[SIMULATOR] Starting task: {task_id}")
        print(f"            Title: {task_data['title']}")

        # 작업 시작
        self.hook.on_task_start(task_data)

        # 명령 실행 시뮬레이션 (1-5개)
        num_commands = random.randint(1, 5)
        for _ in range(num_commands):
            cmd, args = random.choice(self.command_templates)
            # 80% 성공률
            exit_code = 0 if random.random() < 0.8 else 1

            self.hook.on_command_execute(
                [cmd, args], exit_code, f"Output from {cmd}", "" if exit_code == 0 else "Error output"
            )

            print(f"            Command: {cmd} {args} -> {'OK' if exit_code == 0 else 'FAIL'}")
            time.sleep(0.5)  # 명령 간 지연

        # 실행 시간 (5-120초)
        execution_time = random.uniform(5, 120)

        # 성공/실패 결정 (70% 성공률)
        success = random.random() < 0.7
        error_msg = None if success else random.choice(self.error_templates)

        # 작업 완료
        self.hook.on_task_complete(task_data, success, execution_time, error_msg)

        result = "SUCCESS" if success else "FAILED"
        print(f"            Result: {result} ({execution_time:.1f}s)")
        if error_msg:
            print(f"            Error: {error_msg}")

        return {"task_id": task_id, "success": success, "execution_time": execution_time, "error": error_msg}

    def simulate_session(self, num_tasks: int = 10, interval: float = 5.0):
        """세션 시뮬레이션

        Args:
            num_tasks: 시뮬레이션할 작업 수
            interval: 작업 간 간격 (초)
        """
        print("\n" + "=" * 60)
        print("Session Simulator Started")
        print("=" * 60)
        print(f"Tasks to simulate: {num_tasks}")
        print(f"Interval: {interval}s")
        print(f"Session ID: {self.session.session_id}")
        print("=" * 60)

        # 세션 시작
        self.session.start(resume_last=False)

        results = {"total": 0, "success": 0, "failed": 0, "total_time": 0}

        try:
            for i in range(num_tasks):
                print(f"\n[Task {i+1}/{num_tasks}]")

                # 작업 시뮬레이션
                result = self.simulate_task()

                # 통계 업데이트
                results["total"] += 1
                if result["success"]:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                results["total_time"] += result["execution_time"]

                # 진행률 표시
                progress = (i + 1) / num_tasks * 100
                print(f"\n[Progress: {progress:.0f}%]")

                # 다음 작업까지 대기
                if i < num_tasks - 1:
                    print(f"Waiting {interval}s before next task...")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Simulation stopped by user")

        # 최종 통계
        print("\n" + "=" * 60)
        print("Simulation Complete")
        print("=" * 60)
        print(f"Total tasks: {results['total']}")
        print(f"Success: {results['success']} ({results['success']/results['total']*100:.1f}%)")
        print(f"Failed: {results['failed']}")
        print(f"Total execution time: {results['total_time']:.1f}s")
        print(f"Average time per task: {results['total_time']/results['total']:.1f}s")

        # 체크포인트 생성
        self.session.checkpoint()
        print("\n[CHECKPOINT] Session data saved")

        # 실행 요약
        summary = self.hook.get_execution_summary()
        print("\n[SUMMARY]")
        print(f"Session total executions: {summary.get('total_executions', 0)}")
        print(f"Session success rate: {summary.get('success_rate', 0):.1f}%")

    def continuous_simulation(self, interval: float = 5.0):
        """연속 시뮬레이션 (Ctrl+C로 중단)

        Args:
            interval: 작업 간 간격 (초)
        """
        print("\n" + "=" * 60)
        print("Continuous Simulation Mode")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print("=" * 60)

        self.session.start(resume_last=False)
        task_count = 0

        try:
            while True:
                task_count += 1
                print(f"\n[Task #{task_count}]")
                self.simulate_task()
                print(f"Waiting {interval}s...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n[STOPPED] Simulated {task_count} tasks")
            self.session.checkpoint()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Session data simulator for dashboard testing")
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks to simulate (default: 10)")
    parser.add_argument("--interval", type=float, default=5.0, help="Interval between tasks in seconds (default: 5.0)")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode (Ctrl+C to stop)")
    parser.add_argument("--fast", action="store_true", help="Fast mode with 1 second intervals")

    args = parser.parse_args()

    # Fast mode
    if args.fast:
        args.interval = 1.0

    # 시뮬레이터 생성
    simulator = SessionSimulator()

    # 실행 모드
    if args.continuous:
        simulator.continuous_simulation(interval=args.interval)
    else:
        simulator.simulate_session(num_tasks=args.tasks, interval=args.interval)


if __name__ == "__main__":
    main()
