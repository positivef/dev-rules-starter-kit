# AI Agent Handoff Protocol - 실전 사용 가이드

## 🚀 Quick Start for Each AI Agent

### 1. Claude Code (claude.ai/code)

#### 세션 시작 시 (작업 받기)

```bash
# 1. 이전 Handoff Report 확인 (필수!)
cat HANDOFF_REPORT.md

# 2. Context Hash 확인
python scripts/context_provider.py print-hash

# 3. Agent Sync Board 확인
python scripts/multi_agent_sync.py list

# 4. Git 상태 확인
git status
git log --oneline -5

# 5. 작업 시작 알림
python scripts/multi_agent_sync.py update-status claude "Working on: {task}" --context-hash {hash}
```

#### 세션 종료 시 (작업 넘기기)

```bash
# 1. 테스트 실행
pytest tests/ -q

# 2. Constitution 검증
python scripts/constitutional_validator.py

# 3. Git Commit (필수!)
git add .
git commit -m "feat(handoff): {작업 내용}"

# 4. Handoff Report 생성 (Constitution 준수 모드)
python scripts/create_handoff_report.py \
  --author "Claude" \
  --summary "구현한 내용 요약" \
  --test-results "pytest: 152/152 passed" \
  --instructions "다음 에이전트가 해야 할 작업"

# 또는 YAML 모드로 실행 (권장)
python scripts/task_executor.py TASKS/HANDOFF-TEMPLATE.yaml
```

---

### 2. Codex CLI (MCP Codex)

#### 세션 시작 시

```python
# Python 스크립트로 자동화
import subprocess
import json

def start_codex_session():
    """Codex 세션 시작 시 Handoff Protocol 실행"""

    # 1. Handoff Report 읽기
    with open("HANDOFF_REPORT.md", "r", encoding="utf-8") as f:
        report = f.read()
        print("[HANDOFF] Previous work summary:")
        print(report[:500])  # 처음 500자만 출력

    # 2. Context Hash 가져오기
    result = subprocess.run(
        ["python", "scripts/context_provider.py", "print-hash"],
        capture_output=True, text=True
    )
    context_hash = result.stdout.strip()
    print(f"[CONTEXT] Hash: {context_hash}")

    # 3. Agent 상태 업데이트
    subprocess.run([
        "python", "scripts/multi_agent_sync.py",
        "update-status", "codex", "Session started",
        "--context-hash", context_hash
    ])

    return context_hash

# 사용
context_hash = start_codex_session()
```

#### 세션 종료 시

```python
def end_codex_session(work_summary, next_steps):
    """Codex 세션 종료 시 Handoff 생성"""

    # 1. 테스트 실행
    test_result = subprocess.run(
        ["pytest", "tests/", "-q"],
        capture_output=True, text=True
    )

    # 2. Handoff Report 생성
    subprocess.run([
        "python", "scripts/create_handoff_report.py",
        "--author", "Codex",
        "--summary", work_summary,
        "--test-results", f"Tests: {test_result.returncode == 0}",
        "--instructions", next_steps
    ])

    print("[HANDOFF] Report generated successfully")

# 사용
end_codex_session(
    work_summary="Implemented user authentication API",
    next_steps="Add refresh token functionality"
)
```

---

### 3. Gemini CLI

#### 세션 시작 시

```python
# gemini_handoff.py
"""Gemini AI를 위한 Handoff Protocol Helper"""

import os
import subprocess
from pathlib import Path

class GeminiHandoff:
    def __init__(self):
        self.agent_name = "Gemini"
        self.context_hash = None

    def receive_handoff(self):
        """이전 에이전트로부터 작업 받기"""
        print("=" * 50)
        print("GEMINI HANDOFF PROTOCOL - RECEIVING")
        print("=" * 50)

        # 1. Report 확인
        if Path("HANDOFF_REPORT.md").exists():
            with open("HANDOFF_REPORT.md", "r", encoding="utf-8") as f:
                report = f.read()

            # Instructions 섹션 추출
            if "## 6. Instructions for Next Agent" in report:
                instructions = report.split("## 6. Instructions")[1].split("##")[0]
                print(f"\n📋 TODO:\n{instructions}")

        # 2. Uncommitted changes 확인
        status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True
        ).stdout

        if status:
            print(f"\n⚠️  Uncommitted changes detected:")
            print(status)
            print("Consider committing or stashing before proceeding.")

        # 3. Context 동기화
        self.sync_context()

        return True

    def sync_context(self):
        """Context Hash 동기화"""
        result = subprocess.run(
            ["python", "scripts/context_provider.py", "print-hash"],
            capture_output=True, text=True
        )
        self.context_hash = result.stdout.strip()
        print(f"\n✅ Context synchronized: {self.context_hash[:8]}...")

        # Agent board 업데이트
        subprocess.run([
            "python", "scripts/multi_agent_sync.py",
            "update-status", self.agent_name,
            "Active - Context synced",
            "--context-hash", self.context_hash
        ])

    def create_handoff(self, summary, instructions, test_passed=True):
        """다음 에이전트를 위한 Handoff 생성"""
        print("=" * 50)
        print("GEMINI HANDOFF PROTOCOL - SENDING")
        print("=" * 50)

        # 1. Constitution 검증
        print("\n🔍 Running Constitution validation...")
        subprocess.run(["python", "scripts/constitutional_validator.py"])

        # 2. Handoff Report 생성
        test_results = "All tests passed" if test_passed else "Some tests failed"

        subprocess.run([
            "python", "scripts/create_handoff_report.py",
            "--author", self.agent_name,
            "--summary", summary,
            "--test-results", test_results,
            "--instructions", instructions
        ])

        print("\n✅ Handoff complete!")
        print("Next agent can start with: gemini_handoff.receive_handoff()")

# 사용 예제
if __name__ == "__main__":
    handoff = GeminiHandoff()

    # 세션 시작
    handoff.receive_handoff()

    # ... 작업 수행 ...

    # 세션 종료
    handoff.create_handoff(
        summary="Fixed encoding issues in Windows environment",
        instructions="Implement test cases for the encoding fix"
    )
```

---

## 📋 Standard Operating Procedure (SOP)

### A. 세션 시작 체크리스트

```markdown
## Handoff Reception Checklist

- [ ] HANDOFF_REPORT.md 읽기 완료
- [ ] Context Hash 확인 완료
- [ ] Git status 확인 (uncommitted changes 체크)
- [ ] 이전 test results 확인
- [ ] Agent sync board 업데이트
- [ ] Instructions 이해 확인
- [ ] 필요시 이전 에이전트 commit log 검토
```

### B. 세션 종료 체크리스트

```markdown
## Handoff Creation Checklist

- [ ] 모든 변경사항 테스트 완료 (pytest)
- [ ] Constitution 검증 통과
- [ ] Git commit 완료 (Conventional Commits)
- [ ] Handoff Report 생성
- [ ] Obsidian 동기화 확인
- [ ] Agent sync board 업데이트
- [ ] 다음 작업 instructions 명확히 작성
```

---

## 🔄 Automated Workflows

### Git Hooks Integration (.git/hooks/pre-push)

```bash
#!/bin/bash
# Automatic handoff on git push

echo "🤝 Generating Handoff Report..."

# Get current agent from git config
AGENT=$(git config user.name)

# Generate handoff
python scripts/create_handoff_report.py \
  --author "$AGENT" \
  --summary "$(git log -1 --pretty=%B)" \
  --test-results "$(pytest tests/ -q 2>&1 | tail -1)" \
  --instructions "Continue from commit $(git rev-parse --short HEAD)"

echo "✅ Handoff Report generated"
```

### VS Code Task (.vscode/tasks.json)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Handoff Session",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/scripts/multi_agent_sync.py",
        "update-status",
        "${input:agentName}",
        "Session started",
        "--context-hash",
        "$(python scripts/context_provider.py print-hash)"
      ],
      "problemMatcher": []
    },
    {
      "label": "Create Handoff",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/scripts/task_executor.py",
        "TASKS/HANDOFF-TEMPLATE.yaml"
      ],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "agentName",
      "type": "pickString",
      "description": "Select your AI agent",
      "options": ["Claude", "Codex", "Gemini"]
    }
  ]
}
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Context Hash Mismatch
```bash
# Force context refresh
python scripts/context_provider.py save-snapshot --force
python scripts/context_provider.py restore-snapshot
```

#### 2. Obsidian Sync Failed
```bash
# Manual sync
python scripts/obsidian_bridge.py --file HANDOFF_REPORT.md --type handoff
```

#### 3. Git Conflicts
```bash
# Safe merge strategy
git stash
git pull --rebase
git stash pop
# Resolve conflicts, then create handoff
```

---

## 📊 Metrics & Monitoring

### Handoff Quality Metrics

```python
# scripts/handoff_metrics.py
def analyze_handoff_quality():
    """Handoff 품질 메트릭 분석"""
    metrics = {
        "total_handoffs": len(list(Path("RUNS/handoffs").glob("*.md"))),
        "obsidian_synced": check_obsidian_sync(),
        "avg_context_stability": calculate_context_stability(),
        "constitution_compliance": check_constitution_compliance()
    }
    return metrics
```

### Dashboard Integration

Streamlit dashboard (`streamlit_app.py`)에 Handoff 섹션 추가:
- Recent handoffs
- Agent activity timeline
- Context hash history
- Handoff success rate

---

## 🎯 Best Practices

1. **Always Read Previous Handoff**: 이전 작업 컨텍스트 없이 시작하지 말 것
2. **Commit Before Handoff**: Uncommitted changes는 혼란 초래
3. **Clear Instructions**: 다음 에이전트를 위한 명확한 지시사항
4. **Test Everything**: 실패한 테스트와 함께 handoff 금지
5. **Use YAML Mode**: TaskExecutor 통합으로 Constitution 준수

---

## 📚 References

- [AI_HANDOFF_PROTOCOL.md](AI_HANDOFF_PROTOCOL.md) - 프로토콜 상세
- [config/constitution.yaml](../config/constitution.yaml) - Constitution 조항
- [TASKS/HANDOFF-TEMPLATE.yaml](../TASKS/HANDOFF-TEMPLATE.yaml) - YAML 템플릿
