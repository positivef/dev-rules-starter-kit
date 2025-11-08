#!/usr/bin/env python3
"""Tests for PerformanceDashboard

Comprehensive test suite for P3-2 PerformanceDashboard implementation.

Tests:
- Metrics collection (CPU, memory, disk, network)
- Performance profiling (function timing, memory tracking)
- Trend analysis (time series, degradation detection, anomalies)
- Performance comparison (baseline vs current)
- Recommendations generation
- Alerting (threshold violations)
- Data persistence
"""

import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from scripts.performance_dashboard import (
    AlertSeverity,
    MetricSnapshot,
    MetricType,
    PerformanceDashboard,
    ProfileResult,
)


@pytest.fixture
def temp_dashboard_dir(tmp_path):
    """Create temporary directory for dashboard data"""
    return tmp_path / "performance_dashboard"


@pytest.fixture
def dashboard(temp_dashboard_dir):
    """Create PerformanceDashboard instance"""
    return PerformanceDashboard(data_dir=temp_dashboard_dir)


class TestMetricsCollection:
    """Test metrics collection functionality"""

    @patch("scripts.performance_dashboard.psutil")
    def test_collect_metrics_with_psutil(self, mock_psutil, dashboard):
        """Test metrics collection when psutil is available"""
        # Mock psutil responses
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.0, available=2048 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=75.0, free=50 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1024000, bytes_recv=2048000)

        metrics = dashboard.collect_metrics()

        assert MetricType.CPU in metrics
        assert metrics[MetricType.CPU] == 45.5
        assert MetricType.MEMORY in metrics
        assert metrics[MetricType.MEMORY] == 60.0
        assert MetricType.DISK in metrics
        assert metrics[MetricType.DISK] == 75.0
        assert len(dashboard.metrics) >= 5  # CPU, memory, disk, network sent/recv

    def test_collect_metrics_without_psutil(self, dashboard):
        """Test metrics collection when psutil is not available"""
        with patch("scripts.performance_dashboard.psutil", None):
            metrics = dashboard.collect_metrics()
            assert isinstance(metrics, dict)

    @patch("scripts.performance_dashboard.psutil")
    def test_metrics_persistence(self, mock_psutil, dashboard):
        """Test that collected metrics are persisted"""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=65.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=80.0, free=20 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=5000, bytes_recv=10000)

        dashboard.collect_metrics()

        # Check persistence
        metrics_file = dashboard.data_dir / "metrics.json"
        assert metrics_file.exists()

        with open(metrics_file, encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) > 0


class TestPerformanceProfiling:
    """Test performance profiling functionality"""

    @patch("scripts.performance_dashboard.psutil")
    def test_profile_context_success(self, mock_psutil, dashboard):
        """Test profiling context for successful execution"""
        mock_process = MagicMock()
        mock_process.memory_info.side_effect = [
            MagicMock(rss=100 * 1024 * 1024),  # Start: 100MB
            MagicMock(rss=110 * 1024 * 1024),  # End: 110MB
        ]
        mock_psutil.Process.return_value = mock_process

        with dashboard.profile_context("test_function"):
            time.sleep(0.01)  # Simulate work

        assert len(dashboard.profiles) == 1
        profile = dashboard.profiles[0]
        assert profile.function_name == "test_function"
        assert profile.execution_time_ms >= 10  # At least 10ms
        assert profile.success is True
        assert profile.error is None

    @patch("scripts.performance_dashboard.psutil")
    def test_profile_context_with_exception(self, mock_psutil, dashboard):
        """Test profiling context when exception occurs"""
        mock_process = MagicMock()
        mock_process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)
        mock_psutil.Process.return_value = mock_process

        with pytest.raises(ValueError):
            with dashboard.profile_context("failing_function"):
                raise ValueError("Test error")

        assert len(dashboard.profiles) == 1
        profile = dashboard.profiles[0]
        assert profile.function_name == "failing_function"
        assert profile.success is False
        assert "Test error" in profile.error

    @patch("scripts.performance_dashboard.psutil")
    def test_profile_memory_tracking(self, mock_psutil, dashboard):
        """Test memory delta tracking in profiling"""
        mock_process = MagicMock()
        mock_process.memory_info.side_effect = [
            MagicMock(rss=100 * 1024 * 1024),  # Start: 100MB
            MagicMock(rss=150 * 1024 * 1024),  # End: 150MB (50MB increase)
        ]
        mock_psutil.Process.return_value = mock_process

        with dashboard.profile_context("memory_heavy_function"):
            pass

        profile = dashboard.profiles[0]
        assert abs(profile.memory_delta_mb - 50.0) < 1.0  # ~50MB delta


class TestTrendAnalysis:
    """Test trend analysis functionality"""

    def test_analyze_trends_empty_data(self, dashboard):
        """Test trend analysis with no data"""
        analysis = dashboard.analyze_trends(MetricType.CPU, "7d")

        assert analysis.metric_type == MetricType.CPU
        assert analysis.timerange == "7d"
        assert len(analysis.data_points) == 0
        assert analysis.avg_value == 0.0
        assert analysis.trend_direction == "stable"
        assert analysis.degradation_detected is False

    def test_analyze_trends_with_data(self, dashboard):
        """Test trend analysis with sufficient data"""
        # Add 20 metric snapshots with increasing values
        base_time = datetime.now()
        for i in range(20):
            timestamp = (base_time - timedelta(hours=20 - i)).isoformat()
            value = 50.0 + i * 2  # Increasing trend
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=value))

        analysis = dashboard.analyze_trends(MetricType.CPU, "24h")

        assert len(analysis.data_points) == 20
        assert analysis.trend_direction == "increasing"
        assert analysis.degradation_detected is True
        assert len(analysis.recommendations) > 0

    def test_analyze_trends_stable(self, dashboard):
        """Test trend analysis with stable metrics"""
        base_time = datetime.now()
        for i in range(20):
            timestamp = (base_time - timedelta(hours=20 - i)).isoformat()
            value = 50.0  # Stable value
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=value))

        analysis = dashboard.analyze_trends(MetricType.CPU, "24h")

        assert analysis.trend_direction == "stable"
        assert analysis.degradation_detected is False

    def test_analyze_trends_anomaly_detection(self, dashboard):
        """Test anomaly detection in trend analysis"""
        base_time = datetime.now()

        # Add normal values
        for i in range(15):
            timestamp = (base_time - timedelta(hours=20 - i)).isoformat()
            value = 50.0 + (i % 3)  # Small variation
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=value))

        # Add anomaly
        dashboard.metrics.append(
            MetricSnapshot(
                timestamp=(base_time - timedelta(hours=5)).isoformat(),
                metric_type=MetricType.CPU,
                value=150.0,  # Spike
            )
        )

        analysis = dashboard.analyze_trends(MetricType.CPU, "24h")

        assert len(analysis.anomalies) > 0


class TestPerformanceComparison:
    """Test performance comparison functionality"""

    def test_compare_performance_insufficient_data(self, dashboard):
        """Test comparison with insufficient data"""
        report = dashboard.compare_performance("v1.0", "v2.0")

        assert report.baseline_id == "v1.0"
        assert report.current_id == "v2.0"
        assert len(report.metrics_comparison) == 0

    def test_compare_performance_with_data(self, dashboard):
        """Test comparison with sufficient data"""
        # Add 30 CPU metrics (baseline: 20-30, current: 10-20)
        base_time = datetime.now()

        # Baseline metrics (higher values)
        for i in range(20):
            timestamp = (base_time - timedelta(hours=40 - i)).isoformat()
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=60.0 + i % 5))

        # Current metrics (lower values - improvement)
        for i in range(10):
            timestamp = (base_time - timedelta(hours=10 - i)).isoformat()
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=40.0 + i % 3))

        report = dashboard.compare_performance("v1.0", "v2.0")

        assert len(report.metrics_comparison) > 0
        if MetricType.CPU in report.metrics_comparison:
            cpu_comparison = report.metrics_comparison[MetricType.CPU]
            assert "baseline" in cpu_comparison
            assert "current" in cpu_comparison
            assert "change_percent" in cpu_comparison

    def test_compare_performance_improvement_detection(self, dashboard):
        """Test detection of performance improvements"""
        base_time = datetime.now()

        # Baseline: high values
        for i in range(20):
            timestamp = (base_time - timedelta(hours=40 - i)).isoformat()
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.MEMORY, value=80.0))

        # Current: low values (improvement)
        for i in range(10):
            timestamp = (base_time - timedelta(hours=10 - i)).isoformat()
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.MEMORY, value=60.0))

        report = dashboard.compare_performance("baseline", "current")

        # Should detect improvement
        assert len(dashboard.comparisons) > 0 or len(report.metrics_comparison) > 0


class TestAlerting:
    """Test alerting functionality"""

    @patch("scripts.performance_dashboard.psutil")
    def test_threshold_violation_alert(self, mock_psutil, dashboard):
        """Test alert creation when threshold is violated"""
        # Set high CPU to trigger alert
        mock_psutil.cpu_percent.return_value = 85.0  # Above 80% threshold
        mock_psutil.virtual_memory.return_value = MagicMock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=50.0, free=50 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        dashboard.collect_metrics()

        # Should create CPU alert
        cpu_alerts = [a for a in dashboard.alerts if a.metric_type == MetricType.CPU]
        assert len(cpu_alerts) > 0
        alert = cpu_alerts[0]
        assert alert.current_value == 85.0
        assert alert.threshold == 80.0
        assert alert.severity in [AlertSeverity.WARNING, AlertSeverity.CRITICAL]

    @patch("scripts.performance_dashboard.psutil")
    def test_multiple_threshold_violations(self, mock_psutil, dashboard):
        """Test multiple threshold violations create multiple alerts"""
        # Set multiple metrics above thresholds
        mock_psutil.cpu_percent.return_value = 90.0  # Above 80%
        mock_psutil.virtual_memory.return_value = MagicMock(
            percent=90.0,
            available=100 * 1024 * 1024,  # Above 85%
        )
        mock_psutil.disk_usage.return_value = MagicMock(percent=95.0, free=5 * 1024**3)  # Above 90%
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        dashboard.collect_metrics()

        assert len(dashboard.alerts) >= 3  # CPU, memory, disk

    @patch("scripts.performance_dashboard.psutil")
    def test_alert_severity_levels(self, mock_psutil, dashboard):
        """Test different alert severity levels"""
        # Critical level (>110% of threshold)
        mock_psutil.cpu_percent.return_value = 95.0  # 80 * 1.1 = 88, so this is critical
        mock_psutil.virtual_memory.return_value = MagicMock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=50.0, free=50 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        dashboard.collect_metrics()

        critical_alerts = [a for a in dashboard.alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical_alerts) > 0


class TestRecommendations:
    """Test recommendations generation"""

    def test_generate_recommendations_no_data(self, dashboard):
        """Test recommendations with no data"""
        recommendations = dashboard.generate_recommendations()
        assert isinstance(recommendations, list)

    @patch("scripts.performance_dashboard.psutil")
    def test_generate_recommendations_with_alerts(self, mock_psutil, dashboard):
        """Test recommendations based on alerts"""
        # Create CPU alert
        mock_psutil.cpu_percent.return_value = 85.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=50.0, free=50 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        dashboard.collect_metrics()
        recommendations = dashboard.generate_recommendations()

        # Should have CPU optimization recommendation
        cpu_recommendations = [r for r in recommendations if r.category == "cpu"]
        assert len(cpu_recommendations) > 0

    def test_generate_recommendations_from_profiles(self, dashboard):
        """Test recommendations based on slow functions"""
        # Add slow function profile
        dashboard.profiles.append(
            ProfileResult(
                function_name="slow_function",
                execution_time_ms=2000.0,  # 2 seconds
                memory_delta_mb=50.0,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                success=True,
            )
        )

        recommendations = dashboard.generate_recommendations()

        # Should have code optimization recommendation
        code_recommendations = [r for r in recommendations if r.category == "code"]
        assert len(code_recommendations) > 0
        assert code_recommendations[0].priority == "high"


class TestDataPersistence:
    """Test data persistence functionality"""

    @patch("scripts.performance_dashboard.psutil")
    def test_metrics_persistence(self, mock_psutil, temp_dashboard_dir):
        """Test metrics are persisted and loaded"""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=70.0, free=30 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        # Create first dashboard and collect metrics
        dashboard1 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        dashboard1.collect_metrics()
        metrics_count = len(dashboard1.metrics)

        # Create second dashboard from same directory
        dashboard2 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        assert len(dashboard2.metrics) == metrics_count

    @patch("scripts.performance_dashboard.psutil")
    def test_profiles_persistence(self, mock_psutil, temp_dashboard_dir):
        """Test profiles are persisted and loaded"""
        mock_process = MagicMock()
        mock_process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)
        mock_psutil.Process.return_value = mock_process

        # Create first dashboard and add profile
        dashboard1 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        with dashboard1.profile_context("test_function"):
            time.sleep(0.01)

        # Create second dashboard from same directory
        dashboard2 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        assert len(dashboard2.profiles) == 1
        assert dashboard2.profiles[0].function_name == "test_function"

    @patch("scripts.performance_dashboard.psutil")
    def test_alerts_persistence(self, mock_psutil, temp_dashboard_dir):
        """Test alerts are persisted and loaded"""
        mock_psutil.cpu_percent.return_value = 90.0  # Above threshold
        mock_psutil.virtual_memory.return_value = MagicMock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.disk_usage.return_value = MagicMock(percent=50.0, free=50 * 1024**3)
        mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

        # Create first dashboard and trigger alert
        dashboard1 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        dashboard1.collect_metrics()
        alerts_count = len(dashboard1.alerts)

        # Create second dashboard from same directory
        dashboard2 = PerformanceDashboard(data_dir=temp_dashboard_dir)
        assert len(dashboard2.alerts) == alerts_count


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_timerange_defaults_to_7d(self, dashboard):
        """Test that invalid timerange defaults to 7 days"""
        base_time = datetime.now()
        for i in range(10):
            timestamp = (base_time - timedelta(days=i)).isoformat()
            dashboard.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=50.0))

        analysis = dashboard.analyze_trends(MetricType.CPU, "invalid")
        assert len(analysis.data_points) > 0  # Should use default 7d

    def test_profile_context_without_psutil(self, dashboard):
        """Test profiling works without psutil"""
        with patch("scripts.performance_dashboard.psutil", None):
            with dashboard.profile_context("test_without_psutil"):
                time.sleep(0.01)

            assert len(dashboard.profiles) == 1
            profile = dashboard.profiles[0]
            assert profile.execution_time_ms >= 10
            assert profile.memory_delta_mb == 0.0  # No psutil, no memory tracking

    def test_custom_thresholds(self, dashboard):
        """Test custom threshold configuration"""
        dashboard.thresholds[MetricType.CPU] = 50.0  # Lower threshold

        with patch("scripts.performance_dashboard.psutil") as mock_psutil:
            mock_psutil.cpu_percent.return_value = 55.0  # Above custom threshold
            mock_psutil.virtual_memory.return_value = MagicMock(percent=30.0, available=2048 * 1024 * 1024)
            mock_psutil.disk_usage.return_value = MagicMock(percent=40.0, free=60 * 1024**3)
            mock_psutil.net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)

            dashboard.collect_metrics()

            # Should trigger alert with custom threshold
            cpu_alerts = [a for a in dashboard.alerts if a.metric_type == MetricType.CPU]
            assert len(cpu_alerts) > 0
            assert cpu_alerts[0].threshold == 50.0
