#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Feedback Analyzer - AI Communication Quality Analysis Engine

Analyzes user prompts for logical structure, clarity, and effectiveness,
providing actionable feedback for improvement.

Features:
- Logical flow analysis
- Clarity scoring
- Context completeness check
- Improvement suggestions
- Learning pattern tracking
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


@dataclass
class PromptAnalysis:
    """Analysis results for a single prompt"""

    prompt_hash: str
    timestamp: str
    original_prompt: str

    # Scores (0-100)
    clarity_score: float = 0.0
    logic_score: float = 0.0
    context_score: float = 0.0
    structure_score: float = 0.0
    overall_score: float = 0.0

    # Detailed findings
    issues: List[Dict] = field(default_factory=list)
    improvements: List[Dict] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    # Metrics
    word_count: int = 0
    sentence_count: int = 0
    ambiguous_terms: List[str] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)


@dataclass
class FeedbackSuggestion:
    """Improvement suggestion with examples"""

    category: str  # clarity, logic, context, structure
    severity: str  # critical, major, minor
    issue: str
    suggestion: str
    example_before: str
    example_after: str
    learning_point: str


class PromptFeedbackAnalyzer:
    """Analyzes prompts and generates improvement feedback"""

    # Common ambiguous terms that reduce clarity
    AMBIGUOUS_TERMS = {
        "something",
        "stuff",
        "things",
        "various",
        "etc",
        "somehow",
        "maybe",
        "probably",
        "kind of",
        "sort of",
        "a bit",
        "a few",
        "some",
        "many",
        "several",
        "fix",
        "update",
        "change",
        "modify",  # Without specifics
        "improve",
        "optimize",
        "enhance",
        "better",  # Without metrics
    }

    # Logical connectors that should be present
    LOGICAL_CONNECTORS = {
        "sequential": ["then", "next", "after", "before", "first", "finally"],
        "conditional": ["if", "when", "unless", "otherwise", "else"],
        "causal": ["because", "since", "therefore", "so", "thus"],
        "purpose": ["to", "for", "in order to", "so that"],
    }

    # Context elements that should be specified
    CONTEXT_ELEMENTS = {
        "technical": ["language", "framework", "version", "environment"],
        "scope": ["files", "folders", "modules", "components"],
        "constraints": ["performance", "security", "compatibility", "deadline"],
        "output": ["format", "structure", "location", "naming"],
    }

    def __init__(self, learning_dir: Optional[Path] = None):
        """Initialize analyzer with optional learning directory"""
        self.learning_dir = learning_dir or Path("RUNS/prompt_feedback")
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        self.learning_history = self._load_learning_history()

    def analyze(self, prompt: str) -> PromptAnalysis:
        """Perform comprehensive prompt analysis"""
        analysis = PromptAnalysis(
            prompt_hash=self._hash_prompt(prompt), timestamp=datetime.now().isoformat(), original_prompt=prompt
        )

        # Basic metrics
        analysis.word_count = len(prompt.split())
        analysis.sentence_count = len(re.split(r"[.!?]+", prompt))

        # Individual dimension analysis
        analysis.clarity_score = self._analyze_clarity(prompt, analysis)
        analysis.logic_score = self._analyze_logic(prompt, analysis)
        analysis.context_score = self._analyze_context(prompt, analysis)
        analysis.structure_score = self._analyze_structure(prompt, analysis)

        # Overall score (weighted average)
        analysis.overall_score = (
            analysis.clarity_score * 0.3
            + analysis.logic_score * 0.3
            + analysis.context_score * 0.2
            + analysis.structure_score * 0.2
        )

        # Generate improvements based on issues
        analysis.improvements = self._generate_improvements(analysis)

        # Identify strengths
        analysis.strengths = self._identify_strengths(analysis)

        # Save for learning
        self._save_analysis(analysis)

        return analysis

    def _analyze_clarity(self, prompt: str, analysis: PromptAnalysis) -> float:
        """Analyze prompt clarity"""
        score = 100.0
        prompt_lower = prompt.lower()

        # Check for ambiguous terms
        for term in self.AMBIGUOUS_TERMS:
            if term in prompt_lower.split():
                analysis.ambiguous_terms.append(term)
                score -= 5
                analysis.issues.append(
                    {
                        "type": "clarity",
                        "severity": "minor",
                        "description": f"Ambiguous term '{term}' reduces clarity",
                        "location": prompt_lower.find(term),
                    }
                )

        # Check for specific vs vague instructions
        vague_patterns = [
            (r"\b(fix|improve|update)\s+\w+\b", "Vague action without specifics"),
            (r"\bmake\s+it\s+better\b", "Subjective improvement request"),
            (r"\bdo\s+something\b", "Unspecific action request"),
        ]

        for pattern, description in vague_patterns:
            if re.search(pattern, prompt_lower):
                score -= 10
                analysis.issues.append({"type": "clarity", "severity": "major", "description": description})

        # Bonus for specific quantifiers
        if re.search(r"\b\d+\b", prompt):  # Contains numbers
            score = min(100, score + 5)

        # Bonus for explicit file/function names
        if re.search(r'[`"\'][\w/.]+[`"\']', prompt):  # Quoted identifiers
            score = min(100, score + 5)

        return max(0, score)

    def _analyze_logic(self, prompt: str, analysis: PromptAnalysis) -> float:
        """Analyze logical flow and structure"""
        score = 100.0
        prompt_lower = prompt.lower()

        # Check for logical connectors
        connector_count = 0
        for category, connectors in self.LOGICAL_CONNECTORS.items():
            for connector in connectors:
                if f" {connector} " in f" {prompt_lower} ":
                    connector_count += 1

        # Penalize lack of logical flow
        if analysis.sentence_count > 2 and connector_count == 0:
            score -= 20
            analysis.issues.append(
                {"type": "logic", "severity": "major", "description": "Multiple instructions without logical connectors"}
            )

        # Check for contradictions
        contradiction_patterns = [
            (r"\bbut\s+also\b", "Potential contradiction"),
            (r"\bdon\'t\b.*\bbut\b.*\bdo\b", "Contradictory instructions"),
        ]

        for pattern, description in contradiction_patterns:
            if re.search(pattern, prompt_lower):
                score -= 15
                analysis.issues.append({"type": "logic", "severity": "critical", "description": description})

        # Check for clear sequence
        if "and then" in prompt_lower or re.search(r"\b(first|then|finally)\b", prompt_lower):
            score = min(100, score + 10)

        return max(0, score)

    def _analyze_context(self, prompt: str, analysis: PromptAnalysis) -> float:
        """Analyze context completeness"""
        score = 100.0
        prompt_lower = prompt.lower()

        # Check for missing context elements
        context_hints = {
            "file_context": [".py", ".js", ".ts", "file", "script"],
            "tech_context": ["python", "javascript", "react", "django"],
            "scope_context": ["function", "class", "module", "component"],
        }

        context_found = 0
        for category, hints in context_hints.items():
            if any(hint in prompt_lower for hint in hints):
                context_found += 1

        if context_found == 0:
            score -= 30
            analysis.missing_context.append("technical_context")
            analysis.issues.append({"type": "context", "severity": "major", "description": "No technical context provided"})

        # Check for constraints
        if not any(word in prompt_lower for word in ["must", "should", "need", "require"]):
            score -= 10
            analysis.issues.append(
                {"type": "context", "severity": "minor", "description": "No explicit requirements or constraints"}
            )

        # Bonus for environment/version info
        if re.search(r"v?\d+\.\d+", prompt):  # Version numbers
            score = min(100, score + 5)

        return max(0, score)

    def _analyze_structure(self, prompt: str, analysis: PromptAnalysis) -> float:
        """Analyze prompt structure and organization"""
        score = 100.0

        # Check for structure indicators
        has_numbered_list = bool(re.search(r"\n\s*\d+\.", prompt))
        has_bullet_points = bool(re.search(r"\n\s*[-*]", prompt))
        has_clear_sections = bool(re.search(r"\n\n", prompt))

        # Reward structured format
        if has_numbered_list:
            score = min(100, score + 15)
        elif has_bullet_points:
            score = min(100, score + 10)
        elif has_clear_sections:
            score = min(100, score + 5)
        elif analysis.sentence_count > 3:
            # Penalize long unstructured text
            score -= 15
            analysis.issues.append(
                {"type": "structure", "severity": "minor", "description": "Long prompt without clear structure"}
            )

        # Check for clear task separation
        if analysis.word_count > 50 and not (has_numbered_list or has_bullet_points):
            score -= 10
            analysis.issues.append(
                {"type": "structure", "severity": "minor", "description": "Complex request without task breakdown"}
            )

        return max(0, score)

    def _generate_improvements(self, analysis: PromptAnalysis) -> List[Dict]:
        """Generate specific improvement suggestions"""
        improvements = []

        # Address clarity issues
        if analysis.ambiguous_terms:
            improvements.append(
                {
                    "category": "clarity",
                    "priority": "high",
                    "suggestion": f"Replace ambiguous terms: {', '.join(analysis.ambiguous_terms[:3])}",
                    "example": "Instead of 'fix stuff', say 'fix the authentication bug in login.py'",
                }
            )

        # Address logic issues
        logic_issues = [i for i in analysis.issues if i["type"] == "logic"]
        if logic_issues:
            improvements.append(
                {
                    "category": "logic",
                    "priority": "high",
                    "suggestion": "Add logical connectors to show relationship between tasks",
                    "example": "First analyze the data, then generate the report, finally send the email",
                }
            )

        # Address context issues
        if analysis.missing_context:
            improvements.append(
                {
                    "category": "context",
                    "priority": "medium",
                    "suggestion": "Specify technical context and constraints",
                    "example": "Using Python 3.9 with pandas, process the CSV file (max 100MB)",
                }
            )

        # Address structure issues
        if analysis.word_count > 50 and analysis.structure_score < 70:
            improvements.append(
                {
                    "category": "structure",
                    "priority": "medium",
                    "suggestion": "Break down into numbered steps or bullet points",
                    "example": "1. Load data\n2. Clean nulls\n3. Generate plot\n4. Save as PNG",
                }
            )

        return improvements

    def _identify_strengths(self, analysis: PromptAnalysis) -> List[str]:
        """Identify what the prompt does well"""
        strengths = []

        if analysis.clarity_score >= 80:
            strengths.append("Clear and specific language")
        if analysis.logic_score >= 80:
            strengths.append("Logical flow between tasks")
        if analysis.context_score >= 80:
            strengths.append("Good context provided")
        if analysis.structure_score >= 80:
            strengths.append("Well-structured request")

        # Specific strengths
        if not analysis.ambiguous_terms:
            strengths.append("No ambiguous terminology")
        if analysis.word_count < 30 and analysis.clarity_score >= 70:
            strengths.append("Concise and to the point")

        return strengths

    def _format_issues(self, issues: List[Dict]) -> List[str]:
        """Format issues section"""
        result = ["### [IMPROVEMENTS NEEDED]"]
        critical = [i for i in issues if i.get("severity") == "critical"]
        major = [i for i in issues if i.get("severity") == "major"]

        if critical:
            result.append("**Critical Issues:**")
            result.extend(f"- {issue['description']}" for issue in critical[:3])

        if major:
            result.append("**Major Issues:**")
            result.extend(f"- {issue['description']}" for issue in major[:3])

        result.append("")
        return result

    def _format_suggestions(self, improvements: List[Dict]) -> List[str]:
        """Format suggestions section"""
        result = ["### [SUGGESTIONS]"]
        for imp in improvements[:3]:
            result.append(f"**{imp['category'].title()}**: {imp['suggestion']}")
            result.append(f"  Example: {imp['example']}")
            result.append("")
        return result

    def generate_feedback(self, analysis: PromptAnalysis) -> str:
        """Generate human-readable feedback"""
        feedback = []

        # Overall assessment
        level = self._get_skill_level(analysis.overall_score)
        feedback.append(f"## Prompt Quality Assessment: {analysis.overall_score:.0f}/100 ({level})")
        feedback.append("")

        # Scores breakdown
        feedback.append("### Scores Breakdown")
        feedback.extend(
            [
                f"- Clarity: {analysis.clarity_score:.0f}/100",
                f"- Logic: {analysis.logic_score:.0f}/100",
                f"- Context: {analysis.context_score:.0f}/100",
                f"- Structure: {analysis.structure_score:.0f}/100",
                "",
            ]
        )

        # Strengths
        if analysis.strengths:
            feedback.append("### [STRENGTHS]")
            feedback.extend(f"- {strength}" for strength in analysis.strengths)
            feedback.append("")

        # Issues
        if analysis.issues:
            feedback.extend(self._format_issues(analysis.issues))

        # Suggestions
        if analysis.improvements:
            feedback.extend(self._format_suggestions(analysis.improvements))

        # Learning tip
        feedback.extend(["### [LEARNING TIP]", self._get_learning_tip(analysis)])

        return "\n".join(feedback)

    def _get_skill_level(self, score: float) -> str:
        """Determine skill level from score"""
        if score >= 90:
            return "Expert"
        elif score >= 75:
            return "Advanced"
        elif score >= 60:
            return "Intermediate"
        elif score >= 40:
            return "Developing"
        else:
            return "Beginner"

    def _get_learning_tip(self, analysis: PromptAnalysis) -> str:
        """Generate personalized learning tip"""
        lowest_score = min(analysis.clarity_score, analysis.logic_score, analysis.context_score, analysis.structure_score)

        if lowest_score == analysis.clarity_score:
            return "Focus on using specific terms and avoiding ambiguity. Replace vague words with concrete descriptions."
        elif lowest_score == analysis.logic_score:
            return "Practice using logical connectors (first, then, because, if) to show relationships between tasks."
        elif lowest_score == analysis.context_score:
            return "Consider specifying the technical environment, constraints, and expected output format."
        else:
            return "For complex requests, use numbered lists or bullet points to organize your thoughts clearly."

    def _hash_prompt(self, prompt: str) -> str:
        """Generate unique hash for prompt"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    def _save_analysis(self, analysis: PromptAnalysis):
        """Save analysis for learning"""
        file_path = self.learning_dir / f"analysis_{analysis.prompt_hash}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "hash": analysis.prompt_hash,
                    "timestamp": analysis.timestamp,
                    "scores": {
                        "overall": analysis.overall_score,
                        "clarity": analysis.clarity_score,
                        "logic": analysis.logic_score,
                        "context": analysis.context_score,
                        "structure": analysis.structure_score,
                    },
                    "issues_count": len(analysis.issues),
                    "improvements_count": len(analysis.improvements),
                },
                f,
                indent=2,
            )

    def _load_learning_history(self) -> Dict:
        """Load historical learning data"""
        history_file = self.learning_dir / "learning_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"analyses": [], "patterns": {}}

    def track_improvement(self, user_id: str) -> Dict:
        """Track user improvement over time"""
        user_dir = self.learning_dir / user_id
        if not user_dir.exists():
            return {"message": "No history found for user"}

        analyses = []
        for file in user_dir.glob("analysis_*.json"):
            with open(file, "r", encoding="utf-8") as f:
                analyses.append(json.load(f))

        if not analyses:
            return {"message": "No analyses found"}

        # Sort by timestamp
        analyses.sort(key=lambda x: x["timestamp"])

        # Calculate improvement trends
        recent = analyses[-10:]  # Last 10 analyses
        older = analyses[:10] if len(analyses) > 10 else analyses[:5]

        recent_avg = sum(a["scores"]["overall"] for a in recent) / len(recent)
        older_avg = sum(a["scores"]["overall"] for a in older) / len(older)

        improvement = recent_avg - older_avg

        return {
            "total_analyses": len(analyses),
            "recent_average": recent_avg,
            "improvement": improvement,
            "trend": "improving" if improvement > 0 else "declining",
            "best_dimension": max(
                ["clarity", "logic", "context", "structure"], key=lambda d: sum(a["scores"][d] for a in recent) / len(recent)
            ),
            "focus_area": min(
                ["clarity", "logic", "context", "structure"], key=lambda d: sum(a["scores"][d] for a in recent) / len(recent)
            ),
        }


def main():
    """Example usage and testing"""
    analyzer = PromptFeedbackAnalyzer()

    # Test prompts with varying quality
    test_prompts = [
        # Poor quality
        "fix the code and make it better somehow",
        # Medium quality
        "Update the login function to handle errors and then test it",
        # Good quality
        """1. Analyze the authentication module in auth.py
        2. Fix the SQL injection vulnerability in the login function
        3. Add input validation for email and password fields
        4. Write unit tests with pytest covering edge cases
        5. Update the documentation with security notes""",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"Test Prompt {i}:")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}")

        analysis = analyzer.analyze(prompt)
        feedback = analyzer.generate_feedback(analysis)
        print(feedback)


if __name__ == "__main__":
    main()
