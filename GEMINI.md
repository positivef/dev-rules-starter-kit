# Gemini Code Assistant Context

## Project Overview

This project, the "Development Rules Starter Kit," is a framework for building and maintaining software projects. It's designed to be a reusable template that establishes a consistent and high-quality development process. The core of this starter kit is the "Constitution," a set of rules and principles defined in the `config/constitution.yaml` file.

The project is an "Executable Knowledge Base," where all development activities are driven by and captured as "executable assets." This is achieved through a system of YAML-based "contracts" that define tasks, which are then executed by a `TaskExecutor` script. The results of these executions are recorded as evidence, ensuring a transparent and auditable development history.

The main technologies used in this project include:

*   **Python:** The primary language for scripting and automation.
*   **Node.js:** Used for dependency management and release automation (`semantic-release`).
*   **Docker:** For containerization and consistent runtime environments.
*   **Streamlit:** To provide a simple, web-based dashboard for visualizing project status and quality metrics.
*   **Obsidian:** For knowledge management, with automated synchronization of development activities.

The project follows a 7-layer architecture, with the "Constitution" at its core. All tools and processes are designed to enforce the principles laid out in the Constitution.

## Building and Running

### Initial Setup

To set up a new project using this starter kit, you can use the `setup.sh` script (for Linux/macOS) or `setup.py` (for Windows). These scripts will initialize the project, install dependencies, and configure the necessary tools.

**Using `setup.sh` (recommended for Linux/macOS):**

```bash
./setup.sh --project-name "MyNewProject" --framework fastapi
```

**Using `setup.py` (for Windows):**

```bash
python setup.py --project-name "MyNewProject" --framework fastapi
```

### Running Tasks

All development tasks should be defined in YAML "contract" files located in the `TASKS/` directory. These tasks are executed using the `task_executor.py` script.

```bash
# Plan a task (see the execution plan without running it)
python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan

# Execute a task
python scripts/task_executor.py TASKS/TEMPLATE.yaml
```

### Continuous Integration and Deployment (CI/CD)

The project is configured to use GitHub Actions for CI/CD. The workflows are defined in the `.github/workflows/` directory and include:

*   **`commitlint.yml`:** Enforces the Conventional Commits standard for all commit messages.
*   **`semantic-release.yml`:** Automatically manages versioning and releases based on commit messages.

## Development Conventions

### Constitution-Driven Development

All development work must adhere to the principles and rules defined in the `config/constitution.yaml` file. This "Constitution" is the single source of truth for the project's development process.

### Conventional Commits

All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This is enforced by a `pre-commit` hook that uses `commitlint`.

The format for commit messages is:

```
<type>(<scope>): <subject>
```

### Pre-commit Hooks

The project uses `pre-commit` to automatically run checks before each commit. These checks include:

*   Code linting with `ruff`
*   YAML and JSON validation
*   Commit message format validation with `commitlint`
*   Secret scanning with `gitleaks`

## Key Files

*   `README.md`: The main entry point for understanding the project.
*   `NORTH_STAR.md`: A high-level guide to the project's vision and principles.
*   `config/constitution.yaml`: The "Constitution" that defines all development rules and processes.
*   `setup.sh` and `setup.py`: Scripts for initializing a new project from the starter kit.
*   `scripts/task_executor.py`: The script for executing tasks defined in YAML contracts.
*   `TASKS/`: The directory containing YAML "contract" files for development tasks.
*   `.github/workflows/`: The directory containing GitHub Actions workflows for CI/CD.
*   `streamlit_app.py`: The Streamlit application for the project dashboard.

## Obsidian Integration

The project includes a script, `scripts/obsidian_bridge.py`, that automatically synchronizes development activities with an Obsidian vault. This creates a "knowledge asset" from the development process, making it easy to search and reference past work. The path to the Obsidian vault is configured in the `.env` file.
