#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt MCP & Skill Advisor - Context-aware tool recommendation system

Analyzes prompts to recommend optimal MCP servers and skills based on:
- Task type detection
- Performance requirements
- Context patterns
- Historical effectiveness

This extends the prompt feedback system with tool selection intelligence.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MCPRecommendation:
    """MCP server recommendation with rationale"""

    server_name: str
    confidence: float  # 0-1
    reason: str
    triggers: List[str]  # Keywords/patterns that triggered this
    alternatives: List[str] = field(default_factory=list)
    usage_example: str = ""


@dataclass
class SkillRecommendation:
    """Skill recommendation with context"""

    skill_name: str
    confidence: float
    reason: str
    command_format: str
    when_to_use: str
    performance_impact: str  # e.g., "30% faster for bulk edits"


@dataclass
class ToolSelectionAnalysis:
    """Complete tool selection analysis"""

    prompt_hash: str
    timestamp: str
    task_type: str  # coding, analysis, UI, testing, etc.

    # Recommendations
    mcp_recommendations: List[MCPRecommendation] = field(default_factory=list)
    skill_recommendations: List[SkillRecommendation] = field(default_factory=list)

    # Performance predictions
    estimated_time_savings: str = "baseline"
    parallel_opportunities: List[str] = field(default_factory=list)

    # Warnings
    inefficiencies: List[str] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)


class PromptMCPAdvisor:
    """Advises on optimal MCP server and skill usage based on prompt context"""

    # MCP Server capabilities and triggers
    MCP_SERVERS = {
        "context7": {
            "triggers": [
                "import",
                "require",
                "from",
                "library",
                "framework",
                "React",
                "Vue",
                "Angular",
                "Next.js",
                "documentation",
                "how to",
                "best practice",
                "pattern",
                "example",
            ],
            "capabilities": ["Official documentation lookup", "Framework patterns", "Version-specific guidance"],
            "performance": "Fast documentation retrieval",
            "best_for": "Library usage, framework patterns, official docs",
        },
        "sequential": {
            "triggers": [
                "debug",
                "why",
                "analyze",
                "investigate",
                "complex",
                "architecture",
                "design",
                "system",
                "root cause",
                "performance issue",
                "bottleneck",
                "--think",
            ],
            "capabilities": ["Multi-step reasoning", "Deep analysis", "Hypothesis testing"],
            "performance": "Thorough but slower (3-5s)",
            "best_for": "Complex debugging, system design, architectural analysis",
        },
        "magic": {
            "triggers": [
                "UI",
                "component",
                "button",
                "form",
                "modal",
                "responsive",
                "accessible",
                "frontend",
                "/ui",
                "/21",
                "design system",
                "user interface",
            ],
            "capabilities": ["Modern UI components", "21st.dev patterns", "Accessible designs"],
            "performance": "Fast component generation",
            "best_for": "UI components, design systems, frontend development",
        },
        "morphllm": {
            "triggers": [
                "bulk",
                "multiple files",
                "refactor",
                "rename everywhere",
                "update all",
                "pattern",
                "enforce style",
                "migrate",
            ],
            "capabilities": ["Pattern-based edits", "Bulk transformations", "Token-efficient operations"],
            "performance": "30-50% faster for multi-file edits",
            "best_for": "Bulk operations, style enforcement, migrations",
        },
        "serena": {
            "triggers": [
                "symbol",
                "rename function",
                "extract",
                "move",
                "reference",
                "dependency",
                "large codebase",
                "navigate",
                "/sc:load",
                "/sc:save",
                "session",
            ],
            "capabilities": ["Symbol operations", "Session persistence", "Semantic understanding"],
            "performance": "Excellent for large projects",
            "best_for": "Symbol ops, project memory, cross-session work",
        },
        "playwright": {
            "triggers": [
                "browser",
                "E2E",
                "test UI",
                "screenshot",
                "visual",
                "accessibility",
                "WCAG",
                "user flow",
                "form submission",
                "click",
                "navigate",
            ],
            "capabilities": ["Browser automation", "Visual testing", "Accessibility validation"],
            "performance": "Real browser testing",
            "best_for": "E2E testing, visual validation, accessibility",
        },
    }

    # Skill patterns and use cases
    SKILLS = {
        "pdf": {
            "triggers": ["PDF", "fill form", "extract table", "merge PDF"],
            "command": "skill: pdf",
            "performance": "Specialized PDF operations",
            "when": "PDF manipulation, form filling, table extraction",
        },
        "xlsx": {
            "triggers": ["Excel", "spreadsheet", "CSV", "data analysis", "formula", "pivot"],
            "command": "skill: xlsx",
            "performance": "Native Excel operations",
            "when": "Spreadsheet creation, data analysis, formulas",
        },
        "docx": {
            "triggers": ["Word", "document", "tracked changes", "comments"],
            "command": "skill: docx",
            "performance": "Professional document handling",
            "when": "Document editing, tracked changes, formatting",
        },
        "webapp-testing": {
            "triggers": ["test webapp", "debug UI", "browser logs"],
            "command": "skill: webapp-testing",
            "performance": "Integrated Playwright testing",
            "when": "Local web app testing and debugging",
        },
        "artifacts-builder": {
            "triggers": ["complex HTML", "React artifact", "shadcn", "multi-component"],
            "command": "skill: artifacts-builder",
            "performance": "Advanced component creation",
            "when": "Complex artifacts with state management",
        },
    }

    # Task type patterns
    TASK_PATTERNS = {
        "debugging": ["error", "bug", "fix", "issue", "problem", "crash", "fail"],
        "analysis": ["analyze", "review", "understand", "explain", "investigate"],
        "coding": ["implement", "create", "write", "develop", "build", "add"],
        "refactoring": ["refactor", "rename", "extract", "move", "clean", "optimize"],
        "testing": ["test", "verify", "validate", "check", "ensure", "coverage"],
        "ui_development": ["UI", "interface", "component", "frontend", "design"],
        "documentation": ["document", "explain", "describe", "guide", "tutorial"],
        "data_processing": ["data", "CSV", "Excel", "analysis", "transform", "process"],
    }

    def __init__(self, learning_dir: Optional[Path] = None):
        """Initialize advisor with optional learning directory"""
        self.learning_dir = learning_dir or Path("RUNS/mcp_advice")
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        self.usage_history = self._load_usage_history()

    def analyze(self, prompt: str) -> ToolSelectionAnalysis:
        """Analyze prompt for optimal tool selection"""
        import hashlib

        analysis = ToolSelectionAnalysis(
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:16],
            timestamp=datetime.now().isoformat(),
            task_type=self._detect_task_type(prompt),
        )

        # Analyze for MCP servers
        analysis.mcp_recommendations = self._recommend_mcp_servers(prompt)

        # Analyze for Skills
        analysis.skill_recommendations = self._recommend_skills(prompt)

        # Detect parallel opportunities
        analysis.parallel_opportunities = self._detect_parallel_opportunities(prompt)

        # Identify inefficiencies
        analysis.inefficiencies = self._detect_inefficiencies(prompt)

        # Estimate performance impact
        analysis.estimated_time_savings = self._estimate_time_savings(analysis)

        # Save for learning
        self._save_analysis(analysis)

        return analysis

    def _detect_task_type(self, prompt: str) -> str:
        """Detect primary task type from prompt"""
        prompt_lower = prompt.lower()
        task_scores = {}

        for task_type, patterns in self.TASK_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in prompt_lower)
            if score > 0:
                task_scores[task_type] = score

        if task_scores:
            return max(task_scores, key=task_scores.get)
        return "general"

    def _recommend_mcp_servers(self, prompt: str) -> List[MCPRecommendation]:
        """Recommend MCP servers based on prompt content"""
        prompt_lower = prompt.lower()
        recommendations = []

        for server_name, config in self.MCP_SERVERS.items():
            triggered_by = []
            for trigger in config["triggers"]:
                if trigger.lower() in prompt_lower:
                    triggered_by.append(trigger)

            if triggered_by:
                confidence = min(1.0, len(triggered_by) * 0.25)  # More triggers = higher confidence

                rec = MCPRecommendation(
                    server_name=server_name,
                    confidence=confidence,
                    reason=f"Detected: {', '.join(triggered_by[:3])}",
                    triggers=triggered_by,
                    usage_example=f"Enable with --{server_name}",
                )

                # Add alternatives for similar servers
                if server_name == "morphllm" and "serena" not in [r.server_name for r in recommendations]:
                    rec.alternatives = ["serena (for symbol operations)"]
                elif server_name == "serena" and "morphllm" not in [r.server_name for r in recommendations]:
                    rec.alternatives = ["morphllm (for pattern edits)"]

                recommendations.append(rec)

        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence, reverse=True)

        # Add performance notes for combinations
        if len(recommendations) > 1:
            server_names = {r.server_name for r in recommendations}
            if {"sequential", "context7"} <= server_names:
                recommendations[0].usage_example = "Combine: --sequential --context7 for deep analysis with docs"
            if {"morphllm", "serena"} <= server_names:
                recommendations[0].usage_example = "Choose one: morphllm for patterns, serena for symbols"

        return recommendations[:3]  # Top 3 recommendations

    def _recommend_skills(self, prompt: str) -> List[SkillRecommendation]:
        """Recommend skills based on prompt content"""
        prompt_lower = prompt.lower()
        recommendations = []

        for skill_name, config in self.SKILLS.items():
            triggered = any(trigger.lower() in prompt_lower for trigger in config["triggers"])

            if triggered:
                confidence = 0.8  # High confidence for skill triggers

                recommendations.append(
                    SkillRecommendation(
                        skill_name=skill_name,
                        confidence=confidence,
                        reason=f"Task requires {skill_name} capabilities",
                        command_format=config["command"],
                        when_to_use=config["when"],
                        performance_impact=config["performance"],
                    )
                )

        return recommendations

    def _detect_parallel_opportunities(self, prompt: str) -> List[str]:
        """Detect opportunities for parallel execution"""
        opportunities = []
        prompt_lower = prompt.lower()

        # Multiple file operations
        if re.search(r"\bmultiple\s+files?\b|\ball\s+files?\b|\beach\s+file\b", prompt_lower):
            opportunities.append("Parallel file processing possible")

        # Independent tasks with "and"
        if prompt_lower.count(" and ") > 2:
            opportunities.append("Multiple 'and' clauses - consider parallel execution")

        # Numbered lists
        if re.search(r"\n\s*\d+\.", prompt):
            lines = prompt.split("\n")
            numbered = [line for line in lines if re.match(r"\s*\d+\.", line)]
            if len(numbered) > 2:
                opportunities.append(f"{len(numbered)} numbered steps - check for dependencies")

        # Test execution
        if "test" in prompt_lower and ("all" in prompt_lower or "suite" in prompt_lower):
            opportunities.append("Test suite execution - use parallel test runner")

        return opportunities

    def _detect_inefficiencies(self, prompt: str) -> List[str]:
        """Detect potential inefficiencies in approach"""
        inefficiencies = []
        prompt_lower = prompt.lower()

        # Sequential file operations
        if "one by one" in prompt_lower or "each file separately" in prompt_lower:
            inefficiencies.append("Sequential processing specified - consider batch operations")

        # Not using specialized tools
        if "read all files" in prompt_lower and "grep" not in prompt_lower:
            inefficiencies.append("Manual file reading - consider using Grep tool")

        if "edit multiple" in prompt_lower and "morphllm" not in str(self._recommend_mcp_servers(prompt)):
            inefficiencies.append("Multiple edits without Morphllm - 30% slower")

        # Missing context
        if len(prompt) > 100 and not any(
            word in prompt_lower for word in ["python", "javascript", "typescript", "react", "vue"]
        ):
            inefficiencies.append("No technology stack specified - may cause suboptimal tool selection")

        # Vague analysis requests
        if "analyze" in prompt_lower and "--think" not in prompt_lower:
            inefficiencies.append("Complex analysis without --think flag")

        return inefficiencies

    def _estimate_time_savings(self, analysis: ToolSelectionAnalysis) -> str:
        """Estimate time savings from optimal tool usage"""
        savings_factors = []

        # MCP server optimizations
        mcp_names = {r.server_name for r in analysis.mcp_recommendations}

        if "morphllm" in mcp_names:
            savings_factors.append("30-50% faster bulk edits")

        if "sequential" in mcp_names:
            savings_factors.append("Better first-time accuracy")

        if "context7" in mcp_names:
            savings_factors.append("Instant documentation access")

        # Parallel execution
        if analysis.parallel_opportunities:
            savings_factors.append(f"{len(analysis.parallel_opportunities)*20}% from parallelization")

        # Skill usage
        if analysis.skill_recommendations:
            savings_factors.append("Specialized tool efficiency")

        if not savings_factors:
            return "baseline"
        elif len(savings_factors) == 1:
            return savings_factors[0]
        else:
            return f"Combined: {', '.join(savings_factors[:2])}"

    def generate_advice(self, analysis: ToolSelectionAnalysis) -> str:
        """Generate human-readable advice"""
        advice = []

        advice.append(f"## Tool Selection Advice for {analysis.task_type.replace('_', ' ').title()} Task\n")

        # MCP Server recommendations
        if analysis.mcp_recommendations:
            advice.append("### Recommended MCP Servers")
            for rec in analysis.mcp_recommendations:
                confidence_str = "HIGH" if rec.confidence > 0.7 else "MEDIUM" if rec.confidence > 0.4 else "LOW"
                advice.append(f"- **{rec.server_name}** [{confidence_str} confidence]")
                advice.append(f"  Reason: {rec.reason}")
                if rec.usage_example:
                    advice.append(f"  Usage: {rec.usage_example}")
                if rec.alternatives:
                    advice.append(f"  Alternatives: {', '.join(rec.alternatives)}")
            advice.append("")

        # Skill recommendations
        if analysis.skill_recommendations:
            advice.append("### Recommended Skills")
            for rec in analysis.skill_recommendations:
                advice.append(f"- **{rec.skill_name}**")
                advice.append(f"  Command: `{rec.command_format}`")
                advice.append(f"  Performance: {rec.performance_impact}")
            advice.append("")

        # Parallel opportunities
        if analysis.parallel_opportunities:
            advice.append("### Parallelization Opportunities")
            for opp in analysis.parallel_opportunities:
                advice.append(f"- {opp}")
            advice.append("")

        # Inefficiencies
        if analysis.inefficiencies:
            advice.append("### Potential Inefficiencies")
            for ineff in analysis.inefficiencies:
                advice.append(f"- [WARNING] {ineff}")
            advice.append("")

        # Performance estimate
        if analysis.estimated_time_savings != "baseline":
            advice.append("### Expected Performance Impact")
            advice.append(f"{analysis.estimated_time_savings}")
            advice.append("")

        # Quick command
        if analysis.mcp_recommendations:
            servers = " ".join(f"--{r.server_name}" for r in analysis.mcp_recommendations[:2])
            advice.append("### Suggested Command")
            advice.append("```")
            advice.append("# Enable recommended MCP servers:")
            advice.append(f"{servers}")
            advice.append("```")

        return "\n".join(advice)

    def _save_analysis(self, analysis: ToolSelectionAnalysis):
        """Save analysis for learning"""
        file_path = self.learning_dir / f"analysis_{analysis.prompt_hash}.json"

        data = {
            "hash": analysis.prompt_hash,
            "timestamp": analysis.timestamp,
            "task_type": analysis.task_type,
            "mcp_servers": [r.server_name for r in analysis.mcp_recommendations],
            "skills": [r.skill_name for r in analysis.skill_recommendations],
            "parallel_opportunities": len(analysis.parallel_opportunities),
            "inefficiencies": len(analysis.inefficiencies),
            "time_savings": analysis.estimated_time_savings,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_usage_history(self) -> Dict:
        """Load historical usage patterns"""
        history_file = self.learning_dir / "usage_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"patterns": {}, "effectiveness": {}}


def main():
    """Example usage"""
    advisor = PromptMCPAdvisor()

    test_prompts = [
        # Simple task
        "Fix the authentication bug in the login function",
        # Complex debugging
        "Debug why the API is slow and analyze the database queries causing bottlenecks",
        # UI development
        "Create a responsive modal component with dark mode support",
        # Bulk operations
        "Refactor all React class components to use hooks across the entire project",
        # Testing task
        "Write E2E tests for the checkout flow including form validation",
    ]

    for prompt in test_prompts:
        print("\n" + "=" * 60)
        print(f"Prompt: {prompt[:80]}...")
        print("=" * 60)

        analysis = advisor.analyze(prompt)
        advice = advisor.generate_advice(analysis)
        print(advice)


if __name__ == "__main__":
    main()
