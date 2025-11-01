#!/usr/bin/env python3
"""
Error Logger - Search-Optimized Obsidian Saving

Saves errors and solutions in search-optimized format for AI auto-recovery.
Designed to work with OBSIDIAN_AUTO_SEARCH.md proactive search system.

Usage:
    from error_logger import ErrorLogger

    logger = ErrorLogger()
    logger.log_error(
        error_type="ModuleNotFoundError",
        error_message="No module named 'pandas'",
        solution="pip install pandas",
        context={"file": "data_exporter.py", "line": 3}
    )
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ErrorLogger:
    """
    Log errors in search-optimized format to Obsidian

    Key features:
    - Extracts search keywords automatically
    - Standardizes error tags
    - Generates search-friendly titles
    - Includes solution commands
    - Tracks reuse count for ROI metrics
    """

    def __init__(self, vault_path: Optional[str] = None):
        self.vault_path = vault_path or os.getenv("OBSIDIAN_VAULT_PATH", "C:/Users/user/Documents/Obsidian Vault")
        self.error_dir = Path(self.vault_path) / "Errors"
        self.error_dir.mkdir(exist_ok=True)

        # Error type taxonomy for standardized tags
        self.error_taxonomy = {
            "ModuleNotFoundError": "error/import",
            "ImportError": "error/import",
            "FileNotFoundError": "error/file-not-found",
            "PermissionError": "error/permission",
            "UnicodeDecodeError": "error/encoding",
            "UnicodeEncodeError": "error/encoding",
            "SyntaxError": "error/syntax",
            "TypeError": "error/type",
            "ValueError": "error/value",
            "AssertionError": "error/test-failure",
            "401": "error/auth-401",
            "403": "error/auth-403",
            "404": "error/not-found-404",
            "500": "error/server-500",
        }

        # Solution type taxonomy
        self.solution_taxonomy = {
            "pip install": "solution/pip-install",
            "chmod": "solution/chmod",
            "export": "solution/env-var",
            "set": "solution/env-var",
            "echo": "solution/env-var",
            "npm install": "solution/npm-install",
        }

    def extract_search_keywords(self, error_type: str, error_message: str, context: Dict) -> Dict:
        """Extract keywords for search optimization (hierarchical structure)"""
        keywords = {"error_type": error_type, "category": None, "tech_stack": [], "specific": []}

        # 1. Category mapping (error type → category)
        category_map = {
            "ModuleNotFoundError": "import",
            "ImportError": "import",
            "FileNotFoundError": "file-not-found",
            "PermissionError": "permission",
            "UnicodeDecodeError": "encoding",
            "UnicodeEncodeError": "encoding",
            "SyntaxError": "syntax",
            "TypeError": "type",
            "ValueError": "value",
            "AssertionError": "test-failure",
            "401": "auth",
            "403": "auth",
            "404": "not-found",
            "500": "server",
        }
        keywords["category"] = category_map.get(error_type, "runtime")

        # 2. Extract specific keywords (max 3)
        # Module/package names
        module_match = re.search(r"module named ['\"](\w+)['\"]", error_message)
        if module_match:
            keywords["specific"].append(module_match.group(1))

        # File names
        file_match = re.search(r"File ['\"]([^'\"]+)['\"]", error_message)
        if file_match:
            filename = Path(file_match.group(1)).stem
            keywords["specific"].append(filename)

        # Error codes
        code_match = re.search(r"\b(\d{3})\b", error_message)
        if code_match:
            keywords["specific"].append(code_match.group(1))

        # Context file
        if "file" in context:
            file_stem = Path(context["file"]).stem
            if file_stem and file_stem not in keywords["specific"]:
                keywords["specific"].append(file_stem)

        # Limit to 3 most relevant
        keywords["specific"] = keywords["specific"][:3]

        # 3. Tech stack detection (max 1)
        tech_indicators = {
            "python": [".py", "pip", "venv", "pytest", "python"],
            "javascript": [".js", "npm", "node", "jest"],
            "typescript": [".ts", ".tsx", "typescript"],
            "react": ["jsx", "tsx", "react"],
            "vue": ["vue", ".vue"],
            "django": ["django", "manage.py"],
            "fastapi": ["fastapi", "uvicorn"],
        }

        context_str = str(context).lower() + error_message.lower()
        for tech, indicators in tech_indicators.items():
            if any(ind in context_str for ind in indicators):
                keywords["tech_stack"].append(tech)
                break  # Only first match

        return keywords

    def standardize_tags(self, keywords: Dict, solution: str) -> List[str]:
        """Generate hierarchical tags for consistent search"""
        tags = []

        # Level 1: Error category
        if keywords["category"]:
            tags.append(f"error/{keywords['category']}")

        # Level 2: Error type
        error_tag = self.error_taxonomy.get(keywords["error_type"])
        if error_tag:
            tags.append(error_tag)
        else:
            tags.append(f"error/{keywords['error_type'].lower().replace(' ', '-')}")

        # Level 3: Specific (first keyword only)
        if keywords["specific"]:
            specific_tag = f"error/{keywords['category']}/{keywords['specific'][0].lower()}"
            tags.append(specific_tag)

        # Solution type tag
        for pattern, tag in self.solution_taxonomy.items():
            if pattern in solution.lower():
                tags.append(tag)
                break

        # Tech stack tag
        if keywords["tech_stack"]:
            tags.append(f"tech/{keywords['tech_stack'][0]}")

        # Status and generic tags
        tags.extend(["status/resolved", "type/debug", "source/ai-recovery"])

        return tags

    def generate_search_optimized_filename(self, keywords: Dict) -> str:
        """Generate filename optimized for search"""
        # Format: Debug-{ErrorType}-{keyword1}-{keyword2}-{DATE}.md
        date = datetime.now().strftime("%Y-%m-%d")

        # Clean error type
        error_type = keywords["error_type"]
        clean_error = error_type.replace("Error", "").replace(" ", "-")

        # Take top 2 specific keywords
        keyword_str = "-".join(keywords["specific"][:2]) if keywords["specific"] else "generic"

        return f"Debug-{clean_error}-{keyword_str}-{date}.md"

    def generate_yaml_frontmatter(
        self, keywords: Dict, error_message: str, solution: str, context: Dict, tags: List[str]
    ) -> str:
        """Generate search-optimized YAML frontmatter"""
        now = datetime.now()

        yaml_lines = [
            "---",
            f"date: {now.strftime('%Y-%m-%d')}",
            f"time: {now.strftime('%H:%M')}",
            f"error_type: {keywords['error_type']}",
            f"error_category: {keywords['category']}",
            f'error_message: "{error_message[:200]}"',  # Truncate long messages
            f'solution_command: "{solution}"',
            "tags:",
        ]

        # Add tags (one per line for better readability)
        for tag in tags:
            yaml_lines.append(f"  - {tag}")

        # Add search keywords (specific keywords only)
        yaml_lines.append("search_keywords:")
        for keyword in keywords["specific"]:
            yaml_lines.append(f"  - {keyword}")

        # Add tech stack
        if keywords["tech_stack"]:
            yaml_lines.append(f"tech_stack: {keywords['tech_stack'][0]}")

        # Add context fields
        if "file" in context:
            yaml_lines.append(f'context_file: "{context["file"]}"')
        if "line" in context:
            yaml_lines.append(f"context_line: {context['line']}")
        if "function" in context:
            yaml_lines.append(f'context_function: "{context["function"]}"')

        # Metrics for ROI tracking
        yaml_lines.extend(
            [
                "time_saved: 28  # Estimated minutes saved on reuse",
                "reuse_count: 0  # Auto-incremented on each reuse",
                "---",
            ]
        )

        return "\n".join(yaml_lines)

    def generate_content(
        self,
        keywords: Dict,
        error_message: str,
        solution: str,
        context: Dict,
        tags: List[str],
        details: Optional[str] = None,
    ) -> str:
        """Generate search-optimized content with hashtags"""
        # Generate hashtags from top 5 tags
        hashtags = " ".join(f"#{tag}" for tag in tags[:5])

        content_lines = [
            f"# {keywords['error_type']}",
            "",
            "## Classification",
            hashtags,
            "",
            "## Quick Keywords",
            f"`{keywords['error_type']}` " + " ".join(f"`{kw}`" for kw in keywords["specific"][:3]),
            "",
            "## Error Details",
            "",
            "```",
            error_message,
            "```",
            "",
            "## Solution",
            "",
            "```bash",
            solution,
            "```",
            "",
            "## Context",
            "",
        ]

        # Add context information
        if "file" in context:
            content_lines.append(f"- **File**: `{context['file']}`")
        if "line" in context:
            content_lines.append(f"- **Line**: {context['line']}")
        if "function" in context:
            content_lines.append(f"- **Function**: `{context['function']}`")
        if "trigger" in context:
            content_lines.append(f"- **Trigger**: {context['trigger']}")
        if "environment" in context:
            content_lines.append(f"- **Environment**: {context['environment']}")

        content_lines.append("")

        # Add details if provided
        if details:
            content_lines.extend(
                [
                    "## Additional Details",
                    "",
                    details,
                    "",
                ]
            )

        # Add prevention checklist
        content_lines.extend(
            [
                "## Prevention Checklist",
                "",
                "- [ ] Add to project documentation",
                "- [ ] Update setup instructions",
                "- [ ] Add validation check",
                "- [ ] Include in onboarding guide",
                "",
            ]
        )

        # Add related documents placeholder
        content_lines.extend(
            [
                "## Related",
                "",
                "<!-- Links to related error solutions will be auto-added by AI -->",
                "",
            ]
        )

        return "\n".join(content_lines)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        solution: str,
        context: Optional[Dict] = None,
        details: Optional[str] = None,
    ) -> Path:
        """
        Log error in search-optimized format

        Args:
            error_type: Type of error (e.g., "ModuleNotFoundError")
            error_message: Full error message
            solution: Solution command or description
            context: Additional context (file, line, function, etc.)
            details: Optional additional details

        Returns:
            Path to created Obsidian document
        """
        context = context or {}

        # Extract search keywords (now returns Dict)
        keywords = self.extract_search_keywords(error_type, error_message, context)

        # Generate standardized tags (now accepts Dict)
        tags = self.standardize_tags(keywords, solution)

        # Generate filename (now accepts Dict)
        filename = self.generate_search_optimized_filename(keywords)
        filepath = self.error_dir / filename

        # Check if similar error already exists
        existing = self._find_existing_error(keywords)
        if existing:
            print(f"[INFO] Similar error already logged: {existing}")
            self._increment_reuse_count(existing)
            return existing

        # Generate YAML frontmatter (updated signature)
        yaml = self.generate_yaml_frontmatter(keywords, error_message, solution, context, tags)

        # Generate content (updated signature)
        content = self.generate_content(keywords, error_message, solution, context, tags, details)

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml)
            f.write("\n\n")
            f.write(content)

        print(f"[OK] Error logged: {filepath}")
        return filepath

    def _find_existing_error(self, keywords: Dict) -> Optional[Path]:
        """Check if similar error already exists using filename pattern matching"""
        if not self.error_dir.exists():
            return None

        error_type = keywords["error_type"]
        specific_keywords = keywords["specific"]

        # Look for files matching the error type
        for file in self.error_dir.glob(f"Debug-*{error_type.replace('Error', '')}*.md"):
            # Check if any specific keyword matches in filename
            if any(keyword.lower() in file.name.lower() for keyword in specific_keywords):
                return file

        return None

    def _increment_reuse_count(self, filepath: Path):
        """Increment reuse_count in YAML frontmatter"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Update reuse_count
            content = re.sub(r"reuse_count: (\d+)", lambda m: f"reuse_count: {int(m.group(1)) + 1}", content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Incremented reuse_count: {filepath.name}")

        except Exception as e:
            print(f"[WARN] Failed to increment reuse_count: {e}")


def main():
    """Demo usage"""
    logger = ErrorLogger()

    # Example 1: ModuleNotFoundError
    logger.log_error(
        error_type="ModuleNotFoundError",
        error_message="No module named 'pandas'",
        solution="pip install pandas",
        context={
            "file": "scripts/data_exporter.py",
            "line": 3,
            "trigger": "import pandas as pd",
            "environment": "Windows, Python 3.11, venv",
        },
        details="This error occurs when pandas is not installed in the virtual environment.",
    )

    # Example 2: Permission Error
    logger.log_error(
        error_type="PermissionError",
        error_message="Permission denied: 'scripts/deploy.sh'",
        solution="chmod +x scripts/deploy.sh",
        context={"file": "scripts/deploy.sh", "trigger": "Edit file operation", "environment": "Linux"},
    )

    # Example 3: 401 Error
    logger.log_error(
        error_type="401",
        error_message="401 Unauthorized: AUTH_SECRET not set",
        solution="export AUTH_SECRET=your_secret_key",
        context={"file": "tests/test_auth.py", "function": "test_login", "trigger": "pytest execution"},
    )

    print("\n[DEMO] Error logging complete!")
    print(f"[INFO] Check errors in: {logger.error_dir}")


if __name__ == "__main__":
    main()
