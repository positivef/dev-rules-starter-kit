"""Session Metrics Engine - Real-time performance metrics collection.

Features:
- Real-time metrics collection (<1s latency)
- Health score calculation (0-100)
- Anomaly detection
- Trend analysis

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P10: Windows encoding (no emojis)
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass
import statistics
import psutil


@dataclass
class SessionMetrics:
    """Real-time session metrics."""

    timestamp: datetime
    session_id: str
    health_score: float  # 0-100
    operation_latency_ms: float
    active_sessions: int
    error_rate: float  # errors per minute
    cpu_percent: float
    memory_mb: float


class MetricsCollector:
    """Collect real-time session metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.process = psutil.Process()

    def collect_metrics(self, session_id: str) -> SessionMetrics:
        """Collect current metrics snapshot.

        Args:
            session_id: Session identifier

        Returns:
            SessionMetrics object with current values
        """
        # Collect system metrics
        cpu_percent = self.process.cpu_percent(interval=0.1)
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB

        # Create metrics data
        metrics_data = {
            "operation_latency_ms": 100.0,  # Default, should be measured
            "error_rate": 0.0,  # Default, should be tracked
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
        }

        # Calculate health score
        health_score = self.calculate_health_score(metrics_data)

        return SessionMetrics(
            timestamp=datetime.now(timezone.utc),
            session_id=session_id,
            health_score=health_score,
            operation_latency_ms=metrics_data["operation_latency_ms"],
            active_sessions=1,  # Simplified
            error_rate=metrics_data["error_rate"],
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
        )

    def calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate 0-100 health score based on metrics.

        Args:
            metrics: Dictionary with metric values

        Returns:
            Health score from 0 (critical) to 100 (excellent)

        Scoring:
        - Latency: <100ms=25pts, <500ms=20pts, <1000ms=15pts, >1000ms=0-10pts
        - Error rate: 0=25pts, <1=20pts, <5=10pts, >5=0-5pts
        - CPU: <50%=25pts, <70%=20pts, <90%=10pts, >90%=0-5pts
        - Memory: <500MB=25pts, <1GB=20pts, <2GB=10pts, >2GB=0-5pts
        """
        score = 0.0

        # Latency score (0-25 points)
        latency = metrics.get("operation_latency_ms", 1000.0)
        if latency < 100:
            score += 25
        elif latency < 500:
            score += 20
        elif latency < 1000:
            score += 15
        else:
            score += max(0, 10 - (latency / 1000) * 5)

        # Error rate score (0-25 points)
        error_rate = metrics.get("error_rate", 0.0)
        if error_rate == 0:
            score += 25
        elif error_rate < 1:
            score += 20
        elif error_rate < 5:
            score += 10
        else:
            score += max(0, 5 - error_rate)

        # CPU score (0-25 points)
        cpu = metrics.get("cpu_percent", 50.0)
        if cpu < 50:
            score += 25
        elif cpu < 70:
            score += 20
        elif cpu < 90:
            score += 10
        else:
            score += max(0, 5 - (cpu - 90) / 2)

        # Memory score (0-25 points)
        memory_mb = metrics.get("memory_mb", 500.0)
        if memory_mb < 500:
            score += 25
        elif memory_mb < 1000:
            score += 20
        elif memory_mb < 2000:
            score += 10
        else:
            score += max(0, 5 - (memory_mb - 2000) / 500)

        return min(100.0, max(0.0, score))

    def detect_anomalies(self, metrics: SessionMetrics) -> List[str]:
        """Detect anomalous patterns in metrics.

        Args:
            metrics: Session metrics to analyze

        Returns:
            List of anomaly descriptions (empty if none)

        Anomalies:
        - High latency (>1000ms)
        - High error rate (>5/min)
        - High CPU (>90%)
        - High memory (>2GB)
        - Low health score (<50)
        """
        anomalies = []

        # High latency
        if metrics.operation_latency_ms > 1000:
            anomalies.append(f"High latency: {metrics.operation_latency_ms:.0f}ms (threshold: 1000ms)")

        # High error rate
        if metrics.error_rate > 5.0:
            anomalies.append(f"High error rate: {metrics.error_rate:.1f}/min (threshold: 5/min)")

        # High CPU
        if metrics.cpu_percent > 90.0:
            anomalies.append(f"High CPU usage: {metrics.cpu_percent:.1f}% (threshold: 90%)")

        # High memory
        if metrics.memory_mb > 2000.0:
            anomalies.append(f"High memory usage: {metrics.memory_mb:.0f}MB (threshold: 2000MB)")

        # Low health score
        if metrics.health_score < 50.0:
            anomalies.append(f"Low health score: {metrics.health_score:.1f} (threshold: 50)")

        return anomalies


class MetricsAggregator:
    """Aggregate metrics over time periods."""

    def aggregate_by_period(self, metrics: List[SessionMetrics], period_min: int) -> Dict[str, Any]:
        """Aggregate metrics by time period.

        Args:
            metrics: List of metrics to aggregate
            period_min: Period in minutes (currently unused, aggregates all)

        Returns:
            Dictionary with aggregated values
        """
        if not metrics:
            return {}

        health_scores = [m.health_score for m in metrics]
        latencies = [m.operation_latency_ms for m in metrics]
        error_rates = [m.error_rate for m in metrics]

        return {
            "avg_health_score": statistics.mean(health_scores),
            "avg_latency_ms": statistics.mean(latencies),
            "total_errors": sum(error_rates) * period_min,
            "health_scores": health_scores,  # For trend calculation
            "min_health_score": min(health_scores),
            "max_health_score": max(health_scores),
        }

    def calculate_trends(self, aggregated: Dict[str, Any]) -> str:
        """Calculate trend: up/down/stable.

        Args:
            aggregated: Aggregated metrics dictionary

        Returns:
            Trend direction: "up", "down", or "stable"

        Algorithm:
        - Compare first half vs second half of health scores
        - If difference > 5: "up" or "down"
        - Otherwise: "stable"
        """
        health_scores = aggregated.get("health_scores", [])

        if len(health_scores) < 2:
            return "stable"

        # Split into first half and second half
        mid = len(health_scores) // 2
        first_half_avg = statistics.mean(health_scores[:mid])
        second_half_avg = statistics.mean(health_scores[mid:])

        diff = second_half_avg - first_half_avg

        if diff > 5.0:
            return "up"
        elif diff < -5.0:
            return "down"
        else:
            return "stable"
