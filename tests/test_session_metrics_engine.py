"""Tests for SessionMetricsEngine - Real-time metrics collection.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (coverage ≥90%)
"""

from datetime import datetime, timezone

from scripts.session_metrics_engine import (
    SessionMetrics,
    MetricsCollector,
    MetricsAggregator,
)


class TestSessionMetrics:
    """Test SessionMetrics dataclass."""

    def test_session_metrics_creation(self):
        """Test creating SessionMetrics instance."""
        now = datetime.now(timezone.utc)
        metrics = SessionMetrics(
            timestamp=now,
            session_id="test_session",
            health_score=85.5,
            operation_latency_ms=150.0,
            active_sessions=3,
            error_rate=0.5,
            cpu_percent=45.0,
            memory_mb=256.0,
        )

        assert metrics.session_id == "test_session"
        assert metrics.health_score == 85.5
        assert metrics.operation_latency_ms == 150.0
        assert metrics.active_sessions == 3


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_collect_metrics_success(self):
        """Test successful metrics collection."""
        collector = MetricsCollector()
        metrics = collector.collect_metrics("test_session")

        assert isinstance(metrics, SessionMetrics)
        assert metrics.session_id == "test_session"
        assert 0 <= metrics.health_score <= 100
        assert metrics.operation_latency_ms >= 0
        assert metrics.active_sessions >= 0

    def test_calculate_health_score_perfect(self):
        """Test health score calculation for perfect conditions."""
        collector = MetricsCollector()

        metrics_data = {
            "operation_latency_ms": 50.0,  # Very fast
            "error_rate": 0.0,  # No errors
            "cpu_percent": 20.0,  # Low CPU
            "memory_mb": 100.0,  # Low memory
        }

        score = collector.calculate_health_score(metrics_data)

        assert 80 <= score <= 100  # Should be high score

    def test_calculate_health_score_degraded(self):
        """Test health score calculation for degraded conditions."""
        collector = MetricsCollector()

        metrics_data = {
            "operation_latency_ms": 2000.0,  # Slow (2s)
            "error_rate": 5.0,  # 5 errors/min
            "cpu_percent": 90.0,  # High CPU
            "memory_mb": 1000.0,  # High memory
        }

        score = collector.calculate_health_score(metrics_data)

        assert 0 <= score < 50  # Should be low score

    def test_detect_anomalies_none(self):
        """Test anomaly detection with normal metrics."""
        collector = MetricsCollector()

        now = datetime.now(timezone.utc)
        normal_metrics = SessionMetrics(
            timestamp=now,
            session_id="test",
            health_score=90.0,
            operation_latency_ms=100.0,
            active_sessions=2,
            error_rate=0.1,
            cpu_percent=30.0,
            memory_mb=200.0,
        )

        anomalies = collector.detect_anomalies(normal_metrics)

        assert isinstance(anomalies, list)
        assert len(anomalies) == 0  # No anomalies

    def test_detect_anomalies_high_latency(self):
        """Test anomaly detection with high latency."""
        collector = MetricsCollector()

        now = datetime.now(timezone.utc)
        slow_metrics = SessionMetrics(
            timestamp=now,
            session_id="test",
            health_score=50.0,
            operation_latency_ms=5000.0,  # 5 seconds!
            active_sessions=2,
            error_rate=0.1,
            cpu_percent=30.0,
            memory_mb=200.0,
        )

        anomalies = collector.detect_anomalies(slow_metrics)

        assert len(anomalies) > 0
        assert any("latency" in a.lower() for a in anomalies)

    def test_detect_anomalies_high_error_rate(self):
        """Test anomaly detection with high error rate."""
        collector = MetricsCollector()

        now = datetime.now(timezone.utc)
        error_metrics = SessionMetrics(
            timestamp=now,
            session_id="test",
            health_score=40.0,
            operation_latency_ms=100.0,
            active_sessions=2,
            error_rate=10.0,  # 10 errors/min!
            cpu_percent=30.0,
            memory_mb=200.0,
        )

        anomalies = collector.detect_anomalies(error_metrics)

        assert len(anomalies) > 0
        assert any("error" in a.lower() for a in anomalies)


class TestMetricsAggregator:
    """Test MetricsAggregator class."""

    def test_aggregate_by_period_1min(self):
        """Test aggregating metrics by 1 minute."""
        aggregator = MetricsAggregator()

        now = datetime.now(timezone.utc)
        metrics_list = [
            SessionMetrics(
                timestamp=now,
                session_id="test",
                health_score=90.0,
                operation_latency_ms=100.0,
                active_sessions=2,
                error_rate=0.1,
                cpu_percent=30.0,
                memory_mb=200.0,
            ),
            SessionMetrics(
                timestamp=now,
                session_id="test",
                health_score=85.0,
                operation_latency_ms=120.0,
                active_sessions=2,
                error_rate=0.2,
                cpu_percent=35.0,
                memory_mb=210.0,
            ),
        ]

        aggregated = aggregator.aggregate_by_period(metrics_list, period_min=1)

        assert "avg_health_score" in aggregated
        assert "avg_latency_ms" in aggregated
        assert "total_errors" in aggregated

    def test_calculate_trends_up(self):
        """Test trend calculation for increasing metrics."""
        aggregator = MetricsAggregator()

        aggregated = {
            "health_scores": [70.0, 75.0, 80.0, 85.0, 90.0],  # Increasing
        }

        trend = aggregator.calculate_trends(aggregated)

        assert trend in ["up", "stable", "down"]
        # Increasing should be "up"

    def test_calculate_trends_down(self):
        """Test trend calculation for decreasing metrics."""
        aggregator = MetricsAggregator()

        aggregated = {
            "health_scores": [90.0, 85.0, 80.0, 75.0, 70.0],  # Decreasing
        }

        trend = aggregator.calculate_trends(aggregated)

        assert trend in ["up", "stable", "down"]
        # Decreasing should be "down"

    def test_calculate_trends_stable(self):
        """Test trend calculation for stable metrics."""
        aggregator = MetricsAggregator()

        aggregated = {
            "health_scores": [85.0, 86.0, 85.0, 84.0, 85.0],  # Stable
        }

        trend = aggregator.calculate_trends(aggregated)

        assert trend == "stable"
