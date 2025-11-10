#!/usr/bin/env python3
"""TechnicalDebtTracker Usage Examples

5가지 실전 사용 예제
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from technical_debt_tracker import (
    DebtSeverity,
    RefactoringStatus,
    TechnicalDebtTracker,
)


def example_1_basic_detection():
    """예제 1: 기본 부채 감지"""
    print("\n" + "=" * 70)
    print("예제 1: 기술부채 자동 감지")
    print("=" * 70)

    tracker = TechnicalDebtTracker()

    # 프로젝트 스캔
    debt_items = tracker.detect_debt(path="scripts/")

    print(f"\n[감지된 부채 항목: {len(debt_items)}개]")
    if debt_items:
        print("\n상위 5개:")
        for item in debt_items[:5]:
            print(f"\n  [{item.debt_type}] {item.description}")
            print(f"  위치: {item.file_path}:{item.line_number}")
            print(
                f"  복잡도: {item.complexity_score:.1f}, "
                f"영향도: {item.impact_score:.1f}, "
                f"위험도: {item.risk_level:.1f}"
            )


def example_2_quantification():
    """예제 2: 부채 정량화"""
    print("\n\n" + "=" * 70)
    print("예제 2: 기술부채 정량화 및 비용 분석")
    print("=" * 70)

    tracker = TechnicalDebtTracker()
    debt_items = tracker.detect_debt(path="scripts/")

    # 정량화
    report = tracker.quantify_debt(debt_items)

    print("\n[정량화 메트릭]")
    print(f"  총 부채 항목: {report.metrics.total_debt_items}")
    print(f"  총 복잡도: {report.metrics.total_complexity:.1f}")
    print(f"  총 예상 시간: {report.metrics.total_effort_hours:.1f}시간")
    print(f"  유지보수 비용: ${report.metrics.total_maintenance_cost:,.2f}")
    print(f"  월간 이자: ${report.metrics.debt_interest_rate:,.2f}")
    print(f"  평균 복잡도: {report.metrics.average_complexity:.2f}")
    print(f"  고위험 항목: {report.metrics.high_risk_count}개")

    # 유형별 분포
    if report.metrics.by_type:
        print("\n[유형별 분포]")
        for debt_type, count in sorted(report.metrics.by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  {debt_type}: {count}개")


def example_3_prioritization():
    """예제 3: 우선순위 매핑"""
    print("\n\n" + "=" * 70)
    print("예제 3: 우선순위 자동 매핑")
    print("=" * 70)

    tracker = TechnicalDebtTracker()
    debt_items = tracker.detect_debt(path="scripts/")
    report = tracker.quantify_debt(debt_items)

    # 우선순위 매핑
    prioritized = tracker.prioritize_debt(report)

    # 심각도별 집계
    critical = sum(1 for p in prioritized if p.severity == DebtSeverity.CRITICAL)
    high = sum(1 for p in prioritized if p.severity == DebtSeverity.HIGH)
    medium = sum(1 for p in prioritized if p.severity == DebtSeverity.MEDIUM)
    low = sum(1 for p in prioritized if p.severity == DebtSeverity.LOW)

    print("\n[심각도별 분류]")
    print(f"  CRITICAL: {critical}개 (즉시 조치 필요)")
    print(f"  HIGH: {high}개 (현재 스프린트)")
    print(f"  MEDIUM: {medium}개 (다음 2-3 스프린트)")
    print(f"  LOW: {low}개 (여유 시 조치)")

    # 상위 3개 우선순위
    print("\n[최우선 조치 항목]")
    for idx, p in enumerate(prioritized[:3], 1):
        print(f"\n  {idx}. [{p.severity.upper()}] {p.debt_item.description[:60]}")
        print(f"     우선순위: {p.priority_score:.1f}")
        print(f"     권장 스프린트: {p.recommended_sprint}")
        print(
            f"     영향도: {p.priority_factors['impact']:.1f}, "
            f"작업량: {p.priority_factors['effort']:.1f}h, "
            f"위험도: {p.priority_factors['risk']:.1f}"
        )


def example_4_refactoring_plan():
    """예제 4: 리팩토링 계획 생성"""
    print("\n\n" + "=" * 70)
    print("예제 4: 자동 리팩토링 계획 생성")
    print("=" * 70)

    tracker = TechnicalDebtTracker()
    debt_items = tracker.detect_debt(path="scripts/")
    report = tracker.quantify_debt(debt_items)
    prioritized = tracker.prioritize_debt(report)

    # 4 스프린트 계획 생성
    plan = tracker.create_refactoring_plan(prioritized, sprints=4)

    print("\n[리팩토링 계획]")
    print(f"  계획 ID: {plan.plan_id}")
    print(f"  총 스프린트: {plan.total_sprints}")
    print(f"  총 태스크: {len(plan.tasks)}개")
    print(f"  총 예상 시간: {plan.total_effort_hours:.1f}시간")
    print(f"  완료 예상일: {plan.expected_completion_date[:10]}")

    # ROI 분석
    roi = plan.roi_analysis
    print("\n[ROI 분석]")
    print(f"  투자 비용: ${roi['total_cost']:,.2f}")
    print(f"  예상 절감: ${roi['expected_savings']:,.2f}")
    print(f"  ROI: {roi['roi_percentage']:.1f}%")
    print(f"  손익분기: {roi['break_even_months']:.1f}개월")

    # 스프린트별 배정
    print("\n[스프린트별 작업 배정]")
    for sprint_num in range(1, min(plan.total_sprints + 1, 3)):  # 처음 2개만
        task_ids = plan.sprint_allocation.get(sprint_num, [])
        if task_ids:
            print(f"\n  Sprint {sprint_num}: {len(task_ids)}개 태스크")
            for task_id in task_ids[:2]:  # 각 스프린트에서 처음 2개만
                task = next(t for t in plan.tasks if t.task_id == task_id)
                print(f"    - [{task.task_id}] {task.title[:50]}")
                print(f"      예상: {task.estimated_hours:.1f}h")


def example_5_progress_tracking():
    """예제 5: 진행 상황 추적"""
    print("\n\n" + "=" * 70)
    print("예제 5: 리팩토링 진행 상황 추적")
    print("=" * 70)

    tracker = TechnicalDebtTracker()

    # 부채 감지 및 계획 생성
    debt_items = tracker.detect_debt(path="scripts/")
    if not debt_items:
        print("\n  부채 항목이 없습니다.")
        return

    report = tracker.quantify_debt(debt_items)
    prioritized = tracker.prioritize_debt(report)
    plan = tracker.create_refactoring_plan(prioritized, sprints=4)

    # 일부 태스크를 완료로 표시 (시뮬레이션)
    if len(plan.tasks) > 0:
        plan.tasks[0].status = RefactoringStatus.COMPLETED
        plan.tasks[0].actual_hours = 3.5
    if len(plan.tasks) > 1:
        plan.tasks[1].status = RefactoringStatus.IN_PROGRESS

    # 진행 상황 추적
    progress = tracker.track_progress()

    print("\n[진행 상황]")
    print(f"  총 태스크: {progress.total_debt_items}개")
    print(f"  완료: {progress.resolved_items}개")
    print(f"  진행 중: {progress.in_progress_items}개")
    print(f"  대기: {progress.pending_items}개")
    print(f"  완료율: {progress.resolution_percentage:.1f}%")

    print("\n[성과 지표]")
    print(f"  부채 감소 속도: {progress.debt_reduction_rate:.2f} items/sprint")
    print(f"  실제 비용: ${progress.actual_cost:,.2f}")
    print(f"  예상 절감: ${progress.estimated_savings:,.2f}")
    print(f"  ROI: {progress.roi_percentage:.1f}%")


def main():
    """모든 예제 실행"""
    print("\n" + "=" * 70)
    print(" " * 15 + "TechnicalDebtTracker 데모")
    print("=" * 70)
    print("\n기술부채 관리 및 리팩토링 계획 시스템\n")

    try:
        example_1_basic_detection()
        example_2_quantification()
        example_3_prioritization()
        example_4_refactoring_plan()
        example_5_progress_tracking()

        print("\n\n" + "=" * 70)
        print("모든 예제 완료!")
        print("=" * 70)
        print("\n다음 단계:")
        print("  1. 주간 부채 스캔 스케줄 설정")
        print("  2. CRITICAL/HIGH 부채 우선 해결")
        print("  3. 스프린트별 리팩토링 계획 수립")
        print("  4. 진행 상황 대시보드 구축")
        print("  5. CI/CD 통합 및 자동화\n")

    except Exception as e:
        print(f"\n[ERROR] 데모 실패: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
