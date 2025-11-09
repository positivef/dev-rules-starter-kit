#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Documentation Updater - Constitution 변경 시 문서 자동 갱신
===========================================================

핵심 기능:
1. Constitution.yaml 변경 감지 (Git diff 기반)
2. 변경된 조항(Article) 분석
3. 영향받는 문서 자동 업데이트
4. 버전 관리 및 변경 이력 추적
5. Obsidian 자동 동기화

목표: Constitution 변경 시 수동 문서 업데이트 제거 (2시간 → 30초)
"""

import yaml
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import subprocess


@dataclass
class ConstitutionChange:
    """Constitution 변경 사항"""

    article_id: str
    change_type: str  # added, modified, deleted
    old_content: Optional[Dict] = None
    new_content: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DocumentUpdate:
    """문서 업데이트 작업"""

    file_path: Path
    section: str
    old_text: str
    new_text: str
    reason: str  # e.g., "P4 requirement changed"


class ConstitutionMonitor:
    """Constitution.yaml 변경 감지"""

    def __init__(self, constitution_path: Path):
        self.constitution_path = constitution_path
        self.last_hash: Optional[str] = None
        self.history_file = Path("RUNS/constitution_history.json")

    def get_file_hash(self) -> str:
        """파일 해시 계산"""
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            content = f.read()
        return hashlib.sha256(content.encode()).hexdigest()

    def has_changed(self) -> bool:
        """파일이 변경되었는지 확인"""
        current_hash = self.get_file_hash()

        if self.last_hash is None:
            self.last_hash = current_hash
            return False

        changed = current_hash != self.last_hash
        if changed:
            self.last_hash = current_hash

        return changed

    def get_changes_from_git(self) -> List[ConstitutionChange]:
        """Git diff로 변경 사항 감지"""
        try:
            # Get unstaged changes
            result = subprocess.run(
                ["git", "diff", "HEAD", str(self.constitution_path)],
                capture_output=True,
                text=True,
                cwd=self.constitution_path.parent.parent,
            )

            if result.returncode != 0:
                print(f"[WARN] Git diff failed: {result.stderr}")
                return []

            diff_output = result.stdout

            if not diff_output.strip():
                # No changes
                return []

            # Parse diff to extract changed articles
            changes = self._parse_diff(diff_output)
            return changes

        except Exception as e:
            print(f"[ERROR] Failed to get git changes: {e}")
            return []

    def _parse_diff(self, diff_output: str) -> List[ConstitutionChange]:
        """Git diff 출력 파싱"""
        changes = []

        # Simple parsing - look for article ID patterns
        added_lines = [line[1:] for line in diff_output.split("\n") if line.startswith("+") and "id:" in line]
        removed_lines = [line[1:] for line in diff_output.split("\n") if line.startswith("-") and "id:" in line]

        # Extract article IDs
        added_articles = set()
        removed_articles = set()

        for line in added_lines:
            match = re.search(r'id:\s*["\']?([A-Z]\d+)', line)
            if match:
                added_articles.add(match.group(1))

        for line in removed_lines:
            match = re.search(r'id:\s*["\']?([A-Z]\d+)', line)
            if match:
                removed_articles.add(match.group(1))

        # Determine change types
        for article_id in added_articles - removed_articles:
            changes.append(ConstitutionChange(article_id=article_id, change_type="added"))

        for article_id in removed_articles - added_articles:
            changes.append(ConstitutionChange(article_id=article_id, change_type="deleted"))

        for article_id in added_articles & removed_articles:
            changes.append(ConstitutionChange(article_id=article_id, change_type="modified"))

        return changes

    def load_constitution(self) -> Dict:
        """Constitution.yaml 로드"""
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_history(self, changes: List[ConstitutionChange]):
        """변경 이력 저장"""
        self.history_file.parent.mkdir(exist_ok=True)

        history = []
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        for change in changes:
            history.append(
                {"article_id": change.article_id, "change_type": change.change_type, "timestamp": change.timestamp}
            )

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)


class DocumentAnalyzer:
    """문서 분석 및 업데이트 지점 식별"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_to_update = [
            project_root / "CLAUDE.md",
            project_root / "README.md",
            project_root / "DEVELOPMENT_RULES.md",
            project_root / "docs" / "QUICK_START.md",
        ]

    def find_article_references(self, article_id: str) -> Dict[Path, List[Tuple[int, str]]]:
        """특정 조항을 참조하는 문서 위치 찾기"""
        references = {}

        for doc_path in self.docs_to_update:
            if not doc_path.exists():
                continue

            with open(doc_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            matches = []
            for i, line in enumerate(lines, 1):
                # P1, P2, ... P16 패턴 찾기
                if article_id in line:
                    matches.append((i, line.strip()))

            if matches:
                references[doc_path] = matches

        return references

    def extract_article_summary(self, constitution: Dict, article_id: str) -> Optional[str]:
        """조항 요약 추출"""
        for article in constitution.get("articles", []):
            if article.get("id") == article_id:
                name = article.get("name", "")
                priority = article.get("priority", "")
                tool = article.get("enforcement_tool", "N/A")

                return f"{article_id} ({name}) - Priority: {priority}, Tool: {tool}"

        return None


class DocumentUpdater:
    """문서 자동 갱신 엔진"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analyzer = DocumentAnalyzer(project_root)

    def generate_updates(self, changes: List[ConstitutionChange], constitution: Dict) -> List[DocumentUpdate]:
        """필요한 업데이트 목록 생성"""
        updates = []

        for change in changes:
            article_id = change.article_id

            # Find all references to this article
            references = self.analyzer.find_article_references(article_id)

            if not references:
                print(f"[INFO] No references found for {article_id}")
                continue

            # Get article summary
            summary = self.analyzer.extract_article_summary(constitution, article_id)

            if not summary:
                print(f"[WARN] Could not extract summary for {article_id}")
                continue

            # Generate update for each reference
            for doc_path, matches in references.items():
                for line_num, old_line in matches:
                    # Create update (simple replacement for now)
                    update = DocumentUpdate(
                        file_path=doc_path,
                        section=f"Line {line_num}",
                        old_text=old_line,
                        new_text=self._generate_new_text(old_line, summary, change),
                        reason=f"{article_id} {change.change_type}",
                    )
                    updates.append(update)

        return updates

    def _generate_new_text(self, old_text: str, summary: str, change: ConstitutionChange) -> str:
        """새 텍스트 생성"""
        if change.change_type == "modified":
            # Update summary in place
            return old_text  # Placeholder - 실제로는 더 스마트한 업데이트 필요
        elif change.change_type == "added":
            return old_text + f" [NEW: {summary}]"
        elif change.change_type == "deleted":
            return f"[DEPRECATED] {old_text}"

        return old_text

    def apply_updates(self, updates: List[DocumentUpdate], dry_run: bool = False) -> Dict:
        """업데이트 적용"""
        results = {"success": [], "failed": [], "skipped": []}

        for update in updates:
            try:
                if dry_run:
                    print(f"[DRY-RUN] Would update {update.file_path}:{update.section}")
                    print(f"  Reason: {update.reason}")
                    results["skipped"].append(str(update.file_path))
                    continue

                # Read file
                with open(update.file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Replace old text with new text
                if update.old_text in content:
                    new_content = content.replace(update.old_text, update.new_text, 1)

                    # Write back
                    with open(update.file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"[UPDATE] Updated {update.file_path}:{update.section}")
                    results["success"].append(str(update.file_path))
                else:
                    print(f"[SKIP] Text not found in {update.file_path}")
                    results["skipped"].append(str(update.file_path))

            except Exception as e:
                print(f"[ERROR] Failed to update {update.file_path}: {e}")
                results["failed"].append(str(update.file_path))

        return results


class ObsidianSyncer:
    """Obsidian 동기화"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.obsidian_bridge = project_root / "scripts" / "obsidian_bridge.py"

    def sync_changes(self, changes: List[ConstitutionChange]) -> bool:
        """Constitution 변경사항을 Obsidian에 동기화"""
        try:
            if not self.obsidian_bridge.exists():
                print("[WARN] Obsidian bridge not found")
                return False

            # Create sync note
            _ = self._create_sync_note(changes)

            # Save to Obsidian
            result = subprocess.run(
                ["python", str(self.obsidian_bridge), "sync"], capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("[OBSIDIAN] Synced successfully")
                return True
            else:
                print(f"[OBSIDIAN] Sync failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"[ERROR] Obsidian sync failed: {e}")
            return False

    def _create_sync_note(self, changes: List[ConstitutionChange]) -> str:
        """동기화 노트 생성"""
        note = f"""# Constitution Changes

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

"""
        for change in changes:
            note += f"- **{change.article_id}**: {change.change_type}\n"

        return note


class AutoDocUpdater:
    """메인 오케스트레이터"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.constitution_path = self.project_root / "config" / "constitution.yaml"

        self.monitor = ConstitutionMonitor(self.constitution_path)
        self.updater = DocumentUpdater(self.project_root)
        self.obsidian = ObsidianSyncer(self.project_root)

    def check_and_update(self, dry_run: bool = False) -> Dict:
        """Constitution 변경 확인 및 문서 업데이트"""
        print("[CHECK] Checking Constitution for changes...")

        # 1. Check for changes
        if not self.monitor.has_changed():
            print("[INFO] No changes detected")
            return {"status": "no_changes"}

        # 2. Get changes from Git
        changes = self.monitor.get_changes_from_git()

        if not changes:
            print("[INFO] No article changes detected")
            return {"status": "no_article_changes"}

        print(f"[DETECT] Found {len(changes)} article changes")
        for change in changes:
            print(f"  - {change.article_id}: {change.change_type}")

        # 3. Load current constitution
        constitution = self.monitor.load_constitution()

        # 4. Generate updates
        updates = self.updater.generate_updates(changes, constitution)
        print(f"[PLAN] Generated {len(updates)} document updates")

        # 5. Apply updates
        results = self.updater.apply_updates(updates, dry_run=dry_run)

        # 6. Save history
        self.monitor.save_history(changes)

        # 7. Sync to Obsidian
        if not dry_run and results["success"]:
            self.obsidian.sync_changes(changes)

        # 8. Generate report
        report = {
            "status": "updated",
            "changes": len(changes),
            "updates_applied": len(results["success"]),
            "updates_failed": len(results["failed"]),
            "updates_skipped": len(results["skipped"]),
            "timestamp": datetime.now().isoformat(),
        }

        print("\n" + "=" * 60)
        print("[REPORT] Auto Documentation Update Summary")
        print("=" * 60)
        print(f"Constitution Changes: {report['changes']}")
        print(f"Updates Applied: {report['updates_applied']}")
        print(f"Updates Failed: {report['updates_failed']}")
        print(f"Updates Skipped: {report['updates_skipped']}")
        print("=" * 60)

        return report

    def watch_mode(self, interval: int = 60):
        """Watch mode - 주기적 체크"""
        import time

        print(f"[WATCH] Monitoring Constitution (every {interval}s)")
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.check_and_update()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[STOP] Watch mode stopped")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto Documentation Updater")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update files")
    parser.add_argument("--watch", action="store_true", help="Watch mode - continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")

    args = parser.parse_args()

    updater = AutoDocUpdater()

    if args.watch:
        updater.watch_mode(interval=args.interval)
    else:
        report = updater.check_and_update(dry_run=args.dry_run)

        if report["status"] == "updated":
            print("[SUCCESS] Documentation updated successfully!")
            return 0
        elif report["status"] == "no_changes":
            print("[INFO] No changes to process")
            return 0
        else:
            print("[WARNING] Updates completed with issues")
            return 1


if __name__ == "__main__":
    exit(main())
