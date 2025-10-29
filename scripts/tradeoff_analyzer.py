#!/usr/bin/env python3
"""
Trade-off Analyzer (P12 Automation)

Automatically performs trade-off analysis for major decisions,
providing objective evidence-based comparisons with ROI calculations.

Constitution Article P12: 트레이드오프 분석 의무
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Evidence:
    """Evidence supporting a claim."""

    source: str  # "metrics", "git_history", "constitution", "industry_standard"
    data: Any
    confidence: float  # 0.0 to 1.0
    reference: Optional[str] = None


@dataclass
class TradeoffOption:
    """Single option in trade-off analysis."""

    name: str
    description: str
    pros: List[Tuple[str, Evidence]]  # (statement, evidence)
    cons: List[Tuple[str, Evidence]]  # (statement, evidence)
    roi_estimate: Optional[float] = None
    risk_level: str = "medium"  # low, medium, high, critical
    complexity_delta: float = 0.0  # % change in complexity
    reversibility: str = "reversible"  # reversible, costly, irreversible
    implementation_time: str = "1-3 days"


@dataclass
class InnovationSafetyCheck:
    """Innovation Safety Principles checklist (from INNOVATION_SAFETY_PRINCIPLES.md)."""

    why_needed: str
    failure_impact: str
    rollback_time: str  # "5 minutes", "1 hour", etc.
    monitoring_plan: str
    user_impact: str
    risk_score: float  # 0.0 to 1.0


@dataclass
class TradeoffAnalysis:
    """Complete trade-off analysis result."""

    decision_context: str
    options: List[TradeoffOption]
    recommendation: Optional[str] = None
    recommendation_evidence: List[Evidence] = field(default_factory=list)
    innovation_safety: Optional[InnovationSafetyCheck] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TradeoffAnalyzer:
    """Automated trade-off analyzer (P12)."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.evidence_dir = self.project_root / "RUNS" / "evidence"
        self.metrics_file = self.project_root / "RUNS" / "metrics.json"
        self.analysis_log = self.project_root / "RUNS" / "tradeoff_analysis.json"

        # Load project metrics
        self.metrics = self._load_metrics()

        # ROI calculation weights
        self.roi_weights = {
            "time_savings": 0.4,
            "quality_improvement": 0.3,
            "maintenance_reduction": 0.2,
            "risk_mitigation": 0.1,
        }

    def _load_metrics(self) -> Dict:
        """Load current project metrics."""
        metrics = {
            "avg_quality_score": 7.5,
            "test_coverage": 85.0,
            "security_issues": {"critical": 0, "major": 2, "minor": 5},
            "code_lines": 15000,
            "complexity_score": 12.5,
            "documentation_coverage": 75.0,
        }

        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    metrics.update(loaded)
            except (json.JSONDecodeError, IOError, FileNotFoundError):
                pass  # Continue if file cannot be loaded

        return metrics

    def _gather_evidence(self, claim: str, source_type: str) -> Evidence:
        """Gather evidence for a specific claim."""
        evidence = Evidence(source=source_type, data={}, confidence=0.5)

        if source_type == "metrics":
            # Use actual project metrics
            if "quality" in claim.lower():
                evidence.data = {"avg_quality": self.metrics["avg_quality_score"]}
                evidence.confidence = 0.9
            elif "coverage" in claim.lower() or "test" in claim.lower():
                evidence.data = {"test_coverage": self.metrics["test_coverage"]}
                evidence.confidence = 0.95
            elif "security" in claim.lower():
                evidence.data = self.metrics["security_issues"]
                evidence.confidence = 0.85

        elif source_type == "git_history":
            # Analyze git history for similar changes
            evidence.data = self._analyze_git_history(claim)
            evidence.confidence = 0.7 if evidence.data else 0.3

        elif source_type == "constitution":
            # Reference constitutional articles
            relevant_articles = self._find_relevant_articles(claim)
            if relevant_articles:
                evidence.data = {"articles": relevant_articles}
                evidence.confidence = 1.0
                evidence.reference = "config/constitution.yaml"

        elif source_type == "industry_standard":
            # Reference known best practices
            standards = self._get_industry_standards(claim)
            if standards:
                evidence.data = standards
                evidence.confidence = 0.8
                evidence.reference = standards.get("source", "Industry best practice")

        return evidence

    def _analyze_git_history(self, claim: str) -> Dict:
        """Analyze git history for relevant evidence."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "-20"], capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                relevant = [c for c in commits if any(keyword in c.lower() for keyword in claim.lower().split()[:3])]
                return {"related_commits": len(relevant), "total_analyzed": 20}
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            pass  # Git command failed or not in a git repository

        return {}

    def _find_relevant_articles(self, claim: str) -> List[str]:
        """Find relevant Constitution articles."""
        article_keywords = {
            "P1": ["yaml", "contract", "task"],
            "P2": ["evidence", "proof", "tracking"],
            "P3": ["knowledge", "obsidian", "documentation"],
            "P4": ["solid", "quality", "maintainability"],
            "P5": ["security", "safety", "vulnerability"],
            "P6": ["quality gate", "metrics", "threshold"],
            "P7": ["hallucination", "ai", "validation"],
            "P8": ["test", "tdd", "coverage"],
            "P9": ["commit", "version", "conventional"],
            "P10": ["encoding", "windows", "utf-8"],
            "P11": ["conflict", "principle", "contradiction"],
            "P12": ["tradeoff", "analysis", "decision"],
            "P13": ["amendment", "constitution", "change"],
        }

        claim_lower = claim.lower()
        relevant = []

        for article, keywords in article_keywords.items():
            if any(kw in claim_lower for kw in keywords):
                relevant.append(article)

        return relevant

    def _get_industry_standards(self, claim: str) -> Dict:
        """Get relevant industry standards."""
        standards_db = {
            "dashboard": {
                "best_practice": "Dashboards should be read-only views",
                "source": "Martin Fowler - Presentation Domain Separation",
            },
            "architecture": {
                "best_practice": "Layer separation with clear boundaries",
                "source": "Clean Architecture - Robert Martin",
            },
            "testing": {"best_practice": "80%+ test coverage for production code", "source": "Google Testing Blog"},
            "security": {"best_practice": "Zero critical vulnerabilities in production", "source": "OWASP Top 10"},
        }

        claim_lower = claim.lower()
        for key, standard in standards_db.items():
            if key in claim_lower:
                return standard

        return {}

    def _calculate_roi(self, option: TradeoffOption) -> float:
        """Calculate ROI for an option."""
        roi_score = 0.0

        # Time savings component
        if "automation" in option.description.lower():
            roi_score += 50 * self.roi_weights["time_savings"]
        elif "manual" in option.description.lower():
            roi_score -= 20 * self.roi_weights["time_savings"]

        # Quality improvement component
        quality_impact = 0
        for pro, _ in option.pros:
            if "quality" in pro.lower():
                quality_impact += 30
        for con, _ in option.cons:
            if "quality" in con.lower():
                quality_impact -= 15

        roi_score += quality_impact * self.roi_weights["quality_improvement"]

        # Maintenance component
        if option.complexity_delta < 0:
            roi_score += abs(option.complexity_delta) * 2 * self.roi_weights["maintenance_reduction"]
        else:
            roi_score -= option.complexity_delta * self.roi_weights["maintenance_reduction"]

        # Risk component
        risk_scores = {"low": 20, "medium": 0, "high": -20, "critical": -40}
        roi_score += risk_scores.get(option.risk_level, 0) * self.roi_weights["risk_mitigation"]

        return max(roi_score, -100.0)  # Cap at -100%

    def analyze_decision(
        self, context: str, option_a: Dict, option_b: Dict, additional_options: List[Dict] = None
    ) -> TradeoffAnalysis:
        """
        Perform complete trade-off analysis.

        Args:
            context: Decision context/question
            option_a: First option details
            option_b: Second option details
            additional_options: Any additional options to consider

        Returns:
            Complete trade-off analysis with evidence
        """
        options = []

        # Process Option A
        opt_a = self._create_option(option_a)
        opt_a.roi_estimate = self._calculate_roi(opt_a)
        options.append(opt_a)

        # Process Option B
        opt_b = self._create_option(option_b)
        opt_b.roi_estimate = self._calculate_roi(opt_b)
        options.append(opt_b)

        # Process additional options
        if additional_options:
            for opt_dict in additional_options:
                opt = self._create_option(opt_dict)
                opt.roi_estimate = self._calculate_roi(opt)
                options.append(opt)

        # Perform innovation safety check
        innovation_check = self._perform_innovation_safety_check(context, options)

        # Generate recommendation
        recommendation, rec_evidence = self._generate_recommendation(options, innovation_check)

        # Create analysis
        analysis = TradeoffAnalysis(
            decision_context=context,
            options=options,
            recommendation=recommendation,
            recommendation_evidence=rec_evidence,
            innovation_safety=innovation_check,
        )

        # Log analysis
        self._log_analysis(analysis)

        return analysis

    def _create_option(self, option_dict: Dict) -> TradeoffOption:
        """Create TradeoffOption from dictionary."""
        option = TradeoffOption(
            name=option_dict.get("name", "Option"),
            description=option_dict.get("description", ""),
            pros=[],
            cons=[],
            risk_level=option_dict.get("risk_level", "medium"),
            complexity_delta=option_dict.get("complexity_delta", 0.0),
            reversibility=option_dict.get("reversibility", "reversible"),
            implementation_time=option_dict.get("implementation_time", "1-3 days"),
        )

        # Add pros with evidence
        for pro in option_dict.get("pros", []):
            evidence = self._gather_evidence(pro, "metrics")
            option.pros.append((pro, evidence))

        # Add cons with evidence
        for con in option_dict.get("cons", []):
            evidence = self._gather_evidence(con, "metrics")
            option.cons.append((con, evidence))

        return option

    def _perform_innovation_safety_check(self, context: str, options: List[TradeoffOption]) -> InnovationSafetyCheck:
        """Perform innovation safety check per INNOVATION_SAFETY_PRINCIPLES.md."""
        # Analyze why change is needed
        why_needed = f"Address: {context}"

        # Assess failure impact
        max_risk = max(opt.risk_level for opt in options)
        risk_mapping = {"low": 0.2, "medium": 0.5, "high": 0.7, "critical": 0.9}
        risk_score = risk_mapping.get(max_risk, 0.5)

        if risk_score >= 0.7:
            failure_impact = "High - could affect system stability"
        elif risk_score >= 0.5:
            failure_impact = "Medium - limited functionality impact"
        else:
            failure_impact = "Low - minimal user impact"

        # Determine rollback capability
        reversible_count = sum(1 for opt in options if opt.reversibility == "reversible")
        if reversible_count == len(options):
            rollback_time = "5 minutes"
        elif any(opt.reversibility == "irreversible" for opt in options):
            rollback_time = "Not possible - irreversible changes"
        else:
            rollback_time = "1-2 hours"

        # Monitoring plan
        monitoring_plan = "Track metrics: quality score, error rates, performance"

        # User impact assessment
        if "ui" in context.lower() or "interface" in context.lower():
            user_impact = "Direct - visible UI changes"
        elif "backend" in context.lower() or "api" in context.lower():
            user_impact = "Indirect - API behavior changes"
        else:
            user_impact = "Minimal - internal changes only"

        return InnovationSafetyCheck(
            why_needed=why_needed,
            failure_impact=failure_impact,
            rollback_time=rollback_time,
            monitoring_plan=monitoring_plan,
            user_impact=user_impact,
            risk_score=risk_score,
        )

    def _generate_recommendation(
        self, options: List[TradeoffOption], safety_check: InnovationSafetyCheck
    ) -> Tuple[str, List[Evidence]]:
        """Generate recommendation based on analysis."""
        # Score each option
        scores = []
        for opt in options:
            score = 0

            # ROI component (40% weight)
            if opt.roi_estimate:
                score += opt.roi_estimate * 0.4

            # Evidence quality (30% weight)
            avg_confidence = sum(e.confidence for _, e in opt.pros) / len(opt.pros) if opt.pros else 0
            score += avg_confidence * 30

            # Risk component (30% weight)
            risk_penalty = {"low": 0, "medium": -10, "high": -20, "critical": -40}
            score += risk_penalty.get(opt.risk_level, -10)

            scores.append((opt, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        best_option, best_score = scores[0]

        # Generate recommendation
        if safety_check.risk_score > 0.7 and best_option.risk_level in ["high", "critical"]:
            recommendation = f"Option {best_option.name} with risk mitigation strategy"
        else:
            recommendation = f"Option {best_option.name}"

        # Gather evidence for recommendation
        rec_evidence = [
            Evidence(source="roi_calculation", data={"roi": best_option.roi_estimate, "score": best_score}, confidence=0.8),
            Evidence(
                source="risk_assessment",
                data={"risk_level": best_option.risk_level, "safety_score": 1 - safety_check.risk_score},
                confidence=0.9,
            ),
        ]

        # Add constitution evidence if available
        for _, evidence in best_option.pros:
            if evidence.source == "constitution":
                rec_evidence.append(evidence)
                break

        return recommendation, rec_evidence

    def _log_analysis(self, analysis: TradeoffAnalysis):
        """Log analysis to file."""
        # Convert to serializable format
        log_entry = {
            "timestamp": analysis.timestamp,
            "context": analysis.decision_context,
            "options": [
                {
                    "name": opt.name,
                    "description": opt.description,
                    "roi_estimate": opt.roi_estimate,
                    "risk_level": opt.risk_level,
                    "pros_count": len(opt.pros),
                    "cons_count": len(opt.cons),
                }
                for opt in analysis.options
            ],
            "recommendation": analysis.recommendation,
            "innovation_safety": {
                "risk_score": analysis.innovation_safety.risk_score,
                "rollback_time": analysis.innovation_safety.rollback_time,
            }
            if analysis.innovation_safety
            else None,
        }

        # Load existing log
        existing = []
        if self.analysis_log.exists():
            try:
                with open(self.analysis_log, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError, FileNotFoundError):
                pass  # Continue if file cannot be loaded

        # Append and save
        existing.append(log_entry)
        existing = existing[-50:]  # Keep last 50 analyses

        with open(self.analysis_log, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

    def generate_report(self, analysis: TradeoffAnalysis) -> str:
        """Generate human-readable trade-off analysis report."""
        report = []
        report.append("Trade-off Analysis Report (P12)")
        report.append("=" * 60)
        report.append(f"Context: {analysis.decision_context}")
        report.append(f"Timestamp: {analysis.timestamp}")
        report.append("")

        # Options analysis
        for i, option in enumerate(analysis.options, 1):
            report.append(f"Option {option.name}: {option.description}")
            report.append("-" * 40)

            report.append("Pros:")
            for pro, evidence in option.pros:
                conf_str = f"[{evidence.confidence:.0%} confidence]"
                report.append(f"  + {pro} {conf_str}")
                if evidence.reference:
                    report.append(f"    Source: {evidence.reference}")

            report.append("\nCons:")
            for con, evidence in option.cons:
                conf_str = f"[{evidence.confidence:.0%} confidence]"
                report.append(f"  - {con} {conf_str}")

            report.append("\nMetrics:")
            report.append(f"  ROI Estimate: {option.roi_estimate:.1f}%")
            report.append(f"  Risk Level: {option.risk_level}")
            report.append(f"  Complexity Change: {option.complexity_delta:+.1f}%")
            report.append(f"  Reversibility: {option.reversibility}")
            report.append(f"  Implementation Time: {option.implementation_time}")
            report.append("")

        # Innovation Safety Check
        if analysis.innovation_safety:
            report.append("Innovation Safety Assessment:")
            report.append("-" * 40)
            report.append(f"  Why Needed: {analysis.innovation_safety.why_needed}")
            report.append(f"  Failure Impact: {analysis.innovation_safety.failure_impact}")
            report.append(f"  Rollback Time: {analysis.innovation_safety.rollback_time}")
            report.append(f"  Monitoring: {analysis.innovation_safety.monitoring_plan}")
            report.append(f"  User Impact: {analysis.innovation_safety.user_impact}")
            report.append(f"  Risk Score: {analysis.innovation_safety.risk_score:.0%}")
            report.append("")

        # Recommendation
        report.append("RECOMMENDATION:")
        report.append("=" * 60)
        report.append(f"{analysis.recommendation}")
        report.append("")
        report.append("Evidence:")
        for evidence in analysis.recommendation_evidence:
            report.append(f"  - {evidence.source}: {evidence.data}")
            report.append(f"    Confidence: {evidence.confidence:.0%}")

        return "\n".join(report)


def main():
    """Test the trade-off analyzer."""
    analyzer = TradeoffAnalyzer()

    # Test case: Dashboard addition decision
    context = "Should we add a Streamlit dashboard to the project?"

    option_a = {
        "name": "A",
        "description": "Add Streamlit dashboard as Layer 7",
        "pros": [
            "Improved visualization of quality metrics",
            "Better monitoring of Constitution compliance",
            "User-friendly interface for non-technical users",
        ],
        "cons": [
            "Risk of focus shifting from Constitution to UI",
            "Increased complexity by 19%",
            "Additional dependencies and maintenance",
        ],
        "risk_level": "medium",
        "complexity_delta": 19.0,
        "reversibility": "reversible",
        "implementation_time": "2-3 days",
    }

    option_b = {
        "name": "B",
        "description": "Keep system CLI-only without dashboard",
        "pros": ["Maintains simplicity and Constitution focus", "No additional dependencies", "Lower maintenance burden"],
        "cons": [
            "Harder to monitor system health",
            "Less accessible for non-technical users",
            "Manual inspection of logs required",
        ],
        "risk_level": "low",
        "complexity_delta": 0.0,
        "reversibility": "reversible",
        "implementation_time": "0 days",
    }

    print("Trade-off Analyzer (P12 Automation)")
    print("=" * 60)
    print()

    # Perform analysis
    analysis = analyzer.analyze_decision(context, option_a, option_b)

    # Generate and print report
    report = analyzer.generate_report(analysis)
    print(report)


if __name__ == "__main__":
    main()
