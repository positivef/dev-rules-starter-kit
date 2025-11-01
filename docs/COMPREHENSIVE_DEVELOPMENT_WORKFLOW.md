# Comprehensive Development Workflow
**Dev Rules Starter Kit - Systematic Implementation Guide**

**Generated**: 2025-10-31
**Strategy**: Systematic
**Depth**: Deep
**Version**: 1.0.0

---

## Executive Summary

This document provides a **complete, systematic workflow** for developing with the Dev Rules Starter Kit - a Constitution-Based Development Framework. It covers all seven architectural layers, constitutional compliance, quality gates, and cross-session management.

**Key Characteristics**:
- **Flexible Adoption**: 4 levels (Minimal → Full) with progressive enhancement
- **Constitution-Centric**: 15 articles (P1-P15) govern all development
- **Evidence-Based**: All executions auto-recorded and trackable
- **Knowledge Asset**: Automatic synchronization to Obsidian (3 seconds)

**Target Audience**: Developers, architects, DevOps engineers, quality assurance teams

---

## Table of Contents

1. [Project Philosophy & Core Concepts](#1-project-philosophy--core-concepts)
2. [7-Layer Architecture Workflow](#2-7-layer-architecture-workflow)
3. [Progressive Adoption Workflow](#3-progressive-adoption-workflow)
4. [Development Lifecycle](#4-development-lifecycle)
5. [Constitutional Compliance Integration](#5-constitutional-compliance-integration)
6. [Testing & Quality Assurance](#6-testing--quality-assurance)
7. [Deployment & Maintenance](#7-deployment--maintenance)
8. [Cross-Session Workflow Management](#8-cross-session-workflow-management)
9. [Multi-Persona Coordination](#9-multi-persona-coordination)
10. [Dependency Maps](#10-dependency-maps)
11. [Quality Gates Reference](#11-quality-gates-reference)

---

## 1. Project Philosophy & Core Concepts

### 1.1 Core Philosophy

**"Executable Documentation"** - Documents are code, code is documentation.

```
Constitution (YAML) → TaskExecutor → Evidence → Knowledge Base
```

**Three Pillars**:
1. **Constitution-Centric**: 15 articles define all development rules
2. **Evidence-Based**: Every execution logged and traceable
3. **Knowledge Asset**: Automatic Obsidian sync in 3 seconds

### 1.2 Key Principles

| Principle | Description | Enforcing Tool |
|-----------|-------------|----------------|
| YAML First (P1) | All tasks as YAML contracts | TaskExecutor |
| Evidence-Based (P2) | Auto-record all executions | TaskExecutor |
| Knowledge Asset (P3) | Auto-sync to Obsidian | ObsidianBridge |
| SOLID (P4) | Code quality enforcement | DeepAnalyzer |
| Security First (P5) | Security gate checks | DeepAnalyzer |
| Quality Gates (P6) | Metric enforcement | TeamStatsAggregator |
| Hallucination Prevention (P7) | Verify all claims | DeepAnalyzer |
| Test First (P8) | TDD approach | pytest |
| Conventional Commits (P9) | Standardized commits | pre-commit |
| Windows UTF-8 (P10) | No emojis in code | System |
| Convergence (P15) | Stop at 80% (good enough) | Validator |

### 1.3 Minimum Viable Constitution

**Non-Negotiables** (even in flexible mode):
1. ✅ Conventional Commits (feat:, fix:, docs:, etc.)
2. ✅ Feature branch workflow (no direct main commits)
3. ✅ PR required for 10+ line changes
4. ❌ NO emojis in production Python code

---

## 2. 7-Layer Architecture Workflow

### 2.1 Architecture Overview

```
Layer 7: Visualization (Streamlit Dashboard)
    ↓
Layer 6: Knowledge Asset (ObsidianBridge, ContextProvider)
    ↓
Layer 5: Evidence Collection (RUNS/evidence/)
    ↓
Layer 4: Optimization (Cache, CriticalFileDetector, WorkerPool)
    ↓
Layer 3: Analysis (DeepAnalyzer, TeamStatsAggregator)
    ↓
Layer 2: Execution (TaskExecutor, ConstitutionalValidator)
    ↓
Layer 1: Constitution (config/constitution.yaml)
```

### 2.2 Layer-by-Layer Implementation Workflow

#### Phase 1: Foundation (Layer 1)

**Objective**: Establish constitutional foundation

**Tasks**:
1. **Review Constitution**
   ```bash
   cat config/constitution.yaml
   ```
   - Understand all 15 articles (P1-P15)
   - Identify mandatory vs optional rules
   - Note enforcement tools for each article

2. **Configure Project-Specific Rules**
   ```yaml
   # config/constitution.yaml (customize if needed)
   articles:
     - id: "P1"
       requirements:
         - desc: "Customize based on team needs"
   ```

3. **Acceptance Criteria**:
   - [ ] All team members understand P1-P15
   - [ ] Constitution reviewed and approved
   - [ ] Custom rules documented (if any)

**Dependencies**: None (foundation layer)
**Duration**: 1-2 hours
**Quality Gate**: Constitutional compliance score ≥ 80

---

#### Phase 2: Execution Layer (Layer 2)

**Objective**: Set up core execution infrastructure

**Tasks**:

1. **Setup Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

3. **Initialize TaskExecutor**
   ```bash
   # Test with example task
   python scripts/task_executor.py TASKS/TEMPLATE.yaml --plan
   python scripts/task_executor.py TASKS/TEMPLATE.yaml
   ```

4. **Setup Constitutional Validator**
   ```bash
   python scripts/constitutional_validator.py --validate
   ```

5. **Acceptance Criteria**:
   - [ ] Virtual environment active
   - [ ] All dependencies installed
   - [ ] Pre-commit hooks functional
   - [ ] TaskExecutor runs successfully
   - [ ] Constitutional validator passes

**Dependencies**: Phase 1 (Constitution)
**Duration**: 30 minutes - 1 hour
**Quality Gate**: All core tools executable

---

#### Phase 3: Analysis Layer (Layer 3)

**Objective**: Enable code quality and security analysis

**Tasks**:

1. **Configure DeepAnalyzer**
   ```bash
   # Run SOLID/security/hallucination checks
   python scripts/deep_analyzer.py
   ```
   - Verifies P4 (SOLID Principles)
   - Verifies P5 (Security First)
   - Verifies P7 (Hallucination Prevention)

2. **Setup TeamStatsAggregator**
   ```bash
   # Calculate quality metrics
   python scripts/team_stats_aggregator.py
   ```
   - Enforces P6 (Quality Gates)
   - Tracks code coverage, complexity, etc.

3. **Configure CriticalFileDetector**
   ```bash
   # Identify high-impact files (impact >0.5)
   python scripts/critical_file_detector.py
   ```

4. **Acceptance Criteria**:
   - [ ] DeepAnalyzer runs without errors
   - [ ] Quality metrics calculated
   - [ ] Critical files identified
   - [ ] Baseline metrics established

**Dependencies**: Phase 2 (Execution Layer)
**Duration**: 1 hour
**Quality Gate**: Analysis score ≥ 70

---

#### Phase 4: Optimization Layer (Layer 4)

**Objective**: Improve performance and efficiency

**Tasks**:

1. **Enable VerificationCache**
   ```python
   # Automatic caching (60% reduction in duplicate checks)
   from verification_cache import VerificationCache
   cache = VerificationCache(ttl=300)  # 5-minute TTL
   ```

2. **Configure WorkerPool**
   ```python
   # Parallel execution for large tasks
   from enhanced_task_executor_v2 import EnhancedTaskExecutorV2
   executor = EnhancedTaskExecutorV2(max_workers=4)
   ```

3. **Optimize Critical Paths**
   - Identify bottlenecks using CriticalFileDetector
   - Apply caching to expensive operations
   - Enable parallel execution where possible

4. **Acceptance Criteria**:
   - [ ] Caching enabled (60% reduction verified)
   - [ ] Parallel execution working
   - [ ] Performance baseline established
   - [ ] Optimization targets met

**Dependencies**: Phase 3 (Analysis Layer)
**Duration**: 2 hours
**Quality Gate**: Performance improvement ≥ 40%

---

#### Phase 5: Evidence Collection (Layer 5)

**Objective**: Automatic evidence collection and tracking

**Tasks**:

1. **Configure Evidence Directory**
   ```bash
   mkdir -p RUNS/evidence
   ```

2. **Enable Auto-Evidence Collection**
   ```yaml
   # In YAML task contracts
   evidence:
     - path: "RUNS/evidence/{{task_id}}/execution_log.txt"
     - path: "RUNS/evidence/{{task_id}}/test_results.xml"
   ```

3. **Setup Evidence Validation**
   - All TaskExecutor runs auto-generate evidence
   - Evidence files include:
     - Execution logs
     - Test results
     - Code analysis reports
     - Performance metrics

4. **Acceptance Criteria**:
   - [ ] Evidence directory structure created
   - [ ] Auto-collection enabled
   - [ ] Evidence files generated correctly
   - [ ] P2 (Evidence-Based) compliance verified

**Dependencies**: Phase 2 (Execution Layer)
**Duration**: 30 minutes
**Quality Gate**: 100% evidence collection rate

---

#### Phase 6: Knowledge Asset (Layer 6)

**Objective**: Automatic knowledge base synchronization

**Tasks**:

1. **Configure Obsidian Integration**
   ```bash
   # .env file
   OBSIDIAN_VAULT_PATH=C:/Users/user/Documents/ObsidianVault
   OBSIDIAN_ENABLED=true
   PROJECT_NAME=YourProjectName
   ```

2. **Install Obsidian Auto-Sync Hook**
   ```bash
   python scripts/install_obsidian_auto_sync.py
   ```
   - Auto-syncs on every commit (if 3+ files changed)
   - Triggers on: feat:, fix:, refactor:, docs: commits

3. **Test Obsidian Bridge**
   ```bash
   python scripts/obsidian_bridge.py test
   python scripts/obsidian_bridge.py sync
   ```

4. **Setup Context Provider**
   ```bash
   python scripts/context_provider.py init
   ```

5. **Acceptance Criteria**:
   - [ ] Obsidian connected and tested
   - [ ] Auto-sync hook installed
   - [ ] Context provider initialized
   - [ ] P3 (Knowledge Asset) compliance verified

**Dependencies**: Phase 5 (Evidence Collection)
**Duration**: 1 hour
**Quality Gate**: Sync time ≤ 3 seconds

---

#### Phase 7: Visualization (Layer 7)

**Objective**: Real-time dashboard for project status

**Tasks**:

1. **Launch Streamlit Dashboard**
   ```bash
   streamlit run scripts/session_dashboard.py
   ```

2. **Configure Dashboard Views**
   - Session status
   - Evidence collection
   - Quality metrics
   - Constitutional compliance

3. **Setup Lock Dashboard** (for multi-session coordination)
   ```bash
   streamlit run scripts/lock_dashboard_streamlit.py
   ```

4. **Acceptance Criteria**:
   - [ ] Dashboard launches successfully
   - [ ] All metrics visible
   - [ ] Real-time updates working
   - [ ] Multi-session coordination functional

**Dependencies**: All previous phases
**Duration**: 30 minutes
**Quality Gate**: Dashboard operational

---

## 3. Progressive Adoption Workflow

### 3.1 Level 0: Minimal (5 minutes)

**Target**: Get started with zero friction

**Steps**:
1. Install commitlint
   ```bash
   npm install -g @commitlint/cli
   ```

2. Start using conventional commits
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug"
   ```

**Benefits**:
- Standardized commit messages
- Better git history
- Automatic changelog generation

**Quality Gate**: 100% conventional commit compliance

---

### 3.2 Level 1: Basic (30 minutes)

**Target**: Add basic code quality tools

**Steps**:
1. Setup Python environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install ruff
   ```

2. Run code quality checks
   ```bash
   ruff check scripts/
   ruff format scripts/
   ```

**Benefits**:
- Automatic code formatting
- Lint error detection
- Code style consistency

**Quality Gate**: Zero linting errors

---

### 3.3 Level 2: Standard (1 week)

**Target**: Full development workflow

**Steps**:
1. Install all dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. Enable pre-commit hooks
   ```bash
   pre-commit install
   ```

3. Use YAML contracts for major changes
   ```bash
   # For 10+ line changes
   python scripts/task_executor.py TASKS/feature.yaml
   ```

**Benefits**:
- Automatic validation on commits
- Evidence-based development
- Quality gates enforced

**Quality Gate**: Constitutional score ≥ 70

---

### 3.4 Level 3: Full (1 month)

**Target**: Complete Constitution compliance

**Steps**:
1. Enable all features
   ```bash
   pip install -e .
   python scripts/context_provider.py init
   ```

2. Configure Obsidian sync
   ```bash
   python scripts/install_obsidian_auto_sync.py
   ```

3. Use all constitutional articles
   - P1-P15 compliance
   - Full evidence collection
   - Automatic knowledge base sync

**Benefits**:
- 377% ROI (as measured)
- Complete traceability
- Knowledge asset building
- Cross-session continuity

**Quality Gate**: Constitutional score ≥ 85, all 15 articles compliant

---

## 4. Development Lifecycle

### 4.1 Feature Development Workflow

```
Idea → Planning → YAML Contract → Implementation → Testing → Review → Merge → Deploy
```

#### Step 1: Feature Planning

**Input**: Feature request or user story

**Actions**:
1. Create feature branch
   ```bash
   git checkout -b feature/user-authentication
   ```

2. Analyze requirements
   - Functional requirements
   - Non-functional requirements (performance, security)
   - Constitutional implications (which articles apply?)

3. Document in YAML contract
   ```yaml
   # TASKS/FEAT-2025-10-31-01.yaml
   task_id: "FEAT-2025-10-31-01"
   title: "User Authentication System"
   description: "Implement JWT-based authentication"

   acceptance_criteria:
     - "User can register with email/password"
     - "User can login and receive JWT token"
     - "Token expires after 24 hours"
     - "All endpoints protected with authentication"

   gates:
     - type: "constitutional"
       articles: ["P4", "P5", "P8"]  # SOLID, Security, Test-First

   commands:
     - id: "01-implement"
       exec:
         cmd: "python"
         args: ["-m", "pytest", "tests/test_auth.py"]

   evidence:
     - path: "RUNS/evidence/FEAT-2025-10-31-01/test_results.xml"
     - path: "RUNS/evidence/FEAT-2025-10-31-01/coverage_report.html"
   ```

**Output**: YAML contract in TASKS/ directory

**Quality Gate**: Contract reviewed and approved

---

#### Step 2: Implementation

**Input**: Approved YAML contract

**Actions**:
1. Preview execution plan
   ```bash
   python scripts/task_executor.py TASKS/FEAT-2025-10-31-01.yaml --plan
   ```

2. Implement feature (TDD approach - P8)
   ```bash
   # Write tests first
   vim tests/test_auth.py

   # Implement feature
   vim scripts/auth_system.py

   # Run tests
   pytest tests/test_auth.py
   ```

3. Apply SOLID principles (P4)
   ```bash
   python scripts/deep_analyzer.py
   ```

4. Security checks (P5)
   ```bash
   # Automatic security gate checks
   python scripts/deep_analyzer.py --security
   ```

5. Execute full contract
   ```bash
   python scripts/task_executor.py TASKS/FEAT-2025-10-31-01.yaml
   ```

**Output**:
- Implemented feature
- Passing tests
- Evidence collected in RUNS/evidence/

**Quality Gate**: All tests pass, SOLID score ≥ 70, security score ≥ 80

---

#### Step 3: Testing & Quality Assurance

**Input**: Implemented feature

**Actions**:
1. Run full test suite
   ```bash
   pytest tests/
   pytest --cov=scripts tests/
   ```

2. Check code coverage (P6 - Quality Gates)
   ```bash
   # Target: ≥90% coverage
   pytest --cov=scripts --cov-report=html tests/
   ```

3. Run quality metrics
   ```bash
   python scripts/team_stats_aggregator.py
   ```

4. Verify constitutional compliance
   ```bash
   python scripts/constitutional_validator.py
   ```

**Output**:
- Test results
- Coverage report
- Quality metrics
- Constitutional compliance score

**Quality Gate**:
- Coverage ≥ 90%
- Constitutional score ≥ 80
- Zero critical security issues

---

#### Step 4: Code Review & Merge

**Input**: Tested feature with evidence

**Actions**:
1. Create pull request
   ```bash
   gh pr create --title "feat: User Authentication System" \
     --body "$(cat TASKS/FEAT-2025-10-31-01.yaml)"
   ```

2. Attach evidence
   - Link to RUNS/evidence/FEAT-2025-10-31-01/
   - Include test results, coverage, metrics

3. Code review checklist:
   - [ ] P1: YAML contract exists and complete
   - [ ] P2: Evidence collected
   - [ ] P4: SOLID principles followed
   - [ ] P5: Security validated
   - [ ] P6: Quality gates passed
   - [ ] P8: Tests written first
   - [ ] P9: Conventional commit used
   - [ ] P10: No emojis in code

4. Merge after approval
   ```bash
   git merge feature/user-authentication
   ```

**Output**: Merged feature in main branch

**Quality Gate**:
- All reviewers approved
- CI/CD pipeline green
- Constitutional score maintained

---

#### Step 5: Deployment

**Input**: Merged feature

**Actions**:
1. Trigger deployment
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Monitor deployment
   - Check logs
   - Verify functionality
   - Monitor performance

3. Auto-sync to knowledge base (P3)
   ```bash
   # Automatic via post-commit hook
   # Manual if needed:
   python scripts/obsidian_bridge.py sync
   ```

**Output**:
- Deployed feature
- Knowledge base updated
- Evidence archived

**Quality Gate**:
- Zero deployment errors
- All health checks pass
- Knowledge base sync ≤ 3 seconds

---

### 4.2 Bug Fix Workflow

```
Bug Report → Diagnosis → Fix → Test → Merge → Deploy
```

#### Quick Fix (< 10 lines)

```bash
# No YAML required for small fixes
git checkout -b fix/null-pointer-error
vim scripts/auth_system.py
pytest tests/test_auth.py
git commit -m "fix: resolve null pointer in auth"
git push
```

**Quality Gate**: Tests pass

---

#### Major Fix (≥ 10 lines)

```yaml
# TASKS/FIX-2025-10-31-01.yaml
task_id: "FIX-2025-10-31-01"
title: "Fix authentication token expiration bug"

gates:
  - type: "constitutional"
    articles: ["P5", "P8"]  # Security + Tests

commands:
  - exec: ["pytest", "tests/test_auth.py"]

evidence:
  - path: "RUNS/evidence/FIX-2025-10-31-01/test_results.xml"
```

```bash
python scripts/task_executor.py TASKS/FIX-2025-10-31-01.yaml
```

**Quality Gate**: All tests pass, security validated

---

### 4.3 Refactoring Workflow

**Objective**: Improve code without changing functionality

**Steps**:

1. Identify refactoring target
   ```bash
   # Find complex functions
   python scripts/deep_analyzer.py --complexity
   ```

2. Create refactoring contract
   ```yaml
   # TASKS/REFACTOR-2025-10-31-01.yaml
   task_id: "REFACTOR-2025-10-31-01"
   title: "Refactor format_report function (60 lines → 9 functions)"

   gates:
     - type: "constitutional"
       articles: ["P4", "P8"]  # SOLID + Tests
   ```

3. Apply refactoring patterns
   - Single Responsibility Principle
   - Extract Method
   - DRY (Don't Repeat Yourself)
   - Pure Functions

4. Verify tests still pass
   ```bash
   pytest tests/
   ```

5. Measure improvement
   ```bash
   python scripts/deep_analyzer.py
   ```

**Quality Gate**:
- All tests pass (no functionality change)
- SOLID score improved
- Complexity reduced

---

## 5. Constitutional Compliance Integration

### 5.1 Article-by-Article Workflow

#### P1: YAML First

**When to apply**: Any task with 3+ steps or new features

**Workflow**:
```bash
# 1. Create YAML contract
vim TASKS/task.yaml

# 2. Preview plan
python scripts/task_executor.py TASKS/task.yaml --plan

# 3. Execute
python scripts/task_executor.py TASKS/task.yaml
```

**Verification**:
```bash
# Check YAML exists for major changes
ls TASKS/*.yaml
```

---

#### P2: Evidence-Based

**When to apply**: Every task execution

**Workflow**:
- Automatic (TaskExecutor collects evidence)
- Evidence stored in RUNS/evidence/{{task_id}}/

**Verification**:
```bash
# Check evidence collected
ls RUNS/evidence/
cat RUNS/evidence/{{task_id}}/execution_log.txt
```

---

#### P3: Knowledge Asset

**When to apply**: After feature completion or major changes

**Workflow**:
```bash
# Automatic sync via post-commit hook
# Manual sync:
python scripts/obsidian_bridge.py sync
```

**Verification**:
```bash
# Check sync status
python scripts/obsidian_bridge.py test
```

---

#### P4: SOLID Principles

**When to apply**: During implementation and code review

**Workflow**:
```bash
# Run SOLID analysis
python scripts/deep_analyzer.py --solid
```

**Verification**:
- Single Responsibility: Each function/class has one purpose
- Open/Closed: Extendable without modification
- Liskov Substitution: Subclasses substitutable
- Interface Segregation: No unused interfaces
- Dependency Inversion: Depend on abstractions

---

#### P5: Security First

**When to apply**: All code changes, especially authentication/authorization

**Workflow**:
```bash
# Run security checks
python scripts/deep_analyzer.py --security
gitleaks detect
```

**Verification**:
- No hardcoded secrets
- Input validation
- SQL injection prevention
- XSS protection
- Authentication/authorization checks

---

#### P6: Quality Gates

**When to apply**: Before merge and deployment

**Workflow**:
```bash
# Calculate quality metrics
python scripts/team_stats_aggregator.py
```

**Verification**:
- Code coverage ≥ 90%
- Complexity score ≤ 10 per function
- No critical issues
- Documentation completeness ≥ 80%

---

#### P7: Hallucination Prevention

**When to apply**: All documentation and claims

**Workflow**:
```bash
# Verify all claims with evidence
python scripts/deep_analyzer.py --hallucination
```

**Verification**:
- All performance claims tested
- All metrics calculated (not estimated)
- All examples executable

---

#### P8: Test First (TDD)

**When to apply**: Feature development and bug fixes

**Workflow**:
```bash
# 1. Write test
vim tests/test_feature.py

# 2. Run test (should fail)
pytest tests/test_feature.py

# 3. Implement feature
vim scripts/feature.py

# 4. Run test (should pass)
pytest tests/test_feature.py
```

**Verification**:
- Test written before implementation
- Test coverage ≥ 90%

---

#### P9: Conventional Commits

**When to apply**: Every commit

**Workflow**:
```bash
git commit -m "feat: add user authentication"
git commit -m "fix: resolve null pointer"
git commit -m "docs: update API documentation"
git commit -m "refactor: extract method"
git commit -m "test: add integration tests"
```

**Verification**:
- Commitlint hook validates automatically

---

#### P10: Windows UTF-8

**When to apply**: All Python code

**Workflow**:
```bash
# Use ASCII alternatives
print("[SUCCESS] Task completed")  # NOT: print("✅ Task completed")
```

**Verification**:
```bash
# Check for emoji violations
python scripts/fix_all_emoji.py --check
```

---

#### P15: Convergence Principle

**When to apply**: Feature development and refactoring

**Philosophy**: Stop at "good enough" (80-95%), not perfect (100%)

**Workflow**:
```bash
# Measure progress
python scripts/team_stats_aggregator.py

# Decision matrix:
# 80-95% → Good enough, stop here
# <80% → Continue improving
# >95% → Diminishing returns, stop
```

**Verification**:
- Quality score ≥ 80
- ROI analysis shows continuing has <150% ROI

---

## 6. Testing & Quality Assurance

### 6.1 Testing Strategy

#### Unit Tests

**Scope**: Individual functions and classes

**Workflow**:
```bash
# Run all unit tests
pytest tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login

# With verbose output
pytest -xvs tests/test_auth.py
```

**Quality Gate**:
- Coverage ≥ 90%
- All tests pass
- Execution time < 5 minutes

---

#### Integration Tests

**Scope**: Multiple components working together

**Workflow**:
```bash
# Run integration tests
pytest tests/test_*_integration.py

# With markers
pytest -m integration tests/
```

**Quality Gate**:
- All integration tests pass
- No flaky tests

---

#### End-to-End Tests

**Scope**: Complete user workflows

**Workflow**:
```bash
# Run E2E tests (if Playwright MCP available)
pytest tests/e2e/
```

**Quality Gate**:
- All critical paths tested
- All tests pass in production-like environment

---

### 6.2 Quality Metrics

#### Code Coverage

```bash
# Generate coverage report
pytest --cov=scripts --cov-report=html tests/

# View report
open htmlcov/index.html
```

**Target**: ≥ 90%

---

#### Code Complexity

```bash
# Analyze complexity
python scripts/deep_analyzer.py --complexity
```

**Target**:
- Cyclomatic complexity ≤ 10 per function
- Cognitive complexity ≤ 15 per function

---

#### SOLID Score

```bash
# Calculate SOLID compliance
python scripts/deep_analyzer.py --solid
```

**Target**: ≥ 70/100

---

#### Security Score

```bash
# Security analysis
python scripts/deep_analyzer.py --security
gitleaks detect
```

**Target**:
- Zero critical vulnerabilities
- Zero hardcoded secrets

---

### 6.3 Quality Gates Matrix

| Gate | Metric | Threshold | Enforcing Tool |
|------|--------|-----------|----------------|
| Coverage | Line coverage | ≥ 90% | pytest |
| Complexity | Cyclomatic | ≤ 10 | DeepAnalyzer |
| SOLID | SOLID score | ≥ 70 | DeepAnalyzer |
| Security | Vulnerabilities | 0 critical | DeepAnalyzer |
| Secrets | Hardcoded secrets | 0 | gitleaks |
| Lint | Ruff errors | 0 | ruff |
| Constitution | Compliance score | ≥ 80 | ConstitutionalValidator |

---

## 7. Deployment & Maintenance

### 7.1 Deployment Workflow

#### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Code coverage ≥ 90%
- [ ] Constitutional score ≥ 80
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped

---

#### Deployment Steps

```bash
# 1. Run full validation
python scripts/constitutional_validator.py --validate

# 2. Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# 3. Push tag
git push origin v1.0.0

# 4. Build and deploy (project-specific)
# Example for Python package:
python -m build
python -m twine upload dist/*
```

---

### 7.2 Maintenance Workflow

#### Regular Maintenance Tasks

**Daily**:
```bash
# Check for dependency updates
pip list --outdated
```

**Weekly**:
```bash
# Run quality metrics
python scripts/team_stats_aggregator.py

# Check constitutional compliance
python scripts/constitutional_validator.py
```

**Monthly**:
```bash
# Review constitution (next_review date in constitution.yaml)
# Update dependencies
pip install --upgrade -r requirements.txt
```

---

#### Handling Technical Debt

```bash
# Identify technical debt
python scripts/deep_analyzer.py --complexity

# Prioritize by impact
python scripts/critical_file_detector.py

# Create refactoring YAML contracts
# See: Section 4.3 Refactoring Workflow
```

---

## 8. Cross-Session Workflow Management

### 8.1 Session Lifecycle

#### Starting a Session

```bash
# 1. Start session
python scripts/session_manager.py start

# 2. Load previous context (if resuming)
python scripts/context_aware_loader.py --resume

# 3. Check current state
python scripts/context_provider.py get-context
```

---

#### During Session

```bash
# Save checkpoint every 30 minutes
python scripts/session_manager.py save

# Before risky operations
python scripts/session_manager.py checkpoint "before-refactor"
```

---

#### Ending a Session

```bash
# 1. Save session state
python scripts/session_manager.py save

# 2. Sync to knowledge base
python scripts/obsidian_bridge.py sync

# 3. Generate session summary
# (automatic via post-commit hook)
```

---

### 8.2 Multi-Session Coordination

**Use Case**: Multiple AI assistants or developers working in parallel

#### Session Roles

- **Session 1**: Frontend development
- **Session 2**: Backend API
- **Session 3**: Testing & QA
- **Session 4**: DevOps & deployment

#### Coordination Workflow

```bash
# Check file locks before editing
python scripts/agent_sync_status.py --files src/auth.py

# Acquire lock
python scripts/agent_sync.py acquire --file src/auth.py --agent session1

# Do work...

# Release lock
python scripts/agent_sync.py release --file src/auth.py --agent session1
```

#### Monitoring Dashboard

```bash
# Launch real-time dashboard
streamlit run scripts/lock_dashboard_streamlit.py
```

Shows:
- Active sessions
- Locked files
- Current tasks
- Conflicts

---

## 9. Multi-Persona Coordination

### 9.1 Persona Roles

#### Architect

**Responsibilities**:
- System design
- Architecture decisions
- Technology selection
- Constitutional rule design

**Tools**:
- Sequential MCP (complex analysis)
- Context7 MCP (framework research)

---

#### Backend Developer

**Responsibilities**:
- API implementation
- Database design
- Business logic
- Performance optimization

**Tools**:
- DeepAnalyzer (SOLID, security)
- pytest (testing)

---

#### Frontend Developer

**Responsibilities**:
- UI implementation
- User experience
- Component design
- Accessibility

**Tools**:
- Magic MCP (UI generation)
- Playwright MCP (E2E testing)

---

#### DevOps Engineer

**Responsibilities**:
- CI/CD pipeline
- Deployment automation
- Infrastructure
- Monitoring

**Tools**:
- TaskExecutor (automation)
- ObsidianBridge (documentation)

---

#### QA Engineer

**Responsibilities**:
- Test strategy
- Quality metrics
- Bug validation
- Performance testing

**Tools**:
- pytest (testing framework)
- TeamStatsAggregator (metrics)
- DeepAnalyzer (analysis)

---

#### Security Engineer

**Responsibilities**:
- Security audits
- Vulnerability scanning
- Compliance validation
- Threat modeling

**Tools**:
- DeepAnalyzer (security checks)
- gitleaks (secret detection)

---

### 9.2 Coordination Matrix

| Task | Primary | Supporting | Tools |
|------|---------|------------|-------|
| Architecture Design | Architect | Backend, Frontend | Sequential, Context7 |
| Feature Implementation | Backend/Frontend | QA | DeepAnalyzer, pytest |
| Security Audit | Security | Backend | DeepAnalyzer, gitleaks |
| Testing Strategy | QA | Backend, Frontend | pytest, Playwright |
| Deployment | DevOps | Backend | TaskExecutor |
| Documentation | All | Technical Writer | ObsidianBridge |

---

## 10. Dependency Maps

### 10.1 Component Dependencies

```
Constitution (Layer 1)
    ↓ (defines rules for)
TaskExecutor (Layer 2)
    ↓ (executes tasks defined in)
YAML Contracts
    ↓ (generates)
Evidence (Layer 5)
    ↓ (syncs to)
Knowledge Base (Layer 6)
```

---

### 10.2 Tool Dependencies

```
Python 3.8+ (required)
    ├── pytest (testing)
    ├── ruff (linting)
    ├── pre-commit (hooks)
    ├── streamlit (dashboard)
    └── pyyaml (YAML parsing)

Optional:
    ├── obsidian (knowledge base)
    ├── gitleaks (secret detection)
    └── MCP servers (Context7, Magic, Sequential, etc.)
```

---

### 10.3 Workflow Dependencies

```
Level 0 (Minimal)
    ↓ (enables)
Level 1 (Basic)
    ↓ (enables)
Level 2 (Standard)
    ↓ (enables)
Level 3 (Full)
```

Each level depends on all previous levels.

---

## 11. Quality Gates Reference

### 11.1 Pre-Commit Gates

**Triggered**: On every commit

**Checks**:
- [ ] Ruff linting (zero errors)
- [ ] Ruff formatting (auto-fix)
- [ ] Commitlint (conventional commits)
- [ ] gitleaks (no secrets)
- [ ] Trailing whitespace (auto-fix)
- [ ] YAML syntax

---

### 11.2 Pre-Push Gates

**Triggered**: Before push to remote

**Checks**:
- [ ] All unit tests pass
- [ ] Code coverage ≥ 90%
- [ ] No TODO in production code (warnings only)

---

### 11.3 Pull Request Gates

**Triggered**: On PR creation

**Checks**:
- [ ] All tests pass (unit + integration)
- [ ] Constitutional validator ≥ 80
- [ ] Code review approved (≥ 1 reviewer)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

---

### 11.4 Deployment Gates

**Triggered**: Before production deployment

**Checks**:
- [ ] All tests pass (unit + integration + E2E)
- [ ] Code coverage ≥ 90%
- [ ] Constitutional score ≥ 85
- [ ] Security scan clean (0 critical)
- [ ] Performance benchmarks pass
- [ ] Smoke tests pass

---

## 12. Troubleshooting

### 12.1 Common Issues

#### Issue: "Virtual environment not activated"

**Symptom**: `which python` shows system Python

**Solution**:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

---

#### Issue: "TaskExecutor fails with validation errors"

**Symptom**: Constitutional validator rejects task

**Solution**:
```bash
# Check which article is failing
python scripts/constitutional_validator.py --verbose

# Review YAML contract
cat TASKS/your-task.yaml

# Fix violations and retry
```

---

#### Issue: "Obsidian sync fails"

**Symptom**: sync time > 3 seconds or connection error

**Solution**:
```bash
# Test connection
python scripts/obsidian_bridge.py test

# Check .env configuration
cat .env | grep OBSIDIAN

# Verify vault path
ls "$OBSIDIAN_VAULT_PATH"
```

---

#### Issue: "Tests fail intermittently"

**Symptom**: Flaky tests

**Solution**:
```bash
# Run test 10 times to reproduce
pytest tests/test_flaky.py --count=10

# Add more determinism
# - Mock time-dependent functions
# - Use fixtures for data
# - Avoid global state
```

---

### 12.2 Performance Issues

#### Slow Test Execution

```bash
# Profile test execution
pytest --durations=10 tests/

# Run tests in parallel
pytest -n auto tests/
```

---

#### High Memory Usage

```bash
# Profile memory
python -m memory_profiler scripts/your_script.py

# Enable caching
# (VerificationCache automatically reduces memory usage)
```

---

## 13. Best Practices

### 13.1 YAML Contract Best Practices

**DO**:
- ✅ Use descriptive task_id (FEAT-YYYY-MM-DD-XX)
- ✅ Include acceptance_criteria
- ✅ Specify evidence paths
- ✅ Add constitutional gates
- ✅ Keep contracts under 100 lines

**DON'T**:
- ❌ Hardcode paths (use {{task_id}})
- ❌ Skip evidence collection
- ❌ Ignore constitutional gates
- ❌ Create duplicate task_ids

---

### 13.2 Testing Best Practices

**DO**:
- ✅ Write tests before implementation (TDD)
- ✅ Use descriptive test names
- ✅ Test edge cases
- ✅ Mock external dependencies
- ✅ Aim for 90%+ coverage

**DON'T**:
- ❌ Test implementation details
- ❌ Write flaky tests
- ❌ Skip integration tests
- ❌ Ignore failing tests

---

### 13.3 Code Quality Best Practices

**DO**:
- ✅ Follow SOLID principles
- ✅ Keep functions small (<50 lines)
- ✅ Use type hints
- ✅ Document complex logic
- ✅ Refactor regularly

**DON'T**:
- ❌ Use emojis in Python code (P10)
- ❌ Hardcode secrets
- ❌ Ignore linting errors
- ❌ Skip code review

---

## 14. Glossary

**Constitution**: Set of 15 articles (P1-P15) governing development

**YAML Contract**: Executable task definition in YAML format

**Evidence**: Automatically collected proof of execution

**Quality Gate**: Threshold that must be met to proceed

**Layer**: One of 7 architectural layers (1-7)

**TaskExecutor**: Core tool that executes YAML contracts

**Constitutional Validator**: Tool that checks P1-P15 compliance

**DeepAnalyzer**: Tool for SOLID, security, hallucination checks

**ObsidianBridge**: Tool for knowledge base synchronization

---

## 15. Quick Reference

### Essential Commands

```bash
# Setup
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Development
python scripts/task_executor.py TASKS/task.yaml
pytest tests/
python scripts/deep_analyzer.py

# Quality
python scripts/constitutional_validator.py
python scripts/team_stats_aggregator.py

# Knowledge
python scripts/obsidian_bridge.py sync

# Session
python scripts/session_manager.py start
python scripts/session_manager.py save
```

---

### Quality Targets

| Metric | Target |
|--------|--------|
| Code Coverage | ≥ 90% |
| Constitutional Score | ≥ 80 |
| SOLID Score | ≥ 70 |
| Security Critical | 0 |
| Cyclomatic Complexity | ≤ 10 |
| Test Execution | < 5 min |
| Obsidian Sync | < 3 sec |

---

## 16. Next Steps

After completing this workflow:

1. **Review**: Read [CONTINUATION_PLAN.md](CONTINUATION_PLAN.md) for next features
2. **Customize**: Adapt constitution to your team's needs
3. **Scale**: Move from Level 0 → Level 3 progressively
4. **Measure**: Track ROI and quality improvements
5. **Iterate**: Review constitution quarterly

---

## 17. Support & Resources

**Documentation**:
- CLAUDE.md - Project overview
- NORTH_STAR.md - Core philosophy
- DEVELOPMENT_RULES.md - Development standards
- config/constitution.yaml - Full constitutional text

**Tools**:
- TaskExecutor - `python scripts/task_executor.py --help`
- Constitutional Validator - `python scripts/constitutional_validator.py --help`
- Deep Analyzer - `python scripts/deep_analyzer.py --help`

**Community**:
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share experiences

---

**End of Comprehensive Development Workflow**

*Generated: 2025-10-31*
*Version: 1.0.0*
*Based on: CLAUDE.md, constitution.yaml*
