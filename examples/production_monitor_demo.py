#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ProductionMonitor Usage Examples

Demonstrates various use cases of ProductionMonitor for production monitoring.

Examples:
1. Basic exception tracking
2. Alert routing by severity
3. SLA monitoring and violations
4. Root cause analysis
5. Dashboard data retrieval
6. Exception resolution workflow
7. Integration with applications
"""

import sys
from datetime import datetime
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from production_monitor import (
    ProductionMonitor,
    SLAThreshold,
)


def example_1_basic_exception_tracking():
    """Example 1: Track exceptions and group duplicates"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Exception Tracking")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Track first exception
    try:
        raise ValueError("Invalid user input: age cannot be negative")
    except ValueError as e:
        exc_id1 = monitor.track_exception(exc=e, context={"user_id": "user_123", "action": "signup"}, severity="medium")

        print(f"\n[FIRST OCCURRENCE] Exception ID: {exc_id1}")
        print(f"  Type: {monitor.exceptions[exc_id1].exception_type}")
        print(f"  Message: {monitor.exceptions[exc_id1].message}")
        print(f"  Count: {monitor.exceptions[exc_id1].occurrence_count}")

    # Same exception again
    try:
        raise ValueError("Invalid user input: age cannot be negative")
    except ValueError as e:
        exc_id2 = monitor.track_exception(exc=e, context={"user_id": "user_456", "action": "signup"}, severity="medium")

        print(f"\n[SECOND OCCURRENCE] Exception ID: {exc_id2}")
        print(f"  Same ID? {exc_id1 == exc_id2}")
        print(f"  Count: {monitor.exceptions[exc_id2].occurrence_count}")
        print("  → Automatically grouped as same error")

    # Different exception
    try:
        raise KeyError("configuration_key_missing")
    except KeyError as e:
        exc_id3 = monitor.track_exception(exc=e, severity="high")

        print(f"\n[DIFFERENT ERROR] Exception ID: {exc_id3}")
        print(f"  Same as first? {exc_id1 == exc_id3}")
        print("  → Different exception type/message = different ID")


def example_2_alert_routing():
    """Example 2: Alert routing by severity"""
    print("\n\n" + "=" * 70)
    print("Example 2: Alert Routing by Severity")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Critical alert
    try:
        raise ConnectionError("Database connection pool exhausted")
    except ConnectionError as e:
        exc_id = monitor.track_exception(exc=e, severity="critical")

        alert = monitor.alerts[-1]
        print("\n[CRITICAL ALERT]")
        print(f"  Exception: {exc_id}")
        print(f"  Channels: {alert['channels']}")
        print(f"  Escalation: {alert['escalate_after_minutes']} minutes")
        print("  → PagerDuty + SMS for critical errors")

    # High alert
    try:
        raise ValueError("Payment validation failed")
    except ValueError as e:
        exc_id = monitor.track_exception(exc=e, severity="high")

        alert = monitor.alerts[-1]
        print("\n[HIGH ALERT]")
        print(f"  Exception: {exc_id}")
        print(f"  Channels: {alert['channels']}")
        print("  → Slack + Email for high severity")

    # Medium alert
    try:
        raise RuntimeError("Cache miss rate above threshold")
    except RuntimeError as e:
        exc_id = monitor.track_exception(exc=e, severity="medium")

        alert = monitor.alerts[-1]
        print("\n[MEDIUM ALERT]")
        print(f"  Exception: {exc_id}")
        print(f"  Channels: {alert['channels']}")
        print("  → Slack only for medium severity")


def example_3_sla_monitoring():
    """Example 3: SLA monitoring with violations"""
    print("\n\n" + "=" * 70)
    print("Example 3: SLA Monitoring")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Healthy metrics
    print("\n[SCENARIO 1: Healthy System]")
    report1 = monitor.monitor_sla(
        {
            "p50_latency_ms": 45,
            "p95_latency_ms": 180,
            "p99_latency_ms": 400,
            "uptime_percent": 99.95,
            "error_rate_percent": 0.2,
        }
    )

    print(f"  Status: {report1.status}")
    print(f"  Violations: {len(report1.violations)}")
    print("  → All metrics within thresholds")

    # Single violation (warning)
    print("\n[SCENARIO 2: Minor Issue]")
    report2 = monitor.monitor_sla(
        {
            "p50_latency_ms": 150,  # Exceeds 100ms threshold
            "p95_latency_ms": 180,
            "p99_latency_ms": 400,
            "uptime_percent": 99.95,
            "error_rate_percent": 0.2,
        }
    )

    print(f"  Status: {report2.status}")
    print(f"  Violations: {report2.violations}")
    print(f"  Recommendations: {report2.recommendations}")

    # Multiple violations (critical)
    print("\n[SCENARIO 3: System Degradation]")
    report3 = monitor.monitor_sla(
        {
            "p50_latency_ms": 200,  # Exceeds
            "p95_latency_ms": 800,  # Exceeds
            "p99_latency_ms": 1500,  # Exceeds
            "uptime_percent": 98.0,  # Below threshold
            "error_rate_percent": 3.0,  # Exceeds
        }
    )

    print(f"  Status: {report3.status}")
    print(f"  Violations: {len(report3.violations)} critical issues")
    for violation in report3.violations:
        print(f"    - {violation}")


def example_4_root_cause_analysis():
    """Example 4: Root cause analysis with suggestions"""
    print("\n\n" + "=" * 70)
    print("Example 4: Root Cause Analysis")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Timeout exception
    print("\n[CASE 1: Timeout Error]")
    try:
        raise TimeoutError("Database query timeout after 30 seconds")
    except TimeoutError as e:
        exc_id = monitor.track_exception(exc=e)

    analysis = monitor.analyze_root_cause(exc_id)
    print(f"  Exception ID: {exc_id}")
    print(f"  Patterns: {analysis.patterns}")
    print("  Suggested Fixes:")
    for fix in analysis.suggested_fixes:
        print(f"    - {fix}")
    print(f"  Confidence: {analysis.confidence_score:.0%}")

    # Connection exception
    print("\n[CASE 2: Connection Error]")
    try:
        raise ConnectionError("Failed to connect to API endpoint")
    except ConnectionError as e:
        exc_id = monitor.track_exception(exc=e)

    analysis = monitor.analyze_root_cause(exc_id)
    print(f"  Exception ID: {exc_id}")
    print(f"  Patterns: {analysis.patterns}")
    print("  Suggested Fixes:")
    for fix in analysis.suggested_fixes:
        print(f"    - {fix}")

    # High frequency exception
    print("\n[CASE 3: High Frequency Error]")
    try:
        raise ValueError("Invalid configuration")
    except ValueError as e:
        # Track 15 times
        for _ in range(15):
            exc_id = monitor.track_exception(exc=e)

    analysis = monitor.analyze_root_cause(exc_id)
    print(f"  Exception ID: {exc_id}")
    print(f"  Occurrence Count: {monitor.exceptions[exc_id].occurrence_count}")
    print(f"  Patterns: {analysis.patterns}")
    print("  → High frequency detected, likely systemic issue")


def example_5_dashboard_data():
    """Example 5: Dashboard data for visualization"""
    print("\n\n" + "=" * 70)
    print("Example 5: Dashboard Data Retrieval")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Create some test data
    for i in range(5):
        try:
            raise ValueError(f"Test error {i}")
        except ValueError as e:
            monitor.track_exception(exc=e, severity="high" if i < 2 else "medium")

    # Monitor SLA
    monitor.monitor_sla(
        {
            "p50_latency_ms": 150,
            "p95_latency_ms": 200,
            "p99_latency_ms": 400,
            "uptime_percent": 99.95,
            "error_rate_percent": 0.5,
        }
    )

    # Get dashboard data
    data = monitor.get_dashboard_data()

    print("\n[DASHBOARD METRICS]")
    print(f"  Timestamp: {data.timestamp}")
    print(f"  Active Exceptions: {data.active_exceptions}")
    print(f"  Total (24h): {data.total_exceptions_24h}")
    print(f"  Critical Alerts: {data.critical_alerts}")
    print(f"  SLA Status: {data.sla_status}")

    print("\n[TOP ERRORS]")
    for error in data.top_errors[:5]:
        print(f"  - {error['type']}: {error['message'][:40]}... (count: {error['count']})")

    print("\n[ERROR TREND]")
    print("  Last 7 days:")
    for day in data.error_trend[-3:]:
        print(f"    {day['date']}: {day['count']} errors")


def example_6_exception_resolution():
    """Example 6: Exception resolution workflow"""
    print("\n\n" + "=" * 70)
    print("Example 6: Exception Resolution Workflow")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Create exception
    print("\n[STEP 1: Exception Occurs]")
    try:
        raise ConnectionError("Redis connection pool exhausted")
    except ConnectionError as e:
        exc_id = monitor.track_exception(exc=e, context={"service": "cache", "pool_size": 10}, severity="critical")

    exception = monitor.exceptions[exc_id]
    print(f"  Exception ID: {exc_id}")
    print(f"  Status: {exception.status}")
    print(f"  First Seen: {exception.first_seen}")

    # Analyze root cause
    print("\n[STEP 2: Root Cause Analysis]")
    analysis = monitor.analyze_root_cause(exc_id)
    print("  Analysis:")
    for pattern in analysis.patterns:
        print(f"    - {pattern}")
    print("\n  Suggested Fixes:")
    for fix in analysis.suggested_fixes:
        print(f"    - {fix}")

    # Resolve exception
    print("\n[STEP 3: Apply Fix and Resolve]")
    resolution_notes = """
    Root Cause: Redis connection pool size (10) insufficient for load
    Fix Applied: Increased pool size to 50 in config
    Deployed: 2025-11-02 14:30 UTC
    Verification: Monitored for 1 hour, no recurrence
    Impact: Error rate dropped from 5% to 0%
    """

    monitor.resolve_exception(exc_id, resolution_notes.strip())

    exception = monitor.exceptions[exc_id]
    print(f"  Status: {exception.status}")
    print(f"  Resolved At: {exception.resolved_at}")
    print(f"  Notes: {exception.resolution_notes[:50]}...")


def example_7_integration_pattern():
    """Example 7: Integration with application"""
    print("\n\n" + "=" * 70)
    print("Example 7: Application Integration Pattern")
    print("=" * 70)

    monitor = ProductionMonitor()

    # Simulated application with monitoring
    class PaymentService:
        def __init__(self, monitor):
            self.monitor = monitor

        def process_payment(self, user_id, amount):
            try:
                # Simulated payment logic
                if amount <= 0:
                    raise ValueError("Payment amount must be positive")
                if amount > 10000:
                    raise ValueError("Payment amount exceeds limit")

                # Success
                return {"status": "success", "amount": amount}

            except Exception as e:
                # Track exception with context
                exc_id = self.monitor.track_exception(
                    exc=e,
                    context={
                        "user_id": user_id,
                        "amount": amount,
                        "service": "payment",
                        "timestamp": datetime.now().isoformat(),
                    },
                    severity="critical" if amount > 1000 else "high",
                )

                # Return error with incident ID
                return {"status": "error", "incident_id": exc_id, "message": str(e)}

    # Test service
    service = PaymentService(monitor)

    print("\n[TEST 1: Valid Payment]")
    result1 = service.process_payment("user_123", 99.99)
    print(f"  Result: {result1['status']}")

    print("\n[TEST 2: Invalid Amount (Low Value)]")
    result2 = service.process_payment("user_456", -10)
    print(f"  Result: {result2['status']}")
    print(f"  Incident ID: {result2.get('incident_id')}")
    print("  Severity: high (amount < 1000)")

    print("\n[TEST 3: Invalid Amount (High Value)]")
    result3 = service.process_payment("user_789", 15000)
    print(f"  Result: {result3['status']}")
    print(f"  Incident ID: {result3.get('incident_id')}")
    print("  Severity: critical (amount > 1000)")

    # Show collected exceptions
    print("\n[EXCEPTIONS TRACKED]")
    print(f"  Total: {len(monitor.exceptions)}")
    for exc_id, exc in list(monitor.exceptions.items())[:3]:
        print(f"    - {exc_id}: {exc.exception_type} (severity: {exc.severity})")


def example_8_custom_sla_thresholds():
    """Example 8: Custom SLA thresholds for different services"""
    print("\n\n" + "=" * 70)
    print("Example 8: Custom SLA Thresholds")
    print("=" * 70)

    # High-performance API
    print("\n[SERVICE 1: High-Performance API]")
    strict_sla = SLAThreshold(
        p50_latency_ms=50.0,  # Very fast
        p95_latency_ms=150.0,
        p99_latency_ms=300.0,
        uptime_percent=99.99,  # Four nines
        error_rate_percent=0.1,
    )

    monitor_api = ProductionMonitor(sla_thresholds=strict_sla)
    report_api = monitor_api.monitor_sla(
        {
            "p50_latency_ms": 60,
            "p95_latency_ms": 140,
            "p99_latency_ms": 280,
            "uptime_percent": 99.99,
            "error_rate_percent": 0.05,
        }
    )

    print(f"  Thresholds: p50={strict_sla.p50_latency_ms}ms, uptime={strict_sla.uptime_percent}%")
    print(f"  Status: {report_api.status}")
    print(f"  Violations: {len(report_api.violations)}")

    # Batch processing service (relaxed)
    print("\n[SERVICE 2: Batch Processing]")
    relaxed_sla = SLAThreshold(
        p50_latency_ms=1000.0,  # 1 second OK
        p95_latency_ms=5000.0,  # 5 seconds OK
        p99_latency_ms=10000.0,  # 10 seconds OK
        uptime_percent=99.0,  # Two nines OK
        error_rate_percent=5.0,  # 5% error rate acceptable
    )

    monitor_batch = ProductionMonitor(sla_thresholds=relaxed_sla)
    report_batch = monitor_batch.monitor_sla(
        {
            "p50_latency_ms": 800,
            "p95_latency_ms": 4000,
            "p99_latency_ms": 9000,
            "uptime_percent": 99.5,
            "error_rate_percent": 2.0,
        }
    )

    print(f"  Thresholds: p50={relaxed_sla.p50_latency_ms}ms, uptime={relaxed_sla.uptime_percent}%")
    print(f"  Status: {report_batch.status}")
    print(f"  Violations: {len(report_batch.violations)}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" " * 15 + "ProductionMonitor Demo")
    print("=" * 70)
    print("\nThis demo shows how to use ProductionMonitor for production")
    print("exception tracking, SLA monitoring, and alert routing.\n")

    try:
        example_1_basic_exception_tracking()
        example_2_alert_routing()
        example_3_sla_monitoring()
        example_4_root_cause_analysis()
        example_5_dashboard_data()
        example_6_exception_resolution()
        example_7_integration_pattern()
        example_8_custom_sla_thresholds()

        print("\n\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Integrate with your application error handlers")
        print("  2. Configure custom SLA thresholds for your services")
        print("  3. Set up alert channels (Slack, PagerDuty, email)")
        print("  4. Review dashboard regularly for trends")
        print("  5. Resolve exceptions with detailed notes")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
