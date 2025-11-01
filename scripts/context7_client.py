"""
Context7 MCP Client - Official Documentation Search

Wrapper for Context7 MCP server that provides access to official documentation
for libraries, frameworks, and programming languages.

Current Status: Simulation Mode
- Real MCP integration: TODO
- Simulated responses for common libraries: Working

Supported libraries (simulated):
- Python: pandas, numpy, scipy, matplotlib, sklearn, tensorflow, pytorch
- Python Web: fastapi, django, flask
- JavaScript: react, vue, angular, next, express

Usage:
    from scripts.context7_client import Context7Client

    client = Context7Client(enabled=True)

    if client.is_available():
        docs = client.search("ModuleNotFoundError pandas", library="pandas")
        print(docs)
"""

import re
from typing import Dict, Optional, Tuple

# Import confidence calculator
try:
    from confidence_calculator import ConfidenceCalculator
except ImportError:
    try:
        from scripts.confidence_calculator import ConfidenceCalculator
    except ImportError:
        # Fallback if confidence calculator not available
        ConfidenceCalculator = None


class Context7Client:
    """
    Wrapper for Context7 MCP server

    Provides search interface to official documentation.
    Currently uses simulation for common patterns.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize Context7 client

        Args:
            enabled: Whether to enable Context7 lookups
        """
        self.enabled = enabled
        self._cache = {}  # Simple cache for repeated queries
        self.confidence_calc = ConfidenceCalculator() if ConfidenceCalculator else None

    def is_available(self) -> bool:
        """Check if Context7 is available"""
        return self.enabled

    def search_with_confidence(
        self, query: str, library: Optional[str] = None, filters: Optional[Dict] = None, context: Optional[Dict] = None
    ) -> Tuple[Optional[str], float]:
        """
        Search Context7 and return solution with confidence score

        Args:
            query: Search query (usually error message)
            library: Optional library/framework name
            filters: Optional filters
            context: Additional context for confidence calculation

        Returns:
            Tuple of (solution, confidence_score)
            Example: ("pip install pandas", 0.95)
        """
        # Search for solution
        solution = self.search(query, library, filters)

        if not solution:
            return None, 0.0

        # Calculate confidence
        if self.confidence_calc:
            context = context or {}
            confidence, explanation = self.confidence_calc.calculate(error_msg=query, solution=solution, context=context)
            return solution, confidence
        else:
            # Fallback: simple heuristic
            confidence = self._simple_confidence_heuristic(query, solution)
            return solution, confidence

    def _simple_confidence_heuristic(self, query: str, solution: str) -> float:
        """
        Simple confidence calculation when ConfidenceCalculator not available

        Args:
            query: Error message
            solution: Proposed solution

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.70  # Base score

        # Bonus for simple install commands
        if "pip install" in solution.lower() or "npm install" in solution.lower():
            confidence += 0.15

        # Penalty for dangerous commands
        if any(cmd in solution.lower() for cmd in ["sudo", "rm -rf", "delete"]):
            confidence -= 0.20

        # Penalty for complex multi-step
        if solution.count("\n") > 2:
            confidence -= 0.10

        return max(0.0, min(1.0, confidence))

    def search(self, query: str, library: Optional[str] = None, filters: Optional[Dict] = None) -> Optional[str]:
        """
        Search Context7 for official documentation

        Args:
            query: Search query (usually error message)
            library: Optional library/framework name
            filters: Optional filters (type: installation, configuration, usage)

        Returns:
            Documentation string with solution, or None if not found
        """
        if not self.enabled:
            return None

        # Check cache first
        cache_key = f"{query}:{library}:{filters}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Extract library if not provided
        if not library:
            library = self.extract_library_name(query, {})

        # TODO: Implement actual Context7 MCP call
        # For now, simulate with known patterns
        docs = self._simulate_context7_search(query, library, filters)

        if docs:
            self._cache[cache_key] = docs

        return docs

    def extract_library_name(self, error_msg: str, context: Dict) -> Optional[str]:
        """
        Extract library/framework name from error message or context

        Args:
            error_msg: Error message
            context: Additional context

        Returns:
            Library name if detected, None otherwise
        """
        # Check context first
        if "library" in context:
            return context["library"]

        if "import" in context:
            return context["import"]

        # Pattern 1: ModuleNotFoundError
        module_match = re.search(r"module named ['\"](\w+)['\"]", error_msg.lower())
        if module_match:
            return module_match.group(1)

        # Pattern 2: Import statement
        import_match = re.search(r"import (\w+)", error_msg.lower())
        if import_match:
            return import_match.group(1)

        # Pattern 3: Common libraries in error message
        common_libs = [
            "pandas",
            "numpy",
            "scipy",
            "matplotlib",
            "sklearn",
            "tensorflow",
            "pytorch",
            "fastapi",
            "django",
            "flask",
            "react",
            "vue",
            "angular",
            "next",
            "express",
        ]

        error_lower = error_msg.lower()
        for lib in common_libs:
            if lib in error_lower:
                return lib

        return None

    def extract_solution_from_docs(self, docs: str) -> Optional[str]:
        """
        Extract actionable solution from documentation

        Args:
            docs: Documentation text

        Returns:
            Solution command/instruction, or None
        """
        # Pattern 1: pip install
        pip_match = re.search(r"(pip install [\w\-]+)", docs, re.IGNORECASE)
        if pip_match:
            return pip_match.group(1)

        # Pattern 2: npm install
        npm_match = re.search(r"(npm install [\w\-@/]+)", docs, re.IGNORECASE)
        if npm_match:
            return npm_match.group(1)

        # Pattern 3: Configuration change
        config_match = re.search(r"(set \w+ to .+|add .+ to config|update .+)", docs, re.IGNORECASE)
        if config_match:
            return config_match.group(1)

        return None

    def _simulate_context7_search(self, query: str, library: Optional[str], filters: Optional[Dict]) -> Optional[str]:
        """
        Simulate Context7 search for testing

        This will be replaced with actual MCP integration.

        Args:
            query: Search query
            library: Library name
            filters: Search filters

        Returns:
            Simulated documentation response
        """
        # Handle common library installation errors
        if library:
            lib_lower = library.lower()

            # Python libraries
            if lib_lower in [
                "pandas",
                "numpy",
                "scipy",
                "matplotlib",
                "sklearn",
                "seaborn",
            ]:
                return f"pip install {lib_lower}"

            # Python ML libraries
            if lib_lower in ["tensorflow", "pytorch", "torch"]:
                return f"pip install {lib_lower}"

            # Python web frameworks
            if lib_lower in ["fastapi", "django", "flask"]:
                return f"pip install {lib_lower}"

            # JavaScript libraries
            if lib_lower in ["react", "vue", "angular", "next", "svelte"]:
                return f"npm install {lib_lower}"

            # JavaScript frameworks/tools
            if lib_lower in ["express", "webpack", "vite", "jest"]:
                return f"npm install {lib_lower}"

        # Handle common error patterns
        query_lower = query.lower()

        # ModuleNotFoundError
        if "modulenotfounderror" in query_lower or "no module named" in query_lower:
            match = re.search(r"module named ['\"](\w+)['\"]", query_lower)
            if match:
                module_name = match.group(1)
                return f"pip install {module_name}"

        # ImportError
        if "importerror" in query_lower or "cannot import" in query_lower:
            match = re.search(r"cannot import .* from ['\"](\w+)['\"]", query_lower)
            if match:
                module_name = match.group(1)
                return f"pip install {module_name}"

        # Permission errors
        if "permission denied" in query_lower:
            if "windows" in query_lower or "win32" in query_lower:
                return "Run command prompt as Administrator"
            else:
                return "chmod +x filename or sudo command"

        # Encoding errors
        if "unicodedecodeerror" in query_lower or "encoding" in query_lower:
            return "Use UTF-8 encoding: open(file, encoding='utf-8')"

        # No simulation available
        return None


def main():
    """Demo usage of Context7Client"""
    print("=" * 60)
    print("Context7 MCP Client Demo (Simulation Mode)")
    print("=" * 60)

    client = Context7Client(enabled=True)

    test_cases = [
        "ModuleNotFoundError: No module named 'pandas'",
        "ImportError: cannot import name 'DataFrame' from 'pandas'",
        "PermissionError: [Errno 13] Permission denied",
        "UnicodeDecodeError: 'utf-8' codec can't decode",
        "Error: Module not found 'react'",
    ]

    for error in test_cases:
        print(f"\nError: {error}")

        library = client.extract_library_name(error, {})
        if library:
            print(f"Detected library: {library}")

        solution = client.search(error)
        if solution:
            print(f"Solution: {solution}")
        else:
            print("No solution found")

    print("\n" + "=" * 60)
    print("Cache status:", len(client._cache), "entries")


if __name__ == "__main__":
    main()
