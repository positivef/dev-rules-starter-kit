#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Engineering Coach - Integrated AI collaboration enhancement system

Combines prompt quality analysis with MCP/Skill recommendations to provide
comprehensive feedback for optimal AI interaction.

This is the main entry point that integrates:
- Prompt quality analysis (clarity, logic, context, structure)
- MCP server recommendations
- Skill selection guidance
- Performance optimization tips
- Learning tracking
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import sub-systems
sys.path.insert(0, str(Path(__file__).parent))
from prompt_feedback_analyzer import PromptFeedbackAnalyzer, PromptAnalysis
from prompt_mcp_advisor import PromptMCPAdvisor, ToolSelectionAnalysis


@dataclass
class ComprehensiveAnalysis:
    """Complete analysis combining quality and tool selection"""

    timestamp: str
    prompt: str

    # Quality metrics
    quality_analysis: PromptAnalysis
    overall_quality_score: float

    # Tool recommendations
    tool_analysis: ToolSelectionAnalysis
    tool_optimization_score: float

    # Combined insights
    effectiveness_score: float  # Combined quality + tool selection
    primary_improvements: List[str] = field(default_factory=list)
    quick_wins: List[str] = field(default_factory=list)
    learning_points: List[str] = field(default_factory=list)


class PromptEngineeringCoach:
    """Integrated prompt engineering coach system"""

    def __init__(self, learning_dir: Optional[Path] = None):
        """Initialize coach with sub-systems"""
        self.learning_dir = learning_dir or Path("RUNS/prompt_coach")
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-systems
        self.quality_analyzer = PromptFeedbackAnalyzer()
        self.mcp_advisor = PromptMCPAdvisor()

        # Load coaching history
        self.coaching_history = self._load_coaching_history()

    def analyze_prompt(self, prompt: str) -> ComprehensiveAnalysis:
        """Perform comprehensive prompt analysis"""

        # Quality analysis
        quality_analysis = self.quality_analyzer.analyze(prompt)

        # Tool selection analysis
        tool_analysis = self.mcp_advisor.analyze(prompt)

        # Calculate tool optimization score
        tool_score = self._calculate_tool_score(tool_analysis)

        # Calculate combined effectiveness
        effectiveness = quality_analysis.overall_score * 0.6 + tool_score * 0.4

        # Create comprehensive analysis
        analysis = ComprehensiveAnalysis(
            timestamp=datetime.now().isoformat(),
            prompt=prompt,
            quality_analysis=quality_analysis,
            overall_quality_score=quality_analysis.overall_score,
            tool_analysis=tool_analysis,
            tool_optimization_score=tool_score,
            effectiveness_score=effectiveness,
        )

        # Generate insights
        analysis.primary_improvements = self._identify_primary_improvements(analysis)
        analysis.quick_wins = self._identify_quick_wins(analysis)
        analysis.learning_points = self._generate_learning_points(analysis)

        # Save for tracking
        self._save_analysis(analysis)

        return analysis

    def _calculate_tool_score(self, tool_analysis: ToolSelectionAnalysis) -> float:
        """Calculate tool selection optimization score"""
        score = 100.0

        # Deduct for inefficiencies
        score -= len(tool_analysis.inefficiencies) * 10

        # Bonus for appropriate MCP selection
        if tool_analysis.mcp_recommendations:
            score = min(100, score + len(tool_analysis.mcp_recommendations) * 5)

        # Bonus for skill usage
        if tool_analysis.skill_recommendations:
            score = min(100, score + len(tool_analysis.skill_recommendations) * 5)

        # Bonus for parallel opportunities
        if tool_analysis.parallel_opportunities:
            score = min(100, score + len(tool_analysis.parallel_opportunities) * 3)

        return max(0, min(100, score))

    def _identify_primary_improvements(self, analysis: ComprehensiveAnalysis) -> List[str]:
        """Identify top 3 improvements needed"""
        improvements = []

        # Quality issues
        if analysis.quality_analysis.clarity_score < 70:
            improvements.append("Improve clarity: Replace ambiguous terms with specific descriptions")

        if analysis.quality_analysis.logic_score < 70:
            improvements.append("Enhance logic: Add connectors (first, then, because) between tasks")

        if analysis.quality_analysis.context_score < 70:
            improvements.append("Add context: Specify tech stack, constraints, and expected output")

        # Tool selection issues
        if analysis.tool_analysis.inefficiencies:
            improvements.append(f"Fix inefficiency: {analysis.tool_analysis.inefficiencies[0]}")

        if not analysis.tool_analysis.mcp_recommendations:
            improvements.append("Consider MCP servers for specialized tasks")

        return improvements[:3]

    def _identify_quick_wins(self, analysis: ComprehensiveAnalysis) -> List[str]:
        """Identify easy improvements with high impact"""
        quick_wins = []

        # Quality quick wins
        if analysis.quality_analysis.ambiguous_terms:
            quick_wins.append(f"Replace: {', '.join(analysis.quality_analysis.ambiguous_terms[:2])}")

        # Tool quick wins
        if analysis.tool_analysis.parallel_opportunities:
            quick_wins.append("Enable parallel execution for independent tasks")

        if analysis.tool_analysis.mcp_recommendations:
            top_mcp = analysis.tool_analysis.mcp_recommendations[0]
            if top_mcp.confidence > 0.7:
                quick_wins.append(f"Use --{top_mcp.server_name} for this task")

        return quick_wins[:3]

    def _generate_learning_points(self, analysis: ComprehensiveAnalysis) -> List[str]:
        """Generate educational insights"""
        learning = []

        task_type = analysis.tool_analysis.task_type

        # Task-specific learning
        if task_type == "debugging":
            learning.append("For debugging: Use --sequential for deep analysis")
        elif task_type == "refactoring":
            learning.append("For refactoring: Morphllm handles bulk edits 30-50% faster")
        elif task_type == "ui_development":
            learning.append("For UI: Magic MCP provides modern component patterns")

        # General learning
        if analysis.quality_analysis.sentence_count > 3 and analysis.quality_analysis.structure_score < 70:
            learning.append("Complex requests benefit from numbered steps or bullet points")

        return learning

    def generate_coaching_report(self, analysis: ComprehensiveAnalysis) -> str:
        """Generate comprehensive coaching report"""
        report = []

        # Header
        report.append("# Prompt Engineering Coaching Report")
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        level = self._get_proficiency_level(analysis.effectiveness_score)
        report.append(f"**Effectiveness Score**: {analysis.effectiveness_score:.0f}/100 ({level})")
        report.append(f"- Quality Score: {analysis.overall_quality_score:.0f}/100")
        report.append(f"- Tool Optimization: {analysis.tool_optimization_score:.0f}/100")
        report.append("")

        # Quality Analysis
        report.append("## Prompt Quality Analysis")
        report.append(f"- **Clarity**: {analysis.quality_analysis.clarity_score:.0f}/100")
        report.append(f"- **Logic**: {analysis.quality_analysis.logic_score:.0f}/100")
        report.append(f"- **Context**: {analysis.quality_analysis.context_score:.0f}/100")
        report.append(f"- **Structure**: {analysis.quality_analysis.structure_score:.0f}/100")

        if analysis.quality_analysis.strengths:
            report.append("\n**Strengths:**")
            for strength in analysis.quality_analysis.strengths:
                report.append(f"- {strength}")

        report.append("")

        # Tool Recommendations
        report.append("## Tool Selection Recommendations")

        if analysis.tool_analysis.mcp_recommendations:
            report.append("\n### MCP Servers")
            for mcp in analysis.tool_analysis.mcp_recommendations[:2]:
                conf = "HIGH" if mcp.confidence > 0.7 else "MEDIUM"
                report.append(f"- **{mcp.server_name}** [{conf}]: {mcp.reason}")

        if analysis.tool_analysis.skill_recommendations:
            report.append("\n### Skills")
            for skill in analysis.tool_analysis.skill_recommendations[:2]:
                report.append(f"- **{skill.skill_name}**: {skill.when_to_use}")

        if analysis.tool_analysis.parallel_opportunities:
            report.append("\n### Performance Optimizations")
            for opp in analysis.tool_analysis.parallel_opportunities:
                report.append(f"- {opp}")

        report.append("")

        # Improvement Plan
        report.append("## Improvement Plan")

        if analysis.primary_improvements:
            report.append("\n### Priority Improvements")
            for i, imp in enumerate(analysis.primary_improvements, 1):
                report.append(f"{i}. {imp}")

        if analysis.quick_wins:
            report.append("\n### Quick Wins")
            for win in analysis.quick_wins:
                report.append(f"- {win}")

        report.append("")

        # Learning Section
        if analysis.learning_points:
            report.append("## Learning Points")
            for point in analysis.learning_points:
                report.append(f"- {point}")
            report.append("")

        # Example Enhancement
        report.append("## Enhanced Prompt Example")
        report.append("```")
        report.append(self._generate_enhanced_example(analysis))
        report.append("```")

        return "\n".join(report)

    def _generate_enhanced_example(self, analysis: ComprehensiveAnalysis) -> str:
        """Generate an improved version of the prompt"""
        original = analysis.prompt
        enhanced_parts = []

        # Add structure if missing
        if analysis.quality_analysis.structure_score < 70 and len(original) > 50:
            # Convert to numbered steps
            sentences = original.split(". ")
            if len(sentences) > 1:
                for i, sent in enumerate(sentences, 1):
                    enhanced_parts.append(f"{i}. {sent.strip()}")
                enhanced = "\n".join(enhanced_parts)
            else:
                enhanced = original
        else:
            enhanced = original

        # Add context hint
        if analysis.quality_analysis.context_score < 70:
            enhanced = f"[Using Python 3.9] {enhanced}"

        # Add MCP hint
        if analysis.tool_analysis.mcp_recommendations:
            top_mcp = analysis.tool_analysis.mcp_recommendations[0]
            enhanced = f"# Suggested: --{top_mcp.server_name}\n{enhanced}"

        return enhanced

    def _get_proficiency_level(self, score: float) -> str:
        """Get proficiency level from score"""
        if score >= 90:
            return "Expert Prompt Engineer"
        elif score >= 75:
            return "Advanced"
        elif score >= 60:
            return "Intermediate"
        elif score >= 40:
            return "Developing"
        else:
            return "Beginner"

    def _save_analysis(self, analysis: ComprehensiveAnalysis):
        """Save analysis for tracking"""
        import hashlib

        prompt_hash = hashlib.sha256(analysis.prompt.encode()).hexdigest()[:16]
        file_path = self.learning_dir / f"coaching_{prompt_hash}.json"

        data = {
            "timestamp": analysis.timestamp,
            "prompt_length": len(analysis.prompt),
            "effectiveness_score": analysis.effectiveness_score,
            "quality_score": analysis.overall_quality_score,
            "tool_score": analysis.tool_optimization_score,
            "improvements_count": len(analysis.primary_improvements),
            "task_type": analysis.tool_analysis.task_type,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_coaching_history(self) -> Dict:
        """Load coaching history"""
        history_file = self.learning_dir / "coaching_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sessions": [], "improvements": {}}

    def compare_prompts(self, prompt1: str, prompt2: str) -> str:
        """Compare two prompts and show improvements"""
        analysis1 = self.analyze_prompt(prompt1)
        analysis2 = self.analyze_prompt(prompt2)

        comparison = []
        comparison.append("# Prompt Comparison Report\n")

        # Score comparison
        comparison.append("## Overall Scores")
        comparison.append(f"- Prompt 1: {analysis1.effectiveness_score:.0f}/100")
        comparison.append(f"- Prompt 2: {analysis2.effectiveness_score:.0f}/100")

        improvement = analysis2.effectiveness_score - analysis1.effectiveness_score
        if improvement > 0:
            comparison.append(f"\n[IMPROVED] +{improvement:.0f} points")
        elif improvement < 0:
            comparison.append(f"\n[DEGRADED] {improvement:.0f} points")
        else:
            comparison.append("\n[UNCHANGED] Same effectiveness")

        # Detailed improvements
        comparison.append("\n## Detailed Changes")

        # Quality improvements
        q_imp = analysis2.overall_quality_score - analysis1.overall_quality_score
        comparison.append(f"- Quality: {'+' if q_imp >= 0 else ''}{q_imp:.0f}")

        # Tool improvements
        t_imp = analysis2.tool_optimization_score - analysis1.tool_optimization_score
        comparison.append(f"- Tool Usage: {'+' if t_imp >= 0 else ''}{t_imp:.0f}")

        # Specific improvements
        comparison.append("\n## What Improved")

        # Check ambiguous terms
        amb1 = set(analysis1.quality_analysis.ambiguous_terms)
        amb2 = set(analysis2.quality_analysis.ambiguous_terms)
        if len(amb2) < len(amb1):
            comparison.append(f"- Removed ambiguous terms: {', '.join(amb1 - amb2)}")

        # Check MCP usage
        mcp1 = {r.server_name for r in analysis1.tool_analysis.mcp_recommendations}
        mcp2 = {r.server_name for r in analysis2.tool_analysis.mcp_recommendations}
        if mcp2 - mcp1:
            comparison.append(f"- Added MCP servers: {', '.join(mcp2 - mcp1)}")

        return "\n".join(comparison)


def main():
    """Example usage and demonstration"""
    coach = PromptEngineeringCoach()

    # Example prompts showing progression
    examples = [
        # Beginner level
        "fix the bug and make it work",
        # Intermediate level
        "Debug the authentication timeout issue in auth.py and add proper error handling",
        # Advanced level
        """Using React 18 and TypeScript:
        1. Analyze the current authentication flow in src/auth/
        2. Fix the session timeout bug (currently expires after 5 min)
        3. Add retry logic with exponential backoff
        4. Write unit tests with Jest covering edge cases
        5. Update the API documentation""",
    ]

    for i, prompt in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"Example {i}: {prompt[:50]}...")
        print("=" * 70)

        analysis = coach.analyze_prompt(prompt)
        report = coach.generate_coaching_report(analysis)
        print(report)

    # Compare improvement
    print("\n" + "=" * 70)
    print("COMPARISON: Beginner vs Advanced")
    print("=" * 70)
    comparison = coach.compare_prompts(examples[0], examples[2])
    print(comparison)


if __name__ == "__main__":
    main()
