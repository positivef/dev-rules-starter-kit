#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADRBuilder Usage Examples

Demonstrates various use cases of ADRBuilder for documenting
architecture decisions with Constitution mapping.

Examples:
1. Creating an ADR programmatically
2. Searching past ADRs
3. Detecting Constitution conflicts
4. Auto-suggesting ADRs for code changes
"""

import sys
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from adr_builder import ADRBuilder, ADR, Alternative, Consequence, ADRStatus


def example_1_create_adr_programmatically():
    """Example 1: Create ADR programmatically (not interactively)"""
    print("\n" + "=" * 70)
    print("Example 1: Creating ADR Programmatically")
    print("=" * 70)

    builder = ADRBuilder()

    # Create ADR for database selection
    adr = ADR(
        number=builder.get_next_number(),
        title="Use PostgreSQL Instead of MongoDB",
        status=ADRStatus.ACCEPTED.value,
        date=datetime.now().strftime("%Y-%m-%d"),
        context="""
        Our application requires:
        - Strong ACID guarantees for financial transactions
        - Complex relational queries
        - JSON storage for flexible metadata
        - High reliability and data consistency
        """,
        decision="We will use PostgreSQL as our primary database system.",
        rationale="""
        PostgreSQL provides:
        1. Full ACID compliance for financial data integrity
        2. Mature and battle-tested in production environments
        3. Excellent JSON/JSONB support for flexible schemas
        4. Strong community and ecosystem
        5. Better SQL compliance than alternatives
        """,
        alternatives=[
            Alternative(
                name="MongoDB",
                pros=[
                    "Flexible schema design",
                    "Good for rapid prototyping",
                    "Built-in sharding",
                ],
                cons=[
                    "Weaker consistency guarantees",
                    "Not ideal for complex joins",
                    "ACID only within single document",
                ],
                reason_rejected="Need strong ACID across multiple collections for financial data",
            ),
            Alternative(
                name="MySQL",
                pros=[
                    "Very popular and well-known",
                    "Simple to set up",
                    "Good performance",
                ],
                cons=[
                    "Less feature-rich than PostgreSQL",
                    "Weaker JSON support",
                    "Less strict SQL compliance",
                ],
                reason_rejected="PostgreSQL's JSON support and SQL compliance better fit our needs",
            ),
        ],
        consequences=[
            Consequence(type="positive", description="Strong data consistency and reliability", impact_area="reliability"),
            Consequence(
                type="positive", description="Excellent JSON support for flexible schemas", impact_area="flexibility"
            ),
            Consequence(
                type="negative", description="Slightly higher resource usage compared to MySQL", impact_area="performance"
            ),
            Consequence(
                type="negative", description="Team needs to learn PostgreSQL-specific features", impact_area="learning_curve"
            ),
        ],
        related_articles=["P5", "P12"],  # Security First, Trade-off Analysis
        tags=["database", "infrastructure", "architecture"],
        authors=["Tech Lead", "Senior Backend Engineer"],
    )

    # Save ADR
    filepath = builder.save_adr(adr)

    print(f"\n[SUCCESS] ADR created: {filepath}")
    print(f"[SUCCESS] Number: ADR-{adr.number:03d}")
    print(f"[SUCCESS] Related Constitution Articles: {', '.join(adr.related_articles)}")

    # Show preview
    with open(filepath, encoding="utf-8") as f:
        preview = f.read()[:500]
        print(f"\n[PREVIEW] First 500 characters:\n{preview}...")


def example_2_search_adrs():
    """Example 2: Search for past ADRs"""
    print("\n\n" + "=" * 70)
    print("Example 2: Searching Past ADRs")
    print("=" * 70)

    builder = ADRBuilder()

    # Search by keyword
    search_terms = ["database", "PostgreSQL", "security", "nonexistent"]

    for term in search_terms:
        print(f"\n[SEARCHING] Keyword: '{term}'")
        results = builder.search_adrs(term)

        if results:
            print(f"[FOUND] {len(results)} ADR(s):")
            for number, title, filepath in results:
                print(f"  - ADR-{number:03d}: {title}")
                print(f"    File: {filepath}")
        else:
            print(f"[NOT FOUND] No ADRs found for '{term}'")


def example_3_list_all_adrs():
    """Example 3: List all ADRs"""
    print("\n\n" + "=" * 70)
    print("Example 3: Listing All ADRs")
    print("=" * 70)

    builder = ADRBuilder()

    adrs = builder.list_all_adrs()

    print(f"\n[ALL ADRS] Total: {len(adrs)}\n")

    if adrs:
        for adr in adrs:
            status_icon = {"accepted": "[OK]", "proposed": "[?]", "deprecated": "[X]", "superseded": "[~]"}.get(
                adr["status"], "[?]"
            )

            print(f"{status_icon} ADR-{adr['number']:03d}: {adr['title']}")
            print(f"    Status: {adr['status']} | Date: {adr['date']}")
    else:
        print("No ADRs found. Create one with: python scripts/adr_builder.py create")


def example_4_detect_conflicts():
    """Example 4: Detect Constitution principle conflicts"""
    print("\n\n" + "=" * 70)
    print("Example 4: Detecting Principle Conflicts")
    print("=" * 70)

    builder = ADRBuilder()

    # Create ADR with potential conflict (P4 SOLID vs P15 Convergence)
    adr = ADR(
        number=builder.get_next_number(),
        title="Pragmatic SOLID Application Strategy",
        status=ADRStatus.ACCEPTED.value,
        date=datetime.now().strftime("%Y-%m-%d"),
        context="""
        Need to balance code quality with delivery speed.
        Full SOLID compliance takes 3x longer than pragmatic approach.
        """,
        decision="Apply SOLID principles but stop at 80% compliance",
        rationale="""
        80/20 rule: 80% of benefits come from 20% of effort.
        Perfect SOLID compliance has diminishing returns.
        Focus on high-impact principles: Single Responsibility and Dependency Inversion.
        """,
        alternatives=[],
        consequences=[],
        related_articles=["P4", "P15"],  # SOLID vs Convergence - potential conflict!
        tags=["quality", "pragmatism", "trade-off"],
    )

    builder.save_adr(adr)

    print("\n[CHECKING] Scanning for principle conflicts...")
    conflicts = builder.detect_conflicts()

    if conflicts:
        print(f"\n[CONFLICTS FOUND] {len(conflicts)} potential conflict(s):\n")
        for conflict in conflicts:
            print(f"ADR-{conflict['adr']:03d}: {conflict['title']}")
            print(f"  Conflict: {conflict['conflict']}")
            print("  Resolution: Review ADR to ensure conflict is addressed")
            print(f"  File: {conflict['file']}\n")
    else:
        print("\n[OK] No principle conflicts detected")


def example_5_auto_suggest():
    """Example 5: Auto-suggest ADR for code changes"""
    print("\n\n" + "=" * 70)
    print("Example 5: Auto-Suggest ADR for Code Changes")
    print("=" * 70)

    builder = ADRBuilder()

    # Create temporary test file
    test_file = Path("temp_architecture_change.py")
    test_file.write_text(
        """
    # Major architectural refactor: Migrating from REST to GraphQL

    class GraphQLServer:
        '''
        This is a significant architecture decision to migrate from REST API
        to GraphQL for better performance and flexibility.

        Reasons:
        - Single endpoint reduces network overhead
        - Client-specified queries reduce over-fetching
        - Strong typing improves API security
        '''

        def __init__(self):
            self.schema = build_schema()

        def execute_query(self, query):
            # Execute GraphQL query
            pass
    """,
        encoding="utf-8",
    )

    try:
        print(f"\n[ANALYZING] File: {test_file}")
        suggestion = builder.suggest_adr_for_file(str(test_file))

        if suggestion:
            print("\n[ADR SUGGESTED]")
            print(f"\nFile: {suggestion['file']}")

            print("\nReasons:")
            for reason in suggestion["reasons"]:
                print(f"  - {reason}")

            print("\nRelevant Constitution Articles:")
            for article in suggestion["suggested_articles"]:
                article_name = builder._get_article_name(article)
                print(f"  - {article}: {article_name}")

            print(f"\n{suggestion['template']}")
        else:
            print("\n[NO SUGGESTION] No architectural decision detected")

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def example_6_constitution_mapping():
    """Example 6: Demonstrate Constitution article auto-detection"""
    print("\n\n" + "=" * 70)
    print("Example 6: Constitution Article Auto-Detection")
    print("=" * 70)

    builder = ADRBuilder()

    test_cases = [
        ("YAML contract for task specification", ["P1"]),
        ("Security vulnerability in authentication system", ["P5"]),
        ("Test-driven development with pytest", ["P8"]),
        ("Trade-off between performance and maintainability", ["P12"]),
        ("Good enough at 80% is better than perfect", ["P15"]),
        ("YAML contracts with security and testing", ["P1", "P5", "P8"]),
    ]

    print("\n[TEST CASES]")
    for text, expected in test_cases:
        detected = builder.detect_constitution_articles(text)
        match_icon = "[OK]" if any(e in detected for e in expected) else "[PARTIAL]"

        print(f'\n{match_icon} Text: "{text[:60]}..."')
        print(f"    Expected: {expected}")
        print(f"    Detected: {detected}")


def example_7_complete_workflow():
    """Example 7: Complete ADR workflow from creation to reference"""
    print("\n\n" + "=" * 70)
    print("Example 7: Complete ADR Workflow")
    print("=" * 70)

    builder = ADRBuilder()

    print("\n[STEP 1] Creating ADR for API design decision...")

    adr = ADR(
        number=builder.get_next_number(),
        title="RESTful API Design with Versioning",
        status=ADRStatus.ACCEPTED.value,
        date=datetime.now().strftime("%Y-%m-%d"),
        context="Need consistent API design for external consumers",
        decision="Use RESTful API with URL-based versioning (v1, v2)",
        rationale="Industry standard, easy to understand, backward compatible",
        alternatives=[
            Alternative(
                name="GraphQL",
                pros=["Flexible queries", "Single endpoint"],
                cons=["Complex learning curve", "Caching challenges"],
                reason_rejected="Team not familiar with GraphQL",
            )
        ],
        consequences=[Consequence(type="positive", description="Easy for clients to integrate", impact_area="usability")],
        related_articles=["P1", "P3"],
        tags=["api", "architecture"],
    )

    filepath = builder.save_adr(adr)
    print(f"[SUCCESS] Created: {filepath}")

    print("\n[STEP 2] Searching for API-related ADRs...")
    results = builder.search_adrs("API")
    print(f"[FOUND] {len(results)} ADR(s) about 'API'")

    print("\n[STEP 3] Listing all architecture decisions...")
    all_adrs = builder.list_all_adrs()
    print(f"[TOTAL] {len(all_adrs)} ADR(s) in the system")

    print("\n[STEP 4] Checking for conflicts...")
    conflicts = builder.detect_conflicts()
    if conflicts:
        print(f"[WARNING] {len(conflicts)} conflict(s) detected")
    else:
        print("[OK] No conflicts detected")

    print("\n[WORKFLOW COMPLETE] ADR is now part of the knowledge base")
    print("Next steps:")
    print("  1. Review ADR in ADRS/ directory")
    print("  2. Sync to Obsidian for team visibility")
    print("  3. Reference in code reviews and future decisions")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" " * 20 + "ADRBuilder Demo")
    print("=" * 70)
    print("\nThis demo shows how to use ADRBuilder to document")
    print("architecture decisions with Constitution compliance.\n")

    try:
        example_1_create_adr_programmatically()
        example_2_search_adrs()
        example_3_list_all_adrs()
        example_4_detect_conflicts()
        example_5_auto_suggest()
        example_6_constitution_mapping()
        example_7_complete_workflow()

        print("\n\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Try interactive mode: python scripts/adr_builder.py create")
        print("  2. Search ADRs: python scripts/adr_builder.py search <keyword>")
        print("  3. Check conflicts: python scripts/adr_builder.py conflicts")
        print("  4. Review created ADRs in ADRS/ directory")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
