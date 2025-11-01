# 🚀 AI Agent 자동 초기화 설정 가이드

## 이제 세션 시작 시 자동으로 HANDOFF_REPORT.md를 읽습니다!

---

## 🤖 Claude Code 설정

### 방법 1: Python 스크립트 실행 (권장)
```bash
# Claude 세션 시작하자마자 실행
python .claude/init.py
```

### 방법 2: Alias 설정
```bash
# .bashrc 또는 .zshrc에 추가
alias claude-init="python .claude/init.py"

# 세션 시작 시
claude-init
```

### 방법 3: VS Code Task 설정
```json
// .vscode/tasks.json에 추가
{
  "label": "Claude Init",
  "type": "shell",
  "command": "python",
  "args": [".claude/init.py"],
  "runOptions": {
    "runOn": "folderOpen"  // 폴더 열 때 자동 실행
  }
}
```

---

## 💻 Codex CLI 설정

### Python 세션에서 자동 실행
```python
# Codex Python 세션 시작 시 첫 명령
>>> from scripts.codex_auto_init import *

# 또는 더 간단하게
>>> exec(open('scripts/codex_auto_init.py').read())

# 이제 자동으로 사용 가능:
# - create_handoff(summary, instructions)
# - get_context_hash()
# - get_instructions()
# - update_status(status)
```

### IPython 자동 시작 설정
```python
# ~/.ipython/profile_default/startup/00-codex-init.py 생성
import sys
sys.path.insert(0, 'scripts')
from codex_auto_init import *
print("✅ Codex Handoff Protocol loaded")
```

---

## 🌟 Gemini 설정

### Python 세션 자동 초기화
```python
# Gemini 세션 시작 시
>>> from scripts.gemini_auto_init import *

# 자동으로 초기화되고 다음 함수들 사용 가능:
# - create_handoff(summary, instructions)
# - analyze()  # 코드베이스 분석
# - verify_code(path)  # Gemini API 검증
# - view_report()  # 전체 리포트 보기
# - session_info()  # 세션 정보
```

### Jupyter Notebook 자동 시작
```python
# 첫 셀에 추가
%load_ext autoreload
%autoreload 2
from scripts.gemini_auto_init import *
```

---

## 🎯 Universal 자동 실행 (모든 Agent)

### 방법 1: 환경 변수 설정
```bash
# .env 파일에 추가
CLAUDE_CODE=1  # Claude 사용 시
CODEX_CLI=1    # Codex 사용 시
GEMINI_AI=1    # Gemini 사용 시

# 그 다음 실행
python scripts/agent_auto_init.py
```

### 방법 2: Git Hook 활용
```bash
# .git/hooks/post-checkout 생성
#!/bin/bash
echo "🤖 AI Agent Auto Initialization"
python scripts/agent_auto_init.py
```

### 방법 3: Shell 함수 (Linux/Mac)
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
function ai-init() {
    echo "Which AI agent? (1: Claude, 2: Codex, 3: Gemini)"
    read choice
    case $choice in
        1) python .claude/init.py ;;
        2) python scripts/codex_auto_init.py ;;
        3) python scripts/gemini_auto_init.py ;;
        *) python scripts/agent_auto_init.py ;;
    esac
}

# 사용
$ ai-init
```

### 방법 4: Windows 배치 파일
```batch
@echo off
REM ai-init.bat 파일 생성
echo AI Agent Auto Initialization
echo 1. Claude
echo 2. Codex
echo 3. Gemini
set /p choice="Select agent (1-3): "

if %choice%==1 python .claude\init.py
if %choice%==2 python scripts\codex_auto_init.py
if %choice%==3 python scripts\gemini_auto_init.py
```

---

## 📊 자동 초기화 시 일어나는 일

1. **배너 표시**: 어떤 Agent인지 표시
2. **Handoff Report 자동 읽기**: HANDOFF_REPORT.md 파싱
3. **Instructions 추출**: 해야 할 작업 명확히 표시
4. **Context 동기화**: Context hash 확인
5. **Agent Board 업데이트**: Multi-agent sync board 갱신
6. **Git 상태 체크**: Uncommitted changes 경고
7. **Quick Commands 표시**: Agent별 유용한 명령어

---

## ✅ 초기화 확인 방법

### 성공적인 초기화 시 출력
```
============================================================
  AI AGENT HANDOFF PROTOCOL - AUTO INITIALIZATION
  Agent: Claude
  Time: 2025-10-29 15:30:00
============================================================

📄 Reading previous handoff report...
--------------------------------------------------

## 2. Summary of Work Completed
User authentication API implemented successfully

## 6. Instructions for Next Agent
Add refresh token functionality

🔍 - **Latest Commit Hash:** abc123...
🔍 - **Context Hash:** def456...
--------------------------------------------------

🔄 Synchronizing context...
✅ Context hash: def456789abc...

📊 Updating agent sync board...
✅ Agent board updated: Claude is active

🔍 Checking git status...
✅ Working directory clean

============================================================
🎯 YOUR TASK:
## 6. Instructions for Next Agent
Add refresh token functionality
============================================================

📚 Quick Commands:
--------------------------------------------------
# View full report:     cat HANDOFF_REPORT.md
# Create new handoff:   python scripts/create_handoff_report.py --author Claude ...
# Check agent status:   python scripts/multi_agent_sync.py list
--------------------------------------------------

✅ Claude initialization complete!
Ready to continue work.
```

---

## 🔧 Troubleshooting

### HANDOFF_REPORT.md가 없을 때
```
⚠️  No HANDOFF_REPORT.md found
   Starting fresh session (no previous handoff)
```
**해결**: 정상입니다. 첫 세션이거나 이전 handoff가 없는 경우입니다.

### Context hash 실패
```
⚠️  Could not retrieve context hash
```
**해결**: `python scripts/context_provider.py init` 실행

### Agent board 업데이트 실패
```
⚠️  Agent board update failed
```
**해결**: `python scripts/multi_agent_sync.py list`로 확인

---

## 🎉 완료!

이제 모든 AI Agent가 세션 시작 시 자동으로:
1. 이전 작업 내용을 읽고
2. 해야 할 일을 파악하고
3. Context를 동기화하고
4. 바로 작업을 시작할 수 있습니다!

**더 이상 수동으로 `cat HANDOFF_REPORT.md` 할 필요 없습니다!** 🚀
