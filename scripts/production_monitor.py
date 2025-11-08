#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Production Monitor - Exception tracking, Alert routing, and SLA monitoring

Provides real-time production monitoring with:
- Exception tracking and classification
- Smart alert routing by severity
- SLA monitoring and violation detection
- Root cause analysis
- Dashboard data for visualization

Usage:
    from production_monitor import ProductionMonitor

    monitor = ProductionMonitor()

    # Track exception
    exc_id = monitor.track_exception(
        exc=ValueError("Invalid input"),
        context={"user_id": "123", "action": "submit_form"},
        severity="high"
    )

    # Monitor SLA
    sla_report = monitor.monitor_sla({
        "p50_latency_ms": 45,
        "p95_latency_ms": 120,
        "p99_latency_ms": 250,
        "uptime_percent": 99.9,
        "error_rate_percent": 0.5
    })
"""

import hashlib
import json
import logging
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExceptionStatus(Enum):
    """Exception lifecycle status"""

    NEW = "new"
    ACTIVE = "active"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class Severity(Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertChannel(Enum):
    """Alert routing channels"""

    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    PAGERDUTY = "pagerduty"


@dataclass
class ExceptionRecord:
    """Exception tracking record"""

    exception_id: str
    exception_type: str
    message: str
    stack_trace: str
    severity: str
    status: str
    first_seen: str
    last_seen: str
    occurrence_count: int
    context: Dict[str, Any]
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None


@dataclass
class AlertRule:
    """Alert routing rule"""

    severity: str
    channels: List[str]
    assignee: Optional[str] = None
    escalate_after_minutes: int = 30


@dataclass
class SLAThreshold:
    """SLA threshold configuration"""

    p50_latency_ms: float = 100.0
    p95_latency_ms: float = 500.0
    p99_latency_ms: float = 1000.0
    uptime_percent: float = 99.9
    error_rate_percent: float = 1.0


@dataclass
class SLAReport:
    """SLA monitoring report"""

    timestamp: str
    metrics: Dict[str, float]
    violations: List[str]
    status: str  # "healthy", "warning", "critical"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class RootCauseAnalysis:
    """Root cause analysis result"""

    exception_id: str
    patterns: List[str]
    related_logs: List[str]
    affected_scope: Dict[str, Any]
    similar_cases: List[str]
    suggested_fixes: List[str]
    confidence_score: float


@dataclass
class DashboardData:
    """Dashboard visualization data"""

    timestamp: str
    active_exceptions: int
    total_exceptions_24h: int
    critical_alerts: int
    sla_status: str
    top_errors: List[Dict[str, Any]]
    error_trend: List[Dict[str, Any]]


class ProductionMonitor:
    """Production monitoring system for exception tracking and SLA monitoring"""

    def __init__(self, data_dir: Optional[Path] = None, sla_thresholds: Optional[SLAThreshold] = None):
        """Initialize ProductionMonitor

        Args:
            data_dir: Directory for storing monitoring data
            sla_thresholds: SLA threshold configuration
        """
        self.data_dir = data_dir or Path("RUNS/production_monitor")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.exceptions_file = self.data_dir / "exceptions.json"
        self.sla_history_file = self.data_dir / "sla_history.json"
        self.alerts_file = self.data_dir / "alerts.json"

        self.sla_thresholds = sla_thresholds or SLAThreshold()

        # In-memory cache
        self.exceptions: Dict[str, ExceptionRecord] = {}
        self.sla_history: List[SLAReport] = []
        self.alerts: List[Dict[str, Any]] = []

        # Load existing data
        self._load_data()

        # Default alert rules
        self.alert_rules = {
            Severity.CRITICAL.value: AlertRule(
                severity=Severity.CRITICAL.value,
                channels=[AlertChannel.PAGERDUTY.value, AlertChannel.SMS.value],
                escalate_after_minutes=5,
            ),
            Severity.HIGH.value: AlertRule(
                severity=Severity.HIGH.value,
                channels=[AlertChannel.SLACK.value, AlertChannel.EMAIL.value],
                escalate_after_minutes=15,
            ),
            Severity.MEDIUM.value: AlertRule(
                severity=Severity.MEDIUM.value, channels=[AlertChannel.SLACK.value], escalate_after_minutes=30
            ),
            Severity.LOW.value: AlertRule(
                severity=Severity.LOW.value, channels=[AlertChannel.EMAIL.value], escalate_after_minutes=60
            ),
        }

    def _load_data(self) -> None:
        """Load monitoring data from disk"""
        # Load exceptions
        if self.exceptions_file.exists():
            with open(self.exceptions_file, encoding="utf-8") as f:
                data = json.load(f)
                self.exceptions = {exc_id: ExceptionRecord(**exc_data) for exc_id, exc_data in data.items()}

        # Load SLA history
        if self.sla_history_file.exists():
            with open(self.sla_history_file, encoding="utf-8") as f:
                data = json.load(f)
                self.sla_history = [SLAReport(**report) for report in data]

        # Load alerts
        if self.alerts_file.exists():
            with open(self.alerts_file, encoding="utf-8") as f:
                self.alerts = json.load(f)

    def _save_data(self) -> None:
        """Save monitoring data to disk"""
        # Save exceptions
        with open(self.exceptions_file, "w", encoding="utf-8") as f:
            json.dump({exc_id: asdict(exc) for exc_id, exc in self.exceptions.items()}, f, indent=2)

        # Save SLA history (keep last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        recent_sla = [report for report in self.sla_history if datetime.fromisoformat(report.timestamp) > cutoff]
        with open(self.sla_history_file, "w", encoding="utf-8") as f:
            json.dump([asdict(report) for report in recent_sla], f, indent=2)

        # Save alerts (keep last 1000)
        with open(self.alerts_file, "w", encoding="utf-8") as f:
            json.dump(self.alerts[-1000:], f, indent=2)

    def _generate_exception_id(self, exc_type: str, message: str, stack_trace: str) -> str:
        """Generate unique exception ID based on type, message, and stack trace

        Args:
            exc_type: Exception class name
            message: Exception message
            stack_trace: Stack trace string

        Returns:
            Unique exception ID (MD5 hash)
        """
        # Use first 3 lines of stack trace for grouping similar exceptions
        stack_lines = stack_trace.split("\n")[:3]
        fingerprint = f"{exc_type}:{message}:{':'.join(stack_lines)}"
        return hashlib.md5(fingerprint.encode()).hexdigest()[:12]

    def track_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None, severity: str = "medium") -> str:
        """Track exception and return unique ID

        Args:
            exc: Exception instance
            context: Additional context (user_id, action, etc.)
            severity: Exception severity (critical/high/medium/low)

        Returns:
            Exception ID for tracking

        Example:
            exc_id = monitor.track_exception(
                exc=ValueError("Invalid input"),
                context={"user_id": "123", "action": "submit"},
                severity="high"
            )
        """
        exc_type = exc.__class__.__name__
        message = str(exc)
        stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

        exception_id = self._generate_exception_id(exc_type, message, stack_trace)

        now = datetime.now().isoformat()

        if exception_id in self.exceptions:
            # Update existing exception
            record = self.exceptions[exception_id]
            record.occurrence_count += 1
            record.last_seen = now
            logger.info(f"[EXCEPTION] Updated: {exception_id} (count: {record.occurrence_count})")
        else:
            # Create new exception record
            record = ExceptionRecord(
                exception_id=exception_id,
                exception_type=exc_type,
                message=message,
                stack_trace=stack_trace,
                severity=severity,
                status=ExceptionStatus.NEW.value,
                first_seen=now,
                last_seen=now,
                occurrence_count=1,
                context=context or {},
            )
            self.exceptions[exception_id] = record
            logger.warning(f"[EXCEPTION] New: {exception_id} ({exc_type}: {message})")

            # Route alert for new exception
            self.route_alert(exception_id, severity)

        self._save_data()
        return exception_id

    def route_alert(self, exception_id: str, severity: str, channels: Optional[List[str]] = None) -> None:
        """Route alert based on severity

        Args:
            exception_id: Exception ID
            severity: Alert severity
            channels: Override default channels (optional)

        Example:
            monitor.route_alert(
                exception_id="abc123",
                severity="critical",
                channels=["pagerduty", "sms"]
            )
        """
        if exception_id not in self.exceptions:
            logger.error(f"[ALERT] Exception not found: {exception_id}")
            return

        exception = self.exceptions[exception_id]
        rule = self.alert_rules.get(severity)

        if not rule:
            logger.warning(f"[ALERT] No rule for severity: {severity}")
            return

        target_channels = channels if channels is not None else rule.channels

        alert = {
            "timestamp": datetime.now().isoformat(),
            "exception_id": exception_id,
            "severity": severity,
            "channels": target_channels,
            "message": f"{exception.exception_type}: {exception.message}",
            "assignee": rule.assignee,
            "escalate_after_minutes": rule.escalate_after_minutes,
        }

        self.alerts.append(alert)

        # Log alert (in production, send to actual channels)
        logger.info(f"[ALERT] Routing {severity} alert for {exception_id} to {', '.join(target_channels)}")

        self._save_data()

    def monitor_sla(self, metrics: Dict[str, float]) -> SLAReport:
        """Monitor SLA metrics and detect violations

        Args:
            metrics: Performance metrics
                - p50_latency_ms: 50th percentile latency
                - p95_latency_ms: 95th percentile latency
                - p99_latency_ms: 99th percentile latency
                - uptime_percent: Uptime percentage
                - error_rate_percent: Error rate percentage

        Returns:
            SLA report with violations and status

        Example:
            report = monitor.monitor_sla({
                "p50_latency_ms": 45,
                "p95_latency_ms": 120,
                "p99_latency_ms": 250,
                "uptime_percent": 99.9,
                "error_rate_percent": 0.5
            })
        """
        violations = []
        recommendations = []

        # Check latency thresholds
        if metrics.get("p50_latency_ms", 0) > self.sla_thresholds.p50_latency_ms:
            violations.append(
                f"P50 latency ({metrics['p50_latency_ms']}ms) exceeds threshold ({self.sla_thresholds.p50_latency_ms}ms)"
            )
            recommendations.append("Investigate slow database queries or API calls")

        if metrics.get("p95_latency_ms", 0) > self.sla_thresholds.p95_latency_ms:
            violations.append(
                f"P95 latency ({metrics['p95_latency_ms']}ms) exceeds threshold ({self.sla_thresholds.p95_latency_ms}ms)"
            )
            recommendations.append("Check for resource contention or lock issues")

        if metrics.get("p99_latency_ms", 0) > self.sla_thresholds.p99_latency_ms:
            violations.append(
                f"P99 latency ({metrics['p99_latency_ms']}ms) exceeds threshold ({self.sla_thresholds.p99_latency_ms}ms)"
            )
            recommendations.append("Profile slow code paths and optimize hot spots")

        # Check uptime
        if metrics.get("uptime_percent", 100) < self.sla_thresholds.uptime_percent:
            violations.append(
                f"Uptime ({metrics['uptime_percent']}%) below threshold ({self.sla_thresholds.uptime_percent}%)"
            )
            recommendations.append("Review recent downtime incidents and failure patterns")

        # Check error rate
        if metrics.get("error_rate_percent", 0) > self.sla_thresholds.error_rate_percent:
            violations.append(
                f"Error rate ({metrics['error_rate_percent']}%) "
                f"exceeds threshold ({self.sla_thresholds.error_rate_percent}%)"
            )
            recommendations.append("Analyze top errors and implement fixes")

        # Determine status
        if len(violations) >= 3:
            status = "critical"
        elif len(violations) > 0:
            status = "warning"
        else:
            status = "healthy"

        report = SLAReport(
            timestamp=datetime.now().isoformat(),
            metrics=metrics,
            violations=violations,
            status=status,
            recommendations=recommendations,
        )

        self.sla_history.append(report)
        self._save_data()

        if status != "healthy":
            logger.warning(f"[SLA] Status: {status} - {len(violations)} violations")

        return report

    def analyze_root_cause(self, exception_id: str) -> RootCauseAnalysis:
        """Analyze root cause of exception

        Args:
            exception_id: Exception ID to analyze

        Returns:
            Root cause analysis with patterns and suggestions

        Example:
            analysis = monitor.analyze_root_cause("abc123")
            print(analysis.suggested_fixes)
        """
        if exception_id not in self.exceptions:
            raise ValueError(f"Exception not found: {exception_id}")

        exception = self.exceptions[exception_id]

        # Pattern detection
        patterns = []
        if exception.occurrence_count > 10:
            patterns.append(f"High frequency: {exception.occurrence_count} occurrences")
        if "timeout" in exception.message.lower():
            patterns.append("Timeout pattern detected")
        if "connection" in exception.message.lower() or "connect" in exception.message.lower():
            patterns.append("Connection issue pattern detected")
        if "null" in exception.message.lower() or "none" in exception.message.lower():
            patterns.append("Null reference pattern detected")

        # Find similar cases
        similar_cases = []
        for exc_id, exc in self.exceptions.items():
            if exc_id != exception_id and exc.exception_type == exception.exception_type:
                if exc.status == ExceptionStatus.RESOLVED.value:
                    similar_cases.append(exc_id)

        # Generate suggestions
        suggested_fixes = []
        if "timeout" in exception.message.lower():
            suggested_fixes.append("Increase timeout configuration")
            suggested_fixes.append("Optimize slow operations")
            suggested_fixes.append("Implement retry logic with exponential backoff")
        if "connection" in exception.message.lower() or "connect" in exception.message.lower():
            suggested_fixes.append("Check network connectivity")
            suggested_fixes.append("Verify service endpoints are accessible")
            suggested_fixes.append("Implement connection pooling")
        if exception.exception_type == "ValueError":
            suggested_fixes.append("Add input validation")
            suggested_fixes.append("Implement data sanitization")
        if exception.exception_type == "KeyError":
            suggested_fixes.append("Use .get() with default values")
            suggested_fixes.append("Add existence checks before access")

        # Calculate confidence score
        confidence_score = 0.5
        if patterns:
            confidence_score += 0.2
        if similar_cases:
            confidence_score += 0.2
        if suggested_fixes:
            confidence_score += 0.1

        analysis = RootCauseAnalysis(
            exception_id=exception_id,
            patterns=patterns,
            related_logs=[],  # Would integrate with logging system
            affected_scope={"occurrence_count": exception.occurrence_count, "context": exception.context},
            similar_cases=similar_cases,
            suggested_fixes=suggested_fixes,
            confidence_score=min(confidence_score, 1.0),
        )

        return analysis

    def get_dashboard_data(self) -> DashboardData:
        """Get dashboard visualization data

        Returns:
            Dashboard data for real-time monitoring

        Example:
            data = monitor.get_dashboard_data()
            print(f"Active exceptions: {data.active_exceptions}")
        """
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        # Count active exceptions
        active_exceptions = sum(1 for exc in self.exceptions.values() if exc.status == ExceptionStatus.ACTIVE.value)

        # Count exceptions in last 24h
        total_exceptions_24h = sum(1 for exc in self.exceptions.values() if datetime.fromisoformat(exc.last_seen) > last_24h)

        # Count critical alerts in last hour
        last_hour = now - timedelta(hours=1)
        critical_alerts = sum(
            1
            for alert in self.alerts
            if alert["severity"] == Severity.CRITICAL.value and datetime.fromisoformat(alert["timestamp"]) > last_hour
        )

        # Get latest SLA status
        sla_status = self.sla_history[-1].status if self.sla_history else "unknown"

        # Top errors by occurrence
        top_errors = sorted(
            [
                {
                    "exception_id": exc_id,
                    "type": exc.exception_type,
                    "message": exc.message,
                    "count": exc.occurrence_count,
                    "severity": exc.severity,
                }
                for exc_id, exc in self.exceptions.items()
            ],
            key=lambda x: x["count"],
            reverse=True,
        )[:10]

        # Error trend (last 7 days)
        error_trend = []
        for i in range(7):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            count = sum(
                1 for exc in self.exceptions.values() if day_start <= datetime.fromisoformat(exc.first_seen) < day_end
            )

            error_trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

        error_trend.reverse()

        return DashboardData(
            timestamp=now.isoformat(),
            active_exceptions=active_exceptions,
            total_exceptions_24h=total_exceptions_24h,
            critical_alerts=critical_alerts,
            sla_status=sla_status,
            top_errors=top_errors,
            error_trend=error_trend,
        )

    def resolve_exception(self, exception_id: str, resolution_notes: str) -> None:
        """Mark exception as resolved

        Args:
            exception_id: Exception ID to resolve
            resolution_notes: Notes about how it was resolved

        Example:
            monitor.resolve_exception(
                exception_id="abc123",
                resolution_notes="Fixed by updating timeout configuration"
            )
        """
        if exception_id not in self.exceptions:
            raise ValueError(f"Exception not found: {exception_id}")

        exception = self.exceptions[exception_id]
        exception.status = ExceptionStatus.RESOLVED.value
        exception.resolved_at = datetime.now().isoformat()
        exception.resolution_notes = resolution_notes

        self._save_data()
        logger.info(f"[RESOLUTION] Resolved: {exception_id}")


def main():
    """CLI interface for ProductionMonitor"""
    import argparse

    parser = argparse.ArgumentParser(description="Production monitoring system")
    parser.add_argument("command", choices=["dashboard", "exceptions", "sla"], help="Command to run")
    parser.add_argument("--exception-id", help="Exception ID for analysis")

    args = parser.parse_args()

    monitor = ProductionMonitor()

    if args.command == "dashboard":
        data = monitor.get_dashboard_data()
        print(f"\n[DASHBOARD] {data.timestamp}")
        print(f"Active Exceptions: {data.active_exceptions}")
        print(f"Total (24h): {data.total_exceptions_24h}")
        print(f"Critical Alerts: {data.critical_alerts}")
        print(f"SLA Status: {data.sla_status}")
        print("\n[TOP ERRORS]")
        for err in data.top_errors[:5]:
            print(f"  - {err['type']}: {err['message'][:50]} (count: {err['count']})")

    elif args.command == "exceptions":
        print(f"\n[EXCEPTIONS] Total: {len(monitor.exceptions)}")
        for exc_id, exc in list(monitor.exceptions.items())[:10]:
            print(f"\n  ID: {exc_id}")
            print(f"  Type: {exc.exception_type}")
            print(f"  Message: {exc.message}")
            print(f"  Status: {exc.status}")
            print(f"  Count: {exc.occurrence_count}")

    elif args.command == "sla":
        if monitor.sla_history:
            latest = monitor.sla_history[-1]
            print(f"\n[SLA REPORT] {latest.timestamp}")
            print(f"Status: {latest.status}")
            print(f"Metrics: {latest.metrics}")
            if latest.violations:
                print("\n[VIOLATIONS]")
                for violation in latest.violations:
                    print(f"  - {violation}")
            if latest.recommendations:
                print("\n[RECOMMENDATIONS]")
                for rec in latest.recommendations:
                    print(f"  - {rec}")
        else:
            print("[SLA] No reports available")


if __name__ == "__main__":
    main()
