"""Utility helpers for lightweight notifications.

The helpers degrade gracefully when webhooks are not configured so they can be
used in local development without additional setup.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def send_slack_notification(message: str, *, webhook_env: str = "SLACK_WEBHOOK_URL") -> bool:
    """Send a Slack webhook message.

    Returns ``True`` if the message was delivered, ``False`` otherwise. Errors
    are logged to stderr but do not raise exceptions so that notification
    failures never stop the main execution flow.
    """

    url = os.getenv(webhook_env)
    if not url:
        print(f"[INFO] Slack webhook env '{webhook_env}' not set. Skipping notification.")
        return False

    payload = {"text": message}
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=5):
            return True
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        print(f"[WARN] Slack notification failed: {exc}", file=sys.stderr)
        return False


__all__ = ["send_slack_notification"]
