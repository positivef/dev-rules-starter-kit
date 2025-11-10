"""Session Predictor - Predictive analytics for crash and performance.

Features:
- Crash probability prediction (0-1 scale)
- Memory leak detection (pattern-based)
- Time to failure estimation
- Performance bottleneck prediction

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P10: Windows encoding (no emojis)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import statistics


@dataclass
class CrashPrediction:
    """Crash prediction result.

    Attributes:
        probability: Crash probability (0-1 scale)
        confidence: Prediction confidence (0-1 scale)
        estimated_time_to_failure_min: Minutes until estimated failure
        reasons: List of contributing factors
    """

    probability: float  # 0-1
    confidence: float  # 0-1
    estimated_time_to_failure_min: Optional[int]
    reasons: List[str]


class CrashPredictor:
    """Predict potential session crashes.

    Uses rule-based prediction with health score trends,
    error rates, and resource usage patterns.
    """

    def __init__(self):
        """Initialize crash predictor."""
        self.thresholds = {
            "critical_health": 30.0,
            "high_error_rate": 5.0,
            "critical_memory": 2000.0,
            "critical_cpu": 90.0,
        }

    def predict_crash_probability(self, metrics_history: List[Dict[str, Any]]) -> float:
        """Predict crash probability based on metrics history.

        Args:
            metrics_history: List of metric dictionaries with keys:
                - health_score: float (0-100)
                - error_rate: float (errors per minute)
                - memory_mb: float (memory usage in MB)

        Returns:
            Crash probability (0-1 scale)

        Algorithm:
            - Analyzes health score trend (declining = risk)
            - Checks error rate escalation
            - Monitors resource exhaustion
            - Combines factors into probability score
        """
        if not metrics_history:
            return 0.0

        # Extract metrics
        health_scores = [m.get("health_score", 100.0) for m in metrics_history]
        error_rates = [m.get("error_rate", 0.0) for m in metrics_history]
        memory_usage = [m.get("memory_mb", 0.0) for m in metrics_history]

        # Calculate risk factors (0-1 scale each)
        risk_factors = []

        # 1. Health score declining trend (30% weight)
        if len(health_scores) >= 3:
            recent_avg = statistics.mean(health_scores[-3:])
            if recent_avg <= self.thresholds["critical_health"]:
                risk_factors.append(0.9)  # Critical health
            elif recent_avg < 50.0:
                risk_factors.append(0.7)  # Low health
            else:
                # Check if declining
                first_half = statistics.mean(health_scores[: len(health_scores) // 2])
                second_half = statistics.mean(health_scores[len(health_scores) // 2 :])
                if second_half < first_half - 20:
                    risk_factors.append(0.6)  # Significant decline
                else:
                    risk_factors.append(0.1)  # Stable/improving
        else:
            risk_factors.append(0.1)

        # 2. Error rate escalation (30% weight)
        recent_errors = error_rates[-3:] if len(error_rates) >= 3 else error_rates
        avg_error_rate = statistics.mean(recent_errors) if recent_errors else 0.0

        if avg_error_rate > self.thresholds["high_error_rate"]:
            risk_factors.append(0.9)  # High error rate
        elif avg_error_rate > 2.0:
            risk_factors.append(0.5)  # Moderate error rate
        else:
            risk_factors.append(0.1)  # Low error rate

        # 3. Memory exhaustion (20% weight)
        recent_memory = memory_usage[-3:] if len(memory_usage) >= 3 else memory_usage
        avg_memory = statistics.mean(recent_memory) if recent_memory else 0.0

        if avg_memory >= self.thresholds["critical_memory"]:
            risk_factors.append(0.9)  # Critical memory
        elif avg_memory >= 1800.0:
            risk_factors.append(0.7)  # High memory
        elif avg_memory >= 1500.0:
            risk_factors.append(0.5)  # Moderate memory
        else:
            risk_factors.append(0.1)  # Normal memory

        # 4. Trend acceleration (20% weight)
        if len(health_scores) >= 5:
            # Check if health is degrading faster
            early = statistics.mean(health_scores[:3])
            late = statistics.mean(health_scores[-3:])
            decline_rate = (early - late) / len(health_scores)

            if decline_rate > 10:
                risk_factors.append(0.8)  # Fast decline
            elif decline_rate > 5:
                risk_factors.append(0.4)  # Moderate decline
            else:
                risk_factors.append(0.1)  # Stable
        else:
            risk_factors.append(0.1)

        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.2]
        probability = sum(r * w for r, w in zip(risk_factors, weights))

        return min(1.0, max(0.0, probability))

    def detect_memory_leak(self, memory_history: List[float]) -> bool:
        """Detect memory leak pattern in history.

        Args:
            memory_history: List of memory usage values (MB)

        Returns:
            True if memory leak detected, False otherwise

        Algorithm:
            - Requires at least 5 data points
            - Calculates linear trend
            - Leak detected if consistent increase >10% over period
        """
        if len(memory_history) < 5:
            return False  # Need at least 5 points

        # Calculate linear trend
        n = len(memory_history)
        x_values = list(range(n))

        # Linear regression (y = mx + b)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(memory_history)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, memory_history))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return False

        slope = numerator / denominator

        # Calculate increase percentage
        total_increase = slope * n
        increase_pct = (total_increase / memory_history[0] * 100) if memory_history[0] > 0 else 0

        # Leak if increasing >10% and consistent
        return increase_pct > 10.0 and slope > 5.0

    def estimate_time_to_failure(self, metrics: Dict[str, Any]) -> Optional[int]:
        """Estimate minutes until potential failure.

        Args:
            metrics: Current metrics dictionary with keys:
                - health_score: float (0-100)
                - error_rate: float (errors/min)
                - memory_mb: float
                - cpu_percent: float

        Returns:
            Estimated minutes until failure, or None if healthy

        Algorithm:
            - Returns None if health score > 50
            - Critical (<20): 1-5 minutes
            - Very Low (20-30): 5-10 minutes
            - Low (30-50): 10-30 minutes
        """
        health_score = metrics.get("health_score", 100.0)
        error_rate = metrics.get("error_rate", 0.0)
        memory_mb = metrics.get("memory_mb", 0.0)
        cpu_percent = metrics.get("cpu_percent", 0.0)

        # Healthy system
        if health_score > 50.0:
            return None

        # Calculate urgency score (0-100)
        urgency = 0.0

        # Health score contribution
        urgency += max(0, 50 - health_score)

        # Error rate contribution
        if error_rate > 10:
            urgency += 30
        elif error_rate > 5:
            urgency += 15

        # Memory contribution
        if memory_mb > 2500:
            urgency += 20
        elif memory_mb > 2000:
            urgency += 10

        # CPU contribution
        if cpu_percent > 95:
            urgency += 20
        elif cpu_percent > 90:
            urgency += 10

        # Map urgency to time estimate
        if urgency > 80:
            return 1  # Critical - 1 minute
        elif urgency > 60:
            return 5  # Very urgent - 5 minutes
        elif urgency > 40:
            return 10  # Urgent - 10 minutes
        elif urgency > 20:
            return 20  # Warning - 20 minutes
        else:
            return 30  # Low priority - 30 minutes


class PerformancePredictor:
    """Predict performance issues and bottlenecks.

    Uses trend analysis and threshold-based prediction
    for operation times and resource bottlenecks.
    """

    def __init__(self):
        """Initialize performance predictor."""
        self.thresholds = {
            "cpu_bottleneck": 90.0,
            "memory_bottleneck": 2000.0,
            "latency_bottleneck": 2000.0,
            "error_bottleneck": 5.0,
        }

    def predict_operation_time(self, operation: str, history: List[float]) -> float:
        """Predict operation duration based on historical data.

        Args:
            operation: Operation name (for future per-operation prediction)
            history: List of past operation times (seconds)

        Returns:
            Predicted operation time in seconds

        Algorithm:
            - No history: returns 1.0 default
            - Calculates moving average (removes outliers)
            - Applies trend adjustment if declining/improving
        """
        if not history:
            return 1.0  # Default estimate

        # Remove outliers (values > 2x median)
        median = statistics.median(history)
        filtered = [h for h in history if h <= median * 2]

        if not filtered:
            filtered = history  # Keep original if all outliers

        # Trend adjustment
        if len(history) >= 5:
            # Compare first half vs second half
            mid = len(history) // 2
            first_half_avg = statistics.mean(history[:mid])
            second_half_avg = statistics.mean(history[mid:])

            # If strong increasing trend, use recent average as base
            if second_half_avg > first_half_avg * 1.5:
                # Strong upward trend - use recent values with trend factor
                base_prediction = statistics.mean(history[-3:]) * 1.15
            elif second_half_avg > first_half_avg:
                # Moderate upward trend
                base_prediction = statistics.mean(filtered) * 1.1
            else:
                # Stable or declining
                base_prediction = statistics.mean(filtered)
        else:
            # Not enough data for trend analysis
            base_prediction = statistics.mean(filtered)

        return round(base_prediction, 2)

    def predict_bottleneck(self, metrics: Dict[str, Any]) -> str:
        """Predict next bottleneck component.

        Args:
            metrics: Current metrics dictionary with keys:
                - cpu_percent: float
                - memory_mb: float
                - operation_latency_ms: float
                - error_rate: float

        Returns:
            Bottleneck component: "cpu", "memory", "latency", "errors", or "none"

        Algorithm:
            - Checks each metric against thresholds
            - Returns most critical bottleneck
            - Priority: CPU > Memory > Latency > Errors
        """
        cpu = metrics.get("cpu_percent", 0.0)
        memory = metrics.get("memory_mb", 0.0)
        latency = metrics.get("operation_latency_ms", 0.0)
        errors = metrics.get("error_rate", 0.0)

        # Check thresholds (priority order)
        if cpu > self.thresholds["cpu_bottleneck"]:
            return "cpu"

        if memory > self.thresholds["memory_bottleneck"]:
            return "memory"

        if latency > self.thresholds["latency_bottleneck"]:
            return "latency"

        if errors > self.thresholds["error_bottleneck"]:
            return "errors"

        return "none"
