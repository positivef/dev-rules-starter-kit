# Repository Guidelines

Stay consistent with these guardrails when contributing to automation agents.

## Project Structure & Module Organization
- `backend/` contains core services; launch examples via `streamlit_app.py`.
- `web/` hosts experimental front ends; `scripts/` stores automation runners, sync jobs, and notifications.
- `config/` holds central config and schemas, `dev-context/` shares agent context, and `TASKS/` tracks automation contracts.
- Tests live in `tests/` (see `tests/test_task_executor.py` and `tests/test_enhanced_executor.py`), while investigation logs belong in `RUNS/<task_id>/`.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate`: set up the Python environment.
- `pip install -r requirements.txt`: install Python dependencies.
- `npm install --no-fund --no-audit`: fetch Node tooling quietly.
- `python scripts/context_provider.py get-context`: confirm agent context before commits.
- `python3 setup.py --validate-config --project-name Dummy`: validate configuration compatibility.
- `python -m pytest -q tests`: run the full Pytest suite.
- `npm run release -- --dry-run`: verify semantic-release metadata.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation. Prefer snake_case for modules, functions, and locals; PascalCase for classes; UPPER_SNAKE_CASE for constants. Keep YAML keys lowercase-hyphenated and stay ASCII unless files already use Unicode. Run `ruff check .` (or repo pre-commit hooks) to catch drift before pushing.

## Testing Guidelines
Use Pytest for unit and integration coverage. Name tests `tests/test_<feature>.py`, reuse fixtures, and extend orchestrator coverage when automation pipelines evolve. Update `tests/test_master_config_schema.py` whenever schema fields change, and rerun `python -m pytest -q tests` after modifications.

## Commit & Pull Request Guidelines
Write Conventional Commit messages (e.g., `feat(orchestration): add adaptive policy`) and cite relevant TASK IDs. Pull requests should summarize scope, link tasks, and attach logs or screenshots from `RUNS/<task_id>/` plus any documentation updates. Before requesting review, rerun context validation, the full Pytest suite, and the semantic-release dry run, and share results in the PR thread.

## Security & Configuration Tips
Seed local secrets from `.env.example`, consult `docs/SECRET_MANAGEMENT.md` before credential changes, and log production-impacting experiments in `backup/`. Mirror key insights in Obsidian per `docs/OBSIDIAN_TAG_GUIDE.md` and keep sensitive data out of version control.
