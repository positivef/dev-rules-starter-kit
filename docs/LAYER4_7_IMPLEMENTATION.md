# Layer 4~7 Implementation Playbook

> **목적**: Optimization → Evidence → Knowledge Asset → Visualization 계층을 빠르게 체험할 수 있는 최소 구현 사례를 제공합니다.

---

## 1. Layer 4 - Optimization

### 1.1 VerificationCache 활성화
- 실행: `python scripts/verification_cache.py --build` (기본 캐시 생성)
- YAML 계약서 내 `use_verification_cache: true` 옵션을 추가하여 재실행 시 중복 검증을 건너뜁니다.
- Evidence: `RUNS/<task_id>/cache/`에 해시 정보가 저장됩니다.

### 1.2 CriticalFileDetector 적용
- 실행: `python scripts/critical_file_detector.py --path src/ --top 5`
- 출력: 변경 위험도가 높은 파일 목록(JSON + Markdown)
- 활용: P4, P5 조항 위반 가능성이 높은 파일에 우선적으로 리뷰 리소스를 배정합니다.

---

## 2. Layer 5 - Evidence Collection

| 작업 | 자동화 포인트 | Evidence 위치 |
|------|---------------|----------------|
| TaskExecutor 실행 | `AutomaticEvidenceTracker`가 실행 로그 및 해시 기록 | `RUNS/evidence/<task_id>/execution.json` |
| 거버넌스 체크리스트 | `scripts/governance_gate.py`가 체크리스트와 승인자를 수집 | `RUNS/evidence/<task_id>/governance.json` |
| 모델 출력 기록 | `AutomaticEvidenceTracker`의 `model_outputs` 옵션 | `RUNS/evidence/<task_id>/models/` |

> **팁**: Evidence 폴더 구조를 README에 정의하면 신규 팀원 온보딩 속도가 빨라집니다.

---

## 3. Layer 6 - Knowledge Asset

1. `scripts/obsidian_bridge.py --vault ~/Obsidian/ExecutableAssets`
2. 위 명령을 TaskExecutor 후크로 등록하면 Evidence가 Obsidian Vault에 동기화됩니다.
3. Vault 구조 예시:
   ```
   Vault/
     01_Constitution/
     02_Tasks/
     03_Evidence/
       2024-ROI-Report.md
       P11-Conflict-Review.md
   ```
4. Obsidian에서 Dataview 플러그인을 사용하면 Evidence 메타데이터를 표 형태로 조회할 수 있습니다.

---

## 4. Layer 7 - Visualization (Streamlit)

### 4.1 필수 KPI 스크립트 연동
- `scripts/roi_report.py`의 출력(JSON)을 Streamlit에서 읽어 차트로 표시합니다.
- 최소 KPI: `time_saved_hours`, `constitution_compliance_rate`, `governance_reviews_completed`.

### 4.2 대시보드 최소 레이아웃 예시
```python
import json
import streamlit as st

with open("RUNS/reports/latest_roi.json", "r", encoding="utf-8") as f:
    data = json.load(f)

st.title("Constitution Execution Dashboard")
st.metric("연간 절약 시간", f"{data['time_saved_hours']}시간")
st.metric("헌법 준수율", f"{data['constitution_compliance_rate']}%")
st.metric("거버넌스 리뷰 수", data['governance_reviews_completed'])
```

---

## 5. 운영 체크리스트

| 주기 | 항목 | 담당 |
|------|------|------|
| 매 실행 | `scripts/governance_gate.py` 실행 후 TaskExecutor 시작 | 운영자 |
| 주간 | VerificationCache 재생성 및 CriticalFileDetector 리포트 검토 | 테크 리드 |
| 월간 | `scripts/roi_report.py` 실행, Streamlit 스냅샷 업데이트 | 헌법 관리자 |

---

**다음 단계**: Streamlit 대시보드를 운영하기 전에 ROI 리포트와 Evidence 폴더 구조가 안정화되었는지 확인하고, 필요 시 `docs/CONSTITUTION_ONBOARDING_GUIDE.md`에 있는 워크숍을 반복하세요.
