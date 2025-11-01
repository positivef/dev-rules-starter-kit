#!/usr/bin/env python3
"""Constitution Compliance Dashboard - Streamlit Edition

?¯ ê¶ê·¹??ëª©ì : Constitution ê¸°ë°˜ ê°œë°œ ì²´ê³„??ì¤€???„í™© ?œê°??

?´ê²ƒ?€ "?¤í–‰???ì‚° ?œìŠ¤??Executable Knowledge Base)"??Layer 7(?œê°??ê³„ì¸µ)?…ë‹ˆ??

?µì‹¬ ??• :
- P6 ì¡°í•­(Quality Gate) ì¤€???„í™© ?œì‹œ
- P4, P5 ì¡°í•­ ?„ë°˜ Hotspots ?œê°??
- Constitution ê¸°ë°˜ ê°œë°œ ì²´ê³„ ëª¨ë‹ˆ?°ë§
- YAML ê³„ì•½???¤í–‰ ê²°ê³¼ ?•ì¸
- ì§€???ì‚°??ì¶”ì„¸ ë¶„ì„

ì£¼ì˜: ???€?œë³´?œëŠ” ê²€ì¦??„êµ¬ê°€ ?„ë‹™?ˆë‹¤.
     ê²€ì¦ì? DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)ê°€ ?˜í–‰?©ë‹ˆ??
     ?€?œë³´?œëŠ” ?¨ìˆœ??ê²°ê³¼ë¥??œê°?”í•  ë¿ì…?ˆë‹¤.

?¤í–‰:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import json
import sys

# ?„ë¡œ?íŠ¸ ë£¨íŠ¸ë¥?Python path??ì¶”ê?
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ê¸°ì¡´ ì»´í¬?ŒíŠ¸ import
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.deep_analyzer import DeepAnalyzer
from scripts.critical_file_detector import CriticalFileDetector

# ============================================================================
# ?˜ì´ì§€ ?¤ì •
# ============================================================================

st.set_page_config(
    page_title="Constitution Compliance Dashboard", page_icon="?“Š", layout="wide", initial_sidebar_state="expanded"
)

# ============================================================================
# CRITICAL: Dashboard Role Clarification
# ============================================================================

st.warning("""
**? ï¸ ???€?œë³´?œëŠ” ?œê°?”ë§Œ ?˜í–‰?©ë‹ˆ??*

ê²€ì¦ì? ?¤ìŒ ?ì´?„íŠ¸ê°€ ?´ë‹¹?©ë‹ˆ??
- **DeepAnalyzer** (P4: SOLID, P5: ë³´ì•ˆ, P7: Hallucination)
- **TeamStatsAggregator** (P6: ?ˆì§ˆ ê²Œì´??

?€?œë³´?œëŠ” Layer 7 (Visualization)?¼ë¡œ, ?¨ìˆœ??ê²°ê³¼ë¥??œì‹œ??ë¿ì…?ˆë‹¤.

?ì„¸???´ìš©: [NORTH_STAR.md](https://github.com/positivef/dev-rules-starter-kit/blob/main/NORTH_STAR.md)
""")

# ============================================================================
# ?¬í¼ ?¨ìˆ˜??
# ============================================================================


def get_grade(score):
    """0-10 ?ìˆ˜ë¥?A-F ?±ê¸‰?¼ë¡œ ë³€??""
    if score >= 9.0:
        return "A", "?Ÿ¢"
    if score >= 8.0:
        return "B", "?Ÿ¢"
    if score >= 7.0:
        return "C", "?Ÿ¡"
    if score >= 6.0:
        return "D", "?Ÿ¡"
    return "F", "?”´"


def calculate_quality_gate(team_stats):
    """Quality Gate ?µê³¼/?¤íŒ¨ ?ì •"""
    conditions = {
        "?‰ê·  ?ˆì§ˆ ??7.0": team_stats.avg_quality_score >= 7.0,
        "?µê³¼????80%": (team_stats.passed_checks / team_stats.total_checks * 100) >= 80.0
        if team_stats.total_checks > 0
        else False,
        "ë³´ì•ˆ ?´ìŠˆ 0ê°?: team_stats.total_security_issues == 0,
    }

    passed = all(conditions.values())
    return passed, conditions


def estimate_tech_debt(violations):
    """?„ë°˜?¬í•­???˜ì • ?œê°„?¼ë¡œ ë³€??(1 violation = 15ë¶?"""
    if violations == 0:
        return "0 minutes"

    minutes = violations * 15
    hours = minutes / 60
    days = hours / 8  # 1??= 8?œê°„

    if days >= 1:
        return f"~{days:.1f} days"
    elif hours >= 1:
        return f"~{hours:.1f} hours"
    else:
        return f"~{int(minutes)} minutes"


def get_severity_color(severity):
    """?¬ê°?„ë³„ ?‰ìƒ"""
    colors = {"error": "?”´", "warning": "?Ÿ¡", "info": "?Ÿ¢"}
    return colors.get(severity, "??)


# ============================================================================
# ìºì‹œ???°ì´??ë¡œë”
# ============================================================================


@st.cache_resource
def get_components():
    """ì»´í¬?ŒíŠ¸ ì´ˆê¸°??(ìºì‹œ)"""
    cache_dir = project_root / "RUNS" / ".cache"
    evidence_dir = project_root / "RUNS" / "evidence"
    stats_dir = project_root / "RUNS" / "stats"

    aggregator = TeamStatsAggregator(cache_dir=cache_dir, evidence_dir=evidence_dir, output_dir=stats_dir)

    analyzer = DeepAnalyzer(mcp_enabled=False)
    detector = CriticalFileDetector()
    cache = VerificationCache(cache_dir=cache_dir)

    return aggregator, analyzer, detector, cache


@st.cache_data(ttl=30)  # 30ì´?ìºì‹œ
def get_team_stats():
    """?€ ?µê³„ ê°€?¸ì˜¤ê¸?""
    aggregator, _, _, _ = get_components()
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)
    return team_stats, file_stats


@st.cache_data(ttl=60)  # 60ì´?ìºì‹œ
def get_trends_data():
    """ì¶”ì„¸ ?°ì´??ë¡œë“œ"""
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
# ë©”ì¸ ?€?œë³´??
# ============================================================================

st.title("?–ï¸ Constitution ì¤€???„í™©??)
st.markdown("**?¤í–‰???ì‚° ?œìŠ¤??- Constitution ê¸°ë°˜ ê°œë°œ ì²´ê³„ ëª¨ë‹ˆ?°ë§**")
st.caption("Layer 7 (?œê°??ê³„ì¸µ) | ê²€ì¦ì? DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)ê°€ ?˜í–‰")
st.caption(f"ë§ˆì?ë§??…ë°?´íŠ¸: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# ?µê³„ ë¡œë“œ
team_stats, file_stats = get_team_stats()

# ============================================================================
# 1. Quality Gate (ê°€??ì¤‘ìš”!)
# ============================================================================

st.subheader("?¯ Quality Gate")

passed, conditions = calculate_quality_gate(team_stats)

if passed:
    st.success("??**PASSED** - ?Œë??©ë‹ˆ?? ëª¨ë“  ê¸°ì???ì¶©ì¡±?ˆì–´??")
else:
    st.error("??**FAILED** - ê°œì„ ???„ìš”?´ìš”. ?„ë˜ ì¡°ê±´?¤ì„ ?•ì¸?˜ì„¸??")

# ì¡°ê±´ë³??œì‹œ
col1, col2, col3 = st.columns(3)

for idx, (condition, result) in enumerate(conditions.items()):
    with [col1, col2, col3][idx]:
        icon = "?? if result else "??
        st.metric(
            label=condition, value=icon, delta="ì¶©ì¡±" if result else "ë¯¸ë‹¬", delta_color="normal" if result else "inverse"
        )

st.divider()

# ============================================================================
# 2. ?µì‹¬ ë©”íŠ¸ë¦?(?±ê¸‰ ?œìŠ¤???ìš©)
# ============================================================================

st.subheader("?“ˆ ?µì‹¬ ì§€??)

col1, col2, col3, col4 = st.columns(4)

with col1:
    # ?±ê¸‰ ?œìŠ¤??
    grade, emoji = get_grade(team_stats.avg_quality_score)
    st.metric(label=f"{emoji} ?„ì²´ ?±ê¸‰", value=f"{grade}", delta=f"{team_stats.avg_quality_score:.1f}/10")

with col2:
    # ?µê³¼??
    pass_rate = 0.0
    if team_stats.total_checks > 0:
        pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

    pass_emoji = "?Ÿ¢" if pass_rate >= 80 else "?Ÿ¡" if pass_rate >= 60 else "?”´"
    st.metric(
        label=f"{pass_emoji} ?µê³¼??,
        value=f"{pass_rate:.1f}%",
        delta=f"{team_stats.passed_checks}/{team_stats.total_checks}",
    )

with col3:
    # ê¸°ìˆ  ë¶€ì±?
    debt_time = estimate_tech_debt(team_stats.total_violations)
    debt_emoji = "?Ÿ¢" if team_stats.total_violations < 10 else "?Ÿ¡" if team_stats.total_violations < 50 else "?”´"
    st.metric(label=f"{debt_emoji} ê¸°ìˆ  ë¶€ì±?, value=debt_time, delta=f"{team_stats.total_violations}ê°??„ë°˜")

with col4:
    # ë³´ì•ˆ ?´ìŠˆ
    security_emoji = "?Ÿ¢" if team_stats.total_security_issues == 0 else "?”´"
    st.metric(
        label=f"{security_emoji} ë³´ì•ˆ ?´ìŠˆ",
        value=team_stats.total_security_issues,
        delta="?ˆì „" if team_stats.total_security_issues == 0 else "?„í—˜",
        delta_color="normal" if team_stats.total_security_issues == 0 else "inverse",
    )

st.divider()

# ============================================================================
# 3. Hotspots - ê°€??ë¬¸ì œ ë§ì? ?Œì¼ TOP 5
# ============================================================================

st.subheader("?”¥ Hotspots - ???Œì¼?¤ì„ ë¨¼ì? ê³ ì¹˜?¸ìš”!")

# ?Œì¼ ?°ì´?°ë? DataFrame?¼ë¡œ ë³€??
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

    # TOP 5 ë¬¸ì œ ?Œì¼
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
                st.write(f"? ï¸ {row['Violations']} issues")

            with col3:
                if row["Security"] > 0:
                    st.write(f"?›¡ï¸?{row['Security']} security")

            with col4:
                if st.button("?˜ì • ê°€?´ë“œ", key=f"fix_{idx}"):
                    st.session_state["selected_file"] = row["Path"]
                    st.info(f"?“ {row['Path']}ë¥?? íƒ?ˆìŠµ?ˆë‹¤. ?¬ì´?œë°”?ì„œ ?ì„¸ ë¶„ì„???•ì¸?˜ì„¸??")
    else:
        st.success("?‰ ë¬¸ì œê°€ ?ˆëŠ” ?Œì¼???†ìŠµ?ˆë‹¤! ëª¨ë“  ì½”ë“œê°€ ?Œë??´ìš”!")
else:
    st.warning("? ï¸ ë¶„ì„???Œì¼???†ìŠµ?ˆë‹¤. ë¨¼ì? ê²€ì¦ì„ ?¤í–‰?´ì£¼?¸ìš”.")

st.divider()

# ============================================================================
# 4. ?´ìŠˆ ë¶„ë¥˜ (?¬ê°?„ë³„)
# ============================================================================

st.subheader("?“Š ?´ìŠˆ ë¶„ì„")

col1, col2, col3 = st.columns(3)

# ?¤ì œ ?¬ê°???°ì´??(Ruff ê²°ê³¼ ê¸°ë°˜ ì¶”ì •)
critical_count = team_stats.total_security_issues
major_count = team_stats.total_solid_violations
minor_count = team_stats.total_violations - critical_count - major_count
minor_count = max(0, minor_count)  # ?Œìˆ˜ ë°©ì?

with col1:
    st.metric("?”´ Critical", critical_count, "ë³´ì•ˆ ?´ìŠˆ (ì¦‰ì‹œ ?˜ì • ?„ìš”)")

with col2:
    st.metric("?Ÿ¡ Major", major_count, "SOLID ?„ë°˜ (ë¦¬íŒ©? ë§ ê¶Œì¥)")

with col3:
    st.metric("?Ÿ¢ Minor", minor_count, "?¤í????¬ë§¤??(ê°œì„  ê¶Œì¥)")

st.divider()

# ============================================================================
# 5. ?ˆì§ˆ ì¶”ì„¸ ì°¨íŠ¸
# ============================================================================

st.subheader("?“ˆ ?ˆì§ˆ ì¶”ì„¸")

trends_data = get_trends_data()

if trends_data and len(trends_data) > 0:
    # DataFrame ë³€??
    df = pd.DataFrame(trends_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.tail(30)  # ìµœê·¼ 30ê°?

    # Plotly ì°¨íŠ¸
    fig = go.Figure()

    # Quality Score ?¼ì¸
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

    # Pass Rate ?¼ì¸
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

    # ?ˆì´?„ì›ƒ
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

    # ?µê³„ ?”ì•½
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("?‰ê·  ?ˆì§ˆ", f"{df['quality_score'].mean():.1f}")
    with col2:
        st.metric("ìµœê³  ?ˆì§ˆ", f"{df['quality_score'].max():.1f}")
    with col3:
        st.metric("ìµœì? ?ˆì§ˆ", f"{df['quality_score'].min():.1f}")
    with col4:
        trend = df["quality_score"].iloc[-1] - df["quality_score"].iloc[0]
        trend_icon = "?“ˆ" if trend > 0 else "?“‰" if trend < 0 else "?¡ï¸"
        st.metric("ì¶”ì„¸", f"{trend_icon} {abs(trend):.1f}")

else:
    st.info("?’¡ ì¶”ì„¸ ?°ì´?°ê? ?„ì§ ?†ìŠµ?ˆë‹¤. ê²€ì¦ì„ ëª?ë²??¤í–‰?˜ë©´ ì°¨íŠ¸ê°€ ê·¸ë ¤ì§‘ë‹ˆ??")

st.divider()

# ============================================================================
# 6. ?„ì²´ ?Œì¼ ëª©ë¡
# ============================================================================

st.subheader("?“ ?„ì²´ ?Œì¼ ëª©ë¡")

if files_list:
    # ?„í„°ë§??µì…˜
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        sort_by = st.selectbox("?•ë ¬ ê¸°ì?", options=["Violations", "Quality", "Path"], index=0)

    with col2:
        status_filter = st.selectbox("?íƒœ ?„í„°", options=["?„ì²´", "?µê³¼ë§?, "?¤íŒ¨ë§?], index=0)

    with col3:
        min_quality = st.slider("ìµœì†Œ ?ˆì§ˆ", 0.0, 10.0, 0.0, 0.5)

    # ?„í„° ?ìš©
    filtered_df = files_df.copy()
    filtered_df = filtered_df[filtered_df["Quality"] >= min_quality]

    if status_filter == "?µê³¼ë§?:
        filtered_df = filtered_df[filtered_df["Status"] == "??]
    elif status_filter == "?¤íŒ¨ë§?:
        filtered_df = filtered_df[filtered_df["Status"] == "??]

    # ?•ë ¬
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_by == "Path"))

    # ?‰ìƒ ?¨ìˆ˜
    def color_quality(val):
        if val >= 8.0:
            return "background-color: #90EE90"  # ?°í•œ ì´ˆë¡
        elif val >= 6.0:
            return "background-color: #FFE4B5"  # ?°í•œ ?¸ë‘
        else:
            return "background-color: #FFB6C1"  # ?°í•œ ë¹¨ê°•

    # ?¤í????ìš©
    styled_df = filtered_df.style.applymap(color_quality, subset=["Quality"])

    # ?Œì´ë¸??œì‹œ
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

    st.caption(f"?“Š {len(filtered_df)}ê°??Œì¼ ?œì‹œ ì¤?(?„ì²´ {len(files_df)}ê°?")

st.divider()

# ============================================================================
# 7. ?¬ì´?œë°” - ?Œì¼ ?ì„¸ ë¶„ì„
# ============================================================================

with st.sidebar:
    st.header("?” ?Œì¼ ?ì„¸ ë¶„ì„")

    if files_list:
        # ?Œì¼ ? íƒ
        selected_file = st.selectbox("ë¶„ì„???Œì¼ ? íƒ", options=[f["Path"] for f in files_list], index=0)

        st.divider()

        if st.button("?”„ ? íƒ???Œì¼ ë¶„ì„?˜ê¸°", use_container_width=True):
            full_path = project_root / selected_file

            if full_path.exists():
                with st.spinner("ë¶„ì„ ì¤?.."):
                    _, analyzer, detector, _ = get_components()

                    # ë¶„ì„ ?¤í–‰
                    result = analyzer.analyze(full_path)
                    classification = detector.classify(full_path)

                    # ê²°ê³¼ ?œì‹œ
                    st.success("??ë¶„ì„ ?„ë£Œ!")

                    # ?±ê¸‰
                    grade, emoji = get_grade(result.overall_score)
                    st.metric(f"{emoji} Grade", f"{grade}", f"{result.overall_score:.1f}/10")

                    # ?°ì„ ?œìœ„
                    priority = (
                        "?”´ HIGH"
                        if classification.criticality_score >= 0.7
                        else "?Ÿ¡ MEDIUM"
                        if classification.criticality_score >= 0.5
                        else "?Ÿ¢ LOW"
                    )
                    st.metric("Priority", priority)

                    st.divider()

                    # SOLID ?„ë°˜
                    if result.solid_violations:
                        with st.expander(f"? ï¸ SOLID ?„ë°˜ ({len(result.solid_violations)}ê°?", expanded=True):
                            for v in result.solid_violations[:5]:
                                st.text(f"Line {v.line}: {v.message}")

                    # ë³´ì•ˆ ?´ìŠˆ
                    if result.security_issues:
                        with st.expander(f"?›¡ï¸?ë³´ì•ˆ ?´ìŠˆ ({len(result.security_issues)}ê°?", expanded=True):
                            for s in result.security_issues[:5]:
                                st.text(f"Line {s.line}: {s.message}")

                    # Hallucination ?„í—˜
                    if result.hallucination_risks:
                        with st.expander(f"?¤– Hallucination ?„í—˜ ({len(result.hallucination_risks)}ê°?"):
                            for h in result.hallucination_risks[:5]:
                                st.text(f"Line {h.line}: {h.message}")

                    # ê°œì„  ?œì•ˆ
                    st.divider()
                    st.subheader("?’¡ ê°œì„  ?œì•ˆ")

                    if result.overall_score >= 8.0:
                        st.success("?‘ ?Œë???ì½”ë“œ?…ë‹ˆ?? ?„ì¬ ?íƒœë¥?? ì??˜ì„¸??")
                    elif result.overall_score >= 6.0:
                        st.warning("? ï¸ ë¦¬íŒ©? ë§??ê¶Œì¥?©ë‹ˆ?? SOLID ?„ë°˜??ë¨¼ì? ?´ê²°?˜ì„¸??")
                    else:
                        st.error("?š¨ ì¦‰ì‹œ ê°œì„ ???„ìš”?©ë‹ˆ?? ë³´ì•ˆ ?´ìŠˆ?€ SOLID ?„ë°˜???°ì„  ?´ê²°?˜ì„¸??")

            else:
                st.error("???Œì¼??ì°¾ì„ ???†ìŠµ?ˆë‹¤!")

    st.divider()

    # ?ë™ ê°±ì‹ 
    st.header("?™ï¸ ?¤ì •")

    auto_refresh = st.checkbox("?ë™ ê°±ì‹  (10ì´?")

    if st.button("?”„ ì§€ê¸??ˆë¡œê³ ì¹¨", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

# ?ë™ ê°±ì‹  ë¡œì§
if auto_refresh:
    import time

    time.sleep(10)
    st.rerun()

# ============================================================================
# ?¸í„°
# ============================================================================

st.divider()

st.markdown("""
**Dev Rules Dashboard v0.6.0** (Improved)

?¯ **ëª©ì **: ê°œë°œ?ê? ???˜ì? ì½”ë“œë¥??‘ì„±?˜ë„ë¡??•ëŠ”??
- ??ì¦‰ê°???¼ë“œë°?
- ??ëª…í™•??ë°©í–¥ ?œì‹œ
- ??ì§€?ì  ê°œì„  ?…ë ¤
- ??AI ì½”ë“œ ê²€ì¦?
""")

st.caption("Built with ?¤ï¸ using Streamlit | ì§ˆë¬¸?´ë‚˜ ?¼ë“œë°±ì? ?¸ì œ? ì? ?˜ì˜?©ë‹ˆ??")
