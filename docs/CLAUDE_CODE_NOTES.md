# Claude Code Implementation Notes

## 목적
Codex와 Gemini 관점 통합 결과를 바탕으로, Claude Code가 후속 개발 시 집중해야 할 안정화 및 확장 작업을 정리한 가이드입니다. 우선 Phase 1(기반 안정화) 항목을 완료한 이후 Phase 2(가치 확장)로 진행하는 것을 권장합니다.

## Phase 1 ? 기반 안정화
- **MCP 설정 정합화**: `config/master_config.json`의 `serena`, `morphllm` 활성화 상태를 최신 결정과 일치시키고, 옵시디언 노트 `Dev Rules Project/Work Logs/2025-10-22 MCP Precision System Integration.md`에 동일 내용을 갱신합니다. 변경 시 `RUNS/`에 의사결정 로그를 남겨 추적성을 확보하세요.
- **Precision System 방어 로직 추가**: `scripts/use_precision.py` 또는 Precision 관련 진입 스크립트 선두에서 외부 리포지터리 경로 존재 여부와 최소 기능을 점검하십시오. 실패하면 명시적인 오류 메시지로 종료해 환경 차이를 조기에 탐지합니다.
- **에이전트 온보딩 연결성 개선**: `README.md` (또는 `docs/QUICK_START.md`)에 `AGENTS.md` 링크를 추가하고, 옵시디언 핵심 노트(예: `Dev Rules Project/시스템 발전 히스토리.md`)에도 상호 참조를 남겨 양방향 탐색이 가능하도록 합니다.
- **KPI 자동 수집 파이프라인**: `scripts/metrics_collector.py`(신규)에서 pytest 커버리지 및 규정 준수율을 계산해 `metrics.json`으로 출력하고, `.github/workflows/test_coverage.yml`에 실행 단계를 추가합니다. 결과 파일은 `RUNS/` 및 CI 아티팩트에 저장하세요.
- **핸드오프 프로토콜 고도화**: `scripts/create_handoff_report.py`로 생성되는 `HANDOFF_REPORT.md`가 다음 정보를 포함하도록 확장합니다. (1) 수정된 파일 목록, (2) 최신 커밋 해시, (3) `context_provider.py`로부터 얻은 `context_hash`, (4) 실행한 테스트와 결과, (5) 차단 요인. 보고서를 생성한 뒤 공유 채널(README, RUNS 로그, 옵시디언)에 연결해 모든 에이전트가 동일한 컨텍스트를 참조할 수 있게 하세요.

## Phase 2 ? 가치 확장
- **대시보드 고도화**: Phase 1에서 생성한 `metrics.json`을 `streamlit_app.py`에서 로드하여 테스트 커버리지·법 준수율 추이를 시각화합니다. 이후 Constitution 변경 시뮬레이션 등 확장 기능을 설계하세요.
- **DX 향상 MVP**: `constitution.yaml`과 `TASKS/*.yaml` 편집을 돕는 VS Code 확장을 최소 기능(스니펫 또는 키 자동완성)부터 구현하고, 관련 문서를 `docs/` 및 옵시디언에 남겨 협업 기반을 마련하십시오.
- **마이크로서비스 전환 준비**: `scripts/deep_analyzer.py` 등 분석 모듈을 FastAPI 서비스로 분리할 로드맵을 정의하고, TaskExecutor 호출 계층과 테스트 보완 계획을 수립합니다. 실제 분리는 Phase 1 안정화 완료 후 시작하세요.

## 협업 체크리스트 (Claude Code 관점)
1. `HANDOFF_REPORT.md` 확인 후 `git pull`로 최신 커밋과 `context_hash`를 동기화합니다.
2. `python scripts/context_provider.py get-context`로 현재 해시가 보고서와 일치하는지 확인합니다.
3. Phase 1 잔여 과제부터 처리하며, 완료 시 `scripts/create_handoff_report.py`로 새 보고서를 작성합니다.
4. 헌법 검증, 핵심 테스트를 실행해 결과를 보고서와 `RUNS/`에 함께 기록합니다.

## 참고 경로
- 저장소: `config/master_config.json`, `scripts/use_precision.py`, `scripts/create_handoff_report.py`, `streamlit_app.py`, `.github/workflows/*.yml`
- 옵시디언: `Dev Rules Project/시스템 발전 히스토리.md`, `Dev Rules Project/Work Logs/2025-10-22 MCP Precision System Integration.md`, `Dev Rules Project/핸드오프 프로토콜.md`
- 증거 로그: `HANDOFF_REPORT.md`, `RUNS/evidence/`, `RUNS/tradeoff_analysis.json`

## 실행 순서 제안
1. MCP 설정·외부 의존성 정리 및 문서 동기화
2. `AGENTS.md` 링크 추가, KPI 수집 자동화, 핸드오프 보고서 확장
3. 대시보드·VS Code 확장·마이크로서비스 전환 등 성장 과제 착수

위 순서를 따르면 Phase 1의 안정화 목표를 완료한 뒤 Phase 2 확장 전략을 차례대로 구현할 수 있습니다.
