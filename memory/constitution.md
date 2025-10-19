# Dev-Rules-Starter-Kit Constitution

**Purpose**: This constitution defines the immutable principles governing all development within the dev-rules-starter-kit ecosystem.

**Scope**: All code, specifications, and artifacts generated through this system must comply with these articles.

---

## Core Principles

### I. Library-First Development

**Principle**: Every feature must begin as a standalone library with clear boundaries and minimal dependencies.

**Requirements**:
- Features implemented as independent Python packages/modules
- Each library must have single responsibility
- Libraries must be self-contained and independently testable
- Clear purpose required - no organizational-only libraries
- All libraries must include comprehensive docstrings

**Rationale**: Modularity ensures reusability, testability, and maintainability across all projects.

**Enforcement**:
- Pre-commit hooks verify module isolation
- Integration tests validate library boundaries
- Code reviews check for tight coupling

---

### II. CLI Interface Mandate

**Principle**: Every library must expose functionality through command-line interfaces.

**Requirements**:
- All CLI interfaces MUST:
  - Accept text as input (stdin, arguments, or files)
  - Produce text as output (stdout)
  - Report errors to stderr
  - Support JSON format for structured data exchange
  - Provide `--help` documentation

**Rationale**: Text-based I/O ensures:
- Observability (all operations are inspectable)
- Composability (UNIX philosophy: do one thing well)
- Debuggability (trace inputs/outputs easily)
- Automation (scriptable workflows)

**Example**:
```bash
# Good: CLI with clear I/O
python -m error_learner capture \
  --error-type "UnicodeEncodeError" \
  --solution "Use ASCII alternatives" \
  --output json

# Bad: Library-only interface (no CLI)
from error_learner import ErrorLearner
learner = ErrorLearner()  # ❌ No CLI access
```

---

### III. Test-First Development (NON-NEGOTIABLE)

**Principle**: ALL implementation MUST follow strict Test-Driven Development (TDD).

**Requirements**:
1. **Tests written FIRST** (before any implementation code)
2. **User approval** of test specifications
3. **Tests FAIL** (Red phase confirmed)
4. **Then implement** to make tests pass (Green phase)
5. **Refactor** while keeping tests green

**Coverage Requirements**:
- Minimum 90% test coverage for all modules
- Integration tests for all CLI interfaces
- Edge case testing mandatory

**Rationale**: TDD ensures:
- Specifications drive implementation (not vice versa)
- All code is testable by design
- Regression prevention
- Living documentation through tests

**Example Workflow**:
```bash
# 1. Write tests (FAIL)
pytest tests/test_new_feature.py  # ❌ 0/10 passing

# 2. Get user approval
# User confirms: "Tests correctly specify behavior"

# 3. Implement
vim src/new_feature.py

# 4. Tests pass
pytest tests/test_new_feature.py  # ✅ 10/10 passing
```

---

### IV. Integration-First Testing

**Principle**: Prioritize real-world integration tests over isolated unit tests.

**Requirements**:
- **Contract tests** mandatory before implementation
- Use real databases, not mocks (when feasible)
- Use actual service instances over stubs
- Test in realistic environments
- E2E tests for critical user journeys

**Focus Areas**:
- New library contract tests
- API contract changes
- Inter-service communication
- Shared schema validation

**Rationale**: Mocks hide integration issues. Real environments expose actual problems.

---

### V. Windows Encoding Compliance (CRITICAL)

**Principle**: Never use emoji characters in code, print statements, or file operations.

**Requirements**:
- **Prohibited**: Emoji in Python code, YAML, shell scripts
- **Allowed**: Emoji in Markdown, HTML, user-facing UI
- **Replacement**: Use ASCII status icons (`[OK]`, `[FAIL]`, `[WARN]`)

**Rationale**: Windows default encoding (cp949) cannot handle emojis, causing `UnicodeEncodeError`.

**Pre-commit Enforcement**:
```yaml
- id: check-emoji
  entry: python -c "import sys, re; sys.exit(any(re.search(r'[^\x00-\x7F]', open(f).read()) for f in sys.argv[1:]))"
  files: \.(py|yaml|yml|sh)$
```

**ASCII Replacements**:
```python
"✅" → "[OK]" or "[SUCCESS]"
"❌" → "[FAIL]" or "[ERROR]"
"⚠️" → "[WARN]"
"📝" → "[LOG]"
"🚀" → "[DEPLOY]"
```

---

### VI. Observability & Structured Logging

**Principle**: All operations must be observable through structured logging and text-based I/O.

**Requirements**:
- Use Python `logging` module (not `print()`)
- JSON-formatted logs for machine parsing
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include context: timestamps, module, function, line number
- Performance metrics logged for optimization

**Example**:
```python
import logging
import json

logger = logging.getLogger(__name__)

# Good: Structured logging
logger.info(json.dumps({
    "event": "task_completed",
    "task_id": "T001",
    "duration_ms": 1234,
    "status": "success"
}))

# Bad: Unstructured print
print("Task T001 completed")  # ❌ No metadata
```

---

### VII. Simplicity & YAGNI

**Principle**: Start simple, add complexity only when proven necessary.

**Requirements**:
- **Minimal Project Structure**: Maximum 3 projects for initial implementation
- **No Future-Proofing**: Implement current requirements only (YAGNI)
- **No Speculative Features**: All features must trace to user stories
- **Complexity Justification**: Additional complexity requires documented rationale

**Gates** (Pre-implementation checklist):
- [ ] Using ≤3 projects?
- [ ] No future-proofing?
- [ ] All features have user stories?
- [ ] No speculative abstractions?

**Rationale**: Premature optimization and over-engineering cause maintenance burden.

---

### VIII. Anti-Abstraction & Framework Trust

**Principle**: Use framework features directly rather than wrapping them in abstractions.

**Requirements**:
- **Framework Trust**: Trust frameworks to do their job (don't wrap everything)
- **Single Model Representation**: Avoid redundant domain model layers
- **Direct Usage**: Use ORM models directly (no DTO layers unless proven necessary)

**Example**:
```python
# Good: Direct framework usage
from sqlalchemy.orm import Session
session.query(User).filter_by(email=email).first()

# Bad: Unnecessary abstraction
class UserRepository:  # ❌ Wrapping ORM unnecessarily
    def find_by_email(self, email):
        return session.query(User).filter_by(email=email).first()
```

**Exceptions** (Justified Complexity):
- Multi-database support requires abstraction
- Third-party API changes require isolation layer
- Complex business rules need domain logic layer

---

### IX. Specification-Driven Development (SDD)

**Principle**: Specifications are executable artifacts that generate implementation, not merely guide it.

**Requirements**:
- **Specs First**: All features start with spec.md (what/why, not how)
- **Implementation Plans**: plan.md translates requirements to technical decisions
- **Task Breakdown**: tasks.md generates actionable, parallelizable tasks
- **Constitution Check**: All plans pass constitutional gates before implementation
- **Living Documentation**: Specs evolve with code, never drift

**Workflow**:
```bash
/speckit.specify "feature description"  # Create spec.md
/speckit.plan "tech stack choices"      # Generate plan.md + research.md
/speckit.tasks                          # Generate tasks.md
/speckit.implement                      # Execute tasks
```

**Rationale**: Specifications as source of truth eliminate intent-implementation gap.

---

### X. Conventional Commits & Semantic Versioning

**Principle**: All commits follow Conventional Commits standard for automated versioning.

**Commit Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature (MINOR version bump)
- `fix`: Bug fix (PATCH version bump)
- `docs`: Documentation only
- `refactor`: Code refactoring (no behavior change)
- `perf`: Performance improvement (PATCH version bump)
- `test`: Test additions/modifications
- `chore`: Build/config changes
- `BREAKING CHANGE`: Breaking change (MAJOR version bump)

**Scopes**: `api`, `db`, `auth`, `ui`, `core`, `config`, `deploy`, `docs`, `test`, `perf`, `security`, `deps`, `build`

**Versioning**:
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, performance improvements
- **MINOR** (1.0.0 → 1.1.0): New features (backward compatible)
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes (API, DB schema)

---

## Governance

### Amendment Process

**Requirements**:
- Explicit documentation of change rationale
- Review and approval by project maintainers
- Backward compatibility assessment
- Migration plan for existing code
- Version increment according to impact:
  - **MAJOR**: Backward-incompatible governance changes
  - **MINOR**: New principle/section added
  - **PATCH**: Clarifications, wording fixes

### Compliance Enforcement

**Automated**:
- Pre-commit hooks (ruff, commitlint, gitleaks, emoji check)
- CI/CD pipelines (pytest, coverage, type checking)
- Branch protection rules (require passing checks)

**Manual**:
- Code reviews verify constitutional compliance
- PR checklists include constitutional gates
- Quarterly constitution reviews

### Exception Handling

**Justified Violations**:
- Document in `Complexity Tracking` section
- Provide rationale referencing constitution article
- Get explicit approval in code review
- Add TODO for future refactoring if temporary

**Example**:
```markdown
## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4th project (Article VII) | Legacy system integration | 3 projects insufficient for isolation |
| Repository pattern (Article VIII) | Multi-DB support needed | Direct ORM locks us to single DB |
```

---

## Document Lifecycle

**Retention Policy**:
- **Active**: `claudedocs/00_ACTIVE/` (current reference docs)
- **Analysis Reports**: `claudedocs/analysis/` (3 months retention)
- **Performance Reports**: `claudedocs/reports/` (6 months retention)
- **Archive**: `claudedocs/archive/` (3+ months old)

**Monthly Cleanup** (1st-5th of month):
1. Archive analysis reports >90 days old
2. Delete archives >180 days old
3. Consolidate duplicate STATUS/SUMMARY files

---

## Quick Decision Tree

**When adding a feature**:
```
1. Spec exists? NO → Write spec.md first (Article IX)
2. Tests written? NO → Write tests first (Article III)
3. Tests fail? NO → Fix tests (must fail before implementation)
4. ≤3 projects? NO → Justify complexity (Article VII)
5. Using framework directly? NO → Remove abstraction (Article VIII)
6. CLI exposed? NO → Add CLI interface (Article II)
7. Integration tests? NO → Add contract tests (Article IV)
8. Emoji-free? NO → Replace with ASCII (Article V)
9. Structured logging? NO → Add JSON logs (Article VI)
10. Conventional commit? NO → Fix commit message (Article X)
```

---

**Version**: 1.0.0
**Ratified**: 2025-10-20
**Last Amended**: 2025-10-20
**Next Review**: 2026-01-20 (Quarterly)

---

**Constitution supersedes all other development practices.**
When conflicts arise between this constitution and other documentation, the constitution prevails.
