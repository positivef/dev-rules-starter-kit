#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDE.md Smart Updater - Constitution-Based Auto-Update
=========================================================

Core Features:
1. Constitution.yaml -> CLAUDE.md table auto-generation
2. Development Process Articles (P1-P10) table update
3. Governance Articles (P11-P15) table update
4. Strategy Articles (P16) table update
5. Version info and timestamp auto-update

Goal: Eliminate manual CLAUDE.md updates (30min -> 3sec)
"""

import yaml
import re
from pathlib import Path
from typing import Dict
from datetime import datetime


class ConstitutionTableGenerator:
    """Convert Constitution articles to markdown tables"""

    def __init__(self, constitution_path: Path):
        self.constitution_path = constitution_path
        self.constitution = self._load_constitution()

    def _load_constitution(self) -> Dict:
        """Load Constitution.yaml"""
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_process_table(self) -> str:
        """Generate Development Process Articles (P1-P10) table"""
        table = """### Development Process Articles (P1-P10)

| ID | Article | Enforcement Tool | When to Use? |
|----|---------|------------------|--------------|
"""

        for article in self.constitution.get("articles", []):
            article_id = article.get("id", "")

            # Filter P1-P10 only
            if not article_id.startswith("P"):
                continue

            try:
                num = int(article_id[1:])
                if num < 1 or num > 10:
                    continue
            except ValueError:
                continue

            name = article.get("name", "")
            tool = article.get("enforcement_tool", "N/A")

            # Extract when to use (from requires section)
            when_to_use = self._extract_when_to_use(article)

            table += f"| **{article_id}** | {name} | {tool} | {when_to_use} |\n"

        return table

    def generate_governance_table(self) -> str:
        """Generate Governance Articles (P11-P15) table"""
        table = """### Governance Articles (P11-P15)

| ID | Article | Purpose | When to Apply |
|----|---------|---------|---------------|
"""

        for article in self.constitution.get("articles", []):
            article_id = article.get("id", "")

            # Filter P11-P15 only
            if not article_id.startswith("P"):
                continue

            try:
                num = int(article_id[1:])
                if num < 11 or num > 15:
                    continue
            except ValueError:
                continue

            name = article.get("name", "")
            purpose = article.get("purpose", article.get("description", ""))
            when_to_apply = self._extract_when_to_apply(article)

            table += f"| **{article_id}** | {name} | {purpose[:50]}... | {when_to_apply} |\n"

        return table

    def generate_strategy_table(self) -> str:
        """Generate Strategy Articles (P16) table"""
        table = """### Strategy Articles (P16)

| ID | Article | Enforcement Tool | When to Use? |
|----|---------|------------------|--------------|
"""

        for article in self.constitution.get("articles", []):
            article_id = article.get("id", "")

            # P16 only
            if article_id != "P16":
                continue

            name = article.get("name", "")
            tool = article.get("enforcement_tool", "N/A")
            when_to_use = self._extract_when_to_use(article)

            table += f"| **{article_id}** | {name} | {tool} | {when_to_use} |\n"

        return table

    def _extract_when_to_use(self, article: Dict) -> str:
        """Extract 'when to use' information"""
        # Extract from enforcement
        enforcement = article.get("enforcement", {})
        when = enforcement.get("when", "")

        if when:
            return when[:40] + "..." if len(when) > 40 else when

        # Or extract first item from requires
        requires = article.get("requires", [])
        if requires and isinstance(requires, list) and len(requires) > 0:
            first_req = requires[0]
            if isinstance(first_req, str):
                return first_req[:40]

        # Default value
        return "Always"

    def _extract_when_to_apply(self, article: Dict) -> str:
        """Extract 'when to apply' information"""
        enforcement = article.get("enforcement", {})
        when = enforcement.get("when", "")

        if when:
            return when[:30] + "..." if len(when) > 30 else when

        # Default value
        return "Important decisions"


class ClaudeMdUpdater:
    """CLAUDE.md update engine"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_md = project_root / "CLAUDE.md"
        self.constitution_path = project_root / "config" / "constitution.yaml"
        self.generator = ConstitutionTableGenerator(self.constitution_path)

    def update_tables(self) -> bool:
        """Update all Constitution tables"""
        if not self.claude_md.exists():
            print(f"[ERROR] {self.claude_md} not found")
            return False

        try:
            # Read current content
            with open(self.claude_md, "r", encoding="utf-8") as f:
                content = f.read()

            # Update each section
            content = self._update_process_section(content)
            content = self._update_governance_section(content)
            content = self._update_strategy_section(content)
            content = self._update_version_info(content)

            # Write back
            with open(self.claude_md, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[SUCCESS] Updated {self.claude_md}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to update CLAUDE.md: {e}")
            return False

    def _update_process_section(self, content: str) -> str:
        """Update Development Process Articles section"""
        new_table = self.generator.generate_process_table()

        # Find and replace the section
        pattern = r"(### 개발 프로세스 조항 \(P1-P10\).*?\n\n)(.*?)(\n\n###|\Z)"

        def replacement(match):
            return match.group(1) + new_table.split("\n\n", 1)[1] + "\n\n" + match.group(3)

        updated = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if updated == content:
            print("[WARN] Process section not found or not updated")
        else:
            print("[UPDATE] Process section updated")

        return updated

    def _update_governance_section(self, content: str) -> str:
        """Update Governance Articles section"""
        new_table = self.generator.generate_governance_table()

        pattern = r"(### 거버넌스 조항 \(P11-P15\).*?\n\n)(.*?)(\n\n###|\Z)"

        def replacement(match):
            return match.group(1) + new_table.split("\n\n", 1)[1] + "\n\n" + match.group(3)

        updated = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if updated == content:
            print("[WARN] Governance section not found or not updated")
        else:
            print("[UPDATE] Governance section updated")

        return updated

    def _update_strategy_section(self, content: str) -> str:
        """Update Strategy Articles section"""
        new_table = self.generator.generate_strategy_table()

        pattern = r"(### 전략 조항 \(P16\).*?\n\n)(.*?)(\n\n##|\Z)"

        def replacement(match):
            return match.group(1) + new_table.split("\n\n", 1)[1] + "\n\n" + match.group(3)

        updated = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if updated == content:
            print("[WARN] Strategy section not found or not updated")
        else:
            print("[UPDATE] Strategy section updated")

        return updated

    def _update_version_info(self, content: str) -> str:
        """Update version info and timestamp"""
        # Update last update timestamp
        today = datetime.now().strftime("%Y-%m-%d")

        # Find version line
        pattern = r"\*\*Last Update\*\*:.*"
        replacement = f"**Last Update**: {today}"

        updated = re.sub(pattern, replacement, content)

        if updated == content:
            print("[WARN] Version info not found")
        else:
            print("[UPDATE] Version info updated")

        return updated

    def generate_full_constitution_summary(self) -> str:
        """Generate full Constitution summary"""
        summary = "## Constitution Summary (Auto-Generated)\n\n"

        summary += self.generator.generate_process_table() + "\n\n"
        summary += self.generator.generate_governance_table() + "\n\n"
        summary += self.generator.generate_strategy_table() + "\n\n"

        summary += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += "**Source**: config/constitution.yaml\n"

        return summary


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="CLAUDE.md Smart Updater")
    parser.add_argument("--summary", action="store_true", help="Generate full summary")
    parser.add_argument("--output", type=str, help="Output file for summary")

    args = parser.parse_args()

    updater = ClaudeMdUpdater(Path.cwd())

    if args.summary:
        summary = updater.generate_full_constitution_summary()

        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"[SUCCESS] Summary saved to {output_path}")
        else:
            print(summary)
    else:
        success = updater.update_tables()
        return 0 if success else 1


if __name__ == "__main__":
    exit(main())
