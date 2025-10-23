#!/usr/bin/env python3
"""
Obsidian Bridge - Executable Knowledge System Integration
Dev Rules Starter Kit

Features:
- Auto-generate dev logs on task execution
- Auto-update evidence in Obsidian
- Auto-update TASKS/ checklist
- Auto-update MOC knowledge map
- 95% time savings (20min → 3sec)

Usage:
  # Automatic (called by TaskExecutor)
  python scripts/task_executor.py TASKS/FEAT-YYYY-MM-DD-XX.yaml

  # Manual
  from obsidian_bridge import create_devlog, append_evidence
"""

import os
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class ObsidianBridge:
    """Obsidian integration bridge"""

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Args:
            vault_path: Obsidian Vault path (default: from environment)
        """
        self.vault_path = vault_path or Path(os.getenv("OBSIDIAN_VAULT_PATH", "."))
        self.devlog_dir = self.vault_path / "개발일지"
        self.tasks_dir = self.vault_path / "TASKS"
        self.moc_path = self.vault_path / "MOCs" / "PROJECT_NAME_개발_지식맵.md"

    def create_devlog(self, task_contract: Dict, execution_result: Dict) -> Path:
        """
        Auto-generate dev log after task execution

        Args:
            task_contract: Task contract (YAML)
            execution_result: Execution result

        Returns:
            Path to generated dev log
        """
        task_id = task_contract["task_id"]
        title = task_contract["title"]
        status = execution_result.get("status", "unknown")
        today = datetime.now().strftime("%Y-%m-%d")

        # Generate filename
        safe_title = title.replace(" ", "_").replace("/", "_")
        filename = f"{today}_{safe_title}.md"
        filepath = self.devlog_dir / filename

        # Generate frontmatter
        frontmatter = {
            "date": today,
            "project": "[[PROJECT_NAME Development]]",
            "tags": ["devlog", task_contract.get("tags", []), f"task-{task_id}", f"status-{status}"],
            "status": status,
            "task_id": task_id,
            "type": task_contract.get("type", "feature"),
            "impact": task_contract.get("priority", "medium"),
            "git_commits": execution_result.get("git_commits", []),
            "related": ["[[PROJECT_NAME Development]]", f"[[{task_id}]]"],
        }

        # Flatten tags
        tags = []
        for tag in frontmatter["tags"]:
            if isinstance(tag, list):
                tags.extend(tag)
            else:
                tags.append(tag)
        frontmatter["tags"] = list(set(tags))

        # Generate content
        content = self._generate_devlog_content(task_contract, execution_result, frontmatter)

        # Write file
        self.devlog_dir.mkdir(parents=True, exist_ok=True)
        filepath.write_text(self._format_markdown(frontmatter, content), encoding="utf-8")

        return filepath

    def update_task_checklist(self, task_id: str, checklist_updates: Dict):
        """
        Update TASKS/ checklist

        Args:
            task_id: Task ID
            checklist_updates: Checklist updates
        """
        task_file = self.tasks_dir / f"{task_id}.md"

        if not task_file.exists():
            self._create_task_file(task_id, checklist_updates)
        else:
            self._update_task_file(task_file, checklist_updates)

    def update_moc(self, updates: Dict):
        """
        Update MOC knowledge map

        Args:
            updates: Update content
        """
        if not self.moc_path.exists():
            return

        content = self.moc_path.read_text(encoding="utf-8")

        # Update date
        today = datetime.now().strftime("%Y-%m-%d")
        content = content.replace(f"updated: {datetime.now().strftime('%Y-%m-%d')}", f"updated: {today}")

        self.moc_path.write_text(content, encoding="utf-8")

    def append_evidence_to_contract(self, task_id: str, evidence_files: List[str], evidence_hashes: Dict[str, str]):
        """
        Append evidence to task contract

        Args:
            task_id: Task ID
            evidence_files: Evidence file list
            evidence_hashes: SHA-256 hash dictionary
        """
        repo_tasks_dir = Path("TASKS")
        contract_files = list(repo_tasks_dir.glob(f"{task_id}*.yaml"))

        if not contract_files:
            return

        contract_file = contract_files[0]
        contract = yaml.safe_load(contract_file.read_text(encoding="utf-8"))

        # Update provenance
        if "provenance" not in contract:
            contract["provenance"] = {}

        contract["provenance"]["evidence_sha256"] = evidence_hashes
        contract["provenance"]["executed_at"] = datetime.now(timezone.utc).isoformat()
        contract["provenance"]["executor"] = "TaskExecutor-v3.2.1"

        # Update status
        contract["status"] = "completed"
        contract["completion_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Write file
        contract_file.write_text(yaml.dump(contract, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def _generate_devlog_content(self, contract: Dict, result: Dict, frontmatter: Dict) -> str:
        """Generate dev log content"""
        task_id = contract["task_id"]
        title = contract["title"]
        status = result.get("status", "unknown")

        status_icon = "✅" if status == "success" else "❌"

        content = f"""# {datetime.now(timezone.utc).strftime('%Y-%m-%d')} {title}

## 📌 Today's Summary

> [!{"success" if status == "success" else "failure"}] Execution Result
> Task ID: `{task_id}` - {status_icon} {status.upper()}

## 🎯 Task Objective

{contract.get('description', title)}

## ✅ Acceptance Criteria

"""
        for criterion in contract.get("acceptance_criteria", []):
            content += f"- [ ] {criterion}\n"

        content += """
## 🔧 Execution Details

### Commands
```bash
"""
        for cmd in contract.get("commands", []):
            exec_info = cmd.get("exec", {})
            content += f"# {cmd['id']}\n"
            content += f"{exec_info.get('cmd')} {' '.join(exec_info.get('args', []))}\n"

        content += """```

### Quality Gates
"""
        for gate in contract.get("gates", []):
            content += f"- [{'x' if status == 'success' else ' '}] {gate['id']}\n"

        # Evidence files
        evidence_hashes = result.get("evidence_hashes", {})
        if evidence_hashes:
            content += "\n## 📊 Evidence Files\n\n"
            for file_path, hash_value in evidence_hashes.items():
                content += f"- `{file_path}`: `{hash_value[:16]}...`\n"

        # Git commits
        if result.get("git_commits"):
            content += "\n## 📝 Git Commits\n\n"
            for commit in result["git_commits"]:
                content += f"- `{commit}`\n"

        content += f"""
---

**Status**: {status_icon} {status.upper()}
"""

        return content

    def _format_markdown(self, frontmatter: Dict, content: str) -> str:
        """Format Markdown file (frontmatter + content)"""
        yaml_front = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_front}---\n\n{content}"

    def _create_task_file(self, task_id: str, data: Dict):
        """Create new task file"""
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.tasks_dir / f"{task_id}.md"

        frontmatter = {
            "project": "[[PROJECT_NAME Development]]",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "status": data.get("status", "pending"),
            "task_id": task_id,
            "tags": ["task", task_id.split("-")[0].lower()],
        }

        content = f"# {task_id}\n\n{data.get('description', '')}\n"

        filepath.write_text(self._format_markdown(frontmatter, content), encoding="utf-8")

    def _update_task_file(self, filepath: Path, updates: Dict):
        """Update existing task file"""
        content = filepath.read_text(encoding="utf-8")

        # Simple checkbox update
        for key, value in updates.items():
            if key.startswith("checkbox_"):
                pattern = key.replace("checkbox_", "")
                if value:
                    content = content.replace(f"- [ ] {pattern}", f"- [x] {pattern}")
                else:
                    content = content.replace(f"- [x] {pattern}", f"- [ ] {pattern}")

        filepath.write_text(content, encoding="utf-8")


# Global instance
obsidian_bridge = ObsidianBridge()


# Convenience functions
def create_devlog(task_contract: Dict, execution_result: Dict) -> Path:
    """Create dev log"""
    return obsidian_bridge.create_devlog(task_contract, execution_result)


def update_task_checklist(task_id: str, checklist_updates: Dict):
    """Update task checklist"""
    return obsidian_bridge.update_task_checklist(task_id, checklist_updates)


def append_evidence(task_id: str, evidence_files: List[str], evidence_hashes: Dict[str, str]):
    """Append evidence files"""
    return obsidian_bridge.append_evidence_to_contract(task_id, evidence_files, evidence_hashes)
