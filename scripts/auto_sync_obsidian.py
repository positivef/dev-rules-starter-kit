#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obsidian Auto-Sync - Automatic Development Log Generator

Automatically syncs development work to Obsidian based on Git activity.
Implements OBSIDIAN_SYNC_RULES.md automation.

Triggers:
- 3+ files changed
- New feature implementation
- Bug fixes (MEDIUM+ severity)
- Refactoring work

Usage:
  python scripts/auto_sync_obsidian.py  # Auto-detect from git
  python scripts/auto_sync_obsidian.py --force  # Force sync

Called by: .git/hooks/post-commit (automatic)
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_last_commit_info() -> Optional[Dict[str, any]]:
    """Get last commit information"""
    try:
        # Get commit message
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, encoding="utf-8", check=True
        )
        commit_message = result.stdout.strip()

        # Get commit hash
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%H"], capture_output=True, text=True, encoding="utf-8", check=True
        )
        commit_hash = result.stdout.strip()[:8]

        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD"], capture_output=True, text=True, encoding="utf-8", check=True
        )
        changed_files = [f for f in result.stdout.strip().split("\n") if f]

        # Get file stats
        result = subprocess.run(
            ["git", "diff", "--shortstat", "HEAD~1..HEAD"], capture_output=True, text=True, encoding="utf-8", check=True
        )
        stats = result.stdout.strip()

        return {
            "message": commit_message,
            "hash": commit_hash,
            "files": changed_files,
            "stats": stats,
            "file_count": len(changed_files),
        }

    except subprocess.CalledProcessError:
        # Initial commit or no previous commit
        return None
    except Exception as e:
        print(f"[WARN] Failed to get commit info: {e}")
        return None


def should_sync(commit_info: Dict[str, any], force: bool = False) -> Tuple[bool, str]:
    """Check if sync is needed based on OBSIDIAN_SYNC_RULES.md

    Returns:
        (should_sync, reason)
    """
    if force:
        return True, "Force sync requested"

    if not commit_info:
        return False, "No commit info available"

    file_count = commit_info["file_count"]
    message = commit_info["message"].lower()

    # Trigger 1: 3+ files changed
    if file_count >= 3:
        return True, f"{file_count} files changed (>= 3)"

    # Trigger 2: Feature implementation
    if any(keyword in message for keyword in ["feat:", "feature:", "implement", "add"]):
        return True, "Feature implementation detected"

    # Trigger 3: Bug fix
    if any(keyword in message for keyword in ["fix:", "bug:", "resolve"]):
        return True, "Bug fix detected"

    # Trigger 4: Refactoring
    if any(keyword in message for keyword in ["refactor:", "refactoring", "cleanup"]):
        return True, "Refactoring detected"

    # Trigger 5: Documentation/Analysis
    if any(keyword in message for keyword in ["docs:", "analyze", "analysis"]):
        return True, "Documentation/Analysis work detected"

    return False, "No sync trigger matched"


def categorize_work(commit_info: Dict[str, any]) -> str:
    """Categorize the type of work done"""
    message = commit_info["message"].lower()

    if "feat:" in message or "feature:" in message:
        return "feature"
    elif "fix:" in message or "bug:" in message:
        return "bugfix"
    elif "refactor:" in message:
        return "refactor"
    elif "docs:" in message:
        return "documentation"
    elif "test:" in message:
        return "testing"
    elif "chore:" in message:
        return "chore"
    else:
        return "general"


def extract_commit_type(commit_msg: str) -> Optional[str]:
    """Extract conventional commit type (feat, fix, test, etc.)"""
    match = re.match(r"^(feat|fix|test|docs|refactor|chore|style|perf|build|ci):", commit_msg, re.IGNORECASE)
    return match.group(1).lower() if match else None


def parse_stats(stats_str: str) -> Dict[str, int]:
    """Parse git diff stats string

    Example: "3 files changed, 571 insertions(+), 12 deletions(-)"
    Returns: {"files_changed": 3, "insertions": 571, "deletions": 12}
    """
    result = {"files_changed": 0, "insertions": 0, "deletions": 0}

    if not stats_str:
        return result

    # Extract numbers
    files_match = re.search(r"(\d+)\s+files?\s+changed", stats_str)
    insertions_match = re.search(r"(\d+)\s+insertions?", stats_str)
    deletions_match = re.search(r"(\d+)\s+deletions?", stats_str)

    if files_match:
        result["files_changed"] = int(files_match.group(1))
    if insertions_match:
        result["insertions"] = int(insertions_match.group(1))
    if deletions_match:
        result["deletions"] = int(deletions_match.group(1))

    return result


def extract_tags_from_commit(commit_info: Dict[str, any]) -> List[str]:
    """Extract tags from commit info for YAML frontmatter

    Generates hierarchical tags like:
    - type/feature, type/fix
    - domain/testing, domain/obsidian
    - status/completed
    """
    tags = []
    message = commit_info["message"]
    files = commit_info.get("files", [])

    # Type tag
    commit_type = extract_commit_type(message)
    if commit_type:
        tags.append(f"type/{commit_type}")

    # Domain tags from file paths
    has_test = any("test" in f.lower() for f in files)
    has_docs = any(".md" in f for f in files)
    has_scripts = any("scripts/" in f for f in files)
    has_config = any(f.endswith((".yaml", ".yml", ".json", ".toml")) for f in files)

    if has_test:
        tags.append("domain/testing")
    if has_docs:
        tags.append("domain/documentation")
    if has_scripts:
        tags.append("domain/scripts")
    if has_config:
        tags.append("domain/config")

    # Specific domain detection
    if any("obsidian" in f.lower() for f in files):
        tags.append("domain/obsidian")
    if any("q1" in message.lower() or "q1-2026" in message.lower()):
        tags.append("project/q1-2026")
    if any("strategy" in f.lower() for f in files) or "strategy" in message.lower():
        tags.append("project/strategy-b")

    # Status tag (always completed for post-commit)
    tags.append("status/completed")

    return tags


def generate_yaml_frontmatter(commit_info: Dict[str, any]) -> str:
    """Generate YAML frontmatter with metadata for Dataview queries

    Returns YAML block with date, time, project, topic, tags, and stats
    """
    now = datetime.now()
    topic = extract_topic_from_commit(commit_info["message"])
    tags = extract_tags_from_commit(commit_info)
    stats = parse_stats(commit_info["stats"])
    work_type = categorize_work(commit_info)

    # Extract phase if present
    phase_match = re.search(r"[Pp]hase\s+(\d+)", commit_info["message"])
    phase = int(phase_match.group(1)) if phase_match else None

    # Extract project from topic or message
    project = topic.replace("-", " ")

    # Build YAML
    yaml_lines = [
        "---",
        f'date: {now.strftime("%Y-%m-%d")}',
        f'time: "{now.strftime("%H:%M")}"',
        f'project: "{project}"',
        f'topic: "{topic}"',
        f'commit: "{commit_info["hash"]}"',
        f"type: {work_type}",
    ]

    if phase:
        yaml_lines.append(f"phase: {phase}")

    yaml_lines.extend(
        [
            "status: completed",
            f"tags: [{', '.join(tags)}]",
            f"files_changed: {stats['files_changed']}",
            f"lines_added: {stats['insertions']}",
            f"lines_deleted: {stats['deletions']}",
            "---",
        ]
    )

    return "\n".join(yaml_lines)


def extract_key_changes(commit_info: Dict[str, any]) -> List[str]:
    """Extract key changes from commit"""
    changes = []

    files = commit_info["files"]

    # Categorize files
    scripts = [f for f in files if f.startswith("scripts/") and f.endswith(".py")]
    tests = [f for f in files if f.startswith("tests/") and f.endswith(".py")]
    docs = [f for f in files if f.endswith(".md")]
    configs = [f for f in files if f.endswith((".yaml", ".yml", ".json", ".toml"))]
    workflows = [f for f in files if ".github/workflows" in f]

    if scripts:
        changes.append(f"스크립트 {len(scripts)}개 수정: {', '.join([Path(f).name for f in scripts[:3]])}")
    if tests:
        changes.append(f"테스트 {len(tests)}개 수정: {', '.join([Path(f).name for f in tests[:3]])}")
    if docs:
        changes.append(f"문서 {len(docs)}개 수정: {', '.join([Path(f).name for f in docs[:3]])}")
    if configs:
        changes.append(f"설정 파일 {len(configs)}개 수정")
    if workflows:
        changes.append(f"CI/CD 워크플로우 {len(workflows)}개 수정")

    return changes


def generate_devlog_content(commit_info: Dict[str, any]) -> str:
    """Generate development log content with YAML frontmatter"""
    today = datetime.now().strftime("%Y-%m-%d")
    work_type = categorize_work(commit_info)
    key_changes = extract_key_changes(commit_info)

    # Parse commit message
    commit_lines = commit_info["message"].split("\n")
    title = commit_lines[0]
    description = "\n".join(commit_lines[1:]).strip() if len(commit_lines) > 1 else ""

    # Generate YAML frontmatter
    yaml_frontmatter = generate_yaml_frontmatter(commit_info)

    content = f"""{yaml_frontmatter}

# {today} {title}

## [TASK] 오늘의 작업

### 커밋 정보
- **커밋 해시**: `{commit_info["hash"]}`
- **작업 유형**: {work_type}
- **변경 파일 수**: {commit_info["file_count"]}개
- **통계**: {commit_info["stats"]}

### 주요 변경사항
"""

    for change in key_changes:
        content += f"- {change}\n"

    if description:
        content += f"\n### 상세 설명\n{description}\n"

    content += f"""
## [TIP] 배운 점 & 인사이트

### 성공 사례
- [자동 생성됨] 커밋 완료 및 옵시디언 자동 동기화 성공

### 개선 필요 영역
- TODO: 회고 내용 추가

## 🔧 시행착오 및 해결

- TODO: 문제와 해결 과정 기록

## 📋 다음 단계

### 즉시 수행
- [ ] 코드 리뷰 요청
- [ ] 테스트 실행 확인

### 단기 (1-2일)
- [ ] TODO

### 장기 (1주일+)
- [ ] TODO

## 🔗 관련 링크

- 커밋: `{commit_info["hash"]}`
- 변경 파일:
"""

    for file in commit_info["files"][:10]:
        content += f"  - `{file}`\n"

    if len(commit_info["files"]) > 10:
        content += f"  - ... 외 {len(commit_info["files"]) - 10}개\n"

    content += f"""
---
**태그**: #{work_type} #자동동기화
**카테고리**: 개발일지
**우선순위**: MEDIUM
**자동 생성**: post-commit hook
"""

    return content


def extract_topic_from_commit(commit_msg: str) -> str:
    """Extract topic from commit message for file grouping

    Examples:
        "test: add Q1 2026 test infrastructure Phase 1" -> "Q1-Test-Infrastructure"
        "feat: implement user authentication" -> "User-Authentication"
        "fix: resolve login bug" -> "Login-Bug-Fix"
    """
    # Remove conventional commit prefix (feat:, test:, fix:, etc.)
    msg = re.sub(r"^(feat|fix|test|docs|refactor|chore|style|perf|build|ci):\s*", "", commit_msg, flags=re.IGNORECASE)

    # Remove phase indicators
    msg = re.sub(r"\s+[Pp]hase\s+\d+", "", msg)
    msg = re.sub(r"\s+-\s+[Pp]hase\s+\d+", "", msg)

    # Extract first meaningful line (title)
    first_line = msg.split("\n")[0].strip()

    # Common topic patterns
    # "add Q1 2026 test infrastructure" -> "Q1 Test Infrastructure"
    # "implement user auth system" -> "User Auth System"
    # "complete obsidian sync" -> "Obsidian Sync"

    # Remove action verbs
    first_line = re.sub(
        r"^(add|implement|complete|fix|update|create|improve|optimize)\s+",
        "",
        first_line,
        flags=re.IGNORECASE,
    )

    # Extract key words (capitalize important words)
    words = first_line.split()

    # Filter out common words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}
    key_words = [w for w in words if w.lower() not in stop_words][:5]  # Max 5 words

    if not key_words:
        # Fallback to sanitized first line
        key_words = words[:3]

    # Create topic string
    topic = "-".join(key_words)

    # Clean for filename
    topic = re.sub(r"[^\w\s-]", "", topic)
    topic = re.sub(r"[-\s]+", "-", topic).strip("-")

    # Capitalize
    topic = "-".join(word.capitalize() for word in topic.split("-"))

    return topic if topic else "General-Work"


def get_obsidian_file_path(commit_info: Dict[str, any], vault_path: Path) -> Path:
    """Get Obsidian file path with date folder and topic-based filename

    Structure: 개발일지/YYYY-MM-DD/Topic.md

    Returns:
        Path to the devlog file
    """
    today = datetime.now().strftime("%Y-%m-%d")
    topic = extract_topic_from_commit(commit_info["message"])

    # Create date folder
    date_folder = vault_path / "개발일지" / today
    date_folder.mkdir(parents=True, exist_ok=True)

    # Create topic-based filename
    filename = f"{topic}.md"

    return date_folder / filename


def append_section_to_file(filepath: Path, commit_info: Dict[str, any]) -> None:
    """Append new section to existing file or create new file

    If file exists, adds time-based section
    If file doesn't exist, creates with full template
    """
    now = datetime.now()
    time_str = now.strftime("%H:%M")

    # Generate section header
    commit_lines = commit_info["message"].split("\n")
    title = commit_lines[0]

    # Extract phase if present
    phase_match = re.search(r"[Pp]hase\s+(\d+)", title)
    phase_str = f"Phase {phase_match.group(1)}" if phase_match else "Update"

    section_header = f"\n\n## {time_str} - {phase_str}\n"

    # Generate section content (simplified for append)
    work_type = categorize_work(commit_info)
    key_changes = extract_key_changes(commit_info)

    section_content = f"""
### 작업 내용
- **커밋**: `{commit_info["hash"]}`
- **유형**: {work_type}
- **파일 수**: {commit_info["file_count"]}개

### 주요 변경사항
"""
    for change in key_changes:
        section_content += f"- {change}\n"

    # Add description if present
    description = "\n".join(commit_lines[1:]).strip() if len(commit_lines) > 1 else ""
    if description:
        section_content += f"\n### 상세 설명\n{description}\n"

    if filepath.exists():
        # Append to existing file
        existing = filepath.read_text(encoding="utf-8")
        updated = existing + section_header + section_content
        filepath.write_text(updated, encoding="utf-8")
        print(f"[UPDATE] Appended section to existing file: {filepath.name}")
    else:
        # Create new file with full template
        content = generate_devlog_content(commit_info)
        filepath.write_text(content, encoding="utf-8")
        print(f"[CREATE] Created new file: {filepath.name}")


def update_moc(vault_path: Path, date: str, topic: str) -> None:
    """Update MOC (Map of Contents) with new devlog entry

    Creates/updates 개발일지-MOC.md with links organized by date

    Args:
        vault_path: Path to Obsidian vault
        date: Date string (YYYY-MM-DD)
        topic: Topic name for the file
    """
    moc_path = vault_path / "개발일지" / "개발일지-MOC.md"

    # Create link in Obsidian format
    link = f"- [[{date}/{topic}]]"

    # Check if MOC exists
    if moc_path.exists():
        content = moc_path.read_text(encoding="utf-8")

        # Check if date section exists
        date_section = f"## {date}"
        if date_section in content:
            # Date section exists, check if link already exists
            if link not in content:
                # Add link to existing date section
                # Find the date section and append link
                lines = content.split("\n")
                new_lines = []
                in_date_section = False
                link_added = False

                for i, line in enumerate(lines):
                    new_lines.append(line)

                    if line.strip() == date_section:
                        in_date_section = True
                    elif in_date_section and line.startswith("## "):
                        # Next date section, insert before it
                        new_lines.insert(-1, link)
                        link_added = True
                        in_date_section = False
                    elif in_date_section and i == len(lines) - 1:
                        # End of file
                        new_lines.append(link)
                        link_added = True

                if not link_added and in_date_section:
                    # Still in date section at end of file
                    new_lines.append(link)

                content = "\n".join(new_lines)
        else:
            # Date section doesn't exist, add new section at top
            # Find first ## to insert before it, or append at end
            lines = content.split("\n")
            insert_pos = None

            for i, line in enumerate(lines):
                if line.startswith("## "):
                    insert_pos = i
                    break

            new_section = f"\n{date_section}\n{link}\n"

            if insert_pos is not None:
                lines.insert(insert_pos, new_section)
                content = "\n".join(lines)
            else:
                content = content.rstrip() + "\n" + new_section

        moc_path.write_text(content, encoding="utf-8")
        print("[MOC] Updated 개발일지-MOC.md")
    else:
        # Create new MOC from template
        template_path = Path(__file__).parent / "obsidian_moc_template.md"

        if template_path.exists():
            # Load template and replace placeholders
            template_content = template_path.read_text(encoding="utf-8")
            now = datetime.now()
            content = template_content.replace("{last_update}", now.strftime("%Y-%m-%d %H:%M"))
            content = content.replace("{creation_date}", now.strftime("%Y-%m-%d"))
        else:
            # Fallback to simple MOC if template not found
            content = f"""# 개발일지 Map of Contents

> 자동 생성 MOC - Dataview 플러그인이 설치되면 자동 쿼리가 실행됩니다

---

## 📅 최근 작업

\`\`\`dataview
TABLE
  file.link AS "작업",
  type AS "유형",
  date AS "날짜",
  time AS "시간"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
SORT date DESC, time DESC
LIMIT 20
\`\`\`

---

## {date}
{link}
"""

        moc_path.write_text(content, encoding="utf-8")
        print("[MOC] Created 개발일지-MOC.md with Dataview queries")


def sync_to_obsidian(commit_info: Dict[str, any]) -> bool:
    """Sync to Obsidian with date folder and topic-based organization"""
    try:
        # Load environment variables
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        # Check if Obsidian integration is enabled
        obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
        obsidian_enabled = os.getenv("OBSIDIAN_ENABLED", "false").lower() == "true"

        if not obsidian_enabled or not obsidian_path:
            print("[INFO] Obsidian integration disabled or path not configured")
            return False

        vault_path = Path(obsidian_path)

        # Get file path (date folder + topic-based filename)
        filepath = get_obsidian_file_path(commit_info, vault_path)

        # Append section or create new file
        append_section_to_file(filepath, commit_info)

        # Update MOC (Map of Contents)
        today = datetime.now().strftime("%Y-%m-%d")
        topic = extract_topic_from_commit(commit_info["message"])
        update_moc(vault_path, today, topic)

        # Show relative path for clarity
        relative_path = filepath.relative_to(vault_path)
        print(f"[SUCCESS] Obsidian devlog: {relative_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to sync to Obsidian: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main execution"""
    # Parse arguments
    force = "--force" in sys.argv
    quiet = "--quiet" in sys.argv

    # Get commit info
    commit_info = get_last_commit_info()

    if not commit_info:
        if not quiet:
            print("[INFO] No commit information available (initial commit?)")
        return 0

    # Check if sync is needed
    should_sync_result, reason = should_sync(commit_info, force)

    if not should_sync_result:
        if not quiet:
            print(f"[SKIP] Obsidian sync not needed: {reason}")
        return 0

    if not quiet:
        print(f"[TRIGGER] Obsidian sync triggered: {reason}")
        print(f"[INFO] Commit: {commit_info['hash']} - {commit_info['message'].split(chr(10))[0][:50]}")

    # Sync to Obsidian
    success = sync_to_obsidian(commit_info)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
