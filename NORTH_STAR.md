# NORTH_STAR - Dev Rules Starter Kit

**읽기 시간: 1분 | 매 작업 시작 전 필수 확인**

---

## 우리가 만드는 것

### 🎯 핵심 정체성
**"실행형 자산 시스템 (Executable Knowledge Base)"**

프로그램 개발 시 사용할 **기준 시스템 체계** - Constitution(헌법)을 중심으로 한 좋은 기준점

### 핵심 개념 3가지

1. **문서가 곧 코드**
   - YAML 계약서 작성 → TaskExecutor 실행
   - 모든 작업이 자산으로 축적

2. **Constitution이 중심**
   - 10개 조항 (P1-P10)
   - 모든 도구는 특정 조항을 강제
   - 대시보드는 "헌법 준수 현황판"

3. **증거 기반 + 지식 자산화**
   - 모든 실행 결과 자동 기록
   - Obsidian 자동 동기화 (3초)

### 7계층 아키텍처

```
Layer 1: Constitution (헌법) ← 모든 것의 중심!
Layer 2: Execution (TaskExecutor, ConstitutionalValidator)
Layer 3: Analysis (DeepAnalyzer, TeamStatsAggregator)
Layer 4: Optimization (Cache, CriticalFileDetector)
Layer 5: Evidence (자동 기록)
Layer 6: Knowledge Asset (ObsidianBridge)
Layer 7: Visualization (Dashboard) ← 단순 시각화 도구
```

---

## 우리가 만드는 것이 **절대 아닌** 것

### ❌ 코드 품질 대시보드 도구
- SonarQube 같은 것 아님
- 대시보드는 Layer 7 (지원 도구일 뿐)
- 화려한 UI/UX가 목표 아님

### ❌ 독립적 분석 도구들의 모음
- DeepAnalyzer는 "P4, P5 강제 도구"
- TeamStatsAggregator는 "P6 점수 계산기"
- 모든 도구는 Constitution 조항 강제가 목적

### ❌ 완성된 프로덕트
- 스타터킷 = 기준 체계 템플릿
- 사용자가 Constitution 수정하여 자신만의 체계 구축

---

## 작업 시작 전 필수 체크리스트

### 🔍 스스로 물어보기

```yaml
이 작업이:
  - Constitution의 어느 조항과 관련되나? (P1~P10)
  - 7계층 중 어디에 속하나? (Layer 1~7)
  - "실행형 자산 시스템" 개념에 부합하나?

만약 답이 불명확하면:
  → constitution.yaml 다시 읽기
  → 이 문서(NORTH_STAR.md) 다시 읽기
```

### ⚠️ 위험 신호 감지

다음 생각이 들면 **즉시 멈추고 재검토**:

- "대시보드를 더 예쁘게 만들어야지"
  → ❌ 잘못된 방향! Layer 7은 단순 시각화

- "이 도구를 독립적으로 개선해야지"
  → ❌ 잘못된 방향! Constitution 조항 강제가 목적

- "사용자 경험을 최적화해야지"
  → ❌ 잘못된 방향! 기준 체계 템플릿이 목적

- "새 기능을 추가해서 완성도를 높여야지"
  → ⚠️ 주의! Constitution에 없으면 불필요

### ✅ 올바른 방향

다음 생각이 들면 **올바른 길**:

- "이 작업이 P4 조항 강제를 개선하나?"
  → ✅ Constitution 중심 사고

- "TaskExecutor가 YAML 계약서를 잘 실행하나?"
  → ✅ 실행형 자산 시스템 강화

- "Obsidian 동기화가 지식 자산화에 도움되나?"
  → ✅ 핵심 개념 부합

- "이 개선이 7계층 어디를 강화하나?"
  → ✅ 아키텍처 이해 정확

---

## Constitution 핵심 조항 (Quick Reference)

| ID | 조항명 | 강제 도구 | Layer |
|----|--------|----------|-------|
| **P1** | YAML 계약서 우선 | TaskExecutor | 2 |
| **P2** | 증거 기반 개발 | TaskExecutor | 2, 5 |
| **P3** | 지식 자산화 | ObsidianBridge | 6 |
| **P4** | SOLID 원칙 | **DeepAnalyzer** | 3 |
| **P5** | 보안 우선 | **DeepAnalyzer** | 3 |
| **P6** | 품질 게이트 | TeamStatsAggregator | 3 |
| **P7** | Hallucination 방지 | DeepAnalyzer | 3 |
| **P8** | 테스트 우선 | pytest | - |
| **P9** | Conventional Commits | pre-commit | - |
| **P10** | Windows 인코딩 | UTF-8 강제 | - |
| **P11** | 원칙 충돌 검증 | AI (수동) | - |
| **P12** | 트레이드오프 분석 | AI (수동) | - |
| **P13** | 헌법 수정 검증 | 사용자 승인 | - |

---

## 의사결정 플로우 (P11, P12, P13 통합)

```
새 작업/기능 제안
    ↓
이 NORTH_STAR.md 읽기 (1분)
    ↓
P11: 과거 원칙과 충돌하나?
    ├─→ Yes → 과거 지시 리마인드
    │         양측 관점 제시
    │         ↓
    └─→ No → 계속
    ↓
constitution.yaml 참조
    ↓
Constitution 조항과 연결됨?
    ├─→ Yes → 7계층 중 위치 확인
    │         ↓
    │         P12: 트레이드오프 분석
    │           - Option A vs B
    │           - 장단점 + 근거
    │           - ROI 계산
    │           - 추천 + 근거
    │         ↓
    │         사용자 결정
    │         ↓
    │         작업 진행
    │
    └─→ No → Constitution 수정 필요?
            ↓
            P13: 헌법 수정 검증
              - 타당성 분석
              - 트레이드오프 (P12)
              - 사용자 승인
            ↓
            승인되면 조항 추가
```

---

## ROI 중심 사고

### 투자 대비 성과 (현재 기준)

```
투입 시간: 264시간 (11일)
절약 시간: 264시간/년 (매일 1시간 × 264일)

1년 ROI: 100%
2년 ROI: 200%
5년 ROI: 500%
```

**질문**: 이 작업이 연간 절약 시간을 늘리나?
- Yes → Constitution 강화
- No → 우선순위 재고려

---

## 긴급 리마인더 (방향 상실 시)

### 🚨 이것만은 기억하라

1. **Constitution이 법이다**
   - 모든 도구는 조항 강제 수단
   - 대시보드는 시각화일 뿐

2. **실행형 자산 시스템이다**
   - YAML → 실행 → 증거 → Obsidian
   - 문서가 곧 코드

3. **기준 체계 템플릿이다**
   - 완성된 제품 아님
   - 좋은 기준점 제공이 목표

---

**마지막 질문 (작업 시작 전)**:

> "이 작업이 Constitution 중심 개발 체계를 강화하는가?"

- Yes → 진행
- No → 재검토
- 모르겠음 → constitution.yaml 다시 읽기

---

**버전**: 1.0.0
**최종 수정**: 2025-10-23
**필수 읽기**: 매 Phase 시작 전, 방향성 혼란 시
