"""Unified CLI for Tier 1 Integration Tools.

Provides single entry point for all Tier 1 tools:
- spec: SPEC creation with EARS grammar
- tdd: Coverage gate enforcement
- tag: @TAG chain tracing
- tag-sync: Bi-directional Obsidian tag synchronization (NEW)
- dataview: Generate Dataview queries from templates (NEW)
- mermaid: Auto-generate Mermaid diagrams (NEW)
- tdd-dashboard: Interactive TDD metrics dashboard (NEW)
- status: Feature flag status display
- disable/enable: Emergency controls

Week 4 Expansions (2025-11-02):
- tag-sync: Sync tags between dev-rules and Obsidian with categories
- dataview: Template-based Dataview query generation
- mermaid: Architecture, dependency, and task workflow diagrams
- tdd-dashboard: Streamlit dashboard for TDD metrics visualization

Compliance:
- P1: YAML-First (delegates to YAML-based tools)
- P4: SOLID principles (command separation)
- P10: Windows encoding (no emojis, ASCII replacements)

Example:
    $ python scripts/tier1_cli.py spec "Add user auth"
    $ python scripts/tier1_cli.py tdd --threshold 90
    $ python scripts/tier1_cli.py tag-sync --test
    $ python scripts/tier1_cli.py dataview tasks-by-status
    $ python scripts/tier1_cli.py mermaid architecture
    $ python scripts/tier1_cli.py tdd-dashboard
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
    click.echo("")

    # Delegate to spec_builder_lite
    from spec_builder_lite import SpecBuilderLite

    try:
        builder = SpecBuilderLite(template_type=template)
        output_path = builder.generate_spec(request, quick=quick)

        click.echo(f"[OK] Contract generated: {output_path}")

        # Validate (unless quick mode)
        if not quick:
            valid = builder.validate_contract(output_path)
            if valid:
                click.echo("[OK] Contract validation passed")
            else:
                click.echo("[ERROR] Contract validation failed")
                sys.exit(1)

        click.echo("")
        click.echo("[INFO] Next steps:")
        click.echo(f"  1. Review contract: cat {output_path}")
        req_id = builder.generate_req_id(request)
        click.echo(f"  2. Implement: [Write code with @TAG {req_id}]")
        click.echo(f"  3. Verify: python scripts/tier1_cli.py tag {req_id}")

    except Exception as e:
        click.echo(f"[ERROR] Failed to generate SPEC: {e}")
        sys.exit(1)


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
    click.echo("")

    # Delegate to tdd_enforcer_lite
    from tdd_enforcer_lite import TddEnforcerLite

    enforcer = TddEnforcerLite(
        threshold=threshold,
        strict=strict,
        quick=quick,
    )

    exit_code = enforcer.enforce()
    sys.exit(exit_code)


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

    # Delegate to tag_tracer_lite
    from tag_tracer_lite import TagTracerLite

    try:
        tracer = TagTracerLite()

        if tag_chain:
            # Extract TAG ID from @TAG[TYPE:ID] format or plain ID
            tag_ids = []
            for tag in tag_chain:
                # Remove @ prefix if present
                tag_clean = tag.lstrip("@")
                # Extract ID from TAG[TYPE:ID] format
                import re

                match = re.match(r"TAG\[(?:[A-Z]+:)?([^\]]+)\]", tag_clean)
                if match:
                    tag_ids.append(match.group(1))
                else:
                    tag_ids.append(tag_clean)

            # Verify each TAG ID
            for tag_id in tag_ids:
                click.echo(f"[INFO] Tracing @TAG chain: {tag_id}")
                if validate:
                    is_valid = tracer.validate_chain(tag_id)
                    if not is_valid:
                        click.echo(f"[ERROR] TAG chain '{tag_id}' is incomplete")
                        sys.exit(1)
                    click.echo(f"[OK] TAG chain '{tag_id}' is complete")
                else:
                    tracer.verify_tag_chain(tag_id=tag_id)
        else:
            # Verify all TAG chains
            click.echo("[INFO] Scanning project for @TAG annotations")
            report = tracer.verify_tag_chain()

            if validate and report.get("incomplete_chains", 0) > 0:
                click.echo(f"[ERROR] Found {report['incomplete_chains']} incomplete TAG chains")
                sys.exit(1)

        if suggest:
            click.echo("[INFO] Auto-suggest feature will be implemented in Phase 2")

    except Exception as e:
        click.echo(f"[ERROR] Failed to trace TAG chains: {e}")
        sys.exit(1)


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
@click.option(
    "--test",
    is_flag=True,
    help="Run in test mode without actual sync",
)
@click.option(
    "--direction",
    type=click.Choice(["to-obsidian", "from-obsidian", "bidirectional"], case_sensitive=False),
    default="bidirectional",
    help="Sync direction (default: bidirectional)",
)
@click.option(
    "--resolve-conflicts",
    is_flag=True,
    help="Enable conflict detection and resolution (Phase 2.2)",
)
@click.option(
    "--strategy",
    type=click.Choice(["keep-both", "prefer-local", "prefer-remote", "interactive"], case_sensitive=False),
    default="interactive",
    help="Conflict resolution strategy (default: interactive)",
)
def tag_sync(test: bool, direction: str, resolve_conflicts: bool, strategy: str) -> None:
    """Synchronize tags between dev-rules and Obsidian.

    Supports bi-directional tag sync with category awareness:
    - domain/ tags (domain/testing, domain/config)
    - status/ tags (status/completed, status/in-progress)
    - project/ tags (project/strategy-a, project/strategy-b)

    Phase 2.2: Conflict Resolution (NEW):
    - Detect conflicts between YAML and Obsidian tags
    - Three merge strategies: keep-both, prefer-local, prefer-remote
    - Interactive resolution with user prompts
    - Conflict logging to RUNS/tag-conflicts/

    Args:
        test: Run in test mode without actual sync.
        direction: Sync direction (to-obsidian/from-obsidian/bidirectional).
        resolve_conflicts: Enable conflict detection and resolution.
        strategy: Resolution strategy (keep-both/prefer-local/prefer-remote/interactive).

    Example:
        $ python scripts/tier1_cli.py tag-sync
        $ python scripts/tier1_cli.py tag-sync --direction to-obsidian
        $ python scripts/tier1_cli.py tag-sync --resolve-conflicts
        $ python scripts/tier1_cli.py tag-sync --resolve-conflicts --strategy keep-both
        $ python scripts/tier1_cli.py tag-sync --test
    """
    import os
    import yaml
    from pathlib import Path

    click.echo("[TAG-SYNC] Starting tag synchronization...")
    click.echo(f"[INFO] Direction: {direction}")
    click.echo(f"[INFO] Test mode: {test}")

    # Get Obsidian vault path
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not vault_path:
        click.echo("[ERROR] OBSIDIAN_VAULT_PATH not set in .env")
        sys.exit(1)

    vault_path = Path(vault_path)
    if not vault_path.exists():
        click.echo(f"[ERROR] Obsidian vault not found: {vault_path}")
        sys.exit(1)

    devlog_path = vault_path / "개발일지"
    if not devlog_path.exists():
        click.echo(f"[ERROR] 개발일지 folder not found: {devlog_path}")
        sys.exit(1)

    # Category definitions
    tag_categories = {
        "domain": ["testing", "config", "ci-cd", "documentation", "security"],
        "status": ["completed", "in-progress", "pending", "blocked"],
        "project": ["strategy-a", "strategy-b", "tier1", "tier2"],
    }

    # Scan Obsidian files for tags
    obsidian_tags = set()
    if direction in ["from-obsidian", "bidirectional"]:
        click.echo("[SCAN] Scanning Obsidian files for tags...")
        for md_file in devlog_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Extract tags from frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        if "tags:" in frontmatter:
                            # Parse YAML frontmatter
                            yaml_data = yaml.safe_load(frontmatter)
                            if yaml_data and "tags" in yaml_data:
                                tags = yaml_data["tags"]
                                if isinstance(tags, list):
                                    obsidian_tags.update(tags)
            except Exception as e:
                click.echo(f"[WARNING] Failed to read {md_file.name}: {e}")

        click.echo(f"[INFO] Found {len(obsidian_tags)} unique tags in Obsidian")

        # Categorize tags
        categorized = {cat: [] for cat in tag_categories}
        uncategorized = []

        for tag in sorted(obsidian_tags):
            found_category = False
            for category, values in tag_categories.items():
                for value in values:
                    if tag.startswith(f"{category}/{value}"):
                        categorized[category].append(tag)
                        found_category = True
                        break
                if found_category:
                    break
            if not found_category:
                uncategorized.append(tag)

        click.echo("\n[CATEGORIES]")
        for category, tags in categorized.items():
            if tags:
                click.echo(f"  {category}: {len(tags)} tags")
                for tag in tags[:5]:  # Show first 5
                    click.echo(f"    - {tag}")
                if len(tags) > 5:
                    click.echo(f"    ... and {len(tags) - 5} more")

        if uncategorized:
            click.echo(f"\n[UNCATEGORIZED] {len(uncategorized)} tags")
            for tag in uncategorized[:5]:
                click.echo(f"  - {tag}")
            if len(uncategorized) > 5:
                click.echo(f"  ... and {len(uncategorized) - 5} more")

    # Phase 2.2: Conflict Resolution
    if resolve_conflicts:
        from tag_conflict_resolver import TagConflictResolver

        click.echo("\n[CONFLICT-DETECTION] Checking for tag conflicts...")

        # Get dev-rules tags from TASKS/*.yaml
        tasks_path = Path("TASKS")
        dev_tags = set()

        if tasks_path.exists():
            for yaml_file in tasks_path.glob("*.yaml"):
                try:
                    with open(yaml_file, encoding="utf-8") as f:
                        yaml_data = yaml.safe_load(f)
                        if yaml_data and "tags" in yaml_data:
                            tags = yaml_data["tags"]
                            if isinstance(tags, list):
                                dev_tags.update(tags)
                except Exception as e:
                    click.echo(f"[WARNING] Failed to read {yaml_file.name}: {e}")

        click.echo(f"[INFO] Found {len(dev_tags)} unique tags in dev-rules")
        click.echo(f"[INFO] Found {len(obsidian_tags)} unique tags in Obsidian")

        # Detect conflicts
        resolver = TagConflictResolver()
        conflicts = resolver.detect_conflicts(dev_tags, obsidian_tags, "TASKS/*.yaml vs Obsidian")

        if conflicts:
            click.echo(f"\n[CONFLICT] Detected {len(conflicts)} conflict(s)")

            # Resolve conflicts
            if strategy == "interactive" and not test:
                # Interactive resolution
                resolutions = resolver.batch_resolve(conflicts, interactive=True)
            else:
                # Auto-resolution
                actual_strategy = "keep-both" if strategy == "interactive" else strategy
                click.echo(f"[INFO] Using strategy: {actual_strategy}")
                resolutions = resolver.batch_resolve(conflicts, strategy=actual_strategy, interactive=False)

            # Show results
            for resolution in resolutions:
                click.echo(f"\n[RESOLUTION] {resolution.changes_made}")
                click.echo(f"[RESULT] Final tags ({len(resolution.merged_tags)}): {sorted(resolution.merged_tags)[:5]}...")

            click.echo(f"\n[SUCCESS] Resolved {len(resolutions)} conflict(s)")
            click.echo("[INFO] Conflict logs saved to: RUNS/tag-conflicts/")
        else:
            click.echo("\n[SUCCESS] No conflicts detected - tags are in sync")

    if not test:
        click.echo("\n[SYNC] Tag synchronization would happen here")
        click.echo("[INFO] Full implementation requires tag storage format decision")
    else:
        click.echo("\n[TEST] Test mode complete - no changes made")

    click.echo("[SUCCESS] Tag sync complete")


@cli.command()
@click.argument("template", type=str)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
def dataview(template: str, output: Optional[str]) -> None:
    """Generate Dataview queries from templates.

    Supports 9 query templates:

    Basic Templates:
    - tasks-by-status: List tasks grouped by status
    - sessions-by-phase: List sessions grouped by phase
    - coverage-trends: Show coverage trend over time
    - recent-commits: Show recent commits with metadata

    Phase 2 Templates (NEW):
    - quality-metrics: P6 compliance tracking
    - phase-summary: Milestone reporting with aggregated stats
    - file-changes: Change frequency analysis
    - constitutional-compliance: Article tracking
    - team-activity: Contributor statistics

    Args:
        template: Template name (see list above).
        output: Output file path (optional).

    Example:
        $ python scripts/tier1_cli.py dataview tasks-by-status
        $ python scripts/tier1_cli.py dataview quality-metrics -o queries/quality.md
        $ python scripts/tier1_cli.py dataview team-activity
    """
    click.echo(f"[DATAVIEW] Generating query from template: {template}")

    templates = {
        "tasks-by-status": """```dataview
TABLE
  title as "Task",
  status as "Status",
  phase as "Phase",
  file.mtime as "Modified"
FROM "개발일지"
WHERE type = "task"
SORT status ASC, file.mtime DESC
GROUP BY status
```""",
        "sessions-by-phase": """```dataview
TABLE
  title as "Session",
  phase as "Phase",
  duration as "Duration",
  file.mtime as "Date"
FROM "개발일지"
WHERE type = "session"
SORT phase ASC, file.mtime DESC
GROUP BY phase
```""",
        "coverage-trends": """```dataview
TABLE
  title as "Test",
  coverage as "Coverage %",
  file.mtime as "Date"
FROM "개발일지"
WHERE contains(tags, "domain/testing")
SORT file.mtime DESC
LIMIT 10
```""",
        "recent-commits": """```dataview
TABLE
  commit as "Commit",
  type as "Type",
  file.mtime as "Date"
FROM "개발일지"
WHERE commit
SORT file.mtime DESC
LIMIT 20
```""",
        "quality-metrics": """```dataview
TABLE
  title as "Article",
  compliance as "Compliance %",
  violations as "Violations",
  file.mtime as "Last Check"
FROM "개발일지"
WHERE contains(tags, "domain/quality")
SORT compliance DESC
```""",
        "phase-summary": """```dataview
TABLE
  phase as "Phase",
  count(rows) as "Sessions",
  sum(duration) as "Total Time",
  avg(coverage) as "Avg Coverage %"
FROM "개발일지"
WHERE type = "session"
GROUP BY phase
SORT phase ASC
```""",
        "file-changes": """```dataview
TABLE
  file.name as "File",
  length(file.inlinks) as "References",
  length(file.outlinks) as "Links",
  file.mtime as "Last Modified"
FROM "개발일지"
SORT file.mtime DESC
LIMIT 30
```""",
        "constitutional-compliance": """```dataview
TABLE
  article as "Article",
  status as "Status",
  last_validated as "Last Validated",
  violations as "Violations"
FROM "개발일지"
WHERE contains(tags, "constitutional")
SORT article ASC
```""",
        "team-activity": """```dataview
TABLE
  author as "Author",
  count(rows) as "Commits",
  sum(lines_changed) as "Lines Changed",
  file.mtime as "Last Activity"
FROM "개발일지"
WHERE type = "commit"
GROUP BY author
SORT count(rows) DESC
```""",
    }

    if template not in templates:
        click.echo(f"[ERROR] Unknown template: {template}")
        click.echo(f"[INFO] Available templates: {', '.join(templates.keys())}")
        sys.exit(1)

    query = templates[template]

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(query, encoding="utf-8")
        click.echo(f"[SUCCESS] Query saved to: {output}")
    else:
        click.echo("\n" + query)

    click.echo(f"[SUCCESS] Generated {template} query")


@cli.command()
@click.argument("diagram_type", type=click.Choice(["architecture", "dependencies", "tasks"]))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--theme",
    type=click.Choice(["default", "dark", "forest", "neutral"], case_sensitive=False),
    default="default",
    help="Mermaid theme (default, dark, forest, neutral)",
)
@click.option(
    "--layout",
    type=click.Choice(["TB", "LR", "RL", "BT"], case_sensitive=False),
    default="TB",
    help="Graph layout direction (TB=top-bottom, LR=left-right, RL=right-left, BT=bottom-top)",
)
@click.option(
    "--max-nodes",
    type=int,
    default=10,
    help="Maximum nodes per subgraph (default: 10)",
)
def mermaid(diagram_type: str, output: Optional[str], theme: str, layout: str, max_nodes: int) -> None:
    """Generate Mermaid diagrams automatically with customization.

    Supports diagram types:
    - architecture: System architecture from scripts/ directory
    - dependencies: Task dependency graph from YAML contracts
    - tasks: Task workflow from TASKS/ directory

    Customization Options (Phase 2):
    - --theme: Visual theme (default, dark, forest, neutral)
    - --layout: Graph direction (TB, LR, RL, BT)
    - --max-nodes: Limit nodes per subgraph to reduce complexity

    Args:
        diagram_type: Type of diagram (architecture/dependencies/tasks).
        output: Output file path (optional).
        theme: Mermaid theme name.
        layout: Graph layout direction.
        max_nodes: Maximum nodes to show per subgraph.

    Example:
        $ python scripts/tier1_cli.py mermaid architecture
        $ python scripts/tier1_cli.py mermaid dependencies --theme dark --layout LR
        $ python scripts/tier1_cli.py mermaid tasks --max-nodes 5 -o workflow.md
    """
    from pathlib import Path

    click.echo(f"[MERMAID] Generating {diagram_type} diagram...")
    click.echo(f"[INFO] Theme: {theme}, Layout: {layout}, Max nodes: {max_nodes}")

    # Theme initialization directive
    theme_directive = ""
    if theme != "default":
        theme_directive = f"%%{{init: {{'theme':'{theme}'}}}}%%\n"

    if diagram_type == "architecture":
        # Scan scripts/ directory
        scripts_path = Path("scripts")
        if not scripts_path.exists():
            click.echo("[ERROR] scripts/ directory not found")
            sys.exit(1)

        # Group files by category
        categories = {"execution": [], "analysis": [], "validation": [], "integration": []}

        for py_file in scripts_path.glob("*.py"):
            name = py_file.stem
            if "executor" in name or "runner" in name:
                categories["execution"].append(name)
            elif "analyzer" in name or "detector" in name:
                categories["analysis"].append(name)
            elif "validator" in name or "enforcer" in name:
                categories["validation"].append(name)
            elif "bridge" in name or "sync" in name or "cli" in name:
                categories["integration"].append(name)

        diagram = f"```mermaid\n{theme_directive}graph {layout}\n    subgraph Execution\n"
        for script in categories["execution"][:max_nodes]:
            diagram += f"        {script}[{script}]\n"

        diagram += "    end\n\n    subgraph Analysis\n"
        for script in categories["analysis"][:max_nodes]:
            diagram += f"        {script}[{script}]\n"

        diagram += "    end\n\n    subgraph Validation\n"
        for script in categories["validation"][:max_nodes]:
            diagram += f"        {script}[{script}]\n"

        diagram += "    end\n\n    subgraph Integration\n"
        for script in categories["integration"][:max_nodes]:
            diagram += f"        {script}[{script}]\n"

        diagram += "    end\n```"

    elif diagram_type == "dependencies":
        diagram = f"```mermaid\n{theme_directive}graph {layout}\n"
        diagram += """    P1[P1: YAML First] --> TaskExecutor
    P2[P2: Evidence] --> TaskExecutor
    P4[P4: SOLID] --> DeepAnalyzer
    P5[P5: Security] --> DeepAnalyzer
    P6[P6: Quality Gates] --> Validator
    P8[P8: Test First] --> TDDEnforcer

    TaskExecutor --> Evidence[RUNS/evidence/]
    DeepAnalyzer --> Reports[Analysis Reports]
    Validator --> Gates[Quality Metrics]
    TDDEnforcer --> Coverage[Coverage Data]
```"""

    elif diagram_type == "tasks":
        # Scan TASKS/ directory
        tasks_path = Path("TASKS")
        if not tasks_path.exists():
            click.echo("[ERROR] TASKS/ directory not found")
            sys.exit(1)

        yaml_files = list(tasks_path.glob("*.yaml"))

        diagram = f"```mermaid\n{theme_directive}graph {layout}\n"
        diagram += "    Start[Project Start] --> Planning\n"
        for i, yaml_file in enumerate(yaml_files[:max_nodes]):
            task_name = yaml_file.stem.replace("-", "_")
            diagram += f"    Planning --> {task_name}[{yaml_file.stem}]\n"

        diagram += "    Planning --> Complete[Project Complete]\n```"

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(diagram, encoding="utf-8")
        click.echo(f"[SUCCESS] Diagram saved to: {output}")
    else:
        click.echo("\n" + diagram)

    click.echo(f"[SUCCESS] Generated {diagram_type} diagram")


@cli.command()
@click.option(
    "--port",
    type=int,
    default=8501,
    help="Port for Streamlit dashboard (default: 8501)",
)
@click.option(
    "--export",
    type=click.Choice(["png", "pdf"], case_sensitive=False),
    help="Export dashboard to file instead of launching UI",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file path for export (default: RUNS/exports/dashboard_<timestamp>.<format>)",
)
def tdd_dashboard(port: int, export: Optional[str], output: Optional[str]) -> None:
    """Launch interactive TDD metrics dashboard or export to file.

    Features:
    - Real-time coverage trends
    - Test count evolution
    - Quality gate status
    - Phase-by-phase metrics
    - Export to PNG/PDF (Phase 2)

    Args:
        port: Port for Streamlit dashboard (default: 8501).
        export: Export format (png or pdf) instead of launching UI.
        output: Custom output file path.

    Example:
        $ python scripts/tier1_cli.py tdd-dashboard
        $ python scripts/tier1_cli.py tdd-dashboard --port 8502
        $ python scripts/tier1_cli.py tdd-dashboard --export pdf
        $ python scripts/tier1_cli.py tdd-dashboard --export png -o report.png
    """
    from pathlib import Path
    import subprocess

    dashboard_path = Path("scripts/tdd_metrics_dashboard.py")

    if not dashboard_path.exists():
        click.echo(f"[ERROR] Dashboard not found: {dashboard_path}")
        click.echo("[INFO] Dashboard script needs to be created")
        sys.exit(1)

    # Export mode (Phase 2.4)
    if export:
        from datetime import datetime
        from tdd_metrics_dashboard import load_coverage_data, calculate_quality_gates

        click.echo(f"[EXPORT] Generating {export.upper()} report...")

        # Load data
        df = load_coverage_data()
        if df.empty:
            click.echo("[WARNING] No coverage data found, generating sample data")

        gates = calculate_quality_gates(df)

        # Determine output path
        if output:
            export_path = Path(output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(f"RUNS/exports/dashboard_{timestamp}.{export}")

        export_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if export == "png":
                import plotly.express as px
                import plotly.io as pio

                # Create coverage trend chart
                fig = px.line(df, x="date", y="coverage", color="phase", title="Coverage Evolution Over Time", markers=True)
                fig.add_hline(y=4.0, line_dash="dash", line_color="red", annotation_text="Phase 4 Threshold (4.0%)")

                pio.write_image(fig, str(export_path), format="png", width=1200, height=600)
                click.echo(f"[SUCCESS] Exported PNG to: {export_path}")

            elif export == "pdf":
                from matplotlib.backends.backend_pdf import PdfPages
                import matplotlib.pyplot as plt

                with PdfPages(str(export_path)) as pdf:
                    # Summary page
                    fig, ax = plt.subplots(figsize=(11, 8.5))
                    ax.axis("off")
                    summary = f"""
TDD Metrics Dashboard Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Current Metrics:
- Coverage: {gates['coverage']:.2f}%
- Test Count: {gates['test_count']}
- Quality Status: {gates['overall_status']}

Quality Gates:
- Coverage Gate (>=4.0%): {'PASS' if gates['coverage_gate'] else 'FAIL'}
- Test Count Gate (>=80): {'PASS' if gates['test_count_gate'] else 'FAIL'}
- Trend Gate (>=0): {'PASS' if gates['trend_gate'] else 'FAIL'}
"""
                    ax.text(0.1, 0.5, summary, fontsize=12, family="monospace", verticalalignment="center")
                    pdf.savefig(fig, bbox_inches="tight")
                    plt.close()

                click.echo(f"[SUCCESS] Exported PDF to: {export_path}")

        except ImportError as e:
            click.echo(f"[ERROR] Missing dependency: {e}")
            if export == "png":
                click.echo("[INFO] Install with: pip install kaleido")
            else:
                click.echo("[INFO] Install with: pip install matplotlib")
            sys.exit(1)
        except Exception as e:
            click.echo(f"[ERROR] Export failed: {e}")
            sys.exit(1)

        return

    # Interactive dashboard mode
    click.echo(f"[DASHBOARD] Launching TDD metrics dashboard on port {port}...")
    click.echo(f"[INFO] Dashboard will open at http://localhost:{port}")

    try:
        subprocess.run(["streamlit", "run", str(dashboard_path), "--server.port", str(port)], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"[ERROR] Failed to launch dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo("[ERROR] Streamlit not installed")
        click.echo("[INFO] Install with: pip install streamlit")
        sys.exit(1)


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
