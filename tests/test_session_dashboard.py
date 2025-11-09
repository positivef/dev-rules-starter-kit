"""Tests for SessionDashboard - Streamlit monitoring dashboard.

Constitutional Compliance:
- P8: Test-First Development (TDD)
- P6: Quality Gates (coverage for critical functions)

Note: This is a Streamlit UI app, so testing focuses on:
1. Core logic (load_session_data)
2. Smoke tests (import and basic functionality)
3. Mock-based unit tests for data loading
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestSessionDashboardImport:
    """Test dashboard can be imported without errors."""

    def test_import_dashboard(self):
        """Test dashboard module imports successfully."""
        # This is a smoke test - if import fails, something is very wrong
        try:
            import session_dashboard

            assert session_dashboard is not None
        except ImportError as e:
            pytest.fail(f"Failed to import session_dashboard: {e}")

    def test_dashboard_has_main_function(self):
        """Test dashboard has main entry point."""
        import session_dashboard

        assert hasattr(session_dashboard, "main")
        assert callable(session_dashboard.main)


class TestLoadSessionData:
    """Test load_session_data function."""

    @patch("session_dashboard.SESSION_ENABLED", True)
    @patch("session_dashboard.SessionManager")
    @patch("session_dashboard.StateScope")
    def test_load_session_data_success(self, mock_scope, mock_session_manager):
        """Test successful session data loading."""
        from session_dashboard import load_session_data

        # Mock StateScope enum
        mock_scope.SESSION = "SESSION"
        mock_scope.USER = "USER"
        mock_scope.TEMP = "TEMP"

        # Mock SessionManager instance
        mock_session = Mock()
        mock_session.get_session_info.return_value = {
            "session_id": "test_session_123",
            "started_at": "2025-11-09T12:00:00",
            "last_checkpoint": "2025-11-09T12:30:00",
            "data_sizes": {"session": 10, "temp": 5},
        }

        # Mock get method with proper return values
        def mock_get(key, scope, default=None):
            return_values = {
                "current_task": {"task_id": "TASK-001", "status": "running"},
                "execution_stats": {"total_executions": 10, "successful": 8, "failed": 2},
                "completed_tasks": ["TASK-001", "TASK-002"],
                "failed_tasks": {"TASK-003": "error message"},
                "command_log": [{"command": "test", "timestamp": "2025-11-09"}],
            }
            return return_values.get(key, default)

        mock_session.get.side_effect = mock_get
        mock_session_manager.get_instance.return_value = mock_session

        # Load data
        data = load_session_data()

        # Verify data structure
        assert data is not None
        assert "session_info" in data
        assert "current_task" in data
        assert "stats" in data
        assert "completed_tasks" in data
        assert "failed_tasks" in data
        assert "command_log" in data

        # Verify session info
        assert data["session_info"]["session_id"] == "test_session_123"
        assert data["current_task"]["status"] == "running"
        assert data["stats"]["total_executions"] == 10

    @patch("session_dashboard.SESSION_ENABLED", False)
    def test_load_session_data_session_disabled(self):
        """Test load_session_data returns None when SESSION_ENABLED is False."""
        from session_dashboard import load_session_data

        data = load_session_data()
        assert data is None

    @patch("session_dashboard.SESSION_ENABLED", True)
    @patch("session_dashboard.SessionManager")
    def test_load_session_data_exception_handling(self, mock_session_manager):
        """Test load_session_data handles exceptions gracefully."""
        from session_dashboard import load_session_data

        # Mock exception
        mock_session_manager.get_instance.side_effect = Exception("Test error")

        # Should return None on error (with st.error called internally)
        with patch("session_dashboard.st"):  # Mock streamlit
            data = load_session_data()
            assert data is None


class TestDashboardFunctions:
    """Test dashboard display functions (smoke tests)."""

    def test_display_current_status_exists(self):
        """Test display_current_status function exists."""
        import session_dashboard

        assert hasattr(session_dashboard, "display_current_status")
        assert callable(session_dashboard.display_current_status)

    def test_display_statistics_exists(self):
        """Test display_statistics function exists."""
        import session_dashboard

        assert hasattr(session_dashboard, "display_statistics")
        assert callable(session_dashboard.display_statistics)

    def test_display_task_history_exists(self):
        """Test display_task_history function exists."""
        import session_dashboard

        assert hasattr(session_dashboard, "display_task_history")
        assert callable(session_dashboard.display_task_history)

    def test_display_productivity_analysis_exists(self):
        """Test display_productivity_analysis function exists."""
        import session_dashboard

        assert hasattr(session_dashboard, "display_productivity_analysis")
        assert callable(session_dashboard.display_productivity_analysis)

    @patch("session_dashboard.st")
    def test_display_current_status_basic(self, mock_st):
        """Test display_current_status with basic data (smoke test)."""
        from session_dashboard import display_current_status

        # Mock st.columns to return 4 MagicMock objects (support context managers)
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        test_data = {
            "session_info": {
                "session_id": "test123",
                "started_at": "2025-11-09T12:00:00",
                "last_checkpoint": "2025-11-09T12:30:00",
                "data_sizes": {"session": 10},
            },
            "current_task": None,
        }

        # Should not raise exception
        try:
            display_current_status(test_data)
        except Exception as e:
            pytest.fail(f"display_current_status raised exception: {e}")

    @patch("session_dashboard.st")
    def test_display_statistics_basic(self, mock_st):
        """Test display_statistics with basic data (smoke test)."""
        from session_dashboard import display_statistics

        # Mock st.columns to return variable number of MagicMock objects based on input
        def mock_columns(num_cols):
            return [MagicMock() for _ in range(num_cols)]

        mock_st.columns.side_effect = mock_columns

        test_data = {
            "stats": {
                "total_executions": 10,
                "successful": 8,
                "failed": 2,
                "avg_time": 1.5,
                "total_time": 15.0,
            }
        }

        # Should not raise exception
        try:
            display_statistics(test_data)
        except Exception as e:
            pytest.fail(f"display_statistics raised exception: {e}")


class TestDashboardIntegration:
    """Integration tests for dashboard."""

    def test_dashboard_structure(self):
        """Test dashboard has expected structure."""
        import session_dashboard

        # Check required functions exist
        required_functions = [
            "load_session_data",
            "display_current_status",
            "display_statistics",
            "display_task_history",
            "display_productivity_analysis",
            "main",
        ]

        for func_name in required_functions:
            assert hasattr(session_dashboard, func_name), f"Missing function: {func_name}"
            assert callable(getattr(session_dashboard, func_name)), f"{func_name} is not callable"

    def test_streamlit_imports(self):
        """Test required Streamlit dependencies are importable."""
        try:
            import plotly.graph_objects  # noqa: F401
            import streamlit  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Streamlit dependencies not available: {e}")
