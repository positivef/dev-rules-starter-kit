#!/usr/bin/env python3
"""
Auto-Improver: Constitution-Based Automatic Improvement System
===============================================================

This system analyzes code to detect Constitution violations,
automatically suggests improvements, and applies approved changes.

Core Features:
1. Constitution parsing and rule extraction
2. Code pattern analysis and violation detection
3. Automatic improvement generation
4. Risk assessment and auto/manual application

Author: VibeCoding Enhanced v1.5.1
Date: 2025-11-06
"""

import os
import sys
import yaml
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import existing analyzers if available
try:
    from scripts.deep_analyzer import DeepAnalyzer as _  # noqa: F401

    DEEP_ANALYZER_AVAILABLE = True
except ImportError:
    DEEP_ANALYZER_AVAILABLE = False
    print("[INFO] DeepAnalyzer not available, using built-in analysis")

try:
    from scripts.obsidian_bridge import ObsidianBridge

    OBSIDIAN_AVAILABLE = True
except ImportError:
    OBSIDIAN_AVAILABLE = False
    print("[INFO] ObsidianBridge not available, skipping knowledge sync")


class RiskLevel(Enum):
    """Risk level for improvements"""

    LOW = "low"  # Auto-apply allowed
    MEDIUM = "medium"  # Approval required
    HIGH = "high"  # Manual review required
    CRITICAL = "critical"  # Never auto-apply


class ImprovementCategory(Enum):
    """Improvement categories"""

    SOLID = "solid"  # P4: SOLID principles
    SECURITY = "security"  # P5: Security
    HALLUCINATION = "hallucination"  # P7: AI Hallucination
    QUALITY = "quality"  # P6: Quality
    ENCODING = "encoding"  # P10: Windows encoding
    TESTING = "testing"  # P8: Test-first
    STRUCTURE = "structure"  # Code structure
    PERFORMANCE = "performance"  # Performance


@dataclass
class ConstitutionArticle:
    """Constitution article"""

    id: str
    name: str
    category: str
    priority: str
    requirements: List[Dict[str, Any]]
    enforcement_tool: Optional[str] = None
    penalty: Optional[float] = None


@dataclass
class Violation:
    """Constitution violation"""

    article_id: str
    file_path: str
    line_number: int
    description: str
    severity: str
    code_snippet: Optional[str] = None


@dataclass
class Improvement:
    """개선 제안"""

    violation: Violation
    suggestion: str
    fix_code: Optional[str]
    category: ImprovementCategory
    risk_level: RiskLevel
    confidence: float  # 0.0 ~ 1.0
    estimated_impact: str
    auto_applicable: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "article_id": self.violation.article_id,
            "file": self.violation.file_path,
            "line": self.violation.line_number,
            "violation": self.violation.description,
            "suggestion": self.suggestion,
            "fix_code": self.fix_code,
            "category": self.category.value,
            "risk": self.risk_level.value,
            "confidence": self.confidence,
            "impact": self.estimated_impact,
            "auto_applicable": self.auto_applicable,
        }


class ConstitutionParser:
    """Constitution YAML 파서"""

    def __init__(self, constitution_path: str = None):
        self.constitution_path = constitution_path or "config/constitution.yaml"
        self.articles = []
        self.tools_mapping = {}
        self.load_constitution()

    def load_constitution(self):
        """Constitution 파일 로드 및 파싱"""
        try:
            with open(self.constitution_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Parse articles
            for article_data in data.get("articles", []):
                article = ConstitutionArticle(
                    id=article_data["id"],
                    name=article_data["name"],
                    category=article_data["category"],
                    priority=article_data["priority"],
                    requirements=article_data.get("requirements", []),
                )

                # Extract enforcement info
                enforcement = article_data.get("enforcement", {})
                article.enforcement_tool = enforcement.get("tool")

                # Extract penalty info for scoring
                if "penalty" in enforcement:
                    penalty_str = enforcement["penalty"]
                    # Extract number from strings like "-0.5점 per violation"
                    match = re.search(r"(-?\d+\.?\d*)", penalty_str)
                    if match:
                        article.penalty = float(match.group(1))

                self.articles.append(article)

            # Parse tools mapping
            self.tools_mapping = data.get("tools", {})

            print(f"[SUCCESS] Loaded {len(self.articles)} Constitution articles")

        except Exception as e:
            print(f"[ERROR] Failed to load Constitution: {e}")
            # Provide default articles if loading fails
            self._load_default_articles()

    def _load_default_articles(self):
        """기본 Constitution 조항 로드 (fallback)"""
        default_articles = [
            ConstitutionArticle(
                id="P4", name="SOLID 원칙", category="code_quality", priority="high", requirements=[], penalty=-0.5
            ),
            ConstitutionArticle(
                id="P5", name="보안 우선", category="security", priority="critical", requirements=[], penalty=-1.0
            ),
            ConstitutionArticle(
                id="P7", name="Hallucination 방지", category="ai_safety", priority="medium", requirements=[], penalty=-0.1
            ),
            ConstitutionArticle(
                id="P10", name="Windows 인코딩", category="compatibility", priority="medium", requirements=[], penalty=-0.2
            ),
        ]
        self.articles = default_articles
        print("[INFO] Using default Constitution articles")

    def get_article(self, article_id: str) -> Optional[ConstitutionArticle]:
        """특정 조항 가져오기"""
        for article in self.articles:
            if article.id == article_id:
                return article
        return None

    def get_articles_by_category(self, category: str) -> List[ConstitutionArticle]:
        """카테고리별 조항 가져오기"""
        return [a for a in self.articles if a.category == category]


class PatternDetector:
    """코드 패턴 감지 및 Constitution 위반 검사"""

    def __init__(self, constitution_parser: ConstitutionParser):
        self.constitution = constitution_parser
        self.violations = []

        # Compile regex patterns for common issues
        self.patterns = {
            "hardcoded_secrets": re.compile(r'(password|secret|key|token|api_key)\s*=\s*["\'][\w\d]+["\']', re.IGNORECASE),
            "eval_usage": re.compile(r"\beval\s*\("),
            "exec_usage": re.compile(r"\bexec\s*\("),
            "todo_fixme": re.compile(r"#\s*(TODO|FIXME|XXX|HACK)\b", re.IGNORECASE),
            "not_implemented": re.compile(r"raise\s+NotImplementedError"),
            "placeholder": re.compile(r"\b(placeholder|dummy|fake|mock|temp|temporary)\b", re.IGNORECASE),
            "emoji": re.compile(r"[\U0001F300-\U0001F9FF]"),  # Emoji range
            "long_function": re.compile(r"def\s+\w+\([^)]*\):", re.MULTILINE),
            "sql_injection": re.compile(r'(query|execute)\s*\(\s*["\'].*%[s\d].*["\'].*%', re.IGNORECASE),
        }

    def analyze_file(self, file_path: str) -> List[Violation]:
        """단일 파일 분석"""
        violations = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # Skip non-Python files for now
            if not file_path.endswith(".py"):
                return violations

            # P5: Security violations
            violations.extend(self._check_security_issues(file_path, content, lines))

            # P7: Hallucination violations
            violations.extend(self._check_hallucination_risks(file_path, content, lines))

            # P10: Encoding violations (emoji in code)
            if file_path.endswith(".py"):
                violations.extend(self._check_encoding_issues(file_path, content, lines))

            # P4: SOLID violations (using AST for Python files)
            if file_path.endswith(".py"):
                violations.extend(self._check_solid_violations(file_path, content))

        except Exception as e:
            print(f"[ERROR] Failed to analyze {file_path}: {e}")

        return violations

    def _check_security_issues(self, file_path: str, content: str, lines: List[str]) -> List[Violation]:
        """P5: 보안 이슈 검사"""
        violations = []

        # Check for hardcoded secrets
        for match in self.patterns["hardcoded_secrets"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P5",
                    file_path=file_path,
                    line_number=line_no,
                    description="Hardcoded secret detected",
                    severity="critical",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        # Check for eval() usage
        for match in self.patterns["eval_usage"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P5",
                    file_path=file_path,
                    line_number=line_no,
                    description="eval() usage detected (security risk)",
                    severity="critical",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        # Check for SQL injection risks
        for match in self.patterns["sql_injection"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P5",
                    file_path=file_path,
                    line_number=line_no,
                    description="Potential SQL injection vulnerability",
                    severity="critical",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        return violations

    def _check_hallucination_risks(self, file_path: str, content: str, lines: List[str]) -> List[Violation]:
        """P7: AI Hallucination 위험 검사"""
        violations = []

        # Check for TODO/FIXME
        for match in self.patterns["todo_fixme"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P7",
                    file_path=file_path,
                    line_number=line_no,
                    description="TODO/FIXME comment found",
                    severity="low",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        # Check for NotImplementedError
        for match in self.patterns["not_implemented"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P7",
                    file_path=file_path,
                    line_number=line_no,
                    description="NotImplementedError found",
                    severity="medium",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        # Check for placeholder values
        for match in self.patterns["placeholder"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            # Only flag if it's in a string or variable name
            if re.search(r'["\'].*' + match.group() + r'.*["\']', lines[line_no - 1]):
                violations.append(
                    Violation(
                        article_id="P7",
                        file_path=file_path,
                        line_number=line_no,
                        description=f"Placeholder value '{match.group()}' found",
                        severity="low",
                        code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                    )
                )

        return violations

    def _check_encoding_issues(self, file_path: str, content: str, lines: List[str]) -> List[Violation]:
        """P10: Windows 인코딩 이슈 검사"""
        violations = []

        # Check for emojis in Python code
        for match in self.patterns["emoji"].finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    article_id="P10",
                    file_path=file_path,
                    line_number=line_no,
                    description=f"Emoji '{match.group()}' found in code",
                    severity="medium",
                    code_snippet=lines[line_no - 1] if line_no <= len(lines) else None,
                )
            )

        return violations

    def _check_solid_violations(self, file_path: str, content: str) -> List[Violation]:
        """P4: SOLID 원칙 위반 검사"""
        violations = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check function length (>50 lines)
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        violations.append(
                            Violation(
                                article_id="P4",
                                file_path=file_path,
                                line_number=node.lineno,
                                description=f"Function '{node.name}' is too long ({func_lines} lines > 50)",
                                severity="medium",
                                code_snippet=f"def {node.name}(...): # {func_lines} lines",
                            )
                        )

                    # Check function parameters (>5 params)
                    if len(node.args.args) > 5:
                        violations.append(
                            Violation(
                                article_id="P4",
                                file_path=file_path,
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has too many parameters ({len(node.args.args)} > 5)",
                                severity="medium",
                                code_snippet=f"def {node.name}(...): # {len(node.args.args)} params",
                            )
                        )

                # Check class size (>10 methods)
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 10:
                        violations.append(
                            Violation(
                                article_id="P4",
                                file_path=file_path,
                                line_number=node.lineno,
                                description=f"Class '{node.name}' has too many methods ({len(methods)} > 10)",
                                severity="medium",
                                code_snippet=f"class {node.name}: # {len(methods)} methods",
                            )
                        )

        except SyntaxError as e:
            print(f"[WARNING] Syntax error in {file_path}: {e}")

        return violations

    def analyze_repository(self, root_path: str = ".") -> List[Violation]:
        """전체 저장소 분석"""
        all_violations = []

        # Define directories to skip
        skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}

        for root, dirs, files in os.walk(root_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                # Only analyze Python files for now
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    violations = self.analyze_file(file_path)
                    all_violations.extend(violations)

        print(f"[INFO] Found {len(all_violations)} violations across repository")
        return all_violations


class ImprovementEngine:
    """개선안 생성 엔진"""

    def __init__(self, constitution_parser: ConstitutionParser):
        self.constitution = constitution_parser

    def generate_improvement(self, violation: Violation) -> Improvement:
        """위반사항에 대한 개선안 생성"""

        # Route to specific improvement generator based on article
        generators = {
            "P4": self._generate_solid_improvement,
            "P5": self._generate_security_improvement,
            "P7": self._generate_hallucination_improvement,
            "P10": self._generate_encoding_improvement,
        }

        generator = generators.get(violation.article_id, self._generate_generic_improvement)
        return generator(violation)

    def _generate_security_improvement(self, violation: Violation) -> Improvement:
        """P5: 보안 개선안 생성"""

        if "hardcoded secret" in violation.description.lower():
            suggestion = "Move secret to environment variable"
            fix_code = """import os
# Replace hardcoded value with:
value = os.getenv('SECRET_KEY', 'default_value')"""
            risk = RiskLevel.LOW
            confidence = 0.95
            auto_applicable = True

        elif "eval()" in violation.description.lower():
            suggestion = "Replace eval() with ast.literal_eval() or safer alternative"
            fix_code = """import ast
# Replace eval(expr) with:
result = ast.literal_eval(expr)  # For literals only
# OR use json.loads() for JSON data"""
            risk = RiskLevel.MEDIUM
            confidence = 0.85
            auto_applicable = False

        elif "sql injection" in violation.description.lower():
            suggestion = "Use parameterized queries to prevent SQL injection"
            fix_code = """# Use parameterized query:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
# Instead of string formatting"""
            risk = RiskLevel.HIGH
            confidence = 0.90
            auto_applicable = False

        else:
            suggestion = "Review security issue and apply appropriate fix"
            fix_code = None
            risk = RiskLevel.HIGH
            confidence = 0.5
            auto_applicable = False

        return Improvement(
            violation=violation,
            suggestion=suggestion,
            fix_code=fix_code,
            category=ImprovementCategory.SECURITY,
            risk_level=risk,
            confidence=confidence,
            estimated_impact="High - Security vulnerability fixed",
            auto_applicable=auto_applicable,
        )

    def _generate_solid_improvement(self, violation: Violation) -> Improvement:
        """P4: SOLID 원칙 개선안 생성"""

        if "too long" in violation.description.lower():
            suggestion = "Split function into smaller, focused functions"
            fix_code = """# Split into smaller functions:
def validate_input(data):
    # Validation logic
    pass

def process_data(data):
    # Processing logic
    pass

def save_results(results):
    # Save logic
    pass"""
            risk = RiskLevel.MEDIUM
            confidence = 0.75

        elif "too many parameters" in violation.description.lower():
            suggestion = "Use configuration object or builder pattern"
            fix_code = """# Use dataclass for parameters:
from dataclasses import dataclass

@dataclass
class Config:
    param1: str
    param2: int
    param3: bool = False

def function(config: Config):
    # Use config.param1, etc."""
            risk = RiskLevel.MEDIUM
            confidence = 0.80

        elif "too many methods" in violation.description.lower():
            suggestion = "Split class into smaller, focused classes (SRP)"
            fix_code = """# Apply Single Responsibility Principle:
# Split into multiple classes, each with one responsibility"""
            risk = RiskLevel.HIGH
            confidence = 0.70

        else:
            suggestion = "Refactor to follow SOLID principles"
            fix_code = None
            risk = RiskLevel.MEDIUM
            confidence = 0.6

        return Improvement(
            violation=violation,
            suggestion=suggestion,
            fix_code=fix_code,
            category=ImprovementCategory.SOLID,
            risk_level=risk,
            confidence=confidence,
            estimated_impact="Medium - Code quality improved",
            auto_applicable=False,
        )

    def _generate_hallucination_improvement(self, violation: Violation) -> Improvement:
        """P7: Hallucination 방지 개선안 생성"""

        if "todo" in violation.description.lower() or "fixme" in violation.description.lower():
            suggestion = "Implement the TODO/FIXME or remove if obsolete"
            fix_code = "# Implement the actual functionality"
            risk = RiskLevel.LOW
            confidence = 0.85
            auto_applicable = False

        elif "notimplementederror" in violation.description.lower():
            suggestion = "Implement the method or make it abstract"
            fix_code = """# Either implement:
def method(self):
    # Actual implementation
    return result

# Or make abstract:
from abc import ABC, abstractmethod

class MyClass(ABC):
    @abstractmethod
    def method(self):
        pass"""
            risk = RiskLevel.MEDIUM
            confidence = 0.80
            auto_applicable = False

        elif "placeholder" in violation.description.lower():
            suggestion = "Replace placeholder with actual value"
            fix_code = "# Replace with actual implementation or configuration"
            risk = RiskLevel.LOW
            confidence = 0.90
            auto_applicable = False

        else:
            suggestion = "Remove or implement incomplete code"
            fix_code = None
            risk = RiskLevel.LOW
            confidence = 0.7
            auto_applicable = False

        return Improvement(
            violation=violation,
            suggestion=suggestion,
            fix_code=fix_code,
            category=ImprovementCategory.HALLUCINATION,
            risk_level=risk,
            confidence=confidence,
            estimated_impact="Low - Code completeness improved",
            auto_applicable=auto_applicable,
        )

    def _generate_encoding_improvement(self, violation: Violation) -> Improvement:
        """P10: 인코딩 개선안 생성"""

        emoji_map = {
            # Common emojis mapped to ASCII
            "emoji_check": "[SUCCESS]",
            "emoji_cross": "[FAIL]",
            "emoji_warn": "[WARN]",
            "emoji_rocket": "[DEPLOY]",
            "emoji_log": "[LOG]",
            "emoji_wrench": "[CONFIG]",
        }

        suggestion = "Replace emoji with ASCII alternative for Windows compatibility"
        fix_code = "# Replace emoji with ASCII:\n"

        for emoji, ascii_alt in emoji_map.items():
            fix_code += f"# {emoji} -> {ascii_alt}\n"

        return Improvement(
            violation=violation,
            suggestion=suggestion,
            fix_code=fix_code,
            category=ImprovementCategory.ENCODING,
            risk_level=RiskLevel.LOW,
            confidence=0.95,
            estimated_impact="Low - Windows compatibility improved",
            auto_applicable=True,
        )

    def _generate_generic_improvement(self, violation: Violation) -> Improvement:
        """일반적인 개선안 생성"""
        return Improvement(
            violation=violation,
            suggestion="Review and fix the violation",
            fix_code=None,
            category=ImprovementCategory.QUALITY,
            risk_level=RiskLevel.MEDIUM,
            confidence=0.5,
            estimated_impact="Unknown",
            auto_applicable=False,
        )


class AutoImprover:
    """메인 자동 개선 시스템"""

    def __init__(self, constitution_path: str = None):
        self.constitution_parser = ConstitutionParser(constitution_path)
        self.pattern_detector = PatternDetector(self.constitution_parser)
        self.improvement_engine = ImprovementEngine(self.constitution_parser)
        self.improvements = []
        self.stats = defaultdict(int)

    def analyze_repository(self, root_path: str = ".") -> List[Improvement]:
        """저장소 분석 및 개선안 생성"""
        print("\n" + "=" * 60)
        print("[ANALYSIS] Starting Repository Analysis...")
        print("=" * 60)

        # Step 1: Detect violations
        violations = self.pattern_detector.analyze_repository(root_path)

        # Step 2: Generate improvements
        improvements = []
        for violation in violations:
            improvement = self.improvement_engine.generate_improvement(violation)
            improvements.append(improvement)
            self.stats[improvement.category.value] += 1
            self.stats[improvement.risk_level.value] += 1

        self.improvements = improvements

        # Step 3: Sort by risk and confidence
        improvements.sort(
            key=lambda x: (
                x.risk_level.value == "low",  # LOW risk first
                -x.confidence,  # High confidence first
            )
        )

        return improvements

    def categorize_by_risk(self) -> Dict[str, List[Improvement]]:
        """위험도별로 개선사항 분류"""
        categorized = defaultdict(list)
        for improvement in self.improvements:
            categorized[improvement.risk_level.value].append(improvement)
        return dict(categorized)

    def generate_report(self, output_file: str = None) -> str:
        """분석 리포트 생성"""
        report = []
        report.append("\n" + "=" * 60)
        report.append("[REPORT] Auto-Improvement Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total violations found: {len(self.improvements)}")
        report.append("")

        # Statistics by category
        report.append("[STATS] Violations by Category:")
        for category in ImprovementCategory:
            count = self.stats.get(category.value, 0)
            if count > 0:
                report.append(f"  - {category.value.capitalize()}: {count}")
        report.append("")

        # Statistics by risk level
        report.append("[RISK] Violations by Risk Level:")
        for risk in RiskLevel:
            count = self.stats.get(risk.value, 0)
            if count > 0:
                report.append(f"  - {risk.value.upper()}: {count}")
        report.append("")

        # Detailed improvements
        categorized = self.categorize_by_risk()

        for risk_level in ["low", "medium", "high", "critical"]:
            improvements = categorized.get(risk_level, [])
            if improvements:
                report.append(f"\n{'='*40}")
                report.append(f"Risk Level: {risk_level.upper()} ({len(improvements)} items)")
                report.append("=" * 40)

                for i, imp in enumerate(improvements[:10], 1):  # Show top 10 per category
                    report.append(f"\n{i}. {imp.violation.file_path}:{imp.violation.line_number}")
                    report.append(f"   Article: {imp.violation.article_id}")
                    report.append(f"   Violation: {imp.violation.description}")
                    report.append(f"   Suggestion: {imp.suggestion}")
                    report.append(f"   Confidence: {imp.confidence:.1%}")
                    report.append(f"   Auto-applicable: {'Yes' if imp.auto_applicable else 'No'}")

                    if imp.fix_code and len(imp.fix_code) < 200:
                        report.append("   Fix:")
                        for line in imp.fix_code.split("\n"):
                            report.append(f"      {line}")

        # Auto-applicable improvements
        auto_applicable = [imp for imp in self.improvements if imp.auto_applicable]
        if auto_applicable:
            report.append(f"\n{'='*40}")
            report.append(f"[AUTO] Auto-Applicable Improvements: {len(auto_applicable)}")
            report.append("=" * 40)
            for imp in auto_applicable[:5]:
                report.append(f"  - {imp.violation.file_path}:{imp.violation.line_number}")
                report.append(f"    {imp.suggestion}")

        # Summary
        report.append(f"\n{'='*60}")
        report.append("[SUMMARY] Summary")
        report.append("=" * 60)
        report.append(f"Total improvements: {len(self.improvements)}")
        report.append(f"Auto-applicable: {len(auto_applicable)}")
        report.append(f"Manual review required: {len(self.improvements) - len(auto_applicable)}")

        # Constitution compliance estimate
        if self.improvements:
            avg_confidence = sum(imp.confidence for imp in self.improvements) / len(self.improvements)
            report.append(f"Average confidence: {avg_confidence:.1%}")

        report_text = "\n".join(report)

        # Save to file if specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"\n[SUCCESS] Report saved to {output_file}")

        return report_text

    def apply_improvements(self, auto_only: bool = True, dry_run: bool = True) -> Dict[str, Any]:
        """개선사항 적용"""
        results = {"applied": [], "skipped": [], "failed": []}

        for improvement in self.improvements:
            if auto_only and not improvement.auto_applicable:
                results["skipped"].append(improvement)
                continue

            if improvement.risk_level == RiskLevel.CRITICAL:
                results["skipped"].append(improvement)
                continue

            if dry_run:
                print(f"[DRY-RUN] Would apply: {improvement.suggestion}")
                results["applied"].append(improvement)
            else:
                # TODO: Implement actual file modification
                # This would require careful implementation to safely modify files
                pass

        return results

    def save_to_obsidian(self):
        """개선 내용을 Obsidian에 저장"""
        if not OBSIDIAN_AVAILABLE:
            print("[INFO] Obsidian integration not available")
            return

        try:
            bridge = ObsidianBridge()

            # Create improvement report for Obsidian
            content = f"""# Auto-Improvement Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Statistics
- Total violations: {len(self.improvements)}
- Auto-applicable: {len([i for i in self.improvements if i.auto_applicable])}

## Top Improvements
"""

            for imp in self.improvements[:10]:
                content += f"""
### {imp.violation.file_path}
- Line: {imp.violation.line_number}
- Article: {imp.violation.article_id}
- Suggestion: {imp.suggestion}
- Risk: {imp.risk_level.value}
- Confidence: {imp.confidence:.1%}
"""

            # Save to Obsidian
            bridge.sync_to_obsidian(content, "auto-improvement-report")
            print("[SUCCESS] Saved to Obsidian")

        except Exception as e:
            print(f"[WARNING] Failed to save to Obsidian: {e}")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Improver: Constitution-based code improvement system")
    parser.add_argument("--path", "-p", default=".", help="Repository path to analyze (default: current directory)")
    parser.add_argument("--report", "-r", help="Output report file path")
    parser.add_argument("--apply", "-a", action="store_true", help="Apply auto-applicable improvements")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode (default: True)")
    parser.add_argument("--obsidian", "-o", action="store_true", help="Save results to Obsidian")

    args = parser.parse_args()

    # Create Auto-Improver instance
    improver = AutoImprover()

    # Analyze repository
    _ = improver.analyze_repository(args.path)

    # Generate report
    report = improver.generate_report(args.report)
    print(report)

    # Apply improvements if requested
    if args.apply:
        print("\n" + "=" * 60)
        print("[APPLY] Applying Improvements...")
        print("=" * 60)

        results = improver.apply_improvements(auto_only=True, dry_run=args.dry_run)

        print(f"Applied: {len(results['applied'])}")
        print(f"Skipped: {len(results['skipped'])}")
        print(f"Failed: {len(results['failed'])}")

    # Save to Obsidian if requested
    if args.obsidian:
        improver.save_to_obsidian()

    print("\n[SUCCESS] Auto-Improvement analysis complete!")


if __name__ == "__main__":
    main()
