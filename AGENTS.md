# Repository Guidelines

## Project Structure & Module Organization
Place runtime modules inside `src/` and keep automation glue confined to `scripts/` (e.g., `task_executor.py`) so utilities import packaged code cleanly. Store execution contracts in `TASKS/` using uppercase, hyphenated filenames, and archive knowledge artifacts in `docs/`. The `dev-context/`, `memory/`, and `RUNS/` folders hold agent state and evidence; avoid manual edits unless you are diagnosing a run. Update `templates/` when you introduce a repeatable pattern and regenerate downstream copies via the setup script. Add new regression suites under `tests/` alongside the related feature.

## Build, Test, and Development Commands
Install tooling with `pip install -r requirements.txt`. Scaffold a project variant through `python setup.py --project-name MyNewProject --framework fastapi` when you need framework-specific scaffolds. Dry-run automation using `python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan`, then execute with the same command minus `--plan` once approved. Run local guards via `ruff check scripts tests src` and execute the test suite with `pytest -q tests`. Finish with `pre-commit run --all-files` so CI stays green.

## Coding Style & Naming Conventions
Follow PEP 8, four-space indentation, `snake_case` for modules and functions, `PascalCase` for classes, and `UPPER_SNAKE_CASE` constants. Keep Python, YAML, and shell sources ASCII-only per `DEVELOPMENT_RULES.md`; move any emoji or localized copy into Markdown. Let `ruff` fix import ordering and whitespace—avoid silencing rules without consensus.

## Testing Guidelines
Tests use `pytest` discovery over `unittest` fixtures; mirror the structure in `tests/test_task_executor.py`. Name files `test_<feature>.py`, keep mocks local with `unittest.mock`, and cover success, failure, and edge paths for each change. Ensure `pytest -q` passes from a clean checkout and retain determinism by stubbing external calls.

## Commit & Pull Request Guidelines
Commits follow Conventional Commits; scope names mirror directories (`feat(task-exec): tighten port guards`). Squash noisy fixups locally. Each PR should include a crisp summary, linked task or issue IDs, verification notes (`pytest`, `ruff`, `pre-commit`), and updated docs or templates when behavior changes. Keep scaffolding updates separate from runtime logic when feasible.

## Security & Automation Notes
Setup installs emoji guards, `gitleaks`, and Task Executor safety rails (command allowlist, port checks). Prefer running composite work through the executor rather than ad-hoc shell scripts to maintain audit trails. Never commit secrets; if a hook flags sensitive data, rotate the credential and document the remediation in your PR.
