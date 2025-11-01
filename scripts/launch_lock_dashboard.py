#!/usr/bin/env python3
"""Helper to launch or stop the Streamlit lock dashboard."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

DASHBOARD_PATH = os.path.join("scripts", "lock_dashboard_streamlit.py")


def launch(port: int) -> int:
    cmd = [sys.executable, "-m", "streamlit", "run", DASHBOARD_PATH, "--server.port", str(port)]
    print("[INFO] Launching Streamlit dashboard...")
    print("[CMD]", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the lock dashboard (Streamlit)")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the dashboard")
    args = parser.parse_args()
    return launch(args.port)


if __name__ == "__main__":
    raise SystemExit(main())
