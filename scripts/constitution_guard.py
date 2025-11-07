#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constitution Guard - Pre-commit Hook for Stage 5
================================================

목적: Git commit 시 Constitution 자동 검증 (P4, P5, P7, P10)

성능 목표: <3초 (변경된 파일만 검증)

검증 항목:
- P4: SOLID 기본 검증 (eval() 금지, 간단 위반)
- P5: 보안 기본 검증 (secrets, SQL injection 패턴)
- P7: Hallucination 방지 (TODO 과다, 미완성 함수)
- P10: Windows 인코딩 (이모지 금지)

VibeCoding Stage 5: Hook 시스템
"""

import sys
import subprocess
import re
import time
from typing import List, Dict

# ANSI 색상 (Windows 호환)
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class ConstitutionGuard:
    """Constitution 기반 Pre-commit 검증"""

    def __init__(self, files: List[str]):
        self.files = [f for f in files if f.endswith(".py")]
        self.violations = []
        self.warnings = []

    def _safe_print(self, text: str) -> str:
        """Windows 콘솔에서 안전하게 출력 (non-ASCII 안전 처리)"""
        # Keep only ASCII printable + Korean characters
        result = []
        for char in text:
            code = ord(char)
            if code < 128:  # ASCII
                result.append(char)
            elif 0xAC00 <= code <= 0xD7A3:  # Korean Hangul
                result.append(char)
            elif 0x3131 <= code <= 0x318E:  # Korean Jamo
                result.append(char)
            else:  # Other Unicode (emojis, etc.)
                result.append("?")
        return "".join(result)

    def _remove_comments_and_strings(self, content: str) -> str:
        """주석과 문자열을 제거한 순수 코드만 반환 (false positive 방지)"""
        # Remove single-line comments
        code = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
        # Remove triple-quoted strings
        code = re.sub(r'"""[\s\S]*?"""', "", code)
        code = re.sub(r"'''[\s\S]*?'''", "", code)
        # Remove single/double quoted strings
        code = re.sub(r'"[^"\\\\]*(\\\\.[^"\\\\]*)*"', "", code)
        code = re.sub(r"'[^'\\\\]*(\\\\.[^'\\\\]*)*'", "", code)
        return code

    def check_p4_solid(self, file_path: str, content: str) -> List[Dict]:
        """P4: SOLID 기본 검증"""
        violations = []

        # Clean code (remove comments/strings to avoid false positives)
        code = self._remove_comments_and_strings(content)

        # 1. eval() 사용 금지 (보안 + SOLID)
        if re.search(r"\beval\s*\(", code):
            violations.append(
                {
                    "article": "P4",
                    "severity": "HIGH",
                    "rule": "eval() 사용 금지",
                    "reason": "eval()은 보안 위험 + 코드 이해 어려움 (SOLID 위반)",
                    "fix": "ast.literal_eval() 또는 json.loads() 사용",
                }
            )

        # 2. 과도한 함수 길이 (Single Responsibility)
        lines = content.split("\n")
        in_function = False
        func_start = 0
        func_name = ""

        for i, line in enumerate(lines):
            # 함수 시작
            if re.match(r"^\s*def\s+(\w+)", line):
                if in_function and (i - func_start) > 100:
                    violations.append(
                        {
                            "article": "P4",
                            "severity": "MEDIUM",
                            "rule": "Single Responsibility",
                            "reason": f"함수 {func_name}이 {i - func_start}줄 (>100줄)",
                            "fix": "작은 함수로 분리 권장",
                        }
                    )
                in_function = True
                func_start = i
                match = re.match(r"^\s*def\s+(\w+)", line)
                func_name = match.group(1)

            # 클래스/파일 끝
            elif line.strip() == "" or (not line.startswith(" ") and in_function):
                if in_function and (i - func_start) > 100:
                    violations.append(
                        {
                            "article": "P4",
                            "severity": "MEDIUM",
                            "rule": "Single Responsibility",
                            "reason": f"함수 {func_name}이 {i - func_start}줄 (>100줄)",
                            "fix": "작은 함수로 분리 권장",
                        }
                    )
                in_function = False

        return violations

    def check_p5_security(self, file_path: str, content: str) -> List[Dict]:
        """P5: 보안 기본 검증"""
        violations = []

        # Clean code (remove comments/strings to avoid false positives)
        code = self._remove_comments_and_strings(content)

        # 1. SQL Injection 패턴
        if re.search(r'execute\s*\(\s*["\'].*%s.*["\'].*%', code):
            violations.append(
                {
                    "article": "P5",
                    "severity": "HIGH",
                    "rule": "SQL Injection 방지",
                    "reason": "String formatting으로 SQL 쿼리 생성",
                    "fix": "Parameterized queries 사용 (?, :param)",
                }
            )

        # 2. 하드코딩된 시크릿 (간단 패턴) - 원본 content 사용 (실제 코드에서만)
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Password 하드코딩"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API Key 하드코딩"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Secret 하드코딩"),
        ]

        for pattern, name in secret_patterns:
            # Use code to check, but only if not in comments/examples
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(
                    {
                        "article": "P5",
                        "severity": "CRITICAL",
                        "rule": "시크릿 하드코딩 금지",
                        "reason": f"{name} 발견",
                        "fix": "환경 변수 또는 .env 파일 사용",
                    }
                )

        # 3. os.system() 사용 (command injection 위험)
        if re.search(r"\bos\.system\s*\(", code):
            violations.append(
                {
                    "article": "P5",
                    "severity": "HIGH",
                    "rule": "Command Injection 방지",
                    "reason": "os.system() 사용",
                    "fix": "subprocess.run() with shell=False 사용",
                }
            )

        return violations

    def check_p7_hallucination(self, file_path: str, content: str) -> List[Dict]:
        """P7: Hallucination 방지"""
        violations = []

        # 1. TODO 과다 (미완성 표시)
        todo_count = len(re.findall(r"#\s*TODO|#\s*FIXME|#\s*XXX", content, re.IGNORECASE))
        if todo_count > 5:
            violations.append(
                {
                    "article": "P7",
                    "severity": "MEDIUM",
                    "rule": "Hallucination 방지",
                    "reason": f"TODO/FIXME가 {todo_count}개 (>5개)",
                    "fix": "미완성 부분 구현 또는 이슈 트래커로 이동",
                }
            )

        # 2. pass only 함수 (구현 안 함)
        pass_only_funcs = re.findall(r'def\s+(\w+)\([^)]*\):\s*(?:"""[^"]*"""\s*)?pass\s*$', content, re.MULTILINE)
        if pass_only_funcs:
            violations.append(
                {
                    "article": "P7",
                    "severity": "HIGH",
                    "rule": "Hallucination 방지",
                    "reason": f'구현 안 된 함수: {", ".join(pass_only_funcs[:3])}',
                    "fix": "함수 구현 또는 NotImplementedError raise",
                }
            )

        # 3. 주석만 있고 코드 없음 (의도 표현만)
        lines = content.split("\n")
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

        if code_lines > 0 and (comment_lines / code_lines) > 2:
            violations.append(
                {
                    "article": "P7",
                    "severity": "LOW",
                    "rule": "Hallucination 방지",
                    "reason": f"주석이 코드보다 2배 많음 ({comment_lines} vs {code_lines})",
                    "fix": "주석 대신 코드 작성 권장",
                }
            )

        return violations

    def check_p10_encoding(self, file_path: str, content: str) -> List[Dict]:
        """P10: Windows 인코딩 (이모지 금지)"""
        violations = []

        # 1. 이모지 감지 (commonly used ones that cause Windows issues)
        emoji_pattern = re.compile(
            "["
            "\u2600-\u26ff"  # Miscellaneous Symbols (OK/X/! marks)
            "\u2700-\u27bf"  # Dingbats
            "\U0001f600-\U0001f64f"  # Emoticons
            "\U0001f300-\U0001f5ff"  # Symbols & Pictographs
            "\U0001f680-\U0001f6ff"  # Transport & Map
            "\U0001f1e0-\U0001f1ff"  # Flags
            "]",
            flags=re.UNICODE,
        )

        emojis = emoji_pattern.findall(content)
        if emojis:
            violations.append(
                {
                    "article": "P10",
                    "severity": "CRITICAL",
                    "rule": "Windows 인코딩",
                    "reason": f'Python 코드에 이모지 사용: {" ".join(emojis[:5])}',
                    "fix": "ASCII 대체 문자 사용 ([OK], [FAIL], [INFO] 등)",
                }
            )

        # 2. UTF-8 인코딩 선언 확인
        lines = content.split("\n")
        has_encoding = any(re.search(r"#.*coding[:=]\s*utf-?8", line, re.IGNORECASE) for line in lines[:5])

        if not has_encoding and len(content) > 100:
            violations.append(
                {
                    "article": "P10",
                    "severity": "LOW",
                    "rule": "UTF-8 인코딩 선언",
                    "reason": "UTF-8 인코딩 선언 없음",
                    "fix": "파일 상단에 # -*- coding: utf-8 -*- 추가 권장",
                }
            )

        return violations

    def validate_file(self, file_path: str) -> List[Dict]:
        """파일 검증 (모든 Constitution 조항)"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            violations = []
            violations.extend(self.check_p4_solid(file_path, content))
            violations.extend(self.check_p5_security(file_path, content))
            violations.extend(self.check_p7_hallucination(file_path, content))
            violations.extend(self.check_p10_encoding(file_path, content))

            return violations

        except Exception as e:
            return [
                {
                    "article": "ERROR",
                    "severity": "LOW",
                    "rule": "File Read",
                    "reason": f"파일 읽기 실패: {e}",
                    "fix": "파일 확인",
                }
            ]

    def run(self) -> bool:
        """전체 검증 실행"""
        if not self.files:
            print(f"{GREEN}[OK]{RESET} No Python files to check")
            return True

        print(f"\n{BOLD}Constitution Guard - Pre-commit Validation{RESET}")
        print(f"Checking {len(self.files)} Python file(s)...\n")

        start_time = time.time()

        # 파일별 검증
        for file_path in self.files:
            file_violations = self.validate_file(file_path)

            for v in file_violations:
                v["file"] = file_path

                if v["severity"] in ["CRITICAL", "HIGH"]:
                    self.violations.append(v)
                else:
                    self.warnings.append(v)

        elapsed = time.time() - start_time

        # 결과 출력
        self._print_results(elapsed)

        # CRITICAL/HIGH 위반 시 커밋 차단
        return len(self.violations) == 0

    def _print_results(self, elapsed: float):
        """결과 출력"""
        print(f"\n{BOLD}Results:{RESET}")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Files: {len(self.files)}")
        print(f"  Violations: {len(self.violations)}")
        print(f"  Warnings: {len(self.warnings)}")

        # 위반 사항 출력
        if self.violations:
            print(f"\n{RED}{BOLD}[BLOCKED]{RESET} Constitution violations found:\n")

            for v in self.violations:
                print(f"{RED}[{v['severity']}]{RESET} {BOLD}{v['article']}{RESET}: {v['rule']}")
                print(f"  File: {v['file']}")
                # Windows-safe output
                reason = self._safe_print(v["reason"])
                fix_text = self._safe_print(v["fix"])
                print(f"  Reason: {reason}")
                print(f"  Fix: {BLUE}{fix_text}{RESET}")
                print()

        # 경고 출력
        if self.warnings:
            print(f"{YELLOW}Warnings (non-blocking):{RESET}\n")

            for w in self.warnings[:3]:  # 최대 3개만
                print(f"{YELLOW}[{w['severity']}]{RESET} {w['article']}: {w['rule']}")
                print(f"  File: {w['file']}")
                fix_text = self._safe_print(w["fix"])
                print(f"  Fix: {fix_text}")
                print()

            if len(self.warnings) > 3:
                print(f"  ... and {len(self.warnings) - 3} more warnings")

        # 성공
        if not self.violations:
            print(f"\n{GREEN}{BOLD}[OK]{RESET} Constitution check passed!")

            if elapsed < 3:
                print(f"{GREEN}Performance: {elapsed:.2f}s < 3s target{RESET}")
            else:
                print(f"{YELLOW}Performance: {elapsed:.2f}s (target: <3s){RESET}")


def main():
    """메인 실행"""
    # Git staged 파일 가져오기
    result = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"{RED}[ERROR]{RESET} Failed to get staged files")
        sys.exit(1)

    files = result.stdout.strip().split("\n")
    files = [f for f in files if f]

    # Constitution Guard 실행
    guard = ConstitutionGuard(files)
    success = guard.run()

    if not success:
        print(f"\n{RED}{BOLD}Commit blocked by Constitution Guard{RESET}")
        print(f"{YELLOW}Fix the violations above and try again{RESET}")
        print(f"{BLUE}Or use: git commit --no-verify (not recommended){RESET}\n")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
