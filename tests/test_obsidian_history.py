#!/usr/bin/env python3
"""
옵시디언 히스토리 추적 테스트
"""

import pytest
import tempfile
from pathlib import Path
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.obsidian_history_tracker import ObsidianHistoryTracker
from scripts.obsidian_bridge import ObsidianBridge


class TestObsidianHistory:
    """옵시디언 히스토리 추적 테스트"""

    def test_history_tracker_initialization(self):
        """히스토리 트래커 초기화 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            assert tracker is not None
            assert tracker.vault_path == Path(tmpdir)
            assert tracker.history_dir.exists()

    def test_track_single_update(self):
        """단일 업데이트 추적 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 테스트 파일 생성
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test Document\n\nContent", encoding="utf-8")

            # 업데이트 추적
            record = tracker.track_update("test.md", action="create")

            assert record is not None
            assert record["action"] == "create"
            assert record["update_number"] == 1

    def test_track_multiple_updates(self):
        """다중 업데이트 추적 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 테스트 파일 생성
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test Document", encoding="utf-8")

            # 첫 번째 업데이트
            record1 = tracker.track_update("test.md", action="create")
            assert record1["update_number"] == 1

            # 두 번째 업데이트 (0.1초 대기)
            time.sleep(0.1)
            test_file.write_text("# Test Document\n\nUpdated", encoding="utf-8")
            record2 = tracker.track_update("test.md", action="update")
            assert record2["update_number"] == 2

            # 세 번째 업데이트
            time.sleep(0.1)
            test_file.write_text("# Test Document\n\nUpdated again", encoding="utf-8")
            record3 = tracker.track_update("test.md", action="update")
            assert record3["update_number"] == 3

    def test_history_section_generation(self):
        """히스토리 섹션 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 테스트 파일 생성 및 업데이트
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test Document\n\nContent", encoding="utf-8")

            # 3번 업데이트
            for i in range(3):
                tracker.track_update("test.md", action=f"update_{i+1}")
                time.sleep(0.1)

            # 파일 내용 확인
            content = test_file.read_text(encoding="utf-8")

            # 히스토리 섹션이 추가되었는지 확인
            assert "<!-- HISTORY_START -->" in content
            assert "<!-- HISTORY_END -->" in content
            assert "Update History" in content
            assert "**Total Updates**: 3" in content

    def test_get_file_history(self):
        """파일 히스토리 조회 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 테스트 파일 생성
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test", encoding="utf-8")

            # 업데이트 추적
            tracker.track_update("test.md", action="create")
            tracker.track_update("test.md", action="update")

            # 히스토리 조회
            history = tracker.get_file_history("test.md")

            assert history is not None
            assert history["update_count"] == 2
            assert len(history["history"]) == 2

    def test_recent_updates(self):
        """최근 업데이트 조회 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 여러 파일 생성 및 업데이트
            for i in range(5):
                test_file = Path(tmpdir) / f"test{i}.md"
                test_file.write_text(f"# Test {i}", encoding="utf-8")
                tracker.track_update(f"test{i}.md", action="create")
                time.sleep(0.05)

            # 최근 업데이트 조회
            recent = tracker.get_recent_updates(limit=3)

            assert len(recent) == 3
            # 가장 최근 것이 먼저
            assert recent[0]["file_path"] == "test4.md"

    def test_reliability_indicators(self):
        """신뢰도 지표 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test", encoding="utf-8")

            # 12번 업데이트 (HIGH reliability)
            for i in range(12):
                tracker.track_update("test.md", action=f"update_{i+1}")

            content = test_file.read_text(encoding="utf-8")

            # HIGH reliability 표시 확인
            assert "[+++]" in content
            assert "HIGH" in content

    def test_obsidian_bridge_integration(self):
        """ObsidianBridge 통합 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 환경 변수 임시 설정
            os.environ["OBSIDIAN_VAULT_PATH"] = tmpdir

            try:
                bridge = ObsidianBridge(Path(tmpdir))

                # history_tracker가 초기화되었는지 확인
                assert bridge.history_tracker is not None

                # 테스트 작업 계약
                task_contract = {
                    "task_id": "TEST-001",
                    "title": "Test Task",
                    "description": "Test description",
                    "acceptance_criteria": ["Test criteria"],
                    "commands": [],
                    "gates": [],
                }

                execution_result = {"status": "success", "duration": 1.5, "evidence_hashes": {}}

                # devlog 생성
                devlog_path = bridge.create_devlog(task_contract, execution_result)

                # 파일이 생성되었는지 확인
                assert devlog_path.exists()

                # 히스토리가 기록되었는지 확인
                if bridge.history_tracker:
                    relative_path = devlog_path.relative_to(bridge.vault_path).as_posix()
                    history = bridge.history_tracker.get_file_history(relative_path)
                    assert history is not None
                    assert history["update_count"] >= 1

            finally:
                # 환경 변수 정리
                if "OBSIDIAN_VAULT_PATH" in os.environ:
                    del os.environ["OBSIDIAN_VAULT_PATH"]

    def test_history_report_generation(self):
        """히스토리 리포트 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ObsidianHistoryTracker(tmpdir)

            # 여러 파일 업데이트
            for i in range(3):
                test_file = Path(tmpdir) / f"file{i}.md"
                test_file.write_text(f"# File {i}", encoding="utf-8")

                # 각 파일마다 다른 횟수로 업데이트
                for j in range(i + 1):
                    tracker.track_update(f"file{i}.md", action=f"update_{j+1}")

            # 리포트 생성
            report = tracker.generate_history_report()

            assert "Obsidian Vault Update History Report" in report
            assert "**Total Files Tracked**: 3" in report
            assert "Most Updated Files" in report
            assert "Recent Updates" in report

    def test_no_emoji_in_python_code(self):
        """Python 코드에 이모지가 없는지 확인"""
        # obsidian_bridge.py 확인
        bridge_file = Path(__file__).parent.parent / "scripts" / "obsidian_bridge.py"
        if bridge_file.exists():
            content = bridge_file.read_text(encoding="utf-8")

            # Python 코드에서 이모지 검색 (Markdown 생성 부분 제외)
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                # 문자열 리터럴 내부가 아닌 곳에서 이모지 확인
                if not ('"' in line or "'" in line):
                    # 일반적인 이모지 범위 체크
                    for char in line:
                        if ord(char) > 0x1F600:  # 이모지 범위
                            pytest.fail(f"Emoji found in Python code at line {i}: {line}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
