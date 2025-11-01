"""TAG Extractor Lite - @TAG Code Extraction Tool.

Extracts @TAG annotations from source code for Obsidian synchronization.
Uses regex-based pattern matching to find TAG annotations.

Compliance:
- P1: YAML-First (integrates with YAML contracts)
- P2: Evidence-based (generates traceability evidence)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

@TAG Pattern:
    @TAG[TYPE:ID]
    - TYPE: SPEC, TEST, CODE, DOC
    - ID: Unique identifier (e.g., auth-001, REQ-USER-001)

Example:
    $ python scripts/tag_extractor_lite.py
    $ python scripts/tag_extractor_lite.py --file src/auth.py
    $ python scripts/tag_extractor_lite.py --tag-id REQ-AUTH-001
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from feature_flags import FeatureFlags
except ImportError:
    from scripts.feature_flags import FeatureFlags


@dataclass
class CodeTag:
    """Represents a @TAG annotation found in code.

    Attributes:
        tag_type: Type of tag (SPEC/TEST/CODE/DOC).
        tag_id: Unique identifier.
        file_path: Path to source file.
        line_number: Line number where tag appears.
        context: Surrounding code context (3 lines).
    """

    tag_type: str
    tag_id: str
    file_path: Path
    line_number: int
    context: str


class TagExtractorLite:
    """Lightweight @TAG extraction tool.

    Attributes:
        project_root: Root directory for TAG scanning.
        tag_pattern: Regex pattern for @TAG matching.
        file_extensions: Allowed source file extensions.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize TAG extractor.

        Args:
            project_root: Root directory to scan (default: current dir).
        """
        self.project_root = project_root or Path.cwd()
        self.tag_pattern = re.compile(r"@TAG\[([A-Z]+):([^\]]+)\]")
        self.file_extensions = [".py", ".md", ".yaml", ".yml", ".js", ".jsx", ".ts", ".tsx"]

    def extract_tags_from_file(self, file_path: Path) -> List[CodeTag]:
        """Extract all @TAG annotations from a file.

        Args:
            file_path: Path to source file.

        Returns:
            List of CodeTag objects.

        Example:
            >>> extractor.extract_tags_from_file(Path("src/auth.py"))
            [
                CodeTag(
                    tag_type="SPEC",
                    tag_id="auth-001",
                    file_path=Path("src/auth.py"),
                    line_number=15,
                    context="# @TAG[SPEC:auth-001]\ndef validate_token():\n    pass"
                ),
                ...
            ]
        """
        tags: List[CodeTag] = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            for line_num, line in enumerate(lines, start=1):
                for match in self.tag_pattern.finditer(line):
                    tag_type = match.group(1)  # SPEC, TEST, CODE, DOC
                    tag_id = match.group(2)  # auth-001, REQ-USER-001

                    # Get 3-line context (before, current, after)
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context = "\n".join(lines[context_start:context_end])

                    tags.append(
                        CodeTag(
                            tag_type=tag_type,
                            tag_id=tag_id,
                            file_path=file_path,
                            line_number=line_num,
                            context=context,
                        )
                    )
        except Exception:
            # Skip files that can't be read
            pass

        return tags

    def extract_tags_from_directory(self, directory: Optional[Path] = None) -> List[CodeTag]:
        """Extract all @TAG annotations from directory.

        Args:
            directory: Directory to scan (default: project_root).

        Returns:
            List of all CodeTag objects found.
        """
        directory = directory or self.project_root
        all_tags: List[CodeTag] = []

        for file_path in directory.rglob("*"):
            # Skip non-source files
            if file_path.suffix not in self.file_extensions:
                continue

            # Skip hidden directories
            if any(part.startswith(".") or part == "node_modules" for part in file_path.parts):
                continue

            tags = self.extract_tags_from_file(file_path)
            all_tags.extend(tags)

        return all_tags

    def group_by_tag_id(self, tags: List[CodeTag]) -> Dict[str, List[CodeTag]]:
        """Group tags by their tag_id.

        Args:
            tags: List of CodeTag objects.

        Returns:
            Dict mapping tag_id to list of CodeTag objects.

        Example:
            {
                "auth-001": [
                    CodeTag(tag_type="SPEC", ...),
                    CodeTag(tag_type="TEST", ...),
                    CodeTag(tag_type="CODE", ...)
                ]
            }
        """
        grouped: Dict[str, List[CodeTag]] = {}

        for tag in tags:
            if tag.tag_id not in grouped:
                grouped[tag.tag_id] = []
            grouped[tag.tag_id].append(tag)

        return grouped

    def group_by_tag_type(self, tags: List[CodeTag]) -> Dict[str, List[CodeTag]]:
        """Group tags by their tag_type.

        Args:
            tags: List of CodeTag objects.

        Returns:
            Dict mapping tag_type to list of CodeTag objects.

        Example:
            {
                "SPEC": [CodeTag(...), CodeTag(...)],
                "TEST": [CodeTag(...), CodeTag(...)],
                "CODE": [CodeTag(...)]
            }
        """
        grouped: Dict[str, List[CodeTag]] = {}

        for tag in tags:
            if tag.tag_type not in grouped:
                grouped[tag.tag_type] = []
            grouped[tag.tag_type].append(tag)

        return grouped

    def find_tags_by_id(self, tag_id: str) -> List[CodeTag]:
        """Find all tags with specific tag_id.

        Args:
            tag_id: Tag identifier to search for.

        Returns:
            List of CodeTag objects matching tag_id.
        """
        all_tags = self.extract_tags_from_directory()
        return [tag for tag in all_tags if tag.tag_id == tag_id]

    def find_tags_by_type(self, tag_type: str) -> List[CodeTag]:
        """Find all tags with specific tag_type.

        Args:
            tag_type: Tag type to search for (SPEC/TEST/CODE/DOC).

        Returns:
            List of CodeTag objects matching tag_type.
        """
        all_tags = self.extract_tags_from_directory()
        return [tag for tag in all_tags if tag.tag_type == tag_type]

    def print_summary(self, tags: List[CodeTag]) -> None:
        """Print extraction summary.

        Args:
            tags: List of CodeTag objects to summarize.
        """
        if not tags:
            print("[INFO] No @TAG annotations found")
            return

        print(f"[INFO] Found {len(tags)} @TAG annotations")
        print("")

        # Group by type
        by_type = self.group_by_tag_type(tags)
        for tag_type, type_tags in sorted(by_type.items()):
            print(f"  {tag_type}: {len(type_tags)}")

        # Group by ID
        by_id = self.group_by_tag_id(tags)
        print("")
        print(f"[INFO] Total unique tag IDs: {len(by_id)}")

        # Show tag IDs
        for tag_id, id_tags in sorted(by_id.items()):
            types = ", ".join(sorted({tag.tag_type for tag in id_tags}))
            print(f"  {tag_id}: [{types}]")


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="TAG Extractor Lite - @TAG Code Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tag_extractor_lite.py
  python scripts/tag_extractor_lite.py --file src/auth.py
  python scripts/tag_extractor_lite.py --tag-id REQ-AUTH-001
  python scripts/tag_extractor_lite.py --tag-type SPEC
        """,
    )

    parser.add_argument("--file", type=str, help="Extract from specific file")
    parser.add_argument("--tag-id", type=str, help="Find specific tag ID")
    parser.add_argument("--tag-type", type=str, help="Find specific tag type (SPEC/TEST/CODE/DOC)")

    args = parser.parse_args()

    # Check feature flags
    flags = FeatureFlags()
    if not flags.is_enabled("tier1_integration.tools.tag_extractor"):
        print("[ERROR] tag_extractor is disabled by feature flag")
        print("Enable with: python scripts/tier1_cli.py enable tag_extractor")
        return 1

    print("[INFO] TAG Extractor Lite - @TAG Code Extraction")
    print("")

    try:
        extractor = TagExtractorLite()

        if args.file:
            # Extract from specific file
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"[ERROR] File not found: {file_path}")
                return 1

            tags = extractor.extract_tags_from_file(file_path)
            print(f"[INFO] Extracting from: {file_path}")
            extractor.print_summary(tags)

            # Print details
            if tags:
                print("")
                print("=" * 60)
                for tag in tags:
                    print(f"Line {tag.line_number}: @TAG[{tag.tag_type}:{tag.tag_id}]")
                    print(f"Context:\n{tag.context}")
                    print("-" * 60)

        elif args.tag_id:
            # Find by tag ID
            tags = extractor.find_tags_by_id(args.tag_id)
            print(f"[INFO] Searching for tag ID: {args.tag_id}")
            extractor.print_summary(tags)

            # Print details
            if tags:
                print("")
                print("=" * 60)
                for tag in tags:
                    print(f"[{tag.tag_type}] {tag.file_path}:{tag.line_number}")
                    print(f"Context:\n{tag.context}")
                    print("-" * 60)

        elif args.tag_type:
            # Find by tag type
            tags = extractor.find_tags_by_type(args.tag_type)
            print(f"[INFO] Searching for tag type: {args.tag_type}")
            extractor.print_summary(tags)

            # Print details
            if tags:
                print("")
                print("=" * 60)
                for tag in tags:
                    print(f"[{tag.tag_id}] {tag.file_path}:{tag.line_number}")
                    print(f"Context:\n{tag.context}")
                    print("-" * 60)

        else:
            # Extract all from project
            tags = extractor.extract_tags_from_directory()
            print("[INFO] Extracting from entire project")
            extractor.print_summary(tags)

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to extract @TAG annotations: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
