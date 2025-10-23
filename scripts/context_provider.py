"""Context provider for C7-Sync framework.

Loads master configuration plus allowed environment variables and emits a unified
context object along with a deterministic context hash. Designed to be called
by every agent session (L1-L7 compliance).

Usage examples::

    python scripts/context_provider.py get-context
    python scripts/context_provider.py print-hash
    python scripts/context_provider.py diagnose
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable

ROOT = Path(__file__).resolve().parent.parent
MASTER_CONFIG_PATH = ROOT / "config" / "master_config.json"
ENV_PATH = ROOT / ".env"

# Environment keys that are safe to share across agents. Secrets should stay in .env only.
ENV_ALLOWLIST = {
    "OBSIDIAN_VAULT_PATH",
    "OBSIDIAN_ENABLED",
    "PROJECT_NAME",
}


@dataclass
class ContextBundle:
    data: Dict[str, Any]
    context_hash: str


def load_master_config() -> Dict[str, Any]:
    if not MASTER_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"master_config.json not found at {MASTER_CONFIG_PATH}. " "Create it to define the single source of truth."
        )

    try:
        return json.loads(MASTER_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {MASTER_CONFIG_PATH}: {exc}") from exc


def parse_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}

    env_map: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_map[key.strip()] = value.strip().strip('"')
    return env_map


def build_context() -> ContextBundle:
    master = load_master_config()
    env_file = parse_env_file(ENV_PATH)

    env_allowed = {key: env_file.get(key) for key in ENV_ALLOWLIST if key in env_file}

    # version bump when schema changes
    bundle = {
        "schema": master.get("sync", {}).get("context_schema_version", "c7-sync-1.0"),
        "master_config": master,
        "env": env_allowed,
    }
    context_hash = sha256(json.dumps(bundle, sort_keys=True).encode("utf-8")).hexdigest()
    return ContextBundle(bundle, context_hash)


def print_json(data: Dict[str, Any]):
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def ensure_context_keys(bundle: ContextBundle) -> Iterable[str]:
    missing = []
    required = bundle.data.get("master_config", {}).get("sync", {}).get("required_env_keys", [])
    env = bundle.data.get("env", {})
    for key in required:
        if key not in env or env[key] in {None, ""}:
            missing.append(key)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="C7-Sync context provider")
    parser.add_argument(
        "command",
        choices=["get-context", "print-hash", "diagnose"],
        help="Action to perform",
    )
    args = parser.parse_args()

    try:
        bundle = build_context()
    except Exception as exc:  # pragma: no cover - intentionally broad for CLI
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    if args.command == "get-context":
        print_json({"context": bundle.data, "context_hash": bundle.context_hash})
        missing = ensure_context_keys(bundle)
        if missing:
            sys.stderr.write(f"[WARN] Missing required env keys: {', '.join(missing)}\n")
        return 0

    if args.command == "print-hash":
        print(bundle.context_hash)
        return 0

    if args.command == "diagnose":
        print("Context hash:", bundle.context_hash)
        print("Master config:", MASTER_CONFIG_PATH)
        print(".env path:", ENV_PATH if ENV_PATH.exists() else "(missing)")
        missing = ensure_context_keys(bundle)
        if missing:
            print("Missing env keys:", ", ".join(missing))
        else:
            print("All required env keys present.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
