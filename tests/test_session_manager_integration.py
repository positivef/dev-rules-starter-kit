#!/usr/bin/env python3
"""
SessionManager 생태계 통합 테스트
전체 시스템 통합 검증
"""

import pytest
import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session_manager import SessionManager, StateScope
from session_analyzer import SessionAnalyzer
from session_report_generator import SessionReportGenerator
from session_report_scheduler import SessionReportScheduler
from task_executor_session_hook import TaskExecutorSessionHook


@pytest.mark.skip(reason="SessionManager ecosystem needs refactoring for test isolation")
class TestSessionManagerIntegration:
    """SessionManager 전체 생태계 통합 테스트"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """각 테스트 전 초기화"""
        # 테스트용 세션 디렉토리 생성
        self.test_dir = Path("RUNS/sessions")  # 기본 디렉토리 사용
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # SessionManager 싱글톤 리셋
        SessionManager._instance = None
        self.manager = SessionManager.get_instance()
        self.session_id = self.manager.session_id

        # 세션 시작
        self.manager.start(resume_last=False)

        yield

        # 테스트 후 정리
        self.manager._cleanup()
        SessionManager._instance = None

    def test_complete_workflow(self):
        """전체 워크플로우 테스트: 세션 시작 → 작업 실행 → 분석 → 리포트"""

        # 1. 작업 실행 시뮬레이션
        task_ids = ["TEST-001", "TEST-002", "TEST-003"]
        for task_id in task_ids:
            self.manager.set_state("current_task", task_id, StateScope.SESSION)

            # 명령 실행 시뮬레이션
            self.manager.record_execution(command="pytest tests/", success=True, duration=10.5, context={"task_id": task_id})

            # 체크포인트
            checkpoint_file = self.manager.save_checkpoint()
            assert checkpoint_file.exists()

        # 2. 세션 분석
        analyzer = SessionAnalyzer()  # 기본 디렉토리 사용
        patterns = analyzer.analyze_patterns(hours=1)

        assert patterns["total_sessions"] > 0
        assert patterns["total_executions"] == 3
        assert patterns["success_rate"] == 100.0

        # 3. 리포트 생성
        generator = SessionReportGenerator()  # 기본 디렉토리 사용

        # HTML 리포트
        html_report = generator.generate_report(period="daily", days=1, format="html")
        assert html_report and Path(html_report).exists()

        # JSON 리포트
        json_report = generator.generate_report(period="daily", days=1, format="json")
        assert json_report and Path(json_report).exists()

        # JSON 리포트 내용 검증
        with open(json_report) as f:
            report_data = json.load(f)
            assert report_data["analysis"]["execution_stats"]["total_tasks"] >= 3
            assert report_data["analysis"]["execution_stats"]["success_rate"] == 100.0

    def test_task_executor_hook_integration(self):
        """TaskExecutor 훅 통합 테스트"""

        # 훅 초기화
        hook = TaskExecutorSessionHook(None)  # TaskExecutor 없이 테스트
        assert hook.enabled
        assert hook.session_manager == self.manager  # 같은 싱글톤 인스턴스

        # 훅을 통한 작업 기록
        result = {
            "task_id": "HOOK-TEST-001",
            "success": True,
            "duration": 15.5,
            "commands": [{"command": "python test.py", "success": True}],
        }

        hook.on_task_complete(result)

        # 세션에서 기록 확인
        session_file = self.test_dir / f"{self.session_id}.json"
        assert session_file.exists()

        with open(session_file) as f:
            session_data = json.load(f)
            assert len(session_data["executions"]) > 0
            # 마지막 실행이 우리가 기록한 것인지 확인
            last_exec = session_data["executions"][-1]
            assert last_exec["context"]["task_id"] == "HOOK-TEST-001"

    def test_checkpoint_and_recovery(self):
        """체크포인트 및 복구 테스트"""

        # 상태 설정
        self.manager.set_state("test_key", "test_value", StateScope.SESSION)
        self.manager.set_state("user_pref", "dark_mode", StateScope.USER)

        # 체크포인트 생성
        checkpoint_file = self.manager.save_checkpoint()
        assert checkpoint_file.exists()

        # 세션 종료
        self.manager.end_session()

        # 새 SessionManager 인스턴스로 복구
        SessionManager._instance = None
        new_manager = SessionManager.get_instance()  # 기본 디렉토리 사용

        # 이전 세션 로드
        sessions = list(self.test_dir.glob("session_*.json"))
        assert len(sessions) > 0

        # USER 스코프 상태는 유지됨
        assert new_manager.get_state("user_pref", StateScope.USER) == "dark_mode"

    def test_performance_with_many_tasks(self):
        """많은 작업에서의 성능 테스트"""

        start_time = time.time()

        # 100개 작업 시뮬레이션
        for i in range(100):
            self.manager.record_execution(
                command=f"test_command_{i}",
                success=(i % 10 != 0),  # 10%는 실패
                duration=0.5 + (i % 5),
                context={"task_id": f"PERF-{i:03d}"},
            )

        # 체크포인트 저장 시간 측정
        checkpoint_start = time.time()
        self.manager.save_checkpoint()
        checkpoint_time = time.time() - checkpoint_start

        # 성능 검증
        total_time = time.time() - start_time
        assert total_time < 5.0  # 100개 작업 기록이 5초 내에 완료
        assert checkpoint_time < 1.0  # 체크포인트 저장이 1초 내에 완료

        # 분석 성능
        analyzer = SessionAnalyzer()  # 기본 디렉토리 사용
        analysis_start = time.time()
        patterns = analyzer.analyze_patterns(hours=1)
        analysis_time = time.time() - analysis_start

        assert analysis_time < 2.0  # 분석이 2초 내에 완료
        assert patterns["total_executions"] == 100
        assert patterns["success_rate"] == 90.0

    def test_error_recovery(self):
        """에러 상황에서의 복구 테스트"""

        # 잘못된 데이터로 실행 기록 시도
        try:
            self.manager.record_execution(
                command=None,  # 잘못된 명령
                success=True,
                duration=-1,  # 잘못된 시간
                context={},
            )
        except Exception:
            pass  # 예외 무시

        # 시스템이 계속 작동하는지 확인
        self.manager.record_execution(
            command="valid_command", success=True, duration=1.0, context={"task_id": "RECOVERY-001"}
        )

        # 체크포인트가 여전히 작동하는지 확인
        checkpoint_file = self.manager.save_checkpoint()
        assert checkpoint_file.exists()

    def test_concurrent_access(self):
        """동시 접근 테스트 (싱글톤 패턴)"""

        # 여러 곳에서 SessionManager 접근
        manager1 = SessionManager.get_instance()
        manager2 = SessionManager.get_instance()

        # 같은 인스턴스인지 확인
        assert manager1 is manager2
        assert manager1 is self.manager

        # 한 곳에서 상태 변경
        manager1.set_state("shared_key", "value1", StateScope.SESSION)

        # 다른 곳에서 확인
        assert manager2.get_state("shared_key", StateScope.SESSION) == "value1"

    def test_report_scheduler_integration(self):
        """리포트 스케줄러 통합 테스트"""

        # 스케줄러 초기화
        scheduler = SessionReportScheduler()  # 기본 디렉토리 사용

        # 설정 파일 존재 확인
        assert scheduler.config_file.exists()

        # 수동 리포트 생성
        report = scheduler.generate_weekly_report()

        # 리포트가 생성되었는지 확인
        if report:
            assert Path(report).exists()
            assert "weekly" in Path(report).name

    def test_session_lifecycle(self):
        """세션 생명주기 전체 테스트"""

        # 1. 세션 시작
        assert self.manager.session_id == self.session_id
        assert self.manager.is_active

        # 2. 작업 수행
        for i in range(5):
            self.manager.record_execution(
                command=f"lifecycle_test_{i}", success=True, duration=1.0, context={"phase": "execution"}
            )

        # 3. 중간 체크포인트
        checkpoint1 = self.manager.save_checkpoint()
        assert checkpoint1.exists()

        # 4. 추가 작업
        for i in range(5, 10):
            self.manager.record_execution(
                command=f"lifecycle_test_{i}", success=True, duration=1.0, context={"phase": "continuation"}
            )

        # 5. 최종 체크포인트
        checkpoint2 = self.manager.save_checkpoint()
        assert checkpoint2.exists()

        # 6. 세션 종료
        self.manager.end_session()
        assert not self.manager.is_active

        # 7. 세션 파일 검증
        session_file = self.test_dir / f"{self.session_id}.json"
        assert session_file.exists()

        with open(session_file) as f:
            data = json.load(f)
            assert len(data["executions"]) == 10
            assert data["end_time"] is not None

    @pytest.mark.parametrize("period,days", [("daily", 1), ("weekly", 7), ("monthly", 30)])
    def test_report_generation_periods(self, period, days):
        """다양한 기간의 리포트 생성 테스트"""

        # 테스트 데이터 생성
        for i in range(3):
            self.manager.record_execution(command=f"period_test_{i}", success=True, duration=1.0, context={"period": period})

        # 리포트 생성
        generator = SessionReportGenerator()  # 기본 디렉토리 사용
        report = generator.generate_report(period=period, days=days, format="json")

        assert report and Path(report).exists()

        # 리포트 내용 검증
        with open(report) as f:
            data = json.load(f)
            assert data["metadata"]["period"] == period
            assert data["metadata"]["days"] == days


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
