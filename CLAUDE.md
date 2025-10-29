# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dev Rules Starter Kit is a **Constitution-Based Development Framework** implementing an executable knowledge base system. YAML contracts are executed through TaskExecutor to create self-documenting, evidence-based development workflows.

### Core Philosophy
- **Constitution-Centric**: 13 articles (P1-P13) define all development principles
- **Executable Documentation**: YAML contracts â†’ TaskExecutor â†’ Evidence â†’ Obsidian sync
- **7-Layer Architecture**: Each tool enforces specific constitutional articles

## Critical Rules âš ï¸

### Windows Encoding - NEVER USE EMOJIS IN PYTHON CODE
```python
# WRONG - Will crash on Windows
print("âœ… Task completed")
status = "ðŸš€ Deploying"

# CORRECT - Use ASCII alternatives
print("[SUCCESS] Task completed")
status = "[DEPLOY] Deploying"
```

**Emoji Usage Rules**:
- âœ… Markdown files (.md)
- âœ… Git commit messages
- âŒ Python code (.py)
- âŒ YAML files
- âŒ Shell scripts

## Commands

### Environment Setup
```bash
# Virtual environment (ALWAYS use venv)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt      # Core dependencies
pip install -r requirements-dev.txt  # Development dependencies
pip install -e .                     # Package in development mode

# Pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### Core Development Commands
```bash
# TaskExecutor (core system)
python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan  # Preview
python scripts/task_executor.py TASKS/TEMPLATE.yaml         # Execute

# Constitution validation
python scripts/constitutional_validator.py  # Validate compliance
python scripts/constitutional_validator.py --validate  # Full validation

# Code analysis
python scripts/deep_analyzer.py  # SOLID/security/hallucination checks
python scripts/team_stats_aggregator.py  # Quality metrics (P6)
python scripts/critical_file_detector.py  # Find high-impact files

# Testing
pytest tests/                    # All tests
pytest tests/test_file.py       # Single file
pytest tests/ -k "test_name"    # Specific test
pytest --cov=scripts tests/     # With coverage
pytest -xvs tests/test_file.py::test_specific  # Debug single test

# Code quality
ruff check scripts/ tests/      # Linting
ruff format scripts/ tests/     # Formatting
```

### Advanced Tools
```bash
# Development assistant (file watcher)
python scripts/dev_assistant.py  # Auto-verify on save

# Tier 1 CLI features
python scripts/tier1_cli.py tag-sync  # Sync tags to Obsidian
python scripts/tier1_cli.py dataview  # Generate Obsidian queries
python scripts/tier1_cli.py mermaid   # Create Mermaid diagrams
python scripts/tier1_cli.py tdd       # Enforce TDD metrics

# Session management
python scripts/session_manager.py start    # Start session
python scripts/session_manager.py save     # Save session state
python scripts/session_manager.py restore  # Restore session

# Context management
python scripts/context_provider.py init         # Initialize context
python scripts/context_provider.py get-context  # Show current context
python scripts/context_provider.py print-hash   # Verify context hash
python scripts/context_aware_loader.py --resume # Resume with context

# Obsidian sync
python scripts/obsidian_bridge.py test  # Test connection
python scripts/obsidian_bridge.py sync  # Manual sync
```

### Slash Commands for Rapid Development
Available custom slash commands (use with Claude Code):
- `/dev "natural language request"` - 6-stage pipeline with academic verification
- `/speckit-constitution` - Create/update project constitution
- `/speckit-specify` - Create feature spec from natural language
- `/speckit-plan` - Generate implementation plan from spec
- `/speckit-tasks` - Generate dependency-ordered tasks
- `/speckit-implement` - Execute implementation plan

## Architecture

### 7-Layer System
```
Layer 1: Constitution (config/constitution.yaml)
    â”œâ”€â”€ P1-P10: Development process rules
    â””â”€â”€ P11-P13: Governance and meta rules

Layer 2: Execution
    â”œâ”€â”€ TaskExecutor - YAML contract executor (P1, P2)
    â”œâ”€â”€ EnhancedTaskExecutorV2 - Parallel execution with worker pools
    â””â”€â”€ ConstitutionalValidator - Compliance checker (all articles)

Layer 3: Analysis
    â”œâ”€â”€ DeepAnalyzer - SOLID, security, hallucination checks (P4, P5, P7)
    â””â”€â”€ TeamStatsAggregator - Quality metrics (P6)

Layer 4: Optimization
    â”œâ”€â”€ VerificationCache - Prevent duplicate checks (60% reduction)
    â”œâ”€â”€ CriticalFileDetector - Identify core files (impact >0.5)
    â””â”€â”€ WorkerPool - Parallel task execution

Layer 5: Evidence Collection
    â””â”€â”€ RUNS/evidence/ - All execution logs and evidence

Layer 6: Knowledge Asset
    â”œâ”€â”€ ObsidianBridge - Knowledge base sync in 3 seconds (P3)
    â””â”€â”€ ContextProvider - Maintain context across sessions

Layer 7: Visualization
    â””â”€â”€ Streamlit Dashboard - Status display only
```

### Key Components

**Core Execution Pipeline**:
1. `task_executor.py` - Executes YAML contracts, enforces P1-P2
2. `constitutional_validator.py` - Validates compliance with all articles
3. `obsidian_bridge.py` - Syncs to Obsidian knowledge base (P3)
4. `context_provider.py` - Maintains session context

**Analysis & Validation**:
- `deep_analyzer.py` - SOLID principles, security, hallucination detection
- `team_stats_aggregator.py` - Calculates quality metrics
- `critical_file_detector.py` - Identifies high-impact files
- `verification_cache.py` - Caches validation results for performance

**Session & Context Management**:
- `session_manager.py` - Session state persistence (30min checkpoints)
- `context_aware_loader.py` - Resume with previous context
- `auto_context_tracker.py` - Automatic context tracking

**Advanced Features**:
- `enhanced_task_executor_v2.py` - Parallel execution with worker pools
- `tier1_cli.py` - Advanced CLI features (tag sync, dataview, mermaid, TDD)
- `principle_conflict_detector.py` - Detects constitutional conflicts (P11)

### Constitutional Articles Reference

| ID | Article | Enforcing Tool | Purpose |
|----|---------|----------------|---------|
| P1 | YAML First | TaskExecutor | All tasks as YAML contracts |
| P2 | Evidence-Based | TaskExecutor | All executions auto-recorded |
| P3 | Knowledge Asset | ObsidianBridge | Knowledge base sync |
| P4 | SOLID Principles | DeepAnalyzer | Code quality enforcement |
| P5 | Security First | DeepAnalyzer | Security gate checks |
| P6 | Quality Gates | TeamStatsAggregator | Metric enforcement |
| P7 | Hallucination Prevention | DeepAnalyzer | Verify all claims |
| P8 | Test First | pytest | TDD approach |
| P9 | Conventional Commits | pre-commit | Standardized commits |
| P10 | Windows UTF-8 | System | Encoding consistency |
| P11 | Principle Conflicts | AI Manual | Resolve contradictions |
| P12 | Trade-off Analysis | AI Manual | Document decisions |
| P13 | Constitution Updates | User Approval | Change verification |

## Working with the System

### Creating New Features
1. **Define in YAML first** (P1):
   ```yaml
   # TASKS/FEAT-YYYY-MM-DD-XX.yaml
   task_id: "FEAT-2025-10-26-01"
   title: "Feature description"
   gates:
     - type: "constitutional"
       articles: ["P4", "P5"]
   commands:
     - exec: ["python", "scripts/implementation.py"]
   ```

2. **Validate plan then execute**:
   ```bash
   python scripts/task_executor.py TASKS/FEAT-2025-10-26-01.yaml --plan
   # Review plan then execute
   python scripts/task_executor.py TASKS/FEAT-2025-10-26-01.yaml
   ```

3. **Evidence auto-collected**: Saved to `RUNS/evidence/`
4. **Obsidian auto-sync**: Knowledge base updated within 3 seconds

### Security Gates
TaskExecutor enforces:
- Command whitelist (ALLOWED_CMDS)
- Risk pattern detection
- Environment variable filtering
- Secret detection (gitleaks)
- Port conflict checking
- Dependency verification

### Testing Strategy
- **Unit tests**: `tests/test_*.py`
- **Integration tests**: `tests/test_*_integration.py`
- **Coverage requirement**: â‰¥90%
- **Performance tests**: Marked with `@pytest.mark.benchmark`

### Git Workflow
```bash
# ALWAYS check status first
git status && git branch

# Feature branches only
git checkout -b tier1/feature-name

# Conventional Commits (enforced by pre-commit)
git commit -m "feat(scope): add new feature"
git commit -m "fix(scope): resolve issue"
git commit -m "docs(scope): update documentation"
```

## Context Persistence

```bash
# Initialize master configuration
python scripts/context_provider.py init

# Check current context
python scripts/context_provider.py get-context

# Resume session with context
python scripts/context_aware_loader.py --resume
```

**Context mechanism**:
- `config/master_config.json`: Central configuration store
- `RUNS/context/`: Per-session context snapshots
- Automatic context restoration on session start

## Obsidian Integration

### Configuration
Set `OBSIDIAN_VAULT_PATH` in `.env`:
```bash
OBSIDIAN_VAULT_PATH=C:/Users/user/Documents/ObsidianVault
OBSIDIAN_ENABLED=true
PROJECT_NAME=MyProject
```

### Automatic sync triggers
- TaskExecutor execution completion
- 3+ file changes
- Major feature completion
- Bug fixes (MEDIUM+ severity)

### Knowledge structure
- `ê°œë°œì¼ì§€/`: Daily development logs
- `TASKS/`: Task contract copies
- `MOCs/`: Knowledge maps (auto-updated)
- `evidence/`: Execution evidence links

## Critical Files (Impact Score >0.5)

Files requiring extra validation:
- `*_executor.py` - Core execution engines
- `*_validator.py` - Validation systems
- `constitutional_*.py` - Constitution enforcement tools
- `*_guard.py` - Security components
- `project_*.py` - Project steering
- `context_*.py` - Context management
- `obsidian_*.py` - Knowledge synchronization

## Development Philosophy

### NORTH_STAR.md Principles
1. **Constitution is Law** - All tools enforce specific articles
2. **Documentation = Code** - YAML contracts are executable
3. **Evidence > Assumptions** - All claims must be verifiable
4. **ROI-Focused** - 377% annual return on setup investment

### Anti-patterns to Avoid âŒ
- Working directly on main/master branch
- Skipping YAML contracts for complex tasks
- Adding features without constitutional basis
- Focusing on UI over constitution compliance
- Creating isolated tools without article enforcement
- Using system Python without venv
- Ending sessions without context save
- **Using emojis in Python code**

## Troubleshooting

### Common Issues
```bash
# Verify virtual environment is active
which python  # Should show .venv path (Linux/Mac)
where python  # Windows - should show .venv path

# Ruff not found
pip install ruff  # Run inside venv

# Obsidian sync failure
type .env | findstr OBSIDIAN_VAULT_PATH  # Windows
cat .env | grep OBSIDIAN_VAULT_PATH      # Linux/Mac
python scripts/obsidian_bridge.py test   # Test connection

# Context mismatch
python scripts/context_provider.py diagnose  # Run diagnostics

# Pre-commit hooks not running
pre-commit install

# Windows encoding errors
# Set environment variable: PYTHONUTF8=1
# Or add to scripts: # -*- coding: utf-8 -*-
```

### Performance Optimization
- VerificationCache reduces duplicate checks by 60%
- WorkerPool for parallel execution
- Smart cache with 5-minute TTL
- Critical file detection for focused verification
- Context hash for fast consistency checks

## Related Documentation

- **[NORTH_STAR.md](NORTH_STAR.md)**: Core philosophy and direction (1-minute read)
- **[DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)**: Development standards and Windows encoding rules
- **[config/constitution.yaml](config/constitution.yaml)**: Full constitution text (800+ lines)
- **[docs/SESSION_MANAGEMENT_GUIDE.md](docs/SESSION_MANAGEMENT_GUIDE.md)**: Session context persistence details
## Latest Updates (2025-10-29)
- **TaskExecutor internal commands**: write_file, eplace, un_shell_command are now handled via INTERNAL_FUNCTIONS and ALLOWED_SHELL_CMDS. Use dictionaries for internal args and lists for shell args.
- **Collaboration locks**: scripts/agent_sync.py manages per-agent locks; TaskExecutor auto-acquires/releases locks based on contract evidence/commands. Check dev-context/agent_sync_state.json for gents + locks entries.
- **multi_agent_sync**: reads/writes the new state format and keeps _LATEST_LOCKS in sync. Never overwrite the locks array manually.
- **Enhanced Task Executor v2**: provides _parse_task_line, _execute_sequential_tasks, _generate_evidence, _calculate_statistics, and passes 	ests/test_enhanced_task_executor_v2.py. Use EnhancedTaskExecutorV2 for compatibility with older tooling.
- **Validation**: python -m pytest -q tests/test_enhanced_task_executor_v2.py covers the executor API; rerun after touching execution logic.

- **Preflight check**: run python scripts/preflight_checks.py before handoff or major merges to execute 	ests/test_enhanced_task_executor_v2.py automatically.

- **Lock status CLI**: use python scripts/agent_sync_status.py to list active locks or python scripts/agent_sync_status.py --agent codex --task TASK-123 --files src/app.py to preflight conflicts.

## Collaboration Workflow (2025-10-29)
1. python scripts/multi_agent_sync.py list·Î ÇöÀç ÄÚµð³×ÀÌ¼Ç »óÅÂ È®ÀÎ
2. python scripts/agent_sync_status.py / --agent ¡¦ --files ¡¦·Î Àá±Ý Ãæµ¹ ¿©ºÎ ¼±Á¡
3. YAML °è¾à¿¡ Evidence/Commands·Î ÆíÁý ÆÄÀÏÀ» ¸ðµÎ ±âÀç (TaskExecutor°¡ ÀÚµ¿ Àá±Ý)
4. ½ÇÇà Àü python scripts/preflight_checks.py (ÇÊ¿ä ½Ã --quick, --only-handoff)
5. ÇÚµå¿ÀÇÁ ½Ã Àá±Ý ÇØÁ¦ ¹× docs/COLLAB_LOCKING_GUIDE.md Âü°í »çÇ×À» ÇÔ²² Àü´Þ

> »ó¼¼ ÀýÂ÷¿Í Ã¼Å©¸®½ºÆ®´Â docs/COLLAB_LOCKING_GUIDE.md¿¡ Á¤¸®µÇ¾î ÀÖÀ¸¸ç, Obsidian ½ÌÅ© ½Ã ÇØ´ç ¹®¼­¸¦ °øÀ¯ÇÏ¼¼¿ä.

