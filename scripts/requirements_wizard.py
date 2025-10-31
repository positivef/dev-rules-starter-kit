#!/usr/bin/env python
"""
RequirementsWizard: Interactive Requirements Gathering Tool
===========================================================

대화형 요구사항 수집 도구 - Socratic 방법론으로 완전한 요구사항 도출

Features:
- Interactive wizard-style questionnaire
- Socratic method for discovery
- Requirement categorization (functional/non-functional)
- Priority matrix (MoSCoW)
- Risk assessment
- YAML contract generation
- Obsidian documentation

Constitutional Compliance:
- P1: YAML First - Generates YAML contracts
- P2: Evidence-Based - Records all decisions
- P3: Knowledge Asset - Syncs to Obsidian
- P6: Quality Gates - Requirement completeness checks
- P12: Trade-off Analysis - Documents decisions
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import yaml
from enum import Enum

# Constants
REQUIREMENT_TEMPLATE = """# {title}

## Overview
- **Type**: {type}
- **Priority**: {priority}
- **Risk Level**: {risk}
- **Created**: {created}

## Description
{description}

## Acceptance Criteria
{criteria}

## Technical Considerations
{technical}

## Dependencies
{dependencies}

## Trade-offs
{tradeoffs}

## Questions & Answers
{qa_log}
"""


class RequirementType(Enum):
    """Types of requirements"""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    USER_STORY = "user_story"
    CONSTRAINT = "constraint"


class Priority(Enum):
    """MoSCoW prioritization"""

    MUST = "Must have"
    SHOULD = "Should have"
    COULD = "Could have"
    WONT = "Won't have"


class RiskLevel(Enum):
    """Risk assessment levels"""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RequirementsWizard:
    """Interactive requirements gathering wizard"""

    def __init__(self):
        self.requirements = []
        self.qa_log = []
        self.project_context = {}
        self.discovered_items = {"stakeholders": set(), "systems": set(), "constraints": set(), "risks": set()}

    def print_banner(self):
        """Print welcome banner"""
        banner = """
[REQUIREMENTS WIZARD]
=====================================================
Interactive Requirements Discovery System
Using Socratic Method for Complete Requirement Elicitation
=====================================================
        """
        print(banner)

    def ask_question(self, question: str, options: List[str] = None, allow_multiple: bool = False) -> str:
        """Ask interactive question"""
        print(f"\n[QUESTION] {question}")

        if options:
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            if allow_multiple:
                print("  (Multiple choices allowed, comma-separated)")

            while True:
                try:
                    response = input("\nYour answer: ").strip()
                    if allow_multiple:
                        indices = [int(x.strip()) for x in response.split(",")]
                        if all(1 <= i <= len(options) for i in indices):
                            selected = [options[i - 1] for i in indices]
                            self.qa_log.append((question, selected))
                            return selected
                    else:
                        idx = int(response)
                        if 1 <= idx <= len(options):
                            self.qa_log.append((question, options[idx - 1]))
                            return options[idx - 1]
                    print("[ERROR] Invalid selection. Try again.")
                except (ValueError, IndexError):
                    print("[ERROR] Please enter a valid number.")
        else:
            response = input("\nYour answer: ").strip()
            self.qa_log.append((question, response))
            return response

    def gather_project_context(self):
        """Gather initial project context"""
        print("\n[PHASE 1] Project Context Discovery")
        print("=" * 50)

        # Project name and description
        self.project_context["name"] = self.ask_question("What is the project name?")

        self.project_context["description"] = self.ask_question("Briefly describe the project (2-3 sentences):")

        # Project type
        project_types = [
            "Web Application",
            "Mobile App",
            "API/Backend Service",
            "Data Pipeline",
            "Machine Learning",
            "DevOps/Infrastructure",
            "Library/Framework",
            "Other",
        ]
        self.project_context["type"] = self.ask_question("What type of project is this?", project_types)

        # Stakeholders
        stakeholders = self.ask_question("Who are the main stakeholders? (comma-separated)")
        self.discovered_items["stakeholders"].update([s.strip() for s in stakeholders.split(",")])

        # Timeline
        self.project_context["timeline"] = self.ask_question(
            "What is the expected timeline?", ["< 1 month", "1-3 months", "3-6 months", "6-12 months", "> 1 year"]
        )

        # Existing systems
        has_existing = self.ask_question("Are there existing systems to integrate with?", ["Yes", "No"])

        if has_existing == "Yes":
            systems = self.ask_question("List the existing systems (comma-separated):")
            self.discovered_items["systems"].update([s.strip() for s in systems.split(",")])

    def discover_requirements(self):
        """Discover requirements using Socratic method"""
        print("\n[PHASE 2] Requirements Discovery")
        print("=" * 50)

        continue_discovery = True
        requirement_count = 0

        while continue_discovery:
            requirement_count += 1
            print(f"\n[Requirement #{requirement_count}]")

            # Start with open-ended question
            initial = self.ask_question("Describe a feature or requirement for this project:")

            if initial.lower() in ["done", "finish", "no more", "exit"]:
                break

            requirement = {"description": initial}

            # Probe deeper with Socratic questions
            requirement["why"] = self.ask_question(f"Why is '{initial[:50]}...' important? What problem does it solve?")

            requirement["who"] = self.ask_question("Who will use this feature? What is their role?")

            requirement["when"] = self.ask_question(
                "When/how often will this be used?", ["Constantly", "Daily", "Weekly", "Monthly", "Rarely", "One-time setup"]
            )

            # Categorize requirement
            requirement["type"] = self.ask_question("What type of requirement is this?", [t.value for t in RequirementType])

            # Priority
            requirement["priority"] = self.ask_question("How critical is this requirement?", [p.value for p in Priority])

            # Technical probe
            requirement["technical"] = self.ask_question("Are there specific technical constraints or preferences?")

            # Dependencies
            requirement["dependencies"] = self.ask_question(
                "Does this depend on other features or systems? (list or 'none')"
            )

            # Acceptance criteria
            print("\n[ACCEPTANCE CRITERIA]")
            print("Define success criteria (enter 'done' when finished):")
            criteria = []
            while True:
                criterion = input(f"  Criteria {len(criteria)+1}: ").strip()
                if criterion.lower() == "done":
                    break
                if criterion:
                    criteria.append(criterion)
            requirement["criteria"] = criteria

            # Risk assessment
            requirement["risk"] = self.ask_question("What is the implementation risk level?", [r.value for r in RiskLevel])

            if requirement["risk"] in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
                requirement["risk_mitigation"] = self.ask_question("How can we mitigate this risk?")

            # Trade-offs
            requirement["tradeoffs"] = self.ask_question(
                "What trade-offs might this requirement involve? (performance, complexity, cost, time)"
            )

            self.requirements.append(requirement)

            # Check if more requirements
            more = self.ask_question("\nAdd another requirement?", ["Yes", "No"])
            continue_discovery = more == "Yes"

    def analyze_completeness(self) -> Dict[str, Any]:
        """Analyze requirement completeness"""
        analysis = {
            "total_requirements": len(self.requirements),
            "by_type": {},
            "by_priority": {},
            "by_risk": {},
            "coverage_gaps": [],
            "completeness_score": 0,
        }

        # Count by categories
        for req in self.requirements:
            req_type = req.get("type", "Unknown")
            priority = req.get("priority", "Unknown")
            risk = req.get("risk", "Unknown")

            analysis["by_type"][req_type] = analysis["by_type"].get(req_type, 0) + 1
            analysis["by_priority"][priority] = analysis["by_priority"].get(priority, 0) + 1
            analysis["by_risk"][risk] = analysis["by_risk"].get(risk, 0) + 1

        # Check for gaps
        if "functional" not in [r.get("type") for r in self.requirements]:
            analysis["coverage_gaps"].append("No functional requirements defined")

        if "Must have" not in [r.get("priority") for r in self.requirements]:
            analysis["coverage_gaps"].append("No 'Must have' requirements")

        if not any(r.get("criteria") for r in self.requirements):
            analysis["coverage_gaps"].append("Missing acceptance criteria")

        # Calculate completeness score
        score_factors = [
            len(self.requirements) >= 3,  # Minimum requirements
            len(analysis["by_type"]) >= 2,  # Multiple types
            "Must have" in analysis["by_priority"],  # Critical items defined
            all(r.get("criteria") for r in self.requirements),  # All have criteria
            len(self.discovered_items["stakeholders"]) > 0,  # Stakeholders identified
            self.project_context.get("timeline"),  # Timeline defined
            any(r.get("dependencies") != "none" for r in self.requirements),  # Dependencies mapped
        ]

        analysis["completeness_score"] = (sum(score_factors) / len(score_factors)) * 100

        return analysis

    def generate_yaml_contract(self) -> str:
        """Generate YAML contract for requirements"""
        contract = {
            "task_id": f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "title": f"Requirements for {self.project_context.get('name', 'Project')}",
            "description": self.project_context.get("description", ""),
            "metadata": {
                "created": datetime.now().isoformat(),
                "type": "requirements",
                "timeline": self.project_context.get("timeline", "TBD"),
                "stakeholders": list(self.discovered_items["stakeholders"]),
            },
            "requirements": [],
        }

        for i, req in enumerate(self.requirements, 1):
            req_entry = {
                "id": f"R{i:03d}",
                "description": req["description"],
                "type": req["type"],
                "priority": req["priority"],
                "risk": req["risk"],
                "rationale": req["why"],
                "user": req["who"],
                "frequency": req["when"],
                "acceptance_criteria": req.get("criteria", []),
                "technical_notes": req.get("technical", ""),
                "dependencies": req.get("dependencies", "none"),
                "tradeoffs": req.get("tradeoffs", ""),
            }
            contract["requirements"].append(req_entry)

        return yaml.dump(contract, default_flow_style=False, sort_keys=False)

    def generate_documentation(self) -> str:
        """Generate markdown documentation"""
        doc = f"""# Requirements Document: {self.project_context.get('name', 'Project')}

## Project Overview
- **Type**: {self.project_context.get('type', 'TBD')}
- **Timeline**: {self.project_context.get('timeline', 'TBD')}
- **Description**: {self.project_context.get('description', 'TBD')}

## Stakeholders
{chr(10).join([f'- {s}' for s in self.discovered_items['stakeholders']])}

## Requirements Summary

### By Priority
"""
        # Group by priority
        by_priority = {}
        for req in self.requirements:
            priority = req.get("priority", "Unknown")
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(req)

        for priority in [p.value for p in Priority]:
            if priority in by_priority:
                doc += f"\n#### {priority}\n"
                for req in by_priority[priority]:
                    doc += f"- {req['description'][:100]}... ({req['type']})\n"

        doc += "\n## Detailed Requirements\n\n"

        for i, req in enumerate(self.requirements, 1):
            doc += f"""### R{i:03d}: {req['description'][:50]}...

**Type**: {req['type']} | **Priority**: {req['priority']} | **Risk**: {req['risk']}

**Rationale**: {req['why']}

**User**: {req['who']} | **Usage**: {req['when']}

**Acceptance Criteria**:
{chr(10).join([f'- {c}' for c in req.get('criteria', [])])}

**Technical Notes**: {req.get('technical', 'None')}

**Dependencies**: {req.get('dependencies', 'None')}

**Trade-offs**: {req.get('tradeoffs', 'None')}

---

"""
        return doc

    def save_outputs(self):
        """Save all outputs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create output directory
        output_dir = Path("TASKS/requirements")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save YAML contract
        yaml_file = output_dir / f"REQ_{timestamp}.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write(self.generate_yaml_contract())
        print(f"\n[SUCCESS] YAML contract saved: {yaml_file}")

        # Save documentation
        doc_file = output_dir / f"REQ_{timestamp}_doc.md"
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write(self.generate_documentation())
        print(f"[SUCCESS] Documentation saved: {doc_file}")

        # Save Q&A log
        qa_file = output_dir / f"REQ_{timestamp}_qa.json"
        with open(qa_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "project_context": self.project_context,
                    "qa_log": self.qa_log,
                    "discovered_items": {k: list(v) for k, v in self.discovered_items.items()},
                    "requirements": self.requirements,
                },
                f,
                indent=2,
                default=str,
            )
        print(f"[SUCCESS] Q&A log saved: {qa_file}")

        return yaml_file, doc_file, qa_file

    def print_summary(self):
        """Print final summary"""
        analysis = self.analyze_completeness()

        print("\n" + "=" * 60)
        print("[REQUIREMENTS SUMMARY]")
        print("=" * 60)

        print(f"\nTotal Requirements: {analysis['total_requirements']}")

        print("\nBy Type:")
        for type_name, count in analysis["by_type"].items():
            print(f"  - {type_name}: {count}")

        print("\nBy Priority:")
        for priority, count in analysis["by_priority"].items():
            print(f"  - {priority}: {count}")

        print("\nBy Risk:")
        for risk, count in analysis["by_risk"].items():
            print(f"  - {risk}: {count}")

        print(f"\nCompleteness Score: {analysis['completeness_score']:.0f}%")

        if analysis["coverage_gaps"]:
            print("\n[WARNING] Coverage Gaps:")
            for gap in analysis["coverage_gaps"]:
                print(f"  - {gap}")

        print("\n[NEXT STEPS]")
        print("1. Review generated YAML contract")
        print("2. Execute with TaskExecutor for implementation")
        print("3. Use TestGenerator to create test cases")
        print("4. Track progress in Obsidian")

    def run(self):
        """Main wizard execution"""
        self.print_banner()

        try:
            # Phase 1: Context
            self.gather_project_context()

            # Phase 2: Requirements
            self.discover_requirements()

            if not self.requirements:
                print("\n[WARNING] No requirements gathered. Exiting.")
                return

            # Phase 3: Analysis
            print("\n[PHASE 3] Analysis & Documentation")
            print("=" * 50)

            # Save outputs
            yaml_file, doc_file, qa_file = self.save_outputs()

            # Print summary
            self.print_summary()

            print("\n[SUCCESS] Requirements gathering complete!")

        except KeyboardInterrupt:
            print("\n\n[CANCELLED] Requirements gathering cancelled by user")
            if self.requirements:
                save = input("\nSave partial results? (y/n): ").strip().lower()
                if save == "y":
                    self.save_outputs()
                    print("[SUCCESS] Partial results saved")
        except Exception as e:
            print(f"\n[ERROR] Requirements gathering failed: {e}")
            import traceback

            traceback.print_exc()


def main():
    """Main entry point"""
    wizard = RequirementsWizard()
    wizard.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
