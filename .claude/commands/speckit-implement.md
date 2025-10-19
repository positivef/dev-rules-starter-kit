---
description: Execute implementation plan by processing all tasks with constitutional compliance
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. **Find FEATURE_DIR** from current git branch

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files
   - Count: Total items, Completed (`[X]`), Incomplete (`[ ]`)
   - Create status table:
     ```
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | requirements.md | 12 | 12 | 0 | ✓ PASS |
     | security.md | 8 | 5 | 3 | ✗ FAIL |
     ```
   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists incomplete

   - **If any checklist incomplete**:
     - Display table with incomplete counts
     - **STOP** and ask: "Some checklists are incomplete. Proceed anyway? (yes/no)"
     - Wait for user response
     - If "no"/"wait"/"stop": halt execution
     - If "yes"/"proceed"/"continue": continue to step 3

   - **If all checklists complete**:
     - Display table showing all passed
     - Automatically proceed to step 3

3. **Load implementation context**:
   - **REQUIRED**: tasks.md (complete task list)
   - **REQUIRED**: plan.md (tech stack, architecture, file structure)
   - **IF EXISTS**: data-model.md, contracts/, research.md, quickstart.md

4. **Project Setup Verification**:

   **Detection & Creation Logic**:
   - Check if git repo: `git rev-parse --git-dir 2>/dev/null` → create .gitignore
   - Check if Dockerfile exists → create .dockerignore
   - Check if .eslintrc* exists → create .eslintignore
   - Check if .prettierrc* exists → create .prettierignore
   - Check if terraform files (*.tf) → create .terraformignore

   **Common Patterns by Technology** (from plan.md):
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`
   - **Node.js**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

5. **Parse tasks.md structure**:
   - Extract task phases (Setup, Tests, Core, Integration, Polish)
   - Identify dependencies (Sequential vs parallel)
   - Extract task details (ID, description, file paths, [P] markers)
   - Understand execution flow

6. **Execute implementation**:

   **Phase-by-phase execution**:
   - Complete each phase before moving to next
   - Respect dependencies (sequential tasks in order, parallel tasks [P] together)
   - Follow TDD approach (test tasks before implementation tasks)
   - File-based coordination (same file tasks = sequential)
   - Validation checkpoints at phase completion

   **Execution order**:
   a. **Setup first**: Initialize structure, dependencies, config
   b. **Tests before code**: Write tests for contracts, entities, integration (if requested)
   c. **Core development**: Implement models, services, CLI, endpoints
   d. **Integration work**: Database, middleware, logging, external services
   e. **Polish**: Unit tests (optional), performance, documentation

7. **Progress tracking**:
   - Report progress after each completed task
   - Halt if any non-parallel task fails
   - For parallel tasks [P], continue with successful, report failed
   - Provide clear error messages with context
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT**: Mark completed tasks as [X] in tasks.md file

8. **Constitutional Compliance During Implementation**:

   For each task, verify compliance with constitution articles:
   - Article I: Library-first (modular design)
   - Article II: CLI interface (text I/O)
   - Article III: Test-first (TDD workflow)
   - Article V: Windows encoding (no emoji in code)
   - Article VI: Observability (structured logging)
   - Article VII: Simplicity (no over-engineering)
   - Article VIII: Anti-abstraction (direct framework use)

   **If violation detected**:
   - Document in `FEATURE_DIR/compliance-notes.md`
   - Get user approval to proceed or fix

9. **Completion validation**:
   - Verify all required tasks completed
   - Check implemented features match spec.md
   - Validate tests pass and coverage meets requirements (≥90%)
   - Confirm implementation follows plan.md
   - Run constitutional compliance check
   - Report final status with summary

## Implementation Rules

- **Setup first**: Initialize before any development
- **Tests before code**: TDD mandatory (Article III)
- **Core development**: Follow task order in tasks.md
- **Integration work**: Connect all components
- **Polish last**: Final optimizations and documentation

## Error Handling

- Halt execution if non-parallel task fails
- Continue with successful parallel tasks, report failures
- Provide clear error messages with context
- Suggest next steps (e.g., "Fix test failure in T012 before proceeding")

## Completion Criteria

- [ ] All required tasks marked [X] in tasks.md
- [ ] All tests pass (≥90% coverage)
- [ ] Implementation matches spec.md
- [ ] Constitutional compliance verified
- [ ] Documentation updated
- [ ] Ready for commit/PR

## Note

This command assumes complete task breakdown exists in tasks.md. If tasks incomplete/missing, suggest running `/speckit-tasks` first.
