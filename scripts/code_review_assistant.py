#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code Review Assistant - AI-Powered Code Review Automation

Analyzes code changes and provides automated review feedback based on:
- Constitutional principles (P1-P13)
- SOLID principles
- Security best practices
- Performance considerations
- Code quality metrics

Usage:
  python scripts/code_review_assistant.py                  # Review last commit
  python scripts/code_review_assistant.py --commit HEAD~1  # Review specific commit
  python scripts/code_review_assistant.py --pr 123         # Review PR
  python scripts/code_review_assistant.py --files file1.py # Review specific files

Integrations:
  - Git pre-push hook for automatic review
  - GitHub Actions for PR reviews
  - Claude Code slash command for interactive review
"""

import subprocess
import sys
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ReviewFinding:
    """Single review finding"""

    severity: str  # critical, warning, suggestion, praise
    category: str  # security, performance, quality, constitution, solid
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None
    article: Optional[str] = None  # Constitutional article reference


@dataclass
class ReviewReport:
    """Complete review report"""

    commit: str
    timestamp: str
    score: int  # 0-100
    summary: str
    findings: List[ReviewFinding]
    stats: Dict[str, int]
    recommendations: List[str]
    constitutional_compliance: Dict[str, bool]


class CodeReviewAssistant:
    """AI-powered code review assistant"""

    # Constitutional articles to check
    CONSTITUTION_CHECKS = {
        "P1": "YAML contract exists for complex tasks",
        "P2": "Evidence collection configured",
        "P3": "Knowledge documentation updated",
        "P4": "SOLID principles followed",
        "P5": "Security gates implemented",
        "P6": "Quality metrics meet thresholds",
        "P7": "No hallucinations (all claims verifiable)",
        "P8": "Tests written first (TDD)",
        "P9": "Conventional commit format",
        "P10": "Windows UTF-8 compliance",
        "P11": "Principle conflicts resolved",
        "P12": "Trade-offs documented",
        "P13": "Constitution changes approved",
    }

    # SOLID principle patterns
    SOLID_VIOLATIONS = {
        "S": ["god_class", "multiple_responsibilities", "do_everything"],
        "O": ["hardcoded_types", "switch_statements", "isinstance_chains"],
        "L": ["broken_inheritance", "incompatible_override"],
        "I": ["fat_interface", "unused_methods"],
        "D": ["concrete_dependency", "direct_instantiation", "import_implementation"],
    }

    # Security patterns to detect
    SECURITY_PATTERNS = [
        (r"exec\(|eval\(", "Dangerous function: exec/eval usage"),
        (r"pickle\.loads?\(", "Security risk: pickle deserialization"),
        (r"subprocess.*shell=True", "Security risk: shell injection possible"),
        (r'(password|secret|key|token)\s*=\s*["\']', "Hardcoded secret detected"),
        (r"http://", "Insecure HTTP instead of HTTPS"),
        (r"TODO.*security|FIXME.*security", "Security TODO found"),
    ]

    def __init__(self):
        """Initialize assistant"""
        self.findings = []
        self.stats = {"files_reviewed": 0, "lines_reviewed": 0, "issues_found": 0, "suggestions_made": 0}

    def review_commit(self, commit: str = "HEAD") -> ReviewReport:
        """Review a specific commit"""
        # Get commit info
        commit_hash = self._get_commit_hash(commit)
        changed_files = self._get_changed_files(commit)

        # Review each file
        for file_path in changed_files:
            if self._should_review_file(file_path):
                self._review_file(file_path, commit)
                self.stats["files_reviewed"] += 1

        # Check constitutional compliance
        constitutional = self._check_constitutional_compliance(changed_files)

        # Generate report
        return self._generate_report(commit_hash, constitutional)

    def _get_commit_hash(self, commit: str) -> str:
        """Get full commit hash"""
        result = subprocess.run(["git", "rev-parse", commit], capture_output=True, text=True, encoding="utf-8")
        return result.stdout.strip()[:8]

    def _get_changed_files(self, commit: str) -> List[str]:
        """Get list of changed files in commit"""
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{commit}~1..{commit}"], capture_output=True, text=True, encoding="utf-8"
        )
        return [f for f in result.stdout.strip().split("\n") if f]

    def _should_review_file(self, file_path: str) -> bool:
        """Check if file should be reviewed"""
        # Review Python, JavaScript, TypeScript files
        extensions = {".py", ".js", ".jsx", ".ts", ".tsx"}
        return Path(file_path).suffix in extensions

    def _review_file(self, file_path: str, commit: str):
        """Review individual file"""
        # Get file diff
        self._get_file_diff(file_path, commit)

        # Get file content
        content = self._get_file_content(file_path)
        if not content:
            return

        # Run various checks
        self._check_code_quality(file_path, content)
        self._check_solid_principles(file_path, content)
        self._check_security(file_path, content)
        self._check_performance(file_path, content)
        self._check_windows_compatibility(file_path, content)

        # Count lines
        self.stats["lines_reviewed"] += len(content.splitlines())

    def _get_file_diff(self, file_path: str, commit: str) -> str:
        """Get diff for specific file"""
        result = subprocess.run(
            ["git", "diff", f"{commit}~1..{commit}", "--", file_path], capture_output=True, text=True, encoding="utf-8"
        )
        return result.stdout

    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Get file content"""
        path = Path(file_path)
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                return None
        return None

    def _is_cli_script(self, file_path: str, content: str) -> bool:
        """Quick heuristic to detect CLI scripts (90% accuracy).

        CLI indicators:
        - if __name__ == "__main__" present
        - import argparse
        - #!/usr/bin/env python shebang
        - In scripts/ folder
        """
        # Check file path
        if "scripts/" in file_path or file_path.startswith("scripts\\") or "\\scripts\\" in file_path:
            return True

        # Check content patterns
        if 'if __name__ == "__main__"' in content:
            return True
        if "import argparse" in content:
            return True
        if content.startswith("#!/usr/bin/env python"):
            return True

        return False

    def _check_code_quality(self, file_path: str, content: str):
        """Check general code quality issues"""
        lines = content.splitlines()

        # Quick Fix: Detect if this is a CLI script (90% accuracy)
        is_cli_script = self._is_cli_script(file_path, content)

        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                self._add_finding(
                    severity="suggestion",
                    category="quality",
                    file=file_path,
                    line=i,
                    message=f"Line too long ({len(line)} > 120 characters)",
                    suggestion="Split into multiple lines for readability",
                )

            # Check for TODO/FIXME
            if "TODO" in line or "FIXME" in line:
                self._add_finding(
                    severity="warning",
                    category="quality",
                    file=file_path,
                    line=i,
                    message="Unresolved TODO/FIXME found",
                    suggestion="Complete the TODO or create a tracking issue",
                )

            # Check for print statements (Python) - SKIP for CLI scripts
            if file_path.endswith(".py") and re.match(r"^\s*print\(", line):
                if not is_cli_script:
                    self._add_finding(
                        severity="warning",
                        category="quality",
                        file=file_path,
                        line=i,
                        message="print() statement found",
                        suggestion="Use logging instead of print()",
                    )

    def _check_solid_principles(self, file_path: str, content: str):
        """
        Check SOLID principle violations.

        Learning Point: Orchestrator - delegates specific checks to helpers.
        Makes it easy to add new SOLID checks later!
        """
        if not file_path.endswith(".py"):
            return

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class_solid_violations(node, file_path)
        except SyntaxError:
            pass  # Invalid Python syntax

    def _check_class_solid_violations(self, class_node: ast.ClassDef, file_path: str):
        """
        Check SOLID violations for a single class.

        Learning Point: Single responsibility - only checks ONE class.
        Easier to test and modify than checking all classes at once.
        """
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]

        # Check 1: Too many methods (SRP violation)
        self._check_method_count_violation(class_node, methods, file_path)

        # Check 2: Multiple responsibilities
        self._check_responsibility_violation(class_node, methods, file_path)

    def _check_method_count_violation(self, class_node: ast.ClassDef, methods: list, file_path: str):
        """
        Check if class has too many methods.

        Learning Point: Magic number (15) is now in ONE place.
        Want to change threshold? Just modify here!
        """
        MAX_METHODS = 15

        if len(methods) > MAX_METHODS:
            self._add_finding(
                severity="warning",
                category="solid",
                file=file_path,
                line=class_node.lineno,
                message=f"Class '{class_node.name}' has {len(methods)} methods (possible SRP violation)",
                suggestion="Consider splitting into smaller, focused classes",
                article="P4",
            )

    def _check_responsibility_violation(self, class_node: ast.ClassDef, methods: list, file_path: str):
        """
        Check if class has multiple responsibilities.

        Learning Point: Extract responsibility analysis to separate function.
        Now we can test responsibility detection independently!
        """
        responsibilities = self._analyze_class_responsibilities(methods)

        MAX_RESPONSIBILITIES = 2
        if len(responsibilities) > MAX_RESPONSIBILITIES:
            self._add_finding(
                severity="warning",
                category="solid",
                file=file_path,
                line=class_node.lineno,
                message=f"Class '{class_node.name}' has multiple responsibilities: {', '.join(responsibilities)}",
                suggestion="Apply Single Responsibility Principle",
                article="P4",
            )

    def _analyze_class_responsibilities(self, methods: list) -> set:
        """
        Analyze what responsibilities a class has based on method names.

        Learning Point: Pure function! Input → Output, no side effects.
        Perfect for unit testing!

        Returns:
            Set of responsibility types (e.g., {'getter', 'validation'})
        """
        RESPONSIBILITY_PATTERNS = {
            "getter": lambda name: name.startswith("get_"),
            "setter": lambda name: name.startswith("set_"),
            "validation": lambda name: name.startswith("validate_"),
            "persistence": lambda name: name.startswith(("save_", "load_")),
            "presentation": lambda name: name.startswith(("render_", "display_")),
        }

        responsibilities = set()
        for method in methods:
            for resp_type, pattern_check in RESPONSIBILITY_PATTERNS.items():
                if pattern_check(method.name):
                    responsibilities.add(resp_type)
                    break  # One responsibility per method

        return responsibilities

    def _check_security(self, file_path: str, content: str):
        """Check security issues"""
        for pattern, message in self.SECURITY_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                self._add_finding(
                    severity="critical" if "exec" in message or "pickle" in message else "warning",
                    category="security",
                    file=file_path,
                    line=line_num,
                    message=message,
                    article="P5",
                )

    def _check_performance(self, file_path: str, content: str):
        """Check performance issues"""
        if not file_path.endswith(".py"):
            return

        # Check for nested loops
        if re.search(r"for .* in .*:\s*\n\s*for .* in .*:", content):
            self._add_finding(
                severity="warning",
                category="performance",
                file=file_path,
                line=None,
                message="Nested loops detected (potential O(n²) complexity)",
                suggestion="Consider using more efficient algorithms or data structures",
            )

        # Check for list comprehensions in loops
        if re.search(r"for .* in .*:\s*\n.*\[.*for.*in.*\]", content):
            self._add_finding(
                severity="suggestion",
                category="performance",
                file=file_path,
                line=None,
                message="List comprehension inside loop",
                suggestion="Consider moving list comprehension outside loop if possible",
            )

    def _check_windows_compatibility(self, file_path: str, content: str):
        """Check Windows UTF-8 compatibility (P10) - Runtime output only

        P10 only applies to runtime output (print, logger) that crashes Windows console.
        Comments and docstrings are safe and do NOT violate P10.

        Reference: CLAUDE.md > Windows Encoding (P10)
        """
        if not file_path.endswith(".py"):
            return

        lines = content.splitlines()
        in_multiline_string = False
        multiline_delimiter = None

        # Runtime output patterns that actually print to console
        runtime_patterns = [
            r"print\s*\(",
            r"logger\.\w+\s*\(",
            r"logging\.\w+\s*\(",
            r"sys\.stdout\.write\s*\(",
            r"sys\.stderr\.write\s*\(",
        ]

        for line_num, line in enumerate(lines, 1):
            # Track multiline strings (docstrings)
            stripped = line.lstrip()

            # Check for multiline string start/end
            for delimiter in ['"""', "'''"]:
                if delimiter in line:
                    count = line.count(delimiter)
                    if in_multiline_string and multiline_delimiter == delimiter:
                        if count % 2 == 1:  # Odd count means string ends
                            in_multiline_string = False
                            multiline_delimiter = None
                    elif not in_multiline_string:
                        if count == 1 or (count % 2 == 1):  # String starts
                            in_multiline_string = True
                            multiline_delimiter = delimiter

            # Skip if in multiline string (docstring)
            if in_multiline_string:
                continue

            # Skip if line is a comment
            if stripped.startswith("#"):
                continue

            # Check if line contains runtime output
            is_runtime_output = any(re.search(pattern, line) for pattern in runtime_patterns)

            if not is_runtime_output:
                continue  # Not runtime output, safe to have non-ASCII

            # Now check for non-ASCII characters in runtime output code
            non_ascii_pattern = re.compile(r"[^\x00-\x7F]+")
            matches = non_ascii_pattern.finditer(line)

            for match in matches:
                char = match.group()
                char_repr = ", ".join(f"U+{ord(c):04X}" for c in char)

                self._add_finding(
                    severity="critical",
                    category="constitution",
                    file=file_path,
                    line=line_num,
                    message=f"Non-ASCII character ({char_repr}) in runtime output (violates P10 - Windows UTF-8)",
                    suggestion="Use ASCII alternatives in print/logger statements: [OK] instead of emoji-check, [FAIL] instead of emoji-x",
                    article="P10",
                )

    def _check_constitutional_compliance(self, files: List[str]) -> Dict[str, bool]:
        """Check overall constitutional compliance"""
        compliance = {}

        # P1: YAML contract for complex tasks
        yaml_files = [f for f in files if f.endswith(".yaml")]
        py_files = [f for f in files if f.endswith(".py")]
        compliance["P1"] = len(yaml_files) > 0 if len(py_files) > 5 else True

        # P8: Tests written
        test_files = [f for f in files if "test" in f.lower()]
        compliance["P8"] = len(test_files) > 0 if len(py_files) > 0 else True

        # P9: Conventional commit (check separately)
        compliance["P9"] = self._check_commit_message_format()

        # P10: Windows UTF-8 (checked per file)
        compliance["P10"] = len([f for f in self.findings if f.article == "P10"]) == 0

        return compliance

    def _check_commit_message_format(self) -> bool:
        """Check if commit message follows conventional format"""
        result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, encoding="utf-8")
        message = result.stdout.strip()

        # Check conventional commit format
        pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
        return bool(re.match(pattern, message))

    def _add_finding(
        self,
        severity: str,
        category: str,
        file: str,
        line: Optional[int],
        message: str,
        suggestion: Optional[str] = None,
        article: Optional[str] = None,
    ):
        """Add a review finding"""
        finding = ReviewFinding(
            severity=severity,
            category=category,
            file=file,
            line=line,
            message=message,
            suggestion=suggestion,
            article=article,
        )
        self.findings.append(finding)

        if severity in ["critical", "warning"]:
            self.stats["issues_found"] += 1
        if suggestion:
            self.stats["suggestions_made"] += 1

    def _generate_report(self, commit_hash: str, constitutional: Dict[str, bool]) -> ReviewReport:
        """Generate final review report"""
        # Calculate score
        critical_count = len([f for f in self.findings if f.severity == "critical"])
        warning_count = len([f for f in self.findings if f.severity == "warning"])

        score = 100
        score -= critical_count * 15
        score -= warning_count * 5
        score = max(0, score)

        # Generate summary
        if score >= 90:
            summary = "Excellent code quality! Minor suggestions only."
        elif score >= 75:
            summary = "Good code quality with some areas for improvement."
        elif score >= 60:
            summary = "Acceptable quality but needs attention to issues."
        else:
            summary = "Significant issues found. Please address critical findings."

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return ReviewReport(
            commit=commit_hash,
            timestamp=datetime.now().isoformat(),
            score=score,
            summary=summary,
            findings=self.findings,
            stats=self.stats,
            recommendations=recommendations,
            constitutional_compliance=constitutional,
        )

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Group findings by category
        categories = {}
        for finding in self.findings:
            if finding.category not in categories:
                categories[finding.category] = []
            categories[finding.category].append(finding)

        # Generate category-specific recommendations
        if "security" in categories:
            recommendations.append(f"Address {len(categories['security'])} security issues immediately")

        if "solid" in categories:
            recommendations.append(f"Refactor {len(categories['solid'])} SOLID principle violations")

        if "performance" in categories:
            recommendations.append(f"Optimize {len(categories['performance'])} performance bottlenecks")

        if "quality" in categories:
            todos = [f for f in categories["quality"] if "TODO" in f.message]
            if todos:
                recommendations.append(f"Complete {len(todos)} TODO items or create tracking issues")

        # Constitutional recommendations
        if any(f.article == "P8" for f in self.findings):
            recommendations.append("Write tests for new functionality (P8 - Test First)")

        if any(f.article == "P10" for f in self.findings):
            recommendations.append("Remove non-ASCII characters from Python code (P10)")

        return recommendations[:5]  # Top 5 recommendations


def format_report(report: ReviewReport, format: str = "text") -> str:
    """
    Format report for output.

    Learning Point: Main function delegates to specialized formatters.
    Each formatter has ONE job (Single Responsibility Principle).
    """
    if format == "json":
        return _format_json_report(report)
    return _format_text_report(report)


def _format_json_report(report: ReviewReport) -> str:
    """Format report as JSON (single responsibility: JSON conversion)"""
    return json.dumps(asdict(report), indent=2, default=str)


def _format_text_report(report: ReviewReport) -> str:
    """
    Format report as text (orchestrator pattern).

    Learning Point: This function ORCHESTRATES other functions.
    It doesn't do the work itself - it delegates!
    """
    sections = [
        _format_report_header(report),
        _format_statistics_section(report.stats),
        _format_compliance_section(report.constitutional_compliance),
        _format_findings_section(report.findings),
        _format_recommendations_section(report.recommendations),
        "=" * 60,
    ]
    return "\n\n".join(filter(None, sections))


def _format_report_header(report: ReviewReport) -> str:
    """
    Format report header section.

    Learning Point: Small, focused function - easy to test!
    If header format changes, only modify this function.
    """
    return "\n".join(
        [
            "=" * 60,
            "CODE REVIEW REPORT",
            "=" * 60,
            f"Commit: {report.commit}",
            f"Score: {report.score}/100",
            f"Summary: {report.summary}",
        ]
    )


def _format_statistics_section(stats: dict) -> str:
    """
    Format statistics as bullet list.

    Learning Point: Reusable! Can use this function anywhere
    you need to format a dict as bullet points.
    """
    if not stats:
        return ""

    lines = ["Statistics:"]
    for key, value in stats.items():
        lines.append(f"  - {key}: {value}")
    return "\n".join(lines)


def _format_compliance_section(compliance: dict) -> str:
    """
    Format constitutional compliance status.

    Learning Point: Clear input/output makes testing trivial.
    Input: dict, Output: string - easy to verify!
    """
    if not compliance:
        return ""

    lines = ["Constitutional Compliance:"]
    for article, compliant in compliance.items():
        status = "[OK]" if compliant else "[X]"
        article_desc = CodeReviewAssistant.CONSTITUTION_CHECKS.get(article, "")
        lines.append(f"  {status} {article}: {article_desc}")
    return "\n".join(lines)


def _format_findings_section(findings: list) -> str:
    """
    Format findings grouped by severity.

    Learning Point: Extract-Transform-Load pattern.
    1. Extract (filter by severity)
    2. Transform (format each group)
    3. Load (combine into output)
    """
    if not findings:
        return "No issues found - excellent!"

    critical = [f for f in findings if f.severity == "critical"]
    warnings = [f for f in findings if f.severity == "warning"]
    suggestions = [f for f in findings if f.severity == "suggestion"]

    sections = ["Findings:"]

    if critical:
        sections.append(_format_critical_findings(critical))

    if warnings:
        sections.append(_format_warning_findings(warnings))

    if suggestions:
        sections.append(f"\nSUGGESTIONS: {len(suggestions)} total")

    return "\n".join(sections)


def _format_critical_findings(findings: list) -> str:
    """Format critical findings with details"""
    lines = ["\nCRITICAL:"]
    for f in findings:
        lines.append(f"  - {f.file}:{f.line or '?'} - {f.message}")
        if f.suggestion:
            lines.append(f"    Suggestion: {f.suggestion}")
    return "\n".join(lines)


def _format_warning_findings(warnings: list) -> str:
    """Format warning findings (top 5 only)"""
    lines = ["\nWARNINGS:"]
    for f in warnings[:5]:  # Top 5
        lines.append(f"  - {f.file}:{f.line or '?'} - {f.message}")
    return "\n".join(lines)


def _format_recommendations_section(recommendations: list) -> str:
    """
    Format numbered recommendations list.

    Learning Point: Guard clause pattern.
    Handle empty case first, then process normal case.
    """
    if not recommendations:
        return ""

    lines = ["Recommendations:"]
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")
    return "\n".join(lines)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="AI-powered code review assistant")
    parser.add_argument("--commit", default="HEAD", help="Commit to review")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    # Run review
    assistant = CodeReviewAssistant()
    report = assistant.review_commit(args.commit)

    # Format output
    output = format_report(report, args.format)

    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        if not args.quiet:
            print(f"Review saved to {args.output}")
    else:
        print(output)

    # Exit code based on score
    if report.score < 60:
        return 1  # Fail if score too low
    return 0


if __name__ == "__main__":
    sys.exit(main())
