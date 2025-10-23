# Streamlit vs Flask 실전 예시

## 현재 Flask 구현 (1,000+ 줄 예상)

### backend/app.py (562줄)
```python
# Flask 백엔드
@app.route('/api/stats')
def get_stats():
    # 통계 수집
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)
    return jsonify({...})

@app.route('/api/files')
def get_files():
    # 파일 목록
    return jsonify({...})

# WebSocket
@socketio.on('connect')
def handle_connect():
    emit('initial_data', {...})
```

### frontend/src/App.jsx (예상 500+ 줄)
```javascript
// React 프론트엔드
import React, { useState, useEffect } from 'react';
import { Chart } from 'chart.js';

function Dashboard() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetch('/api/stats').then(res => res.json()).then(setStats);
  }, []);

  return (
    <div className="dashboard">
      <h1>Dev Rules Dashboard</h1>
      {/* 메트릭 카드 */}
      {/* 차트 */}
      {/* 테이블 */}
    </div>
  );
}
```

---

## Streamlit 구현 (150줄)

### streamlit_app.py (전체)
```python
#!/usr/bin/env python3
"""Dev Rules Dashboard - Streamlit 버전

단일 파일로 전체 대시보드 구현
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

# 기존 컴포넌트 import
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.deep_analyzer import DeepAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="Dev Rules Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시로 데이터 로딩 최적화
@st.cache_resource
def get_aggregator():
    """TeamStatsAggregator 초기화 (캐시)"""
    project_root = Path.cwd()
    cache_dir = project_root / "RUNS" / ".cache"
    evidence_dir = project_root / "RUNS" / "evidence"
    stats_dir = project_root / "RUNS" / "stats"

    return TeamStatsAggregator(
        cache_dir=cache_dir,
        evidence_dir=evidence_dir,
        output_dir=stats_dir
    )

@st.cache_data(ttl=60)  # 60초 캐시
def get_stats():
    """팀 통계 가져오기"""
    aggregator = get_aggregator()
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)
    return team_stats, file_stats

# ============================================================================
# 메인 대시보드
# ============================================================================

st.title("📊 Dev Rules Dashboard")
st.markdown("**실시간 코드 품질 모니터링**")

# 통계 로드
team_stats, file_stats = get_stats()

# ============================================================================
# 1. 상단 메트릭 카드
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Files",
        value=team_stats.total_files,
        delta=None
    )

with col2:
    pass_rate = 0.0
    if team_stats.total_checks > 0:
        pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

    st.metric(
        label="Pass Rate",
        value=f"{pass_rate:.1f}%",
        delta=f"{team_stats.passed_checks}/{team_stats.total_checks}"
    )

with col3:
    st.metric(
        label="Avg Quality",
        value=f"{team_stats.avg_quality_score:.1f}/10",
        delta="Good" if team_stats.avg_quality_score >= 7.0 else "Needs Improvement"
    )

with col4:
    st.metric(
        label="Total Violations",
        value=team_stats.total_violations,
        delta=f"🛡️ {team_stats.total_security_issues} security"
    )

st.divider()

# ============================================================================
# 2. 품질 추세 차트
# ============================================================================

st.subheader("📈 Quality Trends")

# 추세 데이터 로드
trends_file = Path("RUNS/stats/trends.json")
if trends_file.exists():
    import json
    with open(trends_file) as f:
        trends_data = json.load(f)

    if isinstance(trends_data, list) and trends_data:
        # DataFrame 변환
        df = pd.DataFrame(trends_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Plotly 차트
        fig = px.line(
            df,
            x='timestamp',
            y='quality_score',
            title='Quality Score Over Time',
            labels={'quality_score': 'Quality Score', 'timestamp': 'Date'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available yet")
else:
    st.info("No trend data available yet")

st.divider()

# ============================================================================
# 3. 파일 목록 테이블
# ============================================================================

st.subheader("📁 File List")

# 파일 데이터를 DataFrame으로 변환
files_list = []
for path, stats in file_stats.items():
    files_list.append({
        'Path': str(path.relative_to(Path.cwd())),
        'Quality Score': round(stats.avg_quality_score, 1),
        'Passed': '✅' if stats.passed_checks > stats.failed_checks else '❌',
        'Violations': stats.total_violations,
        'Security Issues': stats.total_security_issues,
        'Last Checked': stats.last_checked or 'N/A'
    })

files_df = pd.DataFrame(files_list)

# 정렬 옵션
sort_by = st.selectbox(
    "Sort by",
    options=['Quality Score', 'Violations', 'Path'],
    index=0
)
files_df = files_df.sort_values(by=sort_by, ascending=(sort_by == 'Path'))

# 필터링
min_quality = st.slider(
    "Minimum Quality Score",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.5
)
filtered_df = files_df[files_df['Quality Score'] >= min_quality]

# 테이블 표시
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Quality Score": st.column_config.ProgressColumn(
            "Quality Score",
            help="Code quality score (0-10)",
            format="%.1f",
            min_value=0,
            max_value=10,
        ),
    }
)

st.caption(f"Showing {len(filtered_df)} of {len(files_df)} files")

st.divider()

# ============================================================================
# 4. 파일 상세 분석 (사이드바)
# ============================================================================

with st.sidebar:
    st.header("🔍 File Details")

    # 파일 선택
    selected_file = st.selectbox(
        "Select a file",
        options=[f['Path'] for f in files_list],
        index=0 if files_list else None
    )

    if selected_file:
        # 선택된 파일 분석
        full_path = Path.cwd() / selected_file

        if st.button("🔄 Re-analyze", use_container_width=True):
            with st.spinner("Analyzing..."):
                analyzer = DeepAnalyzer(mcp_enabled=False)
                result = analyzer.analyze(full_path)

                st.success(f"Quality Score: {result.overall_score:.1f}/10")

                # SOLID 위반
                if result.solid_violations:
                    st.warning(f"⚠️ {len(result.solid_violations)} SOLID violations")
                    with st.expander("Details"):
                        for v in result.solid_violations:
                            st.text(f"Line {v.line}: {v.message}")

                # 보안 이슈
                if result.security_issues:
                    st.error(f"🛡️ {len(result.security_issues)} security issues")
                    with st.expander("Details"):
                        for s in result.security_issues:
                            st.text(f"Line {s.line}: {s.message}")

                # Hallucination 위험
                if result.hallucination_risks:
                    st.warning(f"🤖 {len(result.hallucination_risks)} hallucination risks")

# ============================================================================
# 5. 자동 갱신
# ============================================================================

st.sidebar.divider()

auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)")
if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()

# 수동 갱신
if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
```

---

## 코드량 비교

### Flask + React
```
backend/app.py:           562 줄
frontend/src/App.jsx:     300 줄
frontend/src/components:  200 줄
frontend/package.json:     30 줄
frontend/index.html:       20 줄
---------------------------------
총합:                  1,112 줄
```

### Streamlit
```
streamlit_app.py:         150 줄
---------------------------------
총합:                     150 줄
```

**차이**: 7배 적은 코드!

---

## 개발 시간 비교

### Flask + React
```
Day 1-2:  Flask 백엔드 API (완료)
Day 3-4:  WebSocket 설정
Day 5-6:  React 프로젝트 설정
Day 7-8:  컴포넌트 개발
Day 9-10: Chart.js 통합
Day 11:   WebSocket 클라이언트
Day 12:   스타일링
Day 13:   테스트
Day 14:   배포 설정
---------------------------------
총 개발 기간: 14일 (2주)
```

### Streamlit
```
Day 1:  Streamlit 앱 작성 (4시간)
Day 2:  테스트 및 개선 (2시간)
---------------------------------
총 개발 기간: 1-2일
```

**차이**: 10배 빠른 개발!

---

## 결론

### 당신의 프로젝트에는?

**현재 상황**:
- ✅ 팀 내부 도구
- ✅ 1-10명 사용
- ✅ 빠른 피드백 필요
- ✅ Python 중심 개발
- ❌ 외부 API 불필요
- ❌ 복잡한 UI 불필요

**추천**: 🏆 **Streamlit**

**이유**:
1. 150줄 vs 1,112줄 (7배 적음)
2. 1-2일 vs 14일 (10배 빠름)
3. Python만 알면 됨
4. 유지보수 간단
5. 프로토타입으로 시작 → 나중에 Flask로 전환 가능

---

## 실행 명령어 비교

### Flask (복잡)
```bash
# 백엔드
cd backend
python app.py

# 프론트엔드 (별도 터미널)
cd frontend
npm install
npm run dev

# 2개 프로세스 관리
```

### Streamlit (간단)
```bash
streamlit run streamlit_app.py

# 끝!
```

---

**다음 단계 제안**:

1. **Phase D Week 2를 Streamlit으로 변경?**
   - 장점: 1-2일 만에 완성
   - 단점: Flask 공부 못함

2. **Flask 계속 진행?**
   - 장점: 프로덕션 스킬 습득
   - 단점: 2주 더 걸림

어떤 방향으로 진행할까요?
