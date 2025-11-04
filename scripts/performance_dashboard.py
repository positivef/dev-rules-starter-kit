#!/usr/bin/env python3
"""PerformanceDashboard - Real-time Performance Metrics and Trend Analysis

Tier 3 P3-2 implementation for performance monitoring and optimization.

Features:
1. Real-time metrics collection (CPU, memory, disk, network, DB, API)
2. Performance profiling (function-level timing, hot paths, memory)
3. Trend analysis (time series, degradation detection, anomalies)
4. Comparison & benchmarking (version/environment comparisons)
5. Alerting & recommendations (threshold violations, optimization suggestions)

Usage:
    from performance_dashboard import PerformanceDashboard

    dashboard = PerformanceDashboard()

    # Collect real-time metrics
    metrics = dashboard.collect_metrics()

    # Profile function execution
    with dashboard.profile_context("my_function"):
        expensive_operation()

    # Analyze trends
    trend = dashboard.analyze_trends("cpu_percent", timerange="7d")

    # Compare performance
    comparison = dashboard.compare_performance("v1.0", "v2.0")

    # Get recommendations
    recommendations = dashboard.generate_recommendations()
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types"""

    CPU = "cpu_percent"
    MEMORY = "memory_percent"
    DISK = "disk_percent"
    NETWORK_SENT = "network_sent_bytes"
    NETWORK_RECV = "network_recv_bytes"
    RESPONSE_TIME = "response_time_ms"
    QUERY_TIME = "query_time_ms"
    TASK_TIME = "task_time_ms"
    CACHE_HIT_RATE = "cache_hit_rate"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MetricSnapshot:
    """Single metric snapshot at a point in time"""

    timestamp: str
    metric_type: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileResult:
    """Function profiling result"""

    function_name: str
    execution_time_ms: float
    memory_delta_mb: float
    start_time: str
    end_time: str
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""

    metric_type: str
    timerange: str
    data_points: List[Dict[str, Any]]
    avg_value: float
    min_value: float
    max_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    degradation_detected: bool
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ComparisonReport:
    """Performance comparison report"""

    baseline_id: str
    current_id: str
    timestamp: str
    metrics_comparison: Dict[str, Dict[str, float]]
    improvements: List[str] = field(default_factory=list)
    regressions: List[str] = field(default_factory=list)
    overall_change_percent: float = 0.0


@dataclass
class PerformanceAlert:
    """Performance threshold alert"""

    timestamp: str
    metric_type: str
    current_value: float
    threshold: float
    severity: str
    message: str
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Performance optimization recommendation"""

    category: str  # "cpu", "memory", "disk", "network", "code"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    estimated_impact: str
    action_items: List[str] = field(default_factory=list)


class PerformanceDashboard:
    """Performance monitoring and analysis system"""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize PerformanceDashboard

        Args:
            data_dir: Directory for storing performance data
        """
        self.data_dir = data_dir or Path("RUNS/performance_dashboard")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.metrics: List[MetricSnapshot] = []
        self.profiles: List[ProfileResult] = []
        self.trends: Dict[str, TrendAnalysis] = {}
        self.alerts: List[PerformanceAlert] = []
        self.comparisons: List[ComparisonReport] = []

        # Thresholds (configurable)
        self.thresholds = {
            MetricType.CPU: 80.0,  # 80% CPU
            MetricType.MEMORY: 85.0,  # 85% memory
            MetricType.DISK: 90.0,  # 90% disk
            MetricType.RESPONSE_TIME: 1000.0,  # 1 second
            MetricType.QUERY_TIME: 500.0,  # 500ms
            MetricType.TASK_TIME: 5000.0,  # 5 seconds
            MetricType.CACHE_HIT_RATE: 70.0,  # 70% hit rate (minimum)
        }

        self._load_data()
        logger.info("[DASHBOARD] PerformanceDashboard initialized")

    def _load_data(self):
        """Load existing performance data"""
        metrics_file = self.data_dir / "metrics.json"
        profiles_file = self.data_dir / "profiles.json"
        alerts_file = self.data_dir / "alerts.json"

        if metrics_file.exists():
            with open(metrics_file, encoding="utf-8") as f:
                data = json.load(f)
                self.metrics = [MetricSnapshot(**m) for m in data]

        if profiles_file.exists():
            with open(profiles_file, encoding="utf-8") as f:
                data = json.load(f)
                self.profiles = [ProfileResult(**p) for p in data]

        if alerts_file.exists():
            with open(alerts_file, encoding="utf-8") as f:
                data = json.load(f)
                self.alerts = [PerformanceAlert(**a) for a in data]

    def _save_data(self):
        """Save performance data to disk"""
        # Save metrics
        with open(self.data_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump([vars(m) for m in self.metrics], f, indent=2)

        # Save profiles
        with open(self.data_dir / "profiles.json", "w", encoding="utf-8") as f:
            json.dump([vars(p) for p in self.profiles], f, indent=2)

        # Save alerts
        with open(self.data_dir / "alerts.json", "w", encoding="utf-8") as f:
            json.dump([vars(a) for a in self.alerts], f, indent=2)

    def collect_metrics(self) -> Dict[str, float]:
        """Collect real-time system metrics

        Returns:
            Dictionary of current metric values
        """
        metrics = {}
        timestamp = datetime.now().isoformat()

        if psutil:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics[MetricType.CPU] = cpu_percent
            self.metrics.append(MetricSnapshot(timestamp=timestamp, metric_type=MetricType.CPU, value=cpu_percent))

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            metrics[MetricType.MEMORY] = memory_percent
            self.metrics.append(
                MetricSnapshot(
                    timestamp=timestamp,
                    metric_type=MetricType.MEMORY,
                    value=memory_percent,
                    metadata={"available_mb": memory.available / (1024 * 1024)},
                )
            )

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            metrics[MetricType.DISK] = disk_percent
            self.metrics.append(
                MetricSnapshot(
                    timestamp=timestamp,
                    metric_type=MetricType.DISK,
                    value=disk_percent,
                    metadata={"free_gb": disk.free / (1024**3)},
                )
            )

            # Network metrics
            net = psutil.net_io_counters()
            metrics[MetricType.NETWORK_SENT] = net.bytes_sent
            metrics[MetricType.NETWORK_RECV] = net.bytes_recv
            self.metrics.append(
                MetricSnapshot(timestamp=timestamp, metric_type=MetricType.NETWORK_SENT, value=net.bytes_sent)
            )
            self.metrics.append(
                MetricSnapshot(timestamp=timestamp, metric_type=MetricType.NETWORK_RECV, value=net.bytes_recv)
            )

            # Check thresholds and create alerts
            self._check_thresholds(metrics)

        self._save_data()
        logger.info(f"[METRICS] Collected {len(metrics)} metrics")
        return metrics

    def _check_thresholds(self, metrics: Dict[str, float]):
        """Check if metrics exceed thresholds and create alerts"""
        for metric_type, value in metrics.items():
            if metric_type in self.thresholds:
                threshold = self.thresholds[metric_type]

                # For cache hit rate, alert if BELOW threshold
                if metric_type == MetricType.CACHE_HIT_RATE:
                    if value < threshold:
                        self._create_alert(metric_type, value, threshold, AlertSeverity.WARNING)
                # For other metrics, alert if ABOVE threshold
                elif value > threshold:
                    severity = AlertSeverity.CRITICAL if value > threshold * 1.1 else AlertSeverity.WARNING
                    self._create_alert(metric_type, value, threshold, severity)

    def _create_alert(self, metric_type: str, value: float, threshold: float, severity: str):
        """Create performance alert"""
        timestamp = datetime.now().isoformat()
        message = f"{metric_type} at {value:.1f} exceeds threshold {threshold:.1f}"

        recommendations = []
        if metric_type == MetricType.CPU:
            recommendations = ["Optimize CPU-intensive operations", "Consider horizontal scaling"]
        elif metric_type == MetricType.MEMORY:
            recommendations = ["Check for memory leaks", "Optimize data structures", "Increase memory limit"]
        elif metric_type == MetricType.DISK:
            recommendations = ["Clean up old files", "Archive logs", "Expand disk capacity"]

        alert = PerformanceAlert(
            timestamp=timestamp,
            metric_type=metric_type,
            current_value=value,
            threshold=threshold,
            severity=severity,
            message=message,
            recommendations=recommendations,
        )

        self.alerts.append(alert)
        logger.warning(f"[ALERT] {severity.upper()} - {message}")

    def profile_context(self, function_name: str):
        """Context manager for profiling code execution

        Usage:
            with dashboard.profile_context("my_function"):
                expensive_operation()
        """
        return _ProfileContext(self, function_name)

    def record_profile(self, result: ProfileResult):
        """Record profiling result"""
        self.profiles.append(result)
        self._save_data()

        if result.success:
            logger.info(
                f"[PROFILE] {result.function_name}: {result.execution_time_ms:.2f}ms, "
                f"memory delta: {result.memory_delta_mb:.2f}MB"
            )
        else:
            logger.error(f"[PROFILE] {result.function_name} failed: {result.error}")

    def analyze_trends(self, metric_type: str, timerange: str = "7d") -> TrendAnalysis:
        """Analyze performance trends over time

        Args:
            metric_type: Type of metric to analyze
            timerange: Time range (e.g., "7d", "24h", "30d")

        Returns:
            TrendAnalysis with insights
        """
        # Parse timerange
        try:
            if timerange.endswith("d"):
                days = int(timerange[:-1])
                cutoff = datetime.now() - timedelta(days=days)
            elif timerange.endswith("h"):
                hours = int(timerange[:-1])
                cutoff = datetime.now() - timedelta(hours=hours)
            else:
                cutoff = datetime.now() - timedelta(days=7)  # Default 7 days
        except (ValueError, OverflowError):
            # Invalid format, use default 7 days
            cutoff = datetime.now() - timedelta(days=7)

        # Filter metrics
        relevant_metrics = [
            m for m in self.metrics if m.metric_type == metric_type and datetime.fromisoformat(m.timestamp) >= cutoff
        ]

        if not relevant_metrics:
            return TrendAnalysis(
                metric_type=metric_type,
                timerange=timerange,
                data_points=[],
                avg_value=0.0,
                min_value=0.0,
                max_value=0.0,
                trend_direction="stable",
                degradation_detected=False,
            )

        # Calculate statistics
        values = [m.value for m in relevant_metrics]
        avg_value = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)

        # Detect trend direction (simple moving average comparison)
        if len(values) >= 10:
            first_half_avg = sum(values[: len(values) // 2]) / (len(values) // 2)
            second_half_avg = sum(values[len(values) // 2 :]) / (len(values) - len(values) // 2)

            if second_half_avg > first_half_avg * 1.1:
                trend_direction = "increasing"
                degradation_detected = True
            elif second_half_avg < first_half_avg * 0.9:
                trend_direction = "decreasing"
                degradation_detected = False
            else:
                trend_direction = "stable"
                degradation_detected = False
        else:
            trend_direction = "stable"
            degradation_detected = False

        # Detect anomalies (simple threshold: >2 std deviations)
        anomalies = []
        if len(values) >= 3:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance**0.5

            for m in relevant_metrics:
                if abs(m.value - mean) > 2 * std_dev:
                    anomalies.append({"timestamp": m.timestamp, "value": m.value, "deviation": abs(m.value - mean)})

        # Generate recommendations
        recommendations = []
        if degradation_detected:
            recommendations.append(f"Performance degradation detected in {metric_type}")
            recommendations.append("Investigate recent code changes or increased load")
        if anomalies:
            recommendations.append(f"Found {len(anomalies)} anomalies - investigate unusual spikes")

        data_points = [{"timestamp": m.timestamp, "value": m.value} for m in relevant_metrics]

        analysis = TrendAnalysis(
            metric_type=metric_type,
            timerange=timerange,
            data_points=data_points,
            avg_value=avg_value,
            min_value=min_value,
            max_value=max_value,
            trend_direction=trend_direction,
            degradation_detected=degradation_detected,
            anomalies=anomalies,
            recommendations=recommendations,
        )

        self.trends[f"{metric_type}_{timerange}"] = analysis
        logger.info(f"[TREND] {metric_type} ({timerange}): {trend_direction}, avg={avg_value:.2f}")
        return analysis

    def compare_performance(self, baseline_id: str, current_id: str) -> ComparisonReport:
        """Compare performance between two versions/environments

        Args:
            baseline_id: Baseline version/environment ID
            current_id: Current version/environment ID

        Returns:
            ComparisonReport with detailed comparison
        """
        # For now, use simple mock comparison based on recent vs older metrics
        # In production, would use tagged metrics with version/environment labels

        timestamp = datetime.now().isoformat()
        metrics_comparison = {}
        improvements = []
        regressions = []

        # Simple comparison: last 10 metrics vs previous 10 metrics for each type
        metric_types = [MetricType.CPU, MetricType.MEMORY, MetricType.RESPONSE_TIME]

        for metric_type in metric_types:
            type_metrics = [m for m in self.metrics if m.metric_type == metric_type]

            if len(type_metrics) >= 20:
                baseline_values = [m.value for m in type_metrics[-20:-10]]
                current_values = [m.value for m in type_metrics[-10:]]

                baseline_avg = sum(baseline_values) / len(baseline_values)
                current_avg = sum(current_values) / len(current_values)
                change_percent = ((current_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0

                metrics_comparison[metric_type] = {
                    "baseline": baseline_avg,
                    "current": current_avg,
                    "change_percent": change_percent,
                }

                if change_percent < -5:  # 5% improvement
                    improvements.append(f"{metric_type}: {abs(change_percent):.1f}% improvement")
                elif change_percent > 5:  # 5% regression
                    regressions.append(f"{metric_type}: {change_percent:.1f}% regression")

        overall_change_percent = (
            sum(m["change_percent"] for m in metrics_comparison.values()) / len(metrics_comparison)
            if metrics_comparison
            else 0.0
        )

        report = ComparisonReport(
            baseline_id=baseline_id,
            current_id=current_id,
            timestamp=timestamp,
            metrics_comparison=metrics_comparison,
            improvements=improvements,
            regressions=regressions,
            overall_change_percent=overall_change_percent,
        )

        self.comparisons.append(report)
        logger.info(
            f"[COMPARISON] {baseline_id} vs {current_id}: "
            f"{len(improvements)} improvements, {len(regressions)} regressions"
        )
        return report

    def generate_recommendations(self) -> List[Recommendation]:
        """Generate performance optimization recommendations

        Returns:
            List of prioritized recommendations
        """
        recommendations = []

        # Analyze recent alerts
        recent_alerts = [
            a for a in self.alerts if datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(hours=24)
        ]

        if recent_alerts:
            # Group by metric type
            alert_groups = {}
            for alert in recent_alerts:
                alert_groups.setdefault(alert.metric_type, []).append(alert)

            # CPU recommendations
            if MetricType.CPU in alert_groups:
                count = len(alert_groups[MetricType.CPU])
                recommendations.append(
                    Recommendation(
                        category="cpu",
                        priority="high" if count > 3 else "medium",
                        title="CPU Usage Optimization",
                        description=f"CPU usage exceeded threshold {count} times in the last 24 hours",
                        estimated_impact="15-25% CPU reduction",
                        action_items=[
                            "Profile CPU-intensive functions",
                            "Consider caching expensive computations",
                            "Review algorithmic complexity",
                            "Enable multiprocessing for parallel tasks",
                        ],
                    )
                )

            # Memory recommendations
            if MetricType.MEMORY in alert_groups:
                count = len(alert_groups[MetricType.MEMORY])
                recommendations.append(
                    Recommendation(
                        category="memory",
                        priority="high" if count > 3 else "medium",
                        title="Memory Usage Optimization",
                        description=f"Memory usage exceeded threshold {count} times in the last 24 hours",
                        estimated_impact="20-30% memory reduction",
                        action_items=[
                            "Check for memory leaks",
                            "Optimize data structure sizes",
                            "Implement pagination for large datasets",
                            "Use generators instead of lists where possible",
                        ],
                    )
                )

        # Analyze profiling results for hot paths
        if self.profiles:
            # Find slowest functions
            sorted_profiles = sorted(self.profiles, key=lambda p: p.execution_time_ms, reverse=True)
            if sorted_profiles[0].execution_time_ms > 1000:  # >1 second
                recommendations.append(
                    Recommendation(
                        category="code",
                        priority="high",
                        title="Optimize Hot Path Functions",
                        description=f"Function '{sorted_profiles[0].function_name}' takes "
                        f"{sorted_profiles[0].execution_time_ms:.0f}ms",
                        estimated_impact="30-50% response time reduction",
                        action_items=[
                            f"Profile and optimize {sorted_profiles[0].function_name}",
                            "Consider async/await for I/O operations",
                            "Implement caching strategy",
                            "Break down into smaller functions",
                        ],
                    )
                )

        logger.info(f"[RECOMMENDATIONS] Generated {len(recommendations)} optimization recommendations")
        return recommendations


class _ProfileContext:
    """Internal context manager for profiling"""

    def __init__(self, dashboard: PerformanceDashboard, function_name: str):
        self.dashboard = dashboard
        self.function_name = function_name
        self.start_time = None
        self.start_memory = None

    def __enter__(self):
        self.start_time = time.time()
        if psutil:
            process = psutil.Process()
            self.start_memory = process.memory_info().rss / (1024 * 1024)  # MB
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        execution_time_ms = (end_time - self.start_time) * 1000

        memory_delta_mb = 0.0
        if psutil:
            process = psutil.Process()
            end_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_delta_mb = end_memory - self.start_memory

        success = exc_type is None
        error = str(exc_val) if exc_val else None

        result = ProfileResult(
            function_name=self.function_name,
            execution_time_ms=execution_time_ms,
            memory_delta_mb=memory_delta_mb,
            start_time=datetime.fromtimestamp(self.start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            success=success,
            error=error,
        )

        self.dashboard.record_profile(result)
        return False  # Don't suppress exceptions
