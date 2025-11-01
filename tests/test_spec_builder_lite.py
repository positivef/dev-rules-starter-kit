"""Tests for SPEC Builder Lite.

Test Coverage:
- Requirement ID generation
- Natural language parsing
- Template loading and filling
- YAML contract generation
- Contract validation
- Feature flag integration

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import sys
from pathlib import Path

import pytest
import yaml

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from spec_builder_lite import SpecBuilderLite


@pytest.fixture
def temp_dirs(tmp_path: Path):
    """Create temporary directories for tests.

    Args:
        tmp_path: pytest temporary directory fixture.

    Returns:
        Tuple of (contracts_dir, templates_dir).
    """
    contracts_dir = tmp_path / "contracts"
    templates_dir = tmp_path / "templates/ears"
    contracts_dir.mkdir(parents=True)
    templates_dir.mkdir(parents=True)
    return contracts_dir, templates_dir


@pytest.fixture
def sample_template(temp_dirs):
    """Create sample EARS template.

    Args:
        temp_dirs: Fixture providing temporary directories.

    Returns:
        Path to template file.
    """
    _, templates_dir = temp_dirs
    template_path = templates_dir / "feature.yaml"
    template_content = """requirement:
  id: "{{req_id}}"
  title: "{{title}}"
  type: feature

ears:
  when: "{{trigger_event}}"
  if: "{{precondition}}"
  then: "System SHALL {{system_response}}"
  where: "{{constraints}}"

tags:
  - "{{req_id}}"
"""
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(template_content)
    return template_path


class TestRequirementIdGeneration:
    """Test requirement ID generation."""

    def test_generate_req_id_from_title(self, temp_dirs):
        """Test ID generation from title."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        req_id = builder.generate_req_id("Add user authentication")
        assert req_id.startswith("REQ-")
        assert req_id.endswith("-001")

    def test_generate_req_id_incremental(self, temp_dirs):
        """Test ID increments for same prefix."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        # Create first contract
        (contracts_dir / "REQ-AUTH-001.yaml").touch()

        # Second contract should be -002
        req_id = builder.generate_req_id("Add authentication")
        assert req_id == "REQ-AUTH-002"

    def test_generate_req_id_different_prefixes(self, temp_dirs):
        """Test IDs for different domains."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        auth_id = builder.generate_req_id("Add authentication")
        login_id = builder.generate_req_id("Fix login timeout")

        assert auth_id.startswith("REQ-AUTH")
        assert login_id.startswith("REQ-LOGI")


class TestNaturalLanguageParsing:
    """Test natural language request parsing."""

    def test_parse_feature_request(self, temp_dirs):
        """Test parsing feature request."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(template_type="feature", contracts_dir=contracts_dir, templates_dir=templates_dir)

        result = builder.parse_request("Add user authentication")

        assert "trigger_event" in result
        assert "precondition" in result
        assert "system_response" in result
        assert "constraints" in result
        assert "authentication" in result["trigger_event"].lower()

    def test_parse_bugfix_request(self, temp_dirs):
        """Test parsing bugfix request."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(template_type="bugfix", contracts_dir=contracts_dir, templates_dir=templates_dir)

        result = builder.parse_request("Fix login timeout")

        assert "trigger_event" in result
        assert "error_condition" in result
        assert "fix_behavior" in result
        assert "timeout" in result["trigger_event"].lower()

    def test_parse_refactor_request(self, temp_dirs):
        """Test parsing refactor request."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(template_type="refactor", contracts_dir=contracts_dir, templates_dir=templates_dir)

        result = builder.parse_request("Refactor authentication module")

        assert "trigger_event" in result
        assert "quality_condition" in result
        assert "refactoring_action" in result
        assert "authentication" in result["trigger_event"].lower()


class TestTemplateOperations:
    """Test template loading and filling."""

    def test_load_template_success(self, temp_dirs, sample_template):
        """Test successful template loading."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        template = builder.load_template()
        assert "{{req_id}}" in template
        assert "{{title}}" in template

    def test_load_template_not_found(self, temp_dirs):
        """Test error when template not found."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(template_type="nonexistent", contracts_dir=contracts_dir, templates_dir=templates_dir)

        with pytest.raises(FileNotFoundError):
            builder.load_template()

    def test_fill_template(self, temp_dirs):
        """Test template placeholder filling."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        template = "ID: {{req_id}}, Title: {{title}}"
        values = {"req_id": "REQ-001", "title": "Test"}

        filled = builder.fill_template(template, values)
        assert filled == "ID: REQ-001, Title: Test"

    def test_fill_template_with_date(self, temp_dirs):
        """Test template fills current date."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        template = "Date: {{date}}"
        filled = builder.fill_template(template, {})

        assert "Date: " in filled
        assert filled != "Date: {{date}}"


class TestSpecGeneration:
    """Test YAML contract generation."""

    def test_generate_spec_creates_file(self, temp_dirs, sample_template):
        """Test SPEC generation creates YAML file."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        output_path = builder.generate_spec("Add user authentication")

        assert output_path.exists()
        assert output_path.suffix == ".yaml"

    def test_generate_spec_valid_yaml(self, temp_dirs, sample_template):
        """Test generated SPEC is valid YAML."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        output_path = builder.generate_spec("Add user authentication")

        with open(output_path, encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        assert contract is not None
        assert "requirement" in contract
        assert "ears" in contract

    def test_generate_spec_contains_request(self, temp_dirs, sample_template):
        """Test generated SPEC contains request title."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        output_path = builder.generate_spec("Add user authentication")

        with open(output_path, encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        assert contract["requirement"]["title"] == "Add user authentication"

    def test_generate_spec_quick_mode(self, temp_dirs, sample_template):
        """Test quick mode generation."""
        contracts_dir, templates_dir = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir, templates_dir=templates_dir)

        output_path = builder.generate_spec("Add user authentication", quick=True)

        assert output_path.exists()


class TestContractValidation:
    """Test YAML contract validation."""

    def test_validate_valid_contract(self, temp_dirs):
        """Test validation of valid contract."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create valid contract
        contract_path = contracts_dir / "REQ-001.yaml"
        valid_contract = {
            "requirement": {"id": "REQ-001", "title": "Test"},
            "ears": {"when": "event", "then": "action"},
            "tags": ["REQ-001"],
        }
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(valid_contract, f)

        assert builder.validate_contract(contract_path) is True

    def test_validate_missing_requirement(self, temp_dirs):
        """Test validation fails for missing requirement section."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create invalid contract (missing requirement)
        contract_path = contracts_dir / "REQ-001.yaml"
        invalid_contract = {"ears": {"when": "event", "then": "action"}, "tags": ["REQ-001"]}
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(invalid_contract, f)

        assert builder.validate_contract(contract_path) is False

    def test_validate_missing_ears(self, temp_dirs):
        """Test validation fails for missing EARS section."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create invalid contract (missing ears)
        contract_path = contracts_dir / "REQ-001.yaml"
        invalid_contract = {"requirement": {"id": "REQ-001"}, "tags": ["REQ-001"]}
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(invalid_contract, f)

        assert builder.validate_contract(contract_path) is False

    def test_validate_invalid_yaml(self, temp_dirs):
        """Test validation fails for invalid YAML."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create invalid YAML
        contract_path = contracts_dir / "REQ-001.yaml"
        with open(contract_path, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content: [")

        assert builder.validate_contract(contract_path) is False

    def test_validate_missing_ears_when_field(self, temp_dirs):
        """Test validation fails when EARS 'when' field is missing."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create contract missing 'when' in EARS
        contract_path = contracts_dir / "REQ-001.yaml"
        invalid_contract = {
            "requirement": {"id": "REQ-001"},
            "ears": {"then": "System SHALL do something"},  # Missing 'when'
            "tags": ["REQ-001"],
        }
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(invalid_contract, f)

        assert builder.validate_contract(contract_path) is False

    def test_validate_empty_ears_then_field(self, temp_dirs):
        """Test validation fails when EARS 'then' field is empty."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create contract with empty 'then' in EARS
        contract_path = contracts_dir / "REQ-001.yaml"
        invalid_contract = {
            "requirement": {"id": "REQ-001"},
            "ears": {"when": "trigger", "then": ""},  # Empty 'then'
            "tags": ["REQ-001"],
        }
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(invalid_contract, f)

        assert builder.validate_contract(contract_path) is False

    def test_validate_general_exception(self, temp_dirs, monkeypatch):
        """Test validation handles general exceptions."""
        contracts_dir, _ = temp_dirs
        builder = SpecBuilderLite(contracts_dir=contracts_dir)

        # Create valid contract
        contract_path = contracts_dir / "REQ-001.yaml"
        valid_contract = {
            "requirement": {"id": "REQ-001"},
            "ears": {"when": "trigger", "then": "action"},
            "tags": ["REQ-001"],
        }
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(valid_contract, f)

        # Mock yaml.safe_load to raise an exception
        def mock_load_error(*args, **kwargs):
            raise RuntimeError("Mock validation error")

        monkeypatch.setattr("yaml.safe_load", mock_load_error)
        assert builder.validate_contract(contract_path) is False


class TestMainFunction:
    """Test CLI main function."""

    def test_main_success_feature(self, monkeypatch, temp_dirs, sample_template):
        """Test successful main execution with feature template."""
        contracts_dir, templates_dir = temp_dirs

        # Create bugfix and refactor templates too
        for template_type in ["bugfix", "refactor"]:
            template_path = templates_dir / f"{template_type}.yaml"
            with open(template_path, "w", encoding="utf-8") as f:
                f.write("""requirement:
  id: "{{req_id}}"
  title: "{{title}}"

ears:
  when: "{{trigger_event}}"
  then: "System SHALL {{system_response}}"

tags:
  - "{{req_id}}"
""")

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Add feature"])

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_success_bugfix(self, monkeypatch, temp_dirs):
        """Test successful main execution with bugfix template."""
        contracts_dir, templates_dir = temp_dirs

        # Create bugfix template
        template_path = templates_dir / "bugfix.yaml"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""requirement:
  id: "{{req_id}}"
  title: "{{title}}"
  type: bugfix

ears:
  when: "{{trigger_event}}"
  then: "System SHALL {{fix_behavior}}"

tags:
  - "{{req_id}}"
""")

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Fix bug", "--template", "bugfix"])

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_success_refactor(self, monkeypatch, temp_dirs):
        """Test successful main execution with refactor template."""
        contracts_dir, templates_dir = temp_dirs

        # Create refactor template
        template_path = templates_dir / "refactor.yaml"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""requirement:
  id: "{{req_id}}"
  title: "{{title}}"
  type: refactor

ears:
  when: "{{trigger_event}}"
  then: "System SHALL {{refactoring_action}}"

tags:
  - "{{req_id}}"
""")

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Refactor code", "--template", "refactor"])

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_exception(self, monkeypatch, temp_dirs):
        """Test main function when exception occurs."""
        contracts_dir, templates_dir = temp_dirs

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Add feature"])

        def mock_generate_spec(self, request, quick=False):
            raise Exception("Test error")

        monkeypatch.setattr(SpecBuilderLite, "generate_spec", mock_generate_spec)

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_quick_mode_success(self, monkeypatch, temp_dirs, sample_template):
        """Test main function with quick mode enabled."""
        contracts_dir, templates_dir = temp_dirs

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Add feature", "--quick"])

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 0

    def test_main_with_feature_flag_disabled(self, monkeypatch, temp_dirs):
        """Test main function when spec_builder feature flag is disabled."""
        contracts_dir, templates_dir = temp_dirs

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Add feature"])

        # Mock FeatureFlags to return False for spec_builder
        class MockFlags:
            def is_enabled(self, key):
                return False

            def get_config(self, key):
                return None

        monkeypatch.setattr("spec_builder_lite.FeatureFlags", MockFlags)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 1

    def test_main_with_quick_mode_disabled(self, monkeypatch, temp_dirs, sample_template):
        """Test main function when quick mode is disabled by feature flag."""
        contracts_dir, templates_dir = temp_dirs

        monkeypatch.setattr("sys.argv", ["spec_builder_lite.py", "Add feature", "--quick"])

        # Mock FeatureFlags to disable quick mode
        class MockFlags:
            def is_enabled(self, key):
                if key == "tier1_integration.tools.spec_builder":
                    return True
                if key == "tier1_integration.tools.spec_builder.quick_mode_available":
                    return False
                return True

            def get_config(self, key):
                return None

        monkeypatch.setattr("spec_builder_lite.FeatureFlags", MockFlags)

        original_init = SpecBuilderLite.__init__

        def mock_init(self, template_type="feature", contracts_dir=None, templates_dir=None):
            original_init(self, template_type, temp_dirs[0], temp_dirs[1])

        monkeypatch.setattr(SpecBuilderLite, "__init__", mock_init)

        from spec_builder_lite import main

        exit_code = main()
        assert exit_code == 0  # Should succeed but fall back to non-quick mode


class TestGenerateSpecBugfixTemplate:
    """Test generate_spec with bugfix template."""

    def test_generate_bugfix_spec_full(self, temp_dirs):
        """Test generating bugfix spec with full template fields."""
        contracts_dir, templates_dir = temp_dirs

        # Copy actual bugfix template
        import shutil

        actual_template = Path(__file__).parent.parent / "templates/ears/bugfix.yaml"
        shutil.copy(actual_template, templates_dir / "bugfix.yaml")

        builder = SpecBuilderLite(template_type="bugfix", contracts_dir=contracts_dir, templates_dir=templates_dir)
        output_path = builder.generate_spec("Fix login timeout")

        assert output_path.exists()

        with open(output_path, encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        assert contract["requirement"]["type"] == "bugfix"
        assert "problem" in contract
        assert "severity" in contract["requirement"]
        assert contract["requirement"]["severity"] == "medium"
        assert "root_cause" in contract
        assert "fix_validation" in contract


class TestGenerateSpecRefactorTemplate:
    """Test generate_spec with refactor template."""

    def test_generate_refactor_spec(self, temp_dirs):
        """Test generating refactor spec with full template fields."""
        contracts_dir, templates_dir = temp_dirs

        # Copy actual refactor template
        import shutil

        actual_template = Path(__file__).parent.parent / "templates/ears/refactor.yaml"
        shutil.copy(actual_template, templates_dir / "refactor.yaml")

        builder = SpecBuilderLite(template_type="refactor", contracts_dir=contracts_dir, templates_dir=templates_dir)
        output_path = builder.generate_spec("Refactor auth module")

        # Verify contract was created
        assert output_path.exists()

        # Load and validate refactor-specific fields
        with open(output_path, encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        assert contract["requirement"]["type"] == "refactor"
        assert "motivation" in contract
        assert "current_issues" in contract["motivation"]
        assert "High complexity" in contract["motivation"]["current_issues"]
        assert "success_criteria" in contract
        assert "functional" in contract["success_criteria"]
        assert "quality_metrics" in contract["success_criteria"]
        assert "rollback_plan" in contract
