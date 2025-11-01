"""Lightweight agent sync board for the C7-Sync framework.

Tracks each agent's declared focus and context hash so humans can verify that
all participants share the same configuration.

Usage examples::

    python scripts/multi_agent_sync.py update-status codex "Implement feature" --context-hash abcd
    python scripts/multi_agent_sync.py list
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "dev-context" / "agent_sync_state.json"
_LATEST_LOCKS: list[dict] = []


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentStatus:
    agent: str
    focus: str
    context_hash: str
    updated_at: str
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "AgentStatus":
        return cls(
            agent=data["agent"],
            focus=data["focus"],
            context_hash=data["context_hash"],
            updated_at=data["updated_at"],
            notes=data.get("notes"),
        )


def _read_state() -> dict:
    if not STATE_FILE.exists():
        return {"agents": [], "locks": []}
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"agents": [], "locks": []}
    if isinstance(raw, list):
        return {"agents": raw, "locks": []}
    if isinstance(raw, dict):
        agents = raw.get("agents", [])
        locks = raw.get("locks", [])
        if not isinstance(agents, list):
            agents = []
        if not isinstance(locks, list):
            locks = []
        return {"agents": agents, "locks": locks}
    return {"agents": [], "locks": []}


def load_state() -> Dict[str, AgentStatus]:
    raw = _read_state()
    agents_payload = raw.get("agents", [])
    if isinstance(agents_payload, dict):
        agents_payload = []
    state: Dict[str, AgentStatus] = {}
    for item in agents_payload:
        try:
            state[item["agent"]] = AgentStatus.from_dict(item)
        except KeyError:
            continue
    global _LATEST_LOCKS
    _LATEST_LOCKS = raw.get("locks", []) if isinstance(raw.get("locks"), list) else []
    return state


def save_state(state: Dict[str, AgentStatus]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(status) for status in state.values()]
    raw_state = {"agents": payload, "locks": _LATEST_LOCKS}
    STATE_FILE.write_text(json.dumps(raw_state, indent=2, ensure_ascii=False), encoding="utf-8")


def fmt_status(status: AgentStatus) -> str:
    notes_part = f" | notes: {status.notes}" if status.notes else ""
    return (
        f"{status.agent:10s} | focus: {status.focus:25s} | hash: {status.context_hash}"
        f" | updated: {status.updated_at}{notes_part}"
    )


def run_update(args: argparse.Namespace) -> int:
    state = load_state()
    state[args.agent] = AgentStatus(
        agent=args.agent,
        focus=args.focus,
        context_hash=args.context_hash,
        updated_at=utc_now(),
        notes=args.notes,
    )
    save_state(state)
    print(f"[OK] Updated {args.agent} with context hash {args.context_hash}")
    return 0


def run_list(_: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        print("No agent status recorded yet.")
        return 0
    print("Agent sync board:")
    for status in state.values():
        print(" -", fmt_status(status))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="C7-Sync agent board")
    sub = parser.add_subparsers(dest="command", required=True)

    update = sub.add_parser("update-status", help="Record agent state")
    update.add_argument("agent", help="Agent identifier (e.g., codex, claude, gemini)")
    update.add_argument("focus", help="Current focus area")
    update.add_argument("context_hash", help="Context hash reported by context_provider")
    update.add_argument("--notes", help="Optional notes", default=None)
    update.set_defaults(func=run_update)

    list_cmd = sub.add_parser("list", help="Show current statuses")
    list_cmd.set_defaults(func=run_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
