#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Management Real-Time Dashboard
Real-time session monitoring and analytics dashboard

Features:
- Real-time session status monitoring
- Task execution visualization
- Success/failure statistics charts
- Productivity pattern analysis
- Real-time error log display

Usage:
    streamlit run scripts/session_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, Any, Optional
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import SessionManager and Analyzer
try:
    from session_manager import SessionManager, StateScope
    from session_analyzer import SessionAnalyzer

    SESSION_ENABLED = True
except ImportError:
    SESSION_ENABLED = False
    st.error("SessionManager not found. Please check installation.")

# 페이지 설정
st.set_page_config(page_title="Session Monitor", page_icon="[M]", layout="wide", initial_sidebar_state="expanded")

# CSS Style
st.markdown(
    """
<style>
.success-metric {
    color: #28a745;
    font-size: 2em;
    font-weight: bold;
}
.failure-metric {
    color: #dc3545;
    font-size: 2em;
    font-weight: bold;
}
.neutral-metric {
    color: #6c757d;
    font-size: 2em;
    font-weight: bold;
}
.task-running {
    background-color: #fff3cd;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.task-success {
    background-color: #d4edda;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.task-failed {
    background-color: #f8d7da;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
</style>
""",
    unsafe_allow_html=True,
)


def load_session_data() -> Optional[Dict[str, Any]]:
    """현재 세션 데이터 로드"""
    if not SESSION_ENABLED:
        return None

    try:
        session = SessionManager.get_instance()

        # 세션 정보
        session_info = session.get_session_info()

        # 현재 작업
        current_task = session.get("current_task", StateScope.SESSION)

        # 실행 통계
        stats = session.get("execution_stats", StateScope.USER, {})

        # 완료된 작업들
        completed_tasks = session.get("completed_tasks", StateScope.SESSION, [])

        # 실패한 작업들
        failed_tasks = session.get("failed_tasks", StateScope.SESSION, {})

        # 명령 로그
        command_log = session.get("command_log", StateScope.TEMP, [])

        return {
            "session_info": session_info,
            "current_task": current_task,
            "stats": stats,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "command_log": command_log,
        }
    except Exception as e:
        st.error(f"Error loading session data: {e}")
        return None


def display_current_status(data: Dict[str, Any]):
    """현재 상태 표시"""
    st.header("[현재 세션 상태]")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Session ID", data["session_info"].get("session_id", "N/A")[:12] + "...")

    with col2:
        started = data["session_info"].get("started_at", "")
        if started:
            try:
                start_time = datetime.fromisoformat(started.replace("Z", "+00:00"))
                duration = datetime.now() - start_time.replace(tzinfo=None)
                st.metric("Session Duration", f"{duration.seconds // 60} min")
            except (ValueError, TypeError, AttributeError):
                st.metric("Session Duration", "N/A")
        else:
            st.metric("Session Duration", "N/A")

    with col3:
        last_checkpoint = data["session_info"].get("last_checkpoint", "")
        if last_checkpoint:
            try:
                checkpoint_time = datetime.fromisoformat(last_checkpoint.replace("Z", "+00:00"))
                time_since = datetime.now() - checkpoint_time.replace(tzinfo=None)
                st.metric("Last Checkpoint", f"{time_since.seconds // 60} min ago")
            except (ValueError, TypeError, AttributeError):
                st.metric("Last Checkpoint", "N/A")
        else:
            st.metric("Last Checkpoint", "N/A")

    with col4:
        data_sizes = data["session_info"].get("data_sizes", {})
        total_items = sum(data_sizes.values())
        st.metric("Data Items", total_items)

    # 현재 작업 표시
    if data.get("current_task"):
        task = data["current_task"]
        status = task.get("status", "unknown")

        status_colors = {"running": "task-running", "success": "task-success", "failed": "task-failed"}

        st.markdown("### 현재 작업")
        st.markdown(f'<div class="{status_colors.get(status, "")}">', unsafe_allow_html=True)
        st.write(f"**Task ID**: {task.get('task_id', 'N/A')}")
        st.write(f"**Title**: {task.get('title', 'N/A')}")
        st.write(f"**Status**: {status}")
        if task.get("execution_time"):
            st.write(f"**Execution Time**: {task['execution_time']:.2f}s")
        if task.get("error"):
            st.error(f"Error: {task['error']}")
        st.markdown("</div>", unsafe_allow_html=True)


def display_statistics(data: Dict[str, Any]):
    """통계 표시"""
    st.header("[실행 통계]")

    stats = data.get("stats", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = stats.get("total_executions", 0)
        st.markdown(f'<div class="neutral-metric">{total}</div>', unsafe_allow_html=True)
        st.write("총 실행")

    with col2:
        successful = stats.get("successful", 0)
        st.markdown(f'<div class="success-metric">{successful}</div>', unsafe_allow_html=True)
        st.write("성공")

    with col3:
        failed = stats.get("failed", 0)
        st.markdown(f'<div class="failure-metric">{failed}</div>', unsafe_allow_html=True)
        st.write("실패")

    with col4:
        success_rate = (successful / total * 100) if total > 0 else 0
        color_class = "success-metric" if success_rate >= 80 else "failure-metric"
        st.markdown(f'<div class="{color_class}">{success_rate:.1f}%</div>', unsafe_allow_html=True)
        st.write("성공률")

    # 차트 표시
    if total > 0:
        col1, col2 = st.columns(2)

        with col1:
            # 파이 차트
            fig_pie = go.Figure(
                data=[
                    go.Pie(
                        labels=["Success", "Failed"],
                        values=[successful, failed],
                        hole=0.3,
                        marker=dict(colors=["#28a745", "#dc3545"]),
                    )
                ]
            )
            fig_pie.update_layout(title="Success/Failure Ratio", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # 평균 실행 시간
            avg_time = stats.get("avg_time", 0)
            total_time = stats.get("total_time", 0)

            fig_bar = go.Figure(
                data=[
                    go.Bar(x=["Average Time", "Total Time"], y=[avg_time, total_time], marker_color=["#007bff", "#6c757d"])
                ]
            )
            fig_bar.update_layout(title="Execution Time (seconds)", height=300)
            st.plotly_chart(fig_bar, use_container_width=True)


def display_task_history(data: Dict[str, Any]):
    """작업 이력 표시"""
    st.header("[작업 이력]")

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["완료된 작업", "실패한 작업", "명령 로그"])

    with tab1:
        completed = data.get("completed_tasks", [])
        if completed:
            st.success(f"{len(completed)}개 작업 완료")

            # 최근 10개만 표시
            for task_id in completed[-10:]:
                st.write(f"✅ {task_id}")
        else:
            st.info("완료된 작업이 없습니다")

    with tab2:
        failed = data.get("failed_tasks", {})
        if failed:
            st.error(f"{len(failed)}개 작업 실패")

            for task_id, failure in failed.items():
                st.write(f"❌ **{task_id}**")
                st.write(f"   Error: {failure.get('error', 'Unknown')[:100]}")
                st.write(f"   Time: {failure.get('timestamp', 'Unknown')}")
                st.divider()
        else:
            st.info("실패한 작업이 없습니다")

    with tab3:
        commands = data.get("command_log", [])
        if commands:
            # DataFrame으로 변환
            df_commands = pd.DataFrame(commands)

            # 최근 20개만 표시
            if len(df_commands) > 20:
                df_commands = df_commands.tail(20)

            # 시간 포맷팅
            if "timestamp" in df_commands.columns:
                df_commands["time"] = pd.to_datetime(df_commands["timestamp"]).dt.strftime("%H:%M:%S")

            # 테이블 표시
            st.dataframe(df_commands[["time", "command", "exit_code", "success"]], use_container_width=True)
        else:
            st.info("명령 로그가 없습니다")


def display_productivity_analysis():
    """생산성 분석 표시"""
    st.header("[생산성 분석]")

    # SessionAnalyzer 사용
    try:
        analyzer = SessionAnalyzer()
        results = analyzer.analyze_all(days=7)

        if "error" in results:
            st.warning(results["error"])
            return

        # 생산성 패턴
        productivity = results.get("productivity", {})

        col1, col2 = st.columns(2)

        with col1:
            # 시간대별 활동
            hourly = productivity.get("hourly_distribution", {})
            if hourly:
                hours = list(hourly.keys())
                counts = list(hourly.values())

                fig = go.Figure(data=[go.Bar(x=hours, y=counts, marker_color="#007bff")])
                fig.update_layout(title="시간대별 활동", xaxis_title="Hour", yaxis_title="Sessions", height=300)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 요일별 활동
            daily = productivity.get("daily_distribution", {})
            if daily:
                days = list(daily.keys())
                counts = list(daily.values())

                fig = go.Figure(data=[go.Bar(x=days, y=counts, marker_color="#28a745")])
                fig.update_layout(title="요일별 활동", xaxis_title="Day", yaxis_title="Sessions", height=300)
                st.plotly_chart(fig, use_container_width=True)

        # 인사이트 표시
        insights = results.get("insights", {})

        if insights.get("recommendations"):
            st.subheader("💡 개선 제안")
            for rec in insights["recommendations"]:
                st.info(rec)

        if insights.get("warnings"):
            st.subheader("⚠️ 주의사항")
            for warning in insights["warnings"]:
                st.warning(warning)

        if insights.get("positive_patterns"):
            st.subheader("✅ 긍정적 패턴")
            for pattern in insights["positive_patterns"]:
                st.success(pattern)

    except Exception as e:
        st.error(f"Error analyzing productivity: {e}")


def main():
    """메인 대시보드"""

    # 헤더
    st.title("[Session Management Dashboard]")
    st.markdown("실시간 세션 모니터링 및 분석")

    # 사이드바
    with st.sidebar:
        st.header("Dashboard Settings")

        # 자동 새로고침
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        refresh_interval = st.slider("Refresh Interval (seconds)", min_value=5, max_value=60, value=10)

        # 분석 기간
        st.selectbox("Analysis Period", options=[1, 7, 30], index=1, format_func=lambda x: f"Last {x} days")

        # 수동 새로고침 버튼
        if st.button("Refresh Now"):
            st.rerun()

        st.divider()

        # 세션 관리 액션
        st.header("Session Actions")

        if SESSION_ENABLED:
            session = SessionManager.get_instance()

            if st.button("Create Checkpoint"):
                session.checkpoint()
                st.success("Checkpoint created!")
                time.sleep(1)
                st.rerun()

            if st.button("Clear Temp Data"):
                # TEMP 스코프 데이터 초기화
                session.current_state.scope_data[StateScope.TEMP.value] = {}
                st.success("Temp data cleared!")
                st.rerun()

        # 정보
        st.divider()
        st.info(
            "This dashboard monitors SessionManager data in real-time. "
            "It shows current tasks, execution statistics, and productivity patterns."
        )

    # 데이터 로드
    if not SESSION_ENABLED:
        st.error("SessionManager is not available. Please check the installation.")
        return

    data = load_session_data()

    if data is None:
        st.warning("No session data available. Start a session to see metrics.")
        return

    # 메인 컨텐츠
    # 현재 상태
    display_current_status(data)

    st.divider()

    # 통계
    display_statistics(data)

    st.divider()

    # 작업 이력
    display_task_history(data)

    st.divider()

    # 생산성 분석
    display_productivity_analysis()

    # 자동 새로고침
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
