#!/usr/bin/env python3
"""Constitution Compliance Dashboard - Streamlit Edition

?�� 궁극??목적: Constitution 기반 개발 체계??준???�황 ?�각??

?�것?� "?�행???�산 ?�스??Executable Knowledge Base)"??Layer 7(?�각??계층)?�니??

?�심 ??��:
- P6 조항(Quality Gate) 준???�황 ?�시
- P4, P5 조항 ?�반 Hotspots ?�각??
- Constitution 기반 개발 체계 모니?�링
- YAML 계약???�행 결과 ?�인
- 지???�산??추세 분석

주의: ???�?�보?�는 검�??�구가 ?�닙?�다.
     검증�? DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)가 ?�행?�니??
     ?�?�보?�는 ?�순??결과�??�각?�할 뿐입?�다.

?�행:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import json
import sys

# ?�로?�트 루트�?Python path??추�?
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 기존 컴포?�트 import
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.deep_analyzer import DeepAnalyzer
from scripts.critical_file_detector import CriticalFileDetector

# ============================================================================
# ?�이지 ?�정
# ============================================================================

st.set_page_config(
    page_title="Constitution Compliance Dashboard", page_icon="?��", layout="wide", initial_sidebar_state="expanded"
)

# ============================================================================
# CRITICAL: Dashboard Role Clarification
# ============================================================================

st.warning("""
**?�️ ???�?�보?�는 ?�각?�만 ?�행?�니??*

검증�? ?�음 ?�이?�트가 ?�당?�니??
- **DeepAnalyzer** (P4: SOLID, P5: 보안, P7: Hallucination)
- **TeamStatsAggregator** (P6: ?�질 게이??

?�?�보?�는 Layer 7 (Visualization)?�로, ?�순??결과�??�시??뿐입?�다.

?�세???�용: [NORTH_STAR.md](https://github.com/positivef/dev-rules-starter-kit/blob/main/NORTH_STAR.md)
""")

# ============================================================================
# ?�퍼 ?�수??
# ============================================================================


def get_grade(score):
    """0-10 ?�수�?A-F ?�급?�로 변??""
    if score >= 9.0:
        return "A", "?��"
    if score >= 8.0:
        return "B", "?��"
    if score >= 7.0:
        return "C", "?��"
    if score >= 6.0:
        return "D", "?��"
    return "F", "?��"


def calculate_quality_gate(team_stats):
    """Quality Gate ?�과/?�패 ?�정"""
    conditions = {
        "?�균 ?�질 ??7.0": team_stats.avg_quality_score >= 7.0,
        "?�과????80%": (team_stats.passed_checks / team_stats.total_checks * 100) >= 80.0
        if team_stats.total_checks > 0
        else False,
        "보안 ?�슈 0�?: team_stats.total_security_issues == 0,
    }

    passed = all(conditions.values())
    return passed, conditions


def estimate_tech_debt(violations):
    """?�반?�항???�정 ?�간?�로 변??(1 violation = 15�?"""
    if violations == 0:
        return "0 minutes"

    minutes = violations * 15
    hours = minutes / 60
    days = hours / 8  # 1??= 8?�간

    if days >= 1:
        return f"~{days:.1f} days"
    elif hours >= 1:
        return f"~{hours:.1f} hours"
    else:
        return f"~{int(minutes)} minutes"


def get_severity_color(severity):
    """?�각?�별 ?�상"""
    colors = {"error": "?��", "warning": "?��", "info": "?��"}
    return colors.get(severity, "??)


# ============================================================================
# 캐시???�이??로더
# ============================================================================


@st.cache_resource
def get_components():
    """컴포?�트 초기??(캐시)"""
    cache_dir = project_root / "RUNS" / ".cache"
    evidence_dir = project_root / "RUNS" / "evidence"
    stats_dir = project_root / "RUNS" / "stats"

    aggregator = TeamStatsAggregator(cache_dir=cache_dir, evidence_dir=evidence_dir, output_dir=stats_dir)

    analyzer = DeepAnalyzer(mcp_enabled=False)
    detector = CriticalFileDetector()
    cache = VerificationCache(cache_dir=cache_dir)

    return aggregator, analyzer, detector, cache


@st.cache_data(ttl=30)  # 30�?캐시
def get_team_stats():
    """?� ?�계 가?�오�?""
    aggregator, _, _, _ = get_components()
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)
    return team_stats, file_stats


@st.cache_data(ttl=60)  # 60�?캐시
def get_trends_data():
    """추세 ?�이??로드"""
    trends_file = project_root / "RUNS" / "stats" / "trends.json"

    if not trends_file.exists():
        return None

    try:
        with open(trends_file) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        return None
    except Exception:
        return None


# ============================================================================
# 메인 ?�?�보??
# ============================================================================

st.title("?�️ Constitution 준???�황??)
st.markdown("**?�행???�산 ?�스??- Constitution 기반 개발 체계 모니?�링**")
st.caption("Layer 7 (?�각??계층) | 검증�? DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)가 ?�행")
st.caption(f"마�?�??�데?�트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# ?�계 로드
team_stats, file_stats = get_team_stats()

# ============================================================================
# 1. Quality Gate (가??중요!)
# ============================================================================

st.subheader("?�� Quality Gate")

passed, conditions = calculate_quality_gate(team_stats)

if passed:
    st.success("??**PASSED** - ?��??�니?? 모든 기�???충족?�어??")
else:
    st.error("??**FAILED** - 개선???�요?�요. ?�래 조건?�을 ?�인?�세??")

# 조건�??�시
col1, col2, col3 = st.columns(3)

for idx, (condition, result) in enumerate(conditions.items()):
    with [col1, col2, col3][idx]:
        icon = "?? if result else "??
        st.metric(
            label=condition, value=icon, delta="충족" if result else "미달", delta_color="normal" if result else "inverse"
        )

st.divider()

# ============================================================================
# 2. ?�심 메트�?(?�급 ?�스???�용)
# ============================================================================

st.subheader("?�� ?�심 지??)

col1, col2, col3, col4 = st.columns(4)

with col1:
    # ?�급 ?�스??
    grade, emoji = get_grade(team_stats.avg_quality_score)
    st.metric(label=f"{emoji} ?�체 ?�급", value=f"{grade}", delta=f"{team_stats.avg_quality_score:.1f}/10")

with col2:
    # ?�과??
    pass_rate = 0.0
    if team_stats.total_checks > 0:
        pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

    pass_emoji = "?��" if pass_rate >= 80 else "?��" if pass_rate >= 60 else "?��"
    st.metric(
        label=f"{pass_emoji} ?�과??,
        value=f"{pass_rate:.1f}%",
        delta=f"{team_stats.passed_checks}/{team_stats.total_checks}",
    )

with col3:
    # 기술 부�?
    debt_time = estimate_tech_debt(team_stats.total_violations)
    debt_emoji = "?��" if team_stats.total_violations < 10 else "?��" if team_stats.total_violations < 50 else "?��"
    st.metric(label=f"{debt_emoji} 기술 부�?, value=debt_time, delta=f"{team_stats.total_violations}�??�반")

with col4:
    # 보안 ?�슈
    security_emoji = "?��" if team_stats.total_security_issues == 0 else "?��"
    st.metric(
        label=f"{security_emoji} 보안 ?�슈",
        value=team_stats.total_security_issues,
        delta="?�전" if team_stats.total_security_issues == 0 else "?�험",
        delta_color="normal" if team_stats.total_security_issues == 0 else "inverse",
    )

st.divider()

# ============================================================================
# 3. Hotspots - 가??문제 많�? ?�일 TOP 5
# ============================================================================

st.subheader("?�� Hotspots - ???�일?�을 먼�? 고치?�요!")

# ?�일 ?�이?��? DataFrame?�로 변??
files_list = []
for path, stats in file_stats.items():
    try:
        relative_path = path.relative_to(project_root)
    except ValueError:
        relative_path = path

    files_list.append(
        {
            "Path": str(relative_path),
            "Quality": round(stats.avg_quality_score, 1),
            "Violations": stats.total_violations,
            "Security": stats.total_security_issues,
            "SOLID": stats.total_solid_violations,
            "Status": "?? if stats.passed_checks > stats.failed_checks else "??,
        }
    )

if files_list:
    files_df = pd.DataFrame(files_list)

    # TOP 5 문제 ?�일
    hotspots = files_df.nlargest(5, "Violations")

    if len(hotspots) > 0 and hotspots.iloc[0]["Violations"] > 0:
        for idx, row in hotspots.iterrows():
            if row["Violations"] == 0:
                continue

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                grade, emoji = get_grade(row["Quality"])
                st.write(f"{emoji} **{row['Path']}** (Grade: {grade})")

            with col2:
                st.write(f"?�️ {row['Violations']} issues")

            with col3:
                if row["Security"] > 0:
                    st.write(f"?���?{row['Security']} security")

            with col4:
                if st.button("?�정 가?�드", key=f"fix_{idx}"):
                    st.session_state["selected_file"] = row["Path"]
                    st.info(f"?�� {row['Path']}�??�택?�습?�다. ?�이?�바?�서 ?�세 분석???�인?�세??")
    else:
        st.success("?�� 문제가 ?�는 ?�일???�습?�다! 모든 코드가 ?��??�요!")
else:
    st.warning("?�️ 분석???�일???�습?�다. 먼�? 검증을 ?�행?�주?�요.")

st.divider()

# ============================================================================
# 4. ?�슈 분류 (?�각?�별)
# ============================================================================

st.subheader("?�� ?�슈 분석")

col1, col2, col3 = st.columns(3)

# ?�제 ?�각???�이??(Ruff 결과 기반 추정)
critical_count = team_stats.total_security_issues
major_count = team_stats.total_solid_violations
minor_count = team_stats.total_violations - critical_count - major_count
minor_count = max(0, minor_count)  # ?�수 방�?

with col1:
    st.metric("?�� Critical", critical_count, "보안 ?�슈 (즉시 ?�정 ?�요)")

with col2:
    st.metric("?�� Major", major_count, "SOLID ?�반 (리팩?�링 권장)")

with col3:
    st.metric("?�� Minor", minor_count, "?��????�매??(개선 권장)")

st.divider()

# ============================================================================
# 5. ?�질 추세 차트
# ============================================================================

st.subheader("?�� ?�질 추세")

trends_data = get_trends_data()

if trends_data and len(trends_data) > 0:
    # DataFrame 변??
    df = pd.DataFrame(trends_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.tail(30)  # 최근 30�?

    # Plotly 차트
    fig = go.Figure()

    # Quality Score ?�인
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["quality_score"],
            mode="lines+markers",
            name="Quality Score",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(31, 119, 180, 0.2)",
        )
    )

    # Pass Rate ?�인
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["pass_rate"],
            mode="lines+markers",
            name="Pass Rate (%)",
            line=dict(color="#2ca02c", width=3),
            marker=dict(size=8),
            yaxis="y2",
        )
    )

    # ?�이?�웃
    fig.update_layout(
        xaxis_title="Date",
        yaxis=dict(title="Quality Score", range=[0, 10]),
        yaxis2=dict(title="Pass Rate (%)", overlaying="y", side="right", range=[0, 100]),
        hovermode="x unified",
        height=400,
        showlegend=True,
        legend=dict(x=0, y=1.1, orientation="h"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ?�계 ?�약
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("?�균 ?�질", f"{df['quality_score'].mean():.1f}")
    with col2:
        st.metric("최고 ?�질", f"{df['quality_score'].max():.1f}")
    with col3:
        st.metric("최�? ?�질", f"{df['quality_score'].min():.1f}")
    with col4:
        trend = df["quality_score"].iloc[-1] - df["quality_score"].iloc[0]
        trend_icon = "?��" if trend > 0 else "?��" if trend < 0 else "?�️"
        st.metric("추세", f"{trend_icon} {abs(trend):.1f}")

else:
    st.info("?�� 추세 ?�이?��? ?�직 ?�습?�다. 검증을 �?�??�행?�면 차트가 그려집니??")

st.divider()

# ============================================================================
# 6. ?�체 ?�일 목록
# ============================================================================

st.subheader("?�� ?�체 ?�일 목록")

if files_list:
    # ?�터�??�션
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        sort_by = st.selectbox("?�렬 기�?", options=["Violations", "Quality", "Path"], index=0)

    with col2:
        status_filter = st.selectbox("?�태 ?�터", options=["?�체", "?�과�?, "?�패�?], index=0)

    with col3:
        min_quality = st.slider("최소 ?�질", 0.0, 10.0, 0.0, 0.5)

    # ?�터 ?�용
    filtered_df = files_df.copy()
    filtered_df = filtered_df[filtered_df["Quality"] >= min_quality]

    if status_filter == "?�과�?:
        filtered_df = filtered_df[filtered_df["Status"] == "??]
    elif status_filter == "?�패�?:
        filtered_df = filtered_df[filtered_df["Status"] == "??]

    # ?�렬
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_by == "Path"))

    # ?�상 ?�수
    def color_quality(val):
        if val >= 8.0:
            return "background-color: #90EE90"  # ?�한 초록
        elif val >= 6.0:
            return "background-color: #FFE4B5"  # ?�한 ?�랑
        else:
            return "background-color: #FFB6C1"  # ?�한 빨강

    # ?��????�용
    styled_df = filtered_df.style.applymap(color_quality, subset=["Quality"])

    # ?�이�??�시
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

    st.caption(f"?�� {len(filtered_df)}�??�일 ?�시 �?(?�체 {len(files_df)}�?")

st.divider()

# ============================================================================
# 7. ?�이?�바 - ?�일 ?�세 분석
# ============================================================================

with st.sidebar:
    st.header("?�� ?�일 ?�세 분석")

    if files_list:
        # ?�일 ?�택
        selected_file = st.selectbox("분석???�일 ?�택", options=[f["Path"] for f in files_list], index=0)

        st.divider()

        if st.button("?�� ?�택???�일 분석?�기", use_container_width=True):
            full_path = project_root / selected_file

            if full_path.exists():
                with st.spinner("분석 �?.."):
                    _, analyzer, detector, _ = get_components()

                    # 분석 ?�행
                    result = analyzer.analyze(full_path)
                    classification = detector.classify(full_path)

                    # 결과 ?�시
                    st.success("??분석 ?�료!")

                    # ?�급
                    grade, emoji = get_grade(result.overall_score)
                    st.metric(f"{emoji} Grade", f"{grade}", f"{result.overall_score:.1f}/10")

                    # ?�선?�위
                    priority = (
                        "?�� HIGH"
                        if classification.criticality_score >= 0.7
                        else "?�� MEDIUM"
                        if classification.criticality_score >= 0.5
                        else "?�� LOW"
                    )
                    st.metric("Priority", priority)

                    st.divider()

                    # SOLID ?�반
                    if result.solid_violations:
                        with st.expander(f"?�️ SOLID ?�반 ({len(result.solid_violations)}�?", expanded=True):
                            for v in result.solid_violations[:5]:
                                st.text(f"Line {v.line}: {v.message}")

                    # 보안 ?�슈
                    if result.security_issues:
                        with st.expander(f"?���?보안 ?�슈 ({len(result.security_issues)}�?", expanded=True):
                            for s in result.security_issues[:5]:
                                st.text(f"Line {s.line}: {s.message}")

                    # Hallucination ?�험
                    if result.hallucination_risks:
                        with st.expander(f"?�� Hallucination ?�험 ({len(result.hallucination_risks)}�?"):
                            for h in result.hallucination_risks[:5]:
                                st.text(f"Line {h.line}: {h.message}")

                    # 개선 ?�안
                    st.divider()
                    st.subheader("?�� 개선 ?�안")

                    if result.overall_score >= 8.0:
                        st.success("?�� ?��???코드?�니?? ?�재 ?�태�??��??�세??")
                    elif result.overall_score >= 6.0:
                        st.warning("?�️ 리팩?�링??권장?�니?? SOLID ?�반??먼�? ?�결?�세??")
                    else:
                        st.error("?�� 즉시 개선???�요?�니?? 보안 ?�슈?� SOLID ?�반???�선 ?�결?�세??")

            else:
                st.error("???�일??찾을 ???�습?�다!")

    st.divider()

    # ?�동 갱신
    st.header("?�️ ?�정")

    auto_refresh = st.checkbox("?�동 갱신 (10�?")

    if st.button("?�� 지�??�로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

# ?�동 갱신 로직
if auto_refresh:
    import time

    time.sleep(10)
    st.rerun()

# ============================================================================
# ?�터
# ============================================================================

st.divider()

st.markdown("""
**Dev Rules Dashboard v0.6.0** (Improved)

?�� **목적**: 개발?��? ???��? 코드�??�성?�도�??�는??
- ??즉각???�드�?
- ??명확??방향 ?�시
- ??지?�적 개선 ?�려
- ??AI 코드 검�?
""")

st.caption("Built with ?�️ using Streamlit | 질문?�나 ?�드백�? ?�제?��? ?�영?�니??")
