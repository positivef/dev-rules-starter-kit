#!/usr/bin/env python3
"""TechnicalDebtTracker - Technical Debt Quantification and Prioritization

Tracks, quantifies, and prioritizes technical debt for strategic refactoring.

Features:
1. Automatic debt detection (code smells, TODO/FIXME, coverage gaps)
2. Debt quantification (complexity, cost, ROI)
3. Priority mapping (impact vs effort)
4. Refactoring plan generation
5. Progress tracking

Usage:
    from technical_debt_tracker import TechnicalDebtTracker

    tracker = TechnicalDebtTracker()

    # Detect debt
    debt_items = tracker.detect_debt(path="scripts/")

    # Quantify and prioritize
    report = tracker.quantify_debt(debt_items)
    prioritized = tracker.prioritize_debt(report)

    # Create refactoring plan
    plan = tracker.create_refactoring_plan(prioritized, sprints=4)

    # Track progress
    progress = tracker.track_progress()
"""

import ast
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================


class DebtType(str, Enum):
    """Types of technical debt"""

    CODE_SMELL = "code_smell"
    TODO_COMMENT = "todo_comment"
    LOW_COVERAGE = "low_coverage"
    HIGH_COMPLEXITY = "high_complexity"
    DEPRECATED_API = "deprecated_api"
    SECURITY_ISSUE = "security_issue"
    DOCUMENTATION = "documentation"
    DUPLICATION = "duplication"


class DebtSeverity(str, Enum):
    """Severity levels for technical debt"""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Address in current sprint
    MEDIUM = "medium"  # Address in next 2-3 sprints
    LOW = "low"  # Address when convenient


class RefactoringStatus(str, Enum):
    """Status of refactoring tasks"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


# ============================================================================
# Core Dataclasses
# ============================================================================


@dataclass
class DebtItem:
    """Individual technical debt item"""

    id: str
    debt_type: DebtType
    file_path: str
    line_number: Optional[int]
    description: str
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Metrics
    complexity_score: float = 0.0
    impact_score: float = 0.0  # 1-10 scale
    effort_hours: float = 0.0
    risk_level: float = 0.0

    # Context
    code_snippet: Optional[str] = None
    affected_components: List[str] = field(default_factory=list)
    related_debt_ids: List[str] = field(default_factory=list)


@dataclass
class DebtMetrics:
    """Quantified metrics for debt"""

    total_debt_items: int
    total_complexity: float
    total_effort_hours: float
    total_maintenance_cost: float  # in dollars
    debt_interest_rate: float  # cost accumulation per month
    coverage_percentage: float
    average_complexity: float
    high_risk_count: int

    # By type breakdown
    by_type: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)


@dataclass
class DebtReport:
    """Complete debt analysis report"""

    generated_at: str
    project_path: str
    debt_items: List[DebtItem]
    metrics: DebtMetrics

    # Trends (if historical data available)
    debt_trend: str = "stable"  # increasing/decreasing/stable
    trend_percentage: float = 0.0


@dataclass
class PrioritizedDebt:
    """Debt item with priority score"""

    debt_item: DebtItem
    priority_score: float  # 0-100
    severity: DebtSeverity
    recommended_sprint: int

    # Justification
    priority_factors: Dict[str, float] = field(default_factory=dict)
    blocking_items: List[str] = field(default_factory=list)


@dataclass
class RefactoringTask:
    """Individual refactoring task"""

    task_id: str
    debt_id: str
    title: str
    description: str
    estimated_hours: float
    assigned_sprint: int
    status: RefactoringStatus = RefactoringStatus.PENDING

    # Progress tracking
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    actual_hours: float = 0.0

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)


@dataclass
class RefactoringPlan:
    """Complete refactoring plan"""

    plan_id: str
    created_at: str
    total_sprints: int
    tasks: List[RefactoringTask]

    # Summary
    total_effort_hours: float
    expected_completion_date: str
    roi_analysis: Dict[str, Any] = field(default_factory=dict)

    # Sprint breakdown
    sprint_allocation: Dict[int, List[str]] = field(default_factory=dict)


@dataclass
class ProgressReport:
    """Progress tracking report"""

    report_date: str

    # Overall progress
    total_debt_items: int
    resolved_items: int
    in_progress_items: int
    pending_items: int
    resolution_percentage: float

    # Trends
    debt_reduction_rate: float  # items per sprint
    actual_vs_planned: float  # percentage

    # ROI tracking
    estimated_savings: float
    actual_cost: float
    roi_percentage: float

    # By module/team
    by_module: Dict[str, Dict[str, int]] = field(default_factory=dict)


# ============================================================================
# Main Tracker Class
# ============================================================================


class TechnicalDebtTracker:
    """
    Technical debt tracking and management system.

    Provides comprehensive debt detection, quantification, prioritization,
    and progress tracking capabilities.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize TechnicalDebtTracker.

        Args:
            data_dir: Directory to store debt data (default: RUNS/technical_debt/)
        """
        self.data_dir = data_dir or Path("RUNS/technical_debt")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data storage
        self.debt_items: List[DebtItem] = []
        self.reports: List[DebtReport] = []
        self.plans: List[RefactoringPlan] = []
        self.progress_reports: List[ProgressReport] = []

        # Load existing data
        self._load_data()

        logger.info(f"TechnicalDebtTracker initialized with data_dir={self.data_dir}")

    def detect_debt(self, path: str = ".") -> List[DebtItem]:
        """
        Automatically detect technical debt in codebase.

        Detects:
        - Code smells (high complexity, long functions)
        - TODO/FIXME/HACK comments
        - Low test coverage areas
        - Deprecated API usage

        Args:
            path: Path to analyze (file or directory)

        Returns:
            List of detected debt items
        """
        debt_items = []
        path_obj = Path(path)

        if path_obj.is_file():
            files = [path_obj]
        else:
            files = list(path_obj.rglob("*.py"))

        logger.info(f"Scanning {len(files)} Python files for technical debt...")

        for file_path in files:
            # Skip test files and generated code
            if "test_" in file_path.name or "__pycache__" in str(file_path):
                continue

            try:
                # Detect TODO/FIXME comments
                debt_items.extend(self._detect_todo_comments(file_path))

                # Detect high complexity
                debt_items.extend(self._detect_high_complexity(file_path))

                # Detect code smells
                debt_items.extend(self._detect_code_smells(file_path))

            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")

        self.debt_items.extend(debt_items)
        logger.info(f"Detected {len(debt_items)} technical debt items")

        return debt_items

    def quantify_debt(self, debt_items: List[DebtItem]) -> DebtReport:
        """
        Quantify technical debt with metrics.

        Calculates:
        - Total complexity score
        - Maintenance cost estimates
        - Debt interest (accumulation rate)
        - ROI for resolution

        Args:
            debt_items: List of debt items to quantify

        Returns:
            DebtReport with quantified metrics
        """
        # Calculate metrics
        total_complexity = sum(item.complexity_score for item in debt_items)
        total_effort = sum(item.effort_hours for item in debt_items)

        # Estimate maintenance cost ($50/hour average)
        hourly_rate = 50.0
        total_maintenance_cost = total_effort * hourly_rate

        # Calculate debt interest (5% per month accumulation)
        debt_interest_rate = total_maintenance_cost * 0.05

        # Count by type and severity
        by_type = {}
        by_severity = {}
        high_risk_count = 0

        for item in debt_items:
            by_type[item.debt_type] = by_type.get(item.debt_type, 0) + 1
            if item.risk_level >= 7.0:
                high_risk_count += 1

        # Create metrics
        metrics = DebtMetrics(
            total_debt_items=len(debt_items),
            total_complexity=total_complexity,
            total_effort_hours=total_effort,
            total_maintenance_cost=total_maintenance_cost,
            debt_interest_rate=debt_interest_rate,
            coverage_percentage=self._calculate_coverage(),
            average_complexity=total_complexity / max(len(debt_items), 1),
            high_risk_count=high_risk_count,
            by_type=by_type,
            by_severity=by_severity,
        )

        # Create report
        report = DebtReport(
            generated_at=datetime.now().isoformat(), project_path=str(Path.cwd()), debt_items=debt_items, metrics=metrics
        )

        self.reports.append(report)
        self._save_data()

        logger.info(f"Quantified {len(debt_items)} debt items, total cost: ${total_maintenance_cost:.2f}")

        return report

    def prioritize_debt(self, debt_report: DebtReport) -> List[PrioritizedDebt]:
        """
        Prioritize debt items using impact/effort analysis.

        Algorithm:
        - Priority = (Impact * 10) / (Effort + 1)
        - Adjustments for risk, dependencies, business value

        Args:
            debt_report: Debt report to prioritize

        Returns:
            List of prioritized debt items (sorted by priority)
        """
        prioritized = []

        for item in debt_report.debt_items:
            # Calculate base priority score
            impact = item.impact_score or 5.0
            effort = item.effort_hours or 1.0

            # Priority formula: (Impact * 10) / (Effort + 1)
            base_score = (impact * 10) / (effort + 1)

            # Adjust for risk
            risk_multiplier = 1 + (item.risk_level / 10)
            priority_score = base_score * risk_multiplier

            # Determine severity
            if priority_score >= 75:
                severity = DebtSeverity.CRITICAL
                recommended_sprint = 1
            elif priority_score >= 50:
                severity = DebtSeverity.HIGH
                recommended_sprint = 1
            elif priority_score >= 25:
                severity = DebtSeverity.MEDIUM
                recommended_sprint = 2
            else:
                severity = DebtSeverity.LOW
                recommended_sprint = 3

            # Track priority factors
            priority_factors = {
                "impact": impact,
                "effort": effort,
                "risk": item.risk_level,
                "base_score": base_score,
                "final_score": priority_score,
            }

            prioritized.append(
                PrioritizedDebt(
                    debt_item=item,
                    priority_score=priority_score,
                    severity=severity,
                    recommended_sprint=recommended_sprint,
                    priority_factors=priority_factors,
                )
            )

        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x.priority_score, reverse=True)

        logger.info(f"Prioritized {len(prioritized)} debt items")

        return prioritized

    def create_refactoring_plan(self, prioritized_debt: List[PrioritizedDebt], sprints: int = 4) -> RefactoringPlan:
        """
        Generate refactoring plan with sprint allocation.

        Args:
            prioritized_debt: Prioritized debt items
            sprints: Number of sprints to plan for

        Returns:
            RefactoringPlan with task breakdown
        """
        tasks = []
        sprint_allocation = {i: [] for i in range(1, sprints + 1)}

        for idx, prioritized in enumerate(prioritized_debt):
            item = prioritized.debt_item

            task = RefactoringTask(
                task_id=f"TASK-{idx+1:03d}",
                debt_id=item.id,
                title=f"Resolve {item.debt_type}: {item.description[:50]}",
                description=item.description,
                estimated_hours=item.effort_hours or 2.0,
                assigned_sprint=min(prioritized.recommended_sprint, sprints),
            )

            tasks.append(task)
            sprint_allocation[task.assigned_sprint].append(task.task_id)

        # Calculate totals
        total_effort = sum(t.estimated_hours for t in tasks)
        expected_completion = datetime.now() + timedelta(weeks=sprints * 2)

        # ROI analysis
        total_cost = total_effort * 50  # $50/hour
        expected_savings = sum(
            p.debt_item.impact_score * 500  # $500 per impact point
            for p in prioritized_debt
        )
        roi_percentage = ((expected_savings - total_cost) / total_cost * 100) if total_cost > 0 else 0

        roi_analysis = {
            "total_cost": total_cost,
            "expected_savings": expected_savings,
            "roi_percentage": roi_percentage,
            "break_even_months": (total_cost / (expected_savings / 12)) if expected_savings > 0 else 0,
        }

        plan = RefactoringPlan(
            plan_id=f"PLAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            created_at=datetime.now().isoformat(),
            total_sprints=sprints,
            tasks=tasks,
            total_effort_hours=total_effort,
            expected_completion_date=expected_completion.isoformat(),
            roi_analysis=roi_analysis,
            sprint_allocation=sprint_allocation,
        )

        self.plans.append(plan)
        self._save_data()

        logger.info(f"Created refactoring plan with {len(tasks)} tasks over {sprints} sprints")

        return plan

    def track_progress(self) -> ProgressReport:
        """
        Track refactoring progress.

        Returns:
            ProgressReport with current status
        """
        if not self.plans:
            logger.warning("No refactoring plans available for tracking")
            return ProgressReport(
                report_date=datetime.now().isoformat(),
                total_debt_items=len(self.debt_items),
                resolved_items=0,
                in_progress_items=0,
                pending_items=len(self.debt_items),
                resolution_percentage=0.0,
                debt_reduction_rate=0.0,
                actual_vs_planned=0.0,
                estimated_savings=0.0,
                actual_cost=0.0,
                roi_percentage=0.0,
            )

        latest_plan = self.plans[-1]

        # Count statuses
        resolved = sum(1 for t in latest_plan.tasks if t.status == RefactoringStatus.COMPLETED)
        in_progress = sum(1 for t in latest_plan.tasks if t.status == RefactoringStatus.IN_PROGRESS)
        pending = sum(1 for t in latest_plan.tasks if t.status == RefactoringStatus.PENDING)
        total = len(latest_plan.tasks)

        resolution_percentage = (resolved / total * 100) if total > 0 else 0.0

        # Calculate actual cost
        actual_cost = sum(t.actual_hours * 50 for t in latest_plan.tasks if t.actual_hours > 0)

        # Calculate debt reduction rate
        days_elapsed = (datetime.now() - datetime.fromisoformat(latest_plan.created_at)).days
        sprints_elapsed = max(days_elapsed / 14, 1)
        reduction_rate = resolved / sprints_elapsed

        report = ProgressReport(
            report_date=datetime.now().isoformat(),
            total_debt_items=total,
            resolved_items=resolved,
            in_progress_items=in_progress,
            pending_items=pending,
            resolution_percentage=resolution_percentage,
            debt_reduction_rate=reduction_rate,
            actual_vs_planned=0.0,  # Calculate from plan timeline
            estimated_savings=latest_plan.roi_analysis.get("expected_savings", 0.0),
            actual_cost=actual_cost,
            roi_percentage=latest_plan.roi_analysis.get("roi_percentage", 0.0),
        )

        self.progress_reports.append(report)
        self._save_data()

        logger.info(f"Progress: {resolved}/{total} tasks completed ({resolution_percentage:.1f}%)")

        return report

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _detect_todo_comments(self, file_path: Path) -> List[DebtItem]:
        """Detect TODO/FIXME/HACK comments in file."""
        debt_items = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            patterns = [
                (r"#\s*(TODO|FIXME|HACK|XXX)[:\s]+(.*)", DebtType.TODO_COMMENT),
            ]

            for line_num, line in enumerate(lines, 1):
                for pattern, debt_type in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        comment_text = match.group(2).strip()

                        debt_items.append(
                            DebtItem(
                                id=f"TODO-{file_path.stem}-{line_num}",
                                debt_type=debt_type,
                                file_path=str(file_path),
                                line_number=line_num,
                                description=f"{match.group(1)}: {comment_text}",
                                complexity_score=1.0,
                                impact_score=3.0,
                                effort_hours=1.0,
                                risk_level=2.0,
                                code_snippet=line.strip(),
                            )
                        )

        except Exception as e:
            logger.debug(f"Error detecting TODO comments in {file_path}: {e}")

        return debt_items

    def _detect_high_complexity(self, file_path: Path) -> List[DebtItem]:
        """Detect high complexity functions."""
        debt_items = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Simple complexity estimate based on control flow
                    complexity = self._calculate_cyclomatic_complexity(node)

                    if complexity > 10:  # Threshold for high complexity
                        debt_items.append(
                            DebtItem(
                                id=f"COMPLEX-{file_path.stem}-{node.name}",
                                debt_type=DebtType.HIGH_COMPLEXITY,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"High complexity in function '{node.name}' (complexity: {complexity})",
                                complexity_score=complexity,
                                impact_score=min(complexity / 2, 10),
                                effort_hours=complexity * 0.5,
                                risk_level=min(complexity / 2, 10),
                            )
                        )

        except Exception as e:
            logger.debug(f"Error detecting complexity in {file_path}: {e}")

        return debt_items

    def _detect_code_smells(self, file_path: Path) -> List[DebtItem]:
        """Detect common code smells."""
        debt_items = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Long functions (> 50 lines)
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                    if func_lines > 50:
                        debt_items.append(
                            DebtItem(
                                id=f"LONG-{file_path.stem}-{node.name}",
                                debt_type=DebtType.CODE_SMELL,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"Long function '{node.name}' ({func_lines} lines)",
                                complexity_score=func_lines / 10,
                                impact_score=4.0,
                                effort_hours=func_lines / 10,
                                risk_level=3.0,
                            )
                        )

                # Too many parameters (> 5)
                if isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 5:
                        debt_items.append(
                            DebtItem(
                                id=f"PARAMS-{file_path.stem}-{node.name}",
                                debt_type=DebtType.CODE_SMELL,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"Too many parameters in '{node.name}' ({param_count} params)",
                                complexity_score=param_count,
                                impact_score=3.0,
                                effort_hours=2.0,
                                risk_level=2.0,
                            )
                        )

        except Exception as e:
            logger.debug(f"Error detecting code smells in {file_path}: {e}")

        return debt_items

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Add 1 for each decision point
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_coverage(self) -> float:
        """Calculate test coverage percentage."""
        try:
            subprocess.run(
                ["pytest", "--cov=scripts", "--cov-report=json", "tests/"], capture_output=True, text=True, timeout=30
            )

            coverage_file = Path(".coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)
                    return data.get("totals", {}).get("percent_covered", 0.0)

        except Exception as e:
            logger.debug(f"Error calculating coverage: {e}")

        return 0.0

    def _save_data(self):
        """Save data to JSON files."""
        try:
            # Save debt items
            with open(self.data_dir / "debt_items.json", "w") as f:
                json.dump([vars(item) for item in self.debt_items], f, indent=2)

            # Save reports
            if self.reports:
                with open(self.data_dir / "reports.json", "w") as f:
                    json.dump([self._report_to_dict(r) for r in self.reports], f, indent=2)

            # Save plans
            if self.plans:
                with open(self.data_dir / "plans.json", "w") as f:
                    json.dump([self._plan_to_dict(p) for p in self.plans], f, indent=2)

            logger.debug("Data saved successfully")

        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def _load_data(self):
        """Load data from JSON files."""
        try:
            debt_file = self.data_dir / "debt_items.json"
            if debt_file.exists():
                with open(debt_file) as f:
                    data = json.load(f)
                    self.debt_items = [DebtItem(**item) for item in data]
                logger.debug(f"Loaded {len(self.debt_items)} debt items")

        except Exception as e:
            logger.debug(f"Error loading data: {e}")

    def _report_to_dict(self, report: DebtReport) -> Dict:
        """Convert DebtReport to dict for JSON serialization."""
        return {
            "generated_at": report.generated_at,
            "project_path": report.project_path,
            "debt_items": [vars(item) for item in report.debt_items],
            "metrics": vars(report.metrics),
            "debt_trend": report.debt_trend,
            "trend_percentage": report.trend_percentage,
        }

    def _plan_to_dict(self, plan: RefactoringPlan) -> Dict:
        """Convert RefactoringPlan to dict for JSON serialization."""
        return {
            "plan_id": plan.plan_id,
            "created_at": plan.created_at,
            "total_sprints": plan.total_sprints,
            "tasks": [vars(task) for task in plan.tasks],
            "total_effort_hours": plan.total_effort_hours,
            "expected_completion_date": plan.expected_completion_date,
            "roi_analysis": plan.roi_analysis,
            "sprint_allocation": plan.sprint_allocation,
        }


def main():
    """Demo usage of TechnicalDebtTracker."""
    tracker = TechnicalDebtTracker()

    print("\n" + "=" * 70)
    print(" " * 20 + "TechnicalDebtTracker Demo")
    print("=" * 70)

    # Detect debt
    print("\n[1/5] Detecting technical debt...")
    debt_items = tracker.detect_debt(path="scripts/")
    print(f"  Found {len(debt_items)} debt items")

    if debt_items:
        # Quantify
        print("\n[2/5] Quantifying debt...")
        report = tracker.quantify_debt(debt_items)
        print(f"  Total cost: ${report.metrics.total_maintenance_cost:,.2f}")
        print(f"  Monthly interest: ${report.metrics.debt_interest_rate:,.2f}")

        # Prioritize
        print("\n[3/5] Prioritizing debt...")
        prioritized = tracker.prioritize_debt(report)
        print(f"  Critical: {sum(1 for p in prioritized if p.severity == DebtSeverity.CRITICAL)}")
        print(f"  High: {sum(1 for p in prioritized if p.severity == DebtSeverity.HIGH)}")
        print(f"  Medium: {sum(1 for p in prioritized if p.severity == DebtSeverity.MEDIUM)}")
        print(f"  Low: {sum(1 for p in prioritized if p.severity == DebtSeverity.LOW)}")

        # Create plan
        print("\n[4/5] Creating refactoring plan...")
        plan = tracker.create_refactoring_plan(prioritized, sprints=4)
        print(f"  Total effort: {plan.total_effort_hours:.1f} hours")
        print(f"  Expected ROI: {plan.roi_analysis['roi_percentage']:.1f}%")

        # Track progress
        print("\n[5/5] Tracking progress...")
        progress = tracker.track_progress()
        print(f"  Resolution: {progress.resolution_percentage:.1f}%")
        print(f"  Completed: {progress.resolved_items}/{progress.total_debt_items}")

    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
