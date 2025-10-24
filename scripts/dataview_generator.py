"""Dataview Query Generator - Obsidian Dataview Query Generation.

Generates Dataview queries for TAG traceability and statistics.
Integrates with TagSyncBridge for automatic query insertion.

Compliance:
- P1: YAML-First (integrates with YAML contracts)
- P2: Evidence-based (generates traceability queries)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

Features:
- Related TAGs query (same ID, different types)
- Dependency queries (SPEC->CODE, CODE->TEST)
- Status filtering (pending/active/completed)
- Dashboard statistics (type/ID/status summaries)
- Traceability chain queries

Example:
    $ python scripts/dataview_generator.py --tag-id auth-001 --tag-type SPEC
"""

from typing import Dict, List


class DataviewGenerator:
    """Generate Dataview queries for Obsidian.

    Attributes:
        tag_type_mapping: Maps TAG types to hierarchical tags.
    """

    def __init__(self) -> None:
        """Initialize Dataview generator."""
        self.tag_type_mapping = {
            "SPEC": "req",
            "CODE": "impl",
            "TEST": "test",
            "DOC": "doc",
        }

    def generate_related_tags_query(self, tag_id: str) -> str:
        """Generate query for related TAGs with same ID.

        Args:
            tag_id: TAG ID to search for.

        Returns:
            Dataview query string.

        Example:
            >>> generator.generate_related_tags_query("auth-001")
            '```dataview
            TABLE tag_type, code_location
            FROM #req/auth-001 OR #impl/auth-001 OR #test/auth-001 OR #doc/auth-001
            SORT tag_type ASC
            ```'
        """
        # Generate OR conditions for all tag types
        tags = [f"#{prefix}/{tag_id.lower()}" for prefix in self.tag_type_mapping.values()]
        from_clause = " OR ".join(tags)

        query = f"""```dataview
TABLE tag_type, code_location
FROM {from_clause}
SORT tag_type ASC
```"""
        return query

    def generate_dependencies_query(self, tag_id: str, tag_type: str) -> str:
        """Generate query for TAG dependencies.

        Args:
            tag_id: TAG ID.
            tag_type: Source TAG type (SPEC/CODE/TEST/DOC).

        Returns:
            Dataview query for dependencies.

        Example:
            >>> generator.generate_dependencies_query("auth-001", "SPEC")
            # Returns query for CODE and TEST related to this SPEC
        """
        # Define dependency relationships
        dependencies = {
            "SPEC": ["impl", "test", "doc"],  # SPEC depends on implementations and tests
            "CODE": ["req", "test"],  # CODE depends on specs and tests
            "TEST": ["req", "impl"],  # TEST depends on specs and code
            "DOC": ["req", "impl"],  # DOC depends on specs and code
        }

        dep_types = dependencies.get(tag_type, [])
        tags = [f"#{prefix}/{tag_id.lower()}" for prefix in dep_types]
        from_clause = " OR ".join(tags)

        query = f"""```dataview
TABLE tag_type, code_location, file.mtime AS "Last Modified"
FROM {from_clause}
SORT tag_type ASC
```"""
        return query

    def generate_status_query(self, status: str) -> str:
        """Generate query for TAGs by status.

        Args:
            status: Status to filter (pending/active/completed).

        Returns:
            Dataview query string.

        Example:
            >>> generator.generate_status_query("active")
            '```dataview
            TABLE tag_id, tag_type, code_location
            FROM #status/active
            SORT tag_id ASC
            ```'
        """
        query = f"""```dataview
TABLE tag_id, tag_type, code_location
FROM #status/{status}
SORT tag_id ASC
```"""
        return query

    def generate_type_summary_query(self) -> str:
        """Generate summary query grouped by TAG type.

        Returns:
            Dataview query for type summary.

        Example:
            >>> generator.generate_type_summary_query()
            # Returns query showing count per type (SPEC/CODE/TEST/DOC)
        """
        query = """```dataview
TABLE rows.file.link AS "Files", length(rows) AS "Count"
FROM #type/spec OR #type/code OR #type/test OR #type/doc
GROUP BY tag_type
SORT tag_type ASC
```"""
        return query

    def generate_id_summary_query(self) -> str:
        """Generate summary query grouped by TAG ID.

        Returns:
            Dataview query for ID summary.

        Example:
            >>> generator.generate_id_summary_query()
            # Returns query showing all types per ID
        """
        query = """```dataview
TABLE rows.tag_type AS "Types", length(rows) AS "Count"
FROM #req OR #impl OR #test OR #doc
GROUP BY tag_id
SORT tag_id ASC
```"""
        return query

    def generate_status_summary_query(self) -> str:
        """Generate summary query grouped by status.

        Returns:
            Dataview query for status summary.

        Example:
            >>> generator.generate_status_summary_query()
            # Returns query showing count per status
        """
        query = """```dataview
TABLE length(rows) AS "Count"
FROM #status/pending OR #status/active OR #status/completed
GROUP BY split(file.tags[1], "/")[1] AS "Status"
SORT "Status" ASC
```"""
        return query

    def generate_traceability_chain_query(self, tag_id: str) -> str:
        """Generate query for full traceability chain.

        Args:
            tag_id: TAG ID to trace.

        Returns:
            Dataview query showing full chain.

        Example:
            >>> generator.generate_traceability_chain_query("auth-001")
            # Returns query for SPEC -> CODE -> TEST -> DOC chain
        """
        tags = [f"#{prefix}/{tag_id.lower()}" for prefix in self.tag_type_mapping.values()]
        from_clause = " OR ".join(tags)

        query = f"""```dataview
TABLE tag_type, code_location, file.mtime AS "Last Modified"
FROM {from_clause}
SORT tag_type ASC
```"""
        return query

    def generate_missing_implementations_query(self) -> str:
        """Generate query for SPECs without CODE.

        Returns:
            Dataview query for missing implementations.

        Example:
            >>> generator.generate_missing_implementations_query()
            # Returns SPECs that don't have corresponding CODE
        """
        query = """```dataview
LIST
FROM #req
WHERE !contains(string(file.tags), "impl/" + tag_id)
SORT tag_id ASC
```"""
        return query

    def generate_missing_tests_query(self) -> str:
        """Generate query for CODE without TEST.

        Returns:
            Dataview query for missing tests.

        Example:
            >>> generator.generate_missing_tests_query()
            # Returns CODE that doesn't have corresponding TEST
        """
        query = """```dataview
LIST
FROM #impl
WHERE !contains(string(file.tags), "test/" + tag_id)
SORT tag_id ASC
```"""
        return query

    def generate_all_queries(self, tag_id: str, tag_type: str) -> Dict[str, str]:
        """Generate all queries for a specific TAG.

        Args:
            tag_id: TAG ID.
            tag_type: TAG type.

        Returns:
            Dict of query types to query strings.

        Example:
            >>> generator.generate_all_queries("auth-001", "SPEC")
            {
                'related_tags': '```dataview...',
                'dependencies': '```dataview...',
                'traceability': '```dataview...'
            }
        """
        return {
            "related_tags": self.generate_related_tags_query(tag_id),
            "dependencies": self.generate_dependencies_query(tag_id, tag_type),
            "traceability": self.generate_traceability_chain_query(tag_id),
        }

    def format_for_note(self, tag_id: str, tag_type: str) -> str:
        """Format all queries for Obsidian note.

        Args:
            tag_id: TAG ID.
            tag_type: TAG type.

        Returns:
            Formatted content for Obsidian note.

        Example:
            >>> content = generator.format_for_note("auth-001", "SPEC")
            >>> "## Traceability" in content
            True
        """
        queries = self.generate_all_queries(tag_id, tag_type)

        content = "## Traceability\n\n"
        content += "### Related TAGs\n\n"
        content += queries["related_tags"] + "\n\n"

        content += "### Dependencies\n\n"
        content += queries["dependencies"] + "\n\n"

        content += "### Full Chain\n\n"
        content += queries["traceability"] + "\n\n"

        return content


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Dataview Query Generator - Obsidian Dataview Queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/dataview_generator.py --tag-id auth-001 --tag-type SPEC
  python scripts/dataview_generator.py --dashboard
  python scripts/dataview_generator.py --missing-implementations
        """,
    )

    parser.add_argument("--tag-id", type=str, help="TAG ID for queries")
    parser.add_argument("--tag-type", type=str, help="TAG type (SPEC/CODE/TEST/DOC)")
    parser.add_argument("--dashboard", action="store_true", help="Generate dashboard queries")
    parser.add_argument("--missing-implementations", action="store_true", help="Find SPECs without CODE")
    parser.add_argument("--missing-tests", action="store_true", help="Find CODE without TEST")

    args = parser.parse_args()

    print("[INFO] Dataview Query Generator")
    print("")

    try:
        generator = DataviewGenerator()

        if args.dashboard:
            # Generate dashboard queries
            print("## Dashboard Queries\n")
            print("### By Type")
            print(generator.generate_type_summary_query())
            print("\n### By ID")
            print(generator.generate_id_summary_query())
            print("\n### By Status")
            print(generator.generate_status_summary_query())

        elif args.missing_implementations:
            print("## Missing Implementations\n")
            print(generator.generate_missing_implementations_query())

        elif args.missing_tests:
            print("## Missing Tests\n")
            print(generator.generate_missing_tests_query())

        elif args.tag_id and args.tag_type:
            # Generate queries for specific TAG
            print(f"## Queries for {args.tag_type}:{args.tag_id}\n")
            content = generator.format_for_note(args.tag_id, args.tag_type)
            print(content)

        else:
            print("[ERROR] Specify --tag-id and --tag-type, or use --dashboard/--missing-*")
            return 1

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to generate queries: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
