"""Tests for BenchmarkAnalyzer - Competitive Benchmarking System.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (comprehensive test coverage)
"""

from scripts.benchmark_analyzer import (
    BenchmarkAnalyzer,
    BenchmarkResult,
    Competitor,
    CompetitorSearcher,
    DifferentiationGenerator,
    DifferentiationPoint,
    ProductAnalysis,
    ProductAnalyzer,
    Strength,
    Weakness,
)


class TestCompetitor:
    """Test Competitor dataclass."""

    def test_competitor_creation(self):
        """Test Competitor object creation."""
        comp = Competitor(
            name="Todoist",
            github_url="https://github.com/Doist/todoist-api",
            github_stars=50000,
        )

        assert comp.name == "Todoist"
        assert comp.github_stars == 50000
        assert comp.popularity_score == 0.0  # Default


class TestStrengthWeakness:
    """Test Strength and Weakness dataclasses."""

    def test_strength_to_dict(self):
        """Test Strength serialization."""
        strength = Strength(
            title="Natural Language",
            description="Parse 'tomorrow 3pm' automatically",
        )

        data = strength.to_dict()
        assert data["title"] == "Natural Language"
        assert data["description"] == "Parse 'tomorrow 3pm' automatically"

    def test_weakness_to_dict(self):
        """Test Weakness serialization."""
        weakness = Weakness(
            category="AI",
            description="No auto-priority",
            severity="medium",
        )

        data = weakness.to_dict()
        assert data["category"] == "AI"
        assert data["description"] == "No auto-priority"


class TestCompetitorSearcher:
    """Test CompetitorSearcher functionality."""

    def test_initialization(self, tmp_path):
        """Test searcher initialization."""
        searcher = CompetitorSearcher()
        assert searcher.cache_dir.exists()

    def test_search_competitors_min_results(self):
        """Test search returns minimum 3 competitors."""
        searcher = CompetitorSearcher()
        results = searcher.search_competitors("todo app")

        assert len(results) >= 3
        assert all(isinstance(c, Competitor) for c in results)

    def test_search_competitors_max_results(self):
        """Test search respects max_results limit."""
        searcher = CompetitorSearcher()
        results = searcher.search_competitors("todo app", max_results=2)

        assert len(results) <= 2

    def test_rank_by_popularity(self):
        """Test competitors are ranked by popularity."""
        searcher = CompetitorSearcher()
        competitors = [
            Competitor("A", github_stars=1000, recent_commits=50, readme_length=2000, community_size=500),
            Competitor("B", github_stars=5000, recent_commits=100, readme_length=5000, community_size=2000),
            Competitor("C", github_stars=500, recent_commits=20, readme_length=1000, community_size=200),
        ]

        ranked = searcher._rank_by_popularity(competitors)

        # B should be first (highest stars)
        assert ranked[0].name == "B"
        assert ranked[0].popularity_score > ranked[1].popularity_score

    def test_search_caching(self, tmp_path):
        """Test search results are cached."""
        searcher = CompetitorSearcher()
        searcher.cache_dir = tmp_path

        # First search
        results1 = searcher.search_competitors("todo app")

        # Second search (should use cache)
        results2 = searcher.search_competitors("todo app")

        assert len(results1) == len(results2)
        # Cache file should exist
        cache_files = list(tmp_path.glob("*.json"))
        assert len(cache_files) >= 1


class TestProductAnalyzer:
    """Test ProductAnalyzer functionality."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = ProductAnalyzer()
        assert analyzer.cache_dir.exists()

    def test_analyze_product(self):
        """Test product analysis."""
        analyzer = ProductAnalyzer()
        competitor = Competitor(
            name="Todoist",
            github_url="https://github.com/Doist/todoist-api",
            github_stars=50000,
            readme_length=5000,
        )

        analysis = analyzer.analyze_product(competitor)

        assert isinstance(analysis, ProductAnalysis)
        assert analysis.name == "Todoist"
        assert analysis.github_stars == 50000
        assert len(analysis.strengths) > 0
        assert len(analysis.weaknesses) > 0

    def test_extract_strengths(self):
        """Test strength extraction."""
        analyzer = ProductAnalyzer()
        strengths = analyzer._mock_extract_strengths("Todoist")

        assert len(strengths) >= 3
        assert all(isinstance(s, Strength) for s in strengths)
        assert all(s.title and s.description for s in strengths)

    def test_extract_weaknesses(self):
        """Test weakness extraction."""
        analyzer = ProductAnalyzer()
        weaknesses = analyzer._mock_extract_weaknesses("Todoist")

        assert len(weaknesses) >= 1
        assert all(isinstance(w, Weakness) for w in weaknesses)
        assert all(w.category and w.description for w in weaknesses)

    def test_analysis_caching(self, tmp_path):
        """Test analysis results are cached."""
        analyzer = ProductAnalyzer()
        analyzer.cache_dir = tmp_path

        competitor = Competitor("TestProduct", github_stars=1000)

        # First analysis
        analysis1 = analyzer.analyze_product(competitor)

        # Second analysis (should use cache)
        analysis2 = analyzer.analyze_product(competitor)

        assert analysis1.name == analysis2.name
        # Cache file should exist
        cache_files = list(tmp_path.glob("*.json"))
        assert len(cache_files) >= 1


class TestDifferentiationGenerator:
    """Test DifferentiationGenerator functionality."""

    def test_generate_differentiation_min_3(self):
        """Test generates minimum 3 differentiation points."""
        generator = DifferentiationGenerator()

        analyses = [
            ProductAnalysis(
                name="Product1",
                strengths=[Strength("Feature A", "Description A")],
                weaknesses=[Weakness("Category1", "Weakness A")],
            ),
            ProductAnalysis(
                name="Product2",
                strengths=[Strength("Feature B", "Description B")],
                weaknesses=[Weakness("Category1", "Weakness B")],
            ),
        ]

        points = generator.generate_differentiation(analyses)

        assert len(points) >= 3
        assert all(isinstance(p, DifferentiationPoint) for p in points)

    def test_find_common_gaps(self):
        """Test gap analysis finds missing features."""
        generator = DifferentiationGenerator()

        analyses = [
            ProductAnalysis(name="P1", strengths=[Strength("Natural Language", "NL processing")]),
            ProductAnalysis(name="P2", strengths=[Strength("Calendar Sync", "Calendar integration")]),
        ]

        gaps = generator._find_common_gaps(analyses)

        # Should find features that no competitor has
        assert isinstance(gaps, list)
        assert "ai auto-priority" in gaps  # Neither has AI

    def test_find_common_weaknesses(self):
        """Test finds weaknesses shared by multiple competitors."""
        generator = DifferentiationGenerator()

        analyses = [
            ProductAnalysis(name="P1", weaknesses=[Weakness("AI", "No AI features", "medium")]),
            ProductAnalysis(name="P2", weaknesses=[Weakness("AI", "Lacks AI", "medium")]),
        ]

        common_weaknesses = generator._find_common_weaknesses(analyses)

        assert len(common_weaknesses) >= 1
        assert common_weaknesses[0].category.lower() == "ai"

    def test_differentiation_point_to_dict(self):
        """Test DifferentiationPoint serialization."""
        point = DifferentiationPoint(
            point="AI Auto-Priority",
            rationale="No competitor has this",
            target_market="Busy professionals",
            implementation_complexity="medium",
            estimated_impact="high",
        )

        data = point.to_dict()

        assert data["point"] == "AI Auto-Priority"
        assert data["complexity"] == "medium"
        assert data["impact"] == "high"


class TestBenchmarkResult:
    """Test BenchmarkResult functionality."""

    def test_to_yaml_section(self):
        """Test YAML section generation."""
        analyses = [
            ProductAnalysis(
                name="Todoist",
                github_stars=50000,
                strengths=[Strength("NL", "Natural language")],
                weaknesses=[Weakness("AI", "No AI")],
            )
        ]

        differentiation = [
            DifferentiationPoint(
                point="AI Features",
                rationale="Missing in competitors",
                target_market="Tech users",
            )
        ]

        result = BenchmarkResult(query="todo app", competitors=analyses, differentiation=differentiation)

        yaml_section = result.to_yaml_section()

        # Verify P16 compliance
        assert "benchmarking" in yaml_section
        assert "competitors" in yaml_section["benchmarking"]
        assert "differentiation" in yaml_section["benchmarking"]
        assert len(yaml_section["benchmarking"]["competitors"]) >= 1
        assert len(yaml_section["benchmarking"]["differentiation"]) >= 1

    def test_yaml_section_structure(self):
        """Test YAML section has correct structure."""
        result = BenchmarkResult(
            query="test",
            competitors=[
                ProductAnalysis(
                    name="Test",
                    github_stars=1000,
                    strengths=[Strength("S1", "Description")],
                    weaknesses=[Weakness("W1", "Description")],
                )
            ],
            differentiation=[DifferentiationPoint("Point", "Rationale", "Target")],
        )

        yaml_section = result.to_yaml_section()
        bench = yaml_section["benchmarking"]

        # Check competitor structure
        assert "name" in bench["competitors"][0]
        assert "github_stars" in bench["competitors"][0]
        assert "strengths" in bench["competitors"][0]
        assert "weaknesses" in bench["competitors"][0]

        # Check differentiation structure
        assert "point" in bench["differentiation"][0]
        assert "rationale" in bench["differentiation"][0]
        assert "target" in bench["differentiation"][0]


class TestBenchmarkAnalyzer:
    """Test BenchmarkAnalyzer main interface."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = BenchmarkAnalyzer()
        assert analyzer.searcher is not None
        assert analyzer.analyzer is not None
        assert analyzer.diff_generator is not None

    def test_analyze_full_pipeline(self):
        """Test complete analysis pipeline."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("todo app")

        assert isinstance(result, BenchmarkResult)
        assert result.query == "todo app"
        assert len(result.competitors) >= 3
        assert len(result.differentiation) >= 3

    def test_analyze_todo_app(self):
        """Test analysis for todo app category."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("todo app")

        # Should find known competitors
        competitor_names = [c.name for c in result.competitors]
        assert any("Todoist" in name or "TickTick" in name or "Things" in name for name in competitor_names)

    def test_analyze_habit_tracker(self):
        """Test analysis for habit tracker category."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("habit tracker")

        # Should find habit-related competitors
        competitor_names = [c.name for c in result.competitors]
        assert any("Habitica" in name or "Habit" in name for name in competitor_names)

    def test_to_yaml(self):
        """Test YAML conversion."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("test query")
        yaml_section = analyzer.to_yaml(result)

        assert "benchmarking" in yaml_section
        assert isinstance(yaml_section["benchmarking"], dict)

    def test_performance_under_30min(self):
        """Test analysis completes within 30 minutes."""
        import time

        analyzer = BenchmarkAnalyzer()

        start = time.time()
        analyzer.analyze("todo app")
        duration = time.time() - start

        # Should be much faster than 30 minutes (currently <1 second with mocks)
        assert duration < 1800  # 30 minutes in seconds


class TestP16Compliance:
    """Test P16 Constitutional Compliance."""

    def test_yaml_has_required_sections(self):
        """Test YAML section has all P16 required sections."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("test")
        yaml_section = analyzer.to_yaml(result)

        bench = yaml_section["benchmarking"]

        # P16 requirements
        assert "competitors" in bench
        assert "differentiation" in bench
        assert "target_market" in bench

    def test_minimum_3_competitors(self):
        """Test P16 requirement: minimum 3 competitors."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("test")

        assert len(result.competitors) >= 3

    def test_minimum_3_differentiation_points(self):
        """Test P16 requirement: minimum 3 differentiation points."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("test")

        assert len(result.differentiation) >= 3

    def test_competitors_have_strengths_weaknesses(self):
        """Test each competitor has strengths and weaknesses analyzed."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("todo app")

        for comp in result.competitors:
            assert len(comp.strengths) > 0
            assert len(comp.weaknesses) > 0

    def test_differentiation_has_rationale(self):
        """Test each differentiation point has rationale."""
        analyzer = BenchmarkAnalyzer()
        result = analyzer.analyze("test")

        for diff in result.differentiation:
            assert diff.point
            assert diff.rationale
            assert diff.target_market
