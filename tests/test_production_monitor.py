#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for ProductionMonitor

Tests:
- Exception tracking and ID generation
- Alert routing by severity
- SLA monitoring and violation detection
- Root cause analysis
- Dashboard data generation
- Exception resolution
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scripts.production_monitor import (
    AlertChannel,
    ExceptionStatus,
    ProductionMonitor,
    SLAReport,
    SLAThreshold,
)


@pytest.fixture
def temp_monitor_dir():
    """Create temporary directory for monitor data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def monitor(temp_monitor_dir):
    """Create ProductionMonitor instance"""
    return ProductionMonitor(data_dir=temp_monitor_dir)


@pytest.fixture
def sample_exception():
    """Create sample exception"""
    try:
        raise ValueError("Test error message")
    except ValueError as e:
        return e


class TestExceptionTracking:
    """Test exception tracking functionality"""

    def test_track_new_exception(self, monitor, sample_exception):
        """Test tracking a new exception"""
        exc_id = monitor.track_exception(exc=sample_exception, context={"user_id": "123"}, severity="high")

        assert exc_id in monitor.exceptions
        record = monitor.exceptions[exc_id]
        assert record.exception_type == "ValueError"
        assert record.message == "Test error message"
        assert record.severity == "high"
        assert record.status == ExceptionStatus.NEW.value
        assert record.occurrence_count == 1
        assert record.context == {"user_id": "123"}

    def test_track_duplicate_exception(self, monitor, sample_exception):
        """Test tracking the same exception multiple times"""
        exc_id1 = monitor.track_exception(exc=sample_exception, severity="medium")
        exc_id2 = monitor.track_exception(exc=sample_exception, severity="medium")

        assert exc_id1 == exc_id2  # Same ID for same exception
        assert monitor.exceptions[exc_id1].occurrence_count == 2

    def test_exception_id_generation(self, monitor):
        """Test exception ID generation is consistent for same error"""
        # Same exception tracked twice should update count, not create new
        try:
            raise KeyError("missing key")
        except KeyError as e:
            exc_id1 = monitor.track_exception(e)
            # Track again - should be same ID
            exc_id2 = monitor.track_exception(e)

        assert exc_id1 == exc_id2  # Same exception instance = same ID
        assert monitor.exceptions[exc_id1].occurrence_count == 2

    def test_different_exceptions_different_ids(self, monitor):
        """Test different exceptions get different IDs"""
        try:
            raise ValueError("value error")
        except ValueError as e:
            exc_id1 = monitor.track_exception(e)

        try:
            raise TypeError("type error")
        except TypeError as e:
            exc_id2 = monitor.track_exception(e)

        assert exc_id1 != exc_id2  # Different exception types = different IDs

    def test_exception_persistence(self, temp_monitor_dir, sample_exception):
        """Test exceptions are persisted to disk"""
        monitor1 = ProductionMonitor(data_dir=temp_monitor_dir)
        exc_id = monitor1.track_exception(exc=sample_exception)

        # Create new monitor instance (loads from disk)
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert exc_id in monitor2.exceptions
        assert monitor2.exceptions[exc_id].exception_type == "ValueError"


class TestAlertRouting:
    """Test alert routing functionality"""

    def test_route_critical_alert(self, monitor, sample_exception):
        """Test critical alert routing"""
        exc_id = monitor.track_exception(exc=sample_exception, severity="critical")

        # Alert should be created automatically
        assert len(monitor.alerts) == 1
        alert = monitor.alerts[0]
        assert alert["severity"] == "critical"
        assert alert["exception_id"] == exc_id
        assert AlertChannel.PAGERDUTY.value in alert["channels"]
        assert AlertChannel.SMS.value in alert["channels"]

    def test_route_high_alert(self, monitor, sample_exception):
        """Test high severity alert routing"""
        monitor.track_exception(exc=sample_exception, severity="high")

        alert = monitor.alerts[0]
        assert alert["severity"] == "high"
        assert AlertChannel.SLACK.value in alert["channels"]
        assert AlertChannel.EMAIL.value in alert["channels"]

    def test_route_medium_alert(self, monitor, sample_exception):
        """Test medium severity alert routing"""
        monitor.track_exception(exc=sample_exception, severity="medium")

        alert = monitor.alerts[0]
        assert alert["severity"] == "medium"
        assert AlertChannel.SLACK.value in alert["channels"]

    def test_route_low_alert(self, monitor, sample_exception):
        """Test low severity alert routing"""
        monitor.track_exception(exc=sample_exception, severity="low")

        alert = monitor.alerts[0]
        assert alert["severity"] == "low"
        assert AlertChannel.EMAIL.value in alert["channels"]

    def test_custom_alert_channels(self, monitor, sample_exception):
        """Test custom alert channel override"""
        exc_id = monitor.track_exception(exc=sample_exception, severity="high")

        # Override default channels
        monitor.route_alert(exc_id, "high", channels=["email"])

        # Should have 2 alerts (1 auto + 1 custom)
        assert len(monitor.alerts) == 2
        custom_alert = monitor.alerts[1]
        assert custom_alert["channels"] == ["email"]

    def test_alert_escalation_timing(self, monitor):
        """Test alert escalation timing"""
        # Create two different exceptions
        try:
            raise ValueError("Critical error")
        except ValueError as e:
            monitor.track_exception(exc=e, severity="critical")

        alert = monitor.alerts[0]
        assert alert["escalate_after_minutes"] == 5  # Critical = 5 min

        try:
            raise TypeError("Medium error")
        except TypeError as e:
            monitor.track_exception(exc=e, severity="medium")

        alert2 = monitor.alerts[1]
        assert alert2["escalate_after_minutes"] == 30  # Medium = 30 min


class TestSLAMonitoring:
    """Test SLA monitoring functionality"""

    def test_sla_healthy(self, monitor):
        """Test SLA monitoring with healthy metrics"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 50,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.1,
            }
        )

        assert report.status == "healthy"
        assert len(report.violations) == 0
        assert isinstance(report.timestamp, str)
        assert isinstance(report.metrics, dict)

    def test_sla_warning_single_violation(self, monitor):
        """Test SLA warning with single violation"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 150,  # Exceeds threshold (100)
                "p95_latency_ms": 400,
                "p99_latency_ms": 900,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5,
            }
        )

        assert report.status == "warning"
        assert len(report.violations) == 1
        assert "P50 latency" in report.violations[0]

    def test_sla_critical_multiple_violations(self, monitor):
        """Test SLA critical with multiple violations"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 200,  # Exceeds
                "p95_latency_ms": 800,  # Exceeds
                "p99_latency_ms": 1500,  # Exceeds
                "uptime_percent": 99.5,  # Below threshold
                "error_rate_percent": 2.0,  # Exceeds
            }
        )

        assert report.status == "critical"
        assert len(report.violations) >= 3

    def test_sla_latency_violations(self, monitor):
        """Test SLA latency threshold violations"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 150,
                "p95_latency_ms": 600,
                "p99_latency_ms": 1200,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5,
            }
        )

        assert any("P50 latency" in v for v in report.violations)
        assert any("P95 latency" in v for v in report.violations)
        assert any("P99 latency" in v for v in report.violations)

    def test_sla_uptime_violation(self, monitor):
        """Test SLA uptime violation"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 50,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 98.0,  # Below 99.9%
                "error_rate_percent": 0.5,
            }
        )

        assert any("Uptime" in v for v in report.violations)

    def test_sla_error_rate_violation(self, monitor):
        """Test SLA error rate violation"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 50,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 99.95,
                "error_rate_percent": 5.0,  # Exceeds 1.0%
            }
        )

        assert any("Error rate" in v for v in report.violations)

    def test_sla_recommendations(self, monitor):
        """Test SLA violation recommendations"""
        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 150,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5,
            }
        )

        assert len(report.recommendations) > 0
        assert any("database" in r.lower() or "api" in r.lower() for r in report.recommendations)

    def test_sla_custom_thresholds(self, temp_monitor_dir):
        """Test SLA monitoring with custom thresholds"""
        custom_thresholds = SLAThreshold(
            p50_latency_ms=50.0,
            p95_latency_ms=200.0,
            p99_latency_ms=500.0,
            uptime_percent=99.99,
            error_rate_percent=0.1,
        )

        monitor = ProductionMonitor(data_dir=temp_monitor_dir, sla_thresholds=custom_thresholds)

        report = monitor.monitor_sla(
            {
                "p50_latency_ms": 60,  # Exceeds custom threshold
                "p95_latency_ms": 150,
                "p99_latency_ms": 400,
                "uptime_percent": 99.95,  # Below custom threshold
                "error_rate_percent": 0.05,
            }
        )

        assert len(report.violations) == 2  # p50 and uptime

    def test_sla_history_persistence(self, temp_monitor_dir):
        """Test SLA history is persisted"""
        monitor1 = ProductionMonitor(data_dir=temp_monitor_dir)
        monitor1.monitor_sla(
            {
                "p50_latency_ms": 50,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5,
            }
        )

        # Load from disk
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert len(monitor2.sla_history) == 1


class TestRootCauseAnalysis:
    """Test root cause analysis functionality"""

    def test_analyze_new_exception(self, monitor, sample_exception):
        """Test root cause analysis for new exception"""
        exc_id = monitor.track_exception(exc=sample_exception)
        analysis = monitor.analyze_root_cause(exc_id)

        assert analysis.exception_id == exc_id
        assert isinstance(analysis.patterns, list)
        assert isinstance(analysis.suggested_fixes, list)
        assert 0 <= analysis.confidence_score <= 1.0

    def test_analyze_high_frequency_exception(self, monitor, sample_exception):
        """Test analysis detects high frequency pattern"""
        # Track exception 15 times
        for _ in range(15):
            exc_id = monitor.track_exception(exc=sample_exception)

        analysis = monitor.analyze_root_cause(exc_id)
        assert any("High frequency" in p for p in analysis.patterns)

    def test_analyze_timeout_exception(self, monitor):
        """Test analysis for timeout exceptions"""
        try:
            raise TimeoutError("Connection timeout after 30s")
        except TimeoutError as e:
            exc_id = monitor.track_exception(e)

        analysis = monitor.analyze_root_cause(exc_id)
        assert any("timeout" in p.lower() for p in analysis.patterns)
        assert any("timeout" in f.lower() for f in analysis.suggested_fixes)

    def test_analyze_connection_exception(self, monitor):
        """Test analysis for connection exceptions"""
        try:
            raise ConnectionError("Failed to connect to database")
        except ConnectionError as e:
            exc_id = monitor.track_exception(e)

        analysis = monitor.analyze_root_cause(exc_id)
        # ConnectionError message contains "connect" - should match pattern
        message_lower = "failed to connect to database".lower()
        assert "connect" in message_lower  # Verify test data
        # Should have pattern detected since message contains "connect"
        assert len(analysis.patterns) > 0, f"Expected patterns but got: {analysis.patterns}"
        # Should have suggested fixes
        assert len(analysis.suggested_fixes) > 0

    def test_analyze_value_error(self, monitor, sample_exception):
        """Test analysis for ValueError"""
        exc_id = monitor.track_exception(exc=sample_exception)
        analysis = monitor.analyze_root_cause(exc_id)

        assert any("validation" in f.lower() for f in analysis.suggested_fixes)

    def test_analyze_key_error(self, monitor):
        """Test analysis for KeyError"""
        try:
            raise KeyError("missing_key")
        except KeyError as e:
            exc_id = monitor.track_exception(e)

        analysis = monitor.analyze_root_cause(exc_id)
        assert any("get()" in f or "existence" in f.lower() for f in analysis.suggested_fixes)

    def test_analyze_similar_cases(self, monitor):
        """Test finding similar resolved cases"""
        # Create and resolve similar exception
        try:
            raise ValueError("Test 1")
        except ValueError as e:
            exc_id1 = monitor.track_exception(e)
            monitor.resolve_exception(exc_id1, "Fixed")

        # Create new similar exception
        try:
            raise ValueError("Test 2")
        except ValueError as e:
            exc_id2 = monitor.track_exception(e)

        analysis = monitor.analyze_root_cause(exc_id2)
        assert exc_id1 in analysis.similar_cases

    def test_analyze_nonexistent_exception(self, monitor):
        """Test analysis fails for nonexistent exception"""
        with pytest.raises(ValueError, match="Exception not found"):
            monitor.analyze_root_cause("nonexistent_id")


class TestDashboardData:
    """Test dashboard data generation"""

    def test_get_dashboard_empty(self, monitor):
        """Test dashboard data with no exceptions"""
        data = monitor.get_dashboard_data()

        assert data.active_exceptions == 0
        assert data.total_exceptions_24h == 0
        assert data.critical_alerts == 0
        assert len(data.top_errors) == 0
        assert len(data.error_trend) == 7  # 7 days

    def test_get_dashboard_with_exceptions(self, monitor):
        """Test dashboard data with exceptions"""
        # Create multiple exceptions
        for i in range(5):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                monitor.track_exception(e, severity="high")

        data = monitor.get_dashboard_data()
        assert data.total_exceptions_24h == 5
        assert len(data.top_errors) == 5

    def test_get_dashboard_active_exceptions(self, monitor):
        """Test dashboard counts active exceptions"""
        try:
            raise ValueError("Active error")
        except ValueError as e:
            exc_id = monitor.track_exception(e)
            monitor.exceptions[exc_id].status = ExceptionStatus.ACTIVE.value

        data = monitor.get_dashboard_data()
        assert data.active_exceptions == 1

    def test_get_dashboard_critical_alerts(self, monitor):
        """Test dashboard counts critical alerts"""
        try:
            raise ValueError("Critical error")
        except ValueError as e:
            monitor.track_exception(e, severity="critical")

        data = monitor.get_dashboard_data()
        assert data.critical_alerts >= 1

    def test_get_dashboard_sla_status(self, monitor):
        """Test dashboard shows SLA status"""
        monitor.monitor_sla(
            {
                "p50_latency_ms": 50,
                "p95_latency_ms": 200,
                "p99_latency_ms": 500,
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5,
            }
        )

        data = monitor.get_dashboard_data()
        assert data.sla_status == "healthy"

    def test_get_dashboard_top_errors_sorted(self, monitor):
        """Test top errors are sorted by occurrence count"""
        # Create exceptions with different frequencies
        for i in range(3):
            try:
                raise ValueError("Frequent error")
            except ValueError as e:
                monitor.track_exception(e)

        try:
            raise TypeError("Rare error")
        except TypeError as e:
            monitor.track_exception(e)

        data = monitor.get_dashboard_data()
        assert data.top_errors[0]["count"] == 3  # Most frequent first
        assert data.top_errors[0]["type"] == "ValueError"

    def test_get_dashboard_error_trend(self, monitor):
        """Test error trend shows 7 days"""
        data = monitor.get_dashboard_data()
        assert len(data.error_trend) == 7
        assert all("date" in day and "count" in day for day in data.error_trend)


class TestExceptionResolution:
    """Test exception resolution"""

    def test_resolve_exception(self, monitor, sample_exception):
        """Test resolving an exception"""
        exc_id = monitor.track_exception(exc=sample_exception)
        monitor.resolve_exception(exc_id, "Fixed by updating timeout")

        exception = monitor.exceptions[exc_id]
        assert exception.status == ExceptionStatus.RESOLVED.value
        assert exception.resolution_notes == "Fixed by updating timeout"
        assert exception.resolved_at is not None

    def test_resolve_nonexistent_exception(self, monitor):
        """Test resolving nonexistent exception fails"""
        with pytest.raises(ValueError, match="Exception not found"):
            monitor.resolve_exception("nonexistent_id", "Notes")

    def test_resolution_persistence(self, temp_monitor_dir, sample_exception):
        """Test resolution is persisted"""
        monitor1 = ProductionMonitor(data_dir=temp_monitor_dir)
        exc_id = monitor1.track_exception(exc=sample_exception)
        monitor1.resolve_exception(exc_id, "Fixed")

        # Load from disk
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        exception = monitor2.exceptions[exc_id]
        assert exception.status == ExceptionStatus.RESOLVED.value
        assert exception.resolution_notes == "Fixed"


class TestDataPersistence:
    """Test data persistence"""

    def test_exceptions_persistence(self, temp_monitor_dir):
        """Test exceptions are saved and loaded"""
        monitor1 = ProductionMonitor(data_dir=temp_monitor_dir)
        try:
            raise ValueError("Test")
        except ValueError as e:
            exc_id = monitor1.track_exception(e)

        # Create new instance
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert exc_id in monitor2.exceptions

    def test_alerts_persistence(self, temp_monitor_dir):
        """Test alerts are saved and loaded"""
        monitor1 = ProductionMonitor(data_dir=temp_monitor_dir)
        try:
            raise ValueError("Test")
        except ValueError as e:
            monitor1.track_exception(e, severity="critical")

        # Create new instance
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert len(monitor2.alerts) > 0

    def test_sla_history_cleanup(self, temp_monitor_dir):
        """Test SLA history keeps only last 30 days"""
        monitor = ProductionMonitor(data_dir=temp_monitor_dir)

        # Add old report
        old_report = SLAReport(
            timestamp=(datetime.now() - timedelta(days=35)).isoformat(),
            metrics={},
            violations=[],
            status="healthy",
        )
        monitor.sla_history.append(old_report)

        # Add recent report
        recent_report = SLAReport(timestamp=datetime.now().isoformat(), metrics={}, violations=[], status="healthy")
        monitor.sla_history.append(recent_report)

        monitor._save_data()

        # Load and check
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert len(monitor2.sla_history) == 1  # Only recent report

    def test_alerts_limit(self, temp_monitor_dir):
        """Test alerts are limited to last 1000"""
        monitor = ProductionMonitor(data_dir=temp_monitor_dir)

        # Add 1100 alerts
        for i in range(1100):
            monitor.alerts.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "exception_id": f"exc_{i}",
                    "severity": "low",
                    "channels": ["email"],
                }
            )

        monitor._save_data()

        # Load and check
        monitor2 = ProductionMonitor(data_dir=temp_monitor_dir)
        assert len(monitor2.alerts) == 1000  # Kept last 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
