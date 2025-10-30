# Claude Code Implementation Notes

## ����
Codex�� Gemini ���� ���� ����� ��������, Claude Code�� �ļ� ���� �� �����ؾ� �� ����ȭ �� Ȯ�� �۾��� ������ ���̵��Դϴ�. �켱 Phase 1(��� ����ȭ) �׸��� �Ϸ��� ���� Phase 2(��ġ Ȯ��)�� �����ϴ� ���� �����մϴ�.

## Phase 1 ? ��� ����ȭ
- **MCP ���� ����ȭ**: `config/master_config.json`�� `serena`, `morphllm` Ȱ��ȭ ���¸� �ֽ� ������ ��ġ��Ű��, �ɽõ�� ��Ʈ `Dev Rules Project/Work Logs/2025-10-22 MCP Precision System Integration.md`�� ���� ������ �����մϴ�. ���� �� `RUNS/`�� �ǻ���� �α׸� ���� �������� Ȯ���ϼ���.
- **Precision System ��� ���� �߰�**: `scripts/use_precision.py` �Ǵ� Precision ���� ���� ��ũ��Ʈ ���ο��� �ܺ� �������͸� ��� ���� ���ο� �ּ� ����� �����Ͻʽÿ�. �����ϸ� ������� ���� �޽����� ������ ȯ�� ���̸� ���⿡ Ž���մϴ�.
- **������Ʈ �º��� ���Ἲ ����**: `README.md` (�Ǵ� `docs/QUICK_START.md`)�� `AGENTS.md` ��ũ�� �߰��ϰ�, �ɽõ�� �ٽ� ��Ʈ(��: `Dev Rules Project/�ý��� ���� �����丮.md`)���� ��ȣ ������ ���� ����� Ž���� �����ϵ��� �մϴ�.
- **KPI �ڵ� ���� ����������**: `scripts/metrics_collector.py`(�ű�)���� pytest Ŀ������ �� ���� �ؼ����� ����� `metrics.json`���� ����ϰ�, `.github/workflows/test_coverage.yml`�� ���� �ܰ踦 �߰��մϴ�. ��� ������ `RUNS/` �� CI ��Ƽ��Ʈ�� �����ϼ���.
- **�ڵ���� �������� ��ȭ**: `scripts/create_handoff_report.py`�� �����Ǵ� `HANDOFF_REPORT.md`�� ���� ������ �����ϵ��� Ȯ���մϴ�. (1) ������ ���� ���, (2) �ֽ� Ŀ�� �ؽ�, (3) `context_provider.py`�κ��� ���� `context_hash`, (4) ������ �׽�Ʈ�� ���, (5) ���� ����. ������ ������ �� ���� ä��(README, RUNS �α�, �ɽõ��)�� ������ ��� ������Ʈ�� ������ ���ؽ�Ʈ�� ������ �� �ְ� �ϼ���.

## Phase 2 ? ��ġ Ȯ��
- **��ú��� ��ȭ**: Phase 1���� ������ `metrics.json`�� `streamlit_app.py`���� �ε��Ͽ� �׽�Ʈ Ŀ���������� �ؼ��� ���̸� �ð�ȭ�մϴ�. ���� Constitution ���� �ùķ��̼� �� Ȯ�� ����� �����ϼ���.
- **DX ��� MVP**: `constitution.yaml`�� `TASKS/*.yaml` ������ ���� VS Code Ȯ���� �ּ� ���(������ �Ǵ� Ű �ڵ��ϼ�)���� �����ϰ�, ���� ������ `docs/` �� �ɽõ�� ���� ���� ����� �����Ͻʽÿ�.
- **����ũ�μ��� ��ȯ �غ�**: `scripts/deep_analyzer.py` �� �м� ����� FastAPI ���񽺷� �и��� �ε���� �����ϰ�, TaskExecutor ȣ�� ������ �׽�Ʈ ���� ��ȹ�� �����մϴ�. ���� �и��� Phase 1 ����ȭ �Ϸ� �� �����ϼ���.

## ���� üũ����Ʈ (Claude Code ����)
1. `HANDOFF_REPORT.md` Ȯ�� �� `git pull`�� �ֽ� Ŀ�԰� `context_hash`�� ����ȭ�մϴ�.
2. `python scripts/context_provider.py get-context`�� ���� �ؽð� ������ ��ġ�ϴ��� Ȯ���մϴ�.
3. Phase 1 �ܿ� �������� ó���ϸ�, �Ϸ� �� `scripts/create_handoff_report.py`�� �� ������ �ۼ��մϴ�.
4. ��� ����, �ٽ� �׽�Ʈ�� ������ ����� ������ `RUNS/`�� �Բ� ����մϴ�.

## ���� ���
- �����: `config/master_config.json`, `scripts/use_precision.py`, `scripts/create_handoff_report.py`, `streamlit_app.py`, `.github/workflows/*.yml`
- �ɽõ��: `Dev Rules Project/�ý��� ���� �����丮.md`, `Dev Rules Project/Work Logs/2025-10-22 MCP Precision System Integration.md`, `Dev Rules Project/�ڵ���� ��������.md`
- ���� �α�: `HANDOFF_REPORT.md`, `RUNS/evidence/`, `RUNS/tradeoff_analysis.json`

## ���� ���� ����
1. MCP �������ܺ� ������ ���� �� ���� ����ȭ
2. `AGENTS.md` ��ũ �߰�, KPI ���� �ڵ�ȭ, �ڵ���� ���� Ȯ��
3. ��ú��塤VS Code Ȯ�塤����ũ�μ��� ��ȯ �� ���� ���� ����

�� ������ ������ Phase 1�� ����ȭ ��ǥ�� �Ϸ��� �� Phase 2 Ȯ�� ������ ���ʴ�� ������ �� �ֽ��ϴ�.
