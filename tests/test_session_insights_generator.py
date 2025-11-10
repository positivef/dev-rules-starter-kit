"""Tests for SessionInsightsGenerator - Advanced productivity insights.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (coverage ≥85%)
"""

from scripts.session_insights_generator import (
    OptimizationSuggestion,
    ProductivityAnalyzer,
    OptimizationAdvisor,
)


class TestOptimizationSuggestion:
    """Test OptimizationSuggestion dataclass."""

    def test_optimization_suggestion_creation(self):
        """Test creating OptimizationSuggestion instance."""
        suggestion = OptimizationSuggestion(
            category="performance",
            description="Enable caching for database queries",
            impact="high",
            effort="medium",
            priority=8,
        )

        assert suggestion.category == "performance"
        assert suggestion.description == "Enable caching for database queries"
        assert suggestion.impact == "high"
        assert suggestion.effort == "medium"
        assert suggestion.priority == 8


class TestProductivityAnalyzer:
    """Test ProductivityAnalyzer class."""

    def test_analyze_peak_hours_morning(self):
        """Test peak hours identification for morning productivity."""
        analyzer = ProductivityAnalyzer()

        # Morning productivity pattern (9am-12pm)
        session_data = [
            {"hour": 9, "tasks_completed": 5, "quality_score": 90},
            {"hour": 10, "tasks_completed": 6, "quality_score": 95},
            {"hour": 11, "tasks_completed": 5, "quality_score": 88},
            {"hour": 14, "tasks_completed": 2, "quality_score": 70},
            {"hour": 15, "tasks_completed": 3, "quality_score": 75},
        ]

        peak_hours = analyzer.analyze_peak_hours(session_data)

        assert isinstance(peak_hours, list)
        assert len(peak_hours) > 0
        assert all(isinstance(h, int) and 0 <= h <= 23 for h in peak_hours)
        # Should include morning hours
        assert any(h in [9, 10, 11] for h in peak_hours)

    def test_analyze_peak_hours_evening(self):
        """Test peak hours identification for evening productivity."""
        analyzer = ProductivityAnalyzer()

        # Evening productivity pattern (18-20)
        session_data = [
            {"hour": 18, "tasks_completed": 7, "quality_score": 92},
            {"hour": 19, "tasks_completed": 8, "quality_score": 95},
            {"hour": 20, "tasks_completed": 6, "quality_score": 90},
            {"hour": 9, "tasks_completed": 3, "quality_score": 70},
            {"hour": 10, "tasks_completed": 2, "quality_score": 65},
        ]

        peak_hours = analyzer.analyze_peak_hours(session_data)

        # Should include evening hours
        assert any(h in [18, 19, 20] for h in peak_hours)

    def test_analyze_peak_hours_empty_data(self):
        """Test peak hours with no data."""
        analyzer = ProductivityAnalyzer()

        peak_hours = analyzer.analyze_peak_hours([])

        assert isinstance(peak_hours, list)
        assert len(peak_hours) == 0  # No data = no peaks

    def test_calculate_task_efficiency_high(self):
        """Test task efficiency calculation for high-performing task."""
        analyzer = ProductivityAnalyzer()

        # High efficiency task
        task_data = {
            "estimated_time_min": 60,
            "actual_time_min": 45,  # Completed faster
            "quality_score": 95,  # High quality
            "error_count": 0,
            "revision_count": 1,
        }

        efficiency = analyzer.calculate_task_efficiency(task_data)

        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 100
        assert efficiency >= 80  # Should be high

    def test_calculate_task_efficiency_low(self):
        """Test task efficiency calculation for low-performing task."""
        analyzer = ProductivityAnalyzer()

        # Low efficiency task
        task_data = {
            "estimated_time_min": 60,
            "actual_time_min": 120,  # Took much longer
            "quality_score": 60,  # Lower quality
            "error_count": 5,
            "revision_count": 3,
        }

        efficiency = analyzer.calculate_task_efficiency(task_data)

        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 100
        assert efficiency < 50  # Should be low

    def test_calculate_task_efficiency_missing_data(self):
        """Test task efficiency with missing fields."""
        analyzer = ProductivityAnalyzer()

        # Minimal task data
        task_data = {
            "estimated_time_min": 60,
            "actual_time_min": 60,
        }

        efficiency = analyzer.calculate_task_efficiency(task_data)

        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 100

    def test_analyze_peak_hours_consistent_productivity(self):
        """Test peak hours when productivity is consistent all day."""
        analyzer = ProductivityAnalyzer()

        # Consistent productivity
        session_data = [
            {"hour": h, "tasks_completed": 5, "quality_score": 85}
            for h in range(9, 18)  # 9am-5pm
        ]

        peak_hours = analyzer.analyze_peak_hours(session_data)

        # Should still identify some peaks (even if all similar)
        assert isinstance(peak_hours, list)
        assert len(peak_hours) > 0


class TestOptimizationAdvisor:
    """Test OptimizationAdvisor class."""

    def test_generate_suggestions_performance_issues(self):
        """Test suggestion generation for performance issues."""
        advisor = OptimizationAdvisor()

        # Analysis results showing performance issues
        analysis_results = {
            "avg_response_time_ms": 2500,  # Slow
            "cache_hit_rate": 0.3,  # Low cache usage
            "error_rate": 0.5,  # Some errors
            "test_coverage": 0.75,  # Good coverage
        }

        suggestions = advisor.generate_suggestions(analysis_results)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(s, OptimizationSuggestion) for s in suggestions)

        # Should suggest performance improvements
        perf_suggestions = [s for s in suggestions if s.category == "performance"]
        assert len(perf_suggestions) > 0

    def test_generate_suggestions_quality_issues(self):
        """Test suggestion generation for quality issues."""
        advisor = OptimizationAdvisor()

        # Analysis results showing quality issues
        analysis_results = {
            "avg_response_time_ms": 150,  # Fast
            "cache_hit_rate": 0.9,  # Good cache
            "error_rate": 3.0,  # High errors
            "test_coverage": 0.50,  # Low coverage
        }

        suggestions = advisor.generate_suggestions(analysis_results)

        # Should suggest quality improvements
        quality_suggestions = [s for s in suggestions if s.category in ["quality", "testing"]]
        assert len(quality_suggestions) > 0

    def test_generate_suggestions_healthy_system(self):
        """Test suggestion generation for healthy system."""
        advisor = OptimizationAdvisor()

        # Healthy system
        analysis_results = {
            "avg_response_time_ms": 150,
            "cache_hit_rate": 0.9,
            "error_rate": 0.1,
            "test_coverage": 0.95,
        }

        suggestions = advisor.generate_suggestions(analysis_results)

        # Should have fewer/no critical suggestions
        critical_suggestions = [s for s in suggestions if s.impact == "high"]
        assert len(critical_suggestions) == 0  # No high-impact needed

    def test_prioritize_actions_by_impact_effort(self):
        """Test action prioritization by impact/effort ratio."""
        advisor = OptimizationAdvisor()

        # Mix of suggestions
        suggestions = [
            OptimizationSuggestion(
                category="performance",
                description="Quick win",
                impact="high",
                effort="low",
                priority=0,  # Will be calculated
            ),
            OptimizationSuggestion(
                category="quality",
                description="Big project",
                impact="high",
                effort="high",
                priority=0,
            ),
            OptimizationSuggestion(
                category="maintenance",
                description="Small fix",
                impact="low",
                effort="low",
                priority=0,
            ),
        ]

        prioritized = advisor.prioritize_actions(suggestions)

        assert isinstance(prioritized, list)
        assert len(prioritized) == len(suggestions)

        # High impact, low effort should be first
        assert prioritized[0].description == "Quick win"
        assert prioritized[0].priority > prioritized[-1].priority

    def test_prioritize_actions_empty_list(self):
        """Test prioritization with empty list."""
        advisor = OptimizationAdvisor()

        prioritized = advisor.prioritize_actions([])

        assert isinstance(prioritized, list)
        assert len(prioritized) == 0

    def test_generate_suggestions_returns_unique_categories(self):
        """Test that generated suggestions cover different categories."""
        advisor = OptimizationAdvisor()

        # Mixed issues
        analysis_results = {
            "avg_response_time_ms": 2000,
            "cache_hit_rate": 0.4,
            "error_rate": 2.0,
            "test_coverage": 0.60,
        }

        suggestions = advisor.generate_suggestions(analysis_results)

        # Should have multiple categories
        categories = set(s.category for s in suggestions)
        assert len(categories) >= 2  # At least 2 different categories

    def test_optimization_suggestion_valid_values(self):
        """Test that suggestions have valid impact and effort values."""
        advisor = OptimizationAdvisor()

        analysis_results = {
            "avg_response_time_ms": 1500,
            "cache_hit_rate": 0.5,
            "error_rate": 1.5,
            "test_coverage": 0.70,
        }

        suggestions = advisor.generate_suggestions(analysis_results)
        # Prioritize to calculate priority scores
        prioritized = advisor.prioritize_actions(suggestions)

        for s in prioritized:
            # Impact should be high/medium/low
            assert s.impact in ["high", "medium", "low"]
            # Effort should be high/medium/low
            assert s.effort in ["high", "medium", "low"]
            # Priority should be 1-10
            assert 1 <= s.priority <= 10
