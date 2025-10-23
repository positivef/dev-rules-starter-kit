# C7-Sync Prototype Workspace

이 폴더는 기존 수동 컨텍스트 운영 방식과 C7-Sync 프레임워크를 비교·평가하기 위한 샌드박스입니다.

## 포함 내용
- `scripts/context_compare.py` 활용 가이드
- 측정 지표 제안: 컨텍스트 세팅 단계 수, 오류 감지 시간, 해시 불일치 케이스
- 결과 기록용 `notes/` 폴더 (직접 작성)

## 비교 시나리오
1. **Legacy Flow**
   - 에이전트가 .env, dev-context 문서를 개별적으로 열고 경로/설정을 파악
   - Obsidian 경로를 잘못 참조하거나 오래된 메타데이터에 의존할 위험 존재

2. **C7-Sync Flow**
   - `python3 scripts/context_provider.py get-context`
   - `python3 scripts/multi_agent_sync.py update-status <agent> "focus" <hash>`
   - 보드에서 해시 일치 여부 확인 후 작업 진행

### 빠른 사용법
```bash
# 1. 비교 리포트 생성
python3 scripts/context_compare.py report > experiments/c7-sync-prototype/reports/latest.json

# 2. 에이전트 상태 보드 확인
python3 scripts/multi_agent_sync.py list

# 3. 결과 노트 정리 (수동)
mkdir -p experiments/c7-sync-prototype/notes
# notes/ 디렉터리에 비교 결과를 작성하세요.
```

## 평가 항목 예시
| 항목 | Legacy | C7-Sync |
|------|--------|---------|
| 초기 세팅 단계 수 | 수동 복사/붙여넣기 다수 | 2~3개 CLI 명령 |
| 경로 불일치 탐지 | 사후 발견 | 해시 불일치 즉시 확인 |
| 협업 투명성 | 상태 공유 어려움 | `multi_agent_sync.py list` 로 즉시 확인 |

## 다음 단계 아이디어
- context_provider를 REST API로 래핑해 다른 도구에서도 쉽게 호출
- Slack/Discord 알림으로 context_hash 불일치 자동 감지
- JSON Schema 기반 마스터 설정 검증 추가 (테스트 자동화)

> 주의: 이 폴더는 실험용입니다. 결과를 검토하고 정식 채택 시에는 메인 문서/스크립트에 반영하세요.
