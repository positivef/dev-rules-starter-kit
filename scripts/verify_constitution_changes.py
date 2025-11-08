# -*- coding: utf-8 -*-
"""Verify Constitution changes across all files"""

files = {
    "constitution.yaml": r"C:\Users\user\Documents\GitHub\dev-rules-starter-kit\config\constitution.yaml",
    "fusion SKILL.md": r"C:\Users\user\Documents\GitHub\skill\vibe-coding-fusion\SKILL.md",
    "enhanced SKILL.md": r"C:\Users\user\Documents\GitHub\skill\vibe-coding-enhanced\SKILL.md",
    "dev-rules CLAUDE.md": r"C:\Users\user\Documents\GitHub\dev-rules-starter-kit\CLAUDE.md",
}

print("=== Constitution Changes Verification ===\n")

# Check P8: 80% coverage
print("1. P8 Coverage Standard (should be 80%):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "threshold: 80.0" in content and "threshold: 90.0" not in content:
        print("   [SUCCESS] constitution.yaml: 80% (90% removed)")
    else:
        print("   [FAIL] constitution.yaml: Still has 90% or missing 80%")

with open(files["fusion SKILL.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "coverage: 80%" in content and "mvp:\n    coverage: 80%" in content:
        print("   [SUCCESS] fusion SKILL.md: All profiles 80%")
    else:
        print("   [WARN] fusion SKILL.md: Check coverage values")

with open(files["enhanced SKILL.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "80%" in content:
        print("   [SUCCESS] enhanced SKILL.md: References 80%")
    else:
        print("   [WARN] enhanced SKILL.md: Missing 80% reference")

# Check P16: 2-3 competitors
print("\n2. P16 Competitor Count (should be 2-3):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "2-3" in content:
        print("   [SUCCESS] constitution.yaml: 2-3 range")
    else:
        print("   [FAIL] constitution.yaml: Missing 2-3 range")

with open(files["dev-rules CLAUDE.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "2-3" in content:
        print("   [SUCCESS] dev-rules CLAUDE.md: 2-3 range")
    else:
        print("   [FAIL] dev-rules CLAUDE.md: Missing 2-3 range")

# Check P17 existence
print("\n3. P17 Decision Framework (NEW):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "P17:" in content and "decision_framework" in content:
        print("   [SUCCESS] constitution.yaml: P17 exists")
    else:
        print("   [FAIL] constitution.yaml: P17 missing")

with open(files["dev-rules CLAUDE.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "P17" in content and "Decision Framework" in content:
        print("   [SUCCESS] dev-rules CLAUDE.md: P17 documented")
    else:
        print("   [FAIL] dev-rules CLAUDE.md: P17 missing")

# Check Pattern 2 (Unverified != Rejection)
print("\n4. P11 Pattern 2 (CRITICAL - Unverified != Rejection):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "pattern_2_unverified_not_rejection" in content:
        print("   [SUCCESS] constitution.yaml: Pattern 2 codified")
    else:
        print("   [FAIL] constitution.yaml: Pattern 2 missing")

with open(files["fusion SKILL.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "Pattern 2" in content or "Unverified" in content:
        print("   [SUCCESS] fusion SKILL.md: Pattern 2 referenced")
    else:
        print("   [WARN] fusion SKILL.md: Pattern 2 not explicitly mentioned")

with open(files["dev-rules CLAUDE.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "Pattern 2" in content:
        print("   [SUCCESS] dev-rules CLAUDE.md: Pattern 2 warning added")
    else:
        print("   [FAIL] dev-rules CLAUDE.md: Pattern 2 missing")

# Check RICE Scoring
print("\n5. RICE Scoring (Industry Standard):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "RICE" in content and "Intercom" in content:
        print("   [SUCCESS] constitution.yaml: RICE standards")
    else:
        print("   [FAIL] constitution.yaml: RICE missing")

with open(files["fusion SKILL.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "RICE" in content or "rice_score" in content:
        print("   [SUCCESS] fusion SKILL.md: RICE integrated")
    else:
        print("   [WARN] fusion SKILL.md: RICE not mentioned")

with open(files["dev-rules CLAUDE.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "RICE" in content and "Intercom" in content:
        print("   [SUCCESS] dev-rules CLAUDE.md: RICE documented")
    else:
        print("   [FAIL] dev-rules CLAUDE.md: RICE missing")

# Check P14 Meta-Effects
print("\n6. P14 Meta-Effects (Constitution Self-Improvement):")
with open(files["constitution.yaml"], "r", encoding="utf-8") as f:
    content = f.read()
    if "meta_effects" in content:
        print("   [SUCCESS] constitution.yaml: meta_effects added")
    else:
        print("   [FAIL] constitution.yaml: meta_effects missing")

with open(files["dev-rules CLAUDE.md"], "r", encoding="utf-8") as f:
    content = f.read()
    if "Meta-Effects" in content or "meta_effects" in content:
        print("   [SUCCESS] dev-rules CLAUDE.md: Meta-Effects documented")
    else:
        print("   [FAIL] dev-rules CLAUDE.md: Meta-Effects missing")

print("\n=== Summary ===")
print("Verification complete. Check for any [FAIL] items above.")
