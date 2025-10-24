"""Governance Gate

P11~P13 거버넌스 체크리스트를 검증하고 Evidence 저장 경로에 기록합니다.

Usage:
    python scripts/governance_gate.py --checklist path/to/checklist.yaml --task-id FEAT-123 --output-dir RUNS/evidence
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


PLACEHOLDER_VALUES = {"", "TBD", "TODO"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate governance checklist and persist evidence")
    parser.add_argument("--checklist", type=Path, required=True, help="Path to the completed P11~P13 checklist YAML")
    parser.add_argument("--task-id", type=str, default=None, help="Task identifier used for evidence storage")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("RUNS/evidence"),
        help="Base directory for evidence output (default: RUNS/evidence)",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat warnings as errors to block execution when required fields are missing",
    )
    return parser.parse_args()


def load_checklist(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Checklist file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Checklist must be a YAML mapping")
    return data


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in PLACEHOLDER_VALUES
    if isinstance(value, list):
        return all(is_placeholder(item) for item in value)
    if isinstance(value, dict):
        return all(is_placeholder(v) for v in value.values())
    return False


def ensure_fields(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Return (errors, warnings) detected in the checklist."""

    errors: List[str] = []
    warnings: List[str] = []

    meta = data.get("meta", {})
    for key in ["decision_title", "prepared_by", "date"]:
        if is_placeholder(meta.get(key)):
            errors.append(f"meta.{key} is missing")

    reviewers = meta.get("reviewers")
    if not reviewers or is_placeholder(reviewers):
        warnings.append("meta.reviewers should list at least one reviewer")

    p11 = data.get("p11_conflict_review", {})
    if is_placeholder(p11.get("conflict_summary")):
        errors.append("p11_conflict_review.conflict_summary is missing")
    if is_placeholder(p11.get("resolution")):
        errors.append("p11_conflict_review.resolution is missing")
    if is_placeholder(p11.get("related_principles")):
        warnings.append("p11_conflict_review.related_principles should reference at least one article")
    if is_placeholder(p11.get("past_decisions_consulted")):
        warnings.append("p11_conflict_review.past_decisions_consulted should cite prior work")

    p12 = data.get("p12_tradeoff_analysis", {})
    options = p12.get("options") or []
    cleaned_options = [opt for opt in options if not is_placeholder(opt.get("name"))]
    if not cleaned_options:
        errors.append("p12_tradeoff_analysis.options must describe at least one option")
    for index, option in enumerate(cleaned_options, start=1):
        if is_placeholder(option.get("pros")):
            warnings.append(f"p12_tradeoff_analysis.options[{index}].pros is empty")
        if is_placeholder(option.get("cons")):
            warnings.append(f"p12_tradeoff_analysis.options[{index}].cons is empty")
        if is_placeholder(option.get("evidence")):
            warnings.append(f"p12_tradeoff_analysis.options[{index}].evidence is empty")
    if is_placeholder(p12.get("recommended_option")):
        errors.append("p12_tradeoff_analysis.recommended_option is missing")
    if is_placeholder(p12.get("rationale")):
        errors.append("p12_tradeoff_analysis.rationale is missing")

    p13 = data.get("p13_constitution_change", {})
    if p13.get("required"):
        if is_placeholder(p13.get("target_articles")):
            errors.append("p13_constitution_change.target_articles is missing")
        if is_placeholder(p13.get("change_summary")):
            errors.append("p13_constitution_change.change_summary is missing")
        if is_placeholder(p13.get("approval_status")):
            errors.append("p13_constitution_change.approval_status is missing")
    else:
        if not p13:
            warnings.append("p13_constitution_change section is missing; set required=false when no change is needed")

    signoff = data.get("signoff", {})
    if is_placeholder(signoff.get("approver")):
        errors.append("signoff.approver is missing")
    if is_placeholder(signoff.get("approval_date")):
        warnings.append("signoff.approval_date is missing")

    return errors, warnings


def persist_evidence(data: Dict[str, Any], output_dir: Path, task_id: str | None) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    if task_id:
        evidence_dir = output_dir / task_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        output_path = evidence_dir / "governance.json"
    else:
        reports_dir = output_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / f"governance_{timestamp}.json"

    payload = {
        "generated_at": timestamp,
        "task_id": task_id,
        "checklist": data,
    }
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    args = parse_args()
    checklist = load_checklist(args.checklist)
    errors, warnings = ensure_fields(checklist)

    if errors:
        for msg in errors:
            print(f"[ERROR] {msg}")
    if warnings:
        for msg in warnings:
            print(f"[WARN] {msg}")

    if errors or (warnings and args.fail_on_warning):
        raise SystemExit("Governance gate validation failed")

    output_path = persist_evidence(checklist, args.output_dir, args.task_id)
    print(f"[OK] Governance evidence stored at {output_path}")


if __name__ == "__main__":
    main()
