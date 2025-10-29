#!/usr/bin/env python3
"""
Session Report Generator - Session data report generation and export

Features:
- HTML/PDF report generation
- CSV/Excel data export
- Weekly/monthly/custom period reports
- Charts and graphs included
- Email sending support (optional)

Usage:
    python scripts/session_report_generator.py --period weekly
    python scripts/session_report_generator.py --days 30 --format pdf
    python scripts/session_report_generator.py --export csv
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import argparse

sys.path.insert(0, str(Path(__file__).parent))

# 필수 import
from session_analyzer import SessionAnalyzer

# 선택적 import (설치되어 있을 경우)
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("[INFO] pandas not installed. Excel export will be limited.")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[INFO] matplotlib not installed. Charts will not be included.")

try:
    from jinja2 import Template

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("[INFO] jinja2 not installed. HTML reports will be basic.")


class SessionReportGenerator:
    """세션 리포트 생성기"""

    def __init__(self, analyzer=None, output_dir=None):
        """초기화 with dependency injection (P4 compliance)"""
        # Use dependency injection pattern
        self.analyzer = analyzer or self._create_analyzer()
        self.output_dir = output_dir or Path("RUNS/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _create_analyzer():
        """Factory method for SessionAnalyzer (P4 compliance)"""
        return SessionAnalyzer()

    def generate_report(self, period: str = "weekly", days: Optional[int] = None, format: str = "html") -> str:
        """
        리포트 생성

        Args:
            period: 기간 (daily, weekly, monthly, custom)
            days: 사용자 정의 일수
            format: 출력 형식 (html, pdf, json)

        Returns:
            생성된 리포트 파일 경로
        """
        # 기간 설정
        if period == "daily":
            analysis_days = 1
        elif period == "weekly":
            analysis_days = 7
        elif period == "monthly":
            analysis_days = 30
        elif period == "custom" and days:
            analysis_days = days
        else:
            analysis_days = 7  # 기본값

        print(f"[INFO] Generating {period} report for {analysis_days} days...")

        # 데이터 분석
        analysis_results = self.analyzer.analyze_all(days=analysis_days)

        if "error" in analysis_results:
            print(f"[ERROR] {analysis_results['error']}")
            return ""

        # 리포트 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "html":
            output_file = self._generate_html_report(analysis_results, period, analysis_days, timestamp)
        elif format == "pdf" and MATPLOTLIB_AVAILABLE:
            output_file = self._generate_pdf_report(analysis_results, period, analysis_days, timestamp)
        elif format == "json":
            output_file = self._generate_json_report(analysis_results, period, analysis_days, timestamp)
        else:
            print(f"[ERROR] Unsupported format: {format}")
            return ""

        print(f"[SUCCESS] Report generated: {output_file}")
        return str(output_file)

    def _generate_html_report(self, data: Dict[str, Any], period: str, days: int, timestamp: str) -> str:
        """HTML 리포트 생성"""
        output_file = self.output_dir / f"session_report_{period}_{timestamp}.html"

        if JINJA2_AVAILABLE:
            html_content = self._render_html_template(data, period, days)
        else:
            html_content = self._generate_basic_html(data, period, days)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(output_file)

    def _render_html_template(self, data: Dict[str, Any], period: str, days: int) -> str:
        """Jinja2 템플릿으로 HTML 렌더링"""
        template_str = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Report - {{ period|title }} ({{ days }} days)</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            margin-top: 10px;
        }
        .success { color: #28a745; }
        .failure { color: #dc3545; }
        .neutral { color: #6c757d; }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .insight-box {
            padding: 15px;
            border-left: 4px solid;
            margin-bottom: 10px;
            background: white;
            border-radius: 5px;
        }
        .recommendation {
            border-left-color: #007bff;
            background: #e7f3ff;
        }
        .warning {
            border-left-color: #ffc107;
            background: #fff8e1;
        }
        .positive {
            border-left-color: #28a745;
            background: #e8f5e9;
        }
        .footer {
            text-align: center;
            color: #666;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Session Management Report</h1>
        <p>Period: {{ period|title }} | Duration: {{ days }} days</p>
        <p>Generated: {{ now }}</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{{ stats.total_tasks }}</div>
            <div class="metric-label">Total Tasks</div>
        </div>
        <div class="metric-card">
            <div class="metric-value success">{{ stats.successful_tasks }}</div>
            <div class="metric-label">Successful</div>
        </div>
        <div class="metric-card">
            <div class="metric-value failure">{{ stats.failed_tasks }}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value neutral">{{ "%.1f"|format(stats.success_rate) }}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
    </div>

    <div class="metric-card">
        <h2>Most Frequent Tasks</h2>
        <table>
            <thead>
                <tr>
                    <th>Task ID</th>
                    <th>Executions</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {% for task, count in task_patterns.most_frequent_tasks[:10] %}
                <tr>
                    <td>{{ task }}</td>
                    <td>{{ count }}</td>
                    <td>{{ "%.1f"|format(count / stats.total_tasks * 100) }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    {% if task_patterns.failed_tasks %}
    <div class="metric-card">
        <h2>Failed Tasks</h2>
        <table>
            <thead>
                <tr>
                    <th>Task ID</th>
                    <th>Failures</th>
                </tr>
            </thead>
            <tbody>
                {% for task, count in task_patterns.failed_tasks[:5] %}
                <tr>
                    <td>{{ task }}</td>
                    <td class="failure">{{ count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <div class="metric-card">
        <h2>Productivity Insights</h2>
        <p><strong>Average Session Duration:</strong>
            {{ "%.0f"|format(productivity.avg_session_duration_minutes) }} minutes</p>
        <p><strong>Total Sessions:</strong> {{ productivity.total_sessions }}</p>

        {% if productivity.peak_hours %}
        <p><strong>Most Productive Hours:</strong>
        {% for hour, count in productivity.peak_hours[:3] %}
            {{ hour }}:00 ({{ count }} sessions){% if not loop.last %}, {% endif %}
        {% endfor %}
        </p>
        {% endif %}
    </div>

    {% if insights %}
    <div class="metric-card">
        <h2>Recommendations & Insights</h2>

        {% for rec in insights.recommendations %}
        <div class="insight-box recommendation">
            💡 {{ rec }}
        </div>
        {% endfor %}

        {% for warning in insights.warnings %}
        <div class="insight-box warning">
            ⚠️ {{ warning }}
        </div>
        {% endfor %}

        {% for positive in insights.positive_patterns %}
        <div class="insight-box positive">
            ✅ {{ positive }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>Generated by SessionManager Report System</p>
        <p>© 2025 Dev Rules Starter Kit</p>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            period=period,
            days=days,
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stats=data.get("execution_stats", {}),
            task_patterns=data.get("task_patterns", {}),
            productivity=data.get("productivity", {}),
            insights=data.get("insights", {}),
            error_patterns=data.get("error_patterns", {}),
        )

    def _generate_basic_html(self, data: Dict[str, Any], period: str, days: int) -> str:
        """기본 HTML 생성 (Jinja2 없을 때)"""
        stats = data.get("execution_stats", {})
        task_patterns = data.get("task_patterns", {})
        insights = data.get("insights", {})

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Session Report - {period.title()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
    </style>
</head>
<body>
    <h1>Session Management Report</h1>
    <p>Period: {period.title()} ({days} days)</p>
    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <h2>Summary</h2>
    <ul>
        <li>Total Tasks: {stats.get('total_tasks', 0)}</li>
        <li class="success">Successful: {stats.get('successful_tasks', 0)}</li>
        <li class="failure">Failed: {stats.get('failed_tasks', 0)}</li>
        <li>Success Rate: {stats.get('success_rate', 0):.1f}%</li>
    </ul>

    <h2>Most Frequent Tasks</h2>
    <table>
        <tr>
            <th>Task ID</th>
            <th>Count</th>
        </tr>
"""

        for task, count in task_patterns.get("most_frequent_tasks", [])[:10]:
            html += f"""
        <tr>
            <td>{task}</td>
            <td>{count}</td>
        </tr>
"""

        html += """
    </table>

    <h2>Insights</h2>
    <ul>
"""

        for rec in insights.get("recommendations", []):
            html += f"        <li>{rec}</li>\n"

        html += """
    </ul>
</body>
</html>
"""
        return html

    def _generate_pdf_report(self, data: Dict[str, Any], period: str, days: int, timestamp: str) -> str:
        """PDF 리포트 생성 (matplotlib 사용)"""
        output_file = self.output_dir / f"session_report_{period}_{timestamp}.pdf"

        with PdfPages(output_file) as pdf:
            # Page 1: Summary
            self._create_summary_page(data, period, days, pdf)

            # Page 2: Task Analysis
            self._create_task_analysis_page(data, pdf)

            # Page 3: Productivity Analysis
            self._create_productivity_page(data, pdf)

            # PDF metadata
            d = pdf.infodict()
            d["Title"] = f"Session Report - {period.title()}"
            d["Author"] = "SessionManager"
            d["Subject"] = f"Session Analysis for {days} days"
            d["Keywords"] = "Session, Analysis, Report"
            d["CreationDate"] = datetime.now()

        return str(output_file)

    def _create_summary_page(self, data: Dict[str, Any], period: str, days: int, pdf: "PdfPages") -> None:
        """PDF 요약 페이지 생성"""
        fig = plt.figure(figsize=(8.5, 11))

        # Title
        fig.text(0.5, 0.95, f"Session Report - {period.title()}", ha="center", size=20, weight="bold")
        fig.text(0.5, 0.92, f"Period: {days} days", ha="center", size=12)
        fig.text(0.5, 0.89, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ha="center", size=10)

        # Stats
        stats = data.get("execution_stats", {})
        y_pos = 0.75

        stats_text = f"""
Total Tasks: {stats.get('total_tasks', 0)}
Successful: {stats.get('successful_tasks', 0)}
Failed: {stats.get('failed_tasks', 0)}
Success Rate: {stats.get('success_rate', 0):.1f}%
Total Execution Time: {stats.get('total_execution_hours', 0):.1f} hours
"""

        fig.text(0.1, y_pos, stats_text, size=12, family="monospace")

        # Success/Failure Pie Chart
        ax = fig.add_subplot(2, 1, 2)
        sizes = [stats.get("successful_tasks", 0), stats.get("failed_tasks", 0)]
        labels = ["Success", "Failed"]
        colors = ["#28a745", "#dc3545"]

        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
            ax.set_title("Success/Failure Distribution")

        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    def _create_task_analysis_page(self, data: Dict[str, Any], pdf: "PdfPages") -> None:
        """PDF 작업 분석 페이지"""
        fig, axes = plt.subplots(2, 1, figsize=(8.5, 11))

        task_patterns = data.get("task_patterns", {})

        # Most frequent tasks
        frequent_tasks = task_patterns.get("most_frequent_tasks", [])[:10]
        if frequent_tasks:
            tasks = [t[0] for t in frequent_tasks]
            counts = [t[1] for t in frequent_tasks]

            axes[0].barh(range(len(tasks)), counts, color="#007bff")
            axes[0].set_yticks(range(len(tasks)))
            axes[0].set_yticklabels(tasks)
            axes[0].set_xlabel("Execution Count")
            axes[0].set_title("Most Frequent Tasks")
            axes[0].invert_yaxis()

        # Failed tasks
        failed_tasks = task_patterns.get("failed_tasks", [])[:5]
        if failed_tasks:
            tasks = [t[0] for t in failed_tasks]
            counts = [t[1] for t in failed_tasks]

            axes[1].bar(range(len(tasks)), counts, color="#dc3545")
            axes[1].set_xticks(range(len(tasks)))
            axes[1].set_xticklabels(tasks, rotation=45, ha="right")
            axes[1].set_ylabel("Failure Count")
            axes[1].set_title("Most Failed Tasks")

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    def _create_productivity_page(self, data: Dict[str, Any], pdf: "PdfPages") -> None:
        """PDF 생산성 분석 페이지"""
        fig, axes = plt.subplots(2, 1, figsize=(8.5, 11))

        productivity = data.get("productivity", {})

        # Hourly distribution
        hourly = productivity.get("hourly_distribution", {})
        if hourly:
            hours = list(range(24))
            counts = [hourly.get(h, 0) for h in hours]

            axes[0].bar(hours, counts, color="#28a745")
            axes[0].set_xlabel("Hour of Day")
            axes[0].set_ylabel("Session Count")
            axes[0].set_title("Activity by Hour")
            axes[0].set_xticks(hours)

        # Daily distribution
        daily = productivity.get("daily_distribution", {})
        if daily:
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            days = [d for d in days_order if d in daily]
            counts = [daily[d] for d in days]

            axes[1].bar(range(len(days)), counts, color="#007bff")
            axes[1].set_xticks(range(len(days)))
            axes[1].set_xticklabels(days, rotation=45, ha="right")
            axes[1].set_ylabel("Session Count")
            axes[1].set_title("Activity by Day of Week")

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    def _generate_json_report(self, data: Dict[str, Any], period: str, days: int, timestamp: str) -> str:
        """JSON 리포트 생성"""
        output_file = self.output_dir / f"session_report_{period}_{timestamp}.json"

        report_data = {
            "metadata": {
                "period": period,
                "days": days,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "timestamp": timestamp,
            },
            "analysis": data,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=True)

        return str(output_file)

    def export_to_csv(self, days: int = 7) -> str:
        """CSV로 데이터 내보내기"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"session_data_{timestamp}.csv"

        # 세션 로드
        self.analyzer.load_sessions(days)

        rows = []
        for session in self.analyzer.sessions_data:
            scope_data = session.get("scope_data", {})
            session_data = scope_data.get("session", {})

            # 현재 작업 정보
            current_task = session_data.get("current_task", {})
            if current_task:
                rows.append(
                    {
                        "session_id": session.get("session_id", ""),
                        "started_at": session.get("started_at", ""),
                        "task_id": current_task.get("task_id", ""),
                        "title": current_task.get("title", ""),
                        "status": current_task.get("status", ""),
                        "execution_time": current_task.get("execution_time", 0),
                        "error": current_task.get("error", ""),
                    }
                )

        # CSV 작성
        if rows:
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["session_id", "started_at", "task_id", "title", "status", "execution_time", "error"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        print(f"[SUCCESS] CSV exported: {output_file}")
        return str(output_file)

    def export_to_excel(self, days: int = 7) -> str:
        """Excel로 데이터 내보내기 (pandas 필요)"""
        if not PANDAS_AVAILABLE:
            print("[ERROR] pandas is required for Excel export")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"session_data_{timestamp}.xlsx"

        # 분석 실행
        data = self.analyzer.analyze_all(days)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Summary sheet
            summary_df = pd.DataFrame(
                [
                    {
                        "Total Tasks": data["execution_stats"].get("total_tasks", 0),
                        "Successful": data["execution_stats"].get("successful_tasks", 0),
                        "Failed": data["execution_stats"].get("failed_tasks", 0),
                        "Success Rate": data["execution_stats"].get("success_rate", 0),
                        "Total Hours": data["execution_stats"].get("total_execution_hours", 0),
                    }
                ]
            )
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Task patterns sheet
            if data["task_patterns"].get("most_frequent_tasks"):
                tasks_df = pd.DataFrame(data["task_patterns"]["most_frequent_tasks"], columns=["Task ID", "Count"])
                tasks_df.to_excel(writer, sheet_name="Task Patterns", index=False)

            # Failed tasks sheet
            if data["task_patterns"].get("failed_tasks"):
                failed_df = pd.DataFrame(data["task_patterns"]["failed_tasks"], columns=["Task ID", "Failures"])
                failed_df.to_excel(writer, sheet_name="Failed Tasks", index=False)

        print(f"[SUCCESS] Excel exported: {output_file}")
        return str(output_file)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Generate session reports and export data")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly", "custom"], default="weekly", help="Report period")
    parser.add_argument("--days", type=int, help="Number of days for custom period")
    parser.add_argument("--format", choices=["html", "pdf", "json"], default="html", help="Output format")
    parser.add_argument("--export", choices=["csv", "excel"], help="Export data to CSV or Excel")

    args = parser.parse_args()

    generator = SessionReportGenerator()

    # 데이터 내보내기
    if args.export:
        if args.export == "csv":
            generator.export_to_csv(args.days or 7)
        elif args.export == "excel":
            generator.export_to_excel(args.days or 7)
    else:
        # 리포트 생성
        generator.generate_report(period=args.period, days=args.days, format=args.format)


if __name__ == "__main__":
    main()
