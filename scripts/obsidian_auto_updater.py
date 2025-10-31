#!/usr/bin/env python3
"""Obsidian 자동 업데이트 시스템

Phase C Week 2+에서 사용할 옵시디언 자동 업데이트 기능

주요 기능:
1. Daily Notes 자동 생성 (매일 작업 내용)
2. Git 커밋 자동 기록
3. 테스트 결과 자동 업데이트
4. 성능 벤치마크 자동 기록
5. 문제 파일 추적 (Problem Files Tracker)

사용 예시:
```python
from scripts.obsidian_auto_updater import ObsidianUpdater

updater = ObsidianUpdater(vault_path="C:/Users/user/Documents/Obsidian Vault")

# 1. Daily Note 업데이트
updater.update_daily_note(
    date="2025-01-27",
    tasks=[
        "DeepAnalyzer 구현 완료",
        "83개 테스트 통과",
    ],
    insights="AST 사용법 학습, Threading 성능 3배 향상"
)

# 2. Git 커밋 자동 기록
updater.record_commit(
    commit_hash="8a4feb8",
    message="feat(integration): complete Phase C Week 2",
    files_changed=4,
    lines_added=1307
)

# 3. 테스트 결과 기록
updater.record_test_results(
    total=83,
    passed=83,
    failed=0,
    duration=14.58
)

# 4. 문제 파일 추적
updater.track_problem_file(
    file_path="api/executor.py",
    quality_score=5.2,
    issues=["SRP 위반", "DIP 위반", "eval() 사용"]
)
```

TODO (Phase D):
- [ ] Daily Notes 템플릿 자동 생성
- [ ] Git hook 연동 (커밋 시 자동 기록)
- [ ] 테스트 완료 시 자동 업데이트
- [ ] 성능 그래프 자동 생성 (Mermaid)
- [ ] 주간/월간 리포트 자동 생성
"""

from datetime import datetime
from pathlib import Path

# MCP Obsidian 서버 사용 가정
try:
    import importlib.util

    MCP_AVAILABLE = bool(importlib.util.find_spec("mcp_obsidian"))
    if not MCP_AVAILABLE:
        print("Warning: MCP Obsidian not available, using fallback mode")
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP Obsidian not available, using fallback mode")


class ObsidianUpdater:
    """옵시디언 자동 업데이트 클래스

    Features:
    - Daily Notes 자동 생성/업데이트
    - Git 활동 추적
    - 테스트 결과 기록
    - 성능 메트릭 추적
    - 문제 파일 모니터링
    """

    def __init__(self, vault_path: str | Path):
        """초기화

        Args:
            vault_path: Obsidian vault 경로
        """
        self.vault_path = Path(vault_path)
        self.dev_rules_folder = self.vault_path / "Dev Rules Project"

        if not self.dev_rules_folder.exists():
            self.dev_rules_folder.mkdir(parents=True)

    def update_daily_note(
        self,
        date: str | None = None,
        tasks: list[str] | None = None,
        insights: str | None = None,
    ) -> Path:
        """Daily Note 업데이트

        Args:
            date: 날짜 (YYYY-MM-DD), None이면 오늘
            tasks: 완료한 작업 목록
            insights: 배운 점 / 인사이트

        Returns:
            생성/업데이트된 노트 경로
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        note_path = self.dev_rules_folder / f"Daily Note {date}.md"

        content = f"""# Daily Note - {date}

## 오늘 한 일

"""
        if tasks:
            for task in tasks:
                content += f"- [OK] {task}\n"
        else:
            content += "- (작업 내용 기록)\n"

        content += "\n## 배운 점 / 인사이트\n\n"
        if insights:
            content += f"{insights}\n"
        else:
            content += "(오늘 배운 것 기록)\n"

        content += """
## 통계

- 커밋: (자동 업데이트)
- 테스트: (자동 업데이트)
- 품질: (자동 업데이트)

---

*자동 생성: ObsidianUpdater*
"""

        # 파일 쓰기 (append가 아닌 overwrite)
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def record_commit(
        self,
        commit_hash: str,
        message: str,
        files_changed: int,
        lines_added: int,
        date: str | None = None,
    ) -> None:
        """Git 커밋 기록

        Args:
            commit_hash: 커밋 해시
            message: 커밋 메시지
            files_changed: 변경된 파일 수
            lines_added: 추가된 라인 수
            date: 날짜 (None이면 오늘)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Git History 노트에 추가
        history_path = self.dev_rules_folder / "Git History.md"

        if not history_path.exists():
            history_path.write_text("# Git History\n\n", encoding="utf-8")

        commit_entry = f"""
## {date} - {commit_hash[:7]}

**Message**: {message.split(chr(10))[0]}

**Stats**:
- Files changed: {files_changed}
- Lines added: {lines_added}

---

"""

        # Append mode
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(commit_entry)

    def record_test_results(
        self,
        total: int,
        passed: int,
        failed: int,
        duration: float,
        date: str | None = None,
    ) -> None:
        """테스트 결과 기록

        Args:
            total: 전체 테스트 수
            passed: 통과한 테스트 수
            failed: 실패한 테스트 수
            duration: 실행 시간 (초)
            date: 날짜 (None이면 오늘)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        test_path = self.dev_rules_folder / "Test Results History.md"

        if not test_path.exists():
            test_path.write_text("# Test Results History\n\n", encoding="utf-8")

        pass_rate = (passed / total * 100) if total > 0 else 0

        test_entry = f"""
## {date}

**Results**:
- Total: {total}
- Passed: {passed} ({pass_rate:.1f}%)
- Failed: {failed}
- Duration: {duration:.2f}s

**Status**: {"[OK] ALL PASS" if failed == 0 else f"[WARN] {failed} FAILED"}

---

"""

        with open(test_path, "a", encoding="utf-8") as f:
            f.write(test_entry)

    def track_problem_file(
        self,
        file_path: str,
        quality_score: float,
        issues: list[str],
        date: str | None = None,
    ) -> None:
        """문제 파일 추적

        Args:
            file_path: 파일 경로
            quality_score: 품질 점수 (0-10)
            issues: 문제 목록
            date: 날짜 (None이면 오늘)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        tracker_path = self.dev_rules_folder / "Problem Files Tracker.md"

        if not tracker_path.exists():
            header = """# Problem Files Tracker

품질이 낮은 파일들을 추적하여 개선합니다.

**기준**: 품질 점수 7.0 미만

---

"""
            tracker_path.write_text(header, encoding="utf-8")

        problem_entry = f"""
## {file_path} ({date})

**Quality Score**: {quality_score:.1f}/10

**Issues**:
"""
        for issue in issues:
            problem_entry += f"- {issue}\n"

        problem_entry += "\n**Action Items**:\n- [ ] 리팩토링 계획 수립\n- [ ] 테스트 추가\n\n---\n\n"

        with open(tracker_path, "a", encoding="utf-8") as f:
            f.write(problem_entry)

    def generate_weekly_summary(
        self,
        week_number: int,
        commits: int,
        tests_passed: int,
        avg_quality: float,
        highlights: list[str],
    ) -> Path:
        """주간 요약 생성

        Args:
            week_number: 주 번호
            commits: 총 커밋 수
            tests_passed: 통과한 테스트 수
            avg_quality: 평균 품질 점수
            highlights: 주요 성과

        Returns:
            생성된 주간 요약 경로
        """
        summary_path = self.dev_rules_folder / f"Week {week_number} Summary.md"

        content = f"""# Week {week_number} Summary

## 통계

- [LOG] 커밋: {commits}개
- [OK] 테스트: {tests_passed}개 통과
- [STATUS] 평균 품질: {avg_quality:.1f}/10

## 주요 성과

"""
        for highlight in highlights:
            content += f"- [SUCCESS] {highlight}\n"

        content += """
## 다음 주 계획

- [ ] (계획 작성)

---

*자동 생성: ObsidianUpdater*
"""

        summary_path.write_text(content, encoding="utf-8")
        return summary_path


# CLI 인터페이스
def main():
    """CLI 데모"""
    import argparse

    parser = argparse.ArgumentParser(description="Obsidian Auto Updater")
    parser.add_argument("--vault", required=True, help="Obsidian vault path")
    parser.add_argument("--action", choices=["daily", "commit", "test", "problem"])
    args = parser.parse_args()

    updater = ObsidianUpdater(vault_path=args.vault)

    if args.action == "daily":
        note_path = updater.update_daily_note(tasks=["Example task"], insights="Example insight")
        print(f"Daily note updated: {note_path}")

    elif args.action == "commit":
        updater.record_commit(commit_hash="abc1234", message="feat: example commit", files_changed=3, lines_added=100)
        print("Commit recorded")

    elif args.action == "test":
        updater.record_test_results(total=83, passed=83, failed=0, duration=14.58)
        print("Test results recorded")

    elif args.action == "problem":
        updater.track_problem_file(file_path="api/executor.py", quality_score=5.2, issues=["SRP violation", "DIP violation"])
        print("Problem file tracked")


if __name__ == "__main__":
    main()
