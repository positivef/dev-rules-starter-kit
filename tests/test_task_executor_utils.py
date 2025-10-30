import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from task_executor import write_lessons_template, write_prompt_feedback


def test_write_lessons_template_creates_file(tmp_path):
    runs_dir = tmp_path / "RUNS" / "TASK-001"
    runs_dir.mkdir(parents=True)
    contract = {"task_id": "TASK-001", "project": "demo"}

    write_lessons_template(runs_dir, contract, status="success")

    lessons_path = runs_dir / "lessons.md"
    assert lessons_path.exists()

    content = lessons_path.read_text(encoding="utf-8")
    assert "#lesson #demo" in content
    assert "## Summary" in content

    # running twice should keep existing file (idempotent)
    write_lessons_template(runs_dir, contract, status="success")
    content2 = lessons_path.read_text(encoding="utf-8")
    assert content == content2


def test_write_prompt_feedback_generates_summary(tmp_path):
    runs_dir = tmp_path / "RUNS" / "TASK-OPT"
    runs_dir.mkdir(parents=True)

    stats = [
        {
            "command_id": "cmd1",
            "context": "initial prompt",
            "original_tokens": 120,
            "compressed_tokens": 60,
            "savings_pct": 50.0,
            "rules_applied": 3,
        },
        {
            "command_id": "cmd2",
            "context": "secondary prompt",
            "error": "compression failed",
        },
    ]

    write_prompt_feedback(runs_dir, stats)

    feedback_path = runs_dir / "prompt_feedback.json"
    assert feedback_path.exists()

    data = json.loads(feedback_path.read_text(encoding="utf-8"))
    assert data["summary"]["total_prompts"] == 1
    assert data["summary"]["total_original_tokens"] == 120
    assert data["top_prompt"]["command_id"] == "cmd1"
    assert len(data.get("errors", [])) == 1
