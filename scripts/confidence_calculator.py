"""
Confidence Calculator - Determines solution reliability scores

Calculates confidence scores (0.0-1.0) for error solutions based on:
- Pattern matching
- Command safety
- Source reliability
- Complexity analysis

Safety Features:
- Conservative defaults (70% base)
- Dangerous pattern detection
- Circuit breaker integration
- Explainable scores

Usage:
    from scripts.confidence_calculator import ConfidenceCalculator

    calc = ConfidenceCalculator()
    confidence, explanation = calc.calculate(
        error_msg="ModuleNotFoundError: No module named 'pandas'",
        solution="pip install pandas",
        context={"library": "pandas"}
    )

    print(f"Confidence: {confidence:.0%}")
    print(f"Reasoning: {explanation}")
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level categories"""

    HIGH = "high"  # >= auto_apply threshold
    MEDIUM = "medium"  # >= ask_confirm threshold
    LOW = "low"  # < ask_confirm threshold


@dataclass
class ConfidenceExplanation:
    """Breakdown of confidence calculation"""

    base_score: float
    modifiers: List[Tuple[str, float]]  # (reason, delta)
    final_score: float
    level: ConfidenceLevel

    def __str__(self) -> str:
        """Human-readable explanation"""
        lines = [f"Confidence: {self.final_score:.0%} ({self.level.value.upper()})"]
        lines.append(f"Base score: {self.base_score:.0%}")

        if self.modifiers:
            lines.append("Modifiers:")
            for reason, delta in self.modifiers:
                sign = "+" if delta >= 0 else ""
                lines.append(f"  {sign}{delta:.0%}: {reason}")

        return "\n".join(lines)


class ConfidenceCalculator:
    """
    Calculate confidence scores for error solutions

    Thread-safe, stateless calculator that uses configuration
    to determine how reliable a proposed solution is.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize confidence calculator

        Args:
            config_path: Path to error_resolution_config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "error_resolution_config.yaml"

        self.config = self._load_config(config_path)

        # Extract thresholds
        thresholds = self.config.get("confidence_thresholds", {})
        self.auto_apply_threshold = thresholds.get("auto_apply", 0.95)
        self.ask_confirm_threshold = thresholds.get("ask_confirm", 0.70)

    def _load_config(self, config_path) -> Dict:
        """Load configuration from YAML"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] Failed to load config: {e}, using defaults")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Fallback configuration if file not available"""
        return {
            "confidence_thresholds": {"auto_apply": 0.95, "ask_confirm": 0.70},
            "confidence_modifiers": {
                "bonus": {
                    "whitelist_command": 0.10,
                    "simple_solution": 0.05,
                },
                "penalty": {
                    "system_wide": -0.15,
                    "complex_config": -0.10,
                },
            },
            "auto_apply_patterns": [],
            "always_confirm_patterns": [],
        }

    def calculate(
        self, error_msg: str, solution: str, context: Optional[Dict] = None
    ) -> Tuple[float, ConfidenceExplanation]:
        """
        Calculate confidence score for a solution

        Args:
            error_msg: Original error message
            solution: Proposed solution
            context: Additional context (library, tool, etc.)

        Returns:
            Tuple of (confidence_score, explanation)
        """
        context = context or {}

        # Start with base score from pattern matching
        base_score = self._get_base_score(error_msg, solution, context)

        # Apply modifiers
        modifiers = []

        # Check whitelists/blacklists
        if self._is_whitelisted(solution):
            modifiers.append(("Whitelisted safe pattern", 0.10))

        if self._is_blacklisted(solution):
            modifiers.append(("Blacklisted dangerous pattern", -0.30))

        # Analyze solution complexity
        complexity_mods = self._analyze_complexity(solution)
        modifiers.extend(complexity_mods)

        # Analyze solution safety
        safety_mods = self._analyze_safety(solution)
        modifiers.extend(safety_mods)

        # Calculate final score
        final_score = base_score + sum(delta for _, delta in modifiers)
        final_score = max(0.0, min(1.0, final_score))  # Clamp to [0, 1]

        # Determine level
        level = self._get_level(final_score)

        explanation = ConfidenceExplanation(base_score=base_score, modifiers=modifiers, final_score=final_score, level=level)

        return final_score, explanation

    def _get_base_score(self, error_msg: str, solution: str, context: Dict) -> float:
        """Determine base confidence from error pattern matching"""
        pattern_conf = self.config.get("pattern_confidence", {})

        # Try high confidence patterns first
        for pattern_dict in pattern_conf.get("high_confidence", []):
            if re.search(pattern_dict["pattern"], error_msg, re.IGNORECASE):
                return pattern_dict["base_score"]

        # Try medium confidence patterns
        for pattern_dict in pattern_conf.get("medium_confidence", []):
            if re.search(pattern_dict["pattern"], error_msg, re.IGNORECASE):
                return pattern_dict["base_score"]

        # Try low confidence patterns
        for pattern_dict in pattern_conf.get("low_confidence", []):
            if re.search(pattern_dict["pattern"], error_msg, re.IGNORECASE):
                return pattern_dict["base_score"]

        # Default: conservative medium-low score
        return 0.65

    def _is_whitelisted(self, solution: str) -> bool:
        """Check if solution matches auto-apply whitelist"""
        whitelist = self.config.get("auto_apply_patterns", [])
        solution_lower = solution.lower().strip()

        for pattern in whitelist:
            if pattern.lower() in solution_lower:
                return True

        return False

    def _is_blacklisted(self, solution: str) -> bool:
        """Check if solution contains dangerous patterns"""
        blacklist = self.config.get("always_confirm_patterns", [])
        solution_lower = solution.lower()

        for pattern in blacklist:
            if pattern.lower() in solution_lower:
                return True

        return False

    def _analyze_complexity(self, solution: str) -> List[Tuple[str, float]]:
        """Analyze solution complexity and return modifiers"""
        modifiers = []
        bonus = self.config.get("confidence_modifiers", {}).get("bonus", {})
        penalty = self.config.get("confidence_modifiers", {}).get("penalty", {})

        # Simple solution (single line, single command)
        if "\n" not in solution.strip() and len(solution.split()) <= 5:
            if "simple_solution" in bonus:
                modifiers.append(("Simple single command", bonus["simple_solution"]))
        else:
            # Multiple steps
            if "multiple_steps" in penalty:
                modifiers.append(("Multi-step solution", penalty["multiple_steps"]))

        return modifiers

    def _analyze_safety(self, solution: str) -> List[Tuple[str, float]]:
        """Analyze solution safety and return modifiers"""
        modifiers = []
        penalty = self.config.get("confidence_modifiers", {}).get("penalty", {})
        solution_lower = solution.lower()

        # System-wide changes
        if any(keyword in solution_lower for keyword in ["sudo", "registry", "system-wide"]):
            if "system_wide" in penalty:
                modifiers.append(("System-wide changes", penalty["system_wide"]))

        # Data modification
        if any(keyword in solution_lower for keyword in ["delete", "drop", "remove", "rm"]):
            if "data_modification" in penalty:
                modifiers.append(("Data modification risk", penalty["data_modification"]))

        # Irreversible operations
        if "rm -rf" in solution_lower or "drop table" in solution_lower:
            if "irreversible" in penalty:
                modifiers.append(("Irreversible operation", penalty["irreversible"]))

        return modifiers

    def _get_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score"""
        if score >= self.auto_apply_threshold:
            return ConfidenceLevel.HIGH
        elif score >= self.ask_confirm_threshold:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW


# Circuit Breaker for tracking failures
class CircuitBreaker:
    """
    Track auto-apply failures and disable if too many errors

    Safety mechanism to prevent repeated wrong auto-applications.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize circuit breaker"""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

        if not self.enabled:
            return

        self.max_failures = self.config.get("max_failures", 3)
        self.failure_window = self.config.get("failure_window", 10)
        self.max_rejections = self.config.get("max_rejections", 5)
        self.rejection_window = self.config.get("rejection_window", 10)

        # State
        self.recent_results = []  # List of (success: bool, timestamp)
        self.recent_confirmations = []  # List of (accepted: bool, timestamp)
        self.is_open = False  # Circuit open = auto-apply disabled

    def record_auto_apply(self, success: bool) -> None:
        """Record result of auto-applied solution"""
        if not self.enabled:
            return

        import time

        self.recent_results.append((success, time.time()))

        # Keep only recent window
        if len(self.recent_results) > self.failure_window:
            self.recent_results = self.recent_results[-self.failure_window :]

        # Check if circuit should open
        recent_failures = sum(1 for s, _ in self.recent_results if not s)
        if recent_failures >= self.max_failures:
            self.is_open = True
            print(
                f"[CIRCUIT-BREAKER] Auto-apply disabled: {recent_failures} failures "
                f"in last {len(self.recent_results)} attempts"
            )

    def record_confirmation(self, accepted: bool) -> None:
        """Record user response to confirmation prompt"""
        if not self.enabled:
            return

        import time

        self.recent_confirmations.append((accepted, time.time()))

        # Keep only recent window
        if len(self.recent_confirmations) > self.rejection_window:
            self.recent_confirmations = self.recent_confirmations[-self.rejection_window :]

        # Check for confirmation fatigue (too many rejections)
        recent_rejections = sum(1 for acc, _ in self.recent_confirmations if not acc)
        if recent_rejections >= self.max_rejections:
            print(
                f"[CIRCUIT-BREAKER] High rejection rate: "
                f"{recent_rejections}/{len(self.recent_confirmations)}, increasing threshold"
            )
            # Signal to increase threshold (handled by caller)

    def is_auto_apply_allowed(self) -> bool:
        """Check if auto-apply is currently allowed"""
        if not self.enabled:
            return True

        return not self.is_open

    def reset(self) -> None:
        """Reset circuit breaker (for new session)"""
        self.is_open = False
        self.recent_results = []
        self.recent_confirmations = []


def main():
    """Demo confidence calculator"""
    print("=" * 60)
    print("Confidence Calculator Demo")
    print("=" * 60)

    calc = ConfidenceCalculator()

    test_cases = [
        ("ModuleNotFoundError: No module named 'pandas'", "pip install pandas", {}),
        ("Permission denied: script.sh", "chmod +x script.sh", {}),
        ("Custom business logic error", "Update payment config", {}),
        ("Database connection failed", "sudo systemctl restart postgresql", {}),
    ]

    for error, solution, context in test_cases:
        print(f"\nError: {error}")
        print(f"Solution: {solution}")

        confidence, explanation = calc.calculate(error, solution, context)

        print(explanation)
        print("-" * 60)


if __name__ == "__main__":
    main()
