# CI Preflight Integration

## GitHub Actions Example
```yaml
name: Preflight Checks
on:
  pull_request:
  push:
    branches: [main]

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run preflight checks
        run: |
          python scripts/preflight_checks.py --quick --extra "tests/test_session_ecosystem.py"
```

## Azure Pipelines Snippet
```yaml
- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    python scripts/preflight_checks.py --skip-handoff --extra "tests/test_session_ecosystem.py"
  displayName: 'Preflight checks'
```

## Notes
- Use `--quick` for short-lived checks or `--skip-handoff` if 핸드오프 회귀가 이미 다른 단계에서 수행됩니다.
- `--extra` 옵션으로 프로젝트별 핵심 테스트를 추가하세요. 옵션에 공백이 포함되면 따옴표로 감싸고, 필요한 경우 여러 번 지정할 수 있습니다.
- 실패 시 로그가 곧바로 도출되므로 Evidence 수집을 위해 TaskExecutor/pytest 로그를 아카이브하는 단계를 추가해도 좋습니다.
