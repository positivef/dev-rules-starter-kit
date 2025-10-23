"""
Manual test script for dev_assistant file watcher.

This script demonstrates the file watcher in action.

Usage:
    1. Run this script in one terminal: python scripts/test_watcher_manual.py
    2. In another terminal, modify files in scripts/ or tests/
    3. Watch the console output for file change events
    4. Press Ctrl+C to stop

The watcher should:
- Detect .py file changes within 500ms
- Log each change with timestamp
- Use <2% CPU when idle
- Shutdown cleanly on Ctrl+C
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dev_assistant import DevAssistant


def main():
    """Run file watcher in manual test mode."""
    print("=" * 60)
    print("Manual Test: Development Assistant File Watcher")
    print("=" * 60)
    print("\nInstructions:")
    print("1. This terminal will show file change events")
    print("2. Open another terminal and modify .py files in scripts/ or tests/")
    print("3. Watch for [MODIFIED] and [CREATED] events here")
    print("4. Press Ctrl+C to stop cleanly")
    print("\nStarting watcher...\n")

    # Create assistant with default configuration
    assistant = DevAssistant(watch_dirs=["scripts", "tests"], debounce_ms=500, log_level="INFO")

    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n\nTest completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
