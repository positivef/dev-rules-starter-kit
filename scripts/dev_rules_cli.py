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
def info():
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
# Statistics Commands
# ============================================================================


@cli.group()
def stats():
    """View project statistics and metrics"""
    pass


@stats.command(name="compression")
def stats_compression():
    """Show prompt compression statistics across all tasks"""
    import json
    from pathlib import Path

    runs_dir = Path("RUNS")

    if not runs_dir.exists():
        click.echo("[WARN] No RUNS directory found")
        return

    # Find all compression reports
    reports = list(runs_dir.glob("*/compression_report.json"))

    if not reports:
        click.echo("[INFO] No compression reports found")
        click.echo("       Enable prompt compression in your YAML tasks:")
        click.echo("       prompt_optimization:")
        click.echo("         enabled: true")
        return

    # Aggregate statistics
    total_prompts = 0
    total_original = 0
    total_compressed = 0
    tasks_with_compression = []

    for report_path in reports:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)

            summary = report.get("summary", {})
            total_prompts += summary.get("prompts_compressed", 0)
            total_original += summary.get("total_original_tokens", 0)
            total_compressed += summary.get("total_compressed_tokens", 0)

            tasks_with_compression.append(
                {
                    "task_id": report.get("task_id"),
                    "prompts": summary.get("prompts_compressed", 0),
                    "savings_pct": summary.get("average_savings_pct", 0),
                }
            )
        except Exception:
            continue

    # Display summary
    click.echo("\n[COMPRESSION STATS] Across All Tasks\n")
    click.echo(f"Tasks with compression: {len(tasks_with_compression)}")
    click.echo(f"Total prompts compressed: {total_prompts}")
    click.echo(f"Total original tokens: {total_original}")
    click.echo(f"Total compressed tokens: {total_compressed}")

    if total_original > 0:
        total_savings = ((total_original - total_compressed) / total_original) * 100
        click.echo(f"Total tokens saved: {total_original - total_compressed}")
        click.echo(f"Average savings: {total_savings:.1f}%\n")

        # Show per-task breakdown
        click.echo("[PER-TASK BREAKDOWN]")
        for task in sorted(tasks_with_compression, key=lambda x: x["savings_pct"], reverse=True):
            click.echo(f"  {task['task_id']}: {task['prompts']} prompts, {task['savings_pct']:.1f}% savings")


@stats.command(name="tasks")
def stats_tasks():
    """Show task execution statistics"""
    from pathlib import Path
    import json

    runs_dir = Path("RUNS")

    if not runs_dir.exists():
        click.echo("[WARN] No RUNS directory found")
        return

    # Find all state files
    state_files = list(runs_dir.glob("*/.state.json"))

    if not state_files:
        click.echo("[INFO] No task execution data found")
        return

    # Aggregate statistics
    total_tasks = 0
    successful = 0
    failed = 0

    task_summary = []

    for state_file in state_files:
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            total_tasks += 1
            status = state.get("status", "unknown")

            if status == "success":
                successful += 1
            elif status == "failed":
                failed += 1

            task_id = state_file.parent.name
            task_summary.append(
                {
                    "task_id": task_id,
                    "status": status,
                    "evidence_count": state.get("evidence_count", 0),
                }
            )
        except Exception:
            continue

    # Display summary
    click.echo("\n[TASK STATS] Execution Summary\n")
    click.echo(f"Total tasks: {total_tasks}")
    click.echo(f"Successful: {successful}")
    click.echo(f"Failed: {failed}")

    if total_tasks > 0:
        success_rate = (successful / total_tasks) * 100
        click.echo(f"Success rate: {success_rate:.1f}%\n")

        # Show recent tasks
        click.echo("[RECENT TASKS]")
        for task in task_summary[-10:]:  # Last 10 tasks
            status_icon = "[OK]" if task["status"] == "success" else "[FAIL]"
            click.echo(f"  {status_icon} {task['task_id']} ({task['evidence_count']} evidence files)")


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
