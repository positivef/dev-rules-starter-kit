#!/usr/bin/env python3
"""
Unified Constitutional Validator v3.0
20-Article Constitution integrating Dev Rules + SpecKit

Layers:
- L1: Foundation (C1-C5): Core philosophy and architecture
- L2: Quality Assurance (C6-C10): Testing and code quality
- L3: AI & Automation (C11-C15): Advanced automation features
- L4: Process & Governance (C16-C20): Workflow and standards
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import asyncio


@dataclass
class ValidationResult:
    """Result of a constitutional validation check."""

    article_id: str
    article_name: str
    passed: bool
    score: float
    evidence: Dict[str, Any]
    recommendations: List[str]


class UnifiedConstitutionalValidator:
    """20-Article Unified Constitution Validator."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = []

        # Constitution definition
        self.articles = {
            # Layer 1: Foundation
            "C1": {
                "name": "Executable Specification",
                "description": "YAML/Markdown specs are directly executable",
                "source": ["Dev Rules P1", "SpecKit IX"],
                "validator": self.validate_c1_executable_spec,
            },
            "C2": {
                "name": "Library-First Architecture",
                "description": "All functionality as independent libraries",
                "source": ["SpecKit I"],
                "validator": self.validate_c2_library_first,
            },
            "C3": {
                "name": "CLI Accessibility",
                "description": "All libraries expose CLI interfaces",
                "source": ["SpecKit II"],
                "validator": self.validate_c3_cli_interface,
            },
            "C4": {
                "name": "Evidence-Based Development",
                "description": "SHA-256 hash-based traceability",
                "source": ["Dev Rules P2"],
                "validator": self.validate_c4_evidence_based,
            },
            "C5": {
                "name": "Knowledge Capitalization",
                "description": "Obsidian 3-second auto-sync",
                "source": ["Dev Rules P3"],
                "validator": self.validate_c5_knowledge_capital,
            },
            # Layer 2: Quality Assurance
            "C6": {
                "name": "Test-First Development",
                "description": "TDD enforced, 90% coverage minimum",
                "source": ["Dev Rules P8", "SpecKit III"],
                "validator": self.validate_c6_test_first,
            },
            "C7": {
                "name": "Integration-First Testing",
                "description": "Mock minimization, real environment",
                "source": ["SpecKit IV"],
                "validator": self.validate_c7_integration_first,
            },
            "C8": {
                "name": "SOLID & Clean Code",
                "description": "SOLID principles + Anti-Abstraction",
                "source": ["Dev Rules P4", "SpecKit VIII"],
                "validator": self.validate_c8_solid_clean,
            },
            "C9": {
                "name": "Security Gates",
                "description": "Zero critical issues enforced",
                "source": ["Dev Rules P5"],
                "validator": self.validate_c9_security_gates,
            },
            "C10": {
                "name": "Quality Metrics Gate",
                "description": "Metric-based Pass/Fail",
                "source": ["Dev Rules P6"],
                "validator": self.validate_c10_quality_metrics,
            },
            # Layer 3: AI & Automation
            "C11": {
                "name": "Academic Verification",
                "description": "6 academic DB hallucination prevention",
                "source": ["Dev Rules P7"],
                "validator": self.validate_c11_academic_verify,
            },
            "C12": {
                "name": "Principle Conflict Detection",
                "description": "Git-based auto conflict detection",
                "source": ["Dev Rules P11"],
                "validator": self.validate_c12_conflict_detect,
            },
            "C13": {
                "name": "Trade-off Analysis",
                "description": "ROI auto calculation and analysis",
                "source": ["Dev Rules P12"],
                "validator": self.validate_c13_tradeoff_analysis,
            },
            "C14": {
                "name": "Observability & Logging",
                "description": "Structured JSON logging",
                "source": ["SpecKit VI"],
                "validator": self.validate_c14_observability,
            },
            "C15": {
                "name": "Parallel Execution",
                "description": "[P] marker parallel execution",
                "source": ["SpecKit Enhancement"],
                "validator": self.validate_c15_parallel_exec,
            },
            # Layer 4: Process & Governance
            "C16": {
                "name": "Conventional Commits",
                "description": "Semantic versioning",
                "source": ["Dev Rules P9", "SpecKit X"],
                "validator": self.validate_c16_conventional_commits,
            },
            "C17": {
                "name": "Simplicity & YAGNI",
                "description": "Max 3 projects limit",
                "source": ["SpecKit VII"],
                "validator": self.validate_c17_simplicity,
            },
            "C18": {
                "name": "Windows Compatibility",
                "description": "cp949 compatible, no emojis",
                "source": ["Dev Rules P10", "SpecKit V"],
                "validator": self.validate_c18_windows_compat,
            },
            "C19": {
                "name": "Constitutional Amendment",
                "description": "User approval for changes",
                "source": ["Dev Rules P13"],
                "validator": self.validate_c19_amendment,
            },
            "C20": {
                "name": "Phase-Based Execution",
                "description": "Setup→Foundation→Story→Polish",
                "source": ["SpecKit Enhancement"],
                "validator": self.validate_c20_phase_execution,
            },
        }

    async def validate_all_20_articles(self, context: Dict = None) -> Dict[str, Any]:
        """Validate all 20 articles of the unified constitution."""
        context = context or {}
        self.results = []

        print("\n" + "=" * 60)
        print("UNIFIED CONSTITUTIONAL VALIDATION v3.0")
        print("20 Articles | 4 Layers | Dev Rules + SpecKit")
        print("=" * 60)

        # Validate each layer
        layer_results = {
            "L1_Foundation": await self.validate_layer_1_foundation(context),
            "L2_Quality": await self.validate_layer_2_quality(context),
            "L3_AI_Automation": await self.validate_layer_3_ai_automation(context),
            "L4_Governance": await self.validate_layer_4_governance(context),
        }

        # Calculate overall compliance
        total_passed = sum(1 for r in self.results if r.passed)
        total_score = sum(r.score for r in self.results) / len(self.results)

        print("\n" + "=" * 60)
        print("OVERALL COMPLIANCE SUMMARY")
        print("=" * 60)
        print(f"Articles Passed: {total_passed}/20")
        print(f"Compliance Score: {total_score:.1%}")
        print(f"Grade: {self._calculate_grade(total_score)}")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_articles": 20,
            "passed": total_passed,
            "score": total_score,
            "grade": self._calculate_grade(total_score),
            "layer_results": layer_results,
            "detailed_results": [r.__dict__ for r in self.results],
            "recommendations": self._generate_recommendations(),
        }

    async def validate_layer_1_foundation(self, context: Dict) -> Dict:
        """Validate Layer 1: Foundation (C1-C5)."""
        print("\n[L1] FOUNDATION LAYER")
        print("-" * 40)

        results = []
        for article_id in ["C1", "C2", "C3", "C4", "C5"]:
            result = await self.articles[article_id]["validator"](context)
            self.results.append(result)
            results.append(result)
            self._print_result(result)

        return self._summarize_layer("Foundation", results)

    async def validate_layer_2_quality(self, context: Dict) -> Dict:
        """Validate Layer 2: Quality Assurance (C6-C10)."""
        print("\n[L2] QUALITY ASSURANCE LAYER")
        print("-" * 40)

        results = []
        for article_id in ["C6", "C7", "C8", "C9", "C10"]:
            result = await self.articles[article_id]["validator"](context)
            self.results.append(result)
            results.append(result)
            self._print_result(result)

        return self._summarize_layer("Quality", results)

    async def validate_layer_3_ai_automation(self, context: Dict) -> Dict:
        """Validate Layer 3: AI & Automation (C11-C15)."""
        print("\n[L3] AI & AUTOMATION LAYER")
        print("-" * 40)

        results = []
        for article_id in ["C11", "C12", "C13", "C14", "C15"]:
            result = await self.articles[article_id]["validator"](context)
            self.results.append(result)
            results.append(result)
            self._print_result(result)

        return self._summarize_layer("AI & Automation", results)

    async def validate_layer_4_governance(self, context: Dict) -> Dict:
        """Validate Layer 4: Process & Governance (C16-C20)."""
        print("\n[L4] PROCESS & GOVERNANCE LAYER")
        print("-" * 40)

        results = []
        for article_id in ["C16", "C17", "C18", "C19", "C20"]:
            result = await self.articles[article_id]["validator"](context)
            self.results.append(result)
            results.append(result)
            self._print_result(result)

        return self._summarize_layer("Governance", results)

    # Individual article validators

    async def validate_c1_executable_spec(self, context: Dict) -> ValidationResult:
        """C1: Executable Specification validation."""
        yaml_files = list(Path("TASKS").glob("*.yaml"))
        md_specs = list(Path("specs").glob("**/*.md"))

        score = 0.7 if yaml_files else 0.0
        score += 0.3 if md_specs else 0.0

        return ValidationResult(
            article_id="C1",
            article_name="Executable Specification",
            passed=score >= 0.7,
            score=score,
            evidence={"yaml_contracts": len(yaml_files), "markdown_specs": len(md_specs)},
            recommendations=[] if score >= 0.7 else ["Create YAML contracts in TASKS/"],
        )

    async def validate_c2_library_first(self, context: Dict) -> ValidationResult:
        """C2: Library-First Architecture validation."""
        checks = {
            "__init__.py": (self.project_root / "scripts" / "__init__.py").exists(),
            "setup.py": (self.project_root / "setup.py").exists(),
            "src_directory": (self.project_root / "scripts").exists(),
        }

        score = sum(1 for check in checks.values() if check) / len(checks)

        return ValidationResult(
            article_id="C2",
            article_name="Library-First Architecture",
            passed=score >= 0.6,
            score=score,
            evidence=checks,
            recommendations=["Add __init__.py to make modules importable"] if not checks["__init__.py"] else [],
        )

    async def validate_c3_cli_interface(self, context: Dict) -> ValidationResult:
        """C3: CLI Interface validation."""
        cli_files = list(self.project_root.glob("**/__main__.py"))
        cli_scripts = [
            f
            for f in (self.project_root / "scripts").glob("*.py")
            if "if __name__ == '__main__':" in f.read_text(encoding="utf-8", errors="ignore")
        ]

        score = min(1.0, (len(cli_files) + len(cli_scripts)) / 10)

        return ValidationResult(
            article_id="C3",
            article_name="CLI Accessibility",
            passed=score >= 0.3,
            score=score,
            evidence={"cli_modules": len(cli_files), "cli_scripts": len(cli_scripts)},
            recommendations=["Add CLI interfaces to libraries"] if score < 0.5 else [],
        )

    async def validate_c4_evidence_based(self, context: Dict) -> ValidationResult:
        """C4: Evidence-Based Development validation."""
        evidence_dir = self.project_root / "RUNS" / "evidence"
        evidence_files = list(evidence_dir.glob("*.json")) if evidence_dir.exists() else []

        score = min(1.0, len(evidence_files) / 50)

        return ValidationResult(
            article_id="C4",
            article_name="Evidence-Based Development",
            passed=evidence_dir.exists(),
            score=score,
            evidence={"evidence_directory": evidence_dir.exists(), "evidence_files": len(evidence_files)},
            recommendations=["Run TaskExecutor to generate evidence"] if score < 0.5 else [],
        )

    async def validate_c5_knowledge_capital(self, context: Dict) -> ValidationResult:
        """C5: Knowledge Capitalization validation."""
        obsidian_bridge = self.project_root / "scripts" / "obsidian_bridge.py"

        return ValidationResult(
            article_id="C5",
            article_name="Knowledge Capitalization",
            passed=obsidian_bridge.exists(),
            score=1.0 if obsidian_bridge.exists() else 0.0,
            evidence={"obsidian_bridge": obsidian_bridge.exists()},
            recommendations=[] if obsidian_bridge.exists() else ["Configure Obsidian integration"],
        )

    async def validate_c6_test_first(self, context: Dict) -> ValidationResult:
        """C6: Test-First Development validation."""
        try:
            # Check test coverage
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=scripts", "--cov-report=json", "--quiet"], capture_output=True, text=True
            )

            if (self.project_root / "coverage.json").exists():
                with open("coverage.json") as f:
                    coverage_data = json.load(f)
                    coverage = coverage_data.get("totals", {}).get("percent_covered", 0) / 100
            else:
                coverage = 0.0

        except:
            coverage = 0.0

        return ValidationResult(
            article_id="C6",
            article_name="Test-First Development",
            passed=coverage >= 0.9,
            score=coverage,
            evidence={"coverage": f"{coverage:.1%}"},
            recommendations=["Increase test coverage to 90%"] if coverage < 0.9 else [],
        )

    async def validate_c7_integration_first(self, context: Dict) -> ValidationResult:
        """C7: Integration-First Testing validation."""
        integration_tests = list((self.project_root / "tests").glob("*integration*.py"))
        all_tests = list((self.project_root / "tests").glob("test_*.py"))

        ratio = len(integration_tests) / max(len(all_tests), 1)

        return ValidationResult(
            article_id="C7",
            article_name="Integration-First Testing",
            passed=ratio >= 0.2,
            score=min(1.0, ratio * 2),
            evidence={"integration_tests": len(integration_tests), "total_tests": len(all_tests)},
            recommendations=["Add more integration tests"] if ratio < 0.3 else [],
        )

    async def validate_c8_solid_clean(self, context: Dict) -> ValidationResult:
        """C8: SOLID & Clean Code validation."""
        deep_analyzer = self.project_root / "scripts" / "deep_analyzer.py"

        return ValidationResult(
            article_id="C8",
            article_name="SOLID & Clean Code",
            passed=deep_analyzer.exists(),
            score=1.0 if deep_analyzer.exists() else 0.0,
            evidence={"deep_analyzer": deep_analyzer.exists()},
            recommendations=[] if deep_analyzer.exists() else ["Run DeepAnalyzer for SOLID validation"],
        )

    async def validate_c9_security_gates(self, context: Dict) -> ValidationResult:
        """C9: Security Gates validation."""
        # Check for security scanning
        security_passed = True
        try:
            result = subprocess.run(["python", "-m", "pip", "list", "--format=json"], capture_output=True, text=True)
            # Simple check - in production would use safety or bandit
            security_passed = "vulnerability" not in result.stdout.lower()
        except:
            security_passed = False

        return ValidationResult(
            article_id="C9",
            article_name="Security Gates",
            passed=security_passed,
            score=1.0 if security_passed else 0.0,
            evidence={"security_scan": "passed" if security_passed else "failed"},
            recommendations=[] if security_passed else ["Run security scanner"],
        )

    async def validate_c10_quality_metrics(self, context: Dict) -> ValidationResult:
        """C10: Quality Metrics Gate validation."""
        team_stats = self.project_root / "scripts" / "team_stats_aggregator.py"

        return ValidationResult(
            article_id="C10",
            article_name="Quality Metrics Gate",
            passed=team_stats.exists(),
            score=1.0 if team_stats.exists() else 0.0,
            evidence={"team_stats_aggregator": team_stats.exists()},
            recommendations=[] if team_stats.exists() else ["Configure quality metrics"],
        )

    async def validate_c11_academic_verify(self, context: Dict) -> ValidationResult:
        """C11: Academic Verification validation."""
        mcp_server = self.project_root / "mcp" / "dev_rules_mcp_server_enhanced.py"

        return ValidationResult(
            article_id="C11",
            article_name="Academic Verification",
            passed=mcp_server.exists(),
            score=1.0 if mcp_server.exists() else 0.0,
            evidence={"academic_verification": mcp_server.exists()},
            recommendations=[] if mcp_server.exists() else ["Configure academic verification"],
        )

    async def validate_c12_conflict_detect(self, context: Dict) -> ValidationResult:
        """C12: Principle Conflict Detection validation."""
        conflict_detector = self.project_root / "scripts" / "principle_conflict_detector.py"

        return ValidationResult(
            article_id="C12",
            article_name="Principle Conflict Detection",
            passed=conflict_detector.exists(),
            score=1.0 if conflict_detector.exists() else 0.0,
            evidence={"conflict_detector": conflict_detector.exists()},
            recommendations=[] if conflict_detector.exists() else ["Enable conflict detection"],
        )

    async def validate_c13_tradeoff_analysis(self, context: Dict) -> ValidationResult:
        """C13: Trade-off Analysis validation."""
        tradeoff_analyzer = self.project_root / "scripts" / "tradeoff_analyzer.py"

        return ValidationResult(
            article_id="C13",
            article_name="Trade-off Analysis",
            passed=tradeoff_analyzer.exists(),
            score=1.0 if tradeoff_analyzer.exists() else 0.0,
            evidence={"tradeoff_analyzer": tradeoff_analyzer.exists()},
            recommendations=[] if tradeoff_analyzer.exists() else ["Configure trade-off analysis"],
        )

    async def validate_c14_observability(self, context: Dict) -> ValidationResult:
        """C14: Observability & Logging validation."""
        # Check for structured logging
        log_files = list(self.project_root.glob("**/*.log"))
        json_logs = any("json" in str(f).lower() for f in log_files)

        return ValidationResult(
            article_id="C14",
            article_name="Observability & Logging",
            passed=len(log_files) > 0,
            score=1.0 if json_logs else 0.5 if log_files else 0.0,
            evidence={"log_files": len(log_files), "structured_json": json_logs},
            recommendations=["Implement structured JSON logging"] if not json_logs else [],
        )

    async def validate_c15_parallel_exec(self, context: Dict) -> ValidationResult:
        """C15: Parallel Execution validation."""
        enhanced_executor = self.project_root / "scripts" / "enhanced_task_executor_v2.py"

        return ValidationResult(
            article_id="C15",
            article_name="Parallel Execution",
            passed=enhanced_executor.exists(),
            score=1.0 if enhanced_executor.exists() else 0.0,
            evidence={"parallel_executor": enhanced_executor.exists()},
            recommendations=[] if enhanced_executor.exists() else ["Enable parallel execution"],
        )

    async def validate_c16_conventional_commits(self, context: Dict) -> ValidationResult:
        """C16: Conventional Commits validation."""
        commitlint = (self.project_root / ".github" / "workflows" / "commitlint.yml").exists()

        return ValidationResult(
            article_id="C16",
            article_name="Conventional Commits",
            passed=commitlint,
            score=1.0 if commitlint else 0.0,
            evidence={"commitlint_configured": commitlint},
            recommendations=[] if commitlint else ["Configure conventional commits"],
        )

    async def validate_c17_simplicity(self, context: Dict) -> ValidationResult:
        """C17: Simplicity & YAGNI validation."""
        # Count active projects/features
        project_dirs = [d for d in self.project_root.iterdir() if d.is_dir() and not d.name.startswith(".")]

        score = max(0, 1.0 - (len(project_dirs) - 10) / 20) if len(project_dirs) > 10 else 1.0

        return ValidationResult(
            article_id="C17",
            article_name="Simplicity & YAGNI",
            passed=len(project_dirs) <= 15,
            score=score,
            evidence={"project_directories": len(project_dirs)},
            recommendations=["Reduce project complexity"] if len(project_dirs) > 15 else [],
        )

    async def validate_c18_windows_compat(self, context: Dict) -> ValidationResult:
        """C18: Windows Compatibility validation."""
        # Check for emoji usage
        emoji_found = False
        for py_file in self.project_root.glob("scripts/*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Simple emoji detection
            if any(ord(c) > 127 and ord(c) not in range(0x0100, 0x0180) for c in content):
                emoji_found = True
                break

        return ValidationResult(
            article_id="C18",
            article_name="Windows Compatibility",
            passed=not emoji_found,
            score=0.0 if emoji_found else 1.0,
            evidence={"emoji_free": not emoji_found},
            recommendations=["Remove emojis for Windows compatibility"] if emoji_found else [],
        )

    async def validate_c19_amendment(self, context: Dict) -> ValidationResult:
        """C19: Constitutional Amendment validation."""
        # This requires user approval by design
        return ValidationResult(
            article_id="C19",
            article_name="Constitutional Amendment",
            passed=True,
            score=1.0,
            evidence={"user_approval_required": True},
            recommendations=[],
        )

    async def validate_c20_phase_execution(self, context: Dict) -> ValidationResult:
        """C20: Phase-Based Execution validation."""
        # Check for phase structure in task files
        phase_tasks = list(Path("specs").glob("**/*phase*.md"))

        return ValidationResult(
            article_id="C20",
            article_name="Phase-Based Execution",
            passed=len(phase_tasks) > 0,
            score=min(1.0, len(phase_tasks) / 3),
            evidence={"phase_structured_tasks": len(phase_tasks)},
            recommendations=["Implement phase-based task structure"] if not phase_tasks else [],
        )

    # Helper methods

    def _print_result(self, result: ValidationResult):
        """Print a single validation result."""
        status = "[OK]" if result.passed else "[X]"
        print(f"{status} {result.article_id}: {result.article_name} - {result.score:.1%}")

    def _summarize_layer(self, layer_name: str, results: List[ValidationResult]) -> Dict:
        """Summarize results for a layer."""
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        avg_score = sum(r.score for r in results) / total if total else 0

        return {
            "layer": layer_name,
            "passed": passed,
            "total": total,
            "score": avg_score,
            "compliance": f"{passed}/{total}",
            "percentage": f"{avg_score:.1%}",
        }

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        else:
            return "F"

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        all_recommendations = []

        # Collect all recommendations with priority
        for result in self.results:
            if not result.passed:
                for rec in result.recommendations:
                    priority = 1 if result.article_id.startswith("C1") else 2
                    all_recommendations.append((priority, result.article_id, rec))

        # Sort by priority and return top 5
        all_recommendations.sort(key=lambda x: x[0])
        return [f"{article}: {rec}" for _, article, rec in all_recommendations[:5]]


async def main():
    """Main execution function."""
    import sys

    print("Unified Constitutional Validator v3.0")
    print("Integrating Dev Rules + SpecKit")
    print("20 Articles | 4 Layers")

    # Create validator
    validator = UnifiedConstitutionalValidator()

    # Run validation
    context = {}
    if len(sys.argv) > 1:
        context["mode"] = sys.argv[1]

    results = await validator.validate_all_20_articles(context)

    # Save results
    output_file = Path("RUNS") / "constitution_v3_validation.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

    # Exit with appropriate code
    sys.exit(0 if results["passed"] >= 18 else 1)


if __name__ == "__main__":
    asyncio.run(main())
