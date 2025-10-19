---
description: Generate implementation plan from specification with constitutional compliance checks
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. **Load context**:
   - Find latest spec.md in specs/ directory (use git branch name)
   - Read `/memory/constitution.md` for compliance gates
   - Identify FEATURE_DIR from current branch

2. **Execute plan workflow**:

   a. **Fill Technical Context** (ask user if needed):
      - Language/Version (e.g., Python 3.11, Node.js 18)
      - Primary Dependencies (e.g., FastAPI, React)
      - Storage (PostgreSQL, SQLite, Redis, N/A)
      - Testing (pytest, jest, vitest)
      - Target Platform (Linux, Windows, macOS, iOS, Android)
      - Performance Goals (req/s, latency, throughput)
      - Constraints (memory, offline-capable, etc.)
      - Scale/Scope (users, LOC, screens)

   b. **Constitutional Compliance Check** (PRE-IMPLEMENTATION GATES):
      ```markdown
      ## Phase -1: Constitutional Gates

      ### Article I: Library-First (Pass/Fail)
      - [ ] Feature designed as standalone library?
      - [ ] Clear module boundaries?

      ### Article III: Test-First (Pass/Fail)
      - [ ] TDD workflow planned?
      - [ ] Tests before implementation?

      ### Article VII: Simplicity (Pass/Fail)
      - [ ] Using ≤3 projects?
      - [ ] No future-proofing?
      - [ ] No speculative features?

      ### Article VIII: Anti-Abstraction (Pass/Fail)
      - [ ] Using framework directly?
      - [ ] No unnecessary wrappers?

      ### Article IX: SDD (Pass/Fail)
      - [ ] Spec exists and complete?
      - [ ] Tech choices justified?
      ```

      **If ANY gate fails**: Document in Complexity Tracking section with justification

   c. **Phase 0: Research** (if NEEDS CLARIFICATION exists):
      - For each unknown → research task
      - For each dependency → best practices
      - Generate `research.md` with:
        ```markdown
        ## Decision: [what was chosen]
        **Rationale**: [why chosen]
        **Alternatives Considered**: [what else evaluated]
        ```

   d. **Phase 1: Design & Contracts**:
      - Extract entities from spec → `data-model.md`
      - Generate API contracts from functional requirements → `contracts/`
      - Create quickstart scenarios → `quickstart.md`
      - Update agent context (add new tech to CLAUDE.md if needed)

   e. **Project Structure** (choose based on project type):
      ```
      # Single project (DEFAULT)
      src/, tests/

      # Web application (frontend + backend detected)
      backend/src/, frontend/src/

      # Mobile + API (iOS/Android detected)
      api/src/, ios/ or android/
      ```

3. **Write outputs**:
   - `$FEATURE_DIR/plan.md` - Implementation plan
   - `$FEATURE_DIR/research.md` - Research findings (Phase 0)
   - `$FEATURE_DIR/data-model.md` - Entities and relationships
   - `$FEATURE_DIR/contracts/` - API specifications (OpenAPI/GraphQL)
   - `$FEATURE_DIR/quickstart.md` - Validation scenarios

4. **Report completion**:
   - Plan file path
   - Generated artifacts list
   - Constitutional gate results
   - Ready for: `/speckit-tasks`

## Key Rules

- All paths must be absolute
- ERROR on constitutional gate failures unless justified
- Mark all unknowns as "NEEDS CLARIFICATION" initially
- Phase 0 must resolve ALL clarifications before Phase 1
