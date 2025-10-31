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

    def _check_code_quality(self, file_path: str, content: str):
        """Check general code quality issues"""
        lines = content.splitlines()

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

            # Check for print statements (Python)
            if file_path.endswith(".py") and re.match(r"^\s*print\(", line):
                self._add_finding(
                    severity="warning",
                    category="quality",
                    file=file_path,
                    line=i,
                    message="print() statement found",
                    suggestion="Use logging instead of print()",
                )

    def _check_solid_principles(self, file_path: str, content: str):
        """Check SOLID principle violations"""
        if not file_path.endswith(".py"):
            return

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check Single Responsibility
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 15:
                        self._add_finding(
                            severity="warning",
                            category="solid",
                            file=file_path,
                            line=node.lineno,
                            message=f"Class '{node.name}' has {len(methods)} methods (possible SRP violation)",
                            suggestion="Consider splitting into smaller, focused classes",
                            article="P4",
                        )

                    # Check for multiple responsibilities
                    responsibilities = set()
                    for method in methods:
                        if method.name.startswith("get_"):
                            responsibilities.add("getter")
                        elif method.name.startswith("set_"):
                            responsibilities.add("setter")
                        elif method.name.startswith("validate_"):
                            responsibilities.add("validation")
                        elif method.name.startswith("save_") or method.name.startswith("load_"):
                            responsibilities.add("persistence")
                        elif method.name.startswith("render_") or method.name.startswith("display_"):
                            responsibilities.add("presentation")

                    if len(responsibilities) > 2:
                        self._add_finding(
                            severity="warning",
                            category="solid",
                            file=file_path,
                            line=node.lineno,
                            message=f"Class '{node.name}' has multiple responsibilities: {', '.join(responsibilities)}",
                            suggestion="Apply Single Responsibility Principle",
                            article="P4",
                        )

        except SyntaxError:
            pass  # Invalid Python syntax

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
        """Check Windows UTF-8 compatibility (P10)"""
        if file_path.endswith(".py"):
            # Check for emojis in Python code
            emoji_pattern = re.compile(r"[^\x00-\x7F]+")
            matches = emoji_pattern.finditer(content)

            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                char = match.group()

                # Skip if it's in a comment or string
                line = content.splitlines()[line_num - 1]
                if "#" in line and line.index("#") < match.start() - content.rfind("\n", 0, match.start()):
                    continue  # It's in a comment, might be okay

                self._add_finding(
                    severity="critical",
                    category="constitution",
                    file=file_path,
                    line=line_num,
                    message=f"Non-ASCII character '{char}' found (violates P10 - Windows UTF-8)",
                    suggestion="Use ASCII alternatives in Python code",
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
    """Format report for output"""
    if format == "json":
        return json.dumps(asdict(report), indent=2, default=str)

    # Text format
    output = []
    output.append("=" * 60)
    output.append("CODE REVIEW REPORT")
    output.append("=" * 60)
    output.append(f"Commit: {report.commit}")
    output.append(f"Score: {report.score}/100")
    output.append(f"Summary: {report.summary}")
    output.append("")

    # Statistics
    output.append("Statistics:")
    for key, value in report.stats.items():
        output.append(f"  - {key}: {value}")
    output.append("")

    # Constitutional Compliance
    output.append("Constitutional Compliance:")
    for article, compliant in report.constitutional_compliance.items():
        status = "[OK]" if compliant else "[X]"
        output.append(f"  {status} {article}: {CodeReviewAssistant.CONSTITUTION_CHECKS.get(article, '')}")
    output.append("")

    # Findings by severity
    if report.findings:
        output.append("Findings:")

        critical = [f for f in report.findings if f.severity == "critical"]
        warnings = [f for f in report.findings if f.severity == "warning"]
        suggestions = [f for f in report.findings if f.severity == "suggestion"]

        if critical:
            output.append("\nCRITICAL:")
            for f in critical:
                output.append(f"  - {f.file}:{f.line or '?'} - {f.message}")
                if f.suggestion:
                    output.append(f"    Suggestion: {f.suggestion}")

        if warnings:
            output.append("\nWARNINGS:")
            for f in warnings[:5]:  # Top 5
                output.append(f"  - {f.file}:{f.line or '?'} - {f.message}")

        if suggestions:
            output.append(f"\nSUGGESTIONS: {len(suggestions)} total")
    else:
        output.append("No issues found - excellent!")

    # Recommendations
    if report.recommendations:
        output.append("\nRecommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            output.append(f"  {i}. {rec}")

    output.append("\n" + "=" * 60)

    return "\n".join(output)


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
