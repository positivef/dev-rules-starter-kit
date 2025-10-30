# Preflight Artifact Tips

- Redirect preflight output to a file for evidence:
  ```bash
  python scripts/preflight_checks.py --quick --extra "tests/test_session_ecosystem.py" > RUNS/preflight/latest.log
  ```
- If running within CI, upload `RUNS/preflight/latest.log` as a pipeline artifact.
- Archive key outputs (e.g., `htmlcov`, `coverage.json`) in `RUNS/evidence/` when relevant for handoff.
- Reference these artifacts in `HANDOFF_REPORT.md` or Obsidian notes to guide the next agent.
