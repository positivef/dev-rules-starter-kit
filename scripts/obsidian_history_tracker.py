#!/usr/bin/env python3
"""
Obsidian History Tracker
옵시디언 문서 업데이트 히스토리 관리 시스템

각 문서의 모든 업데이트 시간과 변경 내용을 추적합니다.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional


class ObsidianHistoryTracker:
    """옵시디언 문서 히스토리 추적기"""

    def __init__(self, vault_path: str = None):
        """
        Initialize Obsidian History Tracker

        Args:
            vault_path: 옵시디언 vault 경로
        """
        # .env에서 경로 읽기
        if not vault_path:
            from dotenv import load_dotenv

            load_dotenv()
            vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

        if not vault_path:
            raise ValueError("OBSIDIAN_VAULT_PATH not set in .env")

        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        # 히스토리 저장 경로
        self.history_dir = self.vault_path / ".history"
        self.history_dir.mkdir(exist_ok=True)

        # 히스토리 메타데이터 파일
        self.history_index = self.history_dir / "index.json"

    def track_update(self, file_path: str, action: str = "update", metadata: Dict = None) -> Dict:
        """
        문서 업데이트 추적

        Args:
            file_path: 업데이트된 파일 경로 (vault 내 상대 경로)
            action: 수행된 작업 (create, update, sync, etc.)
            metadata: 추가 메타데이터

        Returns:
            업데이트 기록
        """
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = self.vault_path / file_path

        # 파일 존재 확인
        if not file_path.exists():
            return {"error": "File not found", "path": str(file_path)}

        # 파일 해시 계산 (변경 감지용)
        content = file_path.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]

        # 현재 타임스탬프
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        # 업데이트 기록
        update_record = {
            "timestamp": timestamp_str,
            "timestamp_iso": timestamp.isoformat(),
            "action": action,
            "hash": content_hash,
            "size": len(content),
            "lines": content.count("\n") + 1,
            "metadata": metadata or {},
        }

        # 히스토리 인덱스 로드
        history_index = self._load_history_index()

        # 파일의 상대 경로
        relative_path = file_path.relative_to(self.vault_path).as_posix()

        # 파일 히스토리 가져오기 또는 생성
        if relative_path not in history_index:
            history_index[relative_path] = {
                "first_created": timestamp_str,
                "last_updated": timestamp_str,
                "update_count": 0,
                "history": [],
            }

        file_history = history_index[relative_path]

        # 업데이트 카운트 증가
        file_history["update_count"] += 1
        file_history["last_updated"] = timestamp_str

        # 히스토리에 추가 (순서 번호 포함)
        update_record["update_number"] = file_history["update_count"]
        file_history["history"].append(update_record)

        # 최대 100개 히스토리만 유지 (오래된 것부터 제거)
        if len(file_history["history"]) > 100:
            file_history["history"] = file_history["history"][-100:]

        # 인덱스 저장
        self._save_history_index(history_index)

        # 문서에 히스토리 섹션 추가/업데이트
        self._update_document_history(file_path, file_history)

        return update_record

    def _update_document_history(self, file_path: Path, history: Dict):
        """문서 내 히스토리 섹션 업데이트"""
        content = file_path.read_text(encoding="utf-8")

        # 히스토리 섹션 생성
        history_section = self._generate_history_section(history)

        # 기존 히스토리 섹션 찾기
        history_marker_start = "<!-- HISTORY_START -->"
        history_marker_end = "<!-- HISTORY_END -->"

        if history_marker_start in content:
            # 기존 섹션 교체
            start_idx = content.index(history_marker_start)
            end_idx = content.index(history_marker_end) + len(history_marker_end)
            content = content[:start_idx] + history_section + content[end_idx:]
        else:
            # 문서 끝에 추가
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + history_section

        # 파일 저장
        file_path.write_text(content, encoding="utf-8")

    def _generate_history_section(self, history: Dict) -> str:
        """히스토리 섹션 HTML 생성"""
        section = []
        section.append("<!-- HISTORY_START -->")
        section.append("\n---\n")
        section.append("## [LOG] Update History")
        section.append("")

        # 요약 정보
        section.append(f"- **First Created**: {history['first_created']}")
        section.append(f"- **Last Updated**: {history['last_updated']}")
        section.append(f"- **Total Updates**: {history['update_count']}")
        section.append("")

        # 최근 10개 업데이트만 표시
        recent_updates = history["history"][-10:]
        if recent_updates:
            section.append("### Recent Updates")
            section.append("")

            # 테이블 헤더
            section.append("| # | Timestamp | Action | Size | Hash |")
            section.append("|---|-----------|--------|------|------|")

            # 역순으로 표시 (최신이 위로)
            for update in reversed(recent_updates):
                num = update["update_number"]
                time = update["timestamp"].split(" ")[1].split(" ")[0]  # 시간만
                date = update["timestamp"].split(" ")[0]  # 날짜
                action = update["action"]
                size = f"{update['size']:,} bytes"
                hash_short = update["hash"]

                section.append(f"| {num} | {date} {time} | {action} | {size} | `{hash_short}` |")

        # 신뢰도 지표
        section.append("")
        section.append("### [STATUS] Reliability Indicators")
        section.append("")

        update_count = history["update_count"]
        if update_count >= 10:
            reliability = "HIGH"
            indicator = "[+++]"
        elif update_count >= 5:
            reliability = "MEDIUM"
            indicator = "[++]"
        else:
            reliability = "LOW"
            indicator = "[+]"

        section.append(f"- **Update Frequency**: {indicator} {reliability}")

        # 최근 업데이트 빈도 계산
        if len(history["history"]) >= 2:
            recent = history["history"][-1]
            previous = history["history"][-2]
            recent_time = datetime.fromisoformat(recent["timestamp_iso"])
            prev_time = datetime.fromisoformat(previous["timestamp_iso"])
            time_diff = recent_time - prev_time

            if time_diff.days == 0:
                frequency = "Active (updated today)"
            elif time_diff.days <= 7:
                frequency = f"Recent ({time_diff.days} days ago)"
            elif time_diff.days <= 30:
                frequency = f"Moderate ({time_diff.days} days ago)"
            else:
                frequency = f"Stale ({time_diff.days} days ago)"

            section.append(f"- **Last Activity**: {frequency}")

        section.append("")
        section.append("<!-- HISTORY_END -->")

        return "\n".join(section)

    def _load_history_index(self) -> Dict:
        """히스토리 인덱스 로드"""
        if self.history_index.exists():
            with open(self.history_index, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_history_index(self, index: Dict):
        """히스토리 인덱스 저장"""
        with open(self.history_index, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def get_file_history(self, file_path: str) -> Optional[Dict]:
        """특정 파일의 히스토리 조회"""
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = self.vault_path / file_path

        relative_path = file_path.relative_to(self.vault_path).as_posix()
        history_index = self._load_history_index()

        return history_index.get(relative_path)

    def get_recent_updates(self, limit: int = 10) -> List[Dict]:
        """최근 업데이트된 파일 목록"""
        history_index = self._load_history_index()

        # 모든 파일의 최근 업데이트 수집
        recent_updates = []
        for file_path, history in history_index.items():
            if history["history"]:
                latest = history["history"][-1]
                latest["file_path"] = file_path
                recent_updates.append(latest)

        # 타임스탬프로 정렬
        recent_updates.sort(key=lambda x: x["timestamp_iso"], reverse=True)

        return recent_updates[:limit]

    def generate_history_report(self) -> str:
        """전체 히스토리 리포트 생성"""
        history_index = self._load_history_index()

        report = []
        report.append("# Obsidian Vault Update History Report")
        report.append("")
        report.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")

        # 통계
        total_files = len(history_index)
        total_updates = sum(h["update_count"] for h in history_index.values())

        report.append("## [STATUS] Statistics")
        report.append("")
        report.append(f"- **Total Files Tracked**: {total_files}")
        report.append(f"- **Total Updates**: {total_updates}")
        report.append("")

        # 가장 많이 업데이트된 파일 Top 10
        report.append("## [CRITICAL] Most Updated Files")
        report.append("")

        sorted_files = sorted(history_index.items(), key=lambda x: x[1]["update_count"], reverse=True)[:10]

        for file_path, history in sorted_files:
            count = history["update_count"]
            last_update = history["last_updated"]
            report.append(f"- **{file_path}**: {count} updates (last: {last_update})")

        # 최근 업데이트
        report.append("")
        report.append("## 🕐 Recent Updates")
        report.append("")

        recent = self.get_recent_updates(20)
        for update in recent:
            report.append(f"- {update['timestamp']} - **{update['file_path']}** ({update['action']})")

        return "\n".join(report)


def test_tracker():
    """테스트 함수"""
    print("[TEST] Obsidian History Tracker")
    print("-" * 60)

    # 트래커 초기화
    try:
        tracker = ObsidianHistoryTracker()
        print(f"[OK] Tracker initialized with vault: {tracker.vault_path}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        return

    # 테스트 파일 생성
    test_file = tracker.vault_path / "test_history.md"
    test_content = f"""# Test Document

This is a test document created at {datetime.now()}

## Content
- Test line 1
- Test line 2
"""
    test_file.write_text(test_content, encoding="utf-8")

    # 업데이트 추적
    print("\n[TEST] Tracking updates...")

    for i in range(3):
        # 파일 수정
        test_file.write_text(test_content + f"\n- Update {i+1}\n", encoding="utf-8")

        # 업데이트 추적
        record = tracker.track_update("test_history.md", action=f"update_{i+1}", metadata={"test_run": i + 1})

        print(f"  Update {i+1}: {record['timestamp']} (#{record['update_number']})")

    # 히스토리 조회
    print("\n[TEST] Retrieving history...")
    history = tracker.get_file_history("test_history.md")
    if history:
        print(f"  Total updates: {history['update_count']}")
        print(f"  First created: {history['first_created']}")
        print(f"  Last updated: {history['last_updated']}")

    # 리포트 생성
    print("\n[TEST] Generating report...")
    report = tracker.generate_history_report()
    report_file = tracker.vault_path / "history_report.md"
    report_file.write_text(report, encoding="utf-8")
    print(f"  Report saved to: {report_file}")

    print("\n[OK] All tests completed!")


if __name__ == "__main__":
    test_tracker()
