"""P16 Validator - Constitutional Benchmarking Gate.

Constitutional Compliance:
- P16: Competitive Benchmarking (validates this article)
- P2: Evidence-Based (validation results recorded)

Purpose:
    Validates YAML contracts have proper benchmarking sections before execution.
    Ensures P16 compliance: minimum 3 competitors, 3 differentiation points.

Usage:
    from p16_validator import validate_p16_benchmarking

    # In task_executor.py
    if gate_id == "p16-benchmarking":
        is_valid, error_msg = validate_p16_benchmarking(contract)
        if not is_valid:
            raise ValueError(f"P16 validation failed: {error_msg}")

Related:
    - benchmark_analyzer.py: Generates benchmarking data
    - task_executor.py: Calls this validator for P16 gates
"""

from typing import Dict, Optional, Tuple


def validate_p16_benchmarking(contract: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate P16: Competitive Benchmarking section.

    Args:
        contract: YAML contract dictionary

    Returns:
        (is_valid, error_message)
        - (True, None) if valid
        - (False, "error message") if invalid

    P16 Requirements:
        1. benchmarking section exists
        2. competitors: minimum 3
        3. Each competitor has: name, strengths, weaknesses
        4. differentiation: minimum 3 points
        5. Each differentiation has: point, rationale, target

    Examples:
        >>> contract = {
        ...     "benchmarking": {
        ...         "competitors": [
        ...             {"name": "A", "strengths": [...], "weaknesses": [...]},
        ...             {"name": "B", "strengths": [...], "weaknesses": [...]},
        ...             {"name": "C", "strengths": [...], "weaknesses": [...]}
        ...         ],
        ...         "differentiation": [
        ...             {"point": "X", "rationale": "Y", "target": "Z"},
        ...             {"point": "X2", "rationale": "Y2", "target": "Z2"},
        ...             {"point": "X3", "rationale": "Y3", "target": "Z3"}
        ...         ]
        ...     }
        ... }
        >>> validate_p16_benchmarking(contract)
        (True, None)
    """
    # Check if benchmarking section exists
    if "benchmarking" not in contract:
        return False, "Missing 'benchmarking' section (P16 requirement)"

    benchmarking = contract["benchmarking"]

    # Validate competitors
    competitors = benchmarking.get("competitors", [])
    if not isinstance(competitors, list):
        return False, "'competitors' must be a list"

    if len(competitors) < 3:
        return (
            False,
            f"P16 requires minimum 3 competitors, found {len(competitors)}. "
            "Run: python scripts/benchmark_analyzer.py --query 'your topic'",
        )

    # Validate each competitor structure
    for i, comp in enumerate(competitors, 1):
        if not isinstance(comp, dict):
            return False, f"Competitor {i} must be a dictionary"

        # Check required fields
        if "name" not in comp:
            return False, f"Competitor {i} missing 'name' field"

        if "strengths" not in comp:
            return False, f"Competitor {i} ({comp.get('name', 'unknown')}) missing 'strengths' field"

        if "weaknesses" not in comp:
            return False, f"Competitor {i} ({comp.get('name', 'unknown')}) missing 'weaknesses' field"

        # Validate strengths and weaknesses are lists
        if not isinstance(comp["strengths"], list):
            return False, f"Competitor {i} 'strengths' must be a list"

        if not isinstance(comp["weaknesses"], list):
            return False, f"Competitor {i} 'weaknesses' must be a list"

    # Validate differentiation
    differentiation = benchmarking.get("differentiation", [])
    if not isinstance(differentiation, list):
        return False, "'differentiation' must be a list"

    if len(differentiation) < 3:
        return (
            False,
            f"P16 requires minimum 3 differentiation points, found {len(differentiation)}. "
            "Analyze competitor gaps and propose unique value propositions.",
        )

    # Validate each differentiation point structure
    for i, diff in enumerate(differentiation, 1):
        if not isinstance(diff, dict):
            return False, f"Differentiation point {i} must be a dictionary"

        # Check required fields
        if "point" not in diff:
            return False, f"Differentiation {i} missing 'point' field"

        if "rationale" not in diff:
            return False, f"Differentiation {i} missing 'rationale' field (why this differentiates)"

        if "target" not in diff:
            return False, f"Differentiation {i} missing 'target' field (target market)"

        # Check fields are non-empty strings
        if not diff["point"] or not isinstance(diff["point"], str):
            return False, f"Differentiation {i} 'point' must be a non-empty string"

        if not diff["rationale"] or not isinstance(diff["rationale"], str):
            return False, f"Differentiation {i} 'rationale' must be a non-empty string"

        if not diff["target"] or not isinstance(diff["target"], str):
            return False, f"Differentiation {i} 'target' must be a non-empty string"

    # All validations passed
    return True, None


def get_p16_summary(contract: Dict) -> str:
    """
    Get summary of P16 benchmarking data.

    Args:
        contract: YAML contract with benchmarking section

    Returns:
        Human-readable summary string
    """
    if "benchmarking" not in contract:
        return "[P16] No benchmarking data"

    bench = contract["benchmarking"]
    competitors = bench.get("competitors", [])
    differentiation = bench.get("differentiation", [])

    summary = "[P16 Benchmarking]\n"
    summary += f"  Competitors: {len(competitors)}\n"

    for comp in competitors[:3]:  # Show first 3
        name = comp.get("name", "Unknown")
        strengths_count = len(comp.get("strengths", []))
        weaknesses_count = len(comp.get("weaknesses", []))
        summary += f"    - {name}: {strengths_count} strengths, {weaknesses_count} weaknesses\n"

    summary += f"  Differentiation: {len(differentiation)} points\n"

    for i, diff in enumerate(differentiation, 1):
        point = diff.get("point", "Unknown")
        summary += f"    {i}. {point}\n"

    return summary


def validate_p16_gate(contract: Dict, gate: Dict) -> None:
    """
    Validate P16 gate during task execution.

    This is the main function called by task_executor.py.

    Args:
        contract: Full YAML contract
        gate: Gate configuration

    Raises:
        ValueError: If P16 validation fails

    Example:
        # In task_executor.py
        if gate.get("type") == "constitutional" and "P16" in gate.get("articles", []):
            validate_p16_gate(contract, gate)
    """
    is_valid, error_msg = validate_p16_benchmarking(contract)

    if not is_valid:
        raise ValueError(
            f"[P16 GATE FAILED] {error_msg}\n\n"
            "To fix:\n"
            "1. Run benchmarking analysis:\n"
            "   python scripts/benchmark_analyzer.py --query 'your feature topic'\n\n"
            "2. Add the generated benchmarking section to your YAML contract:\n"
            "   benchmarking:\n"
            "     competitors: [...]\n"
            "     differentiation: [...]\n\n"
            "3. Re-run task executor"
        )

    # Print summary if valid
    print(get_p16_summary(contract))


def main():
    """CLI for testing P16 validation."""
    import argparse
    import sys
    import yaml

    parser = argparse.ArgumentParser(description="P16 Benchmarking Validator")
    parser.add_argument("yaml_file", type=str, help="YAML contract file to validate")

    args = parser.parse_args()

    # Load YAML
    try:
        with open(args.yaml_file, encoding="utf-8") as f:
            contract = yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load YAML: {e}")
        sys.exit(1)

    # Validate
    is_valid, error_msg = validate_p16_benchmarking(contract)

    if is_valid:
        print("[OK] P16 validation passed!")
        print("\n" + get_p16_summary(contract))
        sys.exit(0)
    else:
        print(f"[FAILED] P16 validation failed: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
