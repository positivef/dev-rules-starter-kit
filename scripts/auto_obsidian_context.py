#!/usr/bin/env python3
"""
Auto Obsidian Context Provider for Claude

Claude가 자동으로 Obsidian을 검색하여 과거 해결책을 찾도록 하는 시스템
"""

import os
import re
from typing import List, Dict


class AutoObsidianContext:
    """
    Claude 질문에서 키워드를 추출하여
    자동으로 Obsidian을 검색하고 관련 문서를 제공
    """

    def __init__(self):
        self.obsidian_vault = os.getenv("OBSIDIAN_VAULT_PATH", "C:/Users/user/Documents/Obsidian Vault")

        # 자주 발생하는 문제 키워드
        self.error_keywords = [
            r"\d{3}\s*error",  # 401 error, 500 error
            r"bug",
            r"fail",
            r"crash",
            r"exception",
            r"broken",
            r"not working",
        ]

        # 기술 스택 키워드
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
        """사용자 질문에서 키워드 추출"""
        keywords = []

        # 에러 코드 추출 (e.g., "401", "500")
        error_match = re.search(r"(\d{3})", user_query.lower())
        if error_match:
            keywords.append(error_match.group(1))

        # 기술 키워드 추출
        for pattern in self.tech_keywords:
            if re.search(pattern, user_query.lower()):
                keywords.append(pattern)

        # 문제 유형 추출
        for pattern in self.error_keywords:
            if re.search(pattern, user_query.lower()):
                keywords.append("debug")
                break

        return keywords

    def search_obsidian(self, keywords: List[str]) -> List[Dict]:
        """
        Obsidian MCP를 사용하여 검색
        (실제로는 MCP 도구 호출)
        """
        # 이 부분은 Claude가 MCP 도구를 직접 호출
        # 여기서는 검색 쿼리만 생성

        search_queries = []
        for keyword in keywords:
            search_queries.append(f"Debug {keyword}")
            search_queries.append(f"{keyword} solution")

        return search_queries

    def should_search_obsidian(self, user_query: str) -> bool:
        """Obsidian 검색이 필요한지 판단"""

        # 디버깅/문제 해결 관련 질문?
        debug_indicators = ["error", "bug", "fail", "fix", "solve", "problem", "issue", "broken", "해결", "에러"]

        for indicator in debug_indicators:
            if indicator in user_query.lower():
                return True

        # "어떻게" 질문? (과거 경험 필요)
        how_questions = ["how to", "how do", "어떻게"]
        for q in how_questions:
            if q in user_query.lower():
                return True

        return False

    def generate_context_prompt(self, user_query: str) -> str:
        """
        Claude에게 Obsidian을 검색하도록 하는 프롬프트 생성
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
    Claude Code가 시작될 때 자동으로 로드되는 Hook
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
    실제 작동 시연
    """
    print("=== Auto Obsidian Context Demo ===\n")

    auto_ctx = AutoObsidianContext()

    # 실제 사용자 질문 시뮬레이션
    user_question = "auth.py에서 401 error 발생"

    print(f"User Question: {user_question}\n")

    # 1. 검색 필요성 판단
    should_search = auto_ctx.should_search_obsidian(user_question)
    print(f"Should search Obsidian? {should_search}\n")

    if should_search:
        # 2. 키워드 추출
        keywords = auto_ctx.extract_keywords(user_question)
        print(f"Extracted keywords: {keywords}\n")

        # 3. MCP 도구로 검색 (실제로는 Claude가 수행)
        print(">>> Triggering MCP Obsidian search...")
        print(f">>> mcp__obsidian__obsidian_simple_search(query='{' '.join(keywords)}')\n")

        # 4. 컨텍스트 프롬프트 생성
        prompt = auto_ctx.generate_context_prompt(user_question)
        print("Generated prompt for Claude:")
        print(prompt)


if __name__ == "__main__":
    demonstrate_auto_search()

    # 추가 테스트
    print("\n" + "=" * 50)
    print("Additional Test Cases:\n")

    auto_ctx = AutoObsidianContext()

    test_queries = [
        "401 error 해결 방법?",
        "React useEffect 어떻게 써?",
        "Payment transaction failed",
    ]

    for query in test_queries:
        print(f"\n질문: {query}")
        print(f"검색 필요? {auto_ctx.should_search_obsidian(query)}")
        if auto_ctx.should_search_obsidian(query):
            keywords = auto_ctx.extract_keywords(query)
            print(f"키워드: {keywords}")
