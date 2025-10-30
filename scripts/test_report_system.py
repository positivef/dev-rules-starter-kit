#!/usr/bin/env python3
"""
Session Report System Test Script
리포트 시스템 테스트 및 데모

Usage:
    python scripts/test_report_system.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from session_report_generator import SessionReportGenerator
from session_report_scheduler import SessionReportScheduler
from session_simulator import SessionSimulator


def test_report_generation():
    """리포트 생성 테스트"""
    print("\n" + "=" * 60)
    print("Testing Report Generation")
    print("=" * 60)

    generator = SessionReportGenerator()

    # 1. HTML 리포트 생성
    print("\n1. Generating HTML report...")
    html_report = generator.generate_report(period="weekly", days=7, format="html")
    if html_report:
        print(f"   [OK] HTML report created: {Path(html_report).name}")
    else:
        print("   [FAIL] HTML report generation failed")

    # 2. JSON 리포트 생성
    print("\n2. Generating JSON report...")
    json_report = generator.generate_report(period="weekly", days=7, format="json")
    if json_report:
        print(f"   [OK] JSON report created: {Path(json_report).name}")
    else:
        print("   [FAIL] JSON report generation failed")

    # 3. CSV 내보내기
    print("\n3. Exporting to CSV...")
    csv_file = generator.export_to_csv(days=7)
    if csv_file:
        print(f"   [OK] CSV exported: {Path(csv_file).name}")
    else:
        print("   [FAIL] CSV export failed")

    # 4. PDF 리포트 (matplotlib 설치된 경우)
    try:
        import matplotlib  # noqa: F401

        print("\n4. Generating PDF report...")
        pdf_report = generator.generate_report(period="weekly", days=7, format="pdf")
        if pdf_report:
            print(f"   [OK] PDF report created: {Path(pdf_report).name}")
        else:
            print("   [FAIL] PDF report generation failed")
    except ImportError:
        print("\n4. PDF report skipped (matplotlib not installed)")

    # 5. Excel 내보내기 (pandas 설치된 경우)
    try:
        import pandas  # noqa: F401

        print("\n5. Exporting to Excel...")
        excel_file = generator.export_to_excel(days=7)
        if excel_file:
            print(f"   [OK] Excel exported: {Path(excel_file).name}")
        else:
            print("   [FAIL] Excel export failed")
    except ImportError:
        print("\n5. Excel export skipped (pandas not installed)")

    print("\n" + "=" * 60)
    print("Report Generation Test Complete")
    print("=" * 60)


def test_scheduler():
    """스케줄러 테스트"""
    print("\n" + "=" * 60)
    print("Testing Report Scheduler")
    print("=" * 60)

    scheduler = SessionReportScheduler()

    # 설정 파일 생성 확인
    if scheduler.config_file.exists():
        print(f"\n1. Config file exists: {scheduler.config_file}")
    else:
        print("\n1. Config file not found")

    # 단일 실행 테스트
    print("\n2. Testing single run (weekly report)...")
    report = scheduler.generate_weekly_report()
    if report:
        print(f"   [OK] Weekly report generated: {Path(report).name}")
    else:
        print("   [FAIL] Weekly report generation failed")

    # 마지막 실행 기록 확인
    if scheduler.last_run_file.exists():
        print(f"\n3. Last run recorded: {scheduler.last_run_file}")
    else:
        print("\n3. Last run file not created")

    print("\n" + "=" * 60)
    print("Scheduler Test Complete")
    print("=" * 60)


def generate_sample_data():
    """샘플 데이터 생성"""
    print("\n" + "=" * 60)
    print("Generating Sample Data")
    print("=" * 60)

    simulator = SessionSimulator()

    print("\nSimulating 10 tasks for testing...")
    simulator.simulate_session(num_tasks=10, interval=1)

    print("\n" + "=" * 60)
    print("Sample Data Generated")
    print("=" * 60)


def show_report_paths():
    """생성된 리포트 경로 표시"""
    print("\n" + "=" * 60)
    print("Generated Reports")
    print("=" * 60)

    report_dir = Path("RUNS/reports")
    if report_dir.exists():
        reports = list(report_dir.glob("session_report_*"))
        exports = list(report_dir.glob("session_data_*"))

        if reports:
            print("\nReports:")
            for report in sorted(reports)[-5:]:  # 최근 5개
                print(f"  - {report.name}")

        if exports:
            print("\nData Exports:")
            for export in sorted(exports)[-5:]:  # 최근 5개
                print(f"  - {export.name}")

        print(f"\nTotal files in {report_dir}: {len(list(report_dir.glob('*')))}")
    else:
        print("No reports found")

    print("=" * 60)


def interactive_menu():
    """대화형 메뉴"""
    while True:
        print("\n" + "=" * 60)
        print("Session Report System Test Menu")
        print("=" * 60)
        print("1. Generate sample data")
        print("2. Test report generation")
        print("3. Test scheduler")
        print("4. Generate all report formats")
        print("5. Show generated reports")
        print("6. Run full test suite")
        print("0. Exit")
        print("=" * 60)

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            generate_sample_data()
        elif choice == "2":
            test_report_generation()
        elif choice == "3":
            test_scheduler()
        elif choice == "4":
            generator = SessionReportGenerator()
            print("\nGenerating all formats...")
            for format in ["html", "json", "pdf"]:
                try:
                    report = generator.generate_report(period="weekly", format=format)
                    if report:
                        print(f"  - {format.upper()}: {Path(report).name}")
                except Exception:
                    print(f"  - {format.upper()}: Failed")
        elif choice == "5":
            show_report_paths()
        elif choice == "6":
            generate_sample_data()
            time.sleep(2)
            test_report_generation()
            test_scheduler()
            show_report_paths()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please try again.")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Test session report system")
    parser.add_argument("--auto", action="store_true", help="Run automated test suite")
    parser.add_argument("--interactive", action="store_true", help="Run interactive menu")

    args = parser.parse_args()

    if args.auto:
        # 자동 테스트 실행
        print("Running automated test suite...")
        generate_sample_data()
        time.sleep(2)
        test_report_generation()
        test_scheduler()
        show_report_paths()
    elif args.interactive:
        # 대화형 메뉴
        interactive_menu()
    else:
        # 기본: 간단한 테스트
        print("Running basic test...")
        test_report_generation()
        show_report_paths()


if __name__ == "__main__":
    main()
