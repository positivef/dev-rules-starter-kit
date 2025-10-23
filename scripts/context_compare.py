"""Compare legacy context loading vs C7-Sync bundle.

Legacy approach approximates the pre-C7 method (direct .env + ad-hoc files),
while the C7 path relies on `context_provider` to build a unified bundle.

Usage::

    python3 scripts/context_compare.py report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from context_provider import build_context, parse_env_file

ROOT = Path(__file__).resolve().parent.parent
LEGACY_SOURCES = {
    "env": ROOT / ".env",
    "dev_context_metadata": ROOT / "dev-context" / "metadata.json",
    "dev_context_product": ROOT / "dev-context" / "product.md",
}


def load_legacy_snapshot() -> dict:
    env = parse_env_file(LEGACY_SOURCES["env"])
    metadata_path = LEGACY_SOURCES["dev_context_metadata"]
    metadata = {}
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata = {"error": "metadata.json not valid JSON"}

    snapshot = {
        "schema": "legacy-env-1.0",
        "env": env,
        "metadata": metadata,
        "notes": "Legacy snapshot aggregates .env and dev-context metadata only.",
    }
    return snapshot


def compare() -> dict:
    legacy = load_legacy_snapshot()
    c7_bundle = build_context()
    result = {
        "legacy": legacy,
        "c7": {
            "context": c7_bundle.data,
            "context_hash": c7_bundle.context_hash,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare legacy context vs C7")
    parser.add_argument("command", choices=["report"], help="Action to perform")
    args = parser.parse_args()

    if args.command == "report":
        data = compare()
        json.dump(data, fp=sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
