"""Session Insights Generator - Advanced productivity and optimization insights.

Features:
- Peak productivity hour analysis (hourly patterns)
- Task efficiency scoring (0-100 scale)
- Optimization recommendations (impact/effort prioritization)
- Category-based suggestion generation

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P10: Windows encoding (no emojis)
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion with prioritization.

    Attributes:
        category: Suggestion category (performance, quality, testing, etc.)
        description: Human-readable suggestion text
        impact: Expected impact level (high/medium/low)
        effort: Required effort level (high/medium/low)
        priority: Calculated priority score (1-10, higher is more urgent)
    """

    category: str
    description: str
    impact: str  # high/medium/low
    effort: str  # high/medium/low
    priority: int  # 1-10


class ProductivityAnalyzer:
    """Analyze productivity patterns from session data.

    Identifies peak working hours, task efficiency,
    and productivity trends.
    """

    def __init__(self):
        """Initialize productivity analyzer."""
        self.min_productivity_score = 50.0  # Minimum to consider "peak"

    def analyze_peak_hours(self, session_data: List[Dict[str, Any]]) -> List[int]:
        """Identify peak productivity hours (0-23).

        Args:
            session_data: List of session dictionaries with keys:
                - hour: int (0-23)
                - tasks_completed: int
                - quality_score: float (0-100)

        Returns:
            List of peak hours (0-23), sorted by productivity

        Algorithm:
            - Calculates productivity score per hour (tasks * quality)
            - Returns hours above threshold
            - Maximum 5 peak hours
        """
        if not session_data:
            return []

        # Group by hour and calculate productivity scores
        hourly_productivity = {}

        for session in session_data:
            hour = session.get("hour", 0)
            tasks = session.get("tasks_completed", 0)
            quality = session.get("quality_score", 0.0)

            # Productivity score = tasks * quality (normalized)
            productivity_score = tasks * (quality / 100.0)

            if hour not in hourly_productivity:
                hourly_productivity[hour] = []

            hourly_productivity[hour].append(productivity_score)

        # Calculate average productivity per hour
        hourly_averages = {hour: statistics.mean(scores) for hour, scores in hourly_productivity.items()}

        if not hourly_averages:
            return []

        # Find threshold (mean + 0.5 * stdev)
        all_scores = list(hourly_averages.values())
        mean_score = statistics.mean(all_scores)

        if len(all_scores) >= 2:
            stdev = statistics.stdev(all_scores)
            threshold = mean_score + (0.5 * stdev)
        else:
            threshold = mean_score

        # Get hours above threshold
        peak_hours = [hour for hour, score in hourly_averages.items() if score >= threshold]

        # Sort by productivity (descending) and return top 5
        peak_hours.sort(key=lambda h: hourly_averages[h], reverse=True)
        return peak_hours[:5]

    def calculate_task_efficiency(self, task_data: Dict[str, Any]) -> float:
        """Calculate task efficiency score (0-100).

        Args:
            task_data: Task dictionary with keys:
                - estimated_time_min: int
                - actual_time_min: int
                - quality_score: float (optional, 0-100)
                - error_count: int (optional)
                - revision_count: int (optional)

        Returns:
            Efficiency score (0-100)

        Algorithm:
            - Time efficiency (40%): estimated / actual
            - Quality (30%): quality_score
            - Error rate (20%): penalty for errors
            - Revision count (10%): penalty for revisions
        """
        estimated_time = task_data.get("estimated_time_min", 60)
        actual_time = task_data.get("actual_time_min", 60)
        quality_score = task_data.get("quality_score", 80.0)
        error_count = task_data.get("error_count", 0)
        revision_count = task_data.get("revision_count", 0)

        # 1. Time efficiency (40 points)
        if actual_time > 0:
            time_ratio = estimated_time / actual_time
            time_efficiency = min(40, time_ratio * 40)
        else:
            time_efficiency = 0

        # 2. Quality (30 points)
        quality_points = (quality_score / 100.0) * 30

        # 3. Error penalty (20 points)
        error_penalty = max(0, 20 - (error_count * 4))

        # 4. Revision penalty (10 points)
        revision_penalty = max(0, 10 - (revision_count * 2))

        # Total score
        efficiency = time_efficiency + quality_points + error_penalty + revision_penalty

        return round(min(100.0, max(0.0, efficiency)), 2)


class OptimizationAdvisor:
    """Generate optimization recommendations with prioritization.

    Analyzes system metrics and suggests improvements
    prioritized by impact and effort.
    """

    def __init__(self):
        """Initialize optimization advisor."""
        self.thresholds = {
            "slow_response_ms": 1000,
            "low_cache_hit_rate": 0.7,
            "high_error_rate": 1.0,
            "low_test_coverage": 0.80,
        }

    def generate_suggestions(self, analysis_results: Dict[str, Any]) -> List[OptimizationSuggestion]:
        """Generate prioritized optimization suggestions.

        Args:
            analysis_results: Dictionary with metrics:
                - avg_response_time_ms: float
                - cache_hit_rate: float (0-1)
                - error_rate: float (errors per minute)
                - test_coverage: float (0-1)

        Returns:
            List of OptimizationSuggestion objects

        Categories:
            - performance: Speed, latency, throughput
            - quality: Code quality, errors, bugs
            - testing: Test coverage, test quality
            - maintenance: Tech debt, refactoring
        """
        suggestions = []

        # Check response time
        response_time = analysis_results.get("avg_response_time_ms", 0)
        if response_time > self.thresholds["slow_response_ms"]:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    description=f"Response time is {response_time:.0f}ms. " "Consider caching, query optimization, or CDN.",
                    impact="high",
                    effort="medium",
                    priority=0,  # Will be calculated
                )
            )

        # Check cache hit rate
        cache_hit_rate = analysis_results.get("cache_hit_rate", 1.0)
        if cache_hit_rate < self.thresholds["low_cache_hit_rate"]:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    description=f"Cache hit rate is {cache_hit_rate:.1%}. " "Review caching strategy and TTL settings.",
                    impact="medium",
                    effort="low",
                    priority=0,
                )
            )

        # Check error rate
        error_rate = analysis_results.get("error_rate", 0.0)
        if error_rate > self.thresholds["high_error_rate"]:
            suggestions.append(
                OptimizationSuggestion(
                    category="quality",
                    description=f"Error rate is {error_rate:.1f}/min. " "Review error handling and add monitoring.",
                    impact="high",
                    effort="medium",
                    priority=0,
                )
            )

        # Check test coverage
        test_coverage = analysis_results.get("test_coverage", 1.0)
        if test_coverage < self.thresholds["low_test_coverage"]:
            suggestions.append(
                OptimizationSuggestion(
                    category="testing",
                    description=f"Test coverage is {test_coverage:.1%}. " "Add tests for critical paths and edge cases.",
                    impact="medium",
                    effort="medium",
                    priority=0,
                )
            )

        # If no issues, suggest maintenance
        if not suggestions:
            suggestions.append(
                OptimizationSuggestion(
                    category="maintenance",
                    description="System is healthy. Consider refactoring " "technical debt or improving documentation.",
                    impact="low",
                    effort="low",
                    priority=5,
                )
            )

        return suggestions

    def prioritize_actions(self, suggestions: List[OptimizationSuggestion]) -> List[OptimizationSuggestion]:
        """Prioritize suggestions by impact/effort ratio.

        Args:
            suggestions: List of OptimizationSuggestion objects

        Returns:
            Sorted list by priority (highest first)

        Priority Calculation:
            - high impact + low effort = 10 (quick wins)
            - high impact + medium effort = 8
            - high impact + high effort = 6
            - medium impact + low effort = 7
            - medium impact + medium effort = 5
            - medium impact + high effort = 3
            - low impact + low effort = 4
            - low impact + medium effort = 2
            - low impact + high effort = 1
        """
        if not suggestions:
            return []

        # Impact/effort priority matrix
        priority_matrix = {
            ("high", "low"): 10,
            ("high", "medium"): 8,
            ("high", "high"): 6,
            ("medium", "low"): 7,
            ("medium", "medium"): 5,
            ("medium", "high"): 3,
            ("low", "low"): 4,
            ("low", "medium"): 2,
            ("low", "high"): 1,
        }

        # Calculate priority for each suggestion
        prioritized = []
        for suggestion in suggestions:
            priority = priority_matrix.get((suggestion.impact, suggestion.effort), 5)

            # Create new suggestion with calculated priority
            prioritized_suggestion = OptimizationSuggestion(
                category=suggestion.category,
                description=suggestion.description,
                impact=suggestion.impact,
                effort=suggestion.effort,
                priority=priority,
            )

            prioritized.append(prioritized_suggestion)

        # Sort by priority (descending)
        prioritized.sort(key=lambda s: s.priority, reverse=True)

        return prioritized
