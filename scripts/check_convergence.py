"""Manual convergence check script for P15.

Quick check for stop conditions and complexity budget.
Use this before proposing new features or major changes.

Usage:
    python scripts/check_convergence.py
    python scripts/check_convergence.py --verbose
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_constitution_lines():
    """Count lines in constitution.yaml"""
    const_file = ROOT / "config" / "constitution.yaml"
    if not const_file.exists():
        return 0
    return len(const_file.read_text(encoding="utf-8").splitlines())


def count_articles():
    """Count P1-P13 articles in constitution.yaml"""
    const_file = ROOT / "config" / "constitution.yaml"
    if not const_file.exists():
        return 0

    content = const_file.read_text(encoding="utf-8")
    # Simple count of "article:" or "P1:", "P2:", etc.
    import re

    matches = re.findall(r"\b(P\d+|article\s*\d+)", content, re.IGNORECASE)
    return len(set(matches))


def calculate_total_roi():
    """Calculate total ROI from Phase 1/2/3"""
    # From .constitution-phases-complete.md
    phase_rois = {
        "Phase 1": 9300,  # 9,300%
        "Phase 2": 7200,  # 7,200%
        "Phase 3": 3900,  # 3,900%
    }
    return sum(phase_rois.values()), phase_rois


def check_stop_conditions(verbose=False):
    """Check P15 stop conditions"""
    total_roi, phase_rois = calculate_total_roi()
    articles = count_articles()
    lines = count_constitution_lines()

    # From .constitution-config.yaml
    thresholds = {
        "roi_threshold": 300,
        "satisfaction_threshold": 80,
        "stable_duration_days": 90,
        "new_proposal_roi_min": 150,
        "max_articles": 20,
        "max_lines_per_article": 150,
        "max_total_lines": 1500,
    }

    print("=" * 60)
    print("P15: Convergence Principle Check")
    print("=" * 60)
    print()

    # ROI Check
    roi_met = total_roi >= thresholds["roi_threshold"]
    print("[ROI Check]")
    print(f"  Total ROI: {total_roi:,}% (threshold: {thresholds['roi_threshold']}%)")
    if verbose:
        for phase, roi in phase_rois.items():
            print(f"    - {phase}: {roi:,}%")
    print(f"  Status: {'STOP' if roi_met else 'CONTINUE'} {'[CHECKMARK]' if roi_met else ''}")
    print()

    # Complexity Budget Check
    articles_ok = articles <= thresholds["max_articles"]
    lines_ok = lines <= thresholds["max_total_lines"]

    print("[Complexity Budget]")
    print(f"  Articles: {articles} / {thresholds['max_articles']} (max)")
    print(f"  Status: {'OK' if articles_ok else 'EXCEEDED'} {'[CHECKMARK]' if articles_ok else '[WARNING]'}")
    print()
    print(f"  Lines: {lines} / {thresholds['max_total_lines']} (max)")
    print(f"  Status: {'OK' if lines_ok else 'EXCEEDED'} {'[CHECKMARK]' if lines_ok else '[WARNING]'}")
    print()

    # Overall Recommendation
    print("=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)

    if roi_met and articles_ok and lines_ok:
        print("[SUCCESS] Stop conditions MET.")
        print()
        print("Recommendations:")
        print("  1. STOP adding new features")
        print("  2. FOCUS on:")
        print("     - Documentation")
        print("     - Testing")
        print("     - Stability")
        print("     - User feedback")
        print("  3. New proposals need ROI > 150%")
        print()
        print("Rationale:")
        print(f"  - ROI {total_roi:,}% >> {thresholds['roi_threshold']}% threshold")
        print("  - System is 'Good Enough' (P15)")
        print("  - Avoid diminishing returns")
        print()
        return True
    else:
        print("[INFO] Continue development.")
        print()
        if not roi_met:
            print(f"  - ROI {total_roi}% < {thresholds['roi_threshold']}% threshold")
        if not articles_ok:
            print(f"  - Articles {articles} > {thresholds['max_articles']} max")
        if not lines_ok:
            print(f"  - Lines {lines} > {thresholds['max_total_lines']} max")
        print()
        return False


def check_new_proposal(proposal_roi, verbose=False):
    """Check if new proposal meets ROI requirement"""
    threshold = 150  # new_proposal_roi_min

    print("=" * 60)
    print("New Proposal ROI Check")
    print("=" * 60)
    print()
    print(f"  Proposed ROI: {proposal_roi}%")
    print(f"  Minimum required: {threshold}%")
    print()

    if proposal_roi >= threshold:
        print("  Status: APPROVED [CHECKMARK]")
        print(f"  Rationale: ROI {proposal_roi}% >= {threshold}%")
        return True
    else:
        print("  Status: REJECTED [X]")
        print(f"  Rationale: ROI {proposal_roi}% < {threshold}%")
        print()
        print("  Suggestion: Focus on higher-ROI opportunities")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check P15 convergence conditions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with details")
    parser.add_argument("--proposal-roi", type=float, help="Check if new proposal meets ROI requirement")

    args = parser.parse_args()

    if args.proposal_roi is not None:
        # Check new proposal
        approved = check_new_proposal(args.proposal_roi, args.verbose)
        sys.exit(0 if approved else 1)
    else:
        # Check stop conditions
        check_stop_conditions(args.verbose)
        sys.exit(0)


if __name__ == "__main__":
    main()
