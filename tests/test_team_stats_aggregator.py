#!/usr/bin/env python3
"""Tests for Team Statistics Aggregator (Phase C Week 2 Day 10-11)"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from scripts.team_stats_aggregator import (
    DashboardGenerator,
    FileStats,
    StatsCollector,
    TeamStats,
    TeamStatsAggregator,
    TrendAnalyzer,
)


@pytest.fixture
def temp_dirs():
    """임시 디렉토리 생성"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        cache_dir = base / "cache"
        evidence_dir = base / "evidence"
        output_dir = base / "stats"

        cache_dir.mkdir()
        evidence_dir.mkdir()
        output_dir.mkdir()

        yield {
            "base": base,
            "cache": cache_dir,
            "evidence": evidence_dir,
            "output": output_dir,
        }


@pytest.fixture
def sample_cache_data():
    """샘플 캐시 데이터"""
    return {
        "scripts/good_file.py": {
            "file_hash": "abc123",
            "timestamp": datetime.now().isoformat(),
            "mode": "fast",
            "result": {
                "file_path": "scripts/good_file.py",
                "passed": True,
                "violations": [],
                "duration_ms": 50.0,
            },
        },
        "scripts/bad_file.py": {
            "file_hash": "def456",
            "timestamp": datetime.now().isoformat(),
            "mode": "deep",
            "result": {
                "file_path": "scripts/bad_file.py",
                "passed": False,
                "violations": [
                    {"code": "E501", "message": "Line too long"},
                    {"code": "F401", "message": "Unused import"},
                ],
                "duration_ms": 75.0,
                "overall_score": 6.5,
                "security_issues": [{"issue": "hardcoded_secret", "line": 10}],
                "solid_violations": [
                    {"principle": "SRP", "line": 20},
                    {"principle": "DIP", "line": 30},
                ],
            },
        },
        "scripts/critical_file.py": {
            "file_hash": "ghi789",
            "timestamp": datetime.now().isoformat(),
            "mode": "deep",
            "result": {
                "file_path": "scripts/critical_file.py",
                "passed": False,
                "violations": [],
                "duration_ms": 120.0,
                "overall_score": 4.0,
                "security_issues": [
                    {"issue": "eval", "line": 15},
                    {"issue": "exec", "line": 25},
                ],
                "solid_violations": [
                    {"principle": "SRP", "line": 10},
                    {"principle": "SRP", "line": 20},
                    {"principle": "DIP", "line": 40},
                ],
            },
        },
    }


# ============================================================================
# FileStats Tests
# ============================================================================


def test_file_stats_pass_rate():
    """FileStats pass_rate 계산 테스트"""
    stats = FileStats(file_path="test.py", total_checks=10, passed_checks=8)
    assert stats.pass_rate == 80.0


def test_file_stats_zero_checks():
    """체크가 없을 때 pass_rate=0"""
    stats = FileStats(file_path="test.py", total_checks=0)
    assert stats.pass_rate == 0.0


# ============================================================================
# TeamStats Tests
# ============================================================================


def test_team_stats_pass_rate():
    """TeamStats pass_rate 계산 테스트"""
    stats = TeamStats(total_checks=20, passed_checks=16)
    assert stats.pass_rate == 80.0


def test_team_stats_zero_checks():
    """체크가 없을 때 pass_rate=0"""
    stats = TeamStats(total_checks=0)
    assert stats.pass_rate == 0.0


# ============================================================================
# StatsCollector Tests
# ============================================================================


def test_stats_collector_init(temp_dirs):
    """StatsCollector 초기화 테스트"""
    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    assert collector.cache_dir == temp_dirs["cache"]
    assert collector.evidence_dir == temp_dirs["evidence"]


def test_stats_collector_no_cache_file(temp_dirs):
    """캐시 파일 없을 때 빈 결과 반환"""
    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    file_stats = collector.collect_file_stats()
    assert len(file_stats) == 0


def test_stats_collector_with_cache_data(temp_dirs, sample_cache_data):
    """캐시 데이터로 통계 수집 테스트"""
    # 캐시 파일 생성
    cache_file = temp_dirs["cache"] / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    file_stats = collector.collect_file_stats()

    assert len(file_stats) == 3
    assert "scripts/good_file.py" in file_stats
    assert "scripts/bad_file.py" in file_stats
    assert "scripts/critical_file.py" in file_stats


def test_stats_collector_file_stats_details(temp_dirs, sample_cache_data):
    """파일 통계 상세 내용 검증"""
    cache_file = temp_dirs["cache"] / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    file_stats = collector.collect_file_stats()

    # Good file
    good = file_stats["scripts/good_file.py"]
    assert good.passed_checks == 1
    assert good.failed_checks == 0
    assert good.total_violations == 0

    # Bad file
    bad = file_stats["scripts/bad_file.py"]
    assert bad.passed_checks == 0
    assert bad.failed_checks == 1
    assert bad.total_violations == 2
    assert bad.avg_quality_score == 6.5
    assert bad.total_security_issues == 1
    assert bad.total_solid_violations == 2

    # Critical file
    critical = file_stats["scripts/critical_file.py"]
    assert critical.avg_quality_score == 4.0
    assert critical.total_security_issues == 2
    assert critical.total_solid_violations == 3


def test_stats_collector_team_stats(temp_dirs, sample_cache_data):
    """팀 전체 통계 집계 테스트"""
    cache_file = temp_dirs["cache"] / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    file_stats = collector.collect_file_stats()
    team_stats = collector.collect_team_stats(file_stats)

    assert team_stats.total_files == 3
    assert team_stats.total_checks == 3
    assert team_stats.passed_checks == 1
    assert team_stats.failed_checks == 2
    assert team_stats.total_violations == 2  # Only bad_file has violations
    assert team_stats.total_security_issues == 3  # 1 + 2
    assert team_stats.total_solid_violations == 5  # 2 + 3

    # 평균 품질 점수: (10.0 + 6.5 + 4.0) / 3 = 6.83...
    assert 6.5 <= team_stats.avg_quality_score <= 7.0


def test_stats_collector_empty_team_stats(temp_dirs):
    """파일이 없을 때 팀 통계"""
    collector = StatsCollector(temp_dirs["cache"], temp_dirs["evidence"])
    team_stats = collector.collect_team_stats({})

    assert team_stats.total_files == 0
    assert team_stats.avg_quality_score == 0.0


# ============================================================================
# DashboardGenerator Tests
# ============================================================================


def test_dashboard_generator_init(temp_dirs):
    """DashboardGenerator 초기화 테스트"""
    generator = DashboardGenerator(temp_dirs["output"])
    assert generator.output_dir.exists()


def test_dashboard_generator_create_dashboard(temp_dirs):
    """대시보드 생성 테스트"""
    generator = DashboardGenerator(temp_dirs["output"])

    team_stats = TeamStats(
        total_files=10,
        total_checks=50,
        passed_checks=40,
        failed_checks=10,
        avg_quality_score=7.5,
        total_violations=20,
        total_security_issues=5,
        total_solid_violations=10,
        generated_at=datetime.now().isoformat(),
    )

    file_stats = {
        "test1.py": FileStats(
            file_path="test1.py",
            avg_quality_score=9.0,
            total_violations=1,
        ),
        "test2.py": FileStats(
            file_path="test2.py",
            avg_quality_score=5.0,
            total_violations=10,
            total_security_issues=2,
        ),
    }

    problem_files = [file_stats["test2.py"], file_stats["test1.py"]]

    dashboard_path = generator.generate_dashboard(team_stats, file_stats, problem_files)

    assert dashboard_path.exists()
    content = dashboard_path.read_text(encoding="utf-8")

    # 기본 섹션 확인
    assert "# Team Code Quality Dashboard" in content
    assert "## Overview" in content
    assert "## Quality Metrics" in content
    assert "## Quality Score Distribution" in content
    assert "## Top Problem Files" in content
    assert "## Recommendations" in content

    # 통계 확인
    assert "Total Files**: 10" in content
    assert "Pass Rate**: 80.0%" in content
    assert "Avg Quality Score**: 7.5/10.0" in content


def test_dashboard_score_distribution(temp_dirs):
    """점수 분포 계산 테스트"""
    generator = DashboardGenerator(temp_dirs["output"])

    file_stats = {
        f"file{i}.py": FileStats(
            file_path=f"file{i}.py",
            avg_quality_score=score,
        )
        for i, score in enumerate([9.5, 8.0, 6.0, 4.0, 2.0])
    }

    bins = generator._calculate_score_distribution(file_stats)

    assert bins["9.0-10.0"] == 1
    assert bins["7.0-8.9"] == 1
    assert bins["5.0-6.9"] == 1
    assert bins["3.0-4.9"] == 1
    assert bins["0.0-2.9"] == 1


def test_dashboard_recommendations_security(temp_dirs):
    """보안 이슈 권장사항 테스트"""
    generator = DashboardGenerator(temp_dirs["output"])

    team_stats = TeamStats(total_security_issues=5)
    recommendations = generator._generate_recommendations(team_stats, [])

    assert any("Security" in r for r in recommendations)
    assert any("5개" in r for r in recommendations)


def test_dashboard_recommendations_pass_rate(temp_dirs):
    """낮은 통과율 권장사항 테스트"""
    generator = DashboardGenerator(temp_dirs["output"])

    team_stats = TeamStats(total_checks=100, passed_checks=70)
    recommendations = generator._generate_recommendations(team_stats, [])

    assert any("Pass Rate" in r for r in recommendations)


def test_dashboard_recommendations_all_good(temp_dirs):
    """모든 메트릭 양호 시 권장사항"""
    generator = DashboardGenerator(temp_dirs["output"])

    team_stats = TeamStats(
        total_checks=100,
        passed_checks=90,
        avg_quality_score=8.5,
        total_security_issues=0,
        total_solid_violations=5,
    )
    recommendations = generator._generate_recommendations(team_stats, [])

    assert any("Good Job" in r for r in recommendations)


# ============================================================================
# TrendAnalyzer Tests
# ============================================================================


def test_trend_analyzer_init(temp_dirs):
    """TrendAnalyzer 초기화 테스트"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)
    assert analyzer.trends_file == trends_file


def test_trend_analyzer_add_data_point(temp_dirs):
    """추세 데이터 포인트 추가 테스트"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)

    team_stats = TeamStats(
        avg_quality_score=8.0,
        total_violations=10,
        total_security_issues=2,
        total_checks=100,
        passed_checks=85,
        generated_at=datetime.now().isoformat(),
    )

    analyzer.add_data_point(team_stats)

    # 파일 생성 확인
    assert trends_file.exists()

    # 데이터 확인
    with open(trends_file, "r", encoding="utf-8") as f:
        trends = json.load(f)

    assert len(trends) == 1
    assert trends[0]["quality_score"] == 8.0
    assert trends[0]["violation_count"] == 10
    assert trends[0]["pass_rate"] == 85.0


def test_trend_analyzer_multiple_data_points(temp_dirs):
    """여러 데이터 포인트 추가"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)

    for i in range(5):
        team_stats = TeamStats(
            avg_quality_score=7.0 + i * 0.5,
            total_violations=20 - i * 2,
            generated_at=datetime.now().isoformat(),
        )
        analyzer.add_data_point(team_stats)

    with open(trends_file, "r", encoding="utf-8") as f:
        trends = json.load(f)

    assert len(trends) == 5
    # 품질 점수가 증가하는지 확인
    assert trends[-1]["quality_score"] > trends[0]["quality_score"]


def test_trend_analyzer_old_data_cleanup(temp_dirs):
    """오래된 데이터 정리 (30일 초과)"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)

    # 오래된 데이터 추가
    old_stats = TeamStats(
        avg_quality_score=7.0,
        generated_at=(datetime.now() - timedelta(days=35)).isoformat(),
    )
    analyzer.add_data_point(old_stats)

    # 최근 데이터 추가
    new_stats = TeamStats(
        avg_quality_score=8.0,
        generated_at=datetime.now().isoformat(),
    )
    analyzer.add_data_point(new_stats)

    with open(trends_file, "r", encoding="utf-8") as f:
        trends = json.load(f)

    # 오래된 데이터는 제거되어야 함
    assert len(trends) == 1
    assert trends[0]["quality_score"] == 8.0


def test_trend_analyzer_get_summary_insufficient_data(temp_dirs):
    """데이터 부족 시 추세 요약"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)

    summary = analyzer.get_trend_summary()
    assert summary["available"] is False


def test_trend_analyzer_get_summary_with_data(temp_dirs):
    """데이터 있을 때 추세 요약"""
    trends_file = temp_dirs["output"] / "trends.json"
    analyzer = TrendAnalyzer(trends_file)

    # 첫 번째 데이터
    team_stats1 = TeamStats(
        avg_quality_score=7.0,
        total_violations=20,
        generated_at=datetime.now().isoformat(),
    )
    analyzer.add_data_point(team_stats1)

    # 두 번째 데이터 (개선됨)
    team_stats2 = TeamStats(
        avg_quality_score=8.0,
        total_violations=15,
        generated_at=datetime.now().isoformat(),
    )
    analyzer.add_data_point(team_stats2)

    summary = analyzer.get_trend_summary()

    assert summary["available"] is True
    assert summary["data_points"] == 2
    assert summary["latest_quality"] == 8.0
    assert summary["quality_change"] == 1.0
    assert summary["quality_trend"] == "improving"
    assert summary["violation_change"] == -5


# ============================================================================
# TeamStatsAggregator Integration Tests
# ============================================================================


def test_team_stats_aggregator_init(temp_dirs):
    """TeamStatsAggregator 초기화 테스트"""
    aggregator = TeamStatsAggregator(
        cache_dir=temp_dirs["cache"],
        evidence_dir=temp_dirs["evidence"],
        output_dir=temp_dirs["output"],
    )

    assert aggregator.collector is not None
    assert aggregator.dashboard_gen is not None
    assert aggregator.trend_analyzer is not None


def test_team_stats_aggregator_generate_report(temp_dirs, sample_cache_data):
    """전체 리포트 생성 통합 테스트"""
    # 캐시 데이터 준비
    cache_file = temp_dirs["cache"] / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    aggregator = TeamStatsAggregator(
        cache_dir=temp_dirs["cache"],
        evidence_dir=temp_dirs["evidence"],
        output_dir=temp_dirs["output"],
    )

    dashboard_path = aggregator.generate_report()

    # 대시보드 생성 확인
    assert dashboard_path.exists()
    assert dashboard_path.name == "team_dashboard.md"

    # 추세 파일 생성 확인
    trends_file = temp_dirs["output"] / "trends.json"
    assert trends_file.exists()

    # 문제 파일 목록 생성 확인
    problem_file = temp_dirs["output"] / "problem_files.json"
    assert problem_file.exists()

    # 내용 확인
    content = dashboard_path.read_text(encoding="utf-8")
    assert "Team Code Quality Dashboard" in content
    assert "critical_file.py" in content  # 가장 문제 많은 파일 (basename만 표시됨)


def test_team_stats_aggregator_empty_cache(temp_dirs):
    """캐시가 비어있을 때 리포트 생성"""
    aggregator = TeamStatsAggregator(
        cache_dir=temp_dirs["cache"],
        evidence_dir=temp_dirs["evidence"],
        output_dir=temp_dirs["output"],
    )

    dashboard_path = aggregator.generate_report()

    assert dashboard_path.exists()
    content = dashboard_path.read_text(encoding="utf-8")
    assert "Total Files**: 0" in content


def test_team_stats_aggregator_problem_files_saved(temp_dirs, sample_cache_data):
    """문제 파일 목록 저장 확인"""
    cache_file = temp_dirs["cache"] / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    aggregator = TeamStatsAggregator(
        cache_dir=temp_dirs["cache"],
        evidence_dir=temp_dirs["evidence"],
        output_dir=temp_dirs["output"],
    )

    aggregator.generate_report()

    problem_file = temp_dirs["output"] / "problem_files.json"
    with open(problem_file, "r", encoding="utf-8") as f:
        problem_files = json.load(f)

    assert len(problem_files) == 3
    # 품질 점수 낮은 순으로 정렬되어 있어야 함
    assert problem_files[0]["avg_quality_score"] <= problem_files[1]["avg_quality_score"]


# ============================================================================
# CLI Tests
# ============================================================================


def test_main_function_success(temp_dirs, sample_cache_data, monkeypatch):
    """CLI main 함수 성공 케이스"""
    # 현재 디렉토리를 temp로 변경
    monkeypatch.chdir(temp_dirs["base"])

    # RUNS 디렉토리 구조 생성
    cache_dir = temp_dirs["base"] / "RUNS" / ".cache"
    cache_dir.mkdir(parents=True)

    cache_file = cache_dir / "verification_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(sample_cache_data, f)

    from scripts.team_stats_aggregator import main

    result = main()
    assert result == 0

    # 대시보드 생성 확인
    dashboard_path = temp_dirs["base"] / "RUNS" / "stats" / "team_dashboard.md"
    assert dashboard_path.exists()


def test_main_function_with_error(temp_dirs, monkeypatch):
    """CLI main 함수 에러 처리"""
    # 잘못된 디렉토리로 설정
    monkeypatch.chdir(temp_dirs["base"])

    # 캐시 디렉토리를 생성하지 않음 (에러 발생 상황)
    from scripts.team_stats_aggregator import main

    # 빈 캐시여도 정상 동작해야 함 (에러가 아님)
    result = main()
    assert result == 0
