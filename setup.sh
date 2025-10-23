#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: ./setup.sh --project-name <name> [--framework <framework>]

Wrapper around setup.py to scaffold the Dev Rules Starter Kit with a single command.

Options:
  --project-name  Name of the project to replace the PROJECT_NAME placeholder (required)
  --framework     Optional framework template to merge (matches directories under templates/)
  --python-bin    Override Python executable (default: python3, falling back to python)
  -h, --help      Show this message
USAGE
}

PROJECT_NAME=""
FRAMEWORK=""
PYTHON_BIN_OPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      shift || { echo "[ERROR] Missing value for --project-name" >&2; exit 1; }
      PROJECT_NAME="$1"
      ;;
    --framework)
      shift || { echo "[ERROR] Missing value for --framework" >&2; exit 1; }
      FRAMEWORK="$1"
      ;;
    --python-bin)
      shift || { echo "[ERROR] Missing value for --python-bin" >&2; exit 1; }
      PYTHON_BIN_OPT="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[WARN] Ignoring unknown argument: $1" >&2
      ;;
  esac
  shift
done

if [[ -z "$PROJECT_NAME" ]]; then
  echo "[ERROR] --project-name is required" >&2
  usage
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "$PYTHON_BIN_OPT" ]]; then
  PYTHON_CMD="$PYTHON_BIN_OPT"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "[ERROR] python3 or python is required to run setup.py" >&2
  exit 1
fi

ARGS=("$PYTHON_CMD" "$SCRIPT_DIR/setup.py" "--project-name" "$PROJECT_NAME")
if [[ -n "$FRAMEWORK" ]]; then
  ARGS+=("--framework" "$FRAMEWORK")
fi

echo "[SETUP] Running ${ARGS[*]}"
"${ARGS[@]}"
