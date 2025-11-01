# Beginner Developer Guide - Dev Rules Starter Kit

**Target**: 초보 개발자 (0-2년차)
**Goal**: Constitution-Based Development를 단계별로 안전하게 학습
**Time**: 8주 프로그램 (주당 5-10시간)

---

## 🎯 이 가이드가 필요한 사람

- [ ] Git은 알지만 workflow는 자신 없는 사람
- [ ] Python은 쓰지만 품질 관리는 처음인 사람
- [ ] 테스트 작성이 두려운 사람
- [ ] "YAML이 뭔데?" 하는 사람
- [ ] "Constitution? 그게 먹는 건가요?" 하는 사람

**괜찮습니다! 이 가이드는 당신을 위한 것입니다.**

---

## 📚 전제 조건

### 필수
- [ ] Python 3.9+ 설치
- [ ] Git 기본 명령어 (clone, add, commit, push)
- [ ] VS Code 또는 텍스트 에디터

### 선택 (있으면 좋음)
- [ ] GitHub 계정
- [ ] 터미널/커맨드라인 기본 지식
- [ ] Markdown 문법

---

## 🚀 8주 학습 로드맵

### Week 1-2: Git Workflow 마스터 (Phase 0)

**목표**: Conventional Commits + Feature Branch 습관화

#### Day 1-2: Git Workflow 이해
```bash
# 1. Repository clone
git clone https://github.com/your-username/dev-rules-starter-kit.git
cd dev-rules-starter-kit

# 2. 상태 확인 (항상!)
git status
git branch

# 3. Feature branch 생성
git checkout -b feature/my-first-feature

# 4. 코드 작성 (예: README 수정)
echo "# My Changes" >> README.md

# 5. Commit
git add README.md
git commit -m "docs: update README with my changes"

# 6. Push
git push -u origin feature/my-first-feature
```

**연습 과제**:
- [ ] Feature branch 10개 생성해보기
- [ ] Conventional Commits 20개 작성하기
- [ ] 다음 타입 모두 사용해보기: feat, fix, docs, style, refactor, test

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples**:
```bash
# Good
git commit -m "feat(auth): add JWT authentication"
git commit -m "fix(api): resolve timeout issue in user endpoint"
git commit -m "docs(readme): add installation instructions"

# Bad
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Common Mistakes**:
```bash
# ❌ Wrong: Working on main branch
git branch  # Shows: * main
# Do this instead:
git checkout -b feature/my-feature

# ❌ Wrong: Vague commit message
git commit -m "update code"
# Do this instead:
git commit -m "feat(user): add email validation to registration form"

# ❌ Wrong: Mixing multiple changes
git add .  # 10 files changed with different purposes
# Do this instead:
git add file1.py file2.py  # Related changes only
git commit -m "feat(auth): add login endpoint"
```

#### Day 3-5: Pre-commit Hooks

```bash
# 1. Install pre-commit
pip install pre-commit

# 2. Install hooks
pre-commit install

# 3. Test
git add .
git commit -m "test: verify pre-commit hooks"
# Pre-commit will check your code automatically!
```

**What happens**:
- ✅ Ruff checks your Python code
- ✅ Commit message format validated
- ✅ No secrets in code (gitleaks)
- ✅ YAML/JSON syntax check

#### Week 1-2 Checkpoint

**Quiz**:
1. What command checks current branch?
2. Should you commit directly to main?
3. What's the format for a feature commit?

**Hands-on**:
- [ ] Create 5 feature branches
- [ ] Make 10 conventional commits
- [ ] Fix 3 pre-commit failures
- [ ] Understand why each failure happened

**Success Criteria**:
- ✅ No commits on main branch
- ✅ 100% conventional commits
- ✅ Pre-commit hooks passing

---

### Week 3-4: Virtual Environment & Dependencies (Phase 1 Prep)

**Goal**: Understand Python environments and dependencies

#### Day 1-3: Virtual Environment

```bash
# 1. Create venv
python -m venv .venv

# 2. Activate
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# 3. Verify
which python  # Should show .venv path (Linux/Mac)
where python  # Should show .venv path (Windows)

# 4. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Verify installation
pip list | grep ruff
pip list | grep pytest
```

**Common Mistakes**:
```bash
# ❌ Wrong: Installing without venv
pip install ruff  # Installs to system Python!

# ✅ Right: Always activate venv first
.venv\Scripts\activate
pip install ruff  # Installs to venv
```

#### Day 4-7: Understanding Dependencies

```bash
# Read requirements.txt
cat requirements.txt

# Understand what each package does:
# - ruff: Python linter (quality check)
# - pytest: Testing framework
# - pyyaml: YAML file handling
# - etc.

# Try running tools
ruff check scripts/
pytest tests/ -v
```

**Exercise**:
1. Install each requirement manually
2. Understand what it does
3. Run its basic command

#### Week 3-4 Checkpoint

**Quiz**:
1. Why do we use virtual environments?
2. How to check if venv is activated?
3. What does ruff do?

**Hands-on**:
- [ ] Create and activate venv 5 times
- [ ] Install all dependencies
- [ ] Run ruff on sample code
- [ ] Run pytest on sample tests

**Success Criteria**:
- ✅ venv always activated before pip install
- ✅ All dependencies installed successfully
- ✅ Can run ruff and pytest

---

### Week 5-6: YAML & TaskExecutor (Phase 1 Core)

**Goal**: Write first YAML contract and execute with TaskExecutor

#### Day 1-2: YAML Basics

**Learn YAML syntax**:
```yaml
# This is a comment

# Key-value pairs
task_id: "TASK-001"
title: "My first task"

# Lists
gates:
  - "quality"
  - "security"

# Nested objects
metadata:
  author: "John Doe"
  date: "2025-10-31"
```

**Practice**:
```bash
# Create practice YAML
cat > practice.yaml << 'EOF'
name: "Practice Task"
description: "Learning YAML syntax"
steps:
  - "Read YAML tutorial"
  - "Write YAML file"
  - "Validate YAML syntax"
EOF

# Validate
python -c "import yaml; yaml.safe_load(open('practice.yaml'))"
```

#### Day 3-5: First YAML Contract

**Template**:
```yaml
# TASKS/BEGINNER-001.yaml
task_id: "BEGINNER-001"
title: "My First YAML Task"
description: "Learn TaskExecutor by creating a simple task"

gates:
  - type: "constitutional"
    articles: ["P1"]  # YAML First

commands:
  - exec: ["echo", "Hello from TaskExecutor!"]
  - exec: ["python", "--version"]
```

**Execute**:
```bash
# 1. Preview (dry-run)
python scripts/task_executor.py TASKS/BEGINNER-001.yaml --plan

# 2. Execute
python scripts/task_executor.py TASKS/BEGINNER-001.yaml

# 3. Check evidence
ls RUNS/evidence/
cat RUNS/evidence/BEGINNER-001_*.json
```

**What happens automatically**:
1. TaskExecutor reads YAML
2. Validates against P1 (YAML First)
3. Executes commands
4. Collects evidence to `RUNS/evidence/`
5. Syncs to Obsidian (if enabled)

#### Day 6-7: Real Task Example

**Scenario**: Add a new Python function

```yaml
# TASKS/BEGINNER-002.yaml
task_id: "BEGINNER-002"
title: "Add hello world function"
description: "Create a simple Python function with test"

gates:
  - type: "constitutional"
    articles: ["P4", "P8"]  # SOLID + Test First

  - type: "quality"
    min_score: 7.0

commands:
  # 1. Create function
  - exec: ["python", "-c", "
      def hello(name):
          return f'Hello, {name}!'

      # Save to file
      with open('scripts/hello.py', 'w') as f:
          f.write('def hello(name):\\n')
          f.write('    return f\\'Hello, {name}!\\'\\n')
    "]

  # 2. Create test
  - exec: ["python", "-c", "
      with open('tests/test_hello.py', 'w') as f:
          f.write('from scripts.hello import hello\\n\\n')
          f.write('def test_hello():\\n')
          f.write('    assert hello(\\'World\\') == \\'Hello, World!\\'\\n')
    "]

  # 3. Run test
  - exec: ["pytest", "tests/test_hello.py", "-v"]

  # 4. Quality check
  - exec: ["ruff", "check", "scripts/hello.py"]
```

**Execute and learn**:
```bash
# Execute
python scripts/task_executor.py TASKS/BEGINNER-002.yaml

# Automatic checks:
# ✅ P4 (SOLID) - DeepAnalyzer checks code quality
# ✅ P8 (Test First) - Pytest runs
# ✅ Quality Gate - Min score 7.0
# ✅ Evidence collected
# ✅ Obsidian synced
```

#### Week 5-6 Checkpoint

**Quiz**:
1. What is YAML used for in this project?
2. What's the difference between --plan and normal execution?
3. Where is evidence stored?

**Hands-on**:
- [ ] Write 3 YAML contracts
- [ ] Execute with TaskExecutor
- [ ] Check evidence files
- [ ] Understand automatic checks

**Success Criteria**:
- ✅ Can write valid YAML
- ✅ TaskExecutor executes successfully
- ✅ Evidence collected in RUNS/evidence/
- ✅ Understand P1, P4, P8

---

### Week 7-8: Constitution Experience (Phase 1 Complete)

**Goal**: Experience all core Constitutional articles

#### Day 1-2: P2 (Evidence-Based Development)

**Learn**: Every execution is automatically recorded

```bash
# Execute any task
python scripts/task_executor.py TASKS/BEGINNER-002.yaml

# Evidence is automatically collected
ls RUNS/evidence/

# View evidence
cat RUNS/evidence/BEGINNER-002_*.json

# Evidence contains:
# - Command executed
# - Exit code
# - Stdout/stderr
# - Timestamp
# - Duration
```

**Exercise**:
- [ ] Execute 5 different tasks
- [ ] Find evidence for each
- [ ] Understand evidence format

#### Day 3-4: P3 (Knowledge Asset)

**Learn**: Obsidian auto-sync

```bash
# 1. Set up Obsidian (if not done)
# Edit .env
echo 'OBSIDIAN_VAULT_PATH="C:/Users/you/Documents/ObsidianVault"' >> .env
echo 'OBSIDIAN_ENABLED=true' >> .env

# 2. Test sync
python scripts/obsidian_bridge.py test

# 3. Execute task
python scripts/task_executor.py TASKS/BEGINNER-002.yaml

# 4. Check Obsidian
# Open: ObsidianVault/개발일지/2025-10-31_*.md
# Task is automatically documented!
```

**Exercise**:
- [ ] Enable Obsidian sync
- [ ] Execute 3 tasks
- [ ] Find them in Obsidian
- [ ] Understand knowledge structure

#### Day 5-7: P4/P5/P6/P7 (Quality Gates)

**Learn**: Automatic quality checks

```bash
# Create a task with quality issues
cat > TASKS/BEGINNER-003.yaml << 'EOF'
task_id: "BEGINNER-003"
title: "Test Quality Gates"

gates:
  - type: "constitutional"
    articles: ["P4", "P5", "P6", "P7"]

  - type: "quality"
    min_score: 7.0

commands:
  - exec: ["python", "-c", "
      # Bad code for learning
      def bad_function(x,y,z,a,b,c):  # Too many params (P4 violation)
          password = 'hardcoded123'  # Security issue (P5)
          return x+y+z+a+b+c
    "]
EOF

# Execute
python scripts/task_executor.py TASKS/BEGINNER-003.yaml

# Will FAIL with detailed report:
# ❌ P4 (SOLID): Function has too many parameters
# ❌ P5 (Security): Hardcoded password detected
# ❌ P6 (Quality): Score 4.2 < 7.0
```

**Exercise**:
- [ ] Create task with quality issues
- [ ] See it fail
- [ ] Fix the issues
- [ ] See it pass
- [ ] Understand each Constitutional article

#### Week 7-8 Checkpoint

**Quiz**:
1. What is P2 and why is it important?
2. How does Obsidian sync work?
3. What do P4/P5/P6/P7 check?

**Hands-on**:
- [ ] Execute tasks with evidence collection
- [ ] Sync to Obsidian successfully
- [ ] Trigger and fix quality gate failures
- [ ] Understand all Phase 1 articles

**Success Criteria**:
- ✅ Evidence collected for all tasks
- ✅ Obsidian sync working
- ✅ Can fix P4/P5/P6/P7 violations
- ✅ Quality score >= 7.0

---

## 🚨 Common Mistakes & Solutions

### Mistake 1: Working on main branch

**Symptom**:
```bash
git branch
# * main  ← You're on main!
```

**Why it's bad**:
- Direct commits to main are dangerous
- No code review opportunity
- Hard to rollback

**Solution**:
```bash
# ALWAYS create feature branch
git checkout -b feature/my-work

# Verify
git branch
# * feature/my-work  ← Good!
#   main
```

### Mistake 2: Forgetting to activate venv

**Symptom**:
```bash
which python
# /usr/bin/python  ← System Python!
```

**Why it's bad**:
- Dependencies install to system
- Version conflicts
- Hard to clean up

**Solution**:
```bash
# ALWAYS activate venv first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Verify
which python
# /path/to/project/.venv/bin/python  ← Good!
```

### Mistake 3: Vague commit messages

**Bad examples**:
```bash
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Why it's bad**:
- Can't understand what changed
- Hard to track features
- No context for rollback

**Solution**:
```bash
# Be specific!
git commit -m "feat(auth): add JWT token validation"
git commit -m "fix(api): resolve timeout in user endpoint"
git commit -m "docs(readme): add installation guide"
```

### Mistake 4: Not reading error messages

**Symptom**:
```bash
python scripts/task_executor.py TASKS/my-task.yaml
# [ERROR] ... long error message ...
# "I don't know what's wrong!"
```

**Solution**:
1. **READ the error message** (seriously!)
2. Look for key information:
   - What failed? (command, validation, etc.)
   - Why? (specific error)
   - Where? (file, line number)
3. Check evidence: `cat RUNS/evidence/my-task_*.json`
4. Fix the specific issue
5. Re-run

### Mistake 5: Skipping --plan

**Bad**:
```bash
# Directly execute without preview
python scripts/task_executor.py TASKS/complex-task.yaml
# Oops! It did something unexpected!
```

**Good**:
```bash
# ALWAYS preview first
python scripts/task_executor.py TASKS/complex-task.yaml --plan
# Review the plan
# If looks good, execute:
python scripts/task_executor.py TASKS/complex-task.yaml
```

### Mistake 6: Using emojis in Python code (Windows)

**Bad** (will crash on Windows!):
```python
# ❌ Windows encoding error!
print("✅ Task completed")
status = "🚀 Deploying"
```

**Good**:
```python
# ✅ Works everywhere
print("[SUCCESS] Task completed")
status = "[DEPLOY] Deploying"
```

**P10 Rule**: No emojis in Python/YAML/Shell code!

### Mistake 7: Ignoring quality gates

**Bad**:
```bash
# Quality gate failed: score 4.2 < 7.0
# "Whatever, I'll just skip it"
```

**Good**:
```bash
# Quality gate failed: score 4.2 < 7.0
# 1. Check RUNS/evidence/ for details
# 2. Fix the issues:
#    - Reduce function complexity
#    - Add docstrings
#    - Fix security issues
# 3. Re-run
# 4. Pass with score >= 7.0
```

---

## 📋 Cheat Sheet

### Git Workflow
```bash
# Start new feature
git checkout -b feature/my-feature

# Check status
git status && git branch

# Commit
git add <files>
git commit -m "type(scope): description"

# Push
git push -u origin feature/my-feature
```

### Python Environment
```bash
# Activate venv (ALWAYS!)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install deps
pip install -r requirements.txt

# Run tools
ruff check scripts/
pytest tests/
```

### TaskExecutor
```bash
# Preview
python scripts/task_executor.py TASKS/my-task.yaml --plan

# Execute
python scripts/task_executor.py TASKS/my-task.yaml

# Check evidence
cat RUNS/evidence/my-task_*.json
```

### Debugging
```bash
# Check evidence
ls RUNS/evidence/

# View logs
cat RUNS/evidence/<task-id>_*.json

# Test Obsidian
python scripts/obsidian_bridge.py test

# Validate YAML
python -c "import yaml; yaml.safe_load(open('TASKS/my-task.yaml'))"
```

---

## 🎓 Graduation Criteria

After 8 weeks, you should be able to:

- [ ] Create feature branches without thinking
- [ ] Write conventional commits naturally
- [ ] Activate venv automatically
- [ ] Write valid YAML contracts
- [ ] Use TaskExecutor confidently
- [ ] Understand evidence collection
- [ ] Fix quality gate failures
- [ ] Explain P1-P8 articles

**Ready for Phase 2**: Strategy B productivity tools!

---

## 📚 Next Steps

### After completing this guide:

1. **Read CLAUDE.md** - Complete project guide
2. **Read NORTH_STAR.md** - Understand project philosophy
3. **Try Phase 2 tools** - Strategy B productivity boost
4. **Join community** - Share your learnings

### Resources:

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [YAML Tutorial](https://yaml.org/spec/1.2/spec.html)

---

## 🆘 Getting Help

### When stuck:

1. **Check evidence**: `RUNS/evidence/` has detailed logs
2. **Read error messages**: They usually tell you what's wrong
3. **Review docs**: `CLAUDE.md`, `NORTH_STAR.md`
4. **Ask questions**: Create GitHub issue with:
   - What you tried
   - Error message
   - Evidence file content

### Common questions:

**Q: What if I committed to main by accident?**
```bash
# Reset the commit (careful!)
git reset HEAD~1
# Create feature branch
git checkout -b feature/my-feature
# Re-commit
git add .
git commit -m "type(scope): description"
```

**Q: How do I know if venv is activated?**
```bash
# Prompt shows (.venv)
(.venv) $

# Or check path
which python  # Should show .venv/
```

**Q: What if TaskExecutor fails?**
```bash
# 1. Check evidence
cat RUNS/evidence/<task-id>_*.json

# 2. Look for specific error
# 3. Fix the issue
# 4. Re-run
```

---

**Good luck!** 🎉

Remember: **Everyone was a beginner once. Take it slow, make mistakes, learn, and grow!**
