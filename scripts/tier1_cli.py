"""Unified CLI for Tier 1 Integration Tools.

Provides single entry point for all Tier 1 tools:
- spec: SPEC creation with EARS grammar
- tdd: Coverage gate enforcement
- tag: @TAG chain tracing
- status: Feature flag status display
- disable/enable: Emergency controls

Compliance:
- P1: YAML-First (delegates to YAML-based tools)
- P4: SOLID principles (command separation)
- P10: Windows encoding (no emojis, ASCII replacements)

Example:
    $ python scripts/tier1_cli.py spec "Add user auth"
    $ python scripts/tier1_cli.py tdd --threshold 90
    $ python scripts/tier1_cli.py status
    $ python scripts/tier1_cli.py disable spec_builder
"""

import sys
from pathlib import Path
from typing import Optional

import click

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from feature_flags import FeatureFlags


@click.group()
@click.version_option(version="1.0.0", prog_name="tier1_cli")
def cli() -> None:
    """Tier 1 Integration Tools - Unified CLI.

    Provides unified interface for SPEC builder, TDD enforcer, and TAG tracer.
    All tools respect feature flags and emergency disable controls.
    """
    pass


@cli.command()
@click.argument("request", type=str)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["feature", "bugfix", "refactor"], case_sensitive=False),
    default="feature",
    help="SPEC template type (default: feature)",
)
@click.option(
    "--quick",
    "-q",
    is_flag=True,
    help="Quick mode: skip SPEC, generate YAML directly",
)
def spec(request: str, template: str, quick: bool) -> None:
    """Create SPEC and YAML contract from natural language request.

    Args:
        request: Natural language feature description.
        template: SPEC template type (feature/bugfix/refactor).
        quick: Skip SPEC creation, generate YAML directly.

    Example:
        $ python scripts/tier1_cli.py spec "Add user authentication"
        $ python scripts/tier1_cli.py spec "Fix login bug" -t bugfix
        $ python scripts/tier1_cli.py spec "Refactor auth" -t refactor -q
    """
    flags = FeatureFlags()

    # Check if tool is enabled
    if not flags.is_enabled("tier1_integration.tools.spec_builder"):
        click.echo("[ERROR] spec_builder is disabled by feature flag")
        click.echo("Enable with: python scripts/tier1_cli.py enable spec_builder")
        sys.exit(1)

    # Check if quick mode is available
    if quick and not flags.is_enabled("tier1_integration.tools.spec_builder.quick_mode_available"):
        click.echo("[WARN] Quick mode is disabled by feature flag")
        click.echo("Falling back to standard SPEC creation mode")
        quick = False

    click.echo(f"[INFO] Creating SPEC for: {request}")
    click.echo(f"[INFO] Template: {template}")
    click.echo(f"[INFO] Quick mode: {quick}")

    # TODO: Phase 1 implementation - delegating to spec_builder_lite
    click.echo("[NOT_IMPLEMENTED] spec_builder_lite will be implemented in Phase 1 (Week 4-5)")
    click.echo("[INFO] This CLI infrastructure is ready for integration")


@cli.command()
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=None,
    help="Coverage threshold (default: from feature flags)",
)
@click.option(
    "--strict/--no-strict",
    default=None,
    help="Strict mode: block commits on failure (default: from feature flags)",
)
@click.option(
    "--quick",
    "-q",
    is_flag=True,
    help="Quick mode: warning only, no blocking",
)
def tdd(threshold: Optional[float], strict: Optional[bool], quick: bool) -> None:
    """Enforce TDD coverage gate before commits.

    Args:
        threshold: Coverage threshold percentage (0-100).
        strict: Block commits if coverage < threshold.
        quick: Quick mode (warning only, no blocking).

    Example:
        $ python scripts/tier1_cli.py tdd
        $ python scripts/tier1_cli.py tdd --threshold 90
        $ python scripts/tier1_cli.py tdd --strict
        $ python scripts/tier1_cli.py tdd -q
    """
    flags = FeatureFlags()

    # Check if tool is enabled
    if not flags.is_enabled("tier1_integration.tools.tdd_enforcer"):
        click.echo("[ERROR] tdd_enforcer is disabled by feature flag")
        click.echo("Enable with: python scripts/tier1_cli.py enable tdd_enforcer")
        sys.exit(1)

    # Get defaults from feature flags if not provided
    if threshold is None:
        threshold = flags.get_config("tier1_integration.tools.tdd_enforcer.coverage_threshold")
        if threshold is None:
            threshold = 85.0

    if strict is None:
        strict = flags.get_config("tier1_integration.tools.tdd_enforcer.strict_mode")
        if strict is None:
            strict = False

    # Check if quick mode is available
    if quick and not flags.is_enabled("tier1_integration.mitigation.quick_mode.enabled"):
        click.echo("[WARN] Quick mode is disabled by feature flag")
        quick = False

    click.echo(f"[INFO] Coverage threshold: {threshold}%")
    click.echo(f"[INFO] Strict mode: {strict}")
    click.echo(f"[INFO] Quick mode: {quick}")

    # TODO: Phase 1 implementation - delegating to tdd_enforcer_lite
    click.echo("[NOT_IMPLEMENTED] tdd_enforcer_lite will be implemented in Phase 1 (Week 3)")
    click.echo("[INFO] This CLI infrastructure is ready for integration")


@cli.command()
@click.argument("tag_chain", type=str, nargs=-1)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate @TAG chain integrity (default: True)",
)
@click.option(
    "--suggest",
    "-s",
    is_flag=True,
    help="Auto-suggest missing @TAG annotations",
)
def tag(tag_chain: tuple, validate: bool, suggest: bool) -> None:
    """Trace @TAG chains for requirement traceability.

    Args:
        tag_chain: @TAG chain to trace (e.g., @REQ-001 @IMPL-001).
        validate: Validate chain integrity.
        suggest: Auto-suggest missing @TAG annotations.

    Example:
        $ python scripts/tier1_cli.py tag @REQ-001
        $ python scripts/tier1_cli.py tag @REQ-001 @IMPL-001 --validate
        $ python scripts/tier1_cli.py tag --suggest
    """
    flags = FeatureFlags()

    # Check if tool is enabled
    if not flags.is_enabled("tier1_integration.tools.tag_tracer"):
        click.echo("[ERROR] tag_tracer is disabled by feature flag")
        click.echo("Enable with: python scripts/tier1_cli.py enable tag_tracer")
        sys.exit(1)

    # Get defaults from feature flags
    if validate:
        validate = flags.get_config("tier1_integration.tools.tag_tracer.chain_validation")
        if validate is None:
            validate = True

    if suggest:
        suggest = flags.get_config("tier1_integration.tools.tag_tracer.auto_tag_suggestion")
        if suggest is None:
            suggest = False

    if tag_chain:
        click.echo(f"[INFO] Tracing @TAG chain: {' '.join(tag_chain)}")
    else:
        click.echo("[INFO] Scanning project for @TAG annotations")

    click.echo(f"[INFO] Validate chain: {validate}")
    click.echo(f"[INFO] Auto-suggest: {suggest}")

    # TODO: Phase 1 implementation - delegating to tag_tracer_lite
    click.echo("[NOT_IMPLEMENTED] tag_tracer_lite will be implemented in Phase 1 (Week 6-7)")
    click.echo("[INFO] This CLI infrastructure is ready for integration")


@cli.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed configuration",
)
def status(verbose: bool) -> None:
    """Display feature flag status and configuration.

    Args:
        verbose: Show detailed configuration.

    Example:
        $ python scripts/tier1_cli.py status
        $ python scripts/tier1_cli.py status -v
    """
    flags = FeatureFlags()

    click.echo("=== Tier 1 Integration Status ===")
    click.echo("")

    # Overall status
    tier1_enabled = flags.is_enabled("tier1_integration")
    click.echo(f"Tier 1 Integration: {'[ENABLED]' if tier1_enabled else '[DISABLED]'}")

    # Emergency status
    emergency = flags.get_config("tier1_integration.emergency.disable_all_tier1")
    if emergency:
        click.echo("[EMERGENCY] All Tier 1 features are disabled!")
        last_emergency = flags.get_config("tier1_integration.emergency.last_emergency_datetime")
        if last_emergency:
            click.echo(f"Last emergency disable: {last_emergency}")
        click.echo("")

    # Tool status
    click.echo("Tools:")
    tools = ["spec_builder", "tdd_enforcer", "tag_tracer"]
    for tool in tools:
        enabled = flags.is_enabled(f"tier1_integration.tools.{tool}")
        status_str = "[ENABLED]" if enabled else "[DISABLED]"
        click.echo(f"  - {tool}: {status_str}")

    # Verbose details
    if verbose:
        click.echo("")
        click.echo("Configuration Details:")
        for tool in tools:
            click.echo(f"  {tool}:")
            config = flags.get_config(f"tier1_integration.tools.{tool}")
            if config:
                for key, value in config.items():
                    click.echo(f"    {key}: {value}")


@cli.command()
@click.argument(
    "tool",
    type=click.Choice(["spec_builder", "tdd_enforcer", "tag_tracer", "all"], case_sensitive=False),
)
def disable(tool: str) -> None:
    """Disable a Tier 1 tool or all tools.

    Args:
        tool: Tool to disable (spec_builder/tdd_enforcer/tag_tracer/all).

    Example:
        $ python scripts/tier1_cli.py disable spec_builder
        $ python scripts/tier1_cli.py disable all
    """
    flags = FeatureFlags()

    if tool == "all":
        flags.emergency_disable()
        click.echo("[EMERGENCY] All Tier 1 features disabled!")
        click.echo("Re-enable with: python scripts/tier1_cli.py enable all")
    else:
        click.echo(f"[NOT_IMPLEMENTED] Individual tool disable for {tool} requires config update")
        click.echo("Use emergency disable for immediate effect:")
        click.echo("  python scripts/tier1_cli.py disable all")


@cli.command()
@click.argument(
    "tool",
    type=click.Choice(["spec_builder", "tdd_enforcer", "tag_tracer", "all"], case_sensitive=False),
)
def enable(tool: str) -> None:
    """Enable a Tier 1 tool or all tools.

    Args:
        tool: Tool to enable (spec_builder/tdd_enforcer/tag_tracer/all).

    Example:
        $ python scripts/tier1_cli.py enable spec_builder
        $ python scripts/tier1_cli.py enable all
    """
    flags = FeatureFlags()

    if tool == "all":
        flags.emergency_enable()
        click.echo("[RECOVERY] All Tier 1 features re-enabled!")
    else:
        click.echo(f"[NOT_IMPLEMENTED] Individual tool enable for {tool} requires config update")
        click.echo("Use emergency enable for immediate effect:")
        click.echo("  python scripts/tier1_cli.py enable all")


if __name__ == "__main__":
    cli()
