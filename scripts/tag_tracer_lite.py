"""TAG Tracer Lite - @TAG Chain Verification Tool.

Verifies @TAG chain integrity for requirement traceability.
Uses regex-based pattern matching to find and validate TAG chains.

Compliance:
- P1: YAML-First (works with YAML contracts)
- P2: Evidence-based (generates traceability reports)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

@TAG Pattern:
    @TAG[TYPE:ID]
    - TYPE: SPEC, TEST, CODE, DOC
    - ID: Unique identifier (e.g., auth-001, REQ-USER-001)

Example:
    $ python scripts/tag_tracer_lite.py
    $ python scripts/tag_tracer_lite.py --tag-id REQ-USER-001
    $ python scripts/tag_tracer_lite.py --validate
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    from feature_flags import FeatureFlags
except ImportError:
    from scripts.feature_flags import FeatureFlags


class TagTracerLite:
    """Lightweight @TAG chain verification tool.

    Attributes:
        project_root: Root directory for TAG scanning.
        tag_pattern: Regex pattern for @TAG matching.
        chain_types: Expected TAG types in chain.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize TAG tracer.

        Args:
            project_root: Root directory to scan (default: current dir).
        """
        self.project_root = project_root or Path.cwd()
        self.tag_pattern = re.compile(r"@TAG\[([A-Z]+):([^\]]+)\]")
        self.chain_types = ["SPEC", "TEST", "CODE", "DOC"]
        self.file_extensions = [".py", ".md", ".yaml", ".yml"]

    def collect_all_tags(self) -> Dict[str, List[str]]:
        """Collect all @TAG patterns from project files.

        Returns:
            Dict mapping TAG keys (TYPE:ID) to file locations.

        Example:
            {
                "SPEC:auth-001": ["docs/SPEC_AUTH.md:15"],
                "TEST:auth-001": ["tests/test_auth.py:10"],
                "CODE:auth-001": ["scripts/auth.py:45"]
            }
        """
        tags: Dict[str, List[str]] = {}

        for file_path in self.project_root.rglob("*"):
            # Skip non-source files
            if file_path.suffix not in self.file_extensions:
                continue

            # Skip node_modules, .git, etc.
            if any(part.startswith(".") or part == "node_modules" for part in file_path.parts):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                for match in self.tag_pattern.finditer(content):
                    tag_type = match.group(1)  # SPEC, TEST, CODE, DOC
                    tag_id = match.group(2)  # auth-001, REQ-USER-001
                    tag_key = f"{tag_type}:{tag_id}"

                    if tag_key not in tags:
                        tags[tag_key] = []

                    # Calculate line number
                    line_num = content[: match.start()].count("\n") + 1
                    relative_path = file_path.relative_to(self.project_root)
                    tags[tag_key].append(f"{relative_path}:{line_num}")
            except Exception:
                # Skip files that can't be read
                continue

        return tags

    def build_chains(self, tags: Dict[str, List[str]]) -> List[Dict]:
        """Build TAG chains grouped by ID.

        Args:
            tags: Dict of TAG keys to file locations.

        Returns:
            List of chain dictionaries with id, types, missing, and locations.

        Example:
            [
                {
                    "id": "auth-001",
                    "types": ["SPEC", "TEST", "CODE"],
                    "missing": ["DOC"],
                    "locations": {
                        "SPEC": ["docs/SPEC_AUTH.md:15"],
                        "TEST": ["tests/test_auth.py:10"],
                        "CODE": ["scripts/auth.py:45"]
                    }
                }
            ]
        """
        # Group by tag_id
        by_id: Dict[str, Dict] = {}

        for tag_key, locations in tags.items():
            tag_type, tag_id = tag_key.split(":", 1)

            if tag_id not in by_id:
                by_id[tag_id] = {"id": tag_id, "types": [], "missing": [], "locations": {}}

            by_id[tag_id]["types"].append(tag_type)
            by_id[tag_id]["locations"][tag_type] = locations

        # Identify missing TAG types
        for tag_id, data in by_id.items():
            for expected in self.chain_types:
                if expected not in data["types"]:
                    data["missing"].append(expected)

        return list(by_id.values())

    def find_orphan_tags(self, chains: List[Dict]) -> List[str]:
        """Find orphan TAGs (only one type in chain).

        Args:
            chains: List of chain dictionaries.

        Returns:
            List of orphan TAG IDs.
        """
        orphans = []
        for chain in chains:
            if len(chain["types"]) == 1:
                orphans.append(chain["id"])
        return orphans

    def verify_tag_chain(self, tag_id: Optional[str] = None) -> Dict:
        """Verify TAG chain integrity.

        Args:
            tag_id: Optional specific TAG ID to verify.

        Returns:
            Verification report dictionary.
        """
        print("[INFO] TAG Tracer - Scanning for @TAG patterns...")

        # Collect all TAGs
        tags = self.collect_all_tags()
        print(f"[INFO] Found {len(tags)} TAG instances")

        # Build chains
        chains = self.build_chains(tags)

        # Filter by specific tag_id if provided
        if tag_id:
            chains = [c for c in chains if c["id"] == tag_id]
            if not chains:
                print(f"[ERROR] TAG ID '{tag_id}' not found")
                return {"error": f"TAG ID '{tag_id}' not found"}

        # Find issues
        orphans = self.find_orphan_tags(chains)
        incomplete = [c for c in chains if c["missing"]]
        complete = [c for c in chains if not c["missing"]]

        # Build report
        report = {
            "total_tags": len(tags),
            "total_chains": len(chains),
            "complete_chains": len(complete),
            "incomplete_chains": len(incomplete),
            "orphan_tags": orphans,
            "chains": chains,
        }

        self.print_report(report)
        return report

    def print_report(self, report: Dict) -> None:
        """Print verification report.

        Args:
            report: Verification report dictionary.
        """
        if "error" in report:
            return

        print("")
        print("=== TAG Chain Verification Report ===")
        print("")
        print(f"Total TAG instances: {report['total_tags']}")
        print(f"Total TAG chains: {report['total_chains']}")
        print(f"Complete chains: {report['complete_chains']}")
        print(f"Incomplete chains: {report['incomplete_chains']}")

        if report["orphan_tags"]:
            print("")
            print("[WARN] Orphan TAGs (only 1 type):")
            for orphan in report["orphan_tags"]:
                print(f"  - {orphan}")

        if report["incomplete_chains"] > 0:
            print("")
            print("[WARN] Incomplete chains:")
            for chain in report["chains"]:
                if chain["missing"]:
                    print(f"  - {chain['id']}: missing {', '.join(chain['missing'])}")
                    print(f"    Present: {', '.join(chain['types'])}")

        if report["complete_chains"] == report["total_chains"]:
            print("")
            print("[OK] All TAG chains are complete!")

    def validate_chain(self, tag_id: str) -> bool:
        """Validate a specific TAG chain.

        Args:
            tag_id: TAG ID to validate.

        Returns:
            True if chain is complete, False otherwise.
        """
        report = self.verify_tag_chain(tag_id=tag_id)

        if "error" in report:
            return False

        # Check if chain is complete
        if report["chains"]:
            chain = report["chains"][0]
            return len(chain["missing"]) == 0

        return False


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="TAG Tracer Lite - @TAG Chain Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tag_tracer_lite.py
  python scripts/tag_tracer_lite.py --tag-id REQ-USER-001
  python scripts/tag_tracer_lite.py --validate --tag-id auth-001
        """,
    )

    parser.add_argument("--tag-id", type=str, help="Specific TAG ID to verify")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Exit with error if TAG chain is incomplete",
    )

    args = parser.parse_args()

    # Check feature flags
    flags = FeatureFlags()
    if not flags.is_enabled("tier1_integration.tools.tag_tracer"):
        print("[ERROR] tag_tracer is disabled by feature flag")
        print("Enable with: python scripts/tier1_cli.py enable tag_tracer")
        return 1

    print("[INFO] TAG Tracer Lite - @TAG Chain Verification")
    print("")

    try:
        tracer = TagTracerLite()

        if args.validate and args.tag_id:
            # Validate specific TAG chain
            is_valid = tracer.validate_chain(args.tag_id)
            if not is_valid:
                print("")
                print(f"[ERROR] TAG chain '{args.tag_id}' is incomplete")
                return 1
            print("")
            print(f"[OK] TAG chain '{args.tag_id}' is complete")
            return 0
        else:
            # Verify all TAG chains
            report = tracer.verify_tag_chain(tag_id=args.tag_id)

            if "error" in report:
                return 1

            # Exit with error if there are incomplete chains
            if args.validate and report["incomplete_chains"] > 0:
                print("")
                print(f"[ERROR] Found {report['incomplete_chains']} incomplete TAG chains")
                return 1

            return 0

    except Exception as e:
        print(f"[ERROR] Failed to verify TAG chains: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
