# Constitution Onboarding Guide

> **목적**: `config/constitution.yaml`을 조직 상황에 맞게 빠르게 조정하고, 실행형 자산 시스템을 온보딩할 때 흔히 겪는 시행착오를 줄이기 위한 가이드입니다.

---

## 1. 준비 체크리스트 (30분)

| 단계 | 설명 | 참고 자료 |
|------|------|-----------|
| 1 | NORTH_STAR.md를 읽어 핵심 철학 복습 | `NORTH_STAR.md` |
| 2 | 현재 조직의 필수 규범 정리 | 내부 표준 문서 |
| 3 | 적용 범위 확정 (팀/프로젝트/PoC) | OKR, 프로젝트 계획 |
| 4 | TaskExecutor 데모 실행 | `scripts/demo_executor.py` |

> **TIP**: 첫 워크숍에서는 `config/constitution.yaml` 전체를 다루지 말고, 반드시 필요한 조항(P1~P10)만 골라 적용 범위를 정하세요.

---

## 2. 조항 맞춤화 절차 (Half-day Workshop)

1. **핵심 조항 선별**
   - 조직 필수 규범을 P1~P10과 매핑합니다.
   - 겹치는 항목은 기존 조항에 설명을 추가하고, 없는 항목만 별도 조항으로 작성합니다.
2. **거버넌스 조항(P11~P13) 시뮬레이션**
   - 최근 결정 사례 1~2개를 선택해 P11~P13 체크리스트를 적용해봅니다.
   - 누락된 승인 단계나 기록 포인트가 있는지 확인합니다.
3. **체크리스트 작성**
   - `templates/governance/p11-p13-checklist.yaml`을 복제해 팀 상황에 맞게 수정합니다.
   - TaskExecutor 실행 전에 체크리스트를 채우도록 표준 운영 절차(SOP)에 포함합니다.
4. **증거 경로 설정**
   - `RUNS/evidence/` 하위에 팀별 폴더 구조를 합의하고, ObsidianVault 경로를 설정합니다.

> **워크숍 산출물**: 수정된 `constitution.yaml`, 맞춤형 거버넌스 체크리스트, 증거 수집 경로 정의 문서.

---

## 3. 역할별 온보딩 가이드

### 헌법 관리자 (Lead)
- Constitution 변경 Pull Request 리뷰 책임.
- `scripts/governance_gate.py`를 실행해 체크리스트가 최신 상태인지 확인합니다.
- 분기별로 ROI 리포트를 생성해 경영진에 공유합니다.

### TaskExecutor 운영자
- 작업 시작 전 `templates/governance/p11-p13-checklist.yaml` 작성 상태를 확인합니다.
- `scripts/enhanced_task_executor.py` 실행 시 `--force` 플래그 사용을 최소화하고, 경고 로그를 Evidence에 저장합니다.

### 의사결정 승인자
- P11~P13 문항 중 *승인* 항목에 대한 최종 결정을 내립니다.
- 승인 기록은 `RUNS/evidence/<task_id>/governance.json`에 자동 저장되는지 점검합니다.

---

## 4. 30일 운영 로드맵

| 주차 | 목표 | 실행 포인트 |
|------|------|-------------|
| 1주차 | 파일 구조 정리 및 TaskExecutor 데모 | 샘플 YAML 계약서 실행, Evidence 자동 수집 확인 |
| 2주차 | Constitution 맞춤화 초안 완성 | 워크숍 진행, 거버넌스 체크리스트 초안 작성 |
| 3주차 | 거버넌스 자동화 파일 연결 | `scripts/governance_gate.py` 통합, Evidence 저장 경로 검증 |
| 4주차 | ROI 대시보드 초안 발표 | `scripts/roi_report.py`로 KPI 생성, Streamlit 보조 화면 구성 |

---

## 5. Troubleshooting FAQ

**Q1. 조항이 너무 많아서 팀이 부담스러워합니다.**  
A. `config/constitution.yaml`에서 필수 조항만 남긴 *Lite 버전*을 만들어 첫 달에 사용하세요. 나머지는 체크리스트를 통해 단계적으로 도입합니다.

**Q2. 증거 저장이 누락됩니다.**  
A. `scripts/governance_gate.py` 실행 시 Evidence 경로 유효성을 검증합니다. 경로가 없으면 자동 생성하고, README에 기록하십시오.

**Q3. ROI가 체감되지 않습니다.**  
A. `scripts/roi_report.py`의 입력값 중 "절약 시간"을 실제 팀 데이터를 기반으로 업데이트하세요. Streamlit 대시보드에는 최대 3개의 KPI만 노출하여 집중도를 높입니다.

---

## 6. 다음 단계

1. `docs/LAYER4_7_IMPLEMENTATION.md`를 읽고 최적화~시각화 계층의 구현 예시를 검토합니다.
2. `scripts/roi_report.py`를 실행하여 첫 번째 ROI 리포트를 생성하고, 경영진 브리핑 자료에 포함합니다.
3. 헌법 변경이 필요한 경우 `templates/governance/p11-p13-checklist.yaml`을 통해 P13 절차를 수행한 뒤 Pull Request를 올립니다.

---

**최종 목표**: 모든 의사결정과 실행 자료가 Constitution 조항과 Evidence로 연결되어, 새로운 팀원이 합류해도 즉시 동일한 실행형 자산 시스템을 재현할 수 있도록 하는 것입니다.
