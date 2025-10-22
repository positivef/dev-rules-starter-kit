#!/usr/bin/env python3
"""Phase C Week 2 Integration Tests

전체 시스템 통합 테스트:
- DeepAnalyzer + CriticalFileDetector
- TeamStatsAggregator + VerificationCache
- WorkerPool + DeepAnalyzer
- End-to-end workflow
"""

import tempfile
import time
from pathlib import Path

import pytest

from scripts.critical_file_detector import AnalysisMode, CriticalFileDetector
from scripts.deep_analyzer import DeepAnalyzer
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.worker_pool import Priority, WorkerPool


@pytest.fixture
def temp_workspace():
    """임시 워크스페이스 생성"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        cache_dir = base / "RUNS" / ".cache"
        evidence_dir = base / "RUNS" / "evidence"
        stats_dir = base / "RUNS" / "stats"

        cache_dir.mkdir(parents=True)
        evidence_dir.mkdir(parents=True)
        stats_dir.mkdir(parents=True)

        yield {
            "base": base,
            "cache": cache_dir,
            "evidence": evidence_dir,
            "stats": stats_dir,
        }


@pytest.fixture
def sample_python_files(temp_workspace):
    """샘플 Python 파일 생성"""
    base = temp_workspace["base"]
    files = {}

    # Good file (high quality)
    good_file = base / "good_module.py"
    good_file.write_text(
        """
def calculate_sum(a: int, b: int) -> int:
    '''Calculate sum of two numbers.'''
    return a + b

def calculate_product(a: int, b: int) -> int:
    '''Calculate product of two numbers.'''
    return a * b
""",
        encoding="utf-8",
    )
    files["good"] = good_file

    # Critical file (many issues)
    critical_file = base / "critical_executor.py"
    critical_file.write_text(
        """
import subprocess  # Security-sensitive import
import pickle  # Security-sensitive import

class CriticalExecutor:
    def __init__(self):
        self.db = DatabaseConnection()  # DIP violation
        self.cache = RedisCache()  # DIP violation

    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass  # SRP violation (>10 methods)

    def execute(self, code):
        # TODO: Add validation
        eval(code)  # Security issue
        subprocess.run(code, shell=True)  # Security issue
""",
        encoding="utf-8",
    )
    files["critical"] = critical_file

    # Medium file
    medium_file = base / "utils.py"
    medium_file.write_text(
        """
def helper_function():
    # FIXME: Optimize this
    pass

def another_helper():
    password = "hardcoded123"  # Security issue
    return password
""",
        encoding="utf-8",
    )
    files["medium"] = medium_file

    return files


# ============================================================================
# DeepAnalyzer + CriticalFileDetector Integration
# ============================================================================


def test_deep_analyzer_with_detector(sample_python_files):
    """DeepAnalyzer와 CriticalFileDetector 통합"""
    detector = CriticalFileDetector()
    analyzer = DeepAnalyzer(mcp_enabled=False)

    critical_file = sample_python_files["critical"]

    # 1. 파일 분류
    classification = detector.classify(critical_file)
    # pattern_score 0.4 (*_executor.py) + import/diff/dir = 0.4 total
    assert classification.pattern_score == 0.4  # Executor pattern detected
    assert classification.criticality_score == 0.4  # Below critical threshold
    assert classification.mode == AnalysisMode.FAST_MODE  # Not enough for DEEP

    # 2. Deep 분석 (수동으로 실행)
    result = analyzer.analyze(critical_file)

    # 3. 결과 검증
    assert result.overall_score < 7.0  # Low quality
    assert len(result.solid_violations) > 0  # SOLID issues
    assert len(result.security_issues) > 0  # Security issues
    assert len(result.hallucination_risks) > 0  # TODO found


def test_fast_mode_for_good_files(sample_python_files):
    """좋은 파일은 FAST 모드로 분류"""
    detector = CriticalFileDetector()
    good_file = sample_python_files["good"]

    classification = detector.classify(good_file)

    # Good file은 critical이 아님
    assert classification.criticality_score < 0.5  # Not critical
    assert classification.mode == AnalysisMode.FAST_MODE


# ============================================================================
# TeamStatsAggregator + VerificationCache Integration
# ============================================================================


def test_team_stats_with_cache(temp_workspace, sample_python_files):
    """TeamStatsAggregator와 VerificationCache 통합"""
    cache = VerificationCache(cache_dir=temp_workspace["cache"])
    analyzer = DeepAnalyzer(mcp_enabled=False)

    # 1. 파일 분석 및 캐시 저장
    for name, file_path in sample_python_files.items():
        result = analyzer.analyze(file_path)
        cache.put(file_path, result.ruff_result, mode="deep")

    # 2. 캐시 파일 확인
    cache_file = temp_workspace["cache"] / "verification_cache.json"
    assert cache_file.exists()

    # 3. TeamStatsAggregator로 통계 생성
    aggregator = TeamStatsAggregator(
        cache_dir=temp_workspace["cache"],
        evidence_dir=temp_workspace["evidence"],
        output_dir=temp_workspace["stats"],
    )

    dashboard_path = aggregator.generate_report()

    # 4. 대시보드 검증
    assert dashboard_path.exists()
    content = dashboard_path.read_text(encoding="utf-8")
    assert "Team Code Quality Dashboard" in content
    assert "Total Files" in content

    # 5. 추세 파일 생성 확인
    trends_file = temp_workspace["stats"] / "trends.json"
    assert trends_file.exists()


def test_cache_integration_with_deep_analysis(temp_workspace, sample_python_files):
    """캐시와 Deep 분석 통합"""
    cache = VerificationCache(cache_dir=temp_workspace["cache"])
    analyzer = DeepAnalyzer(mcp_enabled=False)

    file_path = sample_python_files["critical"]

    # 첫 번째 분석 (캐시 미스)
    result1 = analyzer.analyze(file_path)
    cache.put(file_path, result1.ruff_result, mode="deep")

    # 두 번째 분석 (캐시 히트)
    cached_result = cache.get(file_path)
    assert cached_result is not None
    assert cached_result.file_path == result1.ruff_result.file_path


# ============================================================================
# WorkerPool + DeepAnalyzer Integration
# ============================================================================


def test_worker_pool_with_deep_analyzer(sample_python_files):
    """WorkerPool과 DeepAnalyzer 통합"""
    results = []
    analyzer = DeepAnalyzer(mcp_enabled=False)

    def analyze_file(file_path: Path):
        result = analyzer.analyze(file_path)
        results.append((file_path.name, result.overall_score))

    # Worker Pool로 병렬 분석
    pool = WorkerPool(num_workers=2, worker_fn=analyze_file)
    pool.start()

    for file_path in sample_python_files.values():
        pool.submit(file_path, priority=Priority.NORMAL)

    pool.wait_completion(timeout=10.0)
    pool.shutdown(timeout=5.0)

    # 모든 파일 분석 완료
    assert len(results) == 3
    assert all(0 <= score <= 10 for _, score in results)


def test_worker_pool_priority_with_critical_files(sample_python_files):
    """우선순위 기반 파일 처리"""
    processed_order = []
    analyzer = DeepAnalyzer(mcp_enabled=False)

    def analyze_with_tracking(file_path: Path):
        time.sleep(0.05)  # 처리 시간 시뮬레이션
        analyzer.analyze(file_path)
        processed_order.append(file_path.name)

    pool = WorkerPool(num_workers=1, worker_fn=analyze_with_tracking)  # 1 워커로 순서 보장
    pool.start()

    # 우선순위를 명시적으로 설정
    pool.submit(sample_python_files["good"], priority=Priority.LOW)
    pool.submit(sample_python_files["critical"], priority=Priority.HIGH)
    pool.submit(sample_python_files["medium"], priority=Priority.NORMAL)

    pool.wait_completion(timeout=10.0)
    pool.shutdown(timeout=5.0)

    # HIGH 우선순위 파일이 먼저 처리됨
    assert processed_order[0] == "critical_executor.py"
    assert len(processed_order) == 3


# ============================================================================
# End-to-End Workflow
# ============================================================================


def test_complete_workflow(temp_workspace, sample_python_files):
    """전체 워크플로우 통합 테스트"""
    cache = VerificationCache(cache_dir=temp_workspace["cache"])
    detector = CriticalFileDetector()
    analyzer = DeepAnalyzer(mcp_enabled=False)

    analysis_results = []

    def verify_and_cache(file_path: Path):
        # 1. 파일 분류
        classification = detector.classify(file_path)

        # 2. 캐시 확인
        cached = cache.get(file_path)
        if cached:
            return cached

        # 3. 분석 실행
        if classification.mode == AnalysisMode.DEEP_MODE:
            result = analyzer.analyze(file_path)
            deep_result = result
        else:
            # Fast mode는 Ruff만
            result = analyzer._ruff_verifier.verify_file(file_path)
            deep_result = None

        # 4. 캐시 저장
        cache.put(file_path, result if not deep_result else deep_result.ruff_result, mode=classification.mode.value)

        # 5. 결과 기록
        analysis_results.append(
            {
                "file": file_path.name,
                "mode": classification.mode.value,
                "cached": False,
                "score": deep_result.overall_score if deep_result else 10.0,
            }
        )

    # Worker Pool로 병렬 처리
    pool = WorkerPool(num_workers=2, worker_fn=verify_and_cache)
    pool.start()

    for file_path in sample_python_files.values():
        pool.submit(file_path)

    pool.wait_completion(timeout=15.0)
    pool.shutdown(timeout=5.0)

    # 통계 생성
    aggregator = TeamStatsAggregator(
        cache_dir=temp_workspace["cache"],
        evidence_dir=temp_workspace["evidence"],
        output_dir=temp_workspace["stats"],
    )

    dashboard_path = aggregator.generate_report()

    # 전체 검증
    assert len(analysis_results) == 3  # 3 files analyzed
    assert dashboard_path.exists()  # Dashboard created
    assert cache.stats()["size"] >= 3  # Cache populated

    # 대시보드 내용 검증
    content = dashboard_path.read_text(encoding="utf-8")
    assert "critical_executor.py" in content  # Problem file listed


# ============================================================================
# Performance Integration Tests
# ============================================================================


def test_performance_with_caching(temp_workspace, sample_python_files):
    """캐싱으로 성능 향상 검증"""
    cache = VerificationCache(cache_dir=temp_workspace["cache"])
    analyzer = DeepAnalyzer(mcp_enabled=False)

    file_path = sample_python_files["critical"]

    # 첫 번째 분석 (캐시 미스)
    start = time.time()
    result1 = analyzer.analyze(file_path)
    cache.put(file_path, result1.ruff_result, mode="deep")
    first_time = time.time() - start

    # 두 번째 분석 (캐시 히트)
    start = time.time()
    cached_result = cache.get(file_path)
    second_time = time.time() - start

    # 캐시가 훨씬 빠름
    assert second_time < first_time / 10  # 최소 10배 빠름
    assert cached_result is not None


def test_worker_pool_speedup(sample_python_files):
    """Worker Pool 병렬 처리 속도 향상"""
    analyzer = DeepAnalyzer(mcp_enabled=False)
    files = list(sample_python_files.values())

    # 순차 처리
    start = time.time()
    for file_path in files:
        analyzer.analyze(file_path)
    sequential_time = time.time() - start

    # 병렬 처리
    def analyze(file_path):
        analyzer.analyze(file_path)

    pool = WorkerPool(num_workers=2, worker_fn=analyze)
    pool.start()

    start = time.time()
    for file_path in files:
        pool.submit(file_path)
    pool.wait_completion(timeout=10.0)
    parallel_time = time.time() - start
    pool.shutdown(timeout=5.0)

    # 병렬이 더 빠름 (최소 1.3배)
    speedup = sequential_time / parallel_time
    assert speedup > 1.3


# ============================================================================
# Error Handling Integration
# ============================================================================


def test_error_handling_in_workflow(temp_workspace, sample_python_files):
    """에러 처리 통합 테스트"""

    def intentional_failing_worker(file_path):
        """의도적으로 예외를 던지는 워커 함수"""
        if "critical" in file_path.name:
            raise ValueError("Intentional test error")
        # 다른 파일은 정상 처리
        pass

    pool = WorkerPool(num_workers=2, worker_fn=intentional_failing_worker)
    pool.start()

    # Critical 파일은 실패, 다른 파일은 성공
    for file_path in sample_python_files.values():
        pool.submit(file_path)

    pool.wait_completion(timeout=5.0)
    pool.shutdown(timeout=5.0)

    # 에러에도 불구하고 정상 종료
    stats = pool.get_stats()
    assert stats["failed"] == 1  # Critical 파일 1개 실패
    assert stats["completed"] == 2  # Good, Medium 2개 성공


# ============================================================================
# Backward Compatibility Tests
# ============================================================================


def test_backward_compatibility_with_phase_a(sample_python_files):
    """Phase A 컴포넌트와 호환성"""
    from scripts.dev_assistant import RuffVerifier

    verifier = RuffVerifier()
    analyzer = DeepAnalyzer(mcp_enabled=False, ruff_verifier=verifier)

    # Phase A RuffVerifier와 통합
    result = analyzer.analyze(sample_python_files["good"])

    # RuffVerifier 결과 포함
    assert result.ruff_result is not None
    assert hasattr(result.ruff_result, "passed")
    assert hasattr(result.ruff_result, "violations")


def test_backward_compatibility_with_phase_c_week1(temp_workspace, sample_python_files):
    """Phase C Week 1 컴포넌트와 호환성"""
    cache = VerificationCache(cache_dir=temp_workspace["cache"])
    detector = CriticalFileDetector()
    analyzer = DeepAnalyzer(mcp_enabled=False)

    file_path = sample_python_files["critical"]

    # Week 1: CriticalFileDetector + VerificationCache
    classification = detector.classify(file_path)
    result = analyzer.analyze(file_path)
    cache.put(file_path, result.ruff_result, mode="deep")

    # Week 2: DeepAnalyzer + TeamStatsAggregator
    aggregator = TeamStatsAggregator(
        cache_dir=temp_workspace["cache"],
        evidence_dir=temp_workspace["evidence"],
        output_dir=temp_workspace["stats"],
    )

    dashboard_path = aggregator.generate_report()

    # 모든 컴포넌트 호환
    assert classification.pattern_score == 0.4  # Executor pattern detected
    assert result.overall_score < 10.0  # Low quality
    assert cache.get(file_path) is not None  # Cache working
    assert dashboard_path.exists()  # Dashboard generated


# ============================================================================
# Summary Test
# ============================================================================


def test_phase_c_week2_complete_integration():
    """Phase C Week 2 전체 통합 최종 테스트"""
    # 모든 컴포넌트 import 가능
    from scripts.critical_file_detector import CriticalFileDetector
    from scripts.deep_analyzer import DeepAnalyzer
    from scripts.verification_cache import VerificationCache
    from scripts.worker_pool import WorkerPool

    # 모든 클래스 인스턴스화 가능
    detector = CriticalFileDetector()
    analyzer = DeepAnalyzer(mcp_enabled=False)
    cache = VerificationCache(cache_dir=Path("RUNS/.cache"))
    pool = WorkerPool(num_workers=2)

    # 기본 동작 확인
    assert detector is not None
    assert analyzer is not None
    assert cache is not None
    assert pool is not None

    print("\n✅ Phase C Week 2 Integration: ALL SYSTEMS OPERATIONAL")
