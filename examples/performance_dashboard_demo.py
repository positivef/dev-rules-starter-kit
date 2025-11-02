#!/usr/bin/env python3
"""PerformanceDashboard Usage Examples

6가지 실전 사용 예제
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from performance_dashboard import PerformanceDashboard, MetricType


def example_1_basic_metrics():
    """예제 1: 기본 메트릭 수집"""
    print("\n" + "=" * 70)
    print("예제 1: 실시간 메트릭 수집")
    print("=" * 70)

    dashboard = PerformanceDashboard()
    metrics = dashboard.collect_metrics()

    print("\n[실시간 메트릭]")
    if MetricType.CPU in metrics:
        print(f"  CPU: {metrics[MetricType.CPU]:.1f}%")
    if MetricType.MEMORY in metrics:
        print(f"  Memory: {metrics[MetricType.MEMORY]:.1f}%")
    if MetricType.DISK in metrics:
        print(f"  Disk: {metrics[MetricType.DISK]:.1f}%")


def example_2_function_profiling():
    """예제 2: 함수 프로파일링"""
    print("\n\n" + "=" * 70)
    print("예제 2: 함수 프로파일링")
    print("=" * 70)

    dashboard = PerformanceDashboard()

    # 느린 함수 시뮬레이션
    def slow_operation():
        time.sleep(0.1)
        data = [i**2 for i in range(10000)]
        return sum(data)

    print("\n[프로파일링 시작]")
    with dashboard.profile_context("slow_operation"):
        slow_operation()

    profile = dashboard.profiles[-1]
    print(f"  함수: {profile.function_name}")
    print(f"  실행 시간: {profile.execution_time_ms:.2f}ms")
    print(f"  메모리 델타: {profile.memory_delta_mb:.2f}MB")
    print(f"  성공: {profile.success}")


def example_3_trend_analysis():
    """예제 3: 트렌드 분석"""
    print("\n\n" + "=" * 70)
    print("예제 3: 성능 트렌드 분석")
    print("=" * 70)

    dashboard = PerformanceDashboard()

    # 여러 번 메트릭 수집 (트렌드 데이터 생성)
    print("\n[메트릭 수집 중...]")
    for i in range(5):
        dashboard.collect_metrics()
        time.sleep(0.1)

    # 트렌드 분석
    if dashboard.metrics:
        analysis = dashboard.analyze_trends(MetricType.CPU, "24h")
        print("\n[CPU 트렌드 분석]")
        print(f"  시간 범위: {analysis.timerange}")
        print(f"  데이터 포인트: {len(analysis.data_points)}개")
        print(f"  평균 값: {analysis.avg_value:.2f}%")
        print(f"  최소/최대: {analysis.min_value:.2f}% / {analysis.max_value:.2f}%")
        print(f"  트렌드 방향: {analysis.trend_direction}")
        print(f"  성능 저하 감지: {analysis.degradation_detected}")


def example_4_alerting():
    """예제 4: 임계값 알림"""
    print("\n\n" + "=" * 70)
    print("예제 4: 임계값 기반 알림")
    print("=" * 70)

    dashboard = PerformanceDashboard()

    # 낮은 임계값 설정 (테스트용)
    dashboard.thresholds[MetricType.CPU] = 1.0  # 매우 낮은 임계값

    print("\n[임계값 설정]")
    print(f"  CPU 임계값: {dashboard.thresholds[MetricType.CPU]}%")

    # 메트릭 수집 (임계값 초과 시 자동 알림)
    dashboard.collect_metrics()

    print("\n[알림 발생]")
    if dashboard.alerts:
        for alert in dashboard.alerts[-3:]:  # 최근 3개
            print(f"  [{alert.severity.upper()}] {alert.message}")
    else:
        print("  알림 없음")


def example_5_recommendations():
    """예제 5: 최적화 권장사항"""
    print("\n\n" + "=" * 70)
    print("예제 5: 최적화 권장사항 생성")
    print("=" * 70)

    dashboard = PerformanceDashboard()

    # 느린 함수 프로파일 추가 (권장사항 트리거)
    with dashboard.profile_context("very_slow_function"):
        time.sleep(1.5)  # 1.5초 지연

    # 권장사항 생성
    recommendations = dashboard.generate_recommendations()

    print(f"\n[최적화 권장사항: {len(recommendations)}개]")
    for rec in recommendations:
        print(f"\n  [{rec.priority.upper()}] {rec.title}")
        print(f"  카테고리: {rec.category}")
        print(f"  설명: {rec.description}")
        print(f"  예상 효과: {rec.estimated_impact}")
        if rec.action_items:
            print("  액션 아이템:")
            for action in rec.action_items[:2]:  # 처음 2개만
                print(f"    - {action}")


def example_6_performance_comparison():
    """예제 6: 성능 비교"""
    print("\n\n" + "=" * 70)
    print("예제 6: 버전 간 성능 비교")
    print("=" * 70)

    dashboard = PerformanceDashboard()

    # 충분한 데이터 생성
    print("\n[베이스라인 데이터 생성 중...]")
    for _ in range(25):
        dashboard.collect_metrics()
        time.sleep(0.05)

    # 성능 비교
    report = dashboard.compare_performance("baseline", "current")

    print("\n[성능 비교 리포트]")
    print(f"  베이스라인: {report.baseline_id}")
    print(f"  현재: {report.current_id}")
    print(f"  전체 변화율: {report.overall_change_percent:+.2f}%")
    print(f"  개선 사항: {len(report.improvements)}개")
    for improvement in report.improvements:
        print(f"    + {improvement}")
    print(f"  성능 저하: {len(report.regressions)}개")
    for regression in report.regressions:
        print(f"    - {regression}")


def main():
    """모든 예제 실행"""
    print("\n" + "=" * 70)
    print(" " * 15 + "PerformanceDashboard 데모")
    print("=" * 70)
    print("\n실시간 성능 모니터링 및 분석 시스템\n")

    try:
        example_1_basic_metrics()
        example_2_function_profiling()
        example_3_trend_analysis()
        example_4_alerting()
        example_5_recommendations()
        example_6_performance_comparison()

        print("\n\n" + "=" * 70)
        print("모든 예제 완료!")
        print("=" * 70)
        print("\n다음 단계:")
        print("  1. 중요 함수에 프로파일링 적용")
        print("  2. 서비스에 맞는 임계값 설정")
        print("  3. 정기적인 메트릭 수집 스케줄 설정")
        print("  4. 알림 시스템 통합 (Slack, 이메일)")
        print("  5. 주간 성능 트렌드 리뷰\n")

    except Exception as e:
        print(f"\n[ERROR] 데모 실패: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
