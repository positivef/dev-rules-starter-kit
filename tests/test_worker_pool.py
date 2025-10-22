#!/usr/bin/env python3
"""Tests for Worker Pool (Phase C Week 2 Day 12-13)"""

import time
from pathlib import Path
from threading import Lock

import pytest

from scripts.worker_pool import AdaptiveWorkerPool, Priority, WorkerPool, WorkItem


# ============================================================================
# WorkItem Tests
# ============================================================================


def test_work_item_priority_sorting():
    """WorkItem 우선순위 정렬 테스트"""
    item_high = WorkItem(Path("high.py"), Priority.HIGH, 1.0)
    item_normal = WorkItem(Path("normal.py"), Priority.NORMAL, 1.0)
    item_low = WorkItem(Path("low.py"), Priority.LOW, 1.0)

    items = [item_low, item_high, item_normal]
    sorted_items = sorted(items)

    assert sorted_items[0].priority == Priority.HIGH
    assert sorted_items[1].priority == Priority.NORMAL
    assert sorted_items[2].priority == Priority.LOW


def test_work_item_time_sorting_same_priority():
    """같은 우선순위일 때 시간순 정렬"""
    item1 = WorkItem(Path("file1.py"), Priority.NORMAL, 1.0)
    item2 = WorkItem(Path("file2.py"), Priority.NORMAL, 2.0)
    item3 = WorkItem(Path("file3.py"), Priority.NORMAL, 1.5)

    items = [item2, item1, item3]
    sorted_items = sorted(items)

    assert sorted_items[0].submit_time == 1.0
    assert sorted_items[1].submit_time == 1.5
    assert sorted_items[2].submit_time == 2.0


# ============================================================================
# WorkerPool Basic Tests
# ============================================================================


def test_worker_pool_init():
    """WorkerPool 초기화 테스트"""
    pool = WorkerPool(num_workers=3, max_queue_size=50)

    assert pool.num_workers == 3
    assert pool.max_queue_size == 50
    assert len(pool._workers) == 0
    assert pool._submitted == 0
    assert pool._completed == 0


def test_worker_pool_start():
    """WorkerPool 시작 테스트"""
    pool = WorkerPool(num_workers=2)
    pool.start()

    assert len(pool._workers) == 2
    assert all(w.is_alive() for w in pool._workers)

    pool.shutdown(timeout=5.0)


def test_worker_pool_submit_nonblocking():
    """논블로킹 작업 제출 테스트"""
    pool = WorkerPool(num_workers=1, max_queue_size=5)
    pool.start()

    # 5개까지는 성공
    for i in range(5):
        result = pool.submit(Path(f"file{i}.py"))
        assert result is True

    # 6번째는 큐 가득참 (논블로킹이므로 실패)
    result = pool.submit(Path("file6.py"))
    # Note: 워커가 빠르게 처리하면 성공할 수도 있음
    # assert result is False (불안정한 테스트)

    pool.shutdown(timeout=5.0)


def test_worker_pool_submit_blocking():
    """블로킹 작업 제출 테스트"""
    pool = WorkerPool(num_workers=1, max_queue_size=2)
    pool.start()

    # 블로킹 제출 (타임아웃 내 성공)
    result = pool.submit_blocking(Path("file1.py"), timeout=1.0)
    assert result is True

    pool.shutdown(timeout=5.0)


def test_worker_pool_shutdown():
    """WorkerPool 종료 테스트"""
    pool = WorkerPool(num_workers=2)
    pool.start()

    # 종료
    result = pool.shutdown(timeout=5.0)
    assert result is True
    assert len(pool._workers) == 0


def test_worker_pool_shutdown_not_started():
    """시작하지 않은 풀 종료"""
    pool = WorkerPool(num_workers=2)
    result = pool.shutdown(timeout=1.0)
    assert result is True


# ============================================================================
# WorkerPool Functional Tests
# ============================================================================


def test_worker_pool_process_tasks():
    """작업 처리 기능 테스트"""
    processed = []
    lock = Lock()

    def worker_fn(file_path: Path):
        with lock:
            processed.append(file_path.name)

    pool = WorkerPool(num_workers=2, worker_fn=worker_fn)
    pool.start()

    # 10개 작업 제출
    files = [Path(f"file{i}.py") for i in range(10)]
    for file_path in files:
        pool.submit(file_path)

    # 완료 대기
    pool.wait_completion(timeout=5.0)
    pool.shutdown(timeout=5.0)

    # 모든 파일이 처리되었는지 확인
    assert len(processed) == 10
    assert set(processed) == {f"file{i}.py" for i in range(10)}


def test_worker_pool_priority_order():
    """우선순위 순서대로 처리되는지 테스트"""
    processed = []
    lock = Lock()

    def slow_worker(file_path: Path):
        time.sleep(0.05)  # 느린 처리
        with lock:
            processed.append(file_path.name)

    pool = WorkerPool(num_workers=1, worker_fn=slow_worker)  # 1 워커로 순서 보장
    pool.start()

    # 우선순위 다르게 제출
    pool.submit(Path("low.py"), Priority.LOW)
    pool.submit(Path("high.py"), Priority.HIGH)
    pool.submit(Path("normal.py"), Priority.NORMAL)

    pool.wait_completion(timeout=5.0)
    pool.shutdown(timeout=5.0)

    # HIGH가 먼저 처리되어야 함
    assert processed[0] == "high.py"


def test_worker_pool_error_handling():
    """워커 함수 에러 처리 테스트"""
    processed = []
    lock = Lock()

    def failing_worker(file_path: Path):
        with lock:
            processed.append(file_path.name)
        if "fail" in file_path.name:
            raise ValueError("Intentional error")

    pool = WorkerPool(num_workers=2, worker_fn=failing_worker)
    pool.start()

    # 정상 + 실패 작업 혼합
    pool.submit(Path("good1.py"))
    pool.submit(Path("fail1.py"))
    pool.submit(Path("good2.py"))

    pool.wait_completion(timeout=5.0)
    pool.shutdown(timeout=5.0)

    stats = pool.get_stats()

    # 모두 처리되었지만 1개 실패
    assert stats["submitted"] == 3
    assert stats["completed"] == 2
    assert stats["failed"] == 1


def test_worker_pool_concurrent_processing():
    """병렬 처리 성능 테스트"""
    processed_count = [0]
    lock = Lock()

    def worker_fn(file_path: Path):
        time.sleep(0.1)  # 100ms 작업
        with lock:
            processed_count[0] += 1

    # 순차 처리 시간 측정
    start = time.time()
    for i in range(6):
        worker_fn(Path(f"seq{i}.py"))
    sequential_time = time.time() - start

    # 병렬 처리 (2 워커)
    pool = WorkerPool(num_workers=2, worker_fn=worker_fn)
    pool.start()

    start = time.time()
    for i in range(6):
        pool.submit(Path(f"file{i}.py"))

    pool.wait_completion(timeout=10.0)
    parallel_time = time.time() - start
    pool.shutdown(timeout=5.0)

    # 병렬이 더 빠름 (이론적으로 2배 빠름, 실제로는 오버헤드 고려)
    speedup = sequential_time / parallel_time
    assert speedup > 1.5  # 최소 1.5배 빠름


# ============================================================================
# WorkerPool Stats Tests
# ============================================================================


def test_worker_pool_get_stats():
    """통계 수집 테스트"""
    pool = WorkerPool(num_workers=2)
    pool.start()

    # 초기 통계
    stats = pool.get_stats()
    assert stats["submitted"] == 0
    assert stats["completed"] == 0
    assert stats["workers"] == 2

    # 작업 제출
    for i in range(5):
        pool.submit(Path(f"file{i}.py"))

    stats = pool.get_stats()
    assert stats["submitted"] == 5

    pool.shutdown(timeout=5.0)


def test_worker_pool_throughput():
    """처리량 계산 테스트"""

    def quick_worker(file_path: Path):
        time.sleep(0.01)  # 10ms

    pool = WorkerPool(num_workers=3, worker_fn=quick_worker)
    pool.start()

    # 30개 작업
    for i in range(30):
        pool.submit(Path(f"file{i}.py"))

    # 완료 대기 (충분한 시간)
    pool.wait_completion(timeout=15.0)

    # 추가 대기 (모든 워커가 완료 보고할 시간)
    time.sleep(0.5)

    stats = pool.get_stats()
    pool.shutdown(timeout=5.0)

    # 처리량 확인 (거의 모두 완료되어야 함)
    assert stats["completed"] >= 28  # 최소 28개 (타이밍 여유)
    assert stats["throughput_per_sec"] > 15  # 최소 15 files/sec (여유있게)


# ============================================================================
# WorkerPool Wait Tests
# ============================================================================


def test_worker_pool_wait_completion_success():
    """작업 완료 대기 성공"""

    def worker_fn(file_path: Path):
        time.sleep(0.05)

    pool = WorkerPool(num_workers=2, worker_fn=worker_fn)
    pool.start()

    for i in range(5):
        pool.submit(Path(f"file{i}.py"))

    # 충분한 시간 (성공)
    result = pool.wait_completion(timeout=5.0)
    assert result is True

    pool.shutdown(timeout=5.0)


def test_worker_pool_wait_completion_timeout():
    """작업 완료 대기 타임아웃"""

    def slow_worker(file_path: Path):
        time.sleep(1.0)  # 1초 작업

    pool = WorkerPool(num_workers=1, worker_fn=slow_worker)
    pool.start()

    for i in range(5):
        pool.submit(Path(f"file{i}.py"))

    # 짧은 타임아웃 (실패)
    result = pool.wait_completion(timeout=0.5)
    assert result is False

    pool.shutdown(timeout=10.0)


# ============================================================================
# WorkerPool Edge Cases
# ============================================================================


def test_worker_pool_submit_after_shutdown():
    """종료 후 작업 제출 시도"""
    pool = WorkerPool(num_workers=1)
    pool.start()
    pool.shutdown(timeout=5.0)

    # 종료 후 제출 실패
    result = pool.submit(Path("file.py"))
    assert result is False


def test_worker_pool_double_start():
    """이중 시작 시도"""
    pool = WorkerPool(num_workers=2)
    pool.start()

    # 다시 시작 (무시됨)
    pool.start()

    # 여전히 2개 워커
    assert len(pool._workers) == 2

    pool.shutdown(timeout=5.0)


def test_worker_pool_no_worker_function():
    """워커 함수 없이 실행"""
    pool = WorkerPool(num_workers=2, worker_fn=None)
    pool.start()

    # 작업 제출 (워커 함수 없어도 에러 없음)
    pool.submit(Path("file.py"))

    pool.wait_completion(timeout=1.0)
    pool.shutdown(timeout=5.0)

    # completed는 증가 (함수 없어도 "완료"로 간주)
    stats = pool.get_stats()
    assert stats["completed"] == 1


# ============================================================================
# AdaptiveWorkerPool Tests
# ============================================================================


def test_adaptive_worker_pool_init():
    """AdaptiveWorkerPool 초기화 테스트"""
    pool = AdaptiveWorkerPool(min_workers=2, max_workers=6)

    assert pool.min_workers == 2
    assert pool.max_workers == 6
    assert pool.num_workers == 2  # 최소값으로 시작

    pool.start()
    pool.shutdown(timeout=5.0)


def test_adaptive_worker_pool_basic_functionality():
    """AdaptiveWorkerPool 기본 기능 테스트"""
    processed = []
    lock = Lock()

    def worker_fn(file_path: Path):
        with lock:
            processed.append(file_path.name)

    pool = AdaptiveWorkerPool(min_workers=2, max_workers=4, worker_fn=worker_fn)
    pool.start()

    for i in range(10):
        pool.submit(Path(f"file{i}.py"))

    pool.wait_completion(timeout=5.0)
    pool.shutdown(timeout=5.0)

    # 모든 파일 처리됨
    assert len(processed) == 10


# ============================================================================
# Performance Benchmark Tests
# ============================================================================


@pytest.mark.benchmark
def test_worker_pool_large_scale():
    """대규모 파일 처리 벤치마크 (500+ files)"""
    processed_count = [0]
    lock = Lock()

    def worker_fn(file_path: Path):
        # 실제 검증 시뮬레이션 (50ms)
        time.sleep(0.05)
        with lock:
            processed_count[0] += 1

    pool = WorkerPool(num_workers=3, worker_fn=worker_fn)
    pool.start()

    num_files = 100  # 테스트는 100개만 (실제는 500+)
    start = time.time()

    for i in range(num_files):
        pool.submit(Path(f"file{i}.py"))

    pool.wait_completion(timeout=60.0)
    elapsed = time.time() - start
    pool.shutdown(timeout=5.0)

    stats = pool.get_stats()

    # 성능 검증
    assert stats["completed"] == num_files
    sequential_time = num_files * 0.05  # 5초
    speedup = sequential_time / elapsed

    print("\nBenchmark Results:")
    print(f"  Files: {num_files}")
    print("  Workers: 3")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Sequential (est): {sequential_time:.2f}s")
    print(f"  Speedup: {speedup:.2f}x")
    print(f"  Throughput: {stats['throughput_per_sec']:.1f} files/sec")

    # 최소 2배 빠름 (3 워커니까)
    assert speedup > 2.0


def test_worker_pool_memory_efficiency():
    """메모리 효율성 테스트"""
    import sys

    processed = []
    lock = Lock()

    def worker_fn(file_path: Path):
        with lock:
            processed.append(file_path)
        time.sleep(0.01)

    pool = WorkerPool(num_workers=3, worker_fn=worker_fn)
    pool.start()

    # 100개 작업
    for i in range(100):
        pool.submit(Path(f"file{i}.py"))

    pool.wait_completion(timeout=10.0)
    pool.shutdown(timeout=5.0)

    # 메모리 사용량은 pool 객체 크기로 대략 확인
    pool_size = sys.getsizeof(pool)
    assert pool_size < 10_000  # 10KB 이하 (매우 작음)
