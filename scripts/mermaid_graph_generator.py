"""Mermaid Graph Generator - Advanced Traceability Diagrams.

Generates enhanced Mermaid diagrams for TAG traceability visualization.
Supports color coding, bidirectional links, and detailed node information.

Compliance:
- P1: YAML-First (integrates with YAML contracts)
- P2: Evidence-based (generates visual evidence)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

Features:
- Status-based color coding (pending/active/completed)
- Bidirectional link visualization
- Code location in node labels
- Hierarchical layout (SPEC -> CODE -> TEST -> DOC)
- Click handlers for Obsidian integration

Example:
    $ python scripts/mermaid_graph_generator.py --tag-id auth-001
"""

from pathlib import Path
from typing import Dict, List

try:
    from tag_extractor_lite import CodeTag
except ImportError:
    from scripts.tag_extractor_lite import CodeTag


class MermaidGraphGenerator:
    """Generate enhanced Mermaid diagrams for traceability.

    Attributes:
        color_scheme: Status-based color mapping.
        shape_mapping: TAG type to node shape mapping.
    """

    def __init__(self) -> None:
        """Initialize Mermaid graph generator."""
        # Status-based color scheme
        self.color_scheme = {
            "pending": "#FFA500",  # Orange
            "active": "#4CAF50",  # Green
            "completed": "#2196F3",  # Blue
            "default": "#9E9E9E",  # Gray
        }

        # Node shape per TAG type
        self.shape_mapping = {
            "SPEC": "([{text}])",  # Stadium shape
            "CODE": "[{text}]",  # Rectangle
            "TEST": "{{​{text}}}",  # Hexagon
            "DOC": ">{text}]",  # Asymmetric
        }

    def generate_node_id(self, tag: CodeTag, index: int = 0) -> str:
        """Generate unique node ID.

        Args:
            tag: CodeTag object.
            index: Index for multiple tags of same type.

        Returns:
            Node ID string.

        Example:
            >>> gen.generate_node_id(CodeTag(tag_type="SPEC", tag_id="auth-001", ...))
            'SPEC_AUTH_001_0'
        """
        return f"{tag.tag_type}_{tag.tag_id.upper().replace('-', '_')}_{index}"

    def generate_node_label(self, tag: CodeTag) -> str:
        """Generate node label with location info.

        Args:
            tag: CodeTag object.

        Returns:
            Node label string.

        Example:
            >>> gen.generate_node_label(CodeTag(...))
            'SPEC: auth-001<br/>auth.py:15'
        """
        filename = tag.file_path.name if isinstance(tag.file_path, Path) else tag.file_path
        return f"{tag.tag_type}: {tag.tag_id}<br/>{filename}:{tag.line_number}"

    def generate_node_definition(
        self, tag: CodeTag, index: int = 0, status: str = "active"
    ) -> str:
        """Generate Mermaid node definition.

        Args:
            tag: CodeTag object.
            index: Index for multiple tags.
            status: Status for color coding.

        Returns:
            Mermaid node definition.

        Example:
            >>> gen.generate_node_definition(CodeTag(...), 0, "active")
            'SPEC_AUTH_001_0([SPEC: auth-001<br/>auth.py:15])'
        """
        node_id = self.generate_node_id(tag, index)
        label = self.generate_node_label(tag)
        shape_template = self.shape_mapping.get(tag.tag_type, "[{text}]")
        node_def = f"    {node_id}{shape_template.format(text=label)}"
        return node_def

    def generate_link(
        self, from_id: str, to_id: str, label: str = "", bidirectional: bool = False
    ) -> str:
        """Generate Mermaid link between nodes.

        Args:
            from_id: Source node ID.
            to_id: Target node ID.
            label: Optional link label.
            bidirectional: Whether link is bidirectional.

        Returns:
            Mermaid link definition.

        Example:
            >>> gen.generate_link("SPEC_0", "CODE_0", "implements")
            '    SPEC_0 -->|implements| CODE_0'
        """
        if bidirectional:
            arrow = "<-->"
        else:
            arrow = "-->"

        if label:
            return f"    {from_id} {arrow}|{label}| {to_id}"
        return f"    {from_id} {arrow} {to_id}"

    def generate_click_handler(self, node_id: str, file_path: str) -> str:
        """Generate Obsidian click handler.

        Args:
            node_id: Node ID.
            file_path: Path to file for linking.

        Returns:
            Mermaid click handler definition.

        Example:
            >>> gen.generate_click_handler("SPEC_0", "requirements/REQ-AUTH-001.md")
            '    click SPEC_0 "requirements/REQ-AUTH-001.md"'
        """
        return f'    click {node_id} "{file_path}"'

    def generate_style_classes(self) -> str:
        """Generate Mermaid style class definitions.

        Returns:
            Style class definitions.

        Example:
            >>> gen.generate_style_classes()
            '    classDef pending fill:#FFA500...'
        """
        styles = []
        for status, color in self.color_scheme.items():
            styles.append(f"    classDef {status} fill:{color},stroke:#333,stroke-width:2px")
        return "\n".join(styles)

    def generate_advanced_graph(
        self, tags_by_type: Dict[str, List[CodeTag]], tag_id: str
    ) -> str:
        """Generate advanced Mermaid graph with all features.

        Args:
            tags_by_type: Tags grouped by type.
            tag_id: TAG ID for graph title.

        Returns:
            Complete Mermaid graph.

        Example:
            >>> gen.generate_advanced_graph({"SPEC": [...], "CODE": [...]}, "auth-001")
            '```mermaid
            graph TD
            ...
            ```'
        """
        lines = ["```mermaid", "graph TD"]

        # Node definitions
        node_ids = {}
        for tag_type in ["SPEC", "CODE", "TEST", "DOC"]:
            if tag_type in tags_by_type:
                node_ids[tag_type] = []
                for i, tag in enumerate(tags_by_type[tag_type]):
                    node_def = self.generate_node_definition(tag, i)
                    lines.append(node_def)
                    node_ids[tag_type].append(self.generate_node_id(tag, i))

        # Links: SPEC -> CODE
        if "SPEC" in node_ids and "CODE" in node_ids:
            for spec_id in node_ids["SPEC"]:
                for code_id in node_ids["CODE"]:
                    lines.append(self.generate_link(spec_id, code_id, "implements"))

        # Links: CODE -> TEST
        if "CODE" in node_ids and "TEST" in node_ids:
            for code_id in node_ids["CODE"]:
                for test_id in node_ids["TEST"]:
                    lines.append(self.generate_link(code_id, test_id, "tests"))

        # Links: SPEC -> DOC
        if "SPEC" in node_ids and "DOC" in node_ids:
            for spec_id in node_ids["SPEC"]:
                for doc_id in node_ids["DOC"]:
                    lines.append(self.generate_link(spec_id, doc_id, "documents"))

        # Style classes
        lines.append("")
        lines.append(self.generate_style_classes())

        # Apply default style to all nodes
        for tag_type in node_ids:
            for node_id in node_ids[tag_type]:
                lines.append(f"    class {node_id} active")

        lines.append("```")
        return "\n".join(lines)

    def generate_minimal_graph(
        self, tags_by_type: Dict[str, List[CodeTag]], tag_id: str
    ) -> str:
        """Generate minimal Mermaid graph (backward compatibility).

        Args:
            tags_by_type: Tags grouped by type.
            tag_id: TAG ID for graph title.

        Returns:
            Simple Mermaid graph.

        Example:
            >>> gen.generate_minimal_graph({"SPEC": [...], "CODE": [...]}, "auth-001")
            '```mermaid
            graph TD
            ...
            ```'
        """
        lines = ["```mermaid", "graph TD"]

        # Simple node definitions
        if "SPEC" in tags_by_type:
            lines.append(f"    SPEC[SPEC: {tag_id.upper()}]")

        if "CODE" in tags_by_type:
            for i, tag in enumerate(tags_by_type["CODE"]):
                filename = tag.file_path.name if isinstance(tag.file_path, Path) else tag.file_path
                lines.append(f"    CODE{i}[CODE: {filename}:{tag.line_number}]")
                if "SPEC" in tags_by_type:
                    lines.append(f"    SPEC --> CODE{i}")

        if "TEST" in tags_by_type:
            for i, tag in enumerate(tags_by_type["TEST"]):
                filename = tag.file_path.name if isinstance(tag.file_path, Path) else tag.file_path
                lines.append(f"    TEST{i}[TEST: {filename}:{tag.line_number}]")
                if "CODE" in tags_by_type:
                    for j in range(len(tags_by_type["CODE"])):
                        lines.append(f"    CODE{j} --> TEST{i}")

        lines.append("```")
        return "\n".join(lines)


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Mermaid Graph Generator - Advanced Traceability Diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/mermaid_graph_generator.py --tag-id auth-001
  python scripts/mermaid_graph_generator.py --tag-id auth-001 --minimal
        """,
    )

    parser.add_argument("--tag-id", type=str, required=True, help="TAG ID for graph")
    parser.add_argument("--minimal", action="store_true", help="Generate minimal graph")

    args = parser.parse_args()

    print("[INFO] Mermaid Graph Generator")
    print("")

    try:
        generator = MermaidGraphGenerator()

        # Note: This is example usage, actual implementation
        # would integrate with TagExtractor to get real tags
        print(f"[INFO] Generate graph for TAG ID: {args.tag_id}")
        print("[INFO] Use TagSyncBridge.generate_traceability_map() for full functionality")

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to generate graph: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
