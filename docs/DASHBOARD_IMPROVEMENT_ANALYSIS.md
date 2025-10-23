# 코드 품질 대시보드 개선 분석

**날짜**: 2025-10-23
**목적**: 실제 프로그램 조사 및 사용자 관점 개선사항 도출

---

## 1. 경쟁 제품 분석

### SonarQube (업계 표준)

**주요 기능**:
- ✅ 27개 언어 지원
- ✅ 보안 취약점 감지 (SAST)
- ✅ 기술 부채 추적
- ✅ 상세한 보고서
- ✅ CI/CD 통합
- ✅ 히스토리 추적 (시간대별 품질 변화)

**대시보드 특징**:
```
메인 화면:
┌─────────────────────────────────────┐
│ Project Overview                     │
├─────────────────────────────────────┤
│ Reliability: A  Security: B  Maint: A│
│ Coverage: 80%   Duplications: 3%     │
│ Code Smells: 234  Bugs: 5  Vulns: 2 │
├─────────────────────────────────────┤
│ Activity Timeline (6개월)            │
│ [라인 차트: Quality Gate 통과율]      │
├─────────────────────────────────────┤
│ Hotspots (가장 문제 많은 파일)        │
│ 1. api/auth.py (23 issues)          │
│ 2. core/db.py (18 issues)           │
└─────────────────────────────────────┘
```

**우리가 배울 점**:
1. **등급 시스템** (A-F) - 숫자보다 직관적
2. **Quality Gate** (통과/실패) - 명확한 기준
3. **Hotspots** (문제 파일 우선순위)
4. **Activity Timeline** (6개월 추세)
5. **카테고리별 분류** (Reliability, Security, Maintainability)

---

### CodeClimate (개발자 친화적)

**주요 기능**:
- ✅ 유지보수성 점수
- ✅ 기술 부채 시간 표시 (예: "3일 소요")
- ✅ Pull Request 통합
- ✅ 팀 생산성 메트릭
- ✅ 간단한 UI

**대시보드 특징**:
```
메인 화면:
┌─────────────────────────────────────┐
│ Maintainability: A                   │
│ Test Coverage: 85%                   │
│ Technical Debt: 2.5 days            │
├─────────────────────────────────────┤
│ Open Issues: 45                      │
│ ├─ Critical: 3                       │
│ ├─ Major: 12                        │
│ └─ Minor: 30                        │
├─────────────────────────────────────┤
│ Most Complex Files:                  │
│ [막대 차트]                          │
└─────────────────────────────────────┘
```

**우리가 배울 점**:
1. **기술 부채를 시간으로 표시** ("2.5일 소요")
2. **심각도 분류** (Critical, Major, Minor)
3. **복잡도 순위** (막대 차트)
4. **간단한 메트릭** (너무 많은 숫자 X)

---

### Codacy (자동화 중심)

**주요 기능**:
- ✅ 자동 코드 리뷰
- ✅ 스타일 가이드 체크
- ✅ 보안 패턴
- ✅ 중복 코드 감지

**대시보드 특징**:
- 심플한 카드 레이아웃
- 색상 코딩 (빨강/노랑/초록)
- 트렌드 그래프 (상승/하강 화살표)

---

## 2. 대시보드 UI/UX 베스트 프랙티스

### 원칙 1: 5초 이해 규칙

**"사용자가 5초 안에 대시보드 목적을 이해해야 함"**

**현재 우리 대시보드**:
```
❌ 문제:
- 너무 많은 숫자 (Total Files, Pass Rate, Avg Quality, Violations)
- 무엇을 먼저 봐야 할지 모름
- 액션 아이템이 불명확
```

**개선안**:
```
✅ 해결:
1. 가장 중요한 메트릭 강조 (큰 글씨, 색상)
2. 상태를 직관적으로 (🟢 Good, 🟡 Warning, 🔴 Critical)
3. 액션 아이템 명확화 ("3개 파일 수정 필요")
```

---

### 원칙 2: 시각적 계층 구조

**"중요한 것부터 크게, 위에"**

**현재 문제**:
```
❌ 모든 메트릭이 같은 크기
❌ 차트와 테이블의 우선순위 불명확
```

**개선안**:
```
우선순위 1 (제일 위, 큰 글씨):
  → Quality Gate Status (통과/실패)

우선순위 2 (중간):
  → 핵심 메트릭 4개 (현재 그대로)

우선순위 3 (아래):
  → 상세 차트 및 테이블
```

---

### 원칙 3: 7±2 법칙

**"한 화면에 7-9개 요소만"**

**현재 문제**:
```
❌ 메인 화면에 너무 많은 정보
   - 4개 메트릭
   - 차트
   - 대형 테이블
   - 사이드바
   → 정보 과부하!
```

**개선안**:
```
✅ 정보 계층화:
   1. 대시보드 (개요만)
   2. 상세 페이지 (클릭 시)
```

---

### 원칙 4: 액션 중심 디자인

**"데이터만 보여주지 말고, 무엇을 할지 알려줘"**

**현재 문제**:
```
❌ "Violations: 23" → 그래서 뭘 하라고?
❌ "Quality: 6.5" → 어떻게 올려?
```

**개선안**:
```
✅ "⚠️ 3개 파일 수정 필요 [보기] [수정하기]"
✅ "🔴 Critical: 2개 보안 이슈 [즉시 해결]"
✅ "📈 이번 주 품질 5% 상승 [계속 유지하기]"
```

---

### 원칙 5: 색상 사용 (2-3개만)

**현재 문제**:
```
❌ Streamlit 기본 색상만 사용
❌ 상태가 명확하지 않음
```

**개선안**:
```
✅ 3색 시스템:
   🟢 Green (8.0+): 건강
   🟡 Yellow (6.0-7.9): 주의
   🔴 Red (<6.0): 위험

✅ 적용:
   - 메트릭 카드 배경색
   - 차트 라인 색상
   - 테이블 행 색상
```

---

## 3. 우리 대시보드의 구체적 개선 사항

### ❌ 현재 문제점

#### 문제 1: 너무 많은 숫자
```
현재:
┌─────────────────────────────────────┐
│ Total Files: 150                     │
│ Pass Rate: 94.7%                     │
│ Avg Quality: 8.2                     │
│ Total Violations: 23                 │
└─────────────────────────────────────┘

문제: 숫자만 보고 판단하기 어려움
```

#### 문제 2: 액션 불명확
```
현재: "Quality Score: 5.2"
→ 사용자: "그래서 뭘 해야 하지?"
```

#### 문제 3: 우선순위 없음
```
현재: 모든 파일이 평등하게 표시됨
→ 어떤 파일부터 고쳐야 할지 모름
```

#### 문제 4: 히스토리 부족
```
현재: 현재 상태만 표시
→ 지난주보다 좋아졌는지? 나빠졌는지?
```

#### 문제 5: 팀 관점 부족
```
현재: 전체 통계만
→ 누가 가장 잘하고 있는지? (경쟁/동기부여)
```

---

### ✅ 구체적 개선안

#### 개선 1: Quality Gate (통과/실패)

**추가할 것**:
```python
# Quality Gate 로직
def calculate_quality_gate(team_stats):
    """통과/실패 명확한 기준"""
    conditions = [
        team_stats.avg_quality_score >= 7.0,  # 평균 7.0 이상
        team_stats.pass_rate >= 80.0,          # 80% 통과
        team_stats.total_security_issues == 0  # 보안 이슈 0
    ]

    passed = all(conditions)
    return {
        'status': 'PASSED' if passed else 'FAILED',
        'conditions': conditions
    }
```

**UI**:
```
┌─────────────────────────────────────┐
│ Quality Gate                         │
│ ✅ PASSED                            │
│ ✓ Quality >= 7.0                    │
│ ✓ Pass Rate >= 80%                  │
│ ✓ No Security Issues                │
└─────────────────────────────────────┘
```

---

#### 개선 2: 등급 시스템 (A-F)

**추가할 것**:
```python
def get_grade(score):
    """0-10 점수를 A-F 등급으로"""
    if score >= 9.0: return 'A'
    if score >= 8.0: return 'B'
    if score >= 7.0: return 'C'
    if score >= 6.0: return 'D'
    return 'F'
```

**UI**:
```
현재: "Avg Quality: 8.2"
개선: "📊 Grade: B (8.2/10)"
```

---

#### 개선 3: 기술 부채 시간

**추가할 것**:
```python
def estimate_tech_debt(violations):
    """위반사항을 수정 시간으로 변환"""
    # 경험치: 1 violation = 15분
    minutes = violations * 15
    hours = minutes / 60
    days = hours / 8  # 1일 = 8시간

    if days >= 1:
        return f"{days:.1f} days"
    elif hours >= 1:
        return f"{hours:.1f} hours"
    else:
        return f"{minutes} minutes"
```

**UI**:
```
현재: "Total Violations: 23"
개선: "⏱️ Tech Debt: ~6 hours to fix"
```

---

#### 개선 4: Hotspots (문제 파일 TOP 5)

**추가할 것**:
```python
# 메인 대시보드에 추가
st.subheader("🔥 Hotspots - Fix These First!")

# 가장 문제 많은 파일 5개
hotspots = files_df.nlargest(5, 'Violations')

for idx, row in hotspots.iterrows():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"**{row['Path']}**")
    with col2:
        st.write(f"⚠️ {row['Violations']} issues")
    with col3:
        if st.button("Fix", key=f"fix_{idx}"):
            # 파일로 이동
            st.switch_page("pages/file_detail.py")
```

---

#### 개선 5: 트렌드 화살표

**추가할 것**:
```python
def get_trend_arrow(current, previous):
    """현재 vs 이전 비교"""
    if current > previous:
        return "📈", "green"
    elif current < previous:
        return "📉", "red"
    else:
        return "➡️", "gray"

# 사용
arrow, color = get_trend_arrow(8.2, 7.8)
st.metric(
    "Avg Quality",
    "8.2",
    delta=f"{arrow} from last week",
    delta_color=color
)
```

---

#### 개선 6: 심각도 분류

**추가할 것**:
```python
# Violations를 심각도로 분류
critical = len([v for v in violations if v.severity == 'error'])
major = len([v for v in violations if v.severity == 'warning'])
minor = len([v for v in violations if v.severity == 'info'])

# UI
st.subheader("Issues Breakdown")
col1, col2, col3 = st.columns(3)
col1.metric("🔴 Critical", critical)
col2.metric("🟡 Major", major)
col3.metric("🟢 Minor", minor)
```

---

#### 개선 7: 액션 버튼

**추가할 것**:
```python
# 각 메트릭 카드에 액션 추가
if team_stats.total_security_issues > 0:
    if st.button("🛡️ Fix Security Issues Now"):
        st.switch_page("pages/security.py")

if team_stats.avg_quality_score < 7.0:
    if st.button("📚 Learn How to Improve"):
        st.switch_page("pages/guide.py")
```

---

#### 개선 8: 진행 상황 추적

**추가할 것**:
```python
# 주간 목표 진행률
weekly_goal = {
    'target_quality': 8.0,
    'current_quality': 7.5,
    'target_violations': 0,
    'current_violations': 15
}

progress = (7.5 / 8.0) * 100
st.progress(progress / 100)
st.caption(f"Weekly Goal: {progress:.0f}% complete")
```

---

## 4. 최종 개선된 대시보드 레이아웃

```
┌────────────────────────────────────────────────────────────┐
│ Dev Rules Dashboard                          [🔄 Refresh]   │
├────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Quality Gate: ✅ PASSED                                │ │
│ │ ✓ All conditions met                                   │ │
│ └────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                       │
│ │Grade │ │Pass  │ │Tech  │ │Issues│                       │
│ │  B   │ │94.7% │ │6 hrs │ │  23  │                       │
│ │📈+0.2│ │📈+2% │ │📉-1h │ │🔴3🟡12│                      │
│ └──────┘ └──────┘ └──────┘ └──────┘                       │
├────────────────────────────────────────────────────────────┤
│ 🔥 Hotspots - Fix These First!                             │
│ 1. api/auth.py         ⚠️ 18 issues    [Fix Now]          │
│ 2. core/db.py          ⚠️ 12 issues    [Fix Now]          │
│ 3. utils/helpers.py    ⚠️ 8 issues     [Fix Now]          │
├────────────────────────────────────────────────────────────┤
│ 📈 Quality Trends (Last 30 Days)                           │
│ [인터랙티브 차트]                                           │
├────────────────────────────────────────────────────────────┤
│ 📁 All Files              [Sort▼] [Filter] [Search]       │
│ [테이블 - 색상 코딩]                                        │
└────────────────────────────────────────────────────────────┘
```

---

## 5. 우선순위별 구현 계획

### 🔴 Priority 1 (즉시 구현 - 30분)

1. **Quality Gate** (통과/실패 박스)
2. **등급 시스템** (A-F)
3. **색상 코딩** (🟢🟡🔴)

**이유**: 가장 큰 사용자 가치, 빠른 구현

---

### 🟡 Priority 2 (오늘 중 - 1-2시간)

4. **Hotspots** (TOP 5 문제 파일)
5. **심각도 분류** (Critical/Major/Minor)
6. **트렌드 화살표** (상승/하강)

**이유**: 액션 중심, UX 개선

---

### 🟢 Priority 3 (내일 - 2-3시간)

7. **기술 부채 시간**
8. **주간 목표 추적**
9. **액션 버튼들**
10. **다중 페이지** (메인/상세/가이드)

**이유**: 고급 기능, 장기 가치

---

## 6. 실전 개선 코드 스니펫

### Quality Gate 컴포넌트
```python
def render_quality_gate(team_stats):
    """Quality Gate 렌더링"""
    # 조건 체크
    conditions = {
        '평균 품질 >= 7.0': team_stats.avg_quality_score >= 7.0,
        '통과율 >= 80%': (team_stats.passed_checks / team_stats.total_checks * 100) >= 80,
        '보안 이슈 0개': team_stats.total_security_issues == 0
    }

    all_passed = all(conditions.values())

    # UI
    if all_passed:
        st.success("✅ Quality Gate: PASSED")
    else:
        st.error("❌ Quality Gate: FAILED")

    # 조건별 표시
    for condition, passed in conditions.items():
        icon = "✓" if passed else "✗"
        st.caption(f"{icon} {condition}")
```

### Hotspots 컴포넌트
```python
def render_hotspots(files_df, top_n=5):
    """문제 많은 파일 TOP N"""
    st.subheader("🔥 Hotspots - Fix These First!")

    hotspots = files_df.nlargest(top_n, 'Violations')

    for idx, row in hotspots.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            # 파일명 + 등급
            grade = get_grade(row['Quality'])
            st.write(f"**{row['Path']}** (Grade: {grade})")

        with col2:
            # 이슈 수
            st.write(f"⚠️ {row['Violations']} issues")

        with col3:
            # 액션 버튼
            if st.button("Fix", key=f"fix_{idx}"):
                st.session_state['selected_file'] = row['Path']
                st.rerun()
```

---

## 7. 결론

### ✅ 핵심 개선 사항

1. **Quality Gate**: 통과/실패 명확화
2. **등급 시스템**: A-F로 직관적
3. **Hotspots**: 우선순위 명확
4. **색상 코딩**: 시각적 이해
5. **액션 중심**: "무엇을 할지" 명확

### 📊 기대 효과

**개선 전**:
- 사용자: "숫자는 보이는데 뭘 해야 할지 모르겠어요"
- 시간: 대시보드 이해 2-3분 소요

**개선 후**:
- 사용자: "Quality Gate 실패했네요! Hotspots 3개 먼저 고치면 되겠어요!"
- 시간: 5초 안에 이해, 즉시 액션

### 🎯 다음 단계

Priority 1 개선사항부터 바로 구현하시겠습니까?
- Quality Gate
- 등급 시스템 (A-F)
- 색상 코딩
- Hotspots TOP 5

예상 시간: 30-60분
