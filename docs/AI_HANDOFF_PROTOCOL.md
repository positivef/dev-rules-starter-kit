# AI Agent Handoff Protocol

## 1. Purpose

This document outlines the mandatory protocol for handing off work between AI agents (e.g., Gemini, Claude Code) within this project. The purpose of this protocol is to:

- **Prevent context mismatch:** Ensure the receiving agent has the most up-to-date understanding of the codebase.
- **Avoid conflicts:** Eliminate the risk of overwriting changes or performing redundant work.
- **Ensure traceability:** Maintain a clear, auditable history of all work performed and handed off.
- **Fulfill Constitution Principle P2 (Evidence-Based Development) and P3 (Knowledge Asset).**

Adherence to this protocol is not optional; it is a core rule of our development process.

## 2. The Handoff Tool

The primary tool for this protocol is `scripts/create_handoff_report.py`.

This script automatically gathers metadata (commit hash, modified files, context hash) and combines it with agent-provided summaries to generate a standardized `HANDOFF_REPORT.md` file.

## 3. Workflow for the Sending Agent (e.g., Gemini)

Follow these steps **every time** you complete a task and before the next agent begins its work.

### Step 1: Complete Your Task
Make all necessary code modifications to fulfill your assigned task.

### Step 2: Run Verifications
Run all relevant tests and validations to ensure your changes have not introduced any regressions. This must include, at a minimum:
- `pytest`
- `ruff check .`
- Any other constitutional validators relevant to your changes.

### Step 3: Commit Your Changes
Create a single, atomic commit containing all your changes. The commit message **must** follow the Conventional Commits standard.

```bash
git add .
git commit -m "feat(handoff): create script to generate handoff reports"
```

### Step 4: Generate the Handoff Report
Execute the `create_handoff_report.py` script with the following arguments. This is the most critical step in the handoff process.

```bash
python scripts/create_handoff_report.py \
  --author "Your Agent Name (e.g., Gemini)" \
  --summary "A high-level summary of what you accomplished in this work cycle." \
  --test-results "A concise summary of the verification results from Step 2. Example: 'pytest: 152/152 tests passed. ruff: No errors found.'" \
  --instructions "Clear, direct, and actionable instructions for the next agent. State what they should work on next and what they need to know."
```

### Step 5: Verify Report Generation
The script will create/update two files:
1.  `./HANDOFF_REPORT.md`: The current, live report for the next agent.
2.  `./RUNS/handoffs/HANDOFF_{timestamp}.md`: A permanent, archived copy for historical records.

## 4. Workflow for the Receiving Agent (e.g., Claude Code)

Your work cycle **must** begin with the following steps.

### Step 1: Read the Handoff Report
Your first action is to read and fully parse the contents of the root `HANDOFF_REPORT.md` file. Do not proceed until you have this information.

### Step 2: Synchronize Your Context
From the report, understand:
- What was just changed.
- The latest commit hash that represents the new "source of truth".
- The context hash defining the state of the project.
- The results of the last test runs.
- Your specific instructions.

### Step 3: Update Your Local Environment
Ensure your local codebase is synchronized to the latest commit specified in the report.

```bash
git pull
# Or git checkout [commit_hash_from_report]
```

### Step 4: Begin Your Task
You may now safely begin working on the task outlined in the "Instructions for Next Agent" section of the report.

## 5. Important Notes & Troubleshooting

### Note for Windows Users: Character Encoding

When passing arguments with non-ASCII characters (e.g., Korean) to the script on Windows, the text may appear garbled due to terminal encoding issues. The script itself writes the report in UTF-8 correctly, but the input from the shell can be misinterpreted.

To prevent this, choose one of the following solutions:

1.  **(Recommended) Use English for Arguments:** Pass all command-line arguments (`--summary`, `--instructions`, etc.) in English.
2.  **Change Code Page:** Before running the script, change your terminal's code page to UTF-8 by executing the command `chcp 65001`.

### Preflight Automation (2025-10-29)
- 실행 전 python scripts/preflight_checks.py를 수행해 Enhanced Executor 및 Handoff 테스트를 통과했는지 확인합니다.
- 잠금 충돌 여부는 python scripts/agent_sync_status.py --agent <you> --files <paths>로 사전에 점검합니다.
