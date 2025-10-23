#!/usr/bin/env python3
"""Constitution Compliance Dashboard - Streamlit Edition

🎯 궁극적 목적: Constitution 기반 개발 체계의 준수 현황 시각화

이것은 "실행형 자산 시스템(Executable Knowledge Base)"의 Layer 7(시각화 계층)입니다.

핵심 역할:
- P6 조항(Quality Gate) 준수 현황 표시
- P4, P5 조항 위반 Hotspots 시각화
- Constitution 기반 개발 체계 모니터링
- YAML 계약서 실행 결과 확인
- 지식 자산화 추세 분석

주의: 이 대시보드는 검증 도구가 아닙니다.
     검증은 DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)가 수행합니다.
     대시보드는 단순히 결과를 시각화할 뿐입니다.

실행:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import json
import sys

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 기존 컴포넌트 import
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.deep_analyzer import DeepAnalyzer
from scripts.critical_file_detector import CriticalFileDetector

# ============================================================================
# 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="Constitution Compliance Dashboard", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded"
)

# ============================================================================
# 헬퍼 함수들
# ============================================================================


def get_grade(score):
    """0-10 점수를 A-F 등급으로 변환"""
    if score >= 9.0:
        return "A", "🟢"
    if score >= 8.0:
        return "B", "🟢"
    if score >= 7.0:
        return "C", "🟡"
    if score >= 6.0:
        return "D", "🟡"
    return "F", "🔴"


def calculate_quality_gate(team_stats):
    """Quality Gate 통과/실패 판정"""
    conditions = {
        "평균 품질 ≥ 7.0": team_stats.avg_quality_score >= 7.0,
        "통과율 ≥ 80%": (team_stats.passed_checks / team_stats.total_checks * 100) >= 80.0
        if team_stats.total_checks > 0
        else False,
        "보안 이슈 0개": team_stats.total_security_issues == 0,
    }

    passed = all(conditions.values())
    return passed, conditions


def estimate_tech_debt(violations):
    """위반사항을 수정 시간으로 변환 (1 violation = 15분)"""
    if violations == 0:
        return "0 minutes"

    minutes = violations * 15
    hours = minutes / 60
    days = hours / 8  # 1일 = 8시간

    if days >= 1:
        return f"~{days:.1f} days"
    elif hours >= 1:
        return f"~{hours:.1f} hours"
    else:
        return f"~{int(minutes)} minutes"


def get_severity_color(severity):
    """심각도별 색상"""
    colors = {"error": "🔴", "warning": "🟡", "info": "🟢"}
    return colors.get(severity, "⚪")


# ============================================================================
# 캐시된 데이터 로더
# ============================================================================


@st.cache_resource
def get_components():
    """컴포넌트 초기화 (캐시)"""
    cache_dir = project_root / "RUNS" / ".cache"
    evidence_dir = project_root / "RUNS" / "evidence"
    stats_dir = project_root / "RUNS" / "stats"

    aggregator = TeamStatsAggregator(cache_dir=cache_dir, evidence_dir=evidence_dir, output_dir=stats_dir)

    analyzer = DeepAnalyzer(mcp_enabled=False)
    detector = CriticalFileDetector()
    cache = VerificationCache(cache_dir=cache_dir)

    return aggregator, analyzer, detector, cache


@st.cache_data(ttl=30)  # 30초 캐시
def get_team_stats():
    """팀 통계 가져오기"""
    aggregator, _, _, _ = get_components()
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)
    return team_stats, file_stats


@st.cache_data(ttl=60)  # 60초 캐시
def get_trends_data():
    """추세 데이터 로드"""
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
# 메인 대시보드
# ============================================================================

st.title("⚖️ Constitution 준수 현황판")
st.markdown("**실행형 자산 시스템 - Constitution 기반 개발 체계 모니터링**")
st.caption("Layer 7 (시각화 계층) | 검증은 DeepAnalyzer(P4, P5), TeamStatsAggregator(P6)가 수행")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# 통계 로드
team_stats, file_stats = get_team_stats()

# ============================================================================
# 1. Quality Gate (가장 중요!)
# ============================================================================

st.subheader("🎯 Quality Gate")

passed, conditions = calculate_quality_gate(team_stats)

if passed:
    st.success("✅ **PASSED** - 훌륭합니다! 모든 기준을 충족했어요!")
else:
    st.error("❌ **FAILED** - 개선이 필요해요. 아래 조건들을 확인하세요.")

# 조건별 표시
col1, col2, col3 = st.columns(3)

for idx, (condition, result) in enumerate(conditions.items()):
    with [col1, col2, col3][idx]:
        icon = "✅" if result else "❌"
        st.metric(
            label=condition, value=icon, delta="충족" if result else "미달", delta_color="normal" if result else "inverse"
        )

st.divider()

# ============================================================================
# 2. 핵심 메트릭 (등급 시스템 적용)
# ============================================================================

st.subheader("📈 핵심 지표")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # 등급 시스템
    grade, emoji = get_grade(team_stats.avg_quality_score)
    st.metric(label=f"{emoji} 전체 등급", value=f"{grade}", delta=f"{team_stats.avg_quality_score:.1f}/10")

with col2:
    # 통과율
    pass_rate = 0.0
    if team_stats.total_checks > 0:
        pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

    pass_emoji = "🟢" if pass_rate >= 80 else "🟡" if pass_rate >= 60 else "🔴"
    st.metric(
        label=f"{pass_emoji} 통과율",
        value=f"{pass_rate:.1f}%",
        delta=f"{team_stats.passed_checks}/{team_stats.total_checks}",
    )

with col3:
    # 기술 부채
    debt_time = estimate_tech_debt(team_stats.total_violations)
    debt_emoji = "🟢" if team_stats.total_violations < 10 else "🟡" if team_stats.total_violations < 50 else "🔴"
    st.metric(label=f"{debt_emoji} 기술 부채", value=debt_time, delta=f"{team_stats.total_violations}개 위반")

with col4:
    # 보안 이슈
    security_emoji = "🟢" if team_stats.total_security_issues == 0 else "🔴"
    st.metric(
        label=f"{security_emoji} 보안 이슈",
        value=team_stats.total_security_issues,
        delta="안전" if team_stats.total_security_issues == 0 else "위험",
        delta_color="normal" if team_stats.total_security_issues == 0 else "inverse",
    )

st.divider()

# ============================================================================
# 3. Hotspots - 가장 문제 많은 파일 TOP 5
# ============================================================================

st.subheader("🔥 Hotspots - 이 파일들을 먼저 고치세요!")

# 파일 데이터를 DataFrame으로 변환
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
            "Status": "✅" if stats.passed_checks > stats.failed_checks else "❌",
        }
    )

if files_list:
    files_df = pd.DataFrame(files_list)

    # TOP 5 문제 파일
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
                st.write(f"⚠️ {row['Violations']} issues")

            with col3:
                if row["Security"] > 0:
                    st.write(f"🛡️ {row['Security']} security")

            with col4:
                if st.button("수정 가이드", key=f"fix_{idx}"):
                    st.session_state["selected_file"] = row["Path"]
                    st.info(f"📝 {row['Path']}를 선택했습니다. 사이드바에서 상세 분석을 확인하세요.")
    else:
        st.success("🎉 문제가 있는 파일이 없습니다! 모든 코드가 훌륭해요!")
else:
    st.warning("⚠️ 분석된 파일이 없습니다. 먼저 검증을 실행해주세요.")

st.divider()

# ============================================================================
# 4. 이슈 분류 (심각도별)
# ============================================================================

st.subheader("📊 이슈 분석")

col1, col2, col3 = st.columns(3)

# 실제 심각도 데이터 (Ruff 결과 기반 추정)
critical_count = team_stats.total_security_issues
major_count = team_stats.total_solid_violations
minor_count = team_stats.total_violations - critical_count - major_count
minor_count = max(0, minor_count)  # 음수 방지

with col1:
    st.metric("🔴 Critical", critical_count, "보안 이슈 (즉시 수정 필요)")

with col2:
    st.metric("🟡 Major", major_count, "SOLID 위반 (리팩토링 권장)")

with col3:
    st.metric("🟢 Minor", minor_count, "스타일/포매팅 (개선 권장)")

st.divider()

# ============================================================================
# 5. 품질 추세 차트
# ============================================================================

st.subheader("📈 품질 추세")

trends_data = get_trends_data()

if trends_data and len(trends_data) > 0:
    # DataFrame 변환
    df = pd.DataFrame(trends_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.tail(30)  # 최근 30개

    # Plotly 차트
    fig = go.Figure()

    # Quality Score 라인
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

    # Pass Rate 라인
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

    # 레이아웃
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

    # 통계 요약
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("평균 품질", f"{df['quality_score'].mean():.1f}")
    with col2:
        st.metric("최고 품질", f"{df['quality_score'].max():.1f}")
    with col3:
        st.metric("최저 품질", f"{df['quality_score'].min():.1f}")
    with col4:
        trend = df["quality_score"].iloc[-1] - df["quality_score"].iloc[0]
        trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
        st.metric("추세", f"{trend_icon} {abs(trend):.1f}")

else:
    st.info("💡 추세 데이터가 아직 없습니다. 검증을 몇 번 실행하면 차트가 그려집니다!")

st.divider()

# ============================================================================
# 6. 전체 파일 목록
# ============================================================================

st.subheader("📁 전체 파일 목록")

if files_list:
    # 필터링 옵션
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        sort_by = st.selectbox("정렬 기준", options=["Violations", "Quality", "Path"], index=0)

    with col2:
        status_filter = st.selectbox("상태 필터", options=["전체", "통과만", "실패만"], index=0)

    with col3:
        min_quality = st.slider("최소 품질", 0.0, 10.0, 0.0, 0.5)

    # 필터 적용
    filtered_df = files_df.copy()
    filtered_df = filtered_df[filtered_df["Quality"] >= min_quality]

    if status_filter == "통과만":
        filtered_df = filtered_df[filtered_df["Status"] == "✅"]
    elif status_filter == "실패만":
        filtered_df = filtered_df[filtered_df["Status"] == "❌"]

    # 정렬
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_by == "Path"))

    # 색상 함수
    def color_quality(val):
        if val >= 8.0:
            return "background-color: #90EE90"  # 연한 초록
        elif val >= 6.0:
            return "background-color: #FFE4B5"  # 연한 노랑
        else:
            return "background-color: #FFB6C1"  # 연한 빨강

    # 스타일 적용
    styled_df = filtered_df.style.applymap(color_quality, subset=["Quality"])

    # 테이블 표시
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

    st.caption(f"📊 {len(filtered_df)}개 파일 표시 중 (전체 {len(files_df)}개)")

st.divider()

# ============================================================================
# 7. 사이드바 - 파일 상세 분석
# ============================================================================

with st.sidebar:
    st.header("🔍 파일 상세 분석")

    if files_list:
        # 파일 선택
        selected_file = st.selectbox("분석할 파일 선택", options=[f["Path"] for f in files_list], index=0)

        st.divider()

        if st.button("🔄 선택한 파일 분석하기", use_container_width=True):
            full_path = project_root / selected_file

            if full_path.exists():
                with st.spinner("분석 중..."):
                    _, analyzer, detector, _ = get_components()

                    # 분석 실행
                    result = analyzer.analyze(full_path)
                    classification = detector.classify(full_path)

                    # 결과 표시
                    st.success("✅ 분석 완료!")

                    # 등급
                    grade, emoji = get_grade(result.overall_score)
                    st.metric(f"{emoji} Grade", f"{grade}", f"{result.overall_score:.1f}/10")

                    # 우선순위
                    priority = (
                        "🔴 HIGH"
                        if classification.criticality_score >= 0.7
                        else "🟡 MEDIUM"
                        if classification.criticality_score >= 0.5
                        else "🟢 LOW"
                    )
                    st.metric("Priority", priority)

                    st.divider()

                    # SOLID 위반
                    if result.solid_violations:
                        with st.expander(f"⚠️ SOLID 위반 ({len(result.solid_violations)}개)", expanded=True):
                            for v in result.solid_violations[:5]:
                                st.text(f"Line {v.line}: {v.message}")

                    # 보안 이슈
                    if result.security_issues:
                        with st.expander(f"🛡️ 보안 이슈 ({len(result.security_issues)}개)", expanded=True):
                            for s in result.security_issues[:5]:
                                st.text(f"Line {s.line}: {s.message}")

                    # Hallucination 위험
                    if result.hallucination_risks:
                        with st.expander(f"🤖 Hallucination 위험 ({len(result.hallucination_risks)}개)"):
                            for h in result.hallucination_risks[:5]:
                                st.text(f"Line {h.line}: {h.message}")

                    # 개선 제안
                    st.divider()
                    st.subheader("💡 개선 제안")

                    if result.overall_score >= 8.0:
                        st.success("👍 훌륭한 코드입니다! 현재 상태를 유지하세요.")
                    elif result.overall_score >= 6.0:
                        st.warning("⚠️ 리팩토링을 권장합니다. SOLID 위반을 먼저 해결하세요.")
                    else:
                        st.error("🚨 즉시 개선이 필요합니다. 보안 이슈와 SOLID 위반을 우선 해결하세요.")

            else:
                st.error("❌ 파일을 찾을 수 없습니다!")

    st.divider()

    # 자동 갱신
    st.header("⚙️ 설정")

    auto_refresh = st.checkbox("자동 갱신 (10초)")

    if st.button("🔄 지금 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

# 자동 갱신 로직
if auto_refresh:
    import time

    time.sleep(10)
    st.rerun()

# ============================================================================
# 푸터
# ============================================================================

st.divider()

st.markdown("""
**Dev Rules Dashboard v0.6.0** (Improved)

🎯 **목적**: 개발자가 더 나은 코드를 작성하도록 돕는다
- ✅ 즉각적 피드백
- ✅ 명확한 방향 제시
- ✅ 지속적 개선 독려
- ✅ AI 코드 검증
""")

st.caption("Built with ❤️ using Streamlit | 질문이나 피드백은 언제든지 환영합니다!")
