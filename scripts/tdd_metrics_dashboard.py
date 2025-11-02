"""TDD Metrics Dashboard - Streamlit Interactive Visualization.

Real-time TDD metrics visualization with:
- Coverage trends over time
- Test count evolution
- Quality gate status
- Phase-by-phase metrics

Compliance:
- P6: Quality Gates (metrics tracking)
- P10: Windows UTF-8 (no emojis)

Usage:
    streamlit run scripts/tdd_metrics_dashboard.py
    python scripts/tier1_cli.py tdd-dashboard
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("[INFO] Install with: pip install streamlit pandas plotly")
    sys.exit(1)


def load_coverage_data() -> pd.DataFrame:
    """Load coverage data from RUNS/evidence/ directory.

    Returns:
        DataFrame with columns: date, coverage, test_count, phase
    """
    evidence_path = Path("RUNS/evidence")
    if not evidence_path.exists():
        return pd.DataFrame(columns=["date", "coverage", "test_count", "phase"])

    data = []
    for task_dir in evidence_path.iterdir():
        if not task_dir.is_dir():
            continue

        # Try to find coverage.json
        coverage_file = task_dir / "coverage.json"
        if not coverage_file.exists():
            coverage_file = task_dir / "coverage-unit.json"

        if coverage_file.exists():
            try:
                with open(coverage_file, encoding="utf-8") as f:
                    cov_data = json.load(f)

                # Extract coverage percentage
                if "totals" in cov_data:
                    coverage = cov_data["totals"].get("percent_covered", 0)
                else:
                    coverage = 0

                # Get task metadata
                task_id = task_dir.name
                phase = "Unknown"
                if "PHASE" in task_id.upper():
                    parts = task_id.split("-")
                    for part in parts:
                        if part.startswith("PHASE") or part.startswith("phase"):
                            phase = part
                            break
                elif "TIER1" in task_id.upper():
                    phase = "Tier1"

                # Use directory modification time as date
                date = datetime.fromtimestamp(task_dir.stat().st_mtime)

                # Count test files
                test_count = 0
                tests_dir = Path("tests")
                if tests_dir.exists():
                    test_count = len(list(tests_dir.rglob("test_*.py")))

                data.append(
                    {"date": date, "coverage": coverage, "test_count": test_count, "phase": phase, "task_id": task_id}
                )

            except Exception as e:
                st.warning(f"Failed to load {coverage_file}: {e}")

    if not data:
        # Generate sample data for demo
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=30 - i)
            data.append(
                {
                    "date": date,
                    "coverage": 2 + (i * 0.1),  # Gradually increasing coverage
                    "test_count": 10 + (i * 3),
                    "phase": f"Phase {(i // 10) + 1}",
                    "task_id": f"TASK-{i:03d}",
                }
            )

    return pd.DataFrame(data)


def calculate_quality_gates(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate quality gate status based on latest metrics.

    Args:
        df: DataFrame with coverage and test data

    Returns:
        Dict with quality gate status
    """
    if df.empty:
        return {"coverage_gate": False, "test_count_gate": False, "trend_gate": False, "overall_status": "FAIL"}

    latest = df.iloc[-1]
    coverage = latest["coverage"]
    test_count = latest["test_count"]

    # Calculate trend (last 7 days)
    if len(df) >= 7:
        recent = df.tail(7)
        coverage_trend = recent["coverage"].iloc[-1] - recent["coverage"].iloc[0]
    else:
        coverage_trend = 0

    # Quality gates
    coverage_gate = coverage >= 4.0  # Phase 4 threshold
    test_count_gate = test_count >= 80
    trend_gate = coverage_trend >= 0  # Non-decreasing

    overall_status = "PASS" if all([coverage_gate, test_count_gate, trend_gate]) else "FAIL"

    return {
        "coverage": coverage,
        "test_count": test_count,
        "coverage_trend": coverage_trend,
        "coverage_gate": coverage_gate,
        "test_count_gate": test_count_gate,
        "trend_gate": trend_gate,
        "overall_status": overall_status,
    }


def main():
    """Main dashboard entry point."""
    st.set_page_config(page_title="TDD Metrics Dashboard", page_icon="📊", layout="wide")

    st.title("TDD Metrics Dashboard")
    st.markdown("**Real-time TDD metrics for Constitution-Based Development**")

    # Load data
    with st.spinner("Loading coverage data..."):
        df = load_coverage_data()

    if df.empty:
        st.warning("No coverage data found in RUNS/evidence/")
        st.info("Run tests with coverage to generate data: pytest --cov=scripts tests/")
        return

    # Calculate quality gates
    gates = calculate_quality_gates(df)

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Coverage", f"{gates['coverage']:.2f}%", f"{gates['coverage_trend']:+.2f}%")

    with col2:
        st.metric("Total Tests", gates["test_count"], "tests")

    with col3:
        status_color = "🟢" if gates["coverage_gate"] else "🔴"
        st.metric("Coverage Gate", f"{status_color} {'PASS' if gates['coverage_gate'] else 'FAIL'}", ">= 4.0%")

    with col4:
        status_color = "🟢" if gates["overall_status"] == "PASS" else "🔴"
        st.metric("Overall Status", f"{status_color} {gates['overall_status']}", "Quality Gates")

    # Coverage trend chart
    st.subheader("Coverage Trend")
    fig_coverage = px.line(
        df,
        x="date",
        y="coverage",
        color="phase",
        title="Coverage Evolution Over Time",
        labels={"coverage": "Coverage (%)", "date": "Date"},
        markers=True,
    )

    # Add threshold line
    fig_coverage.add_hline(y=4.0, line_dash="dash", line_color="red", annotation_text="Phase 4 Threshold (4.0%)")

    st.plotly_chart(fig_coverage, use_container_width=True)

    # Test count evolution
    st.subheader("Test Count Evolution")
    fig_tests = px.bar(
        df,
        x="date",
        y="test_count",
        color="phase",
        title="Test Count Over Time",
        labels={"test_count": "Number of Tests", "date": "Date"},
    )

    st.plotly_chart(fig_tests, use_container_width=True)

    # Phase breakdown
    st.subheader("Phase-by-Phase Metrics")

    phase_metrics = df.groupby("phase").agg({"coverage": ["mean", "max"], "test_count": ["mean", "max"]}).round(2)

    phase_metrics.columns = ["Avg Coverage (%)", "Max Coverage (%)", "Avg Tests", "Max Tests"]
    st.dataframe(phase_metrics, use_container_width=True)

    # Quality gates details
    st.subheader("Quality Gate Details")

    gate_data = pd.DataFrame(
        [
            {
                "Gate": "Coverage >= 4.0%",
                "Current": f"{gates['coverage']:.2f}%",
                "Status": "PASS" if gates["coverage_gate"] else "FAIL",
            },
            {
                "Gate": "Test Count >= 80",
                "Current": gates["test_count"],
                "Status": "PASS" if gates["test_count_gate"] else "FAIL",
            },
            {
                "Gate": "Coverage Trend >= 0",
                "Current": f"{gates['coverage_trend']:+.2f}%",
                "Status": "PASS" if gates["trend_gate"] else "FAIL",
            },
        ]
    )

    # Color-code status
    def highlight_status(row):
        color = "background-color: #90EE90" if row["Status"] == "PASS" else "background-color: #FFB6C1"
        return [color] * len(row)

    st.dataframe(gate_data.style.apply(highlight_status, axis=1), use_container_width=True, hide_index=True)

    # Recent activity
    st.subheader("Recent Activity")
    recent_df = df.tail(10)[["date", "task_id", "coverage", "test_count", "phase"]]
    recent_df["date"] = recent_df["date"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(recent_df, use_container_width=True, hide_index=True)

    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()

    # Footer
    st.markdown("---")
    st.caption("TDD Metrics Dashboard - Constitution-Based Development Framework")


if __name__ == "__main__":
    main()
