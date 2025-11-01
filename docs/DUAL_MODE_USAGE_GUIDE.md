# 📘 Dual Mode 사용 가이드 - CLI 직접 사용 & Web UI 통합

## 🎯 개요
이 시스템은 **두 가지 방식**으로 사용 가능합니다:
1. **Mode 1: Direct CLI** - Agent가 직접 Dev Rules 폴더를 참조하여 개발
2. **Mode 2: Web UI** - 웹 인터페이스를 통해 Agent 선택 및 제어
3. **Hybrid Mode** - 두 방식을 동시에 사용

---

## 🚀 Mode 1: Direct CLI (Agent 직접 사용)

### Claude Code에서 직접 사용
```bash
# Claude CLI에서
claude "이 프로젝트의 Dev Rules 시스템을 사용하겠습니다"

# 시스템이 자동으로 제공하는 컨텍스트
Available Tools:
- TDD 체크: python scripts/tier1_cli.py tdd --strict
- 증분 테스트: python scripts/incremental_test_runner.py
- 병렬 테스트: python scripts/selective_parallel_runner.py
- TAG 관리: python scripts/simple_tag_system.py
- 캐시 관리: python scripts/smart_cache_manager.py
- 정리: python scripts/evidence_cleaner.py

# Claude가 직접 실행
claude "JWT 인증 시스템을 TDD 방식으로 개발해주세요"
> 1. 테스트 파일 생성: tests/test_auth.py
> 2. TDD 체크 실행: python scripts/tier1_cli.py tdd --strict
> 3. 구현: src/auth.py
> 4. 검증: python scripts/incremental_test_runner.py
```

### 다른 Agent에서 사용 (Cursor, Aider, Copilot)

#### Cursor AI
```bash
# .cursor/settings.json
{
  "dev_rules": {
    "enabled": true,
    "base_path": "./dev-rules-starter-kit",
    "auto_tdd": true,
    "coverage_threshold": 85
  }
}

# Cursor에서 명령
@dev-rules "테스트 실행"
```

#### Aider
```bash
# Aider 시작 시 Dev Rules 활성화
aider --config .agent_configs/aider_config.json

# Aider 세션에서
/run python scripts/tier1_cli.py tdd --strict
/test
/commit
```

#### GitHub Copilot
```python
# .github/copilot-config.yml
dev_rules:
  enabled: true
  tools_path: "./dev-rules-starter-kit/scripts"

# VSCode에서 Copilot 사용 시 자동으로 Dev Rules 도구 제안
```

### Agent별 설정 파일 자동 생성
```bash
# 설정 파일 자동 생성
python orchestrator/unified_system.py --setup

# 생성되는 파일들
.agent_configs/
├── claude_config.json
├── cursor_config.json
├── aider_config.json
├── codex_config.json
└── copilot_config.json
```

### 예시: claude_config.json
```json
{
  "agent": "claude",
  "dev_rules": {
    "enabled": true,
    "base_path": "C:/dev-rules-starter-kit",
    "tools": {
      "tdd": {
        "command": "python scripts/tier1_cli.py tdd --strict",
        "description": "TDD 강제 실행"
      },
      "test": {
        "command": "python scripts/incremental_test_runner.py",
        "description": "증분 테스트"
      }
    }
  },
  "workflow": [
    "SPEC 생성 → 테스트 작성 → TDD 체크 → 구현 → 검증"
  ]
}
```

---

## 🌐 Mode 2: Web UI (웹 인터페이스)

### 웹 서버 시작
```bash
# Web UI 모드로 시작
python orchestrator/unified_system.py --web

# 또는 Windows
launch.bat web

# 또는 Mac/Linux
./launch.sh web
```

### 브라우저에서 접속
```
http://localhost:8000
```

### Web UI 기능

#### 1. Agent 선택 패널 (좌측)
- **Claude Code**: 일반 개발, 리팩토링
- **Codex MCP**: 알고리즘 최적화
- **Cursor AI**: 인라인 편집
- **Aider**: Git 통합 개발
- **GitHub Copilot**: 자동 완성

#### 2. 작업 영역 (우측)
- **터미널**: 실시간 명령 실행 및 결과
- **명령 입력**: 직접 명령어 입력
- **빠른 실행 버튼**:
  - ✅ TDD Check
  - 🧪 Run Tests
  - 🏷️ Extract Tags
  - 🗑️ Clean Evidence

#### 3. Dev Rules Tools (하단)
클릭하면 자동으로 명령어 입력:
- TDD Enforcer
- Incremental Test
- Parallel Test
- TAG System
- Smart Cache
- Evidence Clean

### Web UI 워크플로우
```
1. Agent 선택 (예: Claude)
2. Agent 시작 → Session ID 생성
3. 명령 실행:
   - 직접 입력: "python scripts/tier1_cli.py tdd"
   - 빠른 실행: [TDD Check] 버튼 클릭
   - 도구 선택: Dev Rules Tools 클릭
4. 실시간 결과 확인 (터미널)
5. WebSocket으로 실시간 통신
```

---

## 🔄 Hybrid Mode (추천)

### 시작 방법
```bash
# Hybrid 모드 (기본값)
python orchestrator/unified_system.py --hybrid

# 또는
launch.bat  # Windows
./launch.sh # Mac/Linux
```

### Hybrid Mode 장점
1. **CLI 직접 사용 가능**: Agent가 바로 명령 실행
2. **Web UI 모니터링**: 브라우저에서 실시간 확인
3. **동시 제어**: CLI와 Web UI 동시 사용
4. **세션 공유**: 같은 세션을 여러 인터페이스에서 공유

### 사용 시나리오

#### 시나리오 1: Claude CLI + Web 모니터링
```bash
# Terminal 1: Claude CLI
claude "JWT 인증 시스템 개발"
> Dev Rules 도구를 사용하여 TDD 방식으로 개발합니다...

# Browser: Web UI (http://localhost:8000)
- 실시간 진행 상황 모니터링
- 테스트 결과 시각화
- 커버리지 그래프
```

#### 시나리오 2: Web UI로 Agent 선택 → CLI로 세부 작업
```bash
# Browser: Agent 선택
1. Claude 선택 → Session 시작
2. 기본 설정 및 초기화

# Terminal: 세부 명령
cd dev-rules-starter-kit
python scripts/tier1_cli.py spec "새 기능"
python scripts/incremental_test_runner.py
```

#### 시나리오 3: 멀티 Agent 협업
```bash
# Web UI에서
- Claude: 메인 개발
- Codex: 알고리즘 최적화
- Cursor: UI 수정

# 각 Agent가 Dev Rules 도구 공유
모든 Agent가 같은 TDD 체크, 테스트 실행
```

---

## 📁 프로젝트 구조

```
dev-rules-starter-kit/
├── orchestrator/
│   ├── unified_system.py    # 통합 시스템 메인
│   └── prd_processor.py     # PRD 처리
├── .agent_configs/          # Agent별 설정
│   ├── claude_config.json
│   ├── cursor_config.json
│   └── aider_config.json
├── scripts/                 # Dev Rules 도구들
│   ├── tier1_cli.py
│   ├── incremental_test_runner.py
│   └── ...
├── web/                     # Web UI
│   └── app.py
├── launch.bat              # Windows 실행
└── launch.sh               # Unix 실행
```

---

## 🔧 환경 설정

### .env 파일
```bash
# Dev Rules System Environment
DEV_RULES_PATH=C:/dev-rules-starter-kit
DEV_RULES_MODE=hybrid
PYTHONPATH=C:/dev-rules-starter-kit

# Agent Settings
CLAUDE_ENABLED=true
CODEX_ENABLED=true
CURSOR_ENABLED=true
AIDER_ENABLED=true

# Web UI Settings
WEB_UI_PORT=8000
WEB_UI_HOST=0.0.0.0
```

### 초기 설정
```bash
# 1. 의존성 설치
pip install -r requirements.txt
pip install -r web/requirements.txt

# 2. 설정 초기화
python orchestrator/unified_system.py --setup

# 3. 모드 선택 실행
python orchestrator/unified_system.py --mode hybrid
```

---

## 💡 실제 사용 예제

### 예제 1: 새 프로젝트 시작
```bash
# Claude CLI에서
claude "새 프로젝트를 Dev Rules 시스템으로 시작하겠습니다"

# 자동 실행
1. python scripts/setup_wizard.py  # 초기 설정
2. python scripts/tier1_cli.py spec "프로젝트 개요"
3. 테스트 작성 시작...
```

### 예제 2: 기존 프로젝트 통합
```bash
# Web UI에서
1. Aider Agent 선택
2. "git status" 실행
3. "python scripts/tier1_cli.py tdd --strict" 실행
4. 커버리지 확인 후 개발 진행
```

### 예제 3: CI/CD 통합
```yaml
# .github/workflows/dev-rules.yml
name: Dev Rules Check
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Dev Rules TDD Check
        run: |
          cd dev-rules-starter-kit
          python scripts/tier1_cli.py tdd --strict

      - name: Incremental Test
        run: python scripts/incremental_test_runner.py
```

---

## 🎯 핵심 포인트

### CLI 직접 사용 시
✅ **장점**:
- Agent 네이티브 환경
- 빠른 실행
- 스크립트 자동화 가능

❌ **단점**:
- 시각화 부족
- 모니터링 어려움

### Web UI 사용 시
✅ **장점**:
- 시각적 인터페이스
- 실시간 모니터링
- 여러 Agent 관리

❌ **단점**:
- 추가 서버 필요
- 네트워크 의존

### Hybrid 사용 시 (추천)
✅ **모든 장점 활용**:
- CLI 속도 + Web UI 시각화
- 유연한 워크플로우
- 팀 협업 가능

---

## 📞 문제 해결

### CLI가 작동 안 할 때
```bash
# 환경 변수 확인
echo $DEV_RULES_PATH
echo $PYTHONPATH

# 수동 설정
export DEV_RULES_PATH=/path/to/dev-rules-starter-kit
export PYTHONPATH=$DEV_RULES_PATH
```

### Web UI 접속 안 될 때
```bash
# 포트 확인
netstat -an | grep 8000

# 다른 포트 사용
python orchestrator/unified_system.py --web --port 8080
```

### Agent 연결 실패
```bash
# 설정 파일 확인
cat .agent_configs/claude_config.json

# 재생성
python orchestrator/unified_system.py --setup
```

---

이제 두 가지 모드 모두 완벽하게 사용 가능합니다! 🎉
