"""Risk-aware orchestration policy utilities.

This module reads policy settings from ``config/master_config.json`` and exposes
helpers that decide whether Zen MCP (fast path) can be used and which
post-execution validation commands must run.

The logic is intentionally conservative and data driven so that teams can tune
thresholds without modifying code. Values default to safe fallbacks when
metadata is missing, meaning legacy contracts continue to work.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "master_config.json"


@dataclass
class TaskMetadata:
    risk_level: float
    historical_failure_rate: float
    complexity_score: float
    required_roles: List[str]
    manual_override: str | None = None

    def summary(self) -> str:
        return (
            f"risk={self.risk_level:.2f}, "
            f"failure_rate={self.historical_failure_rate:.2f}, "
            f"complexity={self.complexity_score:.2f}"
        )


class OrchestrationPolicy:
    """Policy engine backed by ``master_config.json``."""

    def __init__(self, config_path: Path | None = None):
        config_path = config_path or CONFIG_PATH
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {config_path}")

        with config_path.open(encoding="utf-8") as fp:
            self._config = json.load(fp)

        precision = self._config.get("precision_system", {})
        self._policy = precision.get("orchestration_policy", {})

    # ------------------------------------------------------------------
    # Configuration accessors
    # ------------------------------------------------------------------
    @property
    def zen_enabled(self) -> bool:
        return bool(self._policy.get("zen_mcp_enabled", True))

    @property
    def risk_threshold(self) -> float:
        return float(self._policy.get("risk_threshold", 0.8))

    @property
    def failure_rate_limit(self) -> float:
        return float(self._policy.get("failure_rate_limit", 0.3))

    @property
    def min_confidence(self) -> float:
        return float(self._policy.get("min_confidence_threshold", 0.0))

    def get_validation_commands(self) -> List[str]:
        commands = self._policy.get("auto_validation_commands", [])
        return [cmd for cmd in commands if isinstance(cmd, str) and cmd.strip()]

    # ------------------------------------------------------------------
    # Decision helpers
    # ------------------------------------------------------------------
    def should_use_zen(self, metadata: TaskMetadata) -> bool:
        """Return ``True`` if Zen MCP fast path is allowed."""
        if metadata.manual_override == "sequential":
            return False
        if metadata.manual_override == "zen":
            return True
        if not self.zen_enabled:
            return False

        risk = max(0.0, min(1.0, metadata.risk_level))
        failure_rate = max(0.0, min(1.0, metadata.historical_failure_rate))
        complexity = max(0.0, min(1.0, metadata.complexity_score))

        # Conservative combination: treat overall risk as the max of the three signals
        combined_risk = max(risk, complexity)

        if combined_risk > self.risk_threshold:
            return False
        if failure_rate > self.failure_rate_limit:
            return False

        return True

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    @staticmethod
    def build_metadata(contract: Dict[str, Any]) -> TaskMetadata:
        """Infer task metadata from a contract dictionary."""
        priority = (contract.get("priority") or "medium").lower()
        risk_map = {"high": 0.9, "medium": 0.6, "low": 0.3}
        risk_level = risk_map.get(priority, 0.6)

        metrics = contract.get("metrics", {})
        failure_rate = float(metrics.get("historical_failure_rate", 0.0))

        commands = contract.get("commands", [])
        complexity = 0.0
        if commands:
            unique_cmds = {cmd.get("exec", {}).get("cmd") for cmd in commands if isinstance(cmd, dict)}
            complexity = min(1.0, 0.2 + 0.1 * len(unique_cmds))
            if contract.get("prompt_optimization", {}).get("enabled"):
                complexity += 0.1
            complexity = min(complexity, 1.0)

        required_roles: Iterable[str] = contract.get("roles_required") or contract.get("tags") or []
        roles = [r for r in required_roles if isinstance(r, str)]

        orchestration = contract.get("orchestration", {})
        override = orchestration.get("execution_mode")
        if override:
            override = override.lower()

        return TaskMetadata(
            risk_level=risk_level,
            historical_failure_rate=failure_rate,
            complexity_score=complexity,
            required_roles=roles,
            manual_override=override,
        )


__all__ = ["OrchestrationPolicy", "TaskMetadata"]
