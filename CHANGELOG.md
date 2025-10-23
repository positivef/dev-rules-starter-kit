# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-10-24

### 🎯 Major Features - Constitution Governance System

#### Added
- **P11: 원칙 충돌 검증 (Principle Conflict Resolution)**
  - AI가 새 기능이 과거 원칙과 충돌 시 자동으로 리마인드
  - 양측 관점 제시 후 사용자가 의식적으로 선택
  - 방향성 상실 방지 메커니즘

- **P12: 트레이드오프 분석 의무 (Trade-off Analysis Mandate)**
  - 모든 의사결정에 Option A vs B 명시 필수
  - 각 옵션의 장단점에 객관적 근거 제시
  - ROI 계산 포함 (측정 가능 시)
  - AI 편향 차단 및 객관적 의사결정 보장

- **P13: 헌법 수정 검증 (Constitutional Amendment Validation)**
  - Constitution 수정 시 타당성 검증 프로세스
  - 재귀적 완전성 (P13 자체도 이 프로세스 적용)
  - 최대 20개 조항 제한으로 비대화 방지
  - 3개월마다 리뷰 의무

#### Documentation
- **NORTH_STAR.md**: 방향성 상실 방지 가이드 (1분 읽기)
  - 프로젝트 정체성 명확화: "실행형 자산 시스템"
  - "우리가 만드는 것 / 절대 아닌 것" 명시
  - P11-P13 통합 의사결정 플로우
  - ROI 중심 사고 프레임워크

- **TASK_TEMPLATE.md**: Constitution 맥락 포함 작업 명세 템플릿
  - Constitution 조항 연결 체크리스트
  - 7계층 아키텍처 위치 명시
  - "우리가 만드는 것이 아닌 것(NOT)" 섹션
  - P11, P12 검증 체크리스트

- **constitution.yaml**: 전체 헌법 문서 (1,050 lines)
  - 10개 개발 프로세스 조항 (P1-P10)
  - 3개 거버넌스 조항 (P11-P13)
  - 도구-조항 매핑
  - 아키텍처 계층 정의

#### Updated
- **README.md**: Constitution 섹션 추가 (13개 조항 표)
- **streamlit_app.py**: 대시보드 제목 변경
  - "Dev Rules Dashboard" → "⚖️ Constitution 준수 현황판"
  - Layer 7 역할 명시 (시각화 계층)

#### Fixed
- **Ruff linting errors** in streamlit_app.py
  - E722: 모든 bare except 구문 수정 (구체적 예외 타입 지정)
  - E402: sys.path 수정 후 import 허용 설정

### 📊 Impact & ROI

**개발 투입 시간**: 4시간
- Constitution P11-P13 설계: 2시간
- 문서화 (NORTH_STAR, TASK_TEMPLATE): 1.5시간
- 구현 및 테스트: 0.5시간

**예상 절약 시간**:
- 방향성 상실로 인한 재작업 방지: 연 40시간
- 의사결정 시간 단축 (명확한 프로세스): 연 20시간
- 불필요한 기능 개발 방지: 연 30시간
- **총 연간 절약**: 90시간

**ROI**:
- 1년: 2,150% (4시간 투입 → 90시간 절약)
- 5년: 11,150%

### 🏗️ Architecture

**7 Layer Architecture**:
1. Layer 1: Constitution (헌법) - 모든 것의 중심
2. Layer 2: Execution (TaskExecutor, ConstitutionalValidator)
3. Layer 3: Analysis (DeepAnalyzer, TeamStatsAggregator)
4. Layer 4: Optimization (Cache, CriticalFileDetector)
5. Layer 5: Evidence Collection
6. Layer 6: Knowledge Asset (ObsidianBridge)
7. Layer 7: Visualization (Dashboard)

### 🔄 Breaking Changes
None - 모든 변경사항은 기존 시스템과 호환

### 📝 Notes
- P11-P13은 거버넌스 조항으로 AI가 수동으로 적용
- ConstitutionalValidator 자동화는 Phase E에서 검토 예정
- 3개월 후 첫 Constitution 리뷰 예정

---

## [1.0.0] - 2025-10-22

### Initial Release
- Phase C Week 2 완료: 통합 및 최적화
- DeepAnalyzer (P4, P5, P7 강제)
- TeamStatsAggregator (P6 강제)
- TaskExecutor (P1, P2 강제)
- ObsidianBridge (P3 강제)
- Streamlit Dashboard (Layer 7)
