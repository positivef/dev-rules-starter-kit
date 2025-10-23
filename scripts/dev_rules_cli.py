#!/usr/bin/env python3
"""
dev-rules - Unified CLI for Dev Rules Starter Kit

Purpose:
- Single entry point for all dev-rules commands
- Improved UX with short, memorable commands
- Auto-discovery of YAML tasks
- Integration with PromptCompressor

Usage:
  dev-rules task run <task-id>      # Run YAML task
  dev-rules task plan <task-id>     # Preview task execution
  dev-rules task list                # List available tasks
  dev-rules prompt compress <text>   # Compress prompt (30-50% savings)
  dev-rules prompt stats             # Show compression statistics
  dev-rules dashboard                # Launch Streamlit dashboard

Constitutional Compliance:
- [P2] CLI Interface Mandate
- [P3] Test-First Development
- [P6] Observability
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import click
import json
from typing import Optional
from task_executor import execute_contract
from prompt_compressor import PromptCompressor


@click.group()
@click.version_option(version="1.1.0", prog_name="dev-rules")
def cli():
    """Dev Rules Starter Kit - Unified CLI

    A constitutional development system for AI-assisted programming.
    """
    pass


# ============================================================================
# Task Management Commands
# ============================================================================


@cli.group()
def task():
    """Task execution and management"""
    pass


@task.command()
@click.argument("task_id")
@click.option("--plan", is_flag=True, help="Preview execution plan (dry-run)")
def run(task_id: str, plan: bool):
    """Run a YAML task by ID

    Examples:
      dev-rules task run FEAT-2025-10-24-01
      dev-rules task run FEAT-2025-10-24-01 --plan
    """
    task_file = find_task_file(task_id)

    if not task_file:
        click.echo(f"[ERROR] Task not found: {task_id}", err=True)
        click.echo("\nAvailable tasks:", err=True)
        list_tasks()
        sys.exit(1)

    click.echo(f"[TASK] {task_id}")
    click.echo(f"[FILE] {task_file}")

    mode = "plan" if plan else "execute"

    try:
        execute_contract(str(task_file), mode=mode)

        if not plan:
            click.echo(f"\n[OK] Task completed: {task_id}")
    except Exception as e:
        click.echo(f"\n[ERROR] Task failed: {e}", err=True)
        sys.exit(1)


@task.command()
@click.argument("task_id")
def plan(task_id: str):
    """Preview task execution plan

    Alias for: dev-rules task run <task-id> --plan
    """
    run(task_id, plan=True)


@task.command(name="list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_tasks(verbose: bool = False):
    """List all available YAML tasks"""
    tasks_dir = Path("TASKS")

    if not tasks_dir.exists():
        click.echo("[WARN] No TASKS directory found", err=True)
        return

    yaml_files = sorted(tasks_dir.glob("*.yaml"))

    if not yaml_files:
        click.echo("No tasks found in TASKS/")
        return

    click.echo(f"[TASKS] Available tasks ({len(yaml_files)}):\n")

    for task_file in yaml_files:
        task_id = task_file.stem

        if verbose:
            # Parse YAML to get title
            import yaml

            try:
                task_data = yaml.safe_load(task_file.read_text(encoding="utf-8"))
                title = task_data.get("title", task_data.get("description", "No title"))
                click.echo(f"  - {task_id}")
                click.echo(f"    {title[:80]}...")
            except Exception:
                click.echo(f"  - {task_id}")
        else:
            click.echo(f"  - {task_id}")


# ============================================================================
# Prompt Compression Commands
# ============================================================================


@cli.group()
def prompt():
    """Prompt compression and optimization"""
    pass


@prompt.command()
@click.argument("text")
@click.option(
    "--level", "-l", type=click.Choice(["light", "medium", "aggressive"]), default="medium", help="Compression level"
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def compress(text: str, level: str, output_json: bool):
    """Compress prompt to reduce token usage (30-50% savings)

    Examples:
      dev-rules prompt compress "Please implement authentication"
      dev-rules prompt compress "Your prompt" --level aggressive --json
    """
    compressor = PromptCompressor(compression_level=level)

    try:
        result = compressor.compress(text)

        if output_json:
            output = {
                "original": result.original,
                "compressed": result.compressed,
                "original_tokens": result.original_tokens,
                "compressed_tokens": result.compressed_tokens,
                "savings_pct": result.savings_pct,
                "compression_rules": result.compression_rules,
            }
            click.echo(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n[INPUT] Original ({result.original_tokens} tokens):")
            click.echo(f"  {result.original}\n")
            click.echo(f"[OUTPUT] Compressed ({result.compressed_tokens} tokens):")
            click.echo(f"  {result.compressed}\n")
            click.echo(f"[SAVINGS] {result.savings_pct:.1f}% ({result.original_tokens - result.compressed_tokens} tokens)")
            click.echo(f"[RULES] Applied: {len(result.compression_rules)}")

    except ValueError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)


@prompt.command()
def stats():
    """Show compression statistics and learned patterns"""
    compressor = PromptCompressor()
    stats = compressor.get_stats()

    click.echo("\n[STATS] PromptCompressor Statistics\n")
    click.echo(f"Compression Level: {stats['compression_level']}")
    click.echo(f"Abbreviations: {stats['abbreviations_count']}")
    click.echo(f"Compression Rules: {stats['compression_rules_count']}")
    click.echo(f"Learned Patterns: {stats['total_learned_patterns']}")
    click.echo(f"High Success Patterns: {stats['high_success_patterns']} (>=80% success rate)")


@prompt.command()
def demo():
    """Run prompt compression demo with examples"""
    compressor = PromptCompressor(compression_level="medium")

    test_prompts = [
        "Please implement the authentication feature for the application with proper error handling",
        "I would like you to create a new database schema for the user management system",
        "Can you make sure that the performance optimization is applied to all the critical files?",
    ]

    click.echo("\n[DEMO] Prompt Compression Demo\n")
    click.echo("=" * 60)

    for i, prompt in enumerate(test_prompts, 1):
        result = compressor.compress(prompt)

        click.echo(f"\n[EXAMPLE] {i}:")
        click.echo(f"Original ({result.original_tokens} tokens):")
        click.echo(f"  {result.original}")
        click.echo(f"\nCompressed ({result.compressed_tokens} tokens):")
        click.echo(f"  {result.compressed}")
        click.echo(f"\n[SAVINGS] {result.savings_pct:.1f}%")
        click.echo("-" * 60)

    stats = compressor.get_stats()
    click.echo("\n[STATS] Compressor Stats:")
    click.echo(f"  Level: {stats['compression_level']}")
    click.echo(f"  Abbreviations: {stats['abbreviations_count']}")
    click.echo(f"  Rules: {stats['compression_rules_count']}")


# ============================================================================
# Dashboard Commands
# ============================================================================


@cli.command()
def dashboard():
    """Launch Streamlit dashboard for Constitution monitoring

    Opens the visual dashboard showing:
    - Constitution compliance rates
    - Quality metrics
    - Project statistics
    """
    import subprocess

    dashboard_path = Path("scripts/dashboard.py")

    if not dashboard_path.exists():
        click.echo("[WARN] Dashboard not found at scripts/dashboard.py", err=True)
        click.echo("\nThe dashboard feature is optional. Skipping.", err=True)
        return

    click.echo("[LAUNCH] Starting Streamlit dashboard...")
    click.echo("[INFO] Dashboard will open in your browser\n")

    try:
        subprocess.run(["streamlit", "run", str(dashboard_path)], check=True)
    except FileNotFoundError:
        click.echo("[ERROR] Streamlit not installed. Install with:", err=True)
        click.echo("  pip install streamlit", err=True)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.echo(f"[ERROR] Dashboard failed: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Helper Functions
# ============================================================================


def find_task_file(task_id: str) -> Optional[Path]:
    """Find YAML task file by ID

    Looks in TASKS/ directory for:
    - Exact match: TASKS/{task_id}.yaml
    - Prefix match: TASKS/FEAT-{task_id}.yaml
    """
    tasks_dir = Path("TASKS")

    if not tasks_dir.exists():
        return None

    # Try exact match first
    exact_match = tasks_dir / f"{task_id}.yaml"
    if exact_match.exists():
        return exact_match

    # Try prefix matches
    for yaml_file in tasks_dir.glob("*.yaml"):
        if yaml_file.stem == task_id or yaml_file.stem.endswith(task_id):
            return yaml_file

    return None


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n[WARN] Interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n[ERROR] Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
