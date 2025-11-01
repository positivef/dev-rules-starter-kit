"""TAG Sync Bridge Lite - @TAG to Obsidian Synchronization.

Synchronizes @TAG annotations from code to Obsidian notes.
Extends ObsidianBridge with TAG-specific functionality.

Compliance:
- P1: YAML-First (integrates with YAML contracts)
- P2: Evidence-based (generates traceability notes)
- P4: SOLID principles (extends ObsidianBridge)
- P10: Windows encoding (UTF-8, no emojis)

Features:
- Automatic Obsidian note generation from @TAG
- Hierarchical tag mapping (#req/auth-001)
- Traceability links (SPEC -> TEST -> CODE -> DOC)
- Dataview query generation

Example:
    $ python scripts/tag_sync_bridge_lite.py
    $ python scripts/tag_sync_bridge_lite.py --tag-id REQ-AUTH-001
    $ python scripts/tag_sync_bridge_lite.py --vault-path "C:/Obsidian"
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dataview_generator import DataviewGenerator
    from feature_flags import FeatureFlags
    from mermaid_graph_generator import MermaidGraphGenerator
    from obsidian_bridge import ObsidianBridge
    from security_utils import MemorySafeResourceManager
    from tag_extractor_lite import CodeTag, TagExtractorLite
except ImportError:
    from scripts.dataview_generator import DataviewGenerator
    from scripts.feature_flags import FeatureFlags
    from scripts.mermaid_graph_generator import MermaidGraphGenerator
    from scripts.obsidian_bridge import ObsidianBridge
    from scripts.security_utils import MemorySafeResourceManager
    from scripts.tag_extractor_lite import CodeTag, TagExtractorLite


class TagSyncBridgeLite(ObsidianBridge):
    """TAG synchronization bridge for Obsidian.

    Extends ObsidianBridge with @TAG-specific functionality.

    Attributes:
        vault_path: Obsidian Vault path.
        tag_extractor: TagExtractorLite instance for tag extraction.
        requirements_dir: Directory for requirement notes.
        implementations_dir: Directory for implementation notes.
        tests_dir: Directory for test notes.
        docs_dir: Directory for documentation notes.
    """

    def __init__(self, vault_path: Optional[Path] = None, project_root: Optional[Path] = None) -> None:
        """Initialize TAG sync bridge.

        Args:
            vault_path: Obsidian Vault path (default: from environment).
            project_root: Project root for TAG extraction.
        """
        super().__init__(vault_path)

        # Initialize memory-safe resource manager
        self.resource_manager = MemorySafeResourceManager()

        # TAG-specific directories
        self.requirements_dir = self.vault_path / "requirements"
        self.implementations_dir = self.vault_path / "implementations"
        self.tests_dir = self.vault_path / "tests"
        self.docs_dir = self.vault_path / "docs"

        # Create directories
        for directory in [self.requirements_dir, self.implementations_dir, self.tests_dir, self.docs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # TAG extractor (register for cleanup)
        self.tag_extractor = TagExtractorLite(project_root=project_root)
        self.resource_manager.register_resource(self.tag_extractor)

        # Dataview generator (register for cleanup)
        self.dataview_generator = DataviewGenerator()
        self.resource_manager.register_resource(self.dataview_generator)

        # Mermaid graph generator (register for cleanup)
        self.mermaid_generator = MermaidGraphGenerator()
        self.resource_manager.register_resource(self.mermaid_generator)

    def create_tag_note(self, tag: CodeTag) -> Path:
        """Create Obsidian note for @TAG.

        Args:
            tag: CodeTag object.

        Returns:
            Path to created note.

        Example:
            >>> bridge.create_tag_note(CodeTag(
            ...     tag_type="SPEC",
            ...     tag_id="auth-001",
            ...     file_path=Path("src/auth.py"),
            ...     line_number=15,
            ...     context="# @TAG[SPEC:auth-001]"
            ... ))
            PosixPath('vault/requirements/REQ-AUTH-001.md')
        """
        # Determine target directory
        if tag.tag_type == "SPEC":
            target_dir = self.requirements_dir
            note_prefix = "REQ"
        elif tag.tag_type == "CODE":
            target_dir = self.implementations_dir
            note_prefix = "IMPL"
        elif tag.tag_type == "TEST":
            target_dir = self.tests_dir
            note_prefix = "TEST"
        else:  # DOC
            target_dir = self.docs_dir
            note_prefix = "DOC"

        # Generate filename
        filename = f"{note_prefix}-{tag.tag_id.upper()}.md"
        note_path = target_dir / filename

        # Check if note already exists
        if note_path.exists():
            # Update existing note
            return self._update_tag_note(note_path, tag)

        # Generate hierarchical tag
        hierarchical_tag = self._generate_hierarchical_tag(tag)

        # Generate frontmatter
        frontmatter = {
            "tags": [hierarchical_tag, f"type/{tag.tag_type.lower()}", "status/active"],
            "tag_id": tag.tag_id,
            "tag_type": tag.tag_type,
            "code_location": f"{tag.file_path}:{tag.line_number}",
            "created": datetime.now().strftime("%Y-%m-%d"),
        }

        # Generate content
        content = self._generate_tag_note_content(tag)

        # Write note
        note_path.write_text(self._format_markdown(frontmatter, content), encoding="utf-8")

        return note_path

    def _update_tag_note(self, note_path: Path, tag: CodeTag) -> Path:
        """Update existing TAG note with new location.

        Args:
            note_path: Path to existing note.
            tag: CodeTag object.

        Returns:
            Path to updated note.
        """
        # Read existing content
        content = note_path.read_text(encoding="utf-8")

        # Add new location reference
        location_line = f"- `{tag.file_path}:{tag.line_number}`"

        if "## Code Locations" in content:
            # Append to existing locations section
            if location_line not in content:
                content = content.replace("## Code Locations\n", f"## Code Locations\n{location_line}\n")
        else:
            # Add locations section before "## Context"
            locations_section = f"\n## Code Locations\n{location_line}\n"
            if "## Context" in content:
                content = content.replace("## Context", f"{locations_section}\n## Context")
            else:
                content += locations_section

        # Write updated content
        note_path.write_text(content, encoding="utf-8")

        return note_path

    def _generate_hierarchical_tag(self, tag: CodeTag) -> str:
        """Generate hierarchical Obsidian tag.

        Args:
            tag: CodeTag object.

        Returns:
            Hierarchical tag string.

        Example:
            >>> bridge._generate_hierarchical_tag(CodeTag(tag_type="SPEC", tag_id="auth-001", ...))
            'req/auth-001'
        """
        # Map TAG type to Obsidian tag prefix
        tag_prefix = {
            "SPEC": "req",
            "CODE": "impl",
            "TEST": "test",
            "DOC": "doc",
        }.get(tag.tag_type, tag.tag_type.lower())

        return f"{tag_prefix}/{tag.tag_id.lower()}"

    def _generate_tag_note_content(self, tag: CodeTag) -> str:
        """Generate content for TAG note.

        Args:
            tag: CodeTag object.

        Returns:
            Note content string.
        """
        # Title
        content = f"# {tag.tag_type}: {tag.tag_id.upper()}\n\n"

        # Description
        if tag.tag_type == "SPEC":
            content += "## Requirement\n\n(Add requirement description)\n\n"
        elif tag.tag_type == "CODE":
            content += "## Implementation\n\n(Add implementation details)\n\n"
        elif tag.tag_type == "TEST":
            content += "## Test Cases\n\n(Add test cases)\n\n"
        else:  # DOC
            content += "## Documentation\n\n(Add documentation)\n\n"

        # Code location
        content += "## Code Locations\n\n"
        content += f"- `{tag.file_path}:{tag.line_number}`\n\n"

        # Context
        content += "## Context\n\n"
        content += "```\n"
        content += tag.context
        content += "\n```\n\n"

        # Traceability links with Dataview queries
        content += self.dataview_generator.format_for_note(tag.tag_id, tag.tag_type)

        # Metadata
        content += "---\n\n"
        content += f"**Created**: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += f"**Type**: {tag.tag_type}\n"
        content += f"**ID**: {tag.tag_id}\n"

        return content

    def sync_all_tags(self, tag_id: Optional[str] = None) -> Dict[str, List[Path]]:
        """Synchronize all @TAG annotations to Obsidian.

        Args:
            tag_id: Optional specific TAG ID to sync.

        Returns:
            Dict mapping TAG types to list of created note paths.

        Example:
            >>> bridge.sync_all_tags()
            {
                'SPEC': [PosixPath('vault/requirements/REQ-AUTH-001.md')],
                'TEST': [PosixPath('vault/tests/TEST-AUTH-001.md')],
                'CODE': [PosixPath('vault/implementations/IMPL-AUTH-001.md')]
            }
        """
        # Extract tags from project
        if tag_id:
            tags = self.tag_extractor.find_tags_by_id(tag_id)
        else:
            tags = self.tag_extractor.extract_tags_from_directory()

        # Group by type
        created_notes: Dict[str, List[Path]] = {"SPEC": [], "CODE": [], "TEST": [], "DOC": []}

        # Create notes for each tag
        for tag in tags:
            note_path = self.create_tag_note(tag)
            created_notes[tag.tag_type].append(note_path)

        return created_notes

    def generate_traceability_map(self, tag_id: str) -> Optional[Path]:
        """Generate traceability map for TAG chain.

        Args:
            tag_id: TAG ID to trace.

        Returns:
            Path to traceability map note.

        Example:
            >>> bridge.generate_traceability_map("auth-001")
            PosixPath('vault/traceability/auth-001-map.md')
        """
        # Find all tags with this ID
        tags = self.tag_extractor.find_tags_by_id(tag_id)

        if not tags:
            return None

        # Create traceability directory
        trace_dir = self.vault_path / "traceability"
        trace_dir.mkdir(parents=True, exist_ok=True)

        # Generate traceability map
        map_path = trace_dir / f"{tag_id.lower()}-map.md"

        # Frontmatter
        frontmatter = {
            "tags": [f"trace/{tag_id.lower()}", "type/traceability"],
            "tag_id": tag_id,
            "created": datetime.now().strftime("%Y-%m-%d"),
        }

        # Content
        content = f"# Traceability Map: {tag_id.upper()}\n\n"

        # Group tags by type
        by_type = {}
        for tag in tags:
            if tag.tag_type not in by_type:
                by_type[tag.tag_type] = []
            by_type[tag.tag_type].append(tag)

        # Add sections for each type
        for tag_type in ["SPEC", "CODE", "TEST", "DOC"]:
            if tag_type in by_type:
                content += f"## {tag_type}\n\n"
                for tag in by_type[tag_type]:
                    content += f"- `{tag.file_path}:{tag.line_number}`\n"
                content += "\n"

        # Add advanced Mermaid diagram
        content += "## Traceability Graph\n\n"
        content += self.mermaid_generator.generate_advanced_graph(by_type, tag_id)
        content += "\n"

        # Write note
        map_path.write_text(self._format_markdown(frontmatter, content), encoding="utf-8")

        return map_path

    def print_sync_summary(self, created_notes: Dict[str, List[Path]]) -> None:
        """Print synchronization summary.

        Args:
            created_notes: Dict of created note paths by type.
        """
        total = sum(len(notes) for notes in created_notes.values())

        print(f"[INFO] Synchronized {total} @TAG annotations to Obsidian")
        print("")

        for tag_type, notes in sorted(created_notes.items()):
            if notes:
                print(f"  {tag_type}: {len(notes)} notes")

        print("")
        print("[INFO] Notes created in:")
        print(f"  - Requirements: {self.requirements_dir}")
        print(f"  - Implementations: {self.implementations_dir}")
        print(f"  - Tests: {self.tests_dir}")
        print(f"  - Docs: {self.docs_dir}")

    def cleanup(self) -> None:
        """Clean up all managed resources.

        Ensures proper resource cleanup to prevent memory leaks.
        """
        if hasattr(self, "resource_manager"):
            self.resource_manager.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def __del__(self):
        """Destructor - ensure cleanup on deletion."""
        self.cleanup()


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="TAG Sync Bridge Lite - @TAG to Obsidian Synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tag_sync_bridge_lite.py
  python scripts/tag_sync_bridge_lite.py --tag-id REQ-AUTH-001
  python scripts/tag_sync_bridge_lite.py --vault-path "C:/Obsidian"
  python scripts/tag_sync_bridge_lite.py --generate-map auth-001
        """,
    )

    parser.add_argument("--vault-path", type=str, help="Obsidian Vault path")
    parser.add_argument("--tag-id", type=str, help="Sync specific TAG ID only")
    parser.add_argument("--generate-map", type=str, help="Generate traceability map for TAG ID")

    args = parser.parse_args()

    # Check feature flags
    flags = FeatureFlags()
    if not flags.is_enabled("tier1_integration.tools.tag_sync_bridge"):
        print("[ERROR] tag_sync_bridge is disabled by feature flag")
        print("Enable with: python scripts/tier1_cli.py enable tag_sync_bridge")
        return 1

    print("[INFO] TAG Sync Bridge Lite - @TAG to Obsidian Synchronization")
    print("")

    try:
        # Get vault path
        vault_path = Path(args.vault_path) if args.vault_path else Path(os.getenv("OBSIDIAN_VAULT_PATH", "."))

        if not vault_path.exists():
            print(f"[ERROR] Vault path does not exist: {vault_path}")
            print("[INFO] Set OBSIDIAN_VAULT_PATH environment variable or use --vault-path")
            return 1

        # Initialize bridge with context manager for proper cleanup
        with TagSyncBridgeLite(vault_path=vault_path) as bridge:
            if args.generate_map:
                # Generate traceability map
                print(f"[INFO] Generating traceability map for: {args.generate_map}")
                map_path = bridge.generate_traceability_map(args.generate_map)

                if map_path:
                    print(f"[OK] Traceability map created: {map_path}")
                else:
                    print(f"[ERROR] No tags found for: {args.generate_map}")
                    return 1

            else:
                # Sync all tags
                if args.tag_id:
                    print(f"[INFO] Syncing TAG ID: {args.tag_id}")
                else:
                    print("[INFO] Syncing all @TAG annotations")

                created_notes = bridge.sync_all_tags(tag_id=args.tag_id)
                bridge.print_sync_summary(created_notes)

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to synchronize @TAG annotations: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
