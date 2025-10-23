#!/usr/bin/env python3
"""
PromptCompressor + TaskExecutor Integration Module

Purpose:
- Automatic prompt extraction from YAML contracts
- Transparent prompt compression for token savings (30-50%)
- Zero manual intervention required

Constitutional Compliance:
- [P1] YAML Contract Priority
- [P3] Test-First Development
- [P6] Observability
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Any
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_compressor import PromptCompressor


@dataclass
class PromptLocation:
    """Location of a prompt in YAML contract"""

    command_id: str
    arg_index: int
    original_prompt: str
    context: str  # --prompt, --message, -m, etc.


def extract_prompts(contract: dict) -> List[PromptLocation]:
    """
    Extract AI prompts from YAML contract.

    Detection strategy:
    1. Look for --prompt, --message, -m flags
    2. Look for common AI-related arguments
    3. Heuristic: Long text (>50 chars) after AI flags

    Args:
        contract: YAML contract dictionary

    Returns:
        List of prompt locations with context

    Example:
        >>> contract = {
        ...     "commands": [{
        ...         "id": "cmd1",
        ...         "exec": {
        ...             "args": ["script.py", "--prompt", "Test prompt"]
        ...         }
        ...     }]
        ... }
        >>> prompts = extract_prompts(contract)
        >>> len(prompts)
        1
    """
    prompts = []

    # Prompt flag patterns to detect
    prompt_flags = [
        "--prompt",
        "--message",
        "-m",
        "--text",
        "--input",
        "--query",
        "--instruction",
    ]

    for cmd in contract.get("commands", []):
        cmd_id = cmd.get("id", "unknown")
        args = cmd.get("exec", {}).get("args", [])

        i = 0
        while i < len(args):
            arg = str(args[i])

            # Check if this is a prompt flag
            if arg in prompt_flags:
                # Next argument is the prompt
                if i + 1 < len(args):
                    next_arg = str(args[i + 1])

                    # Skip if next arg is also a flag
                    if not next_arg.startswith("-"):
                        prompts.append(
                            PromptLocation(
                                command_id=cmd_id,
                                arg_index=i + 1,
                                original_prompt=next_arg,
                                context=arg,
                            )
                        )

                    i += 2  # Skip both flag and value
                    continue

            i += 1

    return prompts


def apply_compression(contract: dict, config: dict) -> Tuple[dict, List[Dict[str, Any]]]:
    """
    Apply prompt compression to YAML contract.

    Args:
        contract: Original YAML contract
        config: Compression configuration from prompt_optimization section

    Returns:
        Tuple of (modified_contract, compression_stats)

    Configuration options:
        - enabled: bool (default: False)
        - compression_level: light|medium|aggressive (default: medium)
        - auto_learn: bool (default: True)
        - report_path: str (default: RUNS/{task_id}/compression_report.json)

    Example:
        >>> contract = {"commands": [...], "prompt_optimization": {"enabled": True}}
        >>> modified, stats = apply_compression(contract, contract["prompt_optimization"])
        >>> len(stats) > 0
        True
    """
    if not config.get("enabled", False):
        return contract, []

    # Initialize compressor
    compression_level = config.get("compression_level", "medium")
    compressor = PromptCompressor(compression_level=compression_level)

    # Extract prompts
    prompts = extract_prompts(contract)

    if not prompts:
        return contract, []

    compression_stats = []

    # Compress each prompt
    for loc in prompts:
        try:
            result = compressor.compress(loc.original_prompt)

            # Find the command in contract
            for cmd in contract.get("commands", []):
                if cmd.get("id") == loc.command_id:
                    # Replace prompt with compressed version
                    args = cmd.get("exec", {}).get("args", [])
                    if loc.arg_index < len(args):
                        args[loc.arg_index] = result.compressed

                    break

            # Track statistics
            compression_stats.append(
                {
                    "command_id": loc.command_id,
                    "context": loc.context,
                    "original_tokens": result.original_tokens,
                    "compressed_tokens": result.compressed_tokens,
                    "savings_pct": result.savings_pct,
                    "rules_applied": len(result.compression_rules),
                }
            )

        except Exception as e:
            # Log error but continue with other prompts
            compression_stats.append(
                {
                    "command_id": loc.command_id,
                    "context": loc.context,
                    "error": str(e),
                }
            )

    return contract, compression_stats


def save_compression_report(stats: List[Dict[str, Any]], report_path: str, task_id: str) -> None:
    """
    Save compression statistics to JSON report.

    Args:
        stats: List of compression statistics
        report_path: Path template with {task_id} placeholder
        task_id: Current task ID for path substitution
    """
    import json
    from datetime import datetime, timezone

    # Substitute task_id in path
    actual_path = Path(report_path.replace("{task_id}", task_id))

    # Ensure directory exists
    actual_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate summary statistics
    total_original = sum(s.get("original_tokens", 0) for s in stats)
    total_compressed = sum(s.get("compressed_tokens", 0) for s in stats)
    avg_savings = sum(s.get("savings_pct", 0) for s in stats) / len(stats) if stats else 0

    report = {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "prompts_compressed": len(stats),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "total_tokens_saved": total_original - total_compressed,
            "average_savings_pct": round(avg_savings, 2),
        },
        "details": stats,
    }

    # Write report
    with open(actual_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
