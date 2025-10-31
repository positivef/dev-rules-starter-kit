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
    """Generate development log content"""
    today = datetime.now().strftime("%Y-%m-%d")
    work_type = categorize_work(commit_info)
    key_changes = extract_key_changes(commit_info)

    # Parse commit message
    commit_lines = commit_info["message"].split("\n")
    title = commit_lines[0]
    description = "\n".join(commit_lines[1:]).strip() if len(commit_lines) > 1 else ""

    content = f"""# {today} {title}

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


def sync_to_obsidian(commit_info: Dict[str, any]) -> bool:
    """Sync to Obsidian using MCP"""
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

        # Generate devlog content
        content = generate_devlog_content(commit_info)

        # Generate filename
        today = datetime.now().strftime("%Y-%m-%d")
        commit_title = commit_info["message"].split("\n")[0]
        # Clean title for filename
        safe_title = re.sub(r"[^\w\s-]", "", commit_title)
        safe_title = re.sub(r"[-\s]+", "-", safe_title).strip("-")[:50]
        filename = f"{today}_{safe_title}.md"

        # Use MCP Obsidian to append (since we're in Claude Code context)
        # For now, write directly to file
        vault_path = Path(obsidian_path)
        devlog_dir = vault_path / "개발일지"
        devlog_dir.mkdir(parents=True, exist_ok=True)

        filepath = devlog_dir / filename

        # Check if file exists, if so append instead of overwrite
        if filepath.exists():
            existing = filepath.read_text(encoding="utf-8")
            content = existing + "\n\n---\n\n" + content

        filepath.write_text(content, encoding="utf-8")

        print(f"[SUCCESS] Obsidian devlog created: {filename}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to sync to Obsidian: {e}")
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
