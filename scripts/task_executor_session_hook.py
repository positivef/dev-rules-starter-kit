#!/usr/bin/env python3
"""
TaskExecutor SessionManager Hook - Loose coupling module
Integrates TaskExecutor and SessionManager without dependencies

Features:
- Automatic session recording on TaskExecutor execution
- Failure/success status tracking
- Execution time and metric collection
- TaskExecutor works normally without SessionManager
"""

import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class TaskExecutorSessionHook:
    """
    TaskExecutor를 위한 선택적 SessionManager 통합

    이 클래스는 TaskExecutor와 SessionManager를 느슨하게 연결합니다.
    SessionManager가 없어도 TaskExecutor는 정상 작동합니다.
    """

    def __init__(self):
        """느슨한 통합 초기화"""
        self.session_manager = None
        self.state_scope = None
        self.enabled = False

        # SessionManager 가져오기 시도 (없으면 무시)
        try:
            # 현재 스크립트와 같은 디렉토리에서 import
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent))

            from session_manager import SessionManager, StateScope

            self.session_manager = SessionManager.get_instance()
            self.state_scope = StateScope
            self.enabled = True
            print("[SESSION_HOOK] SessionManager 통합 활성화")
        except ImportError as e:
            print(f"[SESSION_HOOK] SessionManager 없음 - 독립 실행 모드: {e}")
        except Exception as e:
            print(f"[SESSION_HOOK] SessionManager 로드 실패: {e}")

    def on_task_start(self, task_data: Dict[str, Any]) -> None:
        """
        작업 시작 시 호출

        Args:
            task_data: YAML 작업 데이터
        """
        if not self.enabled or not self.session_manager:
            return

        try:
            # 현재 작업 정보 저장
            task_id = task_data.get("task_id", "unknown")
            title = task_data.get("title", "Unknown Task")

            # 세션에 작업 시작 기록
            self.session_manager.set(
                "current_task",
                {
                    "task_id": task_id,
                    "title": title,
                    "status": "running",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "yaml_path": str(task_data.get("_file_path", "")),
                },
                self.state_scope.SESSION,
            )

            # 작업 이력 추가
            history = self.session_manager.get("task_history", self.state_scope.SESSION, [])
            history.append({"task_id": task_id, "started_at": datetime.now(timezone.utc).isoformat(), "status": "started"})
            # 최근 100개만 유지
            if len(history) > 100:
                history = history[-100:]
            self.session_manager.set("task_history", history, self.state_scope.SESSION)

            print(f"[SESSION_HOOK] 작업 시작 기록: {task_id}")

        except Exception as e:
            # 오류가 있어도 TaskExecutor 실행에 영향 없음
            print(f"[SESSION_HOOK] 기록 실패 (무시): {e}")

    def on_task_complete(
        self, task_data: Dict[str, Any], success: bool, execution_time: float, error_msg: Optional[str] = None
    ) -> None:
        """
        작업 완료 시 호출

        Args:
            task_data: YAML 작업 데이터
            success: 성공 여부
            execution_time: 실행 시간 (초)
            error_msg: 오류 메시지 (실패 시)
        """
        if not self.enabled or not self.session_manager:
            return

        try:
            task_id = task_data.get("task_id", "unknown")

            # 현재 작업 상태 업데이트
            current_task = self.session_manager.get("current_task", self.state_scope.SESSION, {})
            current_task.update(
                {
                    "status": "success" if success else "failed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "execution_time": execution_time,
                    "error": error_msg,
                }
            )
            self.session_manager.set("current_task", current_task, self.state_scope.SESSION)

            # 통계 업데이트
            stats = self.session_manager.get("execution_stats", self.state_scope.USER, {})

            # 전체 실행 카운트
            stats["total_executions"] = stats.get("total_executions", 0) + 1

            # 성공/실패 카운트
            if success:
                stats["successful"] = stats.get("successful", 0) + 1

                # 성공한 작업 목록
                completed = self.session_manager.get("completed_tasks", self.state_scope.SESSION, [])
                completed.append(task_id)
                self.session_manager.set("completed_tasks", completed, self.state_scope.SESSION)
            else:
                stats["failed"] = stats.get("failed", 0) + 1

                # 실패한 작업과 원인 기록
                failures = self.session_manager.get("failed_tasks", self.state_scope.SESSION, {})
                failures[task_id] = {"error": error_msg, "timestamp": datetime.now(timezone.utc).isoformat()}
                self.session_manager.set("failed_tasks", failures, self.state_scope.SESSION)

            # 전체 실행 시간 누적
            stats["total_time"] = stats.get("total_time", 0) + execution_time

            # 평균 실행 시간 계산
            stats["avg_time"] = stats["total_time"] / stats["total_executions"]

            self.session_manager.set("execution_stats", stats, self.state_scope.USER)

            status_str = "성공" if success else "실패"
            print(f"[SESSION_HOOK] 작업 완료 기록: {task_id} - {status_str} ({execution_time:.2f}초)")

            # 중요 변경이므로 체크포인트 생성
            if not success:  # 실패 시 즉시 저장
                self.session_manager.checkpoint()

        except Exception as e:
            print(f"[SESSION_HOOK] 기록 실패 (무시): {e}")

    def on_command_execute(self, command: List[str], result_code: int, stdout: str = "", stderr: str = "") -> None:
        """
        개별 명령 실행 후 호출

        Args:
            command: 실행된 명령어
            result_code: 종료 코드
            stdout: 표준 출력
            stderr: 표준 에러
        """
        if not self.enabled or not self.session_manager:
            return

        try:
            # 명령 실행 로그 (최근 50개만 유지)
            command_log = self.session_manager.get("command_log", self.state_scope.TEMP, [])

            command_log.append(
                {
                    "command": " ".join(command),
                    "exit_code": result_code,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": result_code == 0,
                }
            )

            if len(command_log) > 50:
                command_log = command_log[-50:]

            self.session_manager.set("command_log", command_log, self.state_scope.TEMP)

        except Exception:
            pass  # 명령 로깅 실패는 무시

    def get_last_failed_task(self) -> Optional[Dict[str, Any]]:
        """
        마지막으로 실패한 작업 정보 반환

        Returns:
            실패한 작업 정보 또는 None
        """
        if not self.enabled or not self.session_manager:
            return None

        try:
            failed_tasks = self.session_manager.get("failed_tasks", self.state_scope.SESSION, {})
            if failed_tasks:
                # 가장 최근 실패 반환
                task_id = list(failed_tasks.keys())[-1]
                return {"task_id": task_id, **failed_tasks[task_id]}
        except Exception:
            pass

        return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        실행 요약 통계 반환

        Returns:
            통계 딕셔너리
        """
        if not self.enabled or not self.session_manager:
            return {"enabled": False}

        try:
            stats = self.session_manager.get("execution_stats", self.state_scope.USER, {})
            completed = self.session_manager.get("completed_tasks", self.state_scope.SESSION, [])
            failed = self.session_manager.get("failed_tasks", self.state_scope.SESSION, {})

            return {
                "enabled": True,
                "total_executions": stats.get("total_executions", 0),
                "successful": stats.get("successful", 0),
                "failed": stats.get("failed", 0),
                "avg_execution_time": stats.get("avg_time", 0),
                "total_time": stats.get("total_time", 0),
                "session_completed": len(completed),
                "session_failed": len(failed),
                "success_rate": (
                    stats.get("successful", 0) / stats.get("total_executions", 1) * 100
                    if stats.get("total_executions", 0) > 0
                    else 0
                ),
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


# 글로벌 인스턴스 (import 시 자동 생성)
_hook_instance = None


def get_hook() -> TaskExecutorSessionHook:
    """싱글톤 훅 인스턴스 반환"""
    global _hook_instance
    if _hook_instance is None:
        _hook_instance = TaskExecutorSessionHook()
    return _hook_instance


# 편의 함수들
def on_task_start(task_data: Dict[str, Any]) -> None:
    """작업 시작 기록"""
    get_hook().on_task_start(task_data)


def on_task_complete(
    task_data: Dict[str, Any], success: bool, execution_time: float, error_msg: Optional[str] = None
) -> None:
    """작업 완료 기록"""
    get_hook().on_task_complete(task_data, success, execution_time, error_msg)


def on_command_execute(command: List[str], result_code: int, stdout: str = "", stderr: str = "") -> None:
    """명령 실행 기록"""
    get_hook().on_command_execute(command, result_code, stdout, stderr)


def get_execution_summary() -> Dict[str, Any]:
    """실행 요약 반환"""
    return get_hook().get_execution_summary()


if __name__ == "__main__":
    # 테스트 코드
    hook = get_hook()

    # 테스트 작업 시작
    test_task = {"task_id": "TEST-2025-10-26-01", "title": "Hook Integration Test"}

    print("\n[TEST] Hook 테스트 시작")
    hook.on_task_start(test_task)

    # 작업 실행 시뮬레이션
    time.sleep(1)

    # 작업 완료
    hook.on_task_complete(test_task, success=True, execution_time=1.5)

    # 요약 출력
    summary = hook.get_execution_summary()
    print("\n[TEST] 실행 요약:")
    print(json.dumps(summary, indent=2))
