#!/usr/bin/env python3
"""
Pre-Execution Guard - 검증된 실수 반복 방지
실행 전 자동으로 known error patterns 체크
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional
import json

# Try to load dotenv if available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


class PreExecutionGuard:
    """실행 전 검증 시스템"""

    def __init__(self):
        self.known_errors = self._load_known_errors()

    def _load_known_errors(self) -> List[Dict]:
        """
        Hybrid mode: Load core patterns + optional Obsidian details

        Returns:
            List of error pattern dictionaries
        """
        # 1. Load core patterns (always available)
        core_file = Path("RUNS/error_patterns_core.json")
        if not core_file.exists():
            print("[WARNING] Core patterns file not found: RUNS/error_patterns_core.json")
            return []

        try:
            with open(core_file, "r", encoding="utf-8") as f:
                core_data = json.load(f)

            patterns = core_data.get("patterns", {})
            print(f"[OK] Loaded {len(patterns)} core error patterns (Mode: {core_data.get('mode', 'unknown')})")

            # 2. Try loading detailed examples from Obsidian (optional)
            obsidian_ref = core_data.get("obsidian_reference", {})
            if obsidian_ref.get("enabled"):
                try:
                    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", ".")
                    detailed_file = Path(vault_path) / "Knowledge" / "Dev-Rules" / "Error_Database.md"

                    if detailed_file.exists():
                        print(f"[INFO] Obsidian detailed knowledge available: {detailed_file}")
                        print("[INFO] Using hybrid mode: core patterns + Obsidian details")
                    else:
                        print("[INFO] Obsidian file not found, using core patterns only")

                except Exception as e:
                    print(f"[INFO] Obsidian unavailable, using core patterns only: {e}")

            # 3. Return patterns in compatible format
            error_list = []
            for error_id, pattern_data in patterns.items():
                error_list.append(
                    {
                        "error_id": error_id,
                        "pattern": pattern_data.get("detection", ""),
                        "severity": pattern_data.get("severity", "MEDIUM"),
                        "solution": pattern_data.get("quick_fix", ""),
                        "regex_pattern": pattern_data.get("pattern", ""),
                    }
                )

            return error_list

        except Exception as e:
            print(f"[ERROR] Failed to load error patterns: {e}")
            return []

    def check_code(self, code: str) -> Dict:
        """
        코드 실행 전 검증

        Returns:
            {
                'safe': bool,
                'violations': List[Dict],
                'recommendations': List[str]
            }
        """
        violations = []

        # Pattern 1: print() with emoji
        if self._has_print_with_emoji(code):
            violations.append(
                {
                    "pattern": "print_emoji",
                    "severity": "HIGH",
                    "line": self._find_line_with_pattern(code, r"print.*[\U0001F300-\U0001F9FF]"),
                    "message": "Detected print() with emoji - will cause cp949 error on Windows",
                    "solution": "Remove print() or convert emoji to ASCII ([OK], [X])",
                }
            )

        # Pattern 2: emoji in Python string literals
        if self._has_emoji_in_python(code):
            violations.append(
                {
                    "pattern": "emoji_in_python",
                    "severity": "HIGH",
                    "line": self._find_line_with_pattern(code, r'["\'].*[\U0001F300-\U0001F9FF].*["\']'),
                    "message": "Emoji detected in Python code",
                    "solution": "Use ASCII alternatives: [OK], [X], [!]",
                }
            )

        # Pattern 3: print(variable) where variable contains file/markdown content
        if self._has_risky_print_pattern(code):
            violations.append(
                {
                    "pattern": "print_file_content",
                    "severity": "HIGH",
                    "line": self._find_line_with_pattern(
                        code, r"print\([a-zA-Z_]*(?:content|section|markdown|text|history)[a-zA-Z_]*\)"
                    ),
                    "message": "Printing file content variable - likely contains emoji",
                    "solution": "Use Read tool instead of print() to display file content",
                }
            )

        # Pattern 4: Known high-risk pattern from error_learner
        if "UnicodeEncodeError" in str(self.known_errors):
            # 학습된 패턴 기반 추가 검증
            pass

        recommendations = self._generate_recommendations(violations)

        return {"safe": len(violations) == 0, "violations": violations, "recommendations": recommendations}

    def _has_print_with_emoji(self, code: str) -> bool:
        """print()에 이모지가 있는지 확인"""
        # Unicode emoji range
        emoji_pattern = r"print.*[\U0001F300-\U0001F9FF]"
        return bool(re.search(emoji_pattern, code))

    def _has_emoji_in_python(self, code: str) -> bool:
        """Python 코드에 이모지가 있는지 확인"""
        # Markdown 문자열이 아닌 경우만
        if ".md" in code or "markdown" in code.lower():
            return False

        emoji_pattern = r"[\U0001F300-\U0001F9FF]"
        return bool(re.search(emoji_pattern, code))

    def _has_risky_print_pattern(self, code: str) -> bool:
        """위험한 print 패턴 확인 (파일 내용 변수 출력)"""
        # print(content), print(history_section), print(markdown_text) 등
        risky_pattern = r"print\([a-zA-Z_]*(?:content|section|markdown|text|history)[a-zA-Z_]*\)"
        return bool(re.search(risky_pattern, code))

    def _find_line_with_pattern(self, code: str, pattern: str) -> Optional[int]:
        """패턴이 있는 라인 번호 찾기"""
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return None

    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """위반 사항 기반 권장사항 생성"""
        recommendations = []

        for violation in violations:
            if violation["pattern"] == "print_emoji":
                recommendations.append("Replace: print(emoji_string) -> file.write_text(emoji_string) + Read tool")
            elif violation["pattern"] == "emoji_in_python":
                recommendations.append("Use ASCII: [OK] instead of checkmark, [X] instead of cross, [!] instead of warning")
            elif violation["pattern"] == "print_file_content":
                recommendations.append("NEVER print file/markdown content - use Read tool to display instead")

        return recommendations

    def enforce(self, code: str, auto_fix: bool = False) -> Dict:
        """
        강제 적용

        Args:
            code: 검증할 코드
            auto_fix: 자동 수정 여부

        Returns:
            {
                'passed': bool,
                'fixed_code': Optional[str],
                'report': str
            }
        """
        result = self.check_code(code)

        if result["safe"]:
            return {"passed": True, "fixed_code": None, "report": "[OK] No known error patterns detected"}

        # 보고서 생성
        report = ["[GUARD] Pre-execution violations detected:", ""]

        for violation in result["violations"]:
            severity_mark = "[!!!]" if violation["severity"] == "HIGH" else "[!]"
            report.append(f"{severity_mark} {violation['message']}")
            if violation["line"]:
                report.append(f"  Line: {violation['line']}")
            report.append(f"  Solution: {violation['solution']}")
            report.append("")

        if result["recommendations"]:
            report.append("Recommendations:")
            for rec in result["recommendations"]:
                report.append(f"  - {rec}")

        return {
            "passed": False,
            "fixed_code": None,  # 향후 자동 수정 기능 추가 가능
            "report": "\n".join(report),
        }


def check_file(file_path: str) -> Dict:
    """파일 검증"""
    guard = PreExecutionGuard()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"passed": False, "report": f"[ERROR] Failed to read file: {e}"}

    return guard.enforce(code)


def check_snippet(code: str) -> Dict:
    """코드 스니펫 검증"""
    guard = PreExecutionGuard()
    return guard.enforce(code)


if __name__ == "__main__":
    # 자가 테스트
    print("[TEST] Pre-Execution Guard")
    print("=" * 60)

    # Test 1: print with emoji (should fail)
    test_code_bad = """
def test():
    result = "완료"
    print(f"[OK] {result}")  # 이건 괜찮음
    print("📝 Update History")  # 이건 문제됨
"""

    print("\n[TEST 1] Code with print(emoji):")
    result = check_snippet(test_code_bad)
    print(result["report"])

    # Test 2: Clean code (should pass)
    test_code_good = """
def test():
    result = "완료"
    print(f"[OK] {result}")
    # 이모지는 파일에만 쓰기
    file.write_text("📝 Update History")
"""

    print("\n[TEST 2] Clean code:")
    result = check_snippet(test_code_good)
    print(result["report"])
