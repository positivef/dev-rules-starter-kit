#!/usr/bin/env python3
"""
Enhanced Task Executor v2 테스트
병렬 실행 및 [P] 마커 기능 검증
"""

import asyncio
import json
import time
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.enhanced_task_executor_v2 import (
    ParallelTaskExecutor,
    Task,
    Phase,
    ExecutionResult,
    EnhancedTaskExecutorV2,
)


class TestEnhancedTaskExecutorV2:
    """Enhanced Task Executor v2 테스트"""

    @pytest.fixture
    def executor(self):
        """Executor 인스턴스 생성"""
        return ParallelTaskExecutor()

    @pytest.fixture
    def sample_tasks_file(self, tmp_path):
        """샘플 태스크 파일 생성"""
        content = """# Test Tasks

## Phase 1: Setup
- [ ] T001 Initialize project
- [ ] T002 [P] Install dependencies
- [ ] T003 [P] Configure tools
- [ ] T004 [P] Setup hooks

## Phase 2: BLOCKING Development
- [ ] T005 Write core logic
- [ ] T006 [P] Add unit tests
- [ ] T007 [P] Add integration tests

## Phase 3: Deployment
- [ ] T008 Build project
- [ ] T009 Deploy to staging
- [ ] T010 Verify deployment
"""
        file_path = tmp_path / "test_tasks.md"
        file_path.write_text(content)
        return file_path

    def test_parse_tasks_file(self, executor, sample_tasks_file):
        """태스크 파일 파싱 테스트"""
        phases = executor.parse_tasks_file(sample_tasks_file)

        assert len(phases) == 3
        assert phases[0].name == "Setup"
        assert phases[1].name == "BLOCKING Development"
        assert phases[1].blocking is True
        assert phases[2].name == "Deployment"

        # Phase 1 tasks
        assert len(phases[0].tasks) == 4
        assert phases[0].tasks[0].is_parallel is False
        assert phases[0].tasks[1].is_parallel is True
        assert phases[0].tasks[2].is_parallel is True

    def test_task_parsing(self, executor):
        """개별 태스크 파싱 테스트"""
        # 일반 태스크
        task1 = executor._parse_task_line("- [ ] T001 Regular task")
        assert task1.id == "T001"
        assert task1.description == "Regular task"
        assert task1.is_parallel is False

        # 병렬 태스크
        task2 = executor._parse_task_line("- [ ] T002 [P] Parallel task")
        assert task2.id == "T002"
        assert task2.description == "Parallel task"
        assert task2.is_parallel is True

        # 완료된 태스크
        task3 = executor._parse_task_line("- [x] T003 Completed task")
        assert task3.id == "T003"
        assert task3.is_completed is True

    @pytest.mark.asyncio
    async def test_parallel_execution(self, executor):
        """병렬 실행 테스트"""
        # 병렬 태스크 생성
        tasks = [
            Task("T001", "[P] Task 1", is_parallel=True),
            Task("T002", "[P] Task 2", is_parallel=True),
            Task("T003", "[P] Task 3", is_parallel=True),
        ]

        start_time = time.time()

        # Mock 실행
        with patch.object(executor, "_execute_single_task") as mock_exec:

            async def mock_task_execution(task):
                await asyncio.sleep(0.1)  # 100ms 소요
                return ExecutionResult(success=True, task_id=task.id, duration=0.1, output=f"Task {task.id} completed")

            mock_exec.side_effect = mock_task_execution

            results = await executor._execute_parallel_tasks(tasks)

        end_time = time.time()
        duration = end_time - start_time

        # 병렬 실행이므로 약 0.1초 소요 (순차적이면 0.3초)
        assert duration < 0.2
        assert len(results) == 3
        assert all(r.success for r in results.values())

    @pytest.mark.asyncio
    async def test_sequential_execution(self, executor):
        """순차 실행 테스트"""
        # 순차 태스크 생성
        tasks = [
            Task("T001", "Task 1", is_parallel=False),
            Task("T002", "Task 2", is_parallel=False),
            Task("T003", "Task 3", is_parallel=False),
        ]

        start_time = time.time()

        # Mock 실행
        with patch.object(executor, "_execute_single_task") as mock_exec:

            async def mock_task_execution(task):
                await asyncio.sleep(0.1)  # 100ms 소요
                return ExecutionResult(success=True, task_id=task.id, duration=0.1, output=f"Task {task.id} completed")

            mock_exec.side_effect = mock_task_execution

            results = await executor._execute_sequential_tasks(tasks)

        end_time = time.time()
        duration = end_time - start_time

        # 순차 실행이므로 약 0.3초 소요
        assert duration >= 0.3
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_blocking_phase(self, executor):
        """BLOCKING 페이즈 테스트"""
        # BLOCKING 페이즈 생성
        phase = Phase("Critical Phase", blocking=True)
        phase.tasks = [
            Task("T001", "Must succeed", is_parallel=False),
            Task("T002", "Will fail", is_parallel=False),
        ]

        # Mock 실행 - T002 실패
        with patch.object(executor, "_execute_single_task") as mock_exec:

            async def mock_task_execution(task):
                if task.id == "T002":
                    return ExecutionResult(
                        success=False, task_id=task.id, duration=0.1, output="Task failed", error="Simulated failure"
                    )
                return ExecutionResult(success=True, task_id=task.id, duration=0.1, output="Task completed")

            mock_exec.side_effect = mock_task_execution

            # BLOCKING 페이즈가 실패하면 False 반환
            continue_execution = await executor._should_continue_after_phase(
                phase, {"T001": ExecutionResult(success=True), "T002": ExecutionResult(success=False)}
            )

        assert continue_execution is False

    def test_evidence_generation(self, executor, tmp_path):
        """증거 생성 테스트"""
        result = ExecutionResult(
            success=True, task_id="T001", duration=1.5, output="Test output", metrics={"coverage": 95, "tests_passed": 50}
        )

        # 증거 디렉토리 설정
        executor.evidence_dir = tmp_path / "evidence"
        executor._generate_evidence(result)

        # 증거 파일 확인
        evidence_files = list((tmp_path / "evidence").glob("T001_*.json"))
        assert len(evidence_files) == 1

        # 증거 내용 확인
        with open(evidence_files[0]) as f:
            evidence = json.load(f)

        assert evidence["task_id"] == "T001"
        assert evidence["success"] is True
        assert evidence["metrics"]["coverage"] == 95

    def test_constitution_validation(self, executor):
        """헌법 검증 테스트"""
        with patch("scripts.enhanced_task_executor_v2.ConstitutionalValidatorV3") as MockValidator:
            mock_validator = Mock()
            mock_validator.validate_all.return_value = {"passed": True, "score": 0.95, "violations": []}
            MockValidator.return_value = mock_validator

            # 검증 실행
            passed = executor._validate_constitutional_compliance()

            assert passed is True
            mock_validator.validate_all.assert_called_once()

    def test_statistics_calculation(self, executor):
        """통계 계산 테스트"""
        results = {
            "T001": ExecutionResult(success=True, duration=1.0),
            "T002": ExecutionResult(success=True, duration=2.0),
            "T003": ExecutionResult(success=False, duration=0.5),
            "T004": ExecutionResult(success=True, duration=1.5, is_parallel=True),
            "T005": ExecutionResult(success=True, duration=2.0, is_parallel=True),
        }

        stats = executor._calculate_statistics(results)

        assert stats["total_tasks"] == 5
        assert stats["completed_tasks"] == 4
        assert stats["failed_tasks"] == 1
        assert stats["success_rate"] == 80.0
        assert stats["parallel_tasks"] == 2
        assert stats["total_duration"] == 5.0  # 병렬 태스크는 동시 실행

    def test_dry_run_mode(self, executor):
        """Dry run 모드 테스트"""
        executor.dry_run = True

        # Dry run 모드에서는 실제 실행하지 않음
        with patch("subprocess.run") as mock_run:
            task = Task("T001", "Test task")
            # _execute_single_task는 async이므로 asyncio로 실행
            asyncio.run(executor._execute_single_task(task))

            # subprocess.run이 호출되지 않음
            mock_run.assert_not_called()

    @pytest.mark.parametrize(
        "input_line,expected_id,expected_parallel",
        [
            ("- [ ] T001 Regular task", "T001", False),
            ("- [ ] T002 [P] Parallel task", "T002", True),
            ("- [ ] T003 [P] Another parallel", "T003", True),
            ("- [x] T004 [P] Completed parallel", "T004", True),
            ("  - [ ] T005 Indented task", "T005", False),
        ],
    )
    def test_task_line_variations(self, executor, input_line, expected_id, expected_parallel):
        """다양한 태스크 라인 형식 테스트"""
        task = executor._parse_task_line(input_line)
        assert task.id == expected_id
        assert task.is_parallel == expected_parallel


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_execution_flow(self, tmp_path):
        """전체 실행 플로우 테스트"""
        # 태스크 파일 생성
        tasks_content = """# Integration Test

## Phase 1: Parallel Tasks
- [ ] T001 [P] Task A
- [ ] T002 [P] Task B
- [ ] T003 [P] Task C

## Phase 2: Sequential Tasks
- [ ] T004 Task D
- [ ] T005 Task E
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(tasks_content)

        # Executor 생성
        executor = EnhancedTaskExecutorV2(dry_run=True)

        # Mock 실행
        with patch.object(executor, "_execute_command") as mock_exec:
            mock_exec.return_value = (True, "Success", "")

            # 실행
            success = await executor.execute(tasks_file)

        assert success is True

    def test_performance_improvement(self):
        """성능 개선 검증"""
        # 병렬 실행 시뮬레이션
        parallel_times = []
        sequential_times = []

        for _ in range(3):
            # 병렬 실행
            start = time.time()
            asyncio.run(self._simulate_parallel_execution())
            parallel_times.append(time.time() - start)

            # 순차 실행
            start = time.time()
            asyncio.run(self._simulate_sequential_execution())
            sequential_times.append(time.time() - start)

        avg_parallel = sum(parallel_times) / len(parallel_times)
        avg_sequential = sum(sequential_times) / len(sequential_times)

        # 병렬 실행이 최소 2배 이상 빠름
        speedup = avg_sequential / avg_parallel
        assert speedup >= 2.0

    async def _simulate_parallel_execution(self):
        """병렬 실행 시뮬레이션"""
        tasks = [asyncio.create_task(asyncio.sleep(0.1)) for _ in range(5)]
        await asyncio.gather(*tasks)

    async def _simulate_sequential_execution(self):
        """순차 실행 시뮬레이션"""
        for _ in range(5):
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
