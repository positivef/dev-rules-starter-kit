"""Tests for Mermaid Graph Generator.

Test Coverage:
- Node ID generation
- Node label generation
- Node definition with shapes
- Link generation (unidirectional/bidirectional)
- Style class generation
- Advanced graph generation
- Minimal graph generation (backward compatibility)

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mermaid_graph_generator import MermaidGraphGenerator
from tag_extractor_lite import CodeTag


@pytest.fixture
def sample_tags():
    """Create sample CodeTag objects."""
    return {
        "SPEC": [
            CodeTag(
                tag_type="SPEC",
                tag_id="auth-001",
                file_path=Path("src/auth.py"),
                line_number=15,
                context="",
            )
        ],
        "CODE": [
            CodeTag(
                tag_type="CODE",
                tag_id="auth-001",
                file_path=Path("src/auth.py"),
                line_number=20,
                context="",
            ),
            CodeTag(
                tag_type="CODE",
                tag_id="auth-001",
                file_path=Path("src/middleware.py"),
                line_number=30,
                context="",
            ),
        ],
        "TEST": [
            CodeTag(
                tag_type="TEST",
                tag_id="auth-001",
                file_path=Path("tests/test_auth.py"),
                line_number=10,
                context="",
            )
        ],
    }


class TestNodeGeneration:
    """Test Mermaid node generation."""

    def test_generate_node_id(self):
        """Test generating unique node ID."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        node_id = generator.generate_node_id(tag, 0)
        assert node_id == "SPEC_AUTH_001_0"

    def test_generate_node_label(self):
        """Test generating node label with location."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        label = generator.generate_node_label(tag)
        assert "SPEC: auth-001" in label
        assert "auth.py:15" in label
        assert "<br/>" in label

    def test_generate_node_definition_spec(self):
        """Test generating SPEC node definition (stadium shape)."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        node_def = generator.generate_node_definition(tag, 0)
        assert "SPEC_AUTH_001_0" in node_def
        assert "([" in node_def  # Stadium shape
        assert "])" in node_def

    def test_generate_node_definition_code(self):
        """Test generating CODE node definition (rectangle shape)."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="CODE",
            tag_id="auth-001",
            file_path=Path("src/auth.py"),
            line_number=20,
            context="",
        )

        node_def = generator.generate_node_definition(tag, 0)
        assert "CODE_AUTH_001_0" in node_def
        assert "[" in node_def  # Rectangle shape
        assert "]" in node_def

    def test_generate_node_definition_test(self):
        """Test generating TEST node definition (hexagon shape)."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="TEST",
            tag_id="auth-001",
            file_path=Path("tests/test_auth.py"),
            line_number=10,
            context="",
        )

        node_def = generator.generate_node_definition(tag, 0)
        assert "TEST_AUTH_001_0" in node_def
        assert "{{" in node_def or "{" in node_def  # Hexagon shape


class TestLinkGeneration:
    """Test Mermaid link generation."""

    def test_generate_unidirectional_link(self):
        """Test generating unidirectional link."""
        generator = MermaidGraphGenerator()
        link = generator.generate_link("SPEC_0", "CODE_0")

        assert "SPEC_0" in link
        assert "CODE_0" in link
        assert "-->" in link

    def test_generate_link_with_label(self):
        """Test generating link with label."""
        generator = MermaidGraphGenerator()
        link = generator.generate_link("SPEC_0", "CODE_0", "implements")

        assert "implements" in link
        assert "|implements|" in link

    def test_generate_bidirectional_link(self):
        """Test generating bidirectional link."""
        generator = MermaidGraphGenerator()
        link = generator.generate_link("SPEC_0", "CODE_0", "", bidirectional=True)

        assert "<-->" in link


class TestStyleGeneration:
    """Test Mermaid style generation."""

    def test_generate_style_classes(self):
        """Test generating style class definitions."""
        generator = MermaidGraphGenerator()
        styles = generator.generate_style_classes()

        assert "classDef" in styles
        assert "pending" in styles
        assert "active" in styles
        assert "completed" in styles
        assert "#FFA500" in styles or "#4CAF50" in styles

    def test_click_handler_generation(self):
        """Test generating Obsidian click handler."""
        generator = MermaidGraphGenerator()
        handler = generator.generate_click_handler("SPEC_0", "requirements/REQ-AUTH-001.md")

        assert "click SPEC_0" in handler
        assert "requirements/REQ-AUTH-001.md" in handler


class TestAdvancedGraph:
    """Test advanced Mermaid graph generation."""

    def test_generate_advanced_graph_with_all_types(self, sample_tags):
        """Test generating advanced graph with all TAG types."""
        generator = MermaidGraphGenerator()
        graph = generator.generate_advanced_graph(sample_tags, "auth-001")

        # Check structure
        assert "```mermaid" in graph
        assert "graph TD" in graph
        assert "```" in graph.split("```mermaid")[1]

        # Check nodes
        assert "SPEC_AUTH_001_0" in graph
        assert "CODE_AUTH_001_0" in graph
        assert "CODE_AUTH_001_1" in graph
        assert "TEST_AUTH_001_0" in graph

        # Check links
        assert "implements" in graph
        assert "tests" in graph

        # Check styles
        assert "classDef" in graph
        assert "active" in graph

    def test_generate_advanced_graph_spec_code_only(self):
        """Test generating graph with SPEC and CODE only."""
        generator = MermaidGraphGenerator()
        tags = {
            "SPEC": [
                CodeTag(
                    tag_type="SPEC",
                    tag_id="auth-001",
                    file_path=Path("src/auth.py"),
                    line_number=15,
                    context="",
                )
            ],
            "CODE": [
                CodeTag(
                    tag_type="CODE",
                    tag_id="auth-001",
                    file_path=Path("src/auth.py"),
                    line_number=20,
                    context="",
                )
            ],
        }

        graph = generator.generate_advanced_graph(tags, "auth-001")

        assert "SPEC_AUTH_001_0" in graph
        assert "CODE_AUTH_001_0" in graph
        assert "implements" in graph


class TestMinimalGraph:
    """Test minimal graph generation (backward compatibility)."""

    def test_generate_minimal_graph(self, sample_tags):
        """Test generating minimal graph."""
        generator = MermaidGraphGenerator()
        graph = generator.generate_minimal_graph(sample_tags, "auth-001")

        # Check structure
        assert "```mermaid" in graph
        assert "graph TD" in graph
        assert "```" in graph.split("```mermaid")[1]

        # Check nodes (minimal format)
        assert "SPEC[" in graph
        assert "CODE0[" in graph
        assert "CODE1[" in graph
        assert "TEST0[" in graph

        # Check links (minimal format)
        assert "SPEC --> CODE0" in graph
        assert "SPEC --> CODE1" in graph
        assert "CODE0 --> TEST0" in graph

    def test_minimal_graph_backward_compatible(self, sample_tags):
        """Test minimal graph matches old format."""
        generator = MermaidGraphGenerator()
        graph = generator.generate_minimal_graph(sample_tags, "auth-001")

        # Should NOT have advanced features
        assert "classDef" not in graph
        assert "click" not in graph
        assert "|implements|" not in graph


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_tags(self):
        """Test generating graph with no tags."""
        generator = MermaidGraphGenerator()
        graph = generator.generate_advanced_graph({}, "auth-001")

        assert "```mermaid" in graph
        assert "graph TD" in graph
        # Should have minimal content

    def test_single_tag_type(self):
        """Test generating graph with only one TAG type."""
        generator = MermaidGraphGenerator()
        tags = {
            "SPEC": [
                CodeTag(
                    tag_type="SPEC",
                    tag_id="auth-001",
                    file_path=Path("src/auth.py"),
                    line_number=15,
                    context="",
                )
            ]
        }

        graph = generator.generate_advanced_graph(tags, "auth-001")
        assert "SPEC_AUTH_001_0" in graph
        # Should not crash with missing links

    def test_special_characters_in_tag_id(self):
        """Test handling special characters in TAG ID."""
        generator = MermaidGraphGenerator()
        tag = CodeTag(
            tag_type="SPEC",
            tag_id="auth-001-special",
            file_path=Path("src/auth.py"),
            line_number=15,
            context="",
        )

        node_id = generator.generate_node_id(tag, 0)
        # Should sanitize special characters
        assert "SPEC_AUTH_001_SPECIAL" in node_id
