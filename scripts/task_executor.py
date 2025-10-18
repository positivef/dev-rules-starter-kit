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
from datetime import datetime
from typing import Dict, List, Optional

# Command whitelist - customize for your project
ALLOWED_CMDS = {
    "python", "python3", "pytest", "ruff", "mypy", "black", "isort",
    "gitleaks", "git", "curl", "npx", "pip", "make", "node", "npm"
}

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",      # Dangerous root deletion
    r"\beval\b",          # Code injection risk
    r"\bexec\b",          # Code injection risk
    r">\s*/dev/",         # Device overwrite
    r"\$\(",              # Command substitution
    r"`",                 # Command substitution (backticks)
    r"&&\s*rm",           # Chained deletion
    r";\s*rm",            # Sequential deletion
    r"chmod\s+777",       # Overly permissive permissions
    r"__import__",        # Dynamic imports (Python)
    r"curl.*\|\s*sh",     # Pipe to shell (curl)
    r"wget.*\|\s*sh",     # Pipe to shell (wget)
    r"mktemp.*\|\s*sh",   # Temp file to shell
    r"nc\s+-e",           # Netcat backdoor
    r"dd\s+if=/dev/zero", # Disk wipe
]

# Environment variable allowlist - customize for your secrets
ENV_ALLOWLIST = {
    "PATH", "HOME", "USER", "LANG", "PYTHONPATH", "NODE_ENV",
    "GITHUB_TOKEN", "SECRET_KEY", "API_KEY", "API_SECRET"
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
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
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
        "acceptance_criteria": contract.get("acceptance_criteria", [])
    }
    return hashlib.sha256(
        json.dumps(focus, sort_keys=True).encode()
    ).hexdigest()[:16]


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


def run_exec(cmd: str, args: List[str], cwd: Path, env: Dict[str, str], timeout: int = 300):
    """Safe command execution (exec array, shell=False)"""
    # 1. Command allowlist check
    if cmd not in ALLOWED_CMDS:
        raise SecurityError(f"Command not in allowlist: {cmd}")

    # 2. Dangerous pattern check
    full_cmd = f"{cmd} {' '.join(args)}"
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, full_cmd):
            raise SecurityError(f"Dangerous pattern detected: {pattern}")

    # 3. Execute with exec array (shell=False)
    print(f"[EXEC] {cmd} {' '.join(args)}")
    try:
        result = run(
            [cmd] + args,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            shell=False,
            check=False,
            timeout=timeout
        )

        if result.returncode != 0:
            print(f"[ERROR] Command failed with code {result.returncode}")
            print(f"STDOUT: {result.stdout.decode('utf-8', errors='ignore')}")
            print(f"STDERR: {result.stderr.decode('utf-8', errors='ignore')}")
            raise CalledProcessError(result.returncode, [cmd] + args)

        return result

    except TimeoutExpired:
        raise TaskExecutorError(f"Command timeout ({timeout}s): {cmd}")


def execute_contract(contract_path: str, mode: str = "execute"):
    """Execute task contract"""
    root = Path(".").resolve()
    contract = yaml.safe_load(Path(contract_path).read_text(encoding='utf-8'))

    task_id = contract["task_id"]
    runs_dir = root / "RUNS" / task_id
    runs_dir.mkdir(parents=True, exist_ok=True)

    state_file = runs_dir / ".state.json"
    locks_dir = root / "LOCKS"

    # === 1. Budget gate (pre-check) ===
    estimated_cost = sum(float(cmd.get("cost_estimate_usd", 0)) for cmd in contract.get("commands", []))
    budget = float(contract.get("telemetry", {}).get("cost_budget_usd", 0))
    warn_threshold = float(contract.get("telemetry", {}).get("cost_warn_threshold", 0))
    hard_limit = bool(contract.get("telemetry", {}).get("cost_hard_limit", True))

    if budget and warn_threshold and estimated_cost >= budget * warn_threshold:
        print(f"⚠️  [WARN] Estimated cost ${estimated_cost:.2f} approaching budget ${budget:.2f}")

    if budget and hard_limit and estimated_cost > budget:
        raise BudgetExceededError(f"Budget exceeded: ${estimated_cost:.2f} > ${budget:.2f}")

    # === 2. Plan mode (human approval hash) ===
    if mode == "plan":
        hash_val = plan_hash(contract)
        print(f"\n=== Execution Plan ===")
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
        print(f"\n🔐 Plan Hash: {hash_val}")
        print(f"\nTo approve, run:")
        print(f"  echo '{hash_val}' > RUNS/{task_id}/.human_approved")
        return

    # === 3. Human approval verification ===
    approved_file = runs_dir / ".human_approved"
    need_human = any(g.get("id") == "human-review" for g in contract.get("gates", []))

    if need_human:
        expected_hash = plan_hash(contract)
        if not approved_file.exists():
            raise SecurityError(f"Human approval required. Run with --plan first.")

        actual_hash = approved_file.read_text().strip()
        if actual_hash != expected_hash:
            raise SecurityError(f"Plan hash mismatch: {actual_hash} != {expected_hash}")

        print(f"✅ Human approval verified: {expected_hash}")

    # === 4. Security checks ===
    ensure_secrets(contract.get("secrets_required"), ctx=task_id)

    acquired_locks = []
    try:
        for lock in contract.get("locks", []):
            acquired_locks.append(acquire_lock(lock, locks_dir))

        ports_free(contract.get("ports_should_be_free"))

        env = build_env()

        # === 5. Command execution ===
        atomic_write_json(state_file, {
            "status": "running",
            "step": "commands:begin",
            "at": datetime.utcnow().isoformat()
        })

        for cmd in contract.get("commands", []):
            atomic_write_json(state_file, {
                "status": "running",
                "step": f"commands:{cmd['id']}"
            })

            exec_info = cmd.get("exec", {})
            run_exec(
                exec_info["cmd"],
                exec_info.get("args", []),
                root,
                env
            )

        # === 6. Quality gates ===
        for gate in contract.get("gates", []):
            gate_id = gate.get("id", "unknown")
            atomic_write_json(state_file, {
                "status": "running",
                "step": f"gates:{gate_id}"
            })

            if gate_id == "human-review":
                # Already verified
                pass
            else:
                exec_info = gate.get("exec")
                if exec_info:
                    run_exec(
                        exec_info["cmd"],
                        exec_info.get("args", []),
                        root,
                        env
                    )

        # === 7. Evidence collection + SHA-256 hashing ===
        evidence_hashes = {}
        for pattern in contract.get("evidence", []):
            for filepath in glob_module.glob(pattern):
                path = Path(filepath)
                if path.exists() and path.is_file():
                    evidence_hashes[str(path)] = sha256_file(path)

        # === 8. Provenance recording ===
        provenance = contract.get("provenance", {}).copy()
        provenance["evidence_sha256"] = evidence_hashes
        provenance["executed_at"] = datetime.utcnow().isoformat()
        provenance["executor"] = "TaskExecutor-v3.2.1"

        atomic_write_json(runs_dir / "provenance.json", provenance)

        # === 9. Success state ===
        atomic_write_json(state_file, {
            "status": "success",
            "finished_at": datetime.utcnow().isoformat(),
            "evidence_count": len(evidence_hashes)
        })

        print(f"\n✅ Task {task_id} completed successfully")
        print(f"   Evidence files: {len(evidence_hashes)}")
        print(f"   Provenance: RUNS/{task_id}/provenance.json")

        # === 10. Obsidian sync ===
        if os.getenv("OBSIDIAN_ENABLED", "false").lower() == "true":
            sync_to_obsidian(contract, task_id, evidence_hashes, "success")

    except Exception as e:
        # Failure state
        atomic_write_json(state_file, {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
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

        execution_result = {
            "status": status,
            "evidence_hashes": evidence_hashes,
            "git_commits": []
        }

        devlog_path = create_devlog(contract, execution_result)
        print(f"   📝 Obsidian devlog: {devlog_path.name}")

        if status == "success":
            append_evidence(task_id, list(evidence_hashes.keys()), evidence_hashes)
            print(f"   📎 Evidence synced to Obsidian")

        return True

    except ImportError as e:
        print(f"   ⚠️  Obsidian bridge not available: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  Obsidian sync failed: {e}")
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
        changed_files = [line.strip().split(" ", 1)[1] for line in result.stdout.strip().split('\n') if line.strip()]
        
        if not changed_files:
            print("No changed files detected. Nothing to record. Aborting.")
            return

        print(f"   Found {len(changed_files)} changed file(s).")

        # 3. Create a lightweight, in-memory contract
        task_id = f"LITE-{datetime.now(datetime.UTC).strftime('%Y%m%d-%H%M%S')}"
        lite_contract = {
            "task_id": task_id,
            "title": task_title,
            "project": "PROJECT_NAME", # This will be replaced by setup.py
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

        print(f"\n✅ Lite task '{task_title}' recorded successfully.")

    except Exception as e:
        print(f"\n❌ Error in Lite Mode: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TaskExecutor v3.2.1")
    parser.add_argument("contract", nargs='?', default=None, help="Path to YAML contract file. If omitted, runs in Lite Mode.")
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
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
