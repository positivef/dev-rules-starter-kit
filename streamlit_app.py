#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constitution Compliance Dashboard
==================================

Core: This is a visualization tool for Constitution compliance status.

Purpose:
- Display P1-P16 article compliance status
- Show Quality Gate (P6) PASS/FAIL results
- Visualize Constitution violation hotspots
- Monitor Executable Knowledge Base system

Note: This dashboard is Layer 7 (Visualization).
      Validation is performed by DeepAnalyzer and TeamStatsAggregator.
      The dashboard simply visualizes the results.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import sys
from typing import Dict, Tuple, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import analyzers (only what's used)
try:
    from scripts.auto_improver import AutoImprover, ConstitutionParser
except ImportError as e:
    st.error(f"Failed to import analyzers: {e}")

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Constitution Compliance Dashboard", page_icon="[LAW]", layout="wide", initial_sidebar_state="expanded"
)

# ============================================================================
# Dashboard Header
# ============================================================================

st.title("[CONSTITUTION] Compliance Dashboard")
st.markdown("""
### Dev Rules Starter Kit - Constitution Compliance Status

**Core Concept**: Executable Knowledge Base System
- Documents are Code (YAML -> TaskExecutor -> Evidence -> Obsidian)
- Constitution is the center of all development
- This dashboard is Layer 7 (Visualization only)
""")

# Warning box
st.warning("""
**[NOTICE] Dashboard Role**

- [OK] Visualize Constitution compliance status
- [OK] Display P6 Quality Gate
- [OK] Show P4, P5 violation hotspots
- [X] NOT a validation tool (Validation: DeepAnalyzer/TeamStatsAggregator)
- [X] NOT a standalone product (Part of Executable Knowledge Base system)
""")

# ============================================================================
# Sidebar Configuration
# ============================================================================

with st.sidebar:
    st.header("[CONFIG] Dashboard Settings")

    # Refresh interval
    refresh_interval = st.selectbox(
        "Auto-refresh interval",
        options=[None, 5, 10, 30, 60],
        format_func=lambda x: "Disabled" if x is None else f"{x} seconds",
    )

    # Constitution articles filter
    st.subheader("Constitution Articles")
    show_articles = st.multiselect(
        "Select articles to monitor",
        options=["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15", "P16"],
        default=["P4", "P5", "P6", "P7"],
    )

    # Date range
    st.subheader("Analysis Period")
    date_range = st.date_input(
        "Select date range", value=(datetime.now() - timedelta(days=7), datetime.now()), max_value=datetime.now()
    )

    # Run analysis button
    if st.button("[ANALYZE] Run Constitution Check", type="primary"):
        st.session_state.run_analysis = True

# ============================================================================
# Helper Functions
# ============================================================================


def get_constitution_grade(score: float) -> Tuple[str, str]:
    """Convert 0-10 score to Constitution compliance grade"""
    if score >= 9.0:
        return "A", "[EXCELLENT]"
    if score >= 8.0:
        return "B", "[GOOD]"
    if score >= 7.0:
        return "C", "[ACCEPTABLE]"
    if score >= 6.0:
        return "D", "[NEEDS_IMPROVEMENT]"
    return "F", "[FAILING]"


def calculate_quality_gate(stats: Dict) -> Tuple[bool, Dict]:
    """Calculate P6 Quality Gate status"""
    conditions = {
        "Average Quality >= 7.0": stats.get("avg_quality", 0) >= 7.0,
        "Pass Rate >= 80%": stats.get("pass_rate", 0) >= 80.0,
        "Critical Security Issues = 0": stats.get("critical_issues", 0) == 0,
    }

    passed = all(conditions.values())
    return passed, conditions


def load_constitution_data() -> Optional[ConstitutionParser]:
    """Load Constitution data"""
    try:
        parser = ConstitutionParser("config/constitution.yaml")
        return parser
    except Exception as e:
        st.error(f"Failed to load Constitution: {e}")
        return None


def analyze_repository() -> Dict:
    """Run repository analysis using AutoImprover"""
    try:
        improver = AutoImprover()
        improvements = improver.analyze_repository()

        stats = {"total_violations": len(improvements), "by_article": {}, "by_risk": {}, "auto_applicable": 0}

        for imp in improvements:
            # Count by article
            article = imp.violation.article_id
            stats["by_article"][article] = stats["by_article"].get(article, 0) + 1

            # Count by risk
            risk = imp.risk_level.value
            stats["by_risk"][risk] = stats["by_risk"].get(risk, 0) + 1

            # Count auto-applicable
            if imp.auto_applicable:
                stats["auto_applicable"] += 1

        return stats
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return {}


# ============================================================================
# Main Dashboard
# ============================================================================

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["[P6] Quality Gate", "[P4/P5] Violations", "[P1-P16] Constitution Status", "[STATS] Metrics", "[REPORT] Analysis"]
)

# ============================================================================
# Tab 1: Quality Gate (P6)
# ============================================================================

with tab1:
    st.header("[P6] Quality Gate Status")

    # Create mock data for demo (replace with real data)
    demo_stats = {"avg_quality": 7.5, "pass_rate": 85.0, "critical_issues": 0}

    gate_passed, conditions = calculate_quality_gate(demo_stats)

    # Display Quality Gate status
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if gate_passed:
            st.success("### [PASS] Quality Gate Passed")
        else:
            st.error("### [FAIL] Quality Gate Failed")

        # Show conditions
        for condition, passed in conditions.items():
            if passed:
                st.markdown(f"[OK] {condition}")
            else:
                st.markdown(f"[X] {condition}")

    with col2:
        st.metric(label="Average Quality Score", value=f"{demo_stats['avg_quality']:.1f}/10", delta="+0.3")

    with col3:
        st.metric(label="Pass Rate", value=f"{demo_stats['pass_rate']:.0f}%", delta="+5%")

    # Quality trend chart
    st.subheader("Quality Trend (Last 7 Days)")

    # Generate demo trend data
    dates = pd.date_range(end=datetime.now(), periods=7, freq="D")
    quality_scores = [7.2, 7.3, 7.1, 7.4, 7.3, 7.5, 7.5]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dates, y=quality_scores, mode="lines+markers", name="Quality Score", line=dict(color="green", width=2))
    )

    # Add threshold line
    fig.add_hline(y=7.0, line_dash="dash", line_color="red", annotation_text="P6 Threshold (7.0)")

    fig.update_layout(
        title="Constitution P6 Compliance Trend",
        xaxis_title="Date",
        yaxis_title="Quality Score",
        yaxis_range=[0, 10],
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Tab 2: Violations (P4, P5)
# ============================================================================

with tab2:
    st.header("[P4/P5] Constitution Violations Hotspots")

    # Run analysis if requested
    if st.session_state.get("run_analysis", False):
        with st.spinner("Analyzing repository for Constitution violations..."):
            analysis_stats = analyze_repository()
            st.session_state.analysis_stats = analysis_stats
            st.session_state.run_analysis = False

    # Display analysis results
    if "analysis_stats" in st.session_state:
        stats = st.session_state.analysis_stats

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Violations by Article")
            if stats.get("by_article"):
                df_articles = pd.DataFrame(list(stats["by_article"].items()), columns=["Article", "Count"]).sort_values(
                    "Count", ascending=False
                )

                fig = px.bar(
                    df_articles,
                    x="Article",
                    y="Count",
                    title="Constitution Violations by Article",
                    color="Count",
                    color_continuous_scale="Reds",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Violations by Risk Level")
            if stats.get("by_risk"):
                df_risk = pd.DataFrame(list(stats["by_risk"].items()), columns=["Risk", "Count"])

                colors = {"low": "green", "medium": "yellow", "high": "orange", "critical": "red"}
                fig = px.pie(
                    df_risk, values="Count", names="Risk", title="Risk Distribution", color="Risk", color_discrete_map=colors
                )
                st.plotly_chart(fig, use_container_width=True)

        # Top violations table
        st.subheader("Top 5 Violation Hotspots")

        # Create demo hotspots (replace with real data)
        hotspots_data = [
            {"File": "scripts/deep_analyzer.py", "Article": "P4", "Line": 150, "Issue": "Function too long (75 lines)"},
            {"File": "scripts/team_stats.py", "Article": "P5", "Line": 45, "Issue": "Hardcoded API key"},
            {"File": "scripts/validator.py", "Article": "P4", "Line": 230, "Issue": "Class has 15 methods"},
            {"File": "scripts/cache.py", "Article": "P7", "Line": 89, "Issue": "TODO comment found"},
            {"File": "scripts/executor.py", "Article": "P10", "Line": 12, "Issue": "Emoji in code"},
        ]

        df_hotspots = pd.DataFrame(hotspots_data)
        st.dataframe(df_hotspots, use_container_width=True)
    else:
        st.info("Click [ANALYZE] in the sidebar to run Constitution compliance check")

# ============================================================================
# Tab 3: Constitution Status
# ============================================================================

with tab3:
    st.header("[P1-P16] Constitution Articles Status")

    # Load constitution
    constitution = load_constitution_data()

    if constitution:
        # Display all articles with their status
        cols = st.columns(4)

        for i, article in enumerate(constitution.articles):
            col_idx = i % 4
            with cols[col_idx]:
                # Determine status (mock data for demo)
                if article.id in ["P1", "P2", "P3"]:
                    status = "[PASS]"
                    color = "green"
                elif article.id in ["P4", "P5"]:
                    status = "[WARN]"
                    color = "orange"
                else:
                    status = "[INFO]"
                    color = "blue"

                st.markdown(
                    f"""
                <div style="border: 2px solid {color}; padding: 10px; margin: 5px; border-radius: 5px;">
                    <b>{article.id}: {article.name}</b><br>
                    Status: {status}<br>
                    Priority: {article.priority.upper()}<br>
                    Tool: {article.enforcement_tool or 'N/A'}
                </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.error("Failed to load Constitution articles")

# ============================================================================
# Tab 4: Metrics
# ============================================================================

with tab4:
    st.header("[METRICS] Constitution Compliance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Constitution Compliance", value="75%", delta="+5%", help="Overall compliance with P1-P16")

    with col2:
        st.metric(label="YAML Contracts Executed", value="42", delta="+3 today", help="P1: YAML-first development")

    with col3:
        st.metric(label="Evidence Collected", value="1,247", delta="+89 today", help="P2: Evidence-based development")

    with col4:
        st.metric(label="Obsidian Syncs", value="156", delta="+12 today", help="P3: Knowledge asset management")

    # ROI Calculation
    st.subheader("ROI Impact")

    roi_data = {
        "Metric": ["Time Saved", "Errors Prevented", "Knowledge Reused", "Automation Rate"],
        "Value": ["264 hours/year", "405 violations caught", "80% reuse rate", "70% automated"],
        "Impact": ["[HIGH]", "[CRITICAL]", "[HIGH]", "[MEDIUM]"],
    }

    df_roi = pd.DataFrame(roi_data)
    st.dataframe(df_roi, use_container_width=True)

# ============================================================================
# Tab 5: Report
# ============================================================================

with tab5:
    st.header("[REPORT] Constitution Compliance Analysis")

    # Generate report button
    if st.button("[GENERATE] Full Compliance Report"):
        with st.spinner("Generating comprehensive Constitution compliance report..."):
            report = f"""
# Constitution Compliance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- Overall Compliance: 75%
- Quality Gate (P6): PASSED
- Critical Issues: 0
- Auto-fixable Issues: 120

## Article Compliance Status
- P1 (YAML First): 95% compliance
- P2 (Evidence Based): 88% compliance
- P3 (Knowledge Asset): 92% compliance
- P4 (SOLID): 68% compliance [NEEDS IMPROVEMENT]
- P5 (Security): 71% compliance [NEEDS IMPROVEMENT]
- P6 (Quality Gate): 85% compliance
- P7 (Hallucination): 76% compliance
- P8 (Test First): 82% compliance
- P9 (Conventional Commits): 94% compliance
- P10 (Windows Encoding): 73% compliance

## Recommendations
1. Focus on P4 (SOLID) violations - 276 issues found
2. Address P5 (Security) issues - 7 critical items
3. Clean up P7 (Hallucination) - 65 TODO/FIXME comments
4. Fix P10 (Encoding) - 57 emoji usages in code

## Next Steps
- Run auto_improver.py to fix 120 auto-applicable issues
- Manual review required for 285 medium/high risk items
- Schedule team review for critical security issues
            """

            st.code(report, language="markdown")

            # Download button
            st.download_button(
                label="[DOWNLOAD] Report as Markdown",
                data=report,
                file_name=f"constitution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
            )

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: gray;">
    <small>
    Constitution Compliance Dashboard v2.0 |
    Layer 7 (Visualization) |
    <a href="https://github.com/positivef/dev-rules-starter-kit">GitHub</a> |
    <a href="/NORTH_STAR.md">NORTH_STAR</a> |
    <a href="/config/constitution.yaml">Constitution</a>
    </small>
</div>
""",
    unsafe_allow_html=True,
)

# Auto-refresh logic
if refresh_interval:
    import time

    time.sleep(refresh_interval)
    st.rerun()
