#!/usr/bin/env python3
"""Worker Pool for Parallel File Verification

Phase C Week 2 Day 12-13: Scalability Features

병렬 처리를 통한 대규모 파일 검증 성능 향상

주요 기능:
- 멀티스레드 워커 풀 (기본 3 workers)
- 작업 큐 기반 분산 처리
- 우선순위 큐 (critical files first)
- 백프레셔 관리 (max queue size)
- Graceful shutdown with timeout

성능 목표:
- 500+ files: <30초 (vs 150초 순차)
- CPU 사용률: 60-80% (vs 20% 순차)
- 메모리: <100MB 추가

사용 예시:
```python
pool = WorkerPool(num_workers=3, max_queue_size=100)
pool.start()

for file_path in files:
    pool.submit(file_path, priority=1)

pool.shutdown(timeout=30)
```
"""

import logging
import queue
import threading
import time
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class Priority(IntEnum):
    """작업 우선순위"""

    LOW = 3
    NORMAL = 2
    HIGH = 1  # 낮은 숫자 = 높은 우선순위


@dataclass
class WorkItem:
    """작업 항목"""

    file_path: Path
    priority: Priority
    submit_time: float

    def __lt__(self, other):
        """우선순위 큐 정렬용 (<가 높은 우선순위)"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.submit_time < other.submit_time


class WorkerPool:
    """멀티스레드 파일 검증 워커 풀

    Features:
    - Configurable worker count (default 3)
    - Priority-based task scheduling
    - Backpressure management (queue size limit)
    - Graceful shutdown with timeout
    - Thread-safe operation
    - Performance metrics tracking
    """

    def __init__(
        self,
        num_workers: int = 3,
        max_queue_size: int = 100,
        worker_fn: Optional[Callable[[Path], None]] = None,
    ):
        """초기화

        Args:
            num_workers: 워커 스레드 수 (기본 3)
            max_queue_size: 최대 큐 크기 (백프레셔)
            worker_fn: 각 파일 처리 함수 (file_path -> None)
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        self.worker_fn = worker_fn
        self._queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=max_queue_size)
        self._workers: list[threading.Thread] = []
        self._shutdown_event = threading.Event()
        self._stats_lock = threading.Lock()

        # 통계
        self._submitted = 0
        self._completed = 0
        self._failed = 0
        self._start_time: Optional[float] = None

        self._logger = logging.getLogger(__name__)

    def start(self):
        """워커 풀 시작"""
        if self._workers:
            self._logger.warning("Worker pool already started")
            return

        self._start_time = time.time()
        self._shutdown_event.clear()

        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"Worker-{i+1}",
                daemon=True,
            )
            worker.start()
            self._workers.append(worker)

        self._logger.info(f"Worker pool started with {self.num_workers} workers")

    def submit(self, file_path: Path, priority: Priority = Priority.NORMAL) -> bool:
        """파일 검증 작업 제출

        Args:
            file_path: 검증할 파일 경로
            priority: 작업 우선순위

        Returns:
            True if submitted, False if queue full
        """
        if self._shutdown_event.is_set():
            self._logger.warning("Cannot submit: pool is shutting down")
            return False

        work_item = WorkItem(
            file_path=file_path,
            priority=priority,
            submit_time=time.time(),
        )

        try:
            # 비블로킹 put (큐가 가득 차면 False 반환)
            self._queue.put(work_item, block=False)
            with self._stats_lock:
                self._submitted += 1
            return True
        except queue.Full:
            self._logger.warning(f"Queue full, dropping task: {file_path.name}")
            return False

    def submit_blocking(self, file_path: Path, priority: Priority = Priority.NORMAL, timeout: float = 5.0) -> bool:
        """파일 검증 작업 제출 (블로킹)

        Args:
            file_path: 검증할 파일 경로
            priority: 작업 우선순위
            timeout: 최대 대기 시간

        Returns:
            True if submitted, False if timeout
        """
        if self._shutdown_event.is_set():
            return False

        work_item = WorkItem(
            file_path=file_path,
            priority=priority,
            submit_time=time.time(),
        )

        try:
            self._queue.put(work_item, block=True, timeout=timeout)
            with self._stats_lock:
                self._submitted += 1
            return True
        except queue.Full:
            self._logger.warning(f"Submit timeout for: {file_path.name}")
            return False

    def shutdown(self, timeout: float = 30.0) -> bool:
        """워커 풀 종료

        Args:
            timeout: 최대 대기 시간 (초)

        Returns:
            True if clean shutdown, False if timeout
        """
        if not self._workers:
            return True

        self._logger.info("Shutting down worker pool...")
        self._shutdown_event.set()

        # 모든 워커가 종료될 때까지 대기
        start = time.time()
        for worker in self._workers:
            remaining = timeout - (time.time() - start)
            if remaining <= 0:
                self._logger.warning("Shutdown timeout reached")
                return False

            worker.join(timeout=remaining)
            if worker.is_alive():
                self._logger.warning(f"{worker.name} did not terminate")
                return False

        self._workers.clear()
        elapsed = time.time() - start
        self._logger.info(f"Worker pool shut down cleanly in {elapsed:.2f}s")
        return True

    def get_stats(self) -> dict:
        """성능 통계 반환

        Returns:
            통계 딕셔너리
        """
        with self._stats_lock:
            elapsed = time.time() - self._start_time if self._start_time else 0
            throughput = self._completed / elapsed if elapsed > 0 else 0

            return {
                "submitted": self._submitted,
                "completed": self._completed,
                "failed": self._failed,
                "pending": self._queue.qsize(),
                "elapsed_seconds": elapsed,
                "throughput_per_sec": throughput,
                "workers": self.num_workers,
            }

    def _worker_loop(self):
        """워커 스레드 메인 루프"""
        worker_name = threading.current_thread().name
        self._logger.debug(f"{worker_name} started")

        while not self._shutdown_event.is_set():
            try:
                # 0.5초 타임아웃으로 작업 대기
                work_item = self._queue.get(timeout=0.5)

                # 작업 처리
                try:
                    if self.worker_fn:
                        self.worker_fn(work_item.file_path)

                    with self._stats_lock:
                        self._completed += 1

                except Exception as e:
                    self._logger.error(
                        f"{worker_name} failed on {work_item.file_path.name}: {e}",
                        exc_info=True,
                    )
                    with self._stats_lock:
                        self._failed += 1

                finally:
                    self._queue.task_done()

            except queue.Empty:
                # 타임아웃 - 계속 대기
                continue

        self._logger.debug(f"{worker_name} terminated")

    def wait_completion(self, timeout: Optional[float] = None) -> bool:
        """모든 작업 완료 대기

        Args:
            timeout: 최대 대기 시간 (None=무제한)

        Returns:
            True if all tasks completed, False if timeout
        """
        try:
            if timeout:
                # 타임아웃 있음
                start = time.time()
                while not self._queue.empty():
                    if time.time() - start > timeout:
                        return False
                    time.sleep(0.1)
                return True
            else:
                # 무제한 대기
                self._queue.join()
                return True
        except Exception as e:
            self._logger.error(f"Error waiting for completion: {e}")
            return False


class AdaptiveWorkerPool(WorkerPool):
    """동적으로 워커 수를 조절하는 적응형 풀

    Features:
    - 큐 크기 기반 워커 증가/감소
    - CPU 사용률 모니터링
    - 자동 최적화

    Note: 현재는 기본 WorkerPool과 동일 (향후 확장용)
    """

    def __init__(
        self,
        min_workers: int = 2,
        max_workers: int = 6,
        max_queue_size: int = 100,
        worker_fn: Optional[Callable[[Path], None]] = None,
    ):
        """초기화

        Args:
            min_workers: 최소 워커 수
            max_workers: 최대 워커 수
            max_queue_size: 최대 큐 크기
            worker_fn: 워커 함수
        """
        super().__init__(
            num_workers=min_workers,
            max_queue_size=max_queue_size,
            worker_fn=worker_fn,
        )
        self.min_workers = min_workers
        self.max_workers = max_workers

        # TODO: 향후 구현
        # - 큐 크기 모니터링
        # - CPU 사용률 기반 워커 조정
        # - 동적 워커 추가/제거


def demo():
    """데모 및 성능 테스트"""

    def mock_worker(file_path: Path):
        """모의 워커 함수"""
        # 파일 검증 시뮬레이션 (50-100ms)
        time.sleep(0.05 + (hash(str(file_path)) % 50) / 1000)
        logger.info(f"Processed: {file_path.name}")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 테스트 파일 생성
    test_files = [Path(f"test_file_{i}.py") for i in range(100)]

    print("\n=== Worker Pool Demo ===")
    print(f"Files: {len(test_files)}")
    print("Workers: 3")

    # 워커 풀 실행
    pool = WorkerPool(num_workers=3, worker_fn=mock_worker)
    pool.start()

    start = time.time()

    # 작업 제출
    for i, file_path in enumerate(test_files):
        priority = Priority.HIGH if i < 10 else Priority.NORMAL
        pool.submit(file_path, priority=priority)

    # 완료 대기
    pool.wait_completion()
    elapsed = time.time() - start

    # 통계 출력
    stats = pool.get_stats()
    print("\n=== Performance Stats ===")
    print(f"Submitted:  {stats['submitted']}")
    print(f"Completed:  {stats['completed']}")
    print(f"Failed:     {stats['failed']}")
    print(f"Elapsed:    {elapsed:.2f}s")
    print(f"Throughput: {stats['throughput_per_sec']:.1f} files/sec")

    # 종료
    pool.shutdown()

    # 순차 처리와 비교
    sequential_time = len(test_files) * 0.075  # 평균 75ms
    speedup = sequential_time / elapsed
    print("\n=== Comparison ===")
    print(f"Sequential (estimated): {sequential_time:.2f}s")
    print(f"Parallel (actual):      {elapsed:.2f}s")
    print(f"Speedup:                {speedup:.2f}x")


if __name__ == "__main__":
    demo()
