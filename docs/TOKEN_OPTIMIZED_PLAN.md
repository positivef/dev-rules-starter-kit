# Token-Optimized Implementation Plan
## Codex 피드백 반영 + 토큰 최적화 (90% 목표)

### 📊 토큰 예산: 10K (현재 70K 사용 → 80K 총 예산)

## P1: Schema 검증 [토큰: 500]
```python
# project_steering.py +30줄
def validate_master_config():
    config = json.load("config/master_config.json")
    required = {"version": int, "project": dict}
    return all(k in config for k in required)
```

## P2: 정책 엔진 [토큰: 800]
```python
# enhanced_task_executor.py +50줄
def should_use_zen_mcp(task):
    # risk>0.8 → 🛡️
    # failure>0.3 → 🛡️
    # [P] marker → 🚀
    # else → config.zen_mcp_enabled
```

## P3: Slack 알림 [토큰: 600]
```python
# multi_agent_sync.py +40줄
def send_slack():
    webhook = os.environ["SLACK_WEBHOOK_URL"]
    status = {"agents": list_agents(), "time": now()}
    requests.post(webhook, json=status)
```

## P4: ROI 추적 [토큰: 400]
```python
# automatic_evidence_tracker.py +30줄
def log_zen(task_id, metrics):
    entry = {"id": task_id, "duration": metrics["time"]}
    Path("RUNS/zen.jsonl").append(json.dumps(entry))
```

## GitHub Actions [토큰: 200]
```yaml
# .github/workflows/weekly.yml
on:
  schedule: [cron: '0 9 * * 1']
jobs:
  report:
    steps:
      - run: python scripts/multi_agent_sync.py report
        env: {SLACK_WEBHOOK_URL: ${{secrets.SLACK}}}
```

## 검증 체크리스트
- [ ] master_config.json에 orchestration_policy 추가
- [ ] GitHub Secrets에 SLACK_WEBHOOK_URL 등록
- [ ] pytest 실행 확인
- [ ] Slack 알림 테스트

## 예상 결과
- 컨텍스트: 4.5→5.0 ✅
- 자동화: 3.5→4.5 ✅
- 관측성: 3.0→4.0 ✅
- 민첩성: 4.0→4.5 ✅
**총점: 15→18 (90%)**

## Codex 피드백 반영
✅ SPOF 회피: 단순 Schema 검증만
✅ 복잡성 최소화: 강화학습 없음
✅ 점진적 도입: Slack 읽기 전용
✅ 동기식 유지: Speculative 없음
✅ 핵심 집중: Knowledge Graph 보류
