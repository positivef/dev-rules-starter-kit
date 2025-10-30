"""Tests for Dataview Query Generator.

Test Coverage:
- Dataview query generation per TAG type
- Traceability chain queries
- Status filtering queries
- Dashboard statistics queries

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import sys
from pathlib import Path


# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dataview_generator import DataviewGenerator


class TestQueryGeneration:
    """Test Dataview query generation."""

    def test_generate_related_tags_query(self):
        """Test generating query for related TAGs with same ID."""
        generator = DataviewGenerator()
        query = generator.generate_related_tags_query("auth-001")

        # Check basic structure
        assert "```dataview" in query
        assert "TABLE" in query
        assert "auth-001" in query.lower()
        assert "tag_type" in query

    def test_generate_spec_dependencies_query(self):
        """Test generating query for SPEC dependencies (CODE/TEST)."""
        generator = DataviewGenerator()
        query = generator.generate_dependencies_query("auth-001", "SPEC")

        # Should include CODE and TEST
        assert "```dataview" in query
        assert "impl/" in query or "test/" in query

    def test_generate_code_dependencies_query(self):
        """Test generating query for CODE dependencies (SPEC/TEST)."""
        generator = DataviewGenerator()
        query = generator.generate_dependencies_query("auth-001", "CODE")

        # Should include SPEC and TEST
        assert "```dataview" in query
        assert "req/" in query or "test/" in query

    def test_generate_test_dependencies_query(self):
        """Test generating query for TEST dependencies (SPEC/CODE)."""
        generator = DataviewGenerator()
        query = generator.generate_dependencies_query("auth-001", "TEST")

        # Should include SPEC and CODE
        assert "```dataview" in query
        assert "req/" in query or "impl/" in query


class TestStatusQueries:
    """Test status filtering queries."""

    def test_generate_active_tags_query(self):
        """Test generating query for active TAGs."""
        generator = DataviewGenerator()
        query = generator.generate_status_query(status="active")

        assert "```dataview" in query
        assert "status/active" in query

    def test_generate_pending_tags_query(self):
        """Test generating query for pending TAGs."""
        generator = DataviewGenerator()
        query = generator.generate_status_query(status="pending")

        assert "```dataview" in query
        assert "status/pending" in query

    def test_generate_completed_tags_query(self):
        """Test generating query for completed TAGs."""
        generator = DataviewGenerator()
        query = generator.generate_status_query(status="completed")

        assert "```dataview" in query
        assert "status/completed" in query


class TestDashboardQueries:
    """Test dashboard statistics queries."""

    def test_generate_tag_type_summary(self):
        """Test generating summary by TAG type."""
        generator = DataviewGenerator()
        query = generator.generate_type_summary_query()

        assert "```dataview" in query
        assert "GROUP BY" in query
        assert "type/" in query

    def test_generate_tag_id_summary(self):
        """Test generating summary by TAG ID."""
        generator = DataviewGenerator()
        query = generator.generate_id_summary_query()

        assert "```dataview" in query
        assert "GROUP BY" in query
        assert "tag_id" in query

    def test_generate_status_summary(self):
        """Test generating summary by status."""
        generator = DataviewGenerator()
        query = generator.generate_status_summary_query()

        assert "```dataview" in query
        assert "GROUP BY" in query
        assert "status/" in query


class TestTraceabilityQueries:
    """Test traceability chain queries."""

    def test_generate_full_chain_query(self):
        """Test generating query for full SPEC->CODE->TEST chain."""
        generator = DataviewGenerator()
        query = generator.generate_traceability_chain_query("auth-001")

        # Should include all types
        assert "```dataview" in query
        assert "auth-001" in query.lower()

    def test_generate_missing_implementations_query(self):
        """Test generating query for SPECs without CODE."""
        generator = DataviewGenerator()
        query = generator.generate_missing_implementations_query()

        assert "```dataview" in query
        assert "#req" in query

    def test_generate_missing_tests_query(self):
        """Test generating query for CODE without TEST."""
        generator = DataviewGenerator()
        query = generator.generate_missing_tests_query()

        assert "```dataview" in query
        assert "#impl" in query


class TestQueryFormatting:
    """Test query formatting and structure."""

    def test_query_has_proper_syntax(self):
        """Test all queries have proper Dataview syntax."""
        generator = DataviewGenerator()

        queries = [
            generator.generate_related_tags_query("auth-001"),
            generator.generate_status_query("active"),
            generator.generate_type_summary_query(),
        ]

        for query in queries:
            # Check basic Dataview structure
            assert query.startswith("```dataview")
            assert query.endswith("```")
            assert "FROM" in query or "LIST" in query or "TABLE" in query

    def test_query_escaping(self):
        """Test special characters are properly escaped."""
        generator = DataviewGenerator()
        query = generator.generate_related_tags_query("auth-001-special")

        # Should handle special characters
        assert "auth-001-special" in query.lower()


class TestIntegration:
    """Test integration with TagSyncBridge."""

    def test_generate_all_queries_for_tag(self):
        """Test generating all queries for a specific TAG."""
        generator = DataviewGenerator()
        queries = generator.generate_all_queries("auth-001", "SPEC")

        # Should have multiple query sections
        assert "related_tags" in queries
        assert "dependencies" in queries
        assert "traceability" in queries

    def test_format_for_obsidian_note(self):
        """Test formatting queries for Obsidian note."""
        generator = DataviewGenerator()
        content = generator.format_for_note("auth-001", "SPEC")

        # Should be ready for Obsidian
        assert "## Traceability" in content
        assert "```dataview" in content
        assert "auth-001" in content.lower()
