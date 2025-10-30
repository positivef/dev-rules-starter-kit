#!/usr/bin/env python3
"""Tests for install_obsidian_auto_sync.py"""

import pytest
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from install_obsidian_auto_sync import (
    check_installation,
    install_hook,
    uninstall_hook,
)


class TestInstallation:
    """Test installation checks"""

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_check_installation_installed(self, mock_read, mock_exists, mock_get_hooks):
        """Test detecting installed hook"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = True
        mock_read.return_value = "python scripts/auto_sync_obsidian.py"

        is_installed, message = check_installation()

        assert is_installed is True
        assert "installed" in message.lower()

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    def test_check_installation_not_installed(self, mock_exists, mock_get_hooks):
        """Test detecting missing hook"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = False

        is_installed, message = check_installation()

        assert is_installed is False


class TestHookInstallation:
    """Test hook installation"""

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.chmod")
    def test_install_hook_new(self, mock_chmod, mock_write, mock_exists, mock_get_hooks):
        """Test installing new hook"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = False

        result = install_hook()

        assert result is True

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_install_hook_already_installed(self, mock_read, mock_exists, mock_get_hooks):
        """Test detecting already installed hook"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = True
        mock_read.return_value = "python scripts/auto_sync_obsidian.py --quiet"

        result = install_hook()

        # Should detect it's already there
        assert result is True


class TestUninstallation:
    """Test hook uninstallation"""

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.write_text")
    def test_uninstall_hook_success(self, mock_write, mock_read, mock_exists, mock_get_hooks):
        """Test successful uninstallation"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = True
        mock_read.return_value = "#!/bin/bash\npython scripts/auto_sync_obsidian.py\nother content"

        result = uninstall_hook()

        assert result is True

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    def test_uninstall_hook_not_installed(self, mock_exists, mock_get_hooks):
        """Test uninstalling when not installed"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = False

        result = uninstall_hook()

        assert result is True  # Returns True when nothing to uninstall


class TestIntegration:
    """Integration tests"""

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.chmod")
    def test_full_installation_flow(self, mock_chmod, mock_write, mock_read, mock_exists, mock_get_hooks):
        """Test complete installation workflow"""
        # Setup mocks for successful installation
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.side_effect = [
            False,  # Hook doesn't exist initially
            True,  # Hook exists after check
        ]
        mock_read.return_value = "python scripts/auto_sync_obsidian.py --quiet"

        # Install hook
        result = install_hook()
        assert result is True

        # Check installation
        is_installed, message = check_installation()
        assert is_installed is True


class TestErrorHandling:
    """Test error handling"""

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.exists")
    def test_install_hook_write_error(self, mock_exists, mock_write, mock_get_hooks):
        """Test handling write errors during installation"""
        mock_get_hooks.return_value = Path(".git/hooks")
        mock_exists.return_value = False
        mock_write.side_effect = PermissionError("Access denied")

        result = install_hook()

        assert result is False

    @patch("install_obsidian_auto_sync.get_git_hooks_dir")
    def test_check_installation_error(self, mock_get_hooks):
        """Test handling errors during installation check"""
        mock_get_hooks.side_effect = RuntimeError("Not a git repository")

        is_installed, message = check_installation()

        assert is_installed is False
        assert "failed" in message.lower() or "not" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
