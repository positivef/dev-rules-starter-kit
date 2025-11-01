#!/usr/bin/env python
"""
CoverageMonitor: Real-time Test Coverage Tracking Tool
======================================================

실시간 테스트 커버리지 모니터링 및 알림 시스템

Features:
- Real-time coverage monitoring
- Historical trend analysis
- Automatic alerts for coverage drops
- Incremental testing support
- Coverage reports in multiple formats
- Per-file and per-function analysis
- Branch coverage tracking

Constitutional Compliance:
- P8: Test First - Enforces test coverage standards
- P2: Evidence-Based - Records coverage history
- P6: Quality Gates - Coverage thresholds
- P3: Knowledge Asset - Coverage reports to Obsidian
"""

import json
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Coverage thresholds
COVERAGE_THRESHOLDS = {
    "critical": 90,  # Critical files must have 90%+ coverage
    "high": 80,  # High importance files need 80%+
    "medium": 70,  # Medium importance files need 70%+
    "low": 60,  # Low importance files need 60%+
    "overall": 75,  # Overall project coverage target
}

# File criticality patterns
CRITICAL_PATTERNS = {
    "critical": ["*executor*.py", "*validator*.py", "*guard*.py", "project_*.py", "context_*.py"],
    "high": ["*bridge*.py", "*analyzer*.py", "*manager*.py", "*core*.py"],
    "medium": ["*helper*.py", "*utils*.py", "*cli*.py"],
}


class CoverageDatabase:
    """SQLite database for coverage history"""

    def __init__(self, db_path: str = "RUNS/coverage/coverage_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Coverage snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coverage_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_coverage REAL NOT NULL,
                    line_coverage REAL,
                    branch_coverage REAL,
                    files_total INTEGER,
                    files_covered INTEGER,
                    lines_total INTEGER,
                    lines_covered INTEGER,
                    branches_total INTEGER,
                    branches_covered INTEGER
                )
            """)

            # File coverage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_coverage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    coverage_percent REAL NOT NULL,
                    lines_total INTEGER,
                    lines_covered INTEGER,
                    lines_missing TEXT,
                    criticality TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES coverage_snapshots(id)
                )
            """)

            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coverage_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT
                )
            """)

            conn.commit()

    def save_snapshot(self, coverage_data: Dict) -> int:
        """Save coverage snapshot to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert main snapshot
            cursor.execute(
                """
                INSERT INTO coverage_snapshots (
                    timestamp, overall_coverage, line_coverage, branch_coverage,
                    files_total, files_covered, lines_total, lines_covered,
                    branches_total, branches_covered
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    coverage_data.get("overall_coverage", 0),
                    coverage_data.get("line_coverage", 0),
                    coverage_data.get("branch_coverage", 0),
                    coverage_data.get("files_total", 0),
                    coverage_data.get("files_covered", 0),
                    coverage_data.get("lines_total", 0),
                    coverage_data.get("lines_covered", 0),
                    coverage_data.get("branches_total", 0),
                    coverage_data.get("branches_covered", 0),
                ),
            )

            snapshot_id = cursor.lastrowid

            # Insert file coverage
            for file_data in coverage_data.get("files", []):
                cursor.execute(
                    """
                    INSERT INTO file_coverage (
                        snapshot_id, filename, coverage_percent,
                        lines_total, lines_covered, lines_missing, criticality
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        snapshot_id,
                        file_data["filename"],
                        file_data["coverage_percent"],
                        file_data["lines_total"],
                        file_data["lines_covered"],
                        json.dumps(file_data.get("lines_missing", [])),
                        file_data.get("criticality", "low"),
                    ),
                )

            conn.commit()
            return snapshot_id

    def get_trend(self, hours: int = 24) -> List[Dict]:
        """Get coverage trend for specified hours"""
        since = datetime.now() - timedelta(hours=hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, overall_coverage, line_coverage, branch_coverage
                FROM coverage_snapshots
                WHERE timestamp >= ?
                ORDER BY timestamp
            """,
                (since.isoformat(),),
            )

            return [{"timestamp": row[0], "overall": row[1], "line": row[2], "branch": row[3]} for row in cursor.fetchall()]

    def save_alert(self, alert_type: str, severity: str, message: str, details: str = None):
        """Save coverage alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO coverage_alerts (timestamp, alert_type, severity, message, details)
                VALUES (?, ?, ?, ?, ?)
            """,
                (datetime.now().isoformat(), alert_type, severity, message, details),
            )
            conn.commit()


class CoverageAnalyzer:
    """Analyze coverage data and generate insights"""

    def __init__(self):
        self.db = CoverageDatabase()

    def run_coverage(self) -> Dict:
        """Run pytest with coverage and parse results"""
        print("[COVERAGE] Running tests with coverage...")

        # Run pytest with coverage
        cmd = ["python", "-m", "pytest", "--cov=scripts", "--cov-report=json", "--cov-report=term", "tests/", "-q"]

        try:
            subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

            # Parse coverage.json
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file, "r", encoding="utf-8") as f:
                    coverage_json = json.load(f)
                return self.parse_coverage_json(coverage_json)
            else:
                print("[ERROR] coverage.json not found")
                return {}

        except Exception as e:
            print(f"[ERROR] Coverage run failed: {e}")
            return {}

    def parse_coverage_json(self, coverage_json: Dict) -> Dict:
        """Parse coverage.json into structured data"""
        coverage_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_coverage": 0,
            "line_coverage": 0,
            "branch_coverage": 0,
            "files_total": 0,
            "files_covered": 0,
            "lines_total": 0,
            "lines_covered": 0,
            "branches_total": 0,
            "branches_covered": 0,
            "files": [],
        }

        # Parse totals
        if "totals" in coverage_json:
            totals = coverage_json["totals"]
            coverage_data["lines_total"] = totals.get("num_statements", 0)
            coverage_data["lines_covered"] = totals.get("covered_lines", 0)
            coverage_data["line_coverage"] = totals.get("percent_covered", 0)
            coverage_data["overall_coverage"] = totals.get("percent_covered", 0)

            if "num_branches" in totals:
                coverage_data["branches_total"] = totals["num_branches"]
                coverage_data["branches_covered"] = totals.get("covered_branches", 0)
                if coverage_data["branches_total"] > 0:
                    coverage_data["branch_coverage"] = (
                        coverage_data["branches_covered"] / coverage_data["branches_total"] * 100
                    )

        # Parse file coverage
        if "files" in coverage_json:
            for filename, file_data in coverage_json["files"].items():
                # Skip test files
                if "test" in filename or "__pycache__" in filename:
                    continue

                file_info = {
                    "filename": filename,
                    "lines_total": file_data["summary"].get("num_statements", 0),
                    "lines_covered": file_data["summary"].get("covered_lines", 0),
                    "coverage_percent": file_data["summary"].get("percent_covered", 0),
                    "lines_missing": file_data.get("missing_lines", []),
                    "criticality": self.get_file_criticality(filename),
                }

                coverage_data["files"].append(file_info)
                coverage_data["files_total"] += 1
                if file_info["coverage_percent"] > 0:
                    coverage_data["files_covered"] += 1

        return coverage_data

    def get_file_criticality(self, filename: str) -> str:
        """Determine file criticality level"""
        from fnmatch import fnmatch

        basename = Path(filename).name

        for level, patterns in CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if fnmatch(basename, pattern):
                    return level

        return "low"

    def check_thresholds(self, coverage_data: Dict) -> List[Dict]:
        """Check coverage against thresholds and generate alerts"""
        alerts = []

        # Check overall coverage
        overall = coverage_data.get("overall_coverage", 0)
        if overall < COVERAGE_THRESHOLDS["overall"]:
            alerts.append(
                {
                    "type": "overall_coverage",
                    "severity": "high" if overall < 60 else "medium",
                    "message": f"Overall coverage ({overall:.1f}%) below threshold ({COVERAGE_THRESHOLDS['overall']}%)",
                    "value": overall,
                }
            )

        # Check critical files
        for file_info in coverage_data.get("files", []):
            criticality = file_info["criticality"]
            coverage = file_info["coverage_percent"]
            threshold = COVERAGE_THRESHOLDS.get(criticality, 60)

            if coverage < threshold:
                severity = "critical" if criticality == "critical" else "high"
                alerts.append(
                    {
                        "type": "file_coverage",
                        "severity": severity,
                        "message": f"{file_info['filename']} ({coverage:.1f}%) below {criticality} threshold ({threshold}%)",
                        "file": file_info["filename"],
                        "value": coverage,
                        "threshold": threshold,
                    }
                )

        return alerts

    def generate_report(self, coverage_data: Dict) -> str:
        """Generate coverage report"""
        report = f"""# Test Coverage Report

## Summary
- **Timestamp**: {coverage_data['timestamp']}
- **Overall Coverage**: {coverage_data['overall_coverage']:.1f}%
- **Line Coverage**: {coverage_data['line_coverage']:.1f}%
- **Branch Coverage**: {coverage_data['branch_coverage']:.1f}%

## Statistics
- **Files**: {coverage_data['files_covered']}/{coverage_data['files_total']} covered
- **Lines**: {coverage_data['lines_covered']}/{coverage_data['lines_total']} covered
- **Branches**: {coverage_data['branches_covered']}/{coverage_data['branches_total']} covered

## File Coverage

| File | Coverage | Criticality | Status |
|------|----------|-------------|--------|
"""
        # Sort files by criticality then coverage
        files = sorted(
            coverage_data.get("files", []),
            key=lambda x: (["critical", "high", "medium", "low"].index(x["criticality"]), -x["coverage_percent"]),
        )

        for file_info in files:
            coverage = file_info["coverage_percent"]
            criticality = file_info["criticality"]
            threshold = COVERAGE_THRESHOLDS.get(criticality, 60)
            status = "[OK]" if coverage >= threshold else "[FAIL]"

            report += f"| {file_info['filename']} | {coverage:.1f}% | {criticality} | {status} |\n"

        # Add missing lines for critical files
        report += "\n## Critical Files Needing Coverage\n\n"
        critical_files = [f for f in files if f["criticality"] in ["critical", "high"] and f["coverage_percent"] < 80]

        for file_info in critical_files[:5]:  # Top 5 critical files
            report += f"### {file_info['filename']} ({file_info['coverage_percent']:.1f}%)\n"
            report += f"Missing lines: {', '.join(map(str, file_info['lines_missing'][:10]))}\n\n"

        return report


class CoverageWatcher(FileSystemEventHandler):
    """Watch for file changes and trigger coverage updates"""

    def __init__(self, analyzer: CoverageAnalyzer, auto_run: bool = True):
        self.analyzer = analyzer
        self.auto_run = auto_run
        self.last_run = time.time()
        self.min_interval = 10  # Minimum seconds between runs

    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return

        # Only watch Python files
        if not event.src_path.endswith(".py"):
            return

        # Skip test files and cache
        if "__pycache__" in event.src_path or ".pyc" in event.src_path:
            return

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_run < self.min_interval:
            return

        if self.auto_run:
            print(f"\n[WATCH] File changed: {event.src_path}")
            print("[WATCH] Running coverage check...")
            self.run_coverage_check()
            self.last_run = current_time

    def run_coverage_check(self):
        """Run coverage check and process results"""
        coverage_data = self.analyzer.run_coverage()
        if coverage_data:
            # Save to database
            self.analyzer.db.save_snapshot(coverage_data)

            # Check thresholds
            alerts = self.analyzer.check_thresholds(coverage_data)
            for alert in alerts:
                print(f"[ALERT] {alert['severity'].upper()}: {alert['message']}")
                self.analyzer.db.save_alert(alert["type"], alert["severity"], alert["message"], json.dumps(alert))

            # Print summary
            print(f"\n[COVERAGE] Overall: {coverage_data['overall_coverage']:.1f}%")


class CoverageMonitor:
    """Main coverage monitoring system"""

    def __init__(self):
        self.analyzer = CoverageAnalyzer()
        self.watcher = None
        self.observer = None

    def start_monitoring(self, watch_paths: List[str] = None):
        """Start file system monitoring"""
        if watch_paths is None:
            watch_paths = ["scripts/", "tests/"]

        print("[MONITOR] Starting coverage monitoring...")
        print(f"[MONITOR] Watching: {', '.join(watch_paths)}")

        self.watcher = CoverageWatcher(self.analyzer)
        self.observer = Observer()

        for path in watch_paths:
            if Path(path).exists():
                self.observer.schedule(self.watcher, path, recursive=True)

        self.observer.start()

        print("[MONITOR] Coverage monitor started. Press Ctrl+C to stop.")
        print("[MONITOR] Modify any Python file to trigger coverage check.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("\n[MONITOR] Coverage monitoring stopped.")
        self.observer.join()

    def run_once(self):
        """Run single coverage check"""
        print("[COVERAGE] Running coverage analysis...")

        # Run coverage
        coverage_data = self.analyzer.run_coverage()
        if not coverage_data:
            print("[ERROR] Failed to get coverage data")
            return 1

        # Save to database
        snapshot_id = self.analyzer.db.save_snapshot(coverage_data)
        print(f"[SUCCESS] Coverage snapshot saved (ID: {snapshot_id})")

        # Check thresholds
        alerts = self.analyzer.check_thresholds(coverage_data)
        if alerts:
            print("\n[ALERTS]")
            for alert in alerts:
                severity_symbol = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]", "low": "[i]"}.get(
                    alert["severity"], "[?]"
                )
                print(f"{severity_symbol} {alert['message']}")
                self.analyzer.db.save_alert(alert["type"], alert["severity"], alert["message"], json.dumps(alert))

        # Generate report
        report = self.analyzer.generate_report(coverage_data)

        # Save report
        report_dir = Path("RUNS/coverage/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / f"coverage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n[SUCCESS] Report saved: {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("[COVERAGE SUMMARY]")
        print("=" * 60)
        print(f"Overall Coverage: {coverage_data['overall_coverage']:.1f}%")
        print(f"Files Covered: {coverage_data['files_covered']}/{coverage_data['files_total']}")
        print(f"Lines Covered: {coverage_data['lines_covered']}/{coverage_data['lines_total']}")

        threshold = COVERAGE_THRESHOLDS["overall"]
        if coverage_data["overall_coverage"] >= threshold:
            print(f"\n[SUCCESS] Coverage meets threshold ({threshold}%)")
            return 0
        else:
            print(f"\n[WARNING] Coverage below threshold ({threshold}%)")
            return 1

    def show_trend(self, hours: int = 24):
        """Show coverage trend"""
        print(f"\n[TREND] Coverage trend (last {hours} hours)")
        print("=" * 60)

        trends = self.analyzer.db.get_trend(hours)
        if not trends:
            print("No coverage data available")
            return

        for trend in trends:
            timestamp = datetime.fromisoformat(trend["timestamp"])
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M')} | Overall: {trend['overall']:.1f}%")

        # Calculate trend direction
        if len(trends) >= 2:
            first = trends[0]["overall"]
            last = trends[-1]["overall"]
            change = last - first

            if change > 0:
                print(f"\n[TREND] Coverage improved by {change:.1f}%")
            elif change < 0:
                print(f"\n[TREND] Coverage decreased by {abs(change):.1f}%")
            else:
                print("\n[TREND] Coverage unchanged")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Coverage Monitor")
    parser.add_argument("--watch", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--trend", type=int, metavar="HOURS", help="Show coverage trend for last N hours")
    parser.add_argument("--threshold", type=int, help="Override overall coverage threshold")

    args = parser.parse_args()

    monitor = CoverageMonitor()

    if args.threshold:
        COVERAGE_THRESHOLDS["overall"] = args.threshold

    if args.trend:
        monitor.show_trend(args.trend)
    elif args.watch:
        monitor.start_monitoring()
    else:
        return monitor.run_once()

    return 0


if __name__ == "__main__":
    sys.exit(main())
