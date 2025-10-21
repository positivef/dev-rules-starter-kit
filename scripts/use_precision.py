#!/usr/bin/env python3
"""
Helper to use MCP Precision System from dev-rules-starter-kit

The precision system is now a separate project at:
C:/Users/user/Documents/GitHub/mcp-precision-system
"""

import sys
from pathlib import Path

# Add precision system to path
PRECISION_SYSTEM_PATH = Path(__file__).parent.parent.parent / "mcp-precision-system"
sys.path.insert(0, str(PRECISION_SYSTEM_PATH / "integration"))
sys.path.insert(0, str(PRECISION_SYSTEM_PATH))

# Now you can import
from integration.precision_wrapper import PrecisionEnhancedExecutor, PrecisionConfig, VerificationLevel  # noqa: E402

# Example usage
if __name__ == "__main__":
    config = PrecisionConfig(verification_level=VerificationLevel.STANDARD, min_confidence_threshold=0.8)

    executor = PrecisionEnhancedExecutor(config=config)
    print("[OK] MCP Precision System loaded successfully!")
    print(f"  Location: {PRECISION_SYSTEM_PATH}")
    print(f"  Verification Level: {config.verification_level.value}")
