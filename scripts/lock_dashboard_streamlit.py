#!/usr/bin/env python3
"""Streamlit dashboard for viewing lock status and potential conflicts."""

from __future__ import annotations

import streamlit as st
from agent_sync import get_active_locks, detect_conflicts

st.set_page_config(page_title="Collaboration Lock Dashboard", layout="wide")
st.title("Collaboration Lock Dashboard")

locks = get_active_locks()

with st.expander("Active Locks", expanded=True):
    if not locks:
        st.success("No active locks recorded.")
    else:
        by_agent: dict[str, list[dict]] = {}
        for entry in locks:
            by_agent.setdefault(entry.get("agent_id", "<unknown>"), []).append(entry)
        for agent, entries in sorted(by_agent.items()):
            st.subheader(f"Agent: {agent} ({len(entries)} file(s))")
            st.table(
                {
                    "file": [lock.get("file", "") for lock in entries],
                    "task": [lock.get("task_id", "") for lock in entries],
                    "locked_at": [lock.get("locked_at", "") for lock in entries],
                }
            )

st.markdown("---")
st.header("Conflict Check")

with st.form("conflict_form"):
    agent_id = st.text_input("Your agent id", value="codex")
    task_id = st.text_input("Your task id", value="")
    files_text = st.text_area("Files to check (one per line)", value="")
    submitted = st.form_submit_button("Check conflicts")

if submitted:
    files = [line.strip() for line in files_text.splitlines() if line.strip()]
    conflicts = detect_conflicts(agent_id, task_id, files)
    if not conflicts:
        st.success("No conflicts detected for the requested files.")
    else:
        st.error("Conflicts detected:")
        st.table(
            {
                "file": [lock.get("file", "") for lock in conflicts],
                "agent": [lock.get("agent_id", "") for lock in conflicts],
                "task": [lock.get("task_id", "") for lock in conflicts],
                "locked_at": [lock.get("locked_at", "") for lock in conflicts],
            }
        )

st.markdown("---")
st.caption("Run with: streamlit run scripts/lock_dashboard_streamlit.py")
