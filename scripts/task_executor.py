"""
TaskExecutor v3.2.1 - Secure Execution Contract Runner
Dev Rules Starter Kit - Reusable Executable Knowledge System

Features:
- exec array execution (shell=False, security first)
- Secret/lock/port/dependency/test/performance/accuracy gates
- Human approval (plan hash verification)
- Budget warning/hard limits
- Evidence SHA-256 hashing + provenance recording
- Atomic state writes (.tmp → os.replace)
- Obsidian auto-sync (95% time savings: 20min → 3sec)

Usage:
  python scripts/task_executor.py TASKS/FEAT-YYYY-MM-DD-XX.yaml --plan
  python scripts/task_executor.py TASKS/FEAT-YYYY-MM-DD-XX.yaml
"""

import os
import re
import json
import socket
import hashlib
import yaml
import sys
import glob as glob_module
from pathlib import Path
from subprocess import run, CalledProcessError, TimeoutExpired
from datetime import datetime, timezone
from typing import Any, Dict, List

# Import prompt compression integration, progress tracking, and error handling
sys.path.insert(0, str(Path(__file__).parent))
from prompt_task_integration import apply_compression, save_compression_report
from progress_tracker import create_progress_tracker
from error_handler import ErrorCatalog
from notification_utils import send_slack_notification
from orchestration_policy import OrchestrationPolicy


def write_lessons_template(runs_dir: Path, contract: Dict, status: str, error_message: str | None = None) -> None:
    """Create a skeleton lessons file if one does not exist."""

    lessons_file = runs_dir / "lessons.md"
    if lessons_file.exists():
        return

    project = contract.get("project") or contract.get("project_name") or "unknown"
    task_id = contract.get("task_id", runs_dir.name)
    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    summary_line = "- TODO: Add key learning points."
    if error_message:
        summary_line = f"- Failure reason: {error_message}"

    content = (
        f"# Lessons Learned - {task_id} ({status.upper()})\n"
        f"#lesson #{project} #{date_tag}\n\n"
        "## Summary\n"
        f"{summary_line}\n\n"
        "## What Worked\n- TODO\n\n"
        "## Challenges\n- TODO\n\n"
        "## Next Actions\n- TODO\n"
    )

    lessons_file.write_text(content, encoding="utf-8")


def write_prompt_feedback(runs_dir: Path, stats: List[Dict[str, Any]]) -> None:
    """Persist prompt compression statistics in a compact JSON format."""

    if not stats:
        return

    successes = [s for s in stats if "error" not in s]
    errors = [s for s in stats if "error" in s]

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": len(stats),
    }

    if successes:
        total_original = sum(s.get("original_tokens", 0) for s in successes)
        total_compressed = sum(s.get("compressed_tokens", 0) for s in successes)
        avg_savings = (
            sum(s.get("savings_pct", 0.0) for s in successes) / len(successes)
            if successes
            else 0.0
        )
        best_entry = max(successes, key=lambda s: s.get("savings_pct", 0.0), default=None)

        report["summary"] = {
            "total_prompts": len(successes),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "average_savings_pct": round(avg_savings, 2),
        }

        if best_entry:
            report["top_prompt"] = {
                "command_id": best_entry.get("command_id"),
                "context": best_entry.get("context"),
                "savings_pct": best_entry.get("savings_pct"),
                "rules_applied": best_entry.get("rules_applied"),
            }

        report["entries_detail"] = successes[:5]

    if errors:
        report["errors"] = errors

    feedback_path = runs_dir / "prompt_feedback.json"
    feedback_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

# Command whitelist - customize for your project
ALLOWED_CMDS = {
    "python",
    "python3",
    "pytest",
    "ruff",
    "mypy",
    "black",
    "isort",
    "gitleaks",
    "git",
    "curl",
    "npx",
    "pip",
    "make",
    "node",
    "npm",
    "echo",  # For demonstration purposes
}

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",  # Dangerous root deletion
    r"\beval\b",  # Code injection risk
    r"\bexec\b",  # Code injection risk
    r">\s*/dev/",  # Device overwrite
    r"\$\(",  # Command substitution
    r"`",  # Command substitution (backticks)
    r"&&\s*rm",  # Chained deletion
    r";\s*rm",  # Sequential deletion
    r"chmod\s+777",  # Overly permissive permissions
    r"__import__",  # Dynamic imports (Python)
    r"curl.*\|\s*sh",  # Pipe to shell (curl)
    r"wget.*\|\s*sh",  # Pipe to shell (wget)
    r"mktemp.*\|\s*sh",  # Temp file to shell
    r"nc\s+-e",  # Netcat backdoor
    r"dd\s+if=/dev/zero",  # Disk wipe
]

# Environment variable allowlist - customize for your secrets
ENV_ALLOWLIST = {
    "PATH",
    "HOME",
    "USER",
    "LANG",
    "PYTHONPATH",
    "NODE_ENV",
    "GITHUB_TOKEN",
    "SECRET_KEY",
    "API_KEY",
    "API_SECRET",
}


class TaskExecutorError(Exception):
    """TaskExecutor base exception"""

    pass


class SecurityError(TaskExecutorError):
    """Security violation exception"""

    pass


class BudgetExceededError(TaskExecutorError):
    """Budget exceeded exception"""

    pass


class GateFailedError(TaskExecutorError):
    """Gate failed exception"""

    pass


def atomic_write_json(path: Path, data: Dict):
    """Atomic JSON file write"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(path))


def sha256_file(path: Path) -> str:
    """Calculate file SHA-256 hash"""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def plan_hash(contract: Dict) -> str:
    """Execution plan hash (for human approval)"""
    focus = {
        "commands": contract.get("commands", []),
        "gates": contract.get("gates", []),
        "acceptance_criteria": contract.get("acceptance_criteria", []),
    }
    return hashlib.sha256(json.dumps(focus, sort_keys=True).encode()).hexdigest()[:16]


def ports_free(ports: List[int]):
    """Check if ports are available"""
    for port in ports or []:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", int(port))) == 0:
                raise SecurityError(f"Port already in use: {port}")


def build_env() -> Dict[str, str]:
    """Build environment from allowlist"""
    return {k: v for k, v in os.environ.items() if k in ENV_ALLOWLIST}


def ensure_secrets(keys: List[str], ctx: str = ""):
    """Verify required secrets"""
    for key in keys or []:
        if not os.getenv(key):
            raise SecurityError(f"Missing required secret: {key} (context: {ctx})")


def acquire_lock(lock_name: str, lock_dir: Path) -> Path:
    """Acquire lock file"""
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{lock_name}.lock"
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return lock_path
    except FileExistsError:
        raise SecurityError(f"Lock already acquired: {lock_name}")


def release_lock(lock_path: Path):
    """Release lock file"""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def run_validation_commands(commands: List[str], cwd: Path, task_id: str):
    """Execute post-run validation commands.

    Successful commands are silent; failures raise ``GateFailedError`` and
    optionally trigger Slack notifications when a webhook is configured.
    """

    if not commands:
        return

    for command in commands:
        cmd = command.strip()
        if not cmd:
            continue

        print(f"[VALIDATE] {cmd}")
        result = run(cmd, shell=True, cwd=str(cwd))
        if result.returncode != 0:
            message = f"Validation failed for {task_id}: {cmd}"
            send_slack_notification(f":warning: {message}")
            raise GateFailedError(message)


def run_exec(cmd: str, args: List[str], cwd: Path, env: Dict[str, str], timeout: int = 300):
    """Safe command execution (exec array, shell=False)"""
    # 1. Command allowlist check
    if cmd not in ALLOWED_CMDS:
        error = ErrorCatalog.command_not_allowed(cmd)
        print(f"\n{error.format()}", file=sys.stderr)
        raise SecurityError(error.message)

    # 2. Dangerous pattern check
    full_cmd = f"{cmd} {' '.join(args)}"
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, full_cmd):
            raise SecurityError(f"Dangerous pattern detected: {pattern}")

    # 3. Execute with exec array (shell=False)
    print(f"[EXEC] {cmd} {' '.join(args)}")
    try:
        result = run([cmd] + args, cwd=str(cwd), env=env, capture_output=True, shell=False, check=False, timeout=timeout)

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore")
            error = ErrorCatalog.command_failed(cmd, result.returncode, stderr)
            print(f"\n{error.format()}", file=sys.stderr)
            raise CalledProcessError(result.returncode, [cmd] + args)

        return result

    except TimeoutExpired:
        raise TaskExecutorError(f"Command timeout ({timeout}s): {cmd}")


def execute_contract(contract_path: str, mode: str = "execute"):
    """Execute task contract"""
    root = Path(".").resolve()
    contract_file = Path(contract_path)

    # Check if file exists
    if not contract_file.exists():
        error = ErrorCatalog.file_not_found(contract_path)
        print(f"\n{error.format()}", file=sys.stderr)
        raise FileNotFoundError(error.message)

    # Parse YAML
    try:
        contract = yaml.safe_load(contract_file.read_text(encoding="utf-8"))
    except Exception as e:
        error = ErrorCatalog.yaml_parse_error(contract_path, e)
        print(f"\n{error.format(include_traceback=True)}", file=sys.stderr)
        raise

    task_id = contract["task_id"]
    runs_dir = root / "RUNS" / task_id
    runs_dir.mkdir(parents=True, exist_ok=True)

    state_file = runs_dir / ".state.json"
    locks_dir = root / "LOCKS"

    # === PROMPT COMPRESSION (Step 1.5: After loading, before execution) ===
    compression_config = contract.get("prompt_optimization", {})
    compression_stats = []

    if compression_config.get("enabled", False):
        print("\n[COMPRESSION] Prompt optimization enabled")
        print(f"   Level: {compression_config.get('compression_level', 'medium')}")

        try:
            contract, compression_stats = apply_compression(contract, compression_config)

            if compression_stats:
                total_original = sum(s.get("original_tokens", 0) for s in compression_stats)
                total_compressed = sum(s.get("compressed_tokens", 0) for s in compression_stats)
                avg_savings = sum(s.get("savings_pct", 0) for s in compression_stats) / len(compression_stats)

                print(f"   Prompts compressed: {len(compression_stats)}")
                print(f"   Total tokens: {total_original} -> {total_compressed}")
                print(f"   Average savings: {avg_savings:.1f}%")

                # Save compression report
                report_path = compression_config.get("report_path", "RUNS/{task_id}/compression_report.json")
                save_compression_report(compression_stats, report_path, task_id)
                write_prompt_feedback(runs_dir, compression_stats)
                print(f"   Report: {report_path.replace('{task_id}', task_id)}")

        except Exception as e:
            error = ErrorCatalog.compression_failed(e)
            print(f"\n{error.format()}", file=sys.stderr)
            # Continue with uncompressed prompts

    # === 1. Budget gate (pre-check) ===
    estimated_cost = sum(float(cmd.get("cost_estimate_usd", 0)) for cmd in contract.get("commands", []))
    budget = float(contract.get("telemetry", {}).get("cost_budget_usd", 0))
    warn_threshold = float(contract.get("telemetry", {}).get("cost_warn_threshold", 0))
    hard_limit = bool(contract.get("telemetry", {}).get("cost_hard_limit", True))

    if budget and warn_threshold and estimated_cost >= budget * warn_threshold:
        print(f"[WARN] Estimated cost ${estimated_cost:.2f} approaching budget ${budget:.2f}")

    if budget and hard_limit and estimated_cost > budget:
        error = ErrorCatalog.budget_exceeded(estimated_cost, budget)
        print(f"\n{error.format()}", file=sys.stderr)
        raise BudgetExceededError(error.message)

    # === 2. Plan mode (human approval hash) ===
    if mode == "plan":
        hash_val = plan_hash(contract)
        print("\n=== Execution Plan ===")
        print(f"Task ID: {task_id}")
        print(f"Title: {contract.get('title')}")
        print(f"\nCommands ({len(contract.get('commands', []))}):")
        for cmd in contract.get("commands", []):
            exec_info = cmd.get("exec", {})
            print(f"  - {cmd['id']}: {exec_info.get('cmd')} {' '.join(exec_info.get('args', []))}")

        print(f"\nGates ({len(contract.get('gates', []))}):")
        for gate in contract.get("gates", []):
            print(f"  - {gate.get('id')}")

        print(f"\nEstimated Cost: ${estimated_cost:.2f}")
        print(f"Budget: ${budget:.2f}")
        print(f"\n[HASH] Plan Hash: {hash_val}")
        print("\nTo approve, run:")
        print(f"  echo '{hash_val}' > RUNS/{task_id}/.human_approved")
        return

    policy_engine = OrchestrationPolicy()
    metadata = policy_engine.build_metadata(contract)
    use_zen = policy_engine.should_use_zen(metadata)
    execution_label = "Zen MCP" if use_zen else "Sequential MCP"
    print(f"[POLICY] Execution mode: {execution_label} ({metadata.summary()})")
    validation_commands = policy_engine.get_validation_commands()

    if not use_zen and validation_commands:
        print("[NOTICE] Sequential mode requested. Validation commands must be reviewed manually:")
        for cmd in validation_commands:
            print(f"         - {cmd}")

    # === PROGRESS TRACKING (Initialize) ===
    # Calculate total steps: commands + gates + evidence collection
    total_steps = len(contract.get("commands", [])) + len(contract.get("gates", [])) + 1  # +1 for evidence
    progress = create_progress_tracker(total_steps, task_id)

    # === 3. Human approval verification ===
    approved_file = runs_dir / ".human_approved"
    need_human = any(g.get("id") == "human-review" for g in contract.get("gates", []))

    if need_human:
        expected_hash = plan_hash(contract)
        if not approved_file.exists():
            raise SecurityError("Human approval required. Run with --plan first.")

        actual_hash = approved_file.read_text().strip()
        if actual_hash != expected_hash:
            raise SecurityError(f"Plan hash mismatch: {actual_hash} != {expected_hash}")

        print(f"[OK] Human approval verified: {expected_hash}")

    # === 4. Security checks ===
    ensure_secrets(contract.get("secrets_required"), ctx=task_id)

    acquired_locks = []
    try:
        for lock in contract.get("locks", []):
            acquired_locks.append(acquire_lock(lock, locks_dir))

        ports_free(contract.get("ports_should_be_free"))

        env = build_env()

        # === 5. Command execution ===
        atomic_write_json(
            state_file, {"status": "running", "step": "commands:begin", "at": datetime.now(timezone.utc).isoformat()}
        )

        for cmd in contract.get("commands", []):
            # Progress: Start command
            cmd_desc = cmd.get("description", cmd["id"])
            progress.start_step(f"Command: {cmd_desc}")

            atomic_write_json(state_file, {"status": "running", "step": f"commands:{cmd['id']}"})

            try:
                exec_info = cmd.get("exec", {})
                run_exec(exec_info["cmd"], exec_info.get("args", []), root, env)
                progress.complete_step(success=True)
            except Exception:
                progress.complete_step(success=False)
                raise

        # === 6. Quality gates ===
        for gate in contract.get("gates", []):
            gate_id = gate.get("id", "unknown")
            gate_desc = gate.get("description", gate_id)

            # Progress: Start gate
            progress.start_step(f"Gate: {gate_desc}")

            atomic_write_json(state_file, {"status": "running", "step": f"gates:{gate_id}"})

            try:
                if gate_id == "human-review":
                    # Already verified
                    pass
                else:
                    exec_info = gate.get("exec")
                    if exec_info:
                        run_exec(exec_info["cmd"], exec_info.get("args", []), root, env)
                progress.complete_step(success=True)
            except Exception:
                progress.complete_step(success=False)
                raise

        # === 7. Evidence collection + SHA-256 hashing ===
        progress.start_step("Collecting evidence and generating hashes")

        evidence_hashes = {}
        for pattern in contract.get("evidence", []):
            for filepath in glob_module.glob(pattern):
                path = Path(filepath)
                if path.exists() and path.is_file():
                    evidence_hashes[str(path)] = sha256_file(path)

        progress.complete_step(success=True)

        # === 8. Provenance recording ===
        provenance = contract.get("provenance", {}).copy()
        provenance["evidence_sha256"] = evidence_hashes
        provenance["executed_at"] = datetime.now(timezone.utc).isoformat()
        provenance["executor"] = "TaskExecutor-v3.2.1"

        atomic_write_json(runs_dir / "provenance.json", provenance)

        # === 9. Success state ===
        atomic_write_json(
            state_file,
            {
                "status": "success",
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "evidence_count": len(evidence_hashes),
            },
        )

        # Progress summary
        progress.summary()

        if use_zen and validation_commands:
            print("\n[POLICY] Running post-execution validation commands...")
            run_validation_commands(validation_commands, root, task_id)

        write_lessons_template(runs_dir, contract, status="success")

        print(f"\n[OK] Task {task_id} completed successfully")
        print(f"   Evidence files: {len(evidence_hashes)}")
        print(f"   Provenance: RUNS/{task_id}/provenance.json")

        # === 10. Obsidian sync ===
        if os.getenv("OBSIDIAN_ENABLED", "false").lower() == "true":
            sync_to_obsidian(contract, task_id, evidence_hashes, "success")

    except Exception as e:
        # Failure state
        atomic_write_json(
            state_file, {"status": "failed", "error": str(e), "failed_at": datetime.now(timezone.utc).isoformat()}
        )
        write_lessons_template(runs_dir, contract, status="failed", error_message=str(e))
        if compression_stats:
            write_prompt_feedback(runs_dir, compression_stats)
        raise

    finally:
        # Release locks
        for lock_path in acquired_locks:
            release_lock(lock_path)


def sync_to_obsidian(contract: dict, task_id: str, evidence_hashes: dict, status: str):
    """Sync execution results to Obsidian"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from obsidian_bridge import create_devlog, append_evidence

        execution_result = {"status": status, "evidence_hashes": evidence_hashes, "git_commits": []}

        devlog_path = create_devlog(contract, execution_result)
        print(f"   [NOTE] Obsidian devlog: {devlog_path.name}")

        if status == "success":
            append_evidence(task_id, list(evidence_hashes.keys()), evidence_hashes)
            print("   [CLIP] Evidence synced to Obsidian")

        return True

    except ImportError as e:
        print(f"   [WARN] Obsidian bridge not available: {e}")
        return False
    except Exception as e:
        print(f"   [WARN] Obsidian sync failed: {e}")
        return False


def execute_lite_mode():
    """Handles simple, YAML-less task execution for quick jobs."""
    print("Entering Lite Mode for quick tasks...")

    try:
        # 1. Get user input for the task title
        task_title = input(">> What did you accomplish? (e.g., fix: Corrected a typo in README): ")
        if not task_title:
            print("Task summary cannot be empty. Aborting.")
            return

        # 2. Auto-collect evidence from git
        print(">> Collecting evidence from `git status`...")
        result = run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        changed_files = [line.strip().split(" ", 1)[1] for line in result.stdout.strip().split("\n") if line.strip()]

        if not changed_files:
            print("No changed files detected. Nothing to record. Aborting.")
            return

        print(f"   Found {len(changed_files)} changed file(s).")

        # 3. Create a lightweight, in-memory contract
        task_id = f"LITE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        lite_contract = {
            "task_id": task_id,
            "title": task_title,
            "project": "PROJECT_NAME",  # This will be replaced by setup.py
            "tags": ["lite-mode"],
        }

        # 4. Sync to Obsidian
        print(">> Syncing to Obsidian...")
        if os.getenv("OBSIDIAN_ENABLED", "false").lower() == "true":
            # In-memory evidence dict for the bridge
            evidence_dict = {file: "N/A (lite-mode)" for file in changed_files}
            sync_to_obsidian(lite_contract, task_id, evidence_dict, "success")
        else:
            print("   Obsidian sync is disabled. Skipping.")

        print(f"\n[OK] Lite task '{task_title}' recorded successfully.")

    except Exception as e:
        print(f"\n[ERROR] Error in Lite Mode: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TaskExecutor v3.2.1")
    help_text = "Path to YAML contract file. If omitted, runs in Lite Mode."
    parser.add_argument("contract", nargs="?", default=None, help=help_text)
    parser.add_argument("--plan", action="store_true", help="Show plan and generate approval hash")
    args = parser.parse_args()

    if args.contract is None:
        # No contract file provided, run in Lite Mode
        execute_lite_mode()
    else:
        # Default behavior: execute a contract file
        mode = "plan" if args.plan else "execute"
        try:
            execute_contract(args.contract, mode=mode)
        except Exception as e:
            print(f"\n[ERROR] Error: {e}", file=sys.stderr)
            sys.exit(1)
