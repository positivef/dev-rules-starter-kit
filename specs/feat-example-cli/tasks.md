# Tasks: Simple CLI Calculator

**Created**: 2025-10-20
**Feature**: feat-example-cli
**Total Tasks**: 15

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create project directory structure in simple-calc/
- [X] T002 [P] Create __init__.py files in src/ and tests/
- [X] T003 [P] Create setup.py with package configuration

## Phase 2: Foundational (BLOCKING PREREQUISITES)

⚠️ **CRITICAL**: No user story work can begin until this phase complete

- [X] T004 Create requirements.txt with pytest dependency
- [X] T005 [P] Install development dependencies
- [X] T006 [P] Setup pytest configuration in pytest.ini

## Phase 3: User Story 1 (P1) [MVP]

**Goal**: Basic arithmetic operations (add, subtract)
**Independent Test**: User can perform addition and subtraction from command line

### Tests (Write tests FIRST - TDD)

- [X] T010 [P] [US1] Write test for Calculator.add() in tests/test_calculator.py
- [X] T011 [P] [US1] Write test for Calculator.subtract() in tests/test_calculator.py
- [X] T012 [P] [US1] Write test for division by zero in tests/test_calculator.py
- [X] T013 [US1] Write integration test for CLI in tests/test_cli.py

### Implementation

- [X] T014 [P] [US1] Create Calculator class in src/calculator.py
- [X] T015 [P] [US1] Implement add() method in src/calculator.py
- [X] T016 [P] [US1] Implement subtract() method in src/calculator.py
- [X] T017 [US1] Create CLI interface in src/cli.py
- [X] T018 [US1] Implement argparse setup in src/cli.py
- [X] T019 [US1] Connect CLI to Calculator.add() and Calculator.subtract()

## Phase 4: User Story 2 (P2)

**Goal**: Advanced operations (multiply, divide)
**Independent Test**: User can perform multiplication and division

### Tests

- [X] T020 [P] [US2] Write test for Calculator.multiply() in tests/test_calculator.py
- [X] T021 [P] [US2] Write test for Calculator.divide() in tests/test_calculator.py

### Implementation

- [X] T022 [P] [US2] Implement multiply() method in src/calculator.py
- [X] T023 [P] [US2] Implement divide() method with zero check in src/calculator.py
- [X] T024 [US2] Add multiply and divide to CLI interface in src/cli.py

## Phase 5: Polish & Cross-Cutting

- [X] T030 [P] Create README.md with usage examples
- [X] T031 [P] Add help text to CLI with --help flag
- [X] T032 Run final test suite and verify 100% pass rate

## Dependencies & Execution Order

### Phase Dependencies
- Setup (Phase 1): No dependencies
- Foundational (Phase 2): Depends on Setup - **BLOCKS all stories**
- User Story 1 (Phase 3): Depends on Foundational
- User Story 2 (Phase 4): Depends on User Story 1 (uses same Calculator class)
- Polish (Phase 5): Depends on all user stories

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T005, T006 can run in parallel (different operations)

**Phase 3 (User Story 1)**:
- Tests: T010, T011, T012 can run in parallel (different test methods)
- Implementation: T014, T015, T016 can run in parallel (independent methods)

**Phase 4 (User Story 2)**:
- Tests: T020, T021 can run in parallel (different test methods)
- Implementation: T022, T023 can run in parallel (independent methods)

**Phase 5 (Polish)**:
- T030, T031 can run in parallel (different files)

## MVP Strategy

**Minimum Viable Product**: Phase 1-3 only
- Setup + Foundational + User Story 1
- **Result**: Working CLI with add/subtract operations
- **Test after**: Verify `calc add 5 3` and `calc subtract 10 4` work

**Full Release**: All phases
- Includes multiply/divide operations
- Complete documentation

## Execution Example

```bash
# Run with EnhancedTaskExecutor
python scripts/enhanced_task_executor.py specs/feat-example-cli/tasks.md

# Expected flow:
# 1. Constitutional validation: ✅ ALL PASS
# 2. Setup Phase: Create structure
# 3. Foundational Phase: Install deps
# 4. User Story 1 Phase:
#    - Write tests (T010-T013 parallel)
#    - Implement features (T014-T016 parallel)
#    - Connect CLI (T017-T019 sequential)
# 5. Verify tests pass
# 6. Mark tasks [X] in this file
# 7. Sync to Obsidian
```

---

**Ready for execution**: `python scripts/enhanced_task_executor.py specs/feat-example-cli/tasks.md`
