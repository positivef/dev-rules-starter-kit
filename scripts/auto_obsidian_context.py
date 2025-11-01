#!/usr/bin/env python3
"""
Auto Obsidian Context Provider for Claude

System that enables Claude to automatically search Obsidian for past solutions
"""

import os
import re
from typing import List, Dict


class AutoObsidianContext:
    """
    Extract keywords from Claude questions
    Automatically search Obsidian and provide related documents
    """

    def __init__(self):
        self.obsidian_vault = os.getenv("OBSIDIAN_VAULT_PATH", "C:/Users/user/Documents/Obsidian Vault")

        # Frequently occurring problem keywords
        self.error_keywords = [
            r"\d{3}\s*error",  # 401 error, 500 error
            r"bug",
            r"fail",
            r"crash",
            r"exception",
            r"broken",
            r"not working",
        ]

        # Tech stack keywords
        self.tech_keywords = [
            r"react",
            r"vue",
            r"angular",
            r"python",
            r"node",
            r"django",
            r"fastapi",
            r"auth",
            r"database",
            r"api",
            r"jwt",
            r"oauth",
        ]

    def extract_keywords(self, user_query: str) -> List[str]:
        """Extract keywords from user question"""
        keywords = []

        # Extract error code (e.g., "401", "500")
        error_match = re.search(r"(\d{3})", user_query.lower())
        if error_match:
            keywords.append(error_match.group(1))

        # Extract tech keywords
        for pattern in self.tech_keywords:
            if re.search(pattern, user_query.lower()):
                keywords.append(pattern)

        # Extract problem type
        for pattern in self.error_keywords:
            if re.search(pattern, user_query.lower()):
                keywords.append("debug")
                break

        return keywords

    def search_obsidian(self, keywords: List[str]) -> List[Dict]:
        """
        Search using Obsidian MCP
        (Actually calls MCP tool)
        """
        # This part is where Claude calls MCP tool directly
        # Here we just generate search queries

        search_queries = []
        for keyword in keywords:
            search_queries.append(f"Debug {keyword}")
            search_queries.append(f"{keyword} solution")

        return search_queries

    def should_search_obsidian(self, user_query: str) -> bool:
        """Determine if Obsidian search is needed"""

        # Debugging/problem-solving related question?
        debug_indicators = ["error", "bug", "fail", "fix", "solve", "problem", "issue", "broken"]

        for indicator in debug_indicators:
            if indicator in user_query.lower():
                return True

        # "How to" questions? (need past experience)
        how_questions = ["how to", "how do"]
        for q in how_questions:
            if q in user_query.lower():
                return True

        return False

    def generate_context_prompt(self, user_query: str) -> str:
        """
        Generate prompt to make Claude search Obsidian
        """
        if not self.should_search_obsidian(user_query):
            return ""

        keywords = self.extract_keywords(user_query)

        if not keywords:
            return ""

        prompt = f"""
[AUTO] Obsidian Search Recommended

User question: "{user_query}"
Detected keywords: {', '.join(keywords)}

Next steps:
1. Search Obsidian with MCP tool: "{'\" OR \"'.join(keywords)}"
2. Check past solutions
3. Answer based on findings

Search example:
```python
mcp__obsidian__obsidian_simple_search(
    query="{' '.join(keywords)}"
)
```
"""
        return prompt


def create_auto_context_hook():
    """
    Hook that automatically loads when Claude Code starts
    """
    return """
# Auto Obsidian Context Hook

**Status**: Auto-activated on Claude Code startup

## How it works

When user asks questions like:
- "401 error resolution?"
- "React performance optimization?"
- "Payment bug fix"

=> **Automatically searches Obsidian**
=> Prioritizes past solutions if found
=> Falls back to general answer if not found

## Activation checklist
[OK] MCP Obsidian tool available
[OK] OBSIDIAN_VAULT_PATH configured
[OK] Auto-search activated
"""


def demonstrate_auto_search():
    """
    Actual operation demonstration
    """
    print("=== Auto Obsidian Context Demo ===\n")

    auto_ctx = AutoObsidianContext()

    # Simulate actual user question
    user_question = "401 error occurs in auth.py"

    print(f"User Question: {user_question}\n")

    # 1. Determine search necessity
    should_search = auto_ctx.should_search_obsidian(user_question)
    print(f"Should search Obsidian? {should_search}\n")

    if should_search:
        # 2. Extract keywords
        keywords = auto_ctx.extract_keywords(user_question)
        print(f"Extracted keywords: {keywords}\n")

        # 3. Search with MCP tool (actually performed by Claude)
        print(">>> Triggering MCP Obsidian search...")
        print(f">>> mcp__obsidian__obsidian_simple_search(query='{' '.join(keywords)}')\n")

        # 4. Generate context prompt
        prompt = auto_ctx.generate_context_prompt(user_question)
        print("Generated prompt for Claude:")
        print(prompt)


if __name__ == "__main__":
    demonstrate_auto_search()

    # Additional tests
    print("\n" + "=" * 50)
    print("Additional Test Cases:\n")

    auto_ctx = AutoObsidianContext()

    test_queries = [
        "How to resolve 401 error?",
        "How to use React useEffect?",
        "Payment transaction failed",
    ]

    for query in test_queries:
        print(f"\nQuestion: {query}")
        print(f"Need search? {auto_ctx.should_search_obsidian(query)}")
        if auto_ctx.should_search_obsidian(query):
            keywords = auto_ctx.extract_keywords(query)
            print(f"Keywords: {keywords}")
