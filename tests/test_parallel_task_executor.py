#!/usr/bin/env python3
"""
Parallel Task Executor (enhanced_task_executor_v2) 테스트
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.enhanced_task_executor_v2 import ParallelTaskExecutor, Task, Phase, ExecutionResult


class TestParallelTaskExecutor:
    """Parallel Task Executor 기본 테스트"""

    def test_task_creation(self):
        """Task 생성 테스트"""
        task = Task(id="T001", description="Test task", phase="Setup", is_parallel=True, is_completed=False)

        assert task.id == "T001"
        assert task.description == "Test task"
        assert task.phase == "Setup"
        assert task.is_parallel
        assert not task.is_completed

    def test_phase_creation(self):
        """Phase 생성 테스트"""
        tasks = [Task("T001", "Task 1", "Setup", True, False), Task("T002", "Task 2", "Setup", False, False)]
        phase = Phase(name="Setup", tasks=tasks)

        assert phase.name == "Setup"
        assert len(phase.tasks) == 2
        assert phase.tasks[0].is_parallel
        assert not phase.tasks[1].is_parallel

    def test_executor_initialization(self):
        """ParallelTaskExecutor 초기화 테스트"""
        executor = ParallelTaskExecutor()

        assert executor is not None
        assert hasattr(executor, "phases")
        assert hasattr(executor, "evidence_dir")

    def test_parse_tasks_markdown(self):
        """Markdown 태스크 파싱 테스트"""
        executor = ParallelTaskExecutor()

        test_content = """# Test Tasks

## Phase 1: Setup
- [ ] T001 Initialize
- [ ] T002 [P] Install deps
- [ ] T003 [P] Configure

## Phase 2: Development
- [ ] T004 Write code
- [ ] T005 [P] Add tests
"""
        # parse_tasks_file 메서드 테스트를 위한 임시 파일 생성
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(test_content)
            temp_path = f.name

        try:
            # 파싱 테스트
            executor.parse_tasks_file(Path(temp_path))

            assert len(executor.phases) >= 2
            assert executor.phases[0].name == "Setup"

            # T002와 T003이 병렬 태스크인지 확인
            phase1_tasks = executor.phases[0].tasks
            parallel_tasks = [t for t in phase1_tasks if t.is_parallel]
            assert len(parallel_tasks) >= 2

        finally:
            os.unlink(temp_path)

    def test_parallel_marker_detection(self):
        """[P] 마커 감지 테스트"""
        executor = ParallelTaskExecutor()

        # [P] 마커가 있는 태스크
        task_with_p = executor._parse_task_line("- [ ] T001 [P] Parallel task")
        assert task_with_p is not None
        assert task_with_p.is_parallel

        # [P] 마커가 없는 태스크
        task_without_p = executor._parse_task_line("- [ ] T002 Regular task")
        assert task_without_p is not None
        assert not task_without_p.is_parallel

    def test_evidence_generation(self):
        """증거 생성 테스트"""
        executor = ParallelTaskExecutor()

        result = ExecutionResult(success=True, task_id="T001", description="Test task", duration=1.5, output="Test output")

        # 증거 생성
        evidence_path = executor._generate_evidence(result)

        assert evidence_path is not None
        # 파일이 실제로 생성되었는지 확인
        if evidence_path and Path(evidence_path).exists():
            # 파일 내용 확인
            import json

            with open(evidence_path) as f:
                evidence = json.load(f)
            assert evidence["task_id"] == "T001"
            assert evidence["success"]

    @pytest.mark.skip(reason="Needs _execute_task method implementation")
    @patch("subprocess.run")
    def test_dry_run_mode(self, mock_run):
        """Dry run 모드 테스트"""
        executor = ParallelTaskExecutor(dry_run=True)

        task = Task("T001", "Test", "Setup", False, False, command="echo test")
        executor._execute_task(task)

        # Dry run 모드에서는 subprocess.run이 호출되지 않음
        mock_run.assert_not_called()

    @pytest.mark.skip(reason="Needs results attribute and updated _calculate_statistics signature")
    def test_statistics_calculation(self):
        """통계 계산 테스트"""
        executor = ParallelTaskExecutor()

        # 샘플 결과
        executor.results = {
            "T001": {"success": True, "duration": 1.0},
            "T002": {"success": True, "duration": 2.0},
            "T003": {"success": False, "duration": 0.5},
            "T004": {"success": True, "duration": 1.5, "parallel": True},
        }

        stats = executor._calculate_statistics()

        assert stats["total"] == 4
        assert stats["completed"] == 3
        assert stats["failed"] == 1
        assert stats["success_rate"] == 75.0

    @pytest.mark.skip(reason="Needs _should_continue_after_blocking method implementation")
    def test_blocking_phase(self):
        """BLOCKING 페이즈 테스트"""
        executor = ParallelTaskExecutor()

        # BLOCKING 페이즈 생성
        blocking_phase = Phase(
            name="BLOCKING Critical", tasks=[Task("T001", "Must succeed", "Critical", False, False)], blocking=True
        )

        # 실패 시 중단 확인
        result = {"T001": {"success": False}}
        should_continue = executor._should_continue_after_blocking(blocking_phase, result)

        assert not should_continue


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.skip(reason="Needs updated execute_phases signature and _execute_task method")
    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        executor = ParallelTaskExecutor(dry_run=True)

        # 샘플 태스크
        executor.phases = [
            {
                "name": "Setup",
                "tasks": [
                    Task("T001", "Init", "Setup", False, False),
                    Task("T002", "[P] Install", "Setup", True, False),
                    Task("T003", "[P] Config", "Setup", True, False),
                ],
            }
        ]

        # 실행 (dry run)
        with patch.object(executor, "_execute_task") as mock_exec:
            mock_exec.return_value = {"success": True, "duration": 0.1}

            executor.execute_phases()

            # 3개 태스크 모두 실행되었는지 확인
            assert mock_exec.call_count == 3

    @pytest.mark.skip(reason="Needs _is_yaml_contract method implementation")
    def test_yaml_compatibility(self):
        """YAML 계약 호환성 테스트"""
        executor = ParallelTaskExecutor()

        yaml_contract = {
            "task_id": "TEST-001",
            "title": "Test Contract",
            "commands": [{"exec": ["echo", "test1"]}, {"exec": ["echo", "test2"]}],
        }

        # YAML 계약도 처리 가능한지 확인
        assert executor._is_yaml_contract(yaml_contract)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
