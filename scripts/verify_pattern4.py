# -*- coding: utf-8 -*-
"""Verify Pattern 4 addition to Constitution and CLAUDE.md"""

import yaml


def verify_constitution():
    """Verify pattern_4 in constitution.yaml"""
    print("=" * 60)
    print("Verifying constitution.yaml")
    print("=" * 60)

    with open("config/constitution.yaml", "r", encoding="utf-8") as f:
        constitution = yaml.safe_load(f)

    # Find P11
    p11 = None
    for article in constitution["articles"]:
        if article.get("id") == "P11":
            p11 = article
            break

    if not p11:
        print("[FAIL] P11 not found")
        return False

    # Check pattern_4
    anti_patterns = p11.get("anti_patterns", {})
    if "pattern_4_design_review_first" not in anti_patterns:
        print("[FAIL] pattern_4_design_review_first not found in P11")
        return False

    pattern_4 = anti_patterns["pattern_4_design_review_first"]

    # Check required fields
    required_fields = [
        "name",
        "discovered",
        "severity",
        "trigger",
        "mandatory_steps",
        "never_say",
        "always_say",
    ]

    for field in required_fields:
        if field not in pattern_4:
            print(f"[FAIL] Required field missing: {field}")
            return False

    print("[SUCCESS] Constitution - Pattern 4 verified")
    print(f'  Name: {pattern_4["name"]}')
    print(f'  Severity: {pattern_4["severity"]}')
    print(f'  Mandatory steps: {len(pattern_4["mandatory_steps"])} steps')
    print(f'  Never say: {len(pattern_4["never_say"])} items')
    print(f'  Always say: {len(pattern_4["always_say"])} items')

    # Check 8 risk checklist
    if "step_2_risk_analysis" in pattern_4["mandatory_steps"]:
        risk_analysis = pattern_4["mandatory_steps"]["step_2_risk_analysis"]
        if "checklist" in risk_analysis:
            checklist = risk_analysis["checklist"]
            print(f"  Risk checklist: {len(checklist)} items")
            if len(checklist) != 8:
                print(f"  [WARN] Expected 8 risks, found {len(checklist)}")

    return True


def verify_claude_md():
    """Verify pattern_4 in CLAUDE.md"""
    print("\n" + "=" * 60)
    print("Verifying CLAUDE.md")
    print("=" * 60)

    with open("CLAUDE.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Check Pattern 4 section exists
    if "Pattern 4" not in content:
        print("[FAIL] Pattern 4 section not found in CLAUDE.md")
        return False

    # Check key phrases
    required_phrases = [
        "설계 검토 필수",
        "먼저 설계 검토부터 할게요",
        "8가지 위험 체크",
        "DESIGN_REVIEW.md",
    ]

    for phrase in required_phrases:
        if phrase not in content:
            print(f'[FAIL] Required phrase not found: "{phrase}"')
            return False

    print("[SUCCESS] CLAUDE.md - Pattern 4 verified")
    print("  Found Pattern 4 section: Yes")
    print(f"  Key phrases: {len(required_phrases)}/{len(required_phrases)}")

    return True


def main():
    """Run all verifications"""
    results = []

    results.append(("Constitution", verify_constitution()))
    results.append(("CLAUDE.md", verify_claude_md()))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[SUCCESS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] All verifications passed!")
        return 0
    else:
        print("\n[FAIL] Some verifications failed")
        return 1


if __name__ == "__main__":
    exit(main())
