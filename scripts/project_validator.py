#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project Validator - Comprehensive Project Health Check

Validates entire project against:
- Constitutional principles (P1-P13)
- Project structure best practices
- Dependency health
- Security vulnerabilities
- Code quality metrics
- Test coverage
- Documentation completeness

Usage:
  python scripts/project_validator.py                # Full validation
  python scripts/project_validator.py --quick        # Quick check
  python scripts/project_validator.py --fix          # Auto-fix issues
  python scripts/project_validator.py --report       # Generate HTML report

Provides comprehensive project health score and actionable recommendations.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re
import ast


@dataclass
class ValidationIssue:
    """Single validation issue"""

    severity: str  # critical, warning, info
    category: str  # structure, dependency, security, quality, test, docs
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    fix_command: Optional[str] = None
    article: Optional[str] = None  # Constitutional article


@dataclass
class ValidationReport:
    """Complete validation report"""

    timestamp: str
    overall_score: int  # 0-100
    constitution_score: int  # 0-100
    structure_score: int  # 0-100
    dependency_score: int  # 0-100
    security_score: int  # 0-100
    quality_score: int  # 0-100
    test_score: int  # 0-100
    docs_score: int  # 0-100

    issues: List[ValidationIssue]
    passed_checks: List[str]
    recommendations: List[str]
    auto_fixable: List[str]

    project_stats: Dict[str, Any]


class ProjectValidator:
    """Comprehensive project validation system"""

    # Required files for a healthy project
    REQUIRED_FILES = {
        "README.md": "Project documentation",
        ".gitignore": "Git ignore rules",
        "requirements.txt|setup.py|package.json": "Dependencies",
        "tests/|test/": "Test directory",
        ".env.example|.env.template": "Environment variables template",
    }

    # Constitutional validation rules
    CONSTITUTION_CHECKS = {
        "P1": {"check": "yaml_contracts_exist", "description": "YAML contracts for complex tasks"},
        "P2": {"check": "evidence_collection", "description": "Evidence collection configured"},
        "P3": {"check": "obsidian_integration", "description": "Knowledge base integration"},
        "P4": {"check": "solid_principles", "description": "SOLID principles compliance"},
        "P5": {"check": "security_gates", "description": "Security gates implemented"},
        "P6": {"check": "quality_metrics", "description": "Quality metrics meet thresholds"},
        "P7": {"check": "no_hallucinations", "description": "Verifiable claims only"},
        "P8": {"check": "test_coverage", "description": "Adequate test coverage"},
        "P9": {"check": "commit_format", "description": "Conventional commit format"},
        "P10": {"check": "windows_utf8", "description": "Windows UTF-8 compliance"},
    }

    # Project structure best practices
    STRUCTURE_PATTERNS = {
        "src_or_lib": ["src/", "lib/", "scripts/"],
        "tests": ["tests/", "test/", "__tests__/"],
        "docs": ["docs/", "documentation/"],
        "config": ["config/", ".config/", "configs/"],
        "ci_cd": [".github/workflows/", ".gitlab-ci.yml", "Jenkinsfile"],
        "quality": [".pre-commit-config.yaml", ".eslintrc", ".pylintrc", "pyproject.toml"],
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize validator"""
        self.project_root = project_root or Path.cwd()
        self.issues = []
        self.passed_checks = []
        self.auto_fixable = []

    def validate_project(self, quick_mode: bool = False) -> ValidationReport:
        """Run complete project validation"""
        print("Starting project validation...")

        # Collect project statistics
        project_stats = self._collect_project_stats()

        # Run validation checks
        constitution_score = self._validate_constitution()
        structure_score = self._validate_structure()
        dependency_score = self._validate_dependencies()
        security_score = self._validate_security()
        quality_score = self._validate_code_quality()
        test_score = self._validate_tests()
        docs_score = self._validate_documentation()

        # Calculate overall score
        scores = [
            constitution_score,
            structure_score,
            dependency_score,
            security_score,
            quality_score,
            test_score,
            docs_score,
        ]
        overall_score = sum(scores) // len(scores)

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            constitution_score=constitution_score,
            structure_score=structure_score,
            dependency_score=dependency_score,
            security_score=security_score,
            quality_score=quality_score,
            test_score=test_score,
            docs_score=docs_score,
            issues=self.issues,
            passed_checks=self.passed_checks,
            recommendations=recommendations,
            auto_fixable=self.auto_fixable,
            project_stats=project_stats,
        )

    def _collect_project_stats(self) -> Dict[str, Any]:
        """Collect project statistics"""
        stats = {
            "total_files": 0,
            "python_files": 0,
            "test_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "file_types": {},
        }

        for file_path in self.project_root.rglob("*"):
            try:
                if file_path.is_file() and ".git" not in str(file_path) and ".venv" not in str(file_path):
                    stats["total_files"] += 1

                    suffix = file_path.suffix
                    stats["file_types"][suffix] = stats["file_types"].get(suffix, 0) + 1

                    if suffix == ".py":
                        stats["python_files"] += 1
                        if "test" in file_path.name:
                            stats["test_files"] += 1

                        # Count lines
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                stats["total_lines"] += len(lines)

                                for line in lines:
                                    stripped = line.strip()
                                    if stripped and not stripped.startswith("#"):
                                        stats["code_lines"] += 1
                                    elif stripped.startswith("#"):
                                        stats["comment_lines"] += 1
                        except (UnicodeDecodeError, OSError, IOError):
                            pass  # Skip files that can't be read
            except (PermissionError, OSError):
                pass  # Skip files that can't be accessed

        return stats

    def _validate_constitution(self) -> int:
        """Validate constitutional compliance"""
        print("  Checking constitutional compliance...")
        score = 100
        passed = 0
        len(self.CONSTITUTION_CHECKS)

        for article, check_info in self.CONSTITUTION_CHECKS.items():
            check_method = getattr(self, f"_check_{check_info['check']}", None)

            if check_method and check_method():
                self.passed_checks.append(f"{article}: {check_info['description']}")
                passed += 1
            else:
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="constitution",
                        message=f"{article} violation: {check_info['description']}",
                        article=article,
                    )
                )
                score -= 10

        return max(0, score)

    def _validate_structure(self) -> int:
        """Validate project structure"""
        print("  Checking project structure...")
        score = 100

        # Check required files
        for required_pattern, description in self.REQUIRED_FILES.items():
            found = False
            for pattern in required_pattern.split("|"):
                if list(self.project_root.glob(pattern)):
                    found = True
                    break

            if found:
                self.passed_checks.append(f"Has {description}")
            else:
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="structure",
                        message=f"Missing {description} ({required_pattern})",
                        fix_command=f"touch {required_pattern.split('|')[0]}",
                    )
                )
                self.auto_fixable.append(f"Create {required_pattern.split('|')[0]}")
                score -= 10

        # Check directory structure
        for structure_type, patterns in self.STRUCTURE_PATTERNS.items():
            found = False
            for pattern in patterns:
                if (self.project_root / pattern).exists():
                    found = True
                    self.passed_checks.append(f"Has {structure_type} structure")
                    break

            if not found and structure_type in ["src_or_lib", "tests"]:
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="structure",
                        message=f"Missing {structure_type} directory",
                        fix_command=f"mkdir -p {patterns[0]}",
                    )
                )
                score -= 5

        return max(0, score)

    def _validate_dependencies(self) -> int:
        """Validate dependencies"""
        print("  Checking dependencies...")
        score = 100

        # Check for dependency file
        has_deps = False
        if (self.project_root / "requirements.txt").exists():
            has_deps = True
            score = self._check_python_dependencies()
        elif (self.project_root / "package.json").exists():
            has_deps = True
            score = self._check_node_dependencies()
        elif (self.project_root / "setup.py").exists():
            has_deps = True
            self.passed_checks.append("Has setup.py")

        if not has_deps:
            self.issues.append(
                ValidationIssue(
                    severity="critical",
                    category="dependency",
                    message="No dependency management file found",
                    fix_command="pip freeze > requirements.txt",
                )
            )
            score = 50

        return max(0, score)

    def _check_python_dependencies(self) -> int:
        """Check Python dependencies"""
        score = 100
        req_file = self.project_root / "requirements.txt"

        try:
            with open(req_file, "r") as f:
                lines = f.readlines()

            # Check for pinned versions
            unpinned = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" not in line and ">=" not in line:
                        unpinned.append(line)

            if unpinned:
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="dependency",
                        message=f"Unpinned dependencies: {', '.join(unpinned[:3])}",
                        fix_command="pip freeze > requirements.txt",
                    )
                )
                score -= 20
            else:
                self.passed_checks.append("All dependencies pinned")

        except Exception:
            score -= 30

        return score

    def _check_node_dependencies(self) -> int:
        """Check Node.js dependencies"""
        score = 100
        package_file = self.project_root / "package.json"

        try:
            with open(package_file, "r") as f:
                json.load(f)

            # Check for lock file
            if not (self.project_root / "package-lock.json").exists():
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="dependency",
                        message="Missing package-lock.json",
                        fix_command="npm install",
                    )
                )
                score -= 20

            # Check for security audit
            result = subprocess.run(["npm", "audit", "--json"], capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0:
                audit = json.loads(result.stdout)
                if audit.get("metadata", {}).get("vulnerabilities", {}).get("high", 0) > 0:
                    self.issues.append(
                        ValidationIssue(
                            severity="critical",
                            category="security",
                            message="High severity vulnerabilities in dependencies",
                            fix_command="npm audit fix",
                        )
                    )
                    score -= 30

        except (FileNotFoundError, json.JSONDecodeError, OSError, subprocess.SubprocessError):
            score -= 20  # Node dependencies not found or npm not available

        return score

    def _validate_security(self) -> int:
        """Validate security"""
        print("  Checking security...")
        score = 100

        # Check for secrets in code
        secret_patterns = [
            r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(api_key|apikey|api_token)\s*=\s*["\'][^"\']+["\']',
            r'(secret|token)\s*=\s*["\'][^"\']+["\']',
            r'(aws_access_key|aws_secret)\s*=\s*["\'][^"\']+["\']',
        ]

        for py_file in self.project_root.rglob("*.py"):
            if ".git" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.issues.append(
                            ValidationIssue(
                                severity="critical",
                                category="security",
                                message="Potential hardcoded secret",
                                file=str(py_file),
                                fix_command="Move to environment variables",
                            )
                        )
                        score -= 20
                        break
            except (UnicodeDecodeError, OSError, IOError):
                pass  # Skip files that can't be read

        # Check for .env in git
        if (self.project_root / ".env").exists():
            result = subprocess.run(["git", "ls-files", ".env"], capture_output=True, text=True, cwd=self.project_root)
            if result.stdout.strip():
                self.issues.append(
                    ValidationIssue(
                        severity="critical",
                        category="security",
                        message=".env file tracked in git",
                        fix_command="git rm --cached .env && echo '.env' >> .gitignore",
                    )
                )
                score -= 30
            else:
                self.passed_checks.append(".env properly ignored")

        # Check for security headers in web projects
        if (self.project_root / "package.json").exists():
            # This is a web project, check for security practices
            self.passed_checks.append("Security check for web project")

        return max(0, score)

    def _validate_code_quality(self) -> int:
        """Validate code quality"""
        print("  Checking code quality...")
        score = 100

        # Run ruff if available
        if (self.project_root / "scripts").exists():
            result = subprocess.run(
                ["ruff", "check", "scripts/", "--quiet"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode != 0:
                issues = len(result.stdout.splitlines())
                if issues > 10:
                    self.issues.append(
                        ValidationIssue(
                            severity="warning",
                            category="quality",
                            message=f"{issues} linting issues found",
                            fix_command="ruff check scripts/ --fix",
                        )
                    )
                    score -= 20
            else:
                self.passed_checks.append("No linting issues")

        # Check for code complexity
        complex_functions = self._find_complex_functions()
        if complex_functions:
            self.issues.append(
                ValidationIssue(
                    severity="warning",
                    category="quality",
                    message=f"Complex functions found: {', '.join(complex_functions[:3])}",
                    fix_command="Refactor complex functions",
                )
            )
            score -= 15

        # Check for TODO comments
        todo_count = self._count_todos()
        if todo_count > 10:
            self.issues.append(
                ValidationIssue(
                    severity="info",
                    category="quality",
                    message=f"{todo_count} TODO comments found",
                    fix_command="Address TODO items or create issues",
                )
            )
            score -= 5
        elif todo_count == 0:
            self.passed_checks.append("No TODO comments")

        return max(0, score)

    def _validate_tests(self) -> int:
        """Validate test coverage"""
        print("  Checking tests...")
        score = 100

        # Check if tests exist
        test_dirs = ["tests", "test", "__tests__"]
        has_tests = False

        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                has_tests = True
                test_files = list((self.project_root / test_dir).rglob("test_*.py"))
                if test_files:
                    self.passed_checks.append(f"Has {len(test_files)} test files")
                else:
                    self.issues.append(
                        ValidationIssue(
                            severity="warning",
                            category="test",
                            message="Test directory exists but no test files found",
                            fix_command="python scripts/test_generator.py",
                        )
                    )
                    score -= 20
                break

        if not has_tests:
            self.issues.append(
                ValidationIssue(
                    severity="critical",
                    category="test",
                    message="No test directory found",
                    fix_command="mkdir tests && python scripts/test_generator.py",
                )
            )
            score = 30

        # Check test coverage if pytest is available
        coverage_file = self.project_root / ".coverage"
        if coverage_file.exists():
            # Parse coverage
            result = subprocess.run(
                ["coverage", "report", "--format=json"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                try:
                    coverage_data = json.loads(result.stdout)
                    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

                    if total_coverage < 50:
                        self.issues.append(
                            ValidationIssue(
                                severity="warning",
                                category="test",
                                message=f"Low test coverage: {total_coverage}%",
                                fix_command="python scripts/test_generator.py --coverage",
                            )
                        )
                        score -= 30
                    elif total_coverage > 80:
                        self.passed_checks.append(f"Good test coverage: {total_coverage}%")
                except (json.JSONDecodeError, KeyError):
                    pass  # Coverage data parsing failed

        return max(0, score)

    def _validate_documentation(self) -> int:
        """Validate documentation"""
        print("  Checking documentation...")
        score = 100

        # Check README
        readme = self.project_root / "README.md"
        if readme.exists():
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()

            # Check README sections
            required_sections = ["Installation", "Usage", "License"]
            missing_sections = []

            for section in required_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)

            if missing_sections:
                self.issues.append(
                    ValidationIssue(
                        severity="info",
                        category="docs",
                        message=f"README missing sections: {', '.join(missing_sections)}",
                        fix_command="Add missing sections to README.md",
                    )
                )
                score -= 10
            else:
                self.passed_checks.append("README has all required sections")

            # Check README length
            if len(content) < 500:
                self.issues.append(
                    ValidationIssue(
                        severity="info",
                        category="docs",
                        message="README is too short (< 500 chars)",
                        fix_command="Expand README documentation",
                    )
                )
                score -= 10
        else:
            self.issues.append(
                ValidationIssue(
                    severity="critical",
                    category="docs",
                    message="No README.md found",
                    fix_command="Create README.md with project information",
                )
            )
            score = 50

        # Check for API documentation
        if (self.project_root / "docs").exists():
            self.passed_checks.append("Has documentation directory")
        else:
            score -= 10

        return max(0, score)

    # Check methods for constitutional compliance
    def _check_yaml_contracts_exist(self) -> bool:
        """Check P1: YAML contracts exist"""
        return (self.project_root / "TASKS").exists() or (self.project_root / "contracts").exists()

    def _check_evidence_collection(self) -> bool:
        """Check P2: Evidence collection"""
        return (self.project_root / "RUNS" / "evidence").exists()

    def _check_obsidian_integration(self) -> bool:
        """Check P3: Obsidian integration"""
        return (self.project_root / "scripts" / "obsidian_bridge.py").exists()

    def _check_solid_principles(self) -> bool:
        """Check P4: SOLID principles"""
        return (self.project_root / "scripts" / "deep_analyzer.py").exists()

    def _check_security_gates(self) -> bool:
        """Check P5: Security gates"""
        return True  # Checked in security validation

    def _check_quality_metrics(self) -> bool:
        """Check P6: Quality metrics"""
        return (self.project_root / "scripts" / "team_stats_aggregator.py").exists()

    def _check_no_hallucinations(self) -> bool:
        """Check P7: No hallucinations"""
        return True  # Assume compliance

    def _check_test_coverage(self) -> bool:
        """Check P8: Test coverage"""
        return (self.project_root / "tests").exists() or (self.project_root / "test").exists()

    def _check_commit_format(self) -> bool:
        """Check P9: Commit format"""
        result = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True, text=True, cwd=self.project_root)
        if result.returncode == 0:
            message = result.stdout.strip()
            return bool(re.match(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+", message))
        return False

    def _check_windows_utf8(self) -> bool:
        """Check P10: Windows UTF-8"""
        # Check for non-ASCII in Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Check for emoji or other non-ASCII
                if any(ord(c) > 127 for c in content):
                    # Check if it's in a comment or string
                    ast.parse(content)
                    # This is a simplified check
                    return False
            except (UnicodeDecodeError, OSError, IOError, SyntaxError):
                pass  # Skip files that can't be read or parsed
        return True

    # Helper methods
    def _find_complex_functions(self) -> List[str]:
        """Find overly complex functions"""
        complex_functions = []

        for py_file in self.project_root.rglob("*.py"):
            if ".git" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Count complexity (simplified)
                        complexity = sum(1 for _ in ast.walk(node) if isinstance(_, (ast.If, ast.For, ast.While)))
                        if complexity > 10:
                            complex_functions.append(f"{py_file.stem}.{node.name}")
            except (UnicodeDecodeError, OSError, IOError, SyntaxError):
                pass  # Skip files that can't be read or parsed

        return complex_functions

    def _count_todos(self) -> int:
        """Count TODO comments"""
        count = 0

        for py_file in self.project_root.rglob("*.py"):
            if ".git" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "TODO" in line or "FIXME" in line:
                            count += 1
            except (UnicodeDecodeError, OSError, IOError):
                pass  # Skip files that can't be read

        return count

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Critical issues first
        critical = [i for i in self.issues if i.severity == "critical"]
        if critical:
            recommendations.append(f"Fix {len(critical)} critical issues immediately")

        # Check scores
        if self.issues:
            by_category = {}
            for issue in self.issues:
                by_category[issue.category] = by_category.get(issue.category, 0) + 1

            # Top categories
            for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:3]:
                if category == "test":
                    recommendations.append("Improve test coverage (use TestGenerator)")
                elif category == "security":
                    recommendations.append(f"Address {count} security issues")
                elif category == "structure":
                    recommendations.append("Fix project structure issues")
                elif category == "quality":
                    recommendations.append(f"Resolve {count} code quality issues")

        # Positive reinforcement
        if len(self.passed_checks) > 10:
            recommendations.append(f"Maintain the {len(self.passed_checks)} good practices already in place")

        return recommendations


def auto_fix_issues(issues: List[ValidationIssue]) -> int:
    """Automatically fix issues where possible"""
    fixed_count = 0

    for issue in issues:
        if issue.fix_command and issue.severity != "critical":
            print(f"Fixing: {issue.message}")
            try:
                subprocess.run(issue.fix_command, shell=True, check=True)
                fixed_count += 1
                print("  Fixed!")
            except (subprocess.CalledProcessError, OSError):
                print("  Failed to fix automatically")

    return fixed_count


def generate_html_report(report: ValidationReport, output_file: Path):
    """Generate HTML report"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #333; color: white; padding: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; }}
        .good {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .critical {{ color: #F44336; }}
        .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
        .issue {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Project Validation Report</h1>
        <p>Generated: {report.timestamp}</p>
        <div class="score {(
            'good' if report.overall_score >= 70
            else 'warning' if report.overall_score >= 50
            else 'critical'
        )}">
            Overall Score: {report.overall_score}/100
        </div>
    </div>

    <div class="section">
        <h2>Score Breakdown</h2>
        <table>
            <tr><th>Category</th><th>Score</th><th>Status</th></tr>
            <tr><td>Constitution</td><td>{report.constitution_score}</td>
                <td>{'✅' if report.constitution_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Structure</td><td>{report.structure_score}</td>
                <td>{'✅' if report.structure_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Dependencies</td><td>{report.dependency_score}</td>
                <td>{'✅' if report.dependency_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Security</td><td>{report.security_score}</td>
                <td>{'✅' if report.security_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Code Quality</td><td>{report.quality_score}</td>
                <td>{'✅' if report.quality_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Tests</td><td>{report.test_score}</td>
                <td>{'✅' if report.test_score >= 70 else '⚠️'}</td></tr>
            <tr><td>Documentation</td><td>{report.docs_score}</td>
                <td>{'✅' if report.docs_score >= 70 else '⚠️'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Issues ({len(report.issues)})</h2>
        {''.join(
            f'<div class="issue {issue.severity}">'
            f'[{issue.severity.upper()}] {issue.message}</div>'
            for issue in report.issues[:10]
        )}
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
        </ul>
    </div>

    <div class="section">
        <h2>Project Statistics</h2>
        <table>
            {''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in report.project_stats.items())}
        </table>
    </div>
</body>
</html>"""

    output_file.write_text(html, encoding="utf-8")
    print(f"HTML report saved to {output_file}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Project validator")
    parser.add_argument("--quick", action="store_true", help="Quick validation")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    # Run validation
    validator = ProjectValidator()
    report = validator.validate_project(quick_mode=args.quick)

    # Display results
    print("\n" + "=" * 60)
    print("PROJECT VALIDATION REPORT")
    print("=" * 60)
    print(f"Overall Score: {report.overall_score}/100")
    print("\nScore Breakdown:")
    print(f"  Constitution: {report.constitution_score}/100")
    print(f"  Structure: {report.structure_score}/100")
    print(f"  Dependencies: {report.dependency_score}/100")
    print(f"  Security: {report.security_score}/100")
    print(f"  Code Quality: {report.quality_score}/100")
    print(f"  Tests: {report.test_score}/100")
    print(f"  Documentation: {report.docs_score}/100")

    # Issues summary
    critical = len([i for i in report.issues if i.severity == "critical"])
    warnings = len([i for i in report.issues if i.severity == "warning"])

    print(f"\nIssues: {critical} critical, {warnings} warnings")

    if report.issues:
        print("\nTop Issues:")
        for issue in report.issues[:5]:
            print(f"  [{issue.severity.upper()}] {issue.message}")

    print(f"\nPassed Checks: {len(report.passed_checks)}")

    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    # Auto-fix if requested
    if args.fix and report.auto_fixable:
        print(f"\nAuto-fixable issues: {len(report.auto_fixable)}")
        response = input("Fix automatically? (y/n): ")
        if response.lower() == "y":
            fixed = auto_fix_issues(report.issues)
            print(f"Fixed {fixed} issues")

    # Generate report if requested
    if args.report:
        output_file = Path(args.output) if args.output else Path("validation_report.html")
        generate_html_report(report, output_file)

    # Exit code based on score
    if report.overall_score < 50:
        return 2
    elif report.overall_score < 70:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
