# Collaboration Locking & Preflight Guide

_Last updated: 2025-10-29_

## Purpose
멀티 에이전트/멀티 퍼소나 환경에서 파일 잠금 충돌을 방지하고, 헌법 기반 실행기 회귀를 사전에 차단하기 위한 운영 가이드입니다. 각 단계는 TaskExecutor, Enhanced Executor v2, agent_sync 개선 사항을 전제로 합니다.

## 1. 준비 단계
1. `python scripts/multi_agent_sync.py list` — 현재 에이전트 집중 영역과 콘텍스트 해시 확인
2. `python scripts/agent_sync_status.py` — 활성 잠금을 그룹별로 확인
3. 필요 시 `python scripts/agent_sync_status.py --agent <you> --task <task_id> --files <path …>` — 충돌 가능 파일을 미리 검사
4. YAML 계약에는 `collect_files_to_lock`가 감지할 수 있도록 Evidence/Commands 섹션에 편집 대상 파일을 명시

## 2. 실행 단계
1. 내부 명령(`write_file`, `replace`, `run_shell_command`)은 dict 인자로 제공 (예: `args: {file_path: "…"}`)
2. TaskExecutor는 자동으로 잠금을 획득/해제하며, 충돌 시 `[WARN] File '…' locked by …` 메시지를 표시
3. 잠금 실패가 발생하면 계약을 중단하고 `agent_sync_status.py`로 자세한 정보를 확인

## 3. 검증 단계
1. `python scripts/preflight_checks.py` — Enhanced Executor v2 + Handoff Protocol 테스트 수행
   - 빠른 검증은 `python scripts/preflight_checks.py --quick`
   - 핸드오프 테스트만 필요하면 `python scripts/preflight_checks.py --only-handoff`
2. 추가 회귀가 필요하면 `tests/test_handoff_protocol.py` 외에 해당 도메인 테스트를 수동 실행

## 4. 핸드오프 단계
1. `HANDOFF_REPORT.md` 작성 + `dev-context/agent_sync_state.json` 스냅샷 확인
2. Obsidian 싱크 시 `docs/COLLAB_LOCKING_GUIDE.md` 링크를 함께 남겨 다음 에이전트가 바로 확인하도록 안내
3. 잠금이 남아 있지 않은지 `python scripts/agent_sync_status.py --no-active`로 최종 점검

---

**요약 체크리스트**
- [ ] 잠금/콘텍스트 상태 확인 (`agent_sync_status.py`, `multi_agent_sync.py list`)
- [ ] 계약 작성 시 Evidence/Commands에 파일 경로 포함
- [ ] `python scripts/preflight_checks.py` 실행
- [ ] 핸드오프 전 잠금 해제 및 리포트 공유
- CLI 대시보드: python scripts/lock_dashboard.py --agent <you> --files <paths>로 잠금·충돌 현황을 ASCII 형태로 확인할 수 있습니다.

- Streamlit 대시보드: `streamlit run scripts/lock_dashboard_streamlit.py`로 웹 UI에서 잠금/충돌 현황을 확인할 수 있습니다.
- Preflight 확장: `python scripts/preflight_checks.py --extra "tests/test_session_ecosystem.py"` 와 같이 테스트를 추가하거나 `--skip-handoff`, `--only-handoff` 옵션으로 선택 실행할 수 있습니다.
- Streamlit 실행: `python scripts/launch_lock_dashboard.py` (또는 `--port 8502`)로 대시보드를 띄워 잠금 현황을 시각적으로 확인합니다.
- 프리플라이트 아카이브: `python scripts/preflight_checks.py --quick --extra "tests/test_session_ecosystem.py" > RUNS/preflight/latest.log` 와 같이 로그를 남기고, 필요 시 Evidence 폴더에 첨부하세요.
