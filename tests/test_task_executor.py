
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add scripts directory to path to allow importing task_executor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from task_executor import execute_lite_mode

class TestTaskExecutorLiteMode(unittest.TestCase):

    @patch.dict(os.environ, {"OBSIDIAN_ENABLED": "true"})
    @patch('task_executor.sync_to_obsidian')
    @patch('task_executor.run')
    @patch('task_executor.input')
    def test_execute_lite_mode_success(self, mock_input, mock_run, mock_sync_to_obsidian):
        """Test the successful execution of lite mode."""
        # Arrange: Mock user input and git status output
        mock_input.return_value = "feat: Add amazing new feature"
        
        mock_git_status_result = MagicMock()
        mock_git_status_result.stdout = " M scripts/task_executor.py\n A tests/test_task_executor.py"
        mock_run.return_value = mock_git_status_result

        # Act: Run the function
        execute_lite_mode()

        # Assert: Check that the correct functions were called
        mock_input.assert_called_once()
        mock_run.assert_called_once_with(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        # Check that sync_to_obsidian was called with the correct arguments
        self.assertTrue(mock_sync_to_obsidian.called)
        call_args, call_kwargs = mock_sync_to_obsidian.call_args
        contract_arg = call_args[0]
        self.assertEqual(contract_arg['title'], "feat: Add amazing new feature")
        self.assertIn("lite-mode", contract_arg['tags'])

    @patch('task_executor.input', return_value="")
    def test_execute_lite_mode_empty_input(self, mock_input):
        """Test that lite mode aborts with empty user input."""
        # We need to patch 'builtins.print' to check the output
        with patch('builtins.print') as mock_print:
            execute_lite_mode()
            mock_print.assert_any_call("Task summary cannot be empty. Aborting.")

    @patch('task_executor.input', return_value="A task")
    @patch('task_executor.run')
    def test_execute_lite_mode_no_changed_files(self, mock_run, mock_input):
        """Test that lite mode aborts when no files are changed."""
        mock_git_status_result = MagicMock()
        mock_git_status_result.stdout = ""
        mock_run.return_value = mock_git_status_result
        
        with patch('builtins.print') as mock_print:
            execute_lite_mode()
            mock_print.assert_any_call("No changed files detected. Nothing to record. Aborting.")

if __name__ == '__main__':
    unittest.main()
