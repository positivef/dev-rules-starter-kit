"""Tests for Context Analytics - Context usage analysis and insights.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (comprehensive test coverage)
"""

import json
import time
from datetime import datetime, timedelta, timezone


from scripts.context_analytics import (
    ContextAnalytics,
    ContextEfficiencyMetrics,
    ContextHealthIndicators,
    CoordinationMetrics,
    ContextReuseMetrics,
    HealthAnalyzer,
    MetricsCollector,
    PatternAnalyzer,
    ReportGenerator,
    SessionProductivityMetrics,
)


class TestMetricsCollector:
    """Test MetricsCollector functionality."""

    def test_initialization(self, tmp_path):
        """Test collector initialization."""
        MetricsCollector(context_dir=tmp_path)
        # No assertion needed - just verify it doesn't crash

    def test_collect_context_efficiency_metrics(self, tmp_path):
        """Test context efficiency metrics collection."""
        # Setup context
        context_file = tmp_path / "shared_context.json"
        context = {
            "project": "test",
            "version": "1.0.0",
            "sessions": [],
            "shared_knowledge": {"test_key": "test_value"},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)
        metrics = collector.collect_context_efficiency_metrics()

        assert isinstance(metrics, ContextEfficiencyMetrics)
        assert metrics.total_context_size > 0
        assert metrics.useful_context_size > 0
        assert 0 <= metrics.efficiency_score <= 100
        assert metrics.redundancy_rate >= 0
        assert metrics.compression_ratio >= 0

    def test_collect_session_productivity_metrics(self, tmp_path):
        """Test session productivity metrics collection."""
        # Setup context with session
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {
                    "session_id": "session1",
                    "agent_id": "agent1",
                    "role": "frontend",
                    "status": "active",
                    "registered_at": now.isoformat(),
                    "last_heartbeat": now.isoformat(),
                    "current_task": "TASK-001",
                }
            ],
            "shared_knowledge": {"recent_commits": ["abc123", "def456"]},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)
        metrics = collector.collect_session_productivity_metrics("session1")

        assert metrics is not None
        assert isinstance(metrics, SessionProductivityMetrics)
        assert metrics.session_id == "session1"
        assert metrics.commits_count >= 0
        assert 0 <= metrics.context_quality <= 1
        assert metrics.productivity_score >= 0

    def test_collect_session_productivity_nonexistent(self, tmp_path):
        """Test productivity metrics for nonexistent session."""
        context_file = tmp_path / "shared_context.json"
        context = {"sessions": []}
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)
        metrics = collector.collect_session_productivity_metrics("nonexistent")

        assert metrics is None

    def test_collect_context_reuse_metrics(self, tmp_path):
        """Test context reuse metrics collection."""
        context_file = tmp_path / "shared_context.json"
        context = {
            "sessions": [{"session_id": "s1"}, {"session_id": "s2"}],
            "shared_knowledge": {"key1": "val1", "key2": "val2"},
            "context_versions": [{"version": 1}, {"version": 2}],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)
        metrics = collector.collect_context_reuse_metrics()

        assert isinstance(metrics, ContextReuseMetrics)
        assert metrics.total_context_items > 0
        assert metrics.reused_items >= 0
        assert metrics.new_items >= 0
        assert 0 <= metrics.reuse_rate <= 100
        assert isinstance(metrics.reuse_by_session, dict)
        assert isinstance(metrics.most_reused_items, list)

    def test_collect_coordination_metrics(self, tmp_path):
        """Test coordination metrics collection."""
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {
                    "session_id": "s1",
                    "status": "active",
                    "last_heartbeat": now.isoformat(),
                },
                {
                    "session_id": "s2",
                    "status": "active",
                    "last_heartbeat": (now - timedelta(seconds=200)).isoformat(),
                },
            ],
            "shared_knowledge": {"open_conflicts": []},
            "context_versions": [{"version": 1}],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)
        metrics = collector.collect_coordination_metrics()

        assert isinstance(metrics, CoordinationMetrics)
        assert metrics.total_sessions == 2
        assert metrics.active_sessions >= 0
        assert metrics.session_conflicts >= 0
        assert 0 <= metrics.conflict_resolution_rate <= 100
        assert metrics.average_sync_latency >= 0

    def test_metrics_collection_performance(self, tmp_path):
        """Test metrics collection overhead is <2%."""
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {
                    "session_id": "s1",
                    "last_heartbeat": now.isoformat(),
                }
            ],
            "shared_knowledge": {},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        collector = MetricsCollector(context_dir=tmp_path)

        # Measure collection time
        start = time.time()
        collector.collect_context_efficiency_metrics()
        collector.collect_context_reuse_metrics()
        collector.collect_coordination_metrics()
        duration = time.time() - start

        # Should be very fast (<50ms for all collections)
        assert duration < 0.05  # 50 milliseconds


class TestPatternAnalyzer:
    """Test PatternAnalyzer functionality."""

    def test_analyze_efficiency_patterns(self):
        """Test efficiency pattern analysis."""
        metrics = ContextEfficiencyMetrics(
            total_context_size=1000,
            useful_context_size=850,
            efficiency_score=85.0,
            redundancy_rate=5.0,
            compression_ratio=2.5,
            timestamp=datetime.now(timezone.utc),
        )

        analyzer = PatternAnalyzer()
        insights = analyzer.analyze_efficiency_patterns(metrics)

        assert len(insights) > 0
        assert any("efficiency" in insight.lower() for insight in insights)

    def test_analyze_productivity_patterns(self):
        """Test productivity pattern analysis."""
        metrics = SessionProductivityMetrics(
            session_id="session1",
            session_duration=timedelta(hours=2),
            commits_count=10,
            files_modified=5,
            lines_changed=200,
            tasks_completed=2,
            commits_per_hour=5.0,
            context_quality=0.85,
            productivity_score=4.25,
            timestamp=datetime.now(timezone.utc),
        )

        analyzer = PatternAnalyzer()
        insights = analyzer.analyze_productivity_patterns(metrics)

        assert len(insights) > 0
        assert any("productivity" in insight.lower() or "quality" in insight.lower() for insight in insights)

    def test_analyze_reuse_patterns(self):
        """Test reuse pattern analysis."""
        metrics = ContextReuseMetrics(
            total_context_items=100,
            reused_items=65,
            new_items=35,
            reuse_rate=65.0,
            reuse_by_session={"s1": 30, "s2": 35},
            most_reused_items=[("config", 10), ("utils", 8)],
            timestamp=datetime.now(timezone.utc),
        )

        analyzer = PatternAnalyzer()
        insights = analyzer.analyze_reuse_patterns(metrics)

        assert len(insights) > 0
        assert any("reuse" in insight.lower() for insight in insights)

    def test_analyze_coordination_patterns(self):
        """Test coordination pattern analysis."""
        metrics = CoordinationMetrics(
            total_sessions=4,
            active_sessions=3,
            session_conflicts=2,
            auto_resolved_conflicts=2,
            manual_interventions=0,
            conflict_resolution_rate=100.0,
            average_sync_latency=45.0,
            context_sync_count=10,
            timestamp=datetime.now(timezone.utc),
        )

        analyzer = PatternAnalyzer()
        insights = analyzer.analyze_coordination_patterns(metrics)

        assert len(insights) > 0
        assert any("resolution" in insight.lower() or "sync" in insight.lower() for insight in insights)


class TestHealthAnalyzer:
    """Test HealthAnalyzer functionality."""

    def test_initialization(self, tmp_path):
        """Test health analyzer initialization."""
        HealthAnalyzer(context_dir=tmp_path)

    def test_assess_context_health(self, tmp_path):
        """Test context health assessment."""
        # Setup context
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "project": "test",
            "updated_at": now.isoformat(),
            "sessions": [{"session_id": "s1", "status": "active"}],
            "shared_knowledge": {},
            "context_versions": [
                {
                    "version": 1,
                    "timestamp": now.isoformat(),
                    "context_hash": "testhash",
                }
            ],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        analyzer = HealthAnalyzer(context_dir=tmp_path)
        health = analyzer.assess_context_health()

        assert isinstance(health, ContextHealthIndicators)
        assert 0 <= health.integrity_score <= 1
        assert 0 <= health.consistency_score <= 1
        assert 0 <= health.staleness_score <= 1
        assert 0 <= health.fragmentation_score <= 1
        assert health.health_status in ["excellent", "good", "fair", "poor", "critical"]
        assert health.health_grade in ["A+", "A", "B", "C", "D", "F"]
        assert isinstance(health.issues, list)
        assert isinstance(health.recommendations, list)

    def test_generate_recommendations(self, tmp_path):
        """Test recommendation generation."""
        # Create health indicators
        health = ContextHealthIndicators(
            integrity_score=0.95,
            consistency_score=0.90,
            staleness_score=0.85,
            fragmentation_score=0.10,
            health_status="excellent",
            health_grade="A",
            issues=[],
            recommendations=["Test recommendation"],
            timestamp=datetime.now(timezone.utc),
        )

        analyzer = HealthAnalyzer(context_dir=tmp_path)
        recommendations = analyzer.generate_recommendations(health)

        # Should have at least 5 recommendations
        assert len(recommendations) >= 5

    def test_health_grading(self, tmp_path):
        """Test health grade assignment."""
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)

        # Perfect context
        context = {
            "updated_at": now.isoformat(),
            "sessions": [{"session_id": "s1", "status": "active"}],
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        analyzer = HealthAnalyzer(context_dir=tmp_path)
        health = analyzer.assess_context_health()

        # Should get good grade
        assert health.health_grade in ["A+", "A", "B"]


class TestReportGenerator:
    """Test ReportGenerator functionality."""

    def test_initialization(self, tmp_path):
        """Test report generator initialization."""
        ReportGenerator(context_dir=tmp_path)

    def test_generate_session_report(self, tmp_path):
        """Test session report generation."""
        # Setup context
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {
                    "session_id": "session1",
                    "agent_id": "agent1",
                    "role": "frontend",
                    "status": "active",
                    "registered_at": now.isoformat(),
                    "last_heartbeat": now.isoformat(),
                }
            ],
            "shared_knowledge": {"recent_commits": []},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        generator = ReportGenerator(context_dir=tmp_path)
        report = generator.generate_session_report("session1")

        assert "session_id" in report
        assert "productivity" in report
        assert "efficiency" in report
        assert "health" in report
        assert "insights" in report
        assert "recommendations" in report
        assert len(report["insights"]) > 0
        assert len(report["recommendations"]) >= 5

    def test_generate_session_report_nonexistent(self, tmp_path):
        """Test report generation for nonexistent session."""
        context_file = tmp_path / "shared_context.json"
        context = {"sessions": []}
        context_file.write_text(json.dumps(context), encoding="utf-8")

        generator = ReportGenerator(context_dir=tmp_path)
        report = generator.generate_session_report("nonexistent")

        assert "error" in report

    def test_generate_multi_session_report(self, tmp_path):
        """Test multi-session report generation."""
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {"session_id": "s1", "last_heartbeat": now.isoformat()},
                {"session_id": "s2", "last_heartbeat": now.isoformat()},
            ],
            "shared_knowledge": {},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        generator = ReportGenerator(context_dir=tmp_path)
        report = generator.generate_multi_session_report()

        assert report["report_type"] == "multi_session"
        assert "coordination" in report
        assert "reuse" in report
        assert "health" in report
        assert "insights" in report
        assert "recommendations" in report

    def test_generate_trend_report(self, tmp_path):
        """Test trend report generation."""
        context_file = tmp_path / "shared_context.json"
        context = {"sessions": [], "shared_knowledge": {}, "context_versions": []}
        context_file.write_text(json.dumps(context), encoding="utf-8")

        generator = ReportGenerator(context_dir=tmp_path)
        report = generator.generate_trend_report(days=7)

        assert report["report_type"] == "trend"
        assert report["period_days"] == 7
        assert "current_snapshot" in report


class TestContextAnalytics:
    """Test ContextAnalytics main interface."""

    def test_initialization(self, tmp_path):
        """Test analytics initialization."""
        ContextAnalytics(context_dir=tmp_path)

    def test_analyze_session(self, tmp_path):
        """Test session analysis."""
        # Setup context
        context_file = tmp_path / "shared_context.json"
        now = datetime.now(timezone.utc)
        context = {
            "sessions": [
                {
                    "session_id": "session1",
                    "agent_id": "agent1",
                    "role": "frontend",
                    "status": "active",
                    "registered_at": now.isoformat(),
                    "last_heartbeat": now.isoformat(),
                }
            ],
            "shared_knowledge": {},
            "context_versions": [],
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")

        analytics = ContextAnalytics(context_dir=tmp_path)
        report = analytics.analyze_session("session1")

        assert "session_id" in report
        assert report["session_id"] == "session1"

        # Check report was saved
        analytics_dir = tmp_path / "analytics"
        assert analytics_dir.exists()
        report_files = list(analytics_dir.glob("session_session1_*.json"))
        assert len(report_files) == 1

    def test_analyze_multi_session(self, tmp_path):
        """Test multi-session analysis."""
        context_file = tmp_path / "shared_context.json"
        context = {"sessions": [], "shared_knowledge": {}, "context_versions": []}
        context_file.write_text(json.dumps(context), encoding="utf-8")

        analytics = ContextAnalytics(context_dir=tmp_path)
        report = analytics.analyze_multi_session()

        assert report["report_type"] == "multi_session"

        # Check report was saved
        analytics_dir = tmp_path / "analytics"
        report_files = list(analytics_dir.glob("multi_session_*.json"))
        assert len(report_files) == 1

    def test_analyze_trends(self, tmp_path):
        """Test trend analysis."""
        context_file = tmp_path / "shared_context.json"
        context = {"sessions": [], "shared_knowledge": {}, "context_versions": []}
        context_file.write_text(json.dumps(context), encoding="utf-8")

        analytics = ContextAnalytics(context_dir=tmp_path)
        report = analytics.analyze_trends(days=7)

        assert report["report_type"] == "trend"
        assert report["period_days"] == 7

        # Check report was saved
        analytics_dir = tmp_path / "analytics"
        report_files = list(analytics_dir.glob("trend_7days_*.json"))
        assert len(report_files) == 1
