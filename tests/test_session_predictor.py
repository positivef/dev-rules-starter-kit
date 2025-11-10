"""Tests for SessionPredictor - Predictive analytics for crash and performance.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (coverage ≥85%)
"""

from scripts.session_predictor import (
    CrashPrediction,
    CrashPredictor,
    PerformancePredictor,
)


class TestCrashPrediction:
    """Test CrashPrediction dataclass."""

    def test_crash_prediction_creation(self):
        """Test creating CrashPrediction instance."""
        prediction = CrashPrediction(
            probability=0.75,
            confidence=0.90,
            estimated_time_to_failure_min=15,
            reasons=["High memory usage", "Error rate spike"],
        )

        assert prediction.probability == 0.75
        assert prediction.confidence == 0.90
        assert prediction.estimated_time_to_failure_min == 15
        assert len(prediction.reasons) == 2


class TestCrashPredictor:
    """Test CrashPredictor class."""

    def test_predict_crash_probability_low(self):
        """Test crash probability prediction with healthy metrics."""
        predictor = CrashPredictor()

        # Healthy metrics history
        metrics_history = [
            {"health_score": 90.0, "error_rate": 0.1, "memory_mb": 200.0},
            {"health_score": 92.0, "error_rate": 0.0, "memory_mb": 210.0},
            {"health_score": 88.0, "error_rate": 0.2, "memory_mb": 205.0},
        ]

        probability = predictor.predict_crash_probability(metrics_history)

        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0
        assert probability < 0.3  # Should be low for healthy metrics

    def test_predict_crash_probability_high(self):
        """Test crash probability prediction with degraded metrics."""
        predictor = CrashPredictor()

        # Degraded metrics history
        metrics_history = [
            {"health_score": 40.0, "error_rate": 5.0, "memory_mb": 1800.0},
            {"health_score": 30.0, "error_rate": 8.0, "memory_mb": 1900.0},
            {"health_score": 20.0, "error_rate": 10.0, "memory_mb": 2000.0},
        ]

        probability = predictor.predict_crash_probability(metrics_history)

        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0
        assert probability > 0.7  # Should be high for degraded metrics

    def test_predict_crash_probability_empty_history(self):
        """Test crash probability with empty history."""
        predictor = CrashPredictor()

        probability = predictor.predict_crash_probability([])

        assert probability == 0.0  # No data = no prediction

    def test_detect_memory_leak_positive(self):
        """Test memory leak detection with increasing pattern."""
        predictor = CrashPredictor()

        # Memory increasing over time
        memory_history = [100.0, 150.0, 200.0, 250.0, 300.0, 350.0]

        has_leak = predictor.detect_memory_leak(memory_history)

        assert has_leak is True

    def test_detect_memory_leak_negative(self):
        """Test memory leak detection with stable pattern."""
        predictor = CrashPredictor()

        # Memory stable over time
        memory_history = [200.0, 205.0, 198.0, 202.0, 201.0, 203.0]

        has_leak = predictor.detect_memory_leak(memory_history)

        assert has_leak is False

    def test_detect_memory_leak_insufficient_data(self):
        """Test memory leak detection with insufficient data."""
        predictor = CrashPredictor()

        # Not enough data points
        memory_history = [100.0, 150.0]

        has_leak = predictor.detect_memory_leak(memory_history)

        assert has_leak is False  # Can't detect with < 5 points

    def test_estimate_time_to_failure_critical(self):
        """Test time to failure estimation with critical metrics."""
        predictor = CrashPredictor()

        # Critical metrics
        metrics = {
            "health_score": 10.0,
            "error_rate": 15.0,
            "memory_mb": 2500.0,
            "cpu_percent": 95.0,
        }

        time_estimate = predictor.estimate_time_to_failure(metrics)

        assert time_estimate is not None
        assert isinstance(time_estimate, int)
        assert time_estimate < 10  # Should be very soon

    def test_estimate_time_to_failure_healthy(self):
        """Test time to failure estimation with healthy metrics."""
        predictor = CrashPredictor()

        # Healthy metrics
        metrics = {
            "health_score": 90.0,
            "error_rate": 0.1,
            "memory_mb": 200.0,
            "cpu_percent": 30.0,
        }

        time_estimate = predictor.estimate_time_to_failure(metrics)

        assert time_estimate is None  # Healthy system shouldn't fail

    def test_predict_crash_with_full_prediction(self):
        """Test full crash prediction with all details."""
        predictor = CrashPredictor()

        metrics_history = [
            {"health_score": 50.0, "error_rate": 3.0, "memory_mb": 1500.0},
            {"health_score": 40.0, "error_rate": 5.0, "memory_mb": 1700.0},
            {"health_score": 30.0, "error_rate": 7.0, "memory_mb": 1900.0},
        ]

        # This would be a new method to get full prediction
        probability = predictor.predict_crash_probability(metrics_history)

        assert 0.0 <= probability <= 1.0


class TestPerformancePredictor:
    """Test PerformancePredictor class."""

    def test_predict_operation_time_consistent(self):
        """Test operation time prediction with consistent history."""
        predictor = PerformancePredictor()

        # Consistent operation times
        history = [1.0, 1.1, 0.9, 1.0, 1.2, 1.0]

        predicted_time = predictor.predict_operation_time("database_query", history)

        assert isinstance(predicted_time, float)
        assert predicted_time > 0.0
        assert 0.8 <= predicted_time <= 1.3  # Should be close to average

    def test_predict_operation_time_increasing(self):
        """Test operation time prediction with increasing trend."""
        predictor = PerformancePredictor()

        # Increasing operation times (performance degradation)
        history = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]

        predicted_time = predictor.predict_operation_time("api_call", history)

        assert isinstance(predicted_time, float)
        assert predicted_time > 3.0  # Should predict continued increase

    def test_predict_operation_time_empty_history(self):
        """Test operation time prediction with no history."""
        predictor = PerformancePredictor()

        predicted_time = predictor.predict_operation_time("new_operation", [])

        assert predicted_time == 1.0  # Default estimate

    def test_predict_bottleneck_cpu(self):
        """Test bottleneck prediction with high CPU."""
        predictor = PerformancePredictor()

        metrics = {
            "cpu_percent": 95.0,
            "memory_mb": 500.0,
            "operation_latency_ms": 200.0,
            "error_rate": 0.5,
        }

        bottleneck = predictor.predict_bottleneck(metrics)

        assert isinstance(bottleneck, str)
        assert bottleneck in ["cpu", "memory", "latency", "errors", "none"]
        assert bottleneck == "cpu"

    def test_predict_bottleneck_memory(self):
        """Test bottleneck prediction with high memory."""
        predictor = PerformancePredictor()

        metrics = {
            "cpu_percent": 30.0,
            "memory_mb": 2500.0,
            "operation_latency_ms": 200.0,
            "error_rate": 0.5,
        }

        bottleneck = predictor.predict_bottleneck(metrics)

        assert bottleneck == "memory"

    def test_predict_bottleneck_latency(self):
        """Test bottleneck prediction with high latency."""
        predictor = PerformancePredictor()

        metrics = {
            "cpu_percent": 30.0,
            "memory_mb": 500.0,
            "operation_latency_ms": 5000.0,
            "error_rate": 0.5,
        }

        bottleneck = predictor.predict_bottleneck(metrics)

        assert bottleneck == "latency"

    def test_predict_bottleneck_none(self):
        """Test bottleneck prediction with healthy metrics."""
        predictor = PerformancePredictor()

        metrics = {
            "cpu_percent": 30.0,
            "memory_mb": 500.0,
            "operation_latency_ms": 100.0,
            "error_rate": 0.1,
        }

        bottleneck = predictor.predict_bottleneck(metrics)

        assert bottleneck == "none"

    def test_predict_operation_time_with_outliers(self):
        """Test operation time prediction handles outliers."""
        predictor = PerformancePredictor()

        # History with one outlier
        history = [1.0, 1.1, 10.0, 1.0, 1.2, 1.1]  # 10.0 is outlier

        predicted_time = predictor.predict_operation_time("query", history)

        # Should not be heavily influenced by outlier
        assert 0.8 <= predicted_time <= 2.0
