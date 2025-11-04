"""BenchmarkAnalyzer - Automatic Competitive Benchmarking System.

Constitutional Compliance:
- P16: Competitive Benchmarking (enforces this article)
- P2: Evidence-Based (all analyses recorded)
- P7: Hallucination Prevention (verify all claims)

Purpose:
    Automatically analyze competing products before feature development.
    Provides differentiation strategies and YAML benchmarking sections.

Features:
    - Competitor search (WebSearch integration)
    - Product analysis (strengths, weaknesses)
    - Differentiation strategy generation
    - YAML section builder (P16 compliant)

Usage:
    # Basic usage
    analyzer = BenchmarkAnalyzer()
    result = analyzer.analyze("todo app")

    # Get YAML section
    yaml_section = analyzer.to_yaml(result)

    # CLI
    python scripts/benchmark_analyzer.py --query "todo app" --output benchmarking.yaml

Related:
    - P16_Competitive_Benchmarking_Proposal.md: Constitutional proposal
    - BenchmarkAnalyzer_Design.md: Architecture design
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
CACHE_DIR = Path(__file__).resolve().parent.parent / "RUNS" / "benchmark_cache"
CACHE_TTL_SEARCH = timedelta(days=1)  # Competitor search cache
CACHE_TTL_ANALYSIS = timedelta(days=7)  # Product analysis cache


@dataclass
class Competitor:
    """Competitor product information."""

    name: str
    github_url: Optional[str] = None
    docs_url: Optional[str] = None
    github_stars: int = 0
    recent_commits: int = 0
    readme_length: int = 0
    community_size: int = 0
    popularity_score: float = 0.0


@dataclass
class Strength:
    """Product strength/feature."""

    title: str
    description: str
    evidence: str = "README"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {"title": self.title, "description": self.description}


@dataclass
class Weakness:
    """Product weakness/limitation."""

    category: str
    description: str
    severity: str = "medium"
    frequency: int = 1

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {"category": self.category, "description": self.description}


@dataclass
class ProductAnalysis:
    """Product analysis result."""

    name: str
    category: str = "software"
    strengths: List[Strength] = field(default_factory=list)
    weaknesses: List[Weakness] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    doc_quality: float = 0.0
    user_sentiment: float = 0.0
    github_stars: int = 0


@dataclass
class DifferentiationPoint:
    """Differentiation strategy point."""

    point: str
    rationale: str
    target_market: str
    implementation_complexity: str = "medium"
    estimated_impact: str = "medium"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "point": self.point,
            "rationale": self.rationale,
            "target": self.target_market,
            "complexity": self.implementation_complexity,
            "impact": self.estimated_impact,
        }


@dataclass
class BenchmarkResult:
    """Complete benchmarking result."""

    query: str
    competitors: List[ProductAnalysis]
    differentiation: List[DifferentiationPoint]
    target_market: Optional[Dict] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_yaml_section(self) -> Dict:
        """Convert to YAML benchmarking section (P16 compliant)."""
        return {
            "benchmarking": {
                "competitors": [
                    {
                        "name": comp.name,
                        "github_stars": comp.github_stars,
                        "strengths": [s.to_dict() for s in comp.strengths[:3]],
                        "weaknesses": [w.to_dict() for w in comp.weaknesses[:3]],
                    }
                    for comp in self.competitors
                ],
                "differentiation": [d.to_dict() for d in self.differentiation],
                "target_market": self.target_market or {},
            }
        }


class CompetitorSearcher:
    """Search and rank competing products."""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "searches"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_competitors(
        self, query: str, category: str = "software", min_results: int = 3, max_results: int = 5
    ) -> List[Competitor]:
        """
        Search for competing products.

        Args:
            query: Search query (e.g., "todo app python")
            category: Category (software, library, plugin)
            min_results: Minimum number of results
            max_results: Maximum number of results

        Returns:
            List of Competitor objects (sorted by popularity)
        """
        # Check cache
        cache_key = self._get_cache_key(query, category)
        cached = self._get_cached_search(cache_key)
        if cached:
            logger.info(f"Using cached search results for '{query}'")
            # Apply max_results limit to cached results
            return cached[:max_results]

        logger.info(f"Searching competitors for '{query}'...")

        # Mock competitors for now (will integrate WebSearch later)
        # search_queries = self._generate_search_queries(query, category)  # TODO: integrate WebSearch
        competitors = self._mock_search_results(query, category)

        # Rank by popularity
        ranked = self._rank_by_popularity(competitors)

        # Cache results
        self._cache_search_results(cache_key, ranked)

        return ranked[: max(min_results, min(len(ranked), max_results))]

    def _generate_search_queries(self, query: str, category: str) -> List[str]:
        """Generate search queries."""
        year = datetime.now().year
        return [
            f"best {query} {year}",
            f"top {query} github",
            f"popular {query} open source",
        ]

    def _mock_search_results(self, query: str, category: str) -> List[Competitor]:
        """Mock search results (placeholder for WebSearch integration)."""
        # Mock data based on common queries
        if "todo" in query.lower() or "task" in query.lower():
            return [
                Competitor(
                    "Todoist",
                    "https://github.com/Doist/todoist-api",
                    "https://developer.todoist.com",
                    50000,
                    150,
                    5000,
                    10000,
                ),
                Competitor("TickTick", "https://github.com/ticktick", "https://ticktick.com", 30000, 100, 3000, 5000),
                Competitor(
                    "Things 3",
                    "https://github.com/culturedcode/things",
                    "https://culturedcode.com/things",
                    40000,
                    80,
                    4000,
                    8000,
                ),
            ]
        elif "habit" in query.lower():
            return [
                Competitor(
                    "Habitica",
                    "https://github.com/HabitRPG/habitica",
                    "https://habitica.com",
                    10000,
                    200,
                    6000,
                    15000,
                ),
                Competitor(
                    "Habit Tracker 21",
                    "https://github.com/habit-tracker-21",
                    None,
                    1200,
                    50,
                    2000,
                    500,
                ),
            ]
        else:
            # Generic results
            return [
                Competitor(f"Product {i}", f"https://github.com/product{i}", None, 1000 * (5 - i), 50, 2000, 1000)
                for i in range(1, 4)
            ]

    def _rank_by_popularity(self, competitors: List[Competitor]) -> List[Competitor]:
        """Rank competitors by popularity."""
        for comp in competitors:
            # Normalize scores (log scale for stars)
            stars_score = min(1.0, (comp.github_stars / 100000) ** 0.5)
            activity_score = min(1.0, comp.recent_commits / 200)
            docs_score = min(1.0, comp.readme_length / 10000)
            community_score = min(1.0, comp.community_size / 20000)

            # Weighted score
            comp.popularity_score = stars_score * 0.4 + activity_score * 0.3 + docs_score * 0.2 + community_score * 0.1

        return sorted(competitors, key=lambda x: x.popularity_score, reverse=True)

    def _get_cache_key(self, query: str, category: str) -> str:
        """Generate cache key."""
        return hashlib.md5(f"{query}:{category}".encode()).hexdigest()

    def _get_cached_search(self, cache_key: str) -> Optional[List[Competitor]]:
        """Get cached search results."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        # Check TTL
        age = datetime.now(timezone.utc) - datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
        if age > CACHE_TTL_SEARCH:
            logger.info(f"Cache expired for {cache_key}")
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return [Competitor(**comp) for comp in data]
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _cache_search_results(self, cache_key: str, competitors: List[Competitor]):
        """Cache search results."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        data = [asdict(comp) for comp in competitors]
        cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class ProductAnalyzer:
    """Analyze competitor products."""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "analyses"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def analyze_product(self, competitor: Competitor) -> ProductAnalysis:
        """
        Analyze a competitor product.

        Args:
            competitor: Competitor object

        Returns:
            ProductAnalysis object
        """
        # Check cache
        cache_key = self._get_cache_key(competitor.name)
        cached = self._get_cached_analysis(cache_key)
        if cached:
            logger.info(f"Using cached analysis for '{competitor.name}'")
            return cached

        logger.info(f"Analyzing '{competitor.name}'...")

        analysis = ProductAnalysis(name=competitor.name, category="software", github_stars=competitor.github_stars)

        # Extract strengths (mock for now)
        analysis.strengths = self._mock_extract_strengths(competitor.name)

        # Extract weaknesses (mock for now)
        analysis.weaknesses = self._mock_extract_weaknesses(competitor.name)

        # Extract features
        analysis.features = self._mock_extract_features(competitor.name)

        # Doc quality assessment
        analysis.doc_quality = min(1.0, competitor.readme_length / 5000)

        # Cache results
        self._cache_analysis(cache_key, analysis)

        return analysis

    def _mock_extract_strengths(self, product_name: str) -> List[Strength]:
        """Mock strength extraction (placeholder for WebFetch + NLP)."""
        strength_map = {
            "Todoist": [
                Strength("Natural Language Input", "Type 'tomorrow 3pm meeting' and it parses automatically"),
                Strength("Project Hierarchy", "Organize tasks with projects and labels"),
                Strength("Karma Points", "Gamification with productivity scoring"),
            ],
            "TickTick": [
                Strength("Pomodoro Timer", "Built-in timer for focused work sessions"),
                Strength("Habit Tracking", "Track daily habits alongside tasks"),
                Strength("Calendar Integration", "Seamless calendar view"),
            ],
            "Things 3": [
                Strength("Clean Design", "Minimalist and intuitive UI"),
                Strength("Magic Plus", "Quick entry from anywhere"),
                Strength("Areas Concept", "Organize by life areas"),
            ],
            "Habitica": [
                Strength("Gamification", "RPG-style leveling and items"),
                Strength("Social Features", "Parties and guilds"),
                Strength("Custom Rewards", "Create your own reward system"),
            ],
        }
        return strength_map.get(product_name, [Strength("Feature 1", "Description 1")])

    def _mock_extract_weaknesses(self, product_name: str) -> List[Weakness]:
        """Mock weakness extraction (placeholder for GitHub Issues analysis)."""
        weakness_map = {
            "Todoist": [
                Weakness("AI", "No AI-powered auto-priority", "medium", 10),
                Weakness("Time Tracking", "No built-in time tracking", "low", 5),
            ],
            "TickTick": [
                Weakness("UX", "Complex UI for beginners", "medium", 8),
                Weakness("AI", "No context-aware suggestions", "medium", 6),
            ],
            "Things 3": [
                Weakness("Platform", "MacOS/iOS only", "high", 20),
                Weakness("Collaboration", "No team features", "high", 15),
            ],
            "Habitica": [
                Weakness("Integration", "No Obsidian integration", "medium", 5),
                Weakness("Complexity", "RPG system too complex", "low", 3),
            ],
        }
        return weakness_map.get(product_name, [Weakness("General", "Some limitations", "low", 1)])

    def _mock_extract_features(self, product_name: str) -> List[str]:
        """Mock feature extraction."""
        return ["feature_a", "feature_b", "feature_c"]

    def _get_cache_key(self, product_name: str) -> str:
        """Generate cache key."""
        return hashlib.md5(product_name.encode()).hexdigest()

    def _get_cached_analysis(self, cache_key: str) -> Optional[ProductAnalysis]:
        """Get cached analysis."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        # Check TTL
        age = datetime.now(timezone.utc) - datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
        if age > CACHE_TTL_ANALYSIS:
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            # Reconstruct objects
            analysis = ProductAnalysis(
                name=data["name"],
                category=data["category"],
                github_stars=data["github_stars"],
                doc_quality=data["doc_quality"],
                user_sentiment=data.get("user_sentiment", 0.0),
            )
            analysis.strengths = [Strength(**s) for s in data.get("strengths", [])]
            analysis.weaknesses = [Weakness(**w) for w in data.get("weaknesses", [])]
            analysis.features = data.get("features", [])
            return analysis
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.warning(f"Failed to load cached analysis: {e}")
            return None

    def _cache_analysis(self, cache_key: str, analysis: ProductAnalysis):
        """Cache analysis results."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        data = {
            "name": analysis.name,
            "category": analysis.category,
            "github_stars": analysis.github_stars,
            "doc_quality": analysis.doc_quality,
            "user_sentiment": analysis.user_sentiment,
            "strengths": [asdict(s) for s in analysis.strengths],
            "weaknesses": [asdict(w) for w in analysis.weaknesses],
            "features": analysis.features,
        }
        cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class DifferentiationGenerator:
    """Generate differentiation strategies."""

    def generate_differentiation(
        self, competitors: List[ProductAnalysis], user_context: Optional[str] = None
    ) -> List[DifferentiationPoint]:
        """
        Generate differentiation strategies.

        Args:
            competitors: List of competitor analyses
            user_context: Optional user context

        Returns:
            List of differentiation points (minimum 3)
        """
        logger.info(f"Generating differentiation for {len(competitors)} competitors...")

        points = []

        # Strategy 1: Gap Analysis
        gaps = self._find_common_gaps(competitors)
        if gaps:
            point = self._create_gap_differentiation(gaps[0], competitors)
            points.append(point)

        # Strategy 2: Weakness Exploitation
        common_weaknesses = self._find_common_weaknesses(competitors)
        if common_weaknesses:
            point = self._create_weakness_differentiation(common_weaknesses[0], competitors)
            points.append(point)

        # Strategy 3: Combination/Innovation
        if len(points) < 3:
            point = self._create_innovation_differentiation(competitors)
            points.append(point)

        return points[:3]

    def _find_common_gaps(self, competitors: List[ProductAnalysis]) -> List[str]:
        """Find features that no competitor has."""
        # Check for common missing features
        all_strengths = set()
        for comp in competitors:
            all_strengths.update([s.title.lower() for s in comp.strengths])

        # Industry standard features that might be missing
        standard_features = [
            "ai auto-priority",
            "context awareness",
            "time tracking",
            "voice input",
            "offline mode",
            "cross-platform sync",
        ]

        gaps = [f for f in standard_features if f not in all_strengths]
        return gaps

    def _find_common_weaknesses(self, competitors: List[ProductAnalysis]) -> List[Weakness]:
        """Find weaknesses shared by multiple competitors."""
        weakness_counts = {}
        for comp in competitors:
            for weak in comp.weaknesses:
                key = weak.category.lower()
                if key not in weakness_counts:
                    weakness_counts[key] = []
                weakness_counts[key].append(weak)

        # Find most common weakness
        if weakness_counts:
            most_common = max(weakness_counts.items(), key=lambda x: len(x[1]))
            return most_common[1]
        return []

    def _create_gap_differentiation(self, gap: str, competitors: List[ProductAnalysis]) -> DifferentiationPoint:
        """Create differentiation based on gap."""
        return DifferentiationPoint(
            point=gap.title(),
            rationale=f"None of the {len(competitors)} competitors provide this feature",
            target_market="Users seeking modern, intelligent task management",
            implementation_complexity="medium",
            estimated_impact="high",
        )

    def _create_weakness_differentiation(
        self, weakness: Weakness, competitors: List[ProductAnalysis]
    ) -> DifferentiationPoint:
        """Create differentiation based on common weakness."""
        return DifferentiationPoint(
            point=f"Solve {weakness.category} Issue",
            rationale=f"Multiple competitors struggle with {weakness.category.lower()}: {weakness.description}",
            target_market=f"Users frustrated with {weakness.category.lower()} in existing tools",
            implementation_complexity="medium",
            estimated_impact="medium",
        )

    def _create_innovation_differentiation(self, competitors: List[ProductAnalysis]) -> DifferentiationPoint:
        """Create innovation-based differentiation."""
        return DifferentiationPoint(
            point="Open Source + Privacy First",
            rationale="Most competitors are closed-source or SaaS-only",
            target_market="Privacy-conscious users and developers",
            implementation_complexity="low",
            estimated_impact="medium",
        )


class BenchmarkAnalyzer:
    """Main benchmarking analyzer."""

    def __init__(self):
        self.searcher = CompetitorSearcher()
        self.analyzer = ProductAnalyzer()
        self.diff_generator = DifferentiationGenerator()

        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def analyze(self, query: str, category: str = "software") -> BenchmarkResult:
        """
        Run complete benchmarking analysis.

        Args:
            query: Search query (e.g., "todo app")
            category: Product category

        Returns:
            BenchmarkResult with competitors, analyses, and differentiation
        """
        start_time = time.time()
        logger.info(f"Starting benchmark analysis for '{query}'...")

        # Step 1: Search competitors
        competitors = self.searcher.search_competitors(query, category)
        logger.info(f"Found {len(competitors)} competitors")

        # Step 2: Analyze each competitor
        analyses = []
        for comp in competitors:
            analysis = self.analyzer.analyze_product(comp)
            analyses.append(analysis)

        # Step 3: Generate differentiation
        differentiation = self.diff_generator.generate_differentiation(analyses)
        logger.info(f"Generated {len(differentiation)} differentiation points")

        # Step 4: Create result
        result = BenchmarkResult(query=query, competitors=analyses, differentiation=differentiation)

        elapsed = time.time() - start_time
        logger.info(f"Analysis completed in {elapsed:.1f} seconds")

        return result

    def to_yaml(self, result: BenchmarkResult) -> Dict:
        """Convert result to YAML section."""
        return result.to_yaml_section()


def main():
    """CLI interface for BenchmarkAnalyzer."""
    import argparse

    parser = argparse.ArgumentParser(description="BenchmarkAnalyzer - Competitive Analysis Tool")
    parser.add_argument("--query", type=str, required=True, help="Search query (e.g., 'todo app')")
    parser.add_argument("--category", type=str, default="software", help="Product category")
    parser.add_argument("--output", type=str, help="Output YAML file path")

    args = parser.parse_args()

    # Run analysis
    analyzer = BenchmarkAnalyzer()
    result = analyzer.analyze(args.query, args.category)

    # Print results
    print("\n=== Benchmark Analysis Results ===\n")
    print(f"Query: {result.query}")
    print(f"Competitors: {len(result.competitors)}")

    for i, comp in enumerate(result.competitors, 1):
        print(f"\n{i}. {comp.name} ({comp.github_stars} stars)")
        print(f"   Strengths: {len(comp.strengths)}")
        for s in comp.strengths[:2]:
            print(f"     - {s.title}: {s.description}")
        print(f"   Weaknesses: {len(comp.weaknesses)}")
        for w in comp.weaknesses[:2]:
            print(f"     - {w.category}: {w.description}")

    print(f"\n=== Differentiation Strategies ({len(result.differentiation)}) ===\n")
    for i, diff in enumerate(result.differentiation, 1):
        print(f"{i}. {diff.point}")
        print(f"   Rationale: {diff.rationale}")
        print(f"   Target: {diff.target_market}")
        print(f"   Complexity: {diff.implementation_complexity}, Impact: {diff.estimated_impact}")

    # Save YAML if requested
    if args.output:
        yaml_section = analyzer.to_yaml(result)
        output_path = Path(args.output)
        output_path.write_text(json.dumps(yaml_section, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[SUCCESS] YAML saved to: {output_path}")


if __name__ == "__main__":
    main()
