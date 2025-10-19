---
description: Generate actionable, dependency-ordered tasks from implementation plan
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. **Load context**:
   - Find FEATURE_DIR from current branch
   - **Required**: plan.md (tech stack, structure)
   - **Required**: spec.md (user stories with priorities)
   - **Optional**: data-model.md, contracts/, research.md, quickstart.md

2. **Execute task generation**:

   a. Load plan.md and extract:
      - Tech stack and libraries
      - Project structure
      - Constitutional gate results

   b. Load spec.md and extract:
      - User stories with priorities (P1, P2, P3...)
      - Acceptance scenarios
      - Edge cases

   c. If data-model.md exists:
      - Extract entities
      - Map to user stories

   d. If contracts/ exists:
      - Map endpoints to user stories

   e. Generate tasks organized by user story:
      ```markdown
      ## Phase 1: Setup (Shared Infrastructure)
      - [ ] T001 Create project structure
      - [ ] T002 Initialize dependencies
      - [ ] T003 [P] Configure linting

      ## Phase 2: Foundational (BLOCKING PREREQUISITES)
      - [ ] T004 Setup database schema
      - [ ] T005 [P] Implement auth framework
      - [ ] T006 [P] Setup API routing

      ## Phase 3: User Story 1 (P1) 🎯 MVP
      **Goal**: [Story description]
      **Independent Test**: [How to verify]

      ### Tests (OPTIONAL - only if requested)
      - [ ] T010 [P] [US1] Contract test for [endpoint]
      - [ ] T011 [P] [US1] Integration test for [journey]

      ### Implementation
      - [ ] T012 [P] [US1] Create [Entity1] model in src/models/[file].py
      - [ ] T013 [P] [US1] Create [Entity2] model in src/models/[file].py
      - [ ] T014 [US1] Implement [Service] in src/services/[file].py

      ## Phase 4: User Story 2 (P2)
      ...

      ## Phase N: Polish & Cross-Cutting
      - [ ] TXXX [P] Documentation updates
      - [ ] TXXX Code cleanup
      - [ ] TXXX Performance optimization
      ```

   f. Generate dependency graph:
      ```markdown
      ## Dependencies & Execution Order

      ### Phase Dependencies
      - Setup (Phase 1): No dependencies
      - Foundational (Phase 2): Depends on Setup - BLOCKS all stories
      - User Stories (Phase 3+): All depend on Foundational
        - Stories can proceed in parallel or sequentially by priority

      ### Parallel Opportunities
      - All Setup tasks marked [P]
      - All Foundational tasks marked [P]
      - Once Foundational complete, all stories can start in parallel
      - Models within story marked [P]
      ```

   g. Create parallel execution examples per story

3. **Write tasks.md** using template structure with:
   - Feature name from plan.md
   - Phase 1: Setup tasks
   - Phase 2: Foundational tasks (blocking)
   - Phase 3+: One phase per user story (in priority order)
   - Final Phase: Polish
   - All tasks in checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
   - Dependencies section
   - Parallel execution examples
   - Implementation strategy (MVP first)

4. **Task Generation Rules**:

   **CRITICAL**: Tasks MUST be organized by user story for independent implementation

   **Checklist Format** (REQUIRED):
   ```
   - [ ] [TaskID] [P?] [Story?] Description with file path

   Components:
   1. Checkbox: ALWAYS `- [ ]`
   2. Task ID: T001, T002, T003...
   3. [P] marker: Include ONLY if parallelizable (different files, no dependencies)
   4. [Story] label: REQUIRED for user story tasks only ([US1], [US2], etc.)
   5. Description: Clear action with exact file path
   ```

   **Examples**:
   - ✅ `- [ ] T001 Create project structure`
   - ✅ `- [ ] T005 [P] Implement auth middleware in src/middleware/auth.py`
   - ✅ `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
   - ❌ `- [ ] Create User model` (missing ID and Story)
   - ❌ `T001 [US1] Create model` (missing checkbox)

5. **Report completion**:
   - Path to tasks.md
   - Summary:
     - Total task count
     - Task count per user story
     - Parallel opportunities identified
     - Independent test criteria for each story
     - Suggested MVP scope (typically User Story 1 only)
   - Format validation: Confirm ALL tasks follow checklist format
   - Ready for: `/speckit-implement`

## Task Organization

1. **From User Stories** (PRIMARY):
   - Each story (P1, P2, P3) gets own phase
   - Map all components to their story:
     - Models, Services, Endpoints, UI
     - Tests (if requested)

2. **From Contracts**:
   - Map each endpoint → user story it serves
   - Contract tests [P] before implementation (if requested)

3. **From Data Model**:
   - Map each entity to story(ies) that need it
   - Entity serves multiple stories → earliest story or Setup phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase
   - Foundational/blocking → Foundational phase
   - Story-specific → within that story's phase

## Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each: Tests (optional) → Models → Services → Endpoints → Integration
  - Each phase = complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns
