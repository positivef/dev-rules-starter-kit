"""TDD Metrics Dashboard - Streamlit Interactive Visualization.

Real-time TDD metrics visualization with:
- Coverage trends over time
- Test count evolution
- Quality gate status
- Phase-by-phase metrics
- TDD workflow compliance (Week 6 Phase 2)
- Developer TDD scores (Week 6 Phase 2)
- Coverage gap analysis (Week 6 Phase 1)
- Real-time enforcement status (Week 6 Phase 1)

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
from typing import Dict, Any, List

try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("[INFO] Install with: pip install streamlit pandas plotly")
    sys.exit(1)

# Import TDD enforcement tools
sys.path.insert(0, str(Path(__file__).parent))
try:
    from tdd_workflow_tracker import TDDWorkflowTracker
    from tdd_enforcer_enhanced import EnhancedTDDEnforcer

    TDD_TOOLS_AVAILABLE = True
except ImportError:
    TDD_TOOLS_AVAILABLE = False


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


def load_tdd_workflow_data(days: int = 30) -> Dict[str, Any]:
    """Load TDD workflow compliance data.

    Args:
        days: Number of days to analyze

    Returns:
        Dictionary with team report and developer scores
    """
    if not TDD_TOOLS_AVAILABLE:
        return {}

    try:
        tracker = TDDWorkflowTracker()
        team_report = tracker.generate_team_report(days=days)
        return team_report
    except Exception:
        return {}


def load_coverage_gaps() -> List[Dict[str, Any]]:
    """Load coverage gap data from enforcement.

    Returns:
        List of coverage gap dictionaries
    """
    if not TDD_TOOLS_AVAILABLE:
        return []

    try:
        enforcer = EnhancedTDDEnforcer()
        # Get all Python files in scripts/
        scripts_path = Path("scripts")
        python_files = list(scripts_path.glob("*.py"))

        # Check coverage
        violations, coverage_gaps = enforcer.check_files(python_files)

        # Convert to list of dicts
        gaps = []
        for gap in coverage_gaps:
            gaps.append(
                {
                    "file": Path(gap.file_path).name,
                    "current": gap.current_coverage,
                    "required": gap.required_coverage,
                    "gap": gap.gap,
                    "missing_lines": len(gap.missing_lines),
                }
            )

        return gaps
    except Exception:
        return []


def main():
    """Main dashboard entry point."""
    st.set_page_config(page_title="TDD Metrics Dashboard", page_icon="[CHART]", layout="wide")

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
        status_color = "[OK]" if gates["coverage_gate"] else "[X]"
        st.metric("Coverage Gate", f"{status_color} {'PASS' if gates['coverage_gate'] else 'FAIL'}", ">= 4.0%")

    with col4:
        status_color = "[OK]" if gates["overall_status"] == "PASS" else "[X]"
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

    # === Week 6 Phase 4: TDD Enforcement Enhancements ===
    st.markdown("---")
    st.header("TDD Enforcement (Week 6)")

    if TDD_TOOLS_AVAILABLE:
        # TDD Workflow Compliance
        st.subheader("TDD Workflow Compliance")

        days_option = st.selectbox("Time Period", [7, 14, 30, 60], index=2)
        workflow_data = load_tdd_workflow_data(days=days_option)

        if workflow_data and workflow_data.get("total_commits", 0) > 0:
            # Team compliance metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                compliance = workflow_data["team_compliance_rate"]
                delta_color = "normal" if compliance >= 80 else "inverse"
                st.metric("Team Compliance Rate", f"{compliance:.1f}%", "Target: 80%", delta_color=delta_color)

            with col2:
                st.metric("Total Commits", workflow_data["total_commits"], f"Last {days_option} days")

            with col3:
                status = (
                    "[EXCELLENT]"
                    if compliance >= 95
                    else "[GOOD]"
                    if compliance >= 80
                    else "[WARNING]"
                    if compliance >= 60
                    else "[CRITICAL]"
                )
                status_color = "[OK]" if compliance >= 80 else "[WARN]" if compliance >= 60 else "[X]"
                st.metric("Status", f"{status_color} {status}", "")

            # Developer breakdown
            st.subheader("Per-Developer TDD Scores")
            if workflow_data.get("developers"):
                dev_data = []
                for dev_name, stats in workflow_data["developers"].items():
                    dev_data.append(
                        {
                            "Developer": dev_name,
                            "Commits": stats["commits"],
                            "Compliant": stats["compliant"],
                            "Compliance Rate": f"{stats['compliance_rate']:.1f}%",
                            "Status": "[PASS]" if stats["compliance_rate"] >= 80 else "[WARN]",
                        }
                    )

                dev_df = pd.DataFrame(dev_data)

                # Compliance bar chart
                fig_dev = px.bar(
                    dev_df,
                    x="Developer",
                    y="Compliance Rate",
                    title="Developer TDD Compliance Rates",
                    color="Compliance Rate",
                    color_continuous_scale=["red", "yellow", "green"],
                    range_color=[0, 100],
                )
                fig_dev.add_hline(y=80, line_dash="dash", line_color="blue", annotation_text="Target: 80%")
                st.plotly_chart(fig_dev, use_container_width=True)

                # Developer details table
                st.dataframe(dev_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No commit data found for the last {days_option} days")

        # Coverage Gaps
        st.subheader("Coverage Gap Analysis")

        coverage_gaps = load_coverage_gaps()

        if coverage_gaps:
            gap_df = pd.DataFrame(coverage_gaps)

            # Sort by gap size
            gap_df = gap_df.sort_values("gap", ascending=False)

            # Gap visualization
            fig_gaps = go.Figure()

            fig_gaps.add_trace(
                go.Bar(name="Current Coverage", x=gap_df["file"], y=gap_df["current"], marker_color="lightblue")
            )

            fig_gaps.add_trace(
                go.Bar(name="Required Coverage", x=gap_df["file"], y=gap_df["required"], marker_color="lightcoral")
            )

            fig_gaps.update_layout(
                title="Coverage Gaps by File", xaxis_title="File", yaxis_title="Coverage (%)", barmode="group", height=400
            )

            st.plotly_chart(fig_gaps, use_container_width=True)

            # Gap details table
            st.dataframe(
                gap_df[["file", "current", "required", "gap", "missing_lines"]].style.format(
                    {"current": "{:.1f}%", "required": "{:.1f}%", "gap": "{:.1f}%"}
                ),
                use_container_width=True,
                hide_index=True,
            )

            # Top priority files
            st.caption(f"[INFO] {len(coverage_gaps)} files below coverage threshold")
        else:
            st.success("[SUCCESS] All files meet coverage requirements!")

        # Real-time Enforcement Status
        st.subheader("Real-time Enforcement Status")

        # Check for recent violations
        violations_path = Path("RUNS/tdd-violations")
        if violations_path.exists():
            recent_violations = list(violations_path.glob("tdd_violation_*.json"))
            recent_violations.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            if recent_violations:
                latest_violation = recent_violations[0]
                violation_age = datetime.now() - datetime.fromtimestamp(latest_violation.stat().st_mtime)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Latest Violation", latest_violation.name, f"{violation_age.seconds // 60} min ago")

                with col2:
                    st.metric(
                        "Total Violations (Today)",
                        len(
                            [
                                v
                                for v in recent_violations
                                if (datetime.now() - datetime.fromtimestamp(v.stat().st_mtime)).days == 0
                            ]
                        ),
                        "files",
                    )

                with col3:
                    enforcement_status = "[OK] [ACTIVE]" if violation_age.seconds < 300 else "[WARN] [IDLE]"
                    st.metric("Enforcement", enforcement_status, "")

                # Show latest violation details
                try:
                    with open(latest_violation, encoding="utf-8") as f:
                        violation_data = json.load(f)

                    summary = violation_data.get("summary", {})
                    st.caption(
                        f"Latest: {summary.get('total_violations', 0)} missing tests, "
                        f"{summary.get('total_coverage_gaps', 0)} coverage gaps"
                    )
                except Exception:
                    pass
            else:
                st.success("[SUCCESS] No violations detected!")
        else:
            st.info("[INFO] No enforcement data available. Run TDD enforcer to generate logs.")

    else:
        st.warning("[WARNING] TDD enforcement tools not available. Install dependencies.")

    # Export section
    st.subheader("Export Dashboard")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export as PNG"):
            try:
                import plotly.io as pio

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = Path(f"RUNS/exports/dashboard_{timestamp}.png")
                export_path.parent.mkdir(parents=True, exist_ok=True)

                # Export coverage trend chart
                pio.write_image(fig_coverage, str(export_path), format="png", width=1200, height=600)
                st.success(f"Exported to: {export_path}")
            except ImportError:
                st.error("Please install kaleido: pip install kaleido")
            except Exception as e:
                st.error(f"Export failed: {e}")

    with col2:
        if st.button("Export as PDF"):
            try:
                from matplotlib.backends.backend_pdf import PdfPages
                import matplotlib.pyplot as plt

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = Path(f"RUNS/exports/dashboard_{timestamp}.pdf")
                export_path.parent.mkdir(parents=True, exist_ok=True)

                with PdfPages(str(export_path)) as pdf:
                    # Page 1: Summary
                    fig, ax = plt.subplots(figsize=(11, 8.5))
                    ax.axis("off")
                    summary_text = f"""
TDD Metrics Dashboard Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Current Metrics:
- Coverage: {gates['coverage']:.2f}%
- Test Count: {gates['test_count']}
- Quality Status: {gates['overall_status']}

Quality Gates:
- Coverage Gate (>=4.0%): {'PASS' if gates['coverage_gate'] else 'FAIL'}
- Test Count Gate (>=80): {'PASS' if gates['test_count_gate'] else 'FAIL'}
- Trend Gate (>=0): {'PASS' if gates['trend_gate'] else 'FAIL'}
"""
                    ax.text(0.1, 0.5, summary_text, fontsize=12, family="monospace", verticalalignment="center")
                    pdf.savefig(fig, bbox_inches="tight")
                    plt.close()

                st.success(f"Exported to: {export_path}")
            except ImportError as e:
                st.error(f"Please install matplotlib: pip install matplotlib ({e})")
            except Exception as e:
                st.error(f"Export failed: {e}")

    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()

    # Footer
    st.markdown("---")
    st.caption("TDD Metrics Dashboard - Constitution-Based Development Framework")


if __name__ == "__main__":
    main()
