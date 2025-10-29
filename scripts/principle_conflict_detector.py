#!/usr/bin/env python3
"""
Principle Conflict Detector (P11 Automation)

Automatically detects when new changes conflict with past decisions or existing principles.
Uses Git history, session memory, and constitutional analysis to identify conflicts.

Constitution Article P11: 원칙 충돌 검증
"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ConflictDetection:
    """Structure for detected conflicts."""

    conflict_type: str
    past_decision: str
    past_date: str
    new_proposal: str
    conflict_point: str
    severity: str  # critical, high, medium, low
    git_reference: Optional[str] = None
    resolution_options: List[Dict] = None


class PrincipleConflictDetector:
    """Automated detector for principle conflicts (P11)."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.constitution_path = self.project_root / "config" / "constitution.yaml"
        self.evidence_dir = self.project_root / "RUNS" / "evidence"
        self.conflict_log = self.project_root / "RUNS" / "conflict_detection.json"

        # Conflict trigger patterns
        self.trigger_patterns = {
            "layer_addition": r"(?i)(add|create|implement).*(layer|tier)",
            "architecture_change": r"(?i)(change|modify|refactor).*(architecture|structure)",
            "tool_role_change": r"(?i)(change|update|modify).*(tool|role|responsibility)",
            "constitution_interpretation": r"(?i)(interpret|redefine|clarify).*(constitution|article|principle)",
            "concept_redefinition": r"(?i)(redefine|change|update).*(concept|core|fundamental)",
            "dashboard_focus": r"(?i)(dashboard|ui|interface).*(main|primary|focus)",
            "scope_expansion": r"(?i)(expand|add|include).*(scope|feature|functionality)",
        }

        # Load past decisions from Git history
        self.past_decisions = self._load_past_decisions()

    def _load_past_decisions(self) -> List[Dict]:
        """Load past decisions from Git history and evidence."""
        decisions = []

        # Load from Git commit messages
        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H|%ad|%s", "--date=short", "-100"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split("|", 2)
                        if len(parts) == 3:
                            commit_hash, date, message = parts
                            decisions.append(
                                {
                                    "source": "git",
                                    "hash": commit_hash,
                                    "date": date,
                                    "message": message,
                                    "type": self._classify_decision(message),
                                }
                            )
        except Exception as e:
            print(f"[WARN] Could not load Git history: {e}")

        # Load from evidence files
        if self.evidence_dir.exists():
            for evidence_file in self.evidence_dir.glob("**/*.json"):
                try:
                    with open(evidence_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "decisions" in data:
                            decisions.extend(data["decisions"])
                except:
                    pass

        return decisions

    def _classify_decision(self, message: str) -> str:
        """Classify decision type based on message content."""
        message_lower = message.lower()

        if "constitution" in message_lower:
            return "constitutional"
        elif "architecture" in message_lower or "layer" in message_lower:
            return "architectural"
        elif "dashboard" in message_lower or "ui" in message_lower:
            return "interface"
        elif "tool" in message_lower or "executor" in message_lower:
            return "tooling"
        elif "feat" in message_lower:
            return "feature"
        else:
            return "general"

    def detect_conflicts(self, proposal: str, context: Dict = None) -> List[ConflictDetection]:
        """
        Detect conflicts between proposal and past decisions.

        Args:
            proposal: Description of proposed change
            context: Additional context (files changed, scope, etc.)

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check against trigger patterns
        triggered = False
        trigger_type = None

        for pattern_name, pattern in self.trigger_patterns.items():
            if re.search(pattern, proposal):
                triggered = True
                trigger_type = pattern_name
                break

        if not triggered:
            return conflicts

        # Analyze specific conflict types
        if trigger_type == "dashboard_focus":
            conflicts.append(self._check_dashboard_conflict(proposal))

        if trigger_type == "layer_addition":
            conflicts.append(self._check_layer_conflict(proposal))

        if trigger_type == "architecture_change":
            conflicts.append(self._check_architecture_conflict(proposal))

        # Check against past decisions
        for decision in self.past_decisions:
            conflict = self._compare_with_decision(proposal, decision)
            if conflict:
                conflicts.append(conflict)

        # Filter out None values
        conflicts = [c for c in conflicts if c is not None]

        # Log conflicts
        if conflicts:
            self._log_conflicts(conflicts)

        return conflicts

    def _check_dashboard_conflict(self, proposal: str) -> Optional[ConflictDetection]:
        """Check for dashboard focus conflicts (learned from past experience)."""
        if "main" in proposal.lower() or "primary" in proposal.lower():
            return ConflictDetection(
                conflict_type="focus_shift",
                past_decision="This project is Constitution-centered development system, not dashboard-focused",
                past_date="2025-10-20",
                new_proposal=proposal,
                conflict_point="Dashboard being treated as main product instead of Constitution enforcement",
                severity="high",
                resolution_options=[
                    {
                        "option": "A",
                        "description": "Add dashboard as Layer 7 visualization with clear boundaries",
                        "pros": ["Visual feedback", "Better UX"],
                        "cons": ["Risk of focus shift", "Added complexity"],
                    },
                    {
                        "option": "B",
                        "description": "Keep dashboard minimal or external",
                        "pros": ["Maintains Constitution focus", "Simpler"],
                        "cons": ["Less visual feedback", "Harder monitoring"],
                    },
                ],
            )
        return None

    def _check_layer_conflict(self, proposal: str) -> Optional[ConflictDetection]:
        """Check for layer/architecture conflicts."""
        if "layer 8" in proposal.lower() or "layer 9" in proposal.lower():
            return ConflictDetection(
                conflict_type="architecture_expansion",
                past_decision="7-layer architecture is the defined structure",
                past_date="2025-10-23",
                new_proposal=proposal,
                conflict_point="Adding layers beyond the 7-layer architecture",
                severity="medium",
                resolution_options=[
                    {
                        "option": "A",
                        "description": "Expand to 8+ layers with Constitution amendment",
                        "pros": ["More flexibility", "Room for growth"],
                        "cons": ["Complexity increase", "Constitution change needed"],
                    },
                    {
                        "option": "B",
                        "description": "Fit within existing 7 layers",
                        "pros": ["Maintains simplicity", "No Constitution change"],
                        "cons": ["May feel constrained", "Less granular"],
                    },
                ],
            )
        return None

    def _check_architecture_conflict(self, proposal: str) -> Optional[ConflictDetection]:
        """Check for architecture principle conflicts."""
        # Check if proposal violates core architecture principles
        violations = []

        if "bypass" in proposal.lower() or "skip" in proposal.lower():
            violations.append("Attempting to bypass constitutional gates")

        if "direct" in proposal.lower() and "database" in proposal.lower():
            violations.append("Direct database access violates layer separation")

        if violations:
            return ConflictDetection(
                conflict_type="architectural_violation",
                past_decision="All operations must go through proper layers and gates",
                past_date="2025-10-23",
                new_proposal=proposal,
                conflict_point="; ".join(violations),
                severity="critical",
                resolution_options=[
                    {
                        "option": "A",
                        "description": "Follow proper layer architecture",
                        "pros": ["Maintains integrity", "Consistent"],
                        "cons": ["May be slower", "More complex"],
                    },
                    {
                        "option": "B",
                        "description": "Create exception with documentation",
                        "pros": ["Faster for specific case", "Pragmatic"],
                        "cons": ["Sets precedent", "Technical debt"],
                    },
                ],
            )
        return None

    def _compare_with_decision(self, proposal: str, decision: Dict) -> Optional[ConflictDetection]:
        """Compare proposal with a specific past decision."""
        # Simple keyword-based conflict detection
        decision_keywords = set(decision["message"].lower().split())
        proposal_keywords = set(proposal.lower().split())

        # Check for contradictions
        contradiction_pairs = [
            ("centralized", "distributed"),
            ("monolithic", "microservices"),
            ("sync", "async"),
            ("strict", "flexible"),
            ("mandatory", "optional"),
        ]

        for word1, word2 in contradiction_pairs:
            if word1 in decision_keywords and word2 in proposal_keywords:
                return ConflictDetection(
                    conflict_type="keyword_contradiction",
                    past_decision=decision["message"],
                    past_date=decision["date"],
                    new_proposal=proposal,
                    conflict_point=f"Past: {word1}, Now: {word2}",
                    severity="medium",
                    git_reference=decision.get("hash"),
                )
            elif word2 in decision_keywords and word1 in proposal_keywords:
                return ConflictDetection(
                    conflict_type="keyword_contradiction",
                    past_decision=decision["message"],
                    past_date=decision["date"],
                    new_proposal=proposal,
                    conflict_point=f"Past: {word2}, Now: {word1}",
                    severity="medium",
                    git_reference=decision.get("hash"),
                )

        return None

    def _log_conflicts(self, conflicts: List[ConflictDetection]):
        """Log detected conflicts to file."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "conflicts": [
                {
                    "type": c.conflict_type,
                    "past_decision": c.past_decision,
                    "past_date": c.past_date,
                    "new_proposal": c.new_proposal,
                    "conflict_point": c.conflict_point,
                    "severity": c.severity,
                    "git_reference": c.git_reference,
                    "resolution_options": c.resolution_options,
                }
                for c in conflicts
            ],
        }

        # Append to log file
        existing_logs = []
        if self.conflict_log.exists():
            try:
                with open(self.conflict_log, "r", encoding="utf-8") as f:
                    existing_logs = json.load(f)
            except:
                existing_logs = []

        existing_logs.append(log_data)

        # Keep only last 100 entries
        existing_logs = existing_logs[-100:]

        with open(self.conflict_log, "w", encoding="utf-8") as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)

    def generate_conflict_report(self, conflicts: List[ConflictDetection]) -> str:
        """Generate human-readable conflict report following P11 format."""
        if not conflicts:
            return "[OK] No principle conflicts detected"

        report = []
        report.append("[WARN] Principle Conflict Detection (P11)")
        report.append("=" * 60)

        for i, conflict in enumerate(conflicts, 1):
            report.append(f"\n{i}. {conflict.conflict_type.upper()}")
            report.append(f"   Severity: {conflict.severity}")
            report.append(f"   Past Decision ({conflict.past_date}):")
            report.append(f"   '{conflict.past_decision}'")

            if conflict.git_reference:
                report.append(f"   Git Reference: {conflict.git_reference[:8]}")

            report.append("\n   New Proposal:")
            report.append(f"   '{conflict.new_proposal}'")

            report.append("\n   Conflict Point:")
            report.append(f"   {conflict.conflict_point}")

            if conflict.resolution_options:
                report.append("\n   Resolution Options:")
                for opt in conflict.resolution_options:
                    report.append(f"\n   Option {opt['option']}: {opt['description']}")
                    if "pros" in opt:
                        report.append(f"   Pros: {', '.join(opt['pros'])}")
                    if "cons" in opt:
                        report.append(f"   Cons: {', '.join(opt['cons'])}")

        report.append("\n" + "=" * 60)
        report.append("[ACTION REQUIRED] Please review conflicts and choose resolution")

        return "\n".join(report)


def main():
    """Test the principle conflict detector."""
    detector = PrincipleConflictDetector()

    # Test cases
    test_proposals = [
        "Let's make the Streamlit dashboard the main interface",
        "Add Layer 8 for advanced monitoring",
        "Change the architecture to bypass TaskExecutor",
        "Redefine the core concept to focus on UI",
        "Update tool roles to skip constitutional validation",
    ]

    print("Principle Conflict Detector (P11 Automation)")
    print("=" * 60)

    for proposal in test_proposals:
        print(f"\nTesting: {proposal}")
        print("-" * 40)

        conflicts = detector.detect_conflicts(proposal)
        report = detector.generate_conflict_report(conflicts)
        print(report)
        print()


if __name__ == "__main__":
    main()
