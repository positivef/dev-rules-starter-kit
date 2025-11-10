"""Tests for P16 Validator - Constitutional Benchmarking Gate.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (comprehensive test coverage)
"""

import pytest

from scripts.p16_validator import (
    get_p16_summary,
    validate_p16_benchmarking,
    validate_p16_gate,
)


class TestP16Validation:
    """Test P16 benchmarking validation."""

    def test_valid_benchmarking_section(self):
        """Test valid benchmarking section passes."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "Comp1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "Comp2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "Comp3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "Point1", "rationale": "Reason1", "target": "Market1"},
                    {"point": "Point2", "rationale": "Reason2", "target": "Market2"},
                    {"point": "Point3", "rationale": "Reason3", "target": "Market3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is True
        assert error_msg is None

    def test_missing_benchmarking_section(self):
        """Test missing benchmarking section fails."""
        contract = {"task_id": "test"}

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "Missing 'benchmarking' section" in error_msg

    def test_insufficient_competitors(self):
        """Test less than 3 competitors fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "Comp1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "Comp2", "strengths": ["S2"], "weaknesses": ["W2"]},
                ],
                "differentiation": [
                    {"point": "P1", "rationale": "R1", "target": "T1"},
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "minimum 3 competitors" in error_msg
        assert "found 2" in error_msg

    def test_insufficient_differentiation(self):
        """Test less than 3 differentiation points fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "Point1", "rationale": "Reason1", "target": "Market1"},
                    {"point": "Point2", "rationale": "Reason2", "target": "Market2"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "minimum 3 differentiation points" in error_msg
        assert "found 2" in error_msg

    def test_competitor_missing_name(self):
        """Test competitor without name fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"strengths": ["S1"], "weaknesses": ["W1"]},  # Missing name
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "P1", "rationale": "R1", "target": "T1"},
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'name' field" in error_msg

    def test_competitor_missing_strengths(self):
        """Test competitor without strengths fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "weaknesses": ["W1"]},  # Missing strengths
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "P1", "rationale": "R1", "target": "T1"},
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'strengths' field" in error_msg

    def test_competitor_missing_weaknesses(self):
        """Test competitor without weaknesses fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"]},  # Missing weaknesses
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "P1", "rationale": "R1", "target": "T1"},
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'weaknesses' field" in error_msg

    def test_differentiation_missing_point(self):
        """Test differentiation without point fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"rationale": "Reason1", "target": "Market1"},  # Missing point
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'point' field" in error_msg

    def test_differentiation_missing_rationale(self):
        """Test differentiation without rationale fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "Point1", "target": "Market1"},  # Missing rationale
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'rationale' field" in error_msg

    def test_differentiation_missing_target(self):
        """Test differentiation without target fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "Point1", "rationale": "Reason1"},  # Missing target
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "missing 'target' field" in error_msg

    def test_empty_differentiation_point(self):
        """Test empty string in differentiation point fails."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "", "rationale": "Reason1", "target": "Market1"},  # Empty point
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is False
        assert "must be a non-empty string" in error_msg


class TestP16Summary:
    """Test P16 summary generation."""

    def test_get_summary(self):
        """Test summary generation."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "Todoist", "strengths": ["S1", "S2"], "weaknesses": ["W1"]},
                    {"name": "TickTick", "strengths": ["S3"], "weaknesses": ["W2", "W3"]},
                    {"name": "Things", "strengths": ["S4"], "weaknesses": ["W4"]},
                ],
                "differentiation": [
                    {"point": "AI Auto-Priority", "rationale": "R1", "target": "T1"},
                    {"point": "Open Source", "rationale": "R2", "target": "T2"},
                    {"point": "Privacy First", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        summary = get_p16_summary(contract)

        assert "[P16 Benchmarking]" in summary
        assert "Competitors: 3" in summary
        assert "Todoist" in summary
        assert "2 strengths, 1 weaknesses" in summary
        assert "Differentiation: 3 points" in summary
        assert "AI Auto-Priority" in summary

    def test_get_summary_no_benchmarking(self):
        """Test summary with no benchmarking data."""
        contract = {"task_id": "test"}

        summary = get_p16_summary(contract)

        assert "[P16] No benchmarking data" in summary


class TestP16Gate:
    """Test P16 gate validation for task executor."""

    def test_validate_gate_success(self):
        """Test gate validation passes with valid data."""
        contract = {
            "benchmarking": {
                "competitors": [
                    {"name": "C1", "strengths": ["S1"], "weaknesses": ["W1"]},
                    {"name": "C2", "strengths": ["S2"], "weaknesses": ["W2"]},
                    {"name": "C3", "strengths": ["S3"], "weaknesses": ["W3"]},
                ],
                "differentiation": [
                    {"point": "P1", "rationale": "R1", "target": "T1"},
                    {"point": "P2", "rationale": "R2", "target": "T2"},
                    {"point": "P3", "rationale": "R3", "target": "T3"},
                ],
            }
        }

        gate = {"type": "constitutional", "articles": ["P16"]}

        # Should not raise
        validate_p16_gate(contract, gate)

    def test_validate_gate_failure(self):
        """Test gate validation fails with invalid data."""
        contract = {"task_id": "test"}  # No benchmarking section

        gate = {"type": "constitutional", "articles": ["P16"]}

        with pytest.raises(ValueError) as exc_info:
            validate_p16_gate(contract, gate)

        assert "[P16 GATE FAILED]" in str(exc_info.value)
        assert "Missing 'benchmarking' section" in str(exc_info.value)


class TestP16Integration:
    """Test P16 integration scenarios."""

    def test_real_world_benchmarking(self):
        """Test with real-world-like benchmarking data."""
        contract = {
            "task_id": "FEAT-2025-11-04-TODO-APP",
            "title": "AI Todo App",
            "benchmarking": {
                "competitors": [
                    {
                        "name": "Todoist",
                        "github_stars": 50000,
                        "strengths": [
                            {"title": "Natural Language", "description": "Parse dates automatically"},
                            {"title": "Projects", "description": "Hierarchical organization"},
                        ],
                        "weaknesses": [{"category": "AI", "description": "No auto-priority"}],
                    },
                    {
                        "name": "TickTick",
                        "github_stars": 30000,
                        "strengths": [{"title": "Pomodoro", "description": "Built-in timer"}],
                        "weaknesses": [{"category": "UX", "description": "Complex UI"}],
                    },
                    {
                        "name": "Things 3",
                        "github_stars": 40000,
                        "strengths": [{"title": "Design", "description": "Clean UI"}],
                        "weaknesses": [{"category": "Platform", "description": "MacOS only"}],
                    },
                ],
                "differentiation": [
                    {"point": "AI Auto-Priority", "rationale": "No competitor has this", "target": "Busy professionals"},
                    {"point": "Open Source", "rationale": "Things 3 is closed", "target": "Privacy users"},
                    {
                        "point": "Cross-Platform",
                        "rationale": "Things 3 is Mac only",
                        "target": "Windows/Linux users",
                    },
                ],
                "target_market": {"segment": "Developers", "size": "1M+"},
            },
        }

        is_valid, error_msg = validate_p16_benchmarking(contract)

        assert is_valid is True
        assert error_msg is None
