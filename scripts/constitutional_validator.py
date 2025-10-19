"""Constitutional Validator for Dev-Rules-Starter-Kit

Validates task files against the 10 constitutional articles defined in memory/constitution.md.
Ensures all development adheres to core principles before execution.
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class ConstitutionalViolation:
    """Represents a violation of constitutional principles"""

    article: str
    message: str
    severity: str  # 'error' or 'warning'
    context: Optional[str] = None


class ConstitutionalValidator:
    """Validates tasks against constitution.md principles"""

    def __init__(self, constitution_path: Optional[Path] = None):
        """Initialize validator with constitution document

        Args:
            constitution_path: Path to constitution.md (default: memory/constitution.md)
        """
        if constitution_path is None:
            constitution_path = Path(__file__).parent.parent / "memory" / "constitution.md"

        self.constitution_path = constitution_path
        self.constitution = self._load_constitution()

    def _load_constitution(self) -> Dict[str, str]:
        """Load and parse constitution document"""
        if not self.constitution_path.exists():
            raise FileNotFoundError(
                f"Constitution not found: {self.constitution_path}\n" "Run /speckit-constitution to create it."
            )

        content = self.constitution_path.read_text(encoding="utf-8")

        # Parse articles
        articles = {}
        article_pattern = r"### Article ([IVX]+): (.+?)\n"
        matches = re.finditer(article_pattern, content)

        for match in matches:
            article_num = match.group(1)
            article_title = match.group(2)
            articles[article_num] = article_title

        return articles

    def validate(self, tasks_file: Path) -> List[ConstitutionalViolation]:
        """Validate tasks against all constitutional articles

        Args:
            tasks_file: Path to tasks.md file

        Returns:
            List of violations found (empty if all pass)
        """
        if not tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {tasks_file}")

        tasks_content = tasks_file.read_text(encoding="utf-8")
        violations = []

        # Article I: Library-First Development
        violations.extend(self._check_library_first(tasks_content))

        # Article II: CLI Interface
        violations.extend(self._check_cli_interface(tasks_content))

        # Article III: Test-First Development (NON-NEGOTIABLE)
        violations.extend(self._check_test_first(tasks_content))

        # Article IV: Integration-First Testing
        violations.extend(self._check_integration_first(tasks_content))

        # Article V: Windows Encoding Compliance (CRITICAL)
        violations.extend(self._check_windows_encoding(tasks_content))

        # Article VI: Observability & Structured Logging
        violations.extend(self._check_observability(tasks_content))

        # Article VII: Simplicity & YAGNI
        violations.extend(self._check_simplicity(tasks_content))

        # Article VIII: Anti-Abstraction & Framework Trust
        violations.extend(self._check_anti_abstraction(tasks_content))

        # Article IX: Specification-Driven Development
        violations.extend(self._check_sdd(tasks_content))

        # Article X: Conventional Commits & Semantic Versioning
        violations.extend(self._check_conventional_commits(tasks_content))

        return violations

    def _check_library_first(self, content: str) -> List[ConstitutionalViolation]:
        """Article I: Every feature must begin as a standalone library"""
        violations = []

        # Check if tasks mention "library" or "module" structure
        if "library" not in content.lower() and "module" not in content.lower():
            # Only warn if implementation tasks exist
            if re.search(r"- \[ \] T\d+.*Implement", content):
                violations.append(
                    ConstitutionalViolation(
                        article="I",
                        message="No library/module structure mentioned. Consider organizing as standalone library.",
                        severity="warning",
                        context="Library-First Development",
                    )
                )

        return violations

    def _check_cli_interface(self, content: str) -> List[ConstitutionalViolation]:
        """Article II: All libraries must expose a CLI interface"""
        violations = []

        # Check if CLI tasks exist for implementation tasks
        has_implementation = bool(re.search(r"- \[ \] T\d+.*Implement", content))
        has_cli = bool(re.search(r"CLI|command.?line|argparse|click|typer", content, re.IGNORECASE))

        if has_implementation and not has_cli:
            violations.append(
                ConstitutionalViolation(
                    article="II",
                    message="No CLI interface tasks found. All libraries must expose CLI.",
                    severity="warning",
                    context="CLI Interface Mandate",
                )
            )

        return violations

    def _check_test_first(self, content: str) -> List[ConstitutionalViolation]:
        """Article III: Test-First Development (NON-NEGOTIABLE)"""
        violations = []

        # Find all task IDs
        task_pattern = r"- \[ \] (T\d+)(?:\s+\[P\])?\s+(?:\[US\d+\])?\s+(.+)"
        tasks = re.findall(task_pattern, content)

        # Separate test and implementation tasks
        test_tasks = []
        impl_tasks = []

        for task_id, description in tasks:
            if re.search(r"test|spec|contract", description, re.IGNORECASE):
                test_tasks.append((task_id, description))
            elif re.search(r"implement|create|add|build", description, re.IGNORECASE):
                impl_tasks.append((task_id, description))

        # Check if tests come before implementation
        if impl_tasks and not test_tasks:
            violations.append(
                ConstitutionalViolation(
                    article="III",
                    message="NO TEST TASKS FOUND. Article III is NON-NEGOTIABLE: Tests must come before implementation.",
                    severity="error",
                    context="Test-First Development",
                )
            )
        elif impl_tasks and test_tasks:
            # Extract task numbers for comparison
            first_impl_num = int(impl_tasks[0][0][1:])  # T001 -> 1
            first_test_num = int(test_tasks[0][0][1:])  # T010 -> 10

            if first_test_num > first_impl_num:
                violations.append(
                    ConstitutionalViolation(
                        article="III",
                        message=f"Tests ({test_tasks[0][0]}) appear AFTER implementation ({impl_tasks[0][0]}). "
                        f"Article III requires Test-First: tests must precede implementation.",
                        severity="error",
                        context="Test-First Development",
                    )
                )

        return violations

    def _check_integration_first(self, content: str) -> List[ConstitutionalViolation]:
        """Article IV: Integration-First Testing (minimize mocking)"""
        violations = []

        # Check for mock/stub patterns
        mock_patterns = [r"mock(?:ing)?", r"stub(?:bing)?", r"fake", r"dummy"]

        for pattern in mock_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(
                    ConstitutionalViolation(
                        article="IV",
                        message=f"Found '{pattern}' in tasks. Consider integration tests with real dependencies instead.",
                        severity="warning",
                        context="Integration-First Testing",
                    )
                )
                break  # Only warn once

        return violations

    def _check_windows_encoding(self, content: str) -> List[ConstitutionalViolation]:
        """Article V: Windows Encoding Compliance (CRITICAL - no emoji)"""
        violations = []

        # Check for emoji characters (U+1F300 to U+1F9FF ranges)
        emoji_pattern = r"[\U0001F300-\U0001F9FF]"
        emoji_matches = re.findall(emoji_pattern, content)

        if emoji_matches:
            violations.append(
                ConstitutionalViolation(
                    article="V",
                    message=f"EMOJI DETECTED: {len(emoji_matches)} emoji characters found. "
                    f"Article V CRITICAL: No emoji in code (cp949 compatibility).",
                    severity="error",
                    context="Windows Encoding Compliance",
                )
            )

        return violations

    def _check_observability(self, content: str) -> List[ConstitutionalViolation]:
        """Article VI: Observability & Structured Logging"""
        violations = []

        # Check if logging tasks exist
        has_implementation = bool(re.search(r"- \[ \] T\d+.*Implement", content))
        has_logging = bool(re.search(r"log(?:ging)?|observ|monitor|metric", content, re.IGNORECASE))

        if has_implementation and not has_logging:
            violations.append(
                ConstitutionalViolation(
                    article="VI",
                    message="No logging/observability tasks found. Consider adding structured logging.",
                    severity="warning",
                    context="Observability & Structured Logging",
                )
            )

        return violations

    def _check_simplicity(self, content: str) -> List[ConstitutionalViolation]:
        """Article VII: Simplicity & YAGNI (max 3 projects)"""
        violations = []

        # Count distinct projects/directories
        project_pattern = r"(?:in|at|create)\s+([a-zA-Z0-9_-]+/[a-zA-Z0-9_/-]+)"
        projects = set(re.findall(project_pattern, content))

        # Extract top-level directories
        top_level = {p.split("/")[0] for p in projects}

        if len(top_level) > 3:
            violations.append(
                ConstitutionalViolation(
                    article="VII",
                    message=f"{len(top_level)} top-level projects detected (limit: 3). "
                    f"Article VII: Keep it simple - maximum 3 projects for initial implementation.",
                    severity="error",
                    context=f"Projects: {', '.join(sorted(top_level))}",
                )
            )

        return violations

    def _check_anti_abstraction(self, content: str) -> List[ConstitutionalViolation]:
        """Article VIII: Anti-Abstraction (use frameworks directly)"""
        violations = []

        # Check for abstraction layer keywords
        abstraction_patterns = [
            r"wrapper(?:\s+class)?",
            r"adapter(?:\s+pattern)?",
            r"facade(?:\s+pattern)?",
            r"abstraction(?:\s+layer)?",
        ]

        for pattern in abstraction_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(
                    ConstitutionalViolation(
                        article="VIII",
                        message=f"Found '{pattern}' - consider using framework directly instead of creating wrappers.",
                        severity="warning",
                        context="Anti-Abstraction & Framework Trust",
                    )
                )
                break  # Only warn once

        return violations

    def _check_sdd(self, content: str) -> List[ConstitutionalViolation]:
        """Article IX: Specification-Driven Development"""
        violations = []

        # Check if spec.md and plan.md exist in same directory
        tasks_dir = Path(content).parent if isinstance(content, str) else Path.cwd()
        spec_path = tasks_dir / "spec.md"
        plan_path = tasks_dir / "plan.md"

        if not (spec_path.exists() and plan_path.exists()):
            violations.append(
                ConstitutionalViolation(
                    article="IX",
                    message="Missing spec.md or plan.md. Article IX requires: spec -> plan -> tasks -> implement.",
                    severity="warning",
                    context="Specification-Driven Development",
                )
            )

        return violations

    def _check_conventional_commits(self, content: str) -> List[ConstitutionalViolation]:
        """Article X: Conventional Commits & Semantic Versioning"""
        violations = []

        # Check if commit message format is mentioned
        has_commit_tasks = bool(re.search(r"commit|git\s+commit", content, re.IGNORECASE))
        has_conventional_format = bool(re.search(r"feat|fix|docs|style|refactor|test|chore", content, re.IGNORECASE))

        if has_commit_tasks and not has_conventional_format:
            violations.append(
                ConstitutionalViolation(
                    article="X",
                    message="Commit tasks found but no conventional commit format. "
                    "Use: feat/fix/docs/style/refactor/test/chore(scope): subject",
                    severity="warning",
                    context="Conventional Commits & Semantic Versioning",
                )
            )

        return violations

    def format_violations(self, violations: List[ConstitutionalViolation]) -> str:
        """Format violations for display

        Args:
            violations: List of violations

        Returns:
            Formatted string for console output
        """
        if not violations:
            return "All constitutional checks passed"

        output = []
        output.append(f"\n{'='*60}")
        output.append("CONSTITUTIONAL COMPLIANCE REPORT")
        output.append(f"{'='*60}\n")

        # Group by severity
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]

        if errors:
            output.append(f"ERRORS ({len(errors)}):")
            for v in errors:
                output.append(f"  Article {v.article}: {v.message}")
                if v.context:
                    output.append(f"    Context: {v.context}")
            output.append("")

        if warnings:
            output.append(f"WARNINGS ({len(warnings)}):")
            for v in warnings:
                output.append(f"  Article {v.article}: {v.message}")
                if v.context:
                    output.append(f"    Context: {v.context}")
            output.append("")

        output.append(f"{'='*60}\n")
        return "\n".join(output)


def main():
    """CLI entry point for standalone validation"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python constitutional_validator.py <tasks.md>")
        sys.exit(1)

    tasks_file = Path(sys.argv[1])

    validator = ConstitutionalValidator()
    violations = validator.validate(tasks_file)

    print(validator.format_violations(violations))

    # Exit with error code if violations found
    if any(v.severity == "error" for v in violations):
        sys.exit(1)


if __name__ == "__main__":
    main()
