"""
Prompt Tracker - AI Interaction Logging and Optimization System
Phase 1 Feature #2

Purpose:
- Track all AI interactions (prompts + responses + metadata)
- Measure token usage and costs
- Identify effective prompt patterns
- Detect inefficient prompts
- Learn from successful interactions

ROI: 250% annually (30h saved / 12h invested)
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PromptTracker:
    """
    Lightweight prompt tracking system with JSON storage.

    Features:
    - Automatic prompt/response logging
    - Token usage tracking
    - Cost calculation
    - Pattern analysis (effective vs ineffective prompts)
    - Obsidian MOC generation
    """

    def __init__(self, db_path: str = ".prompt_db.json"):
        """
        Initialize prompt tracker.

        Args:
            db_path: Path to JSON database file
        """
        self.db_path = Path(db_path)
        self.prompts: Dict[str, Dict] = self._load_db()
        self.token_costs = {
            "claude-sonnet-4": {"input": 0.003, "output": 0.015},  # per 1K tokens
            "claude-opus-4": {"input": 0.015, "output": 0.075},
            "gpt-4": {"input": 0.03, "output": 0.06},
        }

    def _load_db(self) -> Dict[str, Dict]:
        """Load prompt database from JSON file."""
        if self.db_path.exists():
            try:
                return json.loads(self.db_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                print("[WARN] Corrupted prompt DB, creating new one")
                return {}
        return {}

    def _save_db(self):
        """Save prompt database to JSON file (atomic write)."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.db_path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.prompts, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        tmp.replace(self.db_path)

    def track_interaction(
        self,
        prompt: str,
        response: str,
        model: str = "claude-sonnet-4",
        tokens_input: int = 0,
        tokens_output: int = 0,
        success: bool = True,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Track an AI interaction.

        Args:
            prompt: User prompt text
            response: AI response text
            model: Model used (e.g., "claude-sonnet-4")
            tokens_input: Input tokens consumed
            tokens_output: Output tokens consumed
            success: Whether interaction achieved desired outcome
            tags: Optional tags for categorization
            metadata: Optional additional metadata

        Returns:
            interaction_id: Unique identifier for this interaction

        Example:
            >>> tracker = PromptTracker()
            >>> interaction_id = tracker.track_interaction(
            ...     prompt="Implement error learning database",
            ...     response="[implementation details]",
            ...     model="claude-sonnet-4",
            ...     tokens_input=1500,
            ...     tokens_output=3000,
            ...     success=True,
            ...     tags=["implementation", "database"]
            ... )
        """
        # Generate unique ID
        timestamp = datetime.now().isoformat()
        interaction_signature = f"{timestamp}:{prompt[:50]}"
        interaction_id = hashlib.sha256(interaction_signature.encode()).hexdigest()[:8]

        # Calculate cost
        cost = self._calculate_cost(model, tokens_input, tokens_output)

        # Store interaction
        self.prompts[interaction_id] = {
            "timestamp": timestamp,
            "prompt": prompt,
            "response": response,
            "model": model,
            "tokens": {
                "input": tokens_input,
                "output": tokens_output,
                "total": tokens_input + tokens_output,
            },
            "cost_usd": cost,
            "success": success,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        self._save_db()
        return interaction_id

    def _calculate_cost(
        self, model: str, tokens_input: int, tokens_output: int
    ) -> float:
        """Calculate cost in USD for token usage."""
        if model not in self.token_costs:
            return 0.0

        costs = self.token_costs[model]
        cost_input = (tokens_input / 1000) * costs["input"]
        cost_output = (tokens_output / 1000) * costs["output"]
        return round(cost_input + cost_output, 6)

    def get_stats(
        self, days: Optional[int] = None, tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Get prompt tracking statistics.

        Args:
            days: Filter to last N days (None = all time)
            tags: Filter by tags (None = all tags)

        Returns:
            Dictionary with statistics
        """
        filtered_prompts = self._filter_prompts(days, tags)

        if not filtered_prompts:
            return {
                "total_interactions": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "success_rate": 0.0,
                "avg_tokens_per_interaction": 0,
            }

        total_tokens = sum(p["tokens"]["total"] for p in filtered_prompts.values())
        total_cost = sum(p["cost_usd"] for p in filtered_prompts.values())
        successful = sum(1 for p in filtered_prompts.values() if p["success"])
        success_rate = (successful / len(filtered_prompts)) * 100

        return {
            "total_interactions": len(filtered_prompts),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2),
            "success_rate": round(success_rate, 1),
            "avg_tokens_per_interaction": round(
                total_tokens / len(filtered_prompts), 0
            ),
            "most_used_model": self._get_most_used_model(filtered_prompts),
        }

    def _filter_prompts(
        self, days: Optional[int], tags: Optional[List[str]]
    ) -> Dict[str, Dict]:
        """Filter prompts by time and tags."""
        filtered = {}

        for interaction_id, data in self.prompts.items():
            # Time filter
            if days:
                interaction_time = datetime.fromisoformat(data["timestamp"])
                if (datetime.now() - interaction_time).days > days:
                    continue

            # Tag filter
            if tags:
                if not any(tag in data["tags"] for tag in tags):
                    continue

            filtered[interaction_id] = data

        return filtered

    def _get_most_used_model(self, prompts: Dict) -> str:
        """Get most frequently used model."""
        model_counts = {}
        for data in prompts.values():
            model = data["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        if not model_counts:
            return "N/A"

        return max(model_counts.items(), key=lambda x: x[1])[0]

    def find_effective_patterns(self, min_success_rate: float = 80.0) -> List[Dict]:
        """
        Find prompt patterns with high success rates.

        Args:
            min_success_rate: Minimum success rate percentage (0-100)

        Returns:
            List of effective prompt patterns
        """
        # Group by tags
        tag_stats = {}

        for data in self.prompts.values():
            for tag in data["tags"]:
                if tag not in tag_stats:
                    tag_stats[tag] = {"total": 0, "successful": 0, "prompts": []}

                tag_stats[tag]["total"] += 1
                if data["success"]:
                    tag_stats[tag]["successful"] += 1
                tag_stats[tag]["prompts"].append(data["prompt"][:100])

        # Filter by success rate
        effective = []
        for tag, stats in tag_stats.items():
            success_rate = (stats["successful"] / stats["total"]) * 100
            if success_rate >= min_success_rate:
                effective.append(
                    {
                        "pattern": tag,
                        "success_rate": round(success_rate, 1),
                        "total_uses": stats["total"],
                        "example_prompts": stats["prompts"][:3],
                    }
                )

        return sorted(effective, key=lambda x: x["success_rate"], reverse=True)

    def find_inefficient_prompts(self, token_threshold: int = 10000) -> List[Dict]:
        """
        Find prompts that consumed excessive tokens.

        Args:
            token_threshold: Token count threshold

        Returns:
            List of inefficient prompts
        """
        inefficient = []

        for interaction_id, data in self.prompts.items():
            if data["tokens"]["total"] > token_threshold:
                inefficient.append(
                    {
                        "interaction_id": interaction_id,
                        "tokens": data["tokens"]["total"],
                        "cost": data["cost_usd"],
                        "prompt_preview": data["prompt"][:100] + "...",
                        "tags": data["tags"],
                    }
                )

        return sorted(inefficient, key=lambda x: x["tokens"], reverse=True)

    def generate_obsidian_moc(self) -> str:
        """
        Generate Obsidian MOC (Map of Content) for prompt database.

        Returns:
            Markdown content for Obsidian MOC
        """
        stats = self.get_stats()

        moc_lines = [
            "# Prompt Tracker - MOC",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Statistics",
            "",
            f"- Total Interactions: {stats['total_interactions']}",
            f"- Total Tokens: {stats['total_tokens']:,}",
            f"- Total Cost: ${stats['total_cost']}",
            f"- Success Rate: {stats['success_rate']}%",
            f"- Avg Tokens/Interaction: {stats['avg_tokens_per_interaction']}",
            "",
            "## Effective Patterns",
            "",
        ]

        effective = self.find_effective_patterns()
        for pattern in effective[:10]:
            moc_lines.extend(
                [
                    f"### {pattern['pattern']}",
                    "",
                    f"**Success Rate**: {pattern['success_rate']}%",
                    f"**Total Uses**: {pattern['total_uses']}",
                    "",
                    "**Example Prompts**:",
                    *[f"- {p}" for p in pattern["example_prompts"]],
                    "",
                    "---",
                    "",
                ]
            )

        # Inefficient prompts
        inefficient = self.find_inefficient_prompts()
        if inefficient:
            moc_lines.extend(["", "## Inefficient Prompts (>10K tokens)", ""])
            for prompt in inefficient[:5]:
                moc_lines.extend(
                    [
                        f"- **{prompt['tokens']:,} tokens** (${prompt['cost']})",
                        f"  - {prompt['prompt_preview']}",
                        f"  - Tags: {', '.join('#' + tag for tag in prompt['tags'])}",
                        "",
                    ]
                )

        return "\n".join(moc_lines)

    def export_to_obsidian(self, vault_path: str):
        """
        Export prompt database to Obsidian vault.

        Args:
            vault_path: Path to Obsidian vault root
        """
        vault_path = Path(vault_path)
        moc_file = vault_path / "Prompt_Tracker.md"

        moc_content = self.generate_obsidian_moc()
        moc_file.write_text(moc_content, encoding="utf-8")

        print(f"[SUCCESS] Exported prompt tracker to {moc_file}")


# Convenience function for quick tracking
def track_quick(prompt: str, response: str, success: bool = True):
    """
    Quick tracking function for immediate use.

    Example:
        track_quick(
            prompt="Implement feature X",
            response="[implementation]",
            success=True
        )
    """
    tracker = PromptTracker()
    tracker.track_interaction(
        prompt=prompt,
        response=response,
        tokens_input=len(prompt.split()) * 2,  # Rough estimate
        tokens_output=len(response.split()) * 2,
        success=success,
    )


if __name__ == "__main__":
    # Demo usage
    tracker = PromptTracker()

    # Track sample interaction
    interaction_id = tracker.track_interaction(
        prompt="Implement error learning database with 90% test coverage",
        response="Created ErrorLearner class with 22 tests, 91% coverage",
        model="claude-sonnet-4",
        tokens_input=1500,
        tokens_output=3000,
        success=True,
        tags=["implementation", "testing", "database"],
    )

    print(f"Tracked interaction: {interaction_id}")

    # Get stats
    stats = tracker.get_stats()
    print(f"\nStats: {stats['total_interactions']} interactions")
    print(f"Total cost: ${stats['total_cost']}")
    print(f"Success rate: {stats['success_rate']}%")
