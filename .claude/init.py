#!/usr/bin/env python3
"""
Claude Code Auto-Initialization Script
This runs automatically when Claude Code session starts
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Import and run auto-init
from agent_auto_init import claude_init

# Set Claude marker
os.environ["CLAUDE_CODE"] = "1"

# Run initialization
print("\n🤖 Claude Code Session Starting...\n")
claude_init()

# Additional Claude-specific setup
print("\n💡 Tips:")
print("- Use 'cat HANDOFF_REPORT.md' to see full report")
print("- Run 'pytest' before creating handoff")
print("- Your agent name is set to 'Claude'")
print("\n" + "=" * 60)
