# C7-Sync Snapshot (Context-7 Framework)

이 문서는 여러 에이전트가 동일한 컨텍스트를 공유하도록 보장하기 위해 추가된 C7-Sync 구성 요소를 요약합니다.

## 핵심 구성 요소

- `config/master_config.json`: 단일 진실 공급원(SSoT). 프로젝트명, 경로, 에이전트 역할 등 공유 설정을 정의합니다.
- `.env`: 보안/로컬 값. 이제 `OBSIDIAN_VAULT_PATH`와 같은 경로도 여기서 관리되지만, C7-Sync는 안전한 키만 선택적으로 읽어 갑니다.
- `scripts/context_provider.py`: 에이전트가 세션 시작 시 실행하는 CLI. master_config + .env를 합쳐 컨텍스트와 `context_hash`를 돌려줍니다.
- `scripts/multi_agent_sync.py`: 각 에이전트가 자신의 컨텍스트 해시를 보고하는 간단한 보드. 해시가 다르면 즉시 재동기화해야 합니다.

## 빠른 사용법

1. **컨텍스트 읽기**
   ```bash
   python3 scripts/context_provider.py get-context
   ```
   - `context`와 `context_hash`가 출력됩니다.

2. **에이전트 상태 갱신**
   ```bash
   python3 scripts/multi_agent_sync.py update-status codex "obsidian fix" <context_hash>
   python3 scripts/multi_agent_sync.py list
   ```
   - 모든 에이전트가 동일한 해시를 보고하는지 확인하세요.

3. **환경 검증**
   - `python scripts/check_release_env.py`도 연속해서 실행하면 Node/semantic-release 설정을 함께 점검할 수 있습니다.

## 초보 개발자를 위한 팁

- **컨텍스트는 한 곳에서 관리**: 경로나 주요 설정이 바뀌면 `config/master_config.json`부터 업데이트하세요.
- **세션 시작 루틴**: 새 작업을 시작할 때 `context_provider.py`와 `multi_agent_sync.py`를 차례로 실행해 해시를 맞춰 보세요.
- **문제 발견 시**: multi-agent 보드에 서로 다른 해시가 보이면, 컨텍스트가 어긋난 것입니다. `master_config.json`과 `.env`를 재확인하고 에이전트 세션을 다시 시작하세요.

C7-Sync는 “같은 정보를 바라보는지”를 항상 눈으로 확인하기 위한 최소한의 장치입니다. 앞으로 자동 푸시/웹훅 등이 추가되면 더욱 완결된 멀티 에이전트 동기화 파이프라인으로 발전할 수 있습니다.
