#!/usr/bin/env python3
"""
Test file for Git Hook validation
"""


def test_function():
    """Test function with emoji violation"""
    message = "Test message"
    # This should pass
    print(f"[OK] {message}")
    return message


if __name__ == "__main__":
    test_function()
