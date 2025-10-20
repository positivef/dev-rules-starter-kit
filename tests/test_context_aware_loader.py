"""
Test Context-Aware Constitutional Loader (Plaesy/cc-sdd pattern)

Based on: Plaesy context-aware system + cc-sdd auto-detection
Pattern: Auto-detect project context and load relevant articles
Validation: TDD-first approach
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestContextAnalysis:
    """Test project context analysis"""

    def test_loader_initialization(self):
        """Test: ContextAwareLoader initializes with thresholds"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        assert loader.THRESHOLDS["HIGH"] == 0.8
        assert loader.THRESHOLDS["MEDIUM"] == 0.6
        assert loader.THRESHOLDS["LOW"] == 0.4

    def test_analyze_file_structure(self):
        """Test: Analyze project file structure"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create test structure
            (temp_dir / "tests").mkdir()
            (temp_dir / "tests" / "test_example.py").write_text("def test(): pass")
            (temp_dir / "app").mkdir()
            (temp_dir / "app" / "routers").mkdir()
            (temp_dir / "app" / "routers" / "api.py").write_text("# API routes")

            scores = loader.analyze_file_structure(temp_dir)

            # Should detect TDD and API patterns
            assert "Article III (TDD)" in scores
            assert "Article VII (API)" in scores
            assert scores["Article III (TDD)"] > 0.5  # Has tests/
            assert scores["Article VII (API)"] > 0.5  # Has app/routers/

        finally:
            shutil.rmtree(temp_dir)

    def test_analyze_task_description(self):
        """Test: Analyze task description for keywords"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()

        # API endpoint task
        scores = loader.analyze_task_description("Add API endpoint for user authentication")
        assert "Article VII (API)" in scores
        assert scores["Article VII (API)"] > 0

        # Refactoring task
        scores = loader.analyze_task_description("Refactor legacy code to improve maintainability")
        assert "Article IX (Refactoring)" in scores

        # Testing task
        scores = loader.analyze_task_description("Write unit tests for authentication module")
        assert "Article III (TDD)" in scores

    def test_combine_scores(self):
        """Test: Combine file structure and task description scores"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create test structure
            (temp_dir / "tests").mkdir()

            scores = loader.analyze_project_context(temp_dir, "Add API endpoint for user management")

            # Should combine both signals
            assert "Article III (TDD)" in scores  # From file structure
            assert "Article VII (API)" in scores  # From task description

        finally:
            shutil.rmtree(temp_dir)


class TestThresholdFiltering:
    """Test threshold-based article filtering"""

    def test_filter_by_high_threshold(self):
        """Test: Filter articles by HIGH threshold (0.8)"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()

        scores = {
            "Article III (TDD)": 0.9,  # Above HIGH
            "Article V (Emoji)": 1.0,  # Always enforce
            "Article VII (API)": 0.6,  # Below HIGH
        }

        filtered = loader.filter_by_threshold(scores, "HIGH")

        assert "Article III (TDD)" in filtered
        assert "Article V (Emoji)" in filtered
        assert "Article VII (API)" not in filtered

    def test_filter_by_medium_threshold(self):
        """Test: Filter articles by MEDIUM threshold (0.6)"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()

        scores = {
            "Article III (TDD)": 0.7,
            "Article VII (API)": 0.6,
            "Article IX (Refactoring)": 0.5,  # Below MEDIUM
        }

        filtered = loader.filter_by_threshold(scores, "MEDIUM")

        assert "Article III (TDD)" in filtered
        assert "Article VII (API)" in filtered
        assert "Article IX (Refactoring)" not in filtered

    def test_always_enforce_articles(self):
        """Test: Some articles always enforced (Article V - Emoji)"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()

        scores = loader.analyze_project_context(Path("."), "Simple task")

        # Article V (Emoji) should always be present
        assert "Article V (Emoji)" in scores
        assert scores["Article V (Emoji)"] == 1.0


class TestArticleRecommendation:
    """Test article recommendation system"""

    def test_recommend_for_api_project(self):
        """Test: Recommend articles for API project"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create API project structure
            (temp_dir / "app").mkdir()
            (temp_dir / "app" / "routers").mkdir()
            (temp_dir / "tests").mkdir()

            recommendations = loader.recommend_articles(temp_dir, "Add new API endpoint for products")

            # Should recommend API and TDD articles
            assert "Article III (TDD)" in recommendations
            assert "Article VII (API)" in recommendations
            assert "Article V (Emoji)" in recommendations  # Always

        finally:
            shutil.rmtree(temp_dir)

    def test_recommend_for_refactoring_task(self):
        """Test: Recommend articles for refactoring task"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()

        recommendations = loader.recommend_articles(Path("."), "Refactor authentication module to improve code quality")

        # Should recommend refactoring article
        assert "Article IX (Refactoring)" in recommendations

    def test_no_over_recommendation(self):
        """Test: Don't recommend irrelevant articles"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Simple project without special structure
            (temp_dir / "src").mkdir()

            recommendations = loader.recommend_articles(temp_dir, "Fix typo in README")

            # Should only recommend always-enforce articles
            assert "Article V (Emoji)" in recommendations
            # Should NOT recommend API/TDD/Refactoring
            assert len(recommendations) <= 2  # Only essential articles

        finally:
            shutil.rmtree(temp_dir)


class TestPerformanceOptimization:
    """Test context analysis performance"""

    def test_fast_analysis(self):
        """Test: Context analysis completes quickly"""
        import time
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create realistic project structure
            (temp_dir / "tests").mkdir()
            (temp_dir / "app").mkdir()
            (temp_dir / "docs").mkdir()

            start_time = time.time()
            loader.analyze_project_context(temp_dir, "Add new feature")
            duration = time.time() - start_time

            # Should complete in under 100ms
            assert duration < 0.1

        finally:
            shutil.rmtree(temp_dir)


class TestIntegration:
    """Test context-aware loader integration"""

    def test_integration_with_guards(self):
        """Test: Context-aware loader works with constitutional guards"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader
        from scripts.constitutional_guards import ConstitutionalGuard, Task

        loader = ContextAwareConstitutionalLoader()

        # Analyze context
        recommendations = loader.recommend_articles(Path("."), "Implement new API endpoint")

        # If Article III recommended, validate TDD
        if "Article III (TDD)" in recommendations:
            tasks = [
                Task(id="1", description="Write test", phase=1, order=1, type="test"),
                Task(
                    id="2",
                    description="Implement API",
                    phase=1,
                    order=2,
                    type="implementation",
                ),
            ]

            result = ConstitutionalGuard.against_implementation_before_tests(tasks)
            assert result.succeeded is True

    def test_export_recommendations(self):
        """Test: Export recommendations to JSON"""
        from scripts.context_aware_loader import ContextAwareConstitutionalLoader

        loader = ContextAwareConstitutionalLoader()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            recommendations = loader.recommend_articles(Path("."), "Add API endpoint")

            output_file = temp_dir / "recommendations.json"
            loader.export_recommendations(recommendations, output_file)

            assert output_file.exists()

            import json

            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "articles" in data
            assert "timestamp" in data

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
