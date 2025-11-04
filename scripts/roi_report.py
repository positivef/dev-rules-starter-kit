"""ROI Report Generator

헌법 기반 실행형 자산 시스템의 핵심 KPI를 계산하여 JSON/Markdown Evidence로 저장합니다.

Usage:
    python scripts/roi_report.py --time-invested-hours 264 --time-saved-hours 264 --hourly-rate 80
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

DEFAULT_HOURLY_RATE = 80  # USD 또는 현지 통화 환산 기준


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ROI metrics for the Development Rules Starter Kit")
    parser.add_argument("--time-invested-hours", type=float, default=264.0, help="초기 구축에 투입된 총 시간")
    parser.add_argument("--time-saved-hours", type=float, default=264.0, help="연간 절약 가능한 시간")
    parser.add_argument("--hourly-rate", type=float, default=DEFAULT_HOURLY_RATE, help="평균 시간당 비용")
    parser.add_argument("--governance-reviews", type=int, default=0, help="기간 내 완료한 거버넌스 리뷰 수")
    parser.add_argument(
        "--compliance-rate",
        type=float,
        default=97.5,
        help="헌법 조항 준수율(%)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("RUNS/reports"),
        help="ROI 리포트를 저장할 경로 (기본: RUNS/reports)",
    )
    return parser.parse_args()


def compute_roi(time_invested: float, time_saved: float, hourly_rate: float) -> Dict[str, float]:
    investment_cost = time_invested * hourly_rate
    annual_savings = time_saved * hourly_rate
    if investment_cost == 0:
        roi_percent = 0.0
    else:
        roi_percent = ((annual_savings - investment_cost) / investment_cost) * 100

    multi_year = {
        "year_1": roi_percent,
        "year_2": ((annual_savings * 2 - investment_cost) / investment_cost) * 100 if investment_cost else 0.0,
        "year_5": ((annual_savings * 5 - investment_cost) / investment_cost) * 100 if investment_cost else 0.0,
    }

    return {
        "investment_cost": round(investment_cost, 2),
        "annual_savings": round(annual_savings, 2),
        "roi_percent_year_1": round(multi_year["year_1"], 2),
        "roi_percent_year_2": round(multi_year["year_2"], 2),
        "roi_percent_year_5": round(multi_year["year_5"], 2),
    }


def persist_report(data: Dict[str, float], args: argparse.Namespace) -> Path:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "generated_at": timestamp,
        "time_invested_hours": args.time_invested_hours,
        "time_saved_hours": args.time_saved_hours,
        "hourly_rate": args.hourly_rate,
        "governance_reviews_completed": args.governance_reviews,
        "constitution_compliance_rate": args.compliance_rate,
        "time_saved_value": round(args.time_saved_hours * args.hourly_rate, 2),
    }
    payload.update(data)

    json_path = args.output_dir / "latest_roi.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    markdown_path = args.output_dir / f"roi_{timestamp}.md"
    with markdown_path.open("w", encoding="utf-8") as f:
        f.write("# ROI Report\n\n")
        f.write(f"- 생성 시각: {timestamp} UTC\n")
        f.write(f"- 연간 절약 시간: {args.time_saved_hours}시간\n")
        f.write(f"- 헌법 준수율: {args.compliance_rate}%\n")
        f.write(f"- 거버넌스 리뷰 수: {args.governance_reviews}\n")
        f.write(f"- 연간 비용 절감액: {payload['annual_savings']}\n")
        f.write(f"- 1년 ROI: {payload['roi_percent_year_1']}%\n")
        f.write(f"- 2년 ROI: {payload['roi_percent_year_2']}%\n")
        f.write(f"- 5년 ROI: {payload['roi_percent_year_5']}%\n")

    return json_path


def main() -> None:
    args = parse_args()
    metrics = compute_roi(args.time_invested_hours, args.time_saved_hours, args.hourly_rate)
    output = persist_report(metrics, args)
    print(f"[OK] ROI report generated at {output}")


if __name__ == "__main__":
    main()
