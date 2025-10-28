# Repository Guidelines

## Project Structure & Module Organization
Core services live under `backend/`, with `streamlit_app.py` providing the demo UI and experimental front ends housed in `web/`. Automation runners, sync jobs, and notification tooling belong in `scripts/`. Central configuration and schema material resides in `config/`, with shared agent context under `dev-context/` and automation contracts in `TASKS/`. Tests stay in `tests/`, notably `tests/test_task_executor.py` and `tests/test_enhanced_executor.py` for integration flows. Capture debugging artifacts under `RUNS/<task_id>/` to keep investigations traceable.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate` prepares the Python environment once per machine.
- `pip install -r requirements.txt` syncs core Python dependencies.
- `npm install --no-fund --no-audit` installs Node tooling without extra prompts.
- `python scripts/context_provider.py get-context` validates agent context before commits.
- `python3 setup.py --validate-config --project-name Dummy` safeguards configuration compatibility.
- `python -m pytest -q tests` runs the entire test suite quietly.
- `npm run release -- --dry-run` confirms semantic-release metadata.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation across Python sources. Use snake_case for modules, functions, and local vars; PascalCase for classes; UPPER_SNAKE_CASE for constants. Keep YAML keys lowercase-hyphenated and stick to ASCII unless a file already uses Unicode. Run `ruff check .` (or the project pre-commit hooks) before submitting changes to catch formatting drift early.

## Testing Guidelines
Pytest drives unit and integration coverage for this codebase. Place new test modules as `tests/test_<feature>.py`, leaning on fixtures for setup. Extend the orchestrator coverage when automation pipelines change, and update `tests/test_master_config_schema.py` whenever schema fields evolve. Re-run `python -m pytest -q tests` plus any focused suites before pushing.

## Commit & Pull Request Guidelines
Write Conventional Commit messages (example: `feat(orchestration): add adaptive policy`) and reference relevant TASK IDs. Pull requests should summarize scope, link tasks, and attach logs or screenshots from `RUNS/<task_id>/` alongside any documentation updates. Before requesting review, rerun context validation, the full pytest suite, and the semantic-release dry run; share the results in the PR discussion.

## Security & Configuration Tips
Seed secrets from `.env.example` and review `docs/SECRET_MANAGEMENT.md` prior to credentials changes. Log experiments that touch production paths inside `backup/` and mirror key takeaways in Obsidian per `docs/OBSIDIAN_TAG_GUIDE.md`. Avoid committing sensitive data, and rely on in-repo tooling for secret rotation and auditing.
