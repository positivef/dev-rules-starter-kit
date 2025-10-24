import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from orchestration_policy import OrchestrationPolicy

ROOT = Path(__file__).resolve().parent.parent


def test_policy_reads_master_config():
    policy = OrchestrationPolicy()
    assert policy.risk_threshold == pytest.approx(0.8)
    assert policy.failure_rate_limit == pytest.approx(0.3)
    assert policy.zen_enabled is True


def test_policy_decision_uses_priority_mapping():
    policy = OrchestrationPolicy()
    contract = {
        "priority": "high",
        "commands": [{"exec": {"cmd": "python"}}],
        "metrics": {"historical_failure_rate": 0.1},
    }

    metadata = policy.build_metadata(contract)
    assert metadata.risk_level > 0.8
    assert policy.should_use_zen(metadata) is False


def test_policy_respects_manual_override():
    policy = OrchestrationPolicy()
    contract = {
        "priority": "low",
        "metrics": {"historical_failure_rate": 0.0},
        "orchestration": {"execution_mode": "sequential"},
    }

    metadata = policy.build_metadata(contract)
    assert policy.should_use_zen(metadata) is False

    contract["orchestration"]["execution_mode"] = "zen"
    metadata = policy.build_metadata(contract)
    assert policy.should_use_zen(metadata) is True


def test_policy_validation_commands_from_config():
    policy = OrchestrationPolicy()
    commands = policy.get_validation_commands()
    assert "python -m pytest tests/ -q" in commands
