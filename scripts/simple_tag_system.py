"""Simplified TAG System for Tier 1 Integration.

Provides simpler TAG format with backward compatibility.
"""

import re
from typing import Dict, List, Optional, Tuple


class SimpleTagSystem:
    """Simplified TAG management with better usability."""

    # Simple TAG format: #REQ-001, #IMPL-002, #TEST-003
    SIMPLE_PATTERN = r"#([A-Z]+)-(\d+)"

    # Legacy complex format: @TAG[TYPE:ID]
    LEGACY_PATTERN = r"@TAG\[([A-Z]+):([A-Z0-9-]+)\]"

    # Common tag types with friendly names
    TAG_TYPES = {
        "REQ": "Requirement",
        "IMPL": "Implementation",
        "TEST": "Test",
        "BUG": "Bug Fix",
        "DOC": "Documentation",
        "PERF": "Performance",
        "SEC": "Security",
        "UI": "User Interface",
        "API": "API Change",
        "DB": "Database",
    }

    def __init__(self, use_simple: bool = True):
        """Initialize tag system.

        Args:
            use_simple: Use simplified format (default: True).
        """
        self.use_simple = use_simple
        self.tags: Dict[str, Dict] = {}

    def parse_tag(self, text: str) -> List[Tuple[str, str]]:
        """Parse tags from text supporting both formats.

        Args:
            text: Text containing tags.

        Returns:
            List of (type, id) tuples.
        """
        tags = []

        # Parse simple format
        for match in re.finditer(self.SIMPLE_PATTERN, text):
            tag_type, tag_id = match.groups()
            tags.append((tag_type, tag_id))

        # Parse legacy format
        for match in re.finditer(self.LEGACY_PATTERN, text):
            tag_type, tag_id = match.groups()
            tags.append((tag_type, tag_id))

        return tags

    def format_tag(self, tag_type: str, tag_id: str) -> str:
        """Format a tag in the appropriate format.

        Args:
            tag_type: Tag type (e.g., 'REQ').
            tag_id: Tag ID (e.g., '001').

        Returns:
            Formatted tag string.
        """
        if self.use_simple:
            return f"#{tag_type}-{tag_id}"
        else:
            return f"@TAG[{tag_type}:{tag_id}]"

    def convert_to_simple(self, text: str) -> str:
        """Convert legacy tags to simple format.

        Args:
            text: Text with legacy tags.

        Returns:
            Text with simple tags.
        """

        def replacer(match):
            tag_type, tag_id = match.groups()
            return f"#{tag_type}-{tag_id}"

        return re.sub(self.LEGACY_PATTERN, replacer, text)

    def convert_to_legacy(self, text: str) -> str:
        """Convert simple tags to legacy format.

        Args:
            text: Text with simple tags.

        Returns:
            Text with legacy tags.
        """

        def replacer(match):
            tag_type, tag_id = match.groups()
            return f"@TAG[{tag_type}:{tag_id}]"

        return re.sub(self.SIMPLE_PATTERN, replacer, text)

    def add_tag(self, tag_type: str, tag_id: str, description: str = "") -> str:
        """Add a new tag to the system.

        Args:
            tag_type: Tag type.
            tag_id: Tag ID.
            description: Tag description.

        Returns:
            Formatted tag string.
        """
        key = f"{tag_type}-{tag_id}"
        self.tags[key] = {
            "type": tag_type,
            "id": tag_id,
            "description": description,
            "references": [],
        }
        return self.format_tag(tag_type, tag_id)

    def link_tags(self, from_tag: str, to_tag: str) -> bool:
        """Link two tags together.

        Args:
            from_tag: Source tag.
            to_tag: Target tag.

        Returns:
            True if successful.
        """
        # Parse tags
        from_tags = self.parse_tag(from_tag)
        to_tags = self.parse_tag(to_tag)

        if not from_tags or not to_tags:
            return False

        from_key = f"{from_tags[0][0]}-{from_tags[0][1]}"
        to_key = f"{to_tags[0][0]}-{to_tags[0][1]}"

        if from_key in self.tags:
            self.tags[from_key]["references"].append(to_key)
            return True

        return False

    def generate_next_id(self, tag_type: str) -> str:
        """Generate next available ID for a tag type.

        Args:
            tag_type: Tag type.

        Returns:
            Next ID (e.g., '004').
        """
        max_id = 0
        for key in self.tags:
            if key.startswith(f"{tag_type}-"):
                try:
                    tag_id = int(key.split("-")[1])
                    max_id = max(max_id, tag_id)
                except ValueError:
                    continue

        return f"{max_id + 1:03d}"

    def get_tag_info(self, tag: str) -> Optional[Dict]:
        """Get information about a tag.

        Args:
            tag: Tag string in any format.

        Returns:
            Tag information dictionary.
        """
        parsed = self.parse_tag(tag)
        if not parsed:
            return None

        tag_type, tag_id = parsed[0]
        key = f"{tag_type}-{tag_id}"
        return self.tags.get(key)

    def format_summary(self) -> str:
        """Format a summary of all tags.

        Returns:
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TAG System Summary")
        lines.append("=" * 60)

        # Group by type
        by_type: Dict[str, List[str]] = {}
        for key, info in self.tags.items():
            tag_type = info["type"]
            if tag_type not in by_type:
                by_type[tag_type] = []
            by_type[tag_type].append(key)

        for tag_type in sorted(by_type.keys()):
            type_name = self.TAG_TYPES.get(tag_type, tag_type)
            lines.append(f"\n{type_name} ({tag_type}):")
            lines.append("-" * 40)

            for key in sorted(by_type[tag_type]):
                info = self.tags[key]
                tag_str = self.format_tag(info["type"], info["id"])
                desc = info.get("description", "")
                if desc:
                    lines.append(f"  {tag_str:15} - {desc}")
                else:
                    lines.append(f"  {tag_str}")

                # Show references
                refs = info.get("references", [])
                if refs:
                    lines.append(f"    → Links to: {', '.join(refs)}")

        lines.append("=" * 60)
        return "\n".join(lines)


class TagSimplifier:
    """Utility to simplify existing TAG usage in codebase."""

    @staticmethod
    def simplify_file(file_path: str, backup: bool = True) -> int:
        """Simplify tags in a single file.

        Args:
            file_path: Path to file.
            backup: Create backup before modifying.

        Returns:
            Number of tags simplified.
        """
        import shutil
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            return 0

        # Read file
        content = path.read_text(encoding="utf-8")

        # Count legacy tags
        legacy_count = len(re.findall(SimpleTagSystem.LEGACY_PATTERN, content))

        if legacy_count == 0:
            return 0

        # Create backup if requested
        if backup:
            backup_path = path.with_suffix(path.suffix + ".backup")
            shutil.copy2(path, backup_path)

        # Convert tags
        tag_system = SimpleTagSystem()
        new_content = tag_system.convert_to_simple(content)

        # Write back
        path.write_text(new_content, encoding="utf-8")

        return legacy_count

    @staticmethod
    def simplify_directory(directory: str, pattern: str = "*.py") -> Dict[str, int]:
        """Simplify tags in all files in directory.

        Args:
            directory: Directory path.
            pattern: File pattern to match.

        Returns:
            Dictionary of file paths and counts.
        """
        from pathlib import Path

        results = {}
        dir_path = Path(directory)

        for file_path in dir_path.rglob(pattern):
            count = TagSimplifier.simplify_file(str(file_path))
            if count > 0:
                results[str(file_path)] = count

        return results


def main():
    """Demonstrate simplified TAG system."""
    print("\n=== Simplified TAG System Demo ===\n")

    # Create tag system
    tags = SimpleTagSystem(use_simple=True)

    # Add some tags
    req1 = tags.add_tag("REQ", "001", "User authentication")
    impl1 = tags.add_tag("IMPL", "001", "JWT implementation")
    test1 = tags.add_tag("TEST", "001", "Auth unit tests")

    print("Created tags:")
    print(f"  {req1}")
    print(f"  {impl1}")
    print(f"  {test1}")

    # Link tags
    tags.link_tags(req1, impl1)
    tags.link_tags(impl1, test1)

    # Parse example text
    text = "Fixed #BUG-042 related to #REQ-001 authentication"
    parsed = tags.parse_tag(text)
    print(f"\nParsed from text: '{text}'")
    for tag_type, tag_id in parsed:
        print(f"  Type: {tag_type}, ID: {tag_id}")

    # Convert formats
    legacy = "@TAG[PERF:OPT-001] @TAG[SEC:VULN-002]"
    simple = tags.convert_to_simple(legacy)
    print("\nFormat conversion:")
    print(f"  Legacy: {legacy}")
    print(f"  Simple: {simple}")

    # Generate next ID
    next_req = tags.generate_next_id("REQ")
    print(f"\nNext REQ ID: {next_req}")

    # Print summary
    print(tags.format_summary())


if __name__ == "__main__":
    main()
