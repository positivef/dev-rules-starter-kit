#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Feedback CLI - Command-line interface for prompt quality analysis

Provides instant feedback on prompt quality through command-line interface.
Can be integrated with VS Code, pre-commit hooks, or used standalone.

Usage:
    python prompt_feedback_cli.py "your prompt here"
    python prompt_feedback_cli.py --file prompt.txt
    python prompt_feedback_cli.py --interactive
    python prompt_feedback_cli.py --track-user john_doe
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prompt_feedback_analyzer import PromptFeedbackAnalyzer, PromptAnalysis


class PromptFeedbackCLI:
    """Command-line interface for prompt feedback system"""

    def __init__(self):
        self.analyzer = PromptFeedbackAnalyzer()

    def analyze_prompt(self, prompt: str, output_format: str = "text") -> None:
        """Analyze a single prompt and display results"""
        analysis = self.analyzer.analyze(prompt)

        if output_format == "json":
            self._output_json(analysis)
        elif output_format == "brief":
            self._output_brief(analysis)
        else:
            self._output_full(analysis)

    def _output_json(self, analysis: PromptAnalysis) -> None:
        """Output analysis as JSON"""
        output = {
            "overall_score": analysis.overall_score,
            "scores": {
                "clarity": analysis.clarity_score,
                "logic": analysis.logic_score,
                "context": analysis.context_score,
                "structure": analysis.structure_score,
            },
            "issues": analysis.issues,
            "improvements": analysis.improvements,
            "strengths": analysis.strengths,
        }
        print(json.dumps(output, indent=2))

    def _output_brief(self, analysis: PromptAnalysis) -> None:
        """Output brief analysis (one line)"""
        level = self._get_level_emoji(analysis.overall_score)
        print(f"{level} Score: {analysis.overall_score:.0f}/100 | ", end="")

        if analysis.issues:
            issue_count = len(analysis.issues)
            print(f"{issue_count} issues found | ", end="")

        if analysis.improvements:
            print(f"Top suggestion: {analysis.improvements[0]['suggestion']}")
        else:
            print("Looking good!")

    def _output_full(self, analysis: PromptAnalysis) -> None:
        """Output full analysis"""
        feedback = self.analyzer.generate_feedback(analysis)
        print(feedback)

    def _get_level_emoji(self, score: float) -> str:
        """Get level indicator (no emoji for Windows)"""
        if score >= 90:
            return "[EXPERT]"
        elif score >= 75:
            return "[ADVANCED]"
        elif score >= 60:
            return "[INTERMEDIATE]"
        elif score >= 40:
            return "[DEVELOPING]"
        else:
            return "[BEGINNER]"

    def interactive_mode(self) -> None:
        """Run in interactive mode"""
        print("=== Prompt Feedback Interactive Mode ===")
        print("Type your prompt and press Enter (or 'quit' to exit)")
        print("For multi-line prompts, end with '###' on a new line")
        print("")

        while True:
            try:
                print("-" * 60)
                lines = []

                # Collect input
                while True:
                    line = input("> " if not lines else "  ")
                    if not lines and line.lower() == "quit":
                        print("Goodbye!")
                        return
                    if line == "###":
                        break
                    lines.append(line)
                    if not lines[0].endswith("###") and len(lines) == 1:
                        # Single line input
                        break

                prompt = "\n".join(lines)
                if prompt.strip():
                    print("\n" + "=" * 60)
                    self.analyze_prompt(prompt)
                    print("")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    def compare_prompts(self, prompt1: str, prompt2: str) -> None:
        """Compare two prompts side by side"""
        analysis1 = self.analyzer.analyze(prompt1)
        analysis2 = self.analyzer.analyze(prompt2)

        print("=== Prompt Comparison ===")
        print("")
        print("Prompt 1:")
        print(f"  {prompt1[:100]}..." if len(prompt1) > 100 else f"  {prompt1}")
        print(f"  Overall Score: {analysis1.overall_score:.0f}/100")
        print("")
        print("Prompt 2:")
        print(f"  {prompt2[:100]}..." if len(prompt2) > 100 else f"  {prompt2}")
        print(f"  Overall Score: {analysis2.overall_score:.0f}/100")
        print("")

        # Compare scores
        print("Score Comparison:")
        dimensions = ["clarity", "logic", "context", "structure"]
        for dim in dimensions:
            score1 = getattr(analysis1, f"{dim}_score")
            score2 = getattr(analysis2, f"{dim}_score")
            diff = score2 - score1

            if diff > 0:
                symbol = "+"
                better = "Prompt 2"
            elif diff < 0:
                symbol = ""
                better = "Prompt 1"
            else:
                symbol = ""
                better = "Equal"

            print(f"  {dim.title():12} | P1: {score1:3.0f} | P2: {score2:3.0f} | Diff: {symbol}{diff:3.0f} ({better})")

        print("")
        winner_score = analysis2.overall_score - analysis1.overall_score
        if winner_score > 5:
            print(f"[RESULT] Prompt 2 is significantly better (+{winner_score:.0f} points)")
        elif winner_score < -5:
            print(f"[RESULT] Prompt 1 is significantly better (+{-winner_score:.0f} points)")
        else:
            print("[RESULT] Both prompts are similar in quality")

    def track_user_progress(self, user_id: str) -> None:
        """Display user's improvement tracking"""
        progress = self.analyzer.track_improvement(user_id)

        if "message" in progress:
            print(progress["message"])
            return

        print(f"=== Progress Report for {user_id} ===")
        print("")
        print(f"Total Analyses: {progress['total_analyses']}")
        print(f"Recent Average Score: {progress['recent_average']:.1f}/100")
        print(f"Improvement: {progress['improvement']:+.1f} points")
        print(f"Trend: {progress['trend'].upper()}")
        print(f"Strongest Area: {progress['best_dimension'].title()}")
        print(f"Focus Area: {progress['focus_area'].title()}")

        # Provide personalized advice
        print("")
        print("=== Personalized Advice ===")
        focus = progress["focus_area"]
        if focus == "clarity":
            print("- Replace vague terms with specific descriptions")
            print("- Use concrete examples and exact file/function names")
            print("- Avoid words like 'somehow', 'better', 'fix'")
        elif focus == "logic":
            print("- Use logical connectors (first, then, because, if)")
            print("- Show clear relationships between tasks")
            print("- Ensure instructions follow a logical sequence")
        elif focus == "context":
            print("- Always specify the technical environment")
            print("- Include constraints and requirements")
            print("- Mention expected output format and location")
        else:
            print("- Use numbered lists for complex requests")
            print("- Break down tasks into clear steps")
            print("- Separate different concerns into sections")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze prompt quality and get improvement suggestions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Update the login function"
  %(prog)s --file requirements.txt --format json
  %(prog)s --interactive
  %(prog)s --compare "fix it" "Fix the authentication bug in login.py"
  %(prog)s --track-user john_doe
        """,
    )

    parser.add_argument("prompt", nargs="?", help="The prompt to analyze")
    parser.add_argument("-f", "--file", help="Read prompt from file")
    parser.add_argument("--format", choices=["text", "json", "brief"], default="text", help="Output format (default: text)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--compare", nargs=2, metavar=("PROMPT1", "PROMPT2"), help="Compare two prompts")
    parser.add_argument("--track-user", help="Track improvement for specific user")

    args = parser.parse_args()

    cli = PromptFeedbackCLI()

    # Handle different modes
    if args.interactive:
        cli.interactive_mode()
    elif args.compare:
        cli.compare_prompts(args.compare[0], args.compare[1])
    elif args.track_user:
        cli.track_user_progress(args.track_user)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            prompt = f.read()
        cli.analyze_prompt(prompt, args.format)
    elif args.prompt:
        cli.analyze_prompt(args.prompt, args.format)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
