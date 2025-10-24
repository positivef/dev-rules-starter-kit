"""SPEC Builder Lite - YAML Contract Generator with EARS Grammar.

Generates YAML-based requirement contracts from natural language requests.
Uses EARS (Easy Approach to Requirements Syntax) grammar for clarity.

Compliance:
- P1: YAML-First (generates YAML contracts)
- P2: Evidence-based (contracts as evidence)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

EARS Grammar:
- WHEN <trigger>: Event that initiates requirement
- IF <condition>: Precondition for requirement
- THEN System SHALL <response>: Mandatory system behavior
- WHERE <constraints>: Environmental or quality constraints

Example:
    $ python scripts/spec_builder_lite.py "Add user authentication"
    $ python scripts/spec_builder_lite.py "Fix login timeout" -t bugfix
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import yaml

try:
    from feature_flags import FeatureFlags
    from security_utils import SecurePathValidator, SecureFileLock, SecureConfig
except ImportError:
    from scripts.feature_flags import FeatureFlags
    from scripts.security_utils import SecurePathValidator, SecureFileLock


class SpecBuilderLite:
    """Lightweight SPEC generator with EARS grammar.

    Attributes:
        template_type: Type of requirement (feature/bugfix/refactor).
        contracts_dir: Directory for generated YAML contracts.
        templates_dir: Directory for EARS templates.
    """

    def __init__(
        self,
        template_type: str = "feature",
        contracts_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
    ) -> None:
        """Initialize SPEC builder.

        Args:
            template_type: Template to use (feature/bugfix/refactor).
            contracts_dir: Output directory for contracts.
            templates_dir: Directory containing EARS templates.
        """
        self.template_type = template_type
        self.contracts_dir = contracts_dir or Path("contracts")
        self.templates_dir = templates_dir or Path("templates/ears")
        self.contracts_dir.mkdir(parents=True, exist_ok=True)

    def generate_req_id(self, title: str) -> str:
        """Generate requirement ID from title.

        Uses file locking to prevent race conditions in concurrent environments.

        Args:
            title: Requirement title.

        Returns:
            Requirement ID (e.g., REQ-AUTH-001).

        Example:
            >>> builder.generate_req_id("Add user authentication")
            'REQ-AUTH-001'
        """
        # Extract key words from title
        words = re.findall(r"\b[A-Z][A-Z]+\b|\b[a-z]+\b", title)
        # Take first meaningful word
        key_word = next((w for w in words if w.lower() not in ["add", "fix", "update", "refactor"]), "FEATURE")
        key_word = key_word.upper()[:4]

        # Use secure file lock to prevent race conditions
        lock_file = self.contracts_dir / ".req_id.lock"

        with SecureFileLock(lock_file):
            # Count existing contracts with same prefix (while holding lock)
            prefix = f"REQ-{key_word}"
            existing = list(self.contracts_dir.glob(f"{prefix}-*.yaml"))
            next_num = len(existing) + 1

            return f"{prefix}-{next_num:03d}"

    def parse_request(self, request: str) -> Dict[str, str]:
        """Parse natural language request into EARS components.

        Args:
            request: Natural language requirement description.

        Returns:
            Dict with EARS components (trigger, condition, response, constraints).

        Example:
            >>> builder.parse_request("Add JWT authentication for API endpoints")
            {
                'trigger_event': 'User submits credentials',
                'precondition': 'Credentials are valid',
                'system_response': 'generate JWT token',
                'constraints': 'Token expires in 24 hours'
            }
        """
        # Simple heuristic parsing (in production, use NLP or LLM)
        request_lower = request.lower()

        # Extract action verb
        action_match = re.match(r"(add|create|implement|build)\s+(.+)", request_lower)
        if action_match:
            core_request = action_match.group(2)
        else:
            core_request = request_lower

        # Generate EARS components based on template type
        if self.template_type == "feature":
            return {
                "trigger_event": f"User requests {core_request}",
                "precondition": "User is authenticated",
                "system_response": f"provide {core_request}",
                "constraints": "Response time < 200ms",
            }
        elif self.template_type == "bugfix":
            return {
                "trigger_event": f"User encounters {core_request}",
                "error_condition": "System in error state",
                "fix_behavior": f"handle {core_request} correctly",
                "constraints": "No data loss or corruption",
            }
        else:  # refactor
            return {
                "trigger_event": f"Code quality issues in {core_request}",
                "quality_condition": "Maintainability below threshold",
                "refactoring_action": f"improve {core_request} structure",
                "constraints": "No functional changes, all tests pass",
            }

    def load_template(self) -> str:
        """Load EARS template for requirement type.

        Returns:
            Template content as string.

        Raises:
            FileNotFoundError: If template file not found.
            ValueError: If template type contains invalid characters.
        """
        # Use secure path validation
        validator = SecurePathValidator()

        # Sanitize template_type
        safe_type = validator.sanitize_filename(self.template_type)
        if safe_type != self.template_type:
            raise ValueError(f"Invalid template type: {self.template_type}")

        template_path = self.templates_dir / f"{safe_type}.yaml"

        # Secure path validation (prevents symlink attacks)
        try:
            validator.validate_path(self.templates_dir, template_path)
        except Exception as e:
            raise ValueError(f"Path traversal detected: {self.template_type}") from e

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, encoding="utf-8") as f:
            return f.read()

    def fill_template(self, template: str, values: Dict[str, str]) -> str:
        """Fill template placeholders with values.

        Args:
            template: Template string with {{placeholder}} syntax.
            values: Dict mapping placeholder names to values.

        Returns:
            Filled template string.
        """
        # Replace placeholders
        result = template
        for key, value in values.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value))

        # Fill common placeholders
        result = result.replace("{{date}}", datetime.now().isoformat())

        return result

    def generate_spec(self, request: str, quick: bool = False) -> Path:
        """Generate YAML contract from natural language request.

        Args:
            request: Natural language requirement description.
            quick: Skip SPEC, generate minimal YAML directly.

        Returns:
            Path to generated YAML contract.

        Example:
            >>> builder.generate_spec("Add user authentication")
            PosixPath('contracts/REQ-AUTH-001.yaml')
        """
        # Generate requirement ID
        req_id = self.generate_req_id(request)

        # Parse request into EARS components
        ears_components = self.parse_request(request)

        # Load template
        template = self.load_template()

        # Prepare template values
        values = {
            "req_id": req_id,
            "title": request,
            **ears_components,
        }

        # Add template-specific defaults
        if self.template_type == "feature":
            values.update(
                {
                    "criterion_1": "Functionality works as specified",
                    "criterion_2": "All tests pass",
                    "criterion_3": "Code review approved",
                    "stakeholder": "Product Team",
                    "business_value": "Enable user authentication",
                    "effort_hours": "8",
                    "domain": "authentication",
                }
            )
        elif self.template_type == "bugfix":
            values.update(
                {
                    "severity": "medium",
                    "problem_description": request,
                    "step_1": "Reproduce the issue",
                    "step_2": "Identify root cause",
                    "step_3": "Verify fix",
                    "expected": "System behaves correctly",
                    "actual": "System has incorrect behavior",
                    "root_cause": "To be analyzed",
                    "component_1": "Core component",
                    "validation_1": "Unit tests pass",
                    "validation_2": "Integration tests pass",
                    "test_case_1": "Regression test added",
                    "monitoring_1": "Error rate tracking",
                    "reporter": "Development Team",
                    "report_date": datetime.now().isoformat(),
                    "user_count": "TBD",
                    "component": "core",
                }
            )
        else:  # refactor
            values.update(
                {
                    "issue_1": "High complexity",
                    "issue_2": "Code duplication",
                    "debt_description": "Technical debt accumulation",
                    "goal_1": "Reduce complexity",
                    "goal_2": "Improve maintainability",
                    "file_1": "TBD",
                    "component_1": "Core module",
                    "criterion_1": "Code coverage maintained",
                    "target_maintainability": "A grade",
                    "target_complexity": "< 10 cyclomatic",
                    "mitigation_1": "Incremental changes with reviews",
                    "rollback_step_1": "Revert to previous version",
                    "commit_hash": "TBD",
                    "initiator": "Development Team",
                    "justification": "Improve long-term maintainability",
                    "component": "core",
                }
            )

        # Fill template
        filled = self.fill_template(template, values)

        # Save to contracts directory
        output_path = self.contracts_dir / f"{req_id}.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(filled)

        return output_path

    def validate_contract(self, contract_path: Path) -> bool:
        """Validate YAML contract structure.

        Args:
            contract_path: Path to YAML contract file.

        Returns:
            True if contract is valid, False otherwise.
        """
        try:
            with open(contract_path, encoding="utf-8") as f:
                contract = yaml.safe_load(f)
        except (IOError, PermissionError) as e:
            print(f"[ERROR] Cannot read contract file: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"[ERROR] Invalid file encoding: {e}")
            return False
        except yaml.YAMLError as e:
            print(f"[ERROR] Invalid YAML: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            return False

        try:
            # Check required sections
            required = ["requirement", "ears", "tags"]
            for section in required:
                if section not in contract:
                    print(f"[ERROR] Missing required section: {section}")
                    return False

            # Check EARS grammar
            ears = contract["ears"]
            ears_required = ["when", "then"]
            for field in ears_required:
                if field not in ears or not ears[field]:
                    print(f"[ERROR] Missing EARS field: {field}")
                    return False

            return True

        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            return False


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="SPEC Builder Lite - YAML Contract Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/spec_builder_lite.py "Add user authentication"
  python scripts/spec_builder_lite.py "Fix login timeout" -t bugfix
  python scripts/spec_builder_lite.py "Refactor auth module" -t refactor
  python scripts/spec_builder_lite.py "Add JWT auth" -q
        """,
    )

    parser.add_argument("request", type=str, help="Natural language requirement description")
    parser.add_argument(
        "--template",
        "-t",
        type=str,
        choices=["feature", "bugfix", "refactor"],
        default="feature",
        help="SPEC template type (default: feature)",
    )
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode: skip validation, generate minimal YAML")

    args = parser.parse_args()

    # Check feature flags
    flags = FeatureFlags()
    if not flags.is_enabled("tier1_integration.tools.spec_builder"):
        print("[ERROR] spec_builder is disabled by feature flag")
        print("Enable with: python scripts/tier1_cli.py enable spec_builder")
        return 1

    # Check quick mode availability
    if args.quick and not flags.is_enabled("tier1_integration.tools.spec_builder.quick_mode_available"):
        print("[WARN] Quick mode is disabled by feature flag")
        print("Falling back to standard SPEC creation mode")
        args.quick = False

    print("[INFO] SPEC Builder Lite - YAML Contract Generator")
    print(f"[INFO] Request: {args.request}")
    print(f"[INFO] Template: {args.template}")
    print(f"[INFO] Quick mode: {args.quick}")
    print("")

    try:
        builder = SpecBuilderLite(template_type=args.template)

        # Generate SPEC
        output_path = builder.generate_spec(args.request, quick=args.quick)
        print(f"[OK] Contract generated: {output_path}")

        # Validate (unless quick mode)
        if not args.quick:
            valid = builder.validate_contract(output_path)
            if valid:
                print("[OK] Contract validation passed")
            else:
                print("[ERROR] Contract validation failed")
                return 1

        print("")
        print("[INFO] Next steps:")
        print(f"  1. Review contract: cat {output_path}")
        print(f"  2. Implement: [Write code with @TAG {builder.generate_req_id(args.request)}]")
        print(f"  3. Verify: python scripts/tier1_cli.py tag {builder.generate_req_id(args.request)}")

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to generate SPEC: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
