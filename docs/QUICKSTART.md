# 🚀 Dev Rules Starter Kit - 빠른 시작 가이드

5분 안에 시작할 수 있는 가장 빠른 방법!

## 📦 1분 설치

### Windows
```batch
git clone https://github.com/your-org/dev-rules-starter-kit
cd dev-rules-starter-kit
launch.bat
```

### Mac/Linux
```bash
git clone https://github.com/your-org/dev-rules-starter-kit
cd dev-rules-starter-kit
chmod +x launch.sh
./launch.sh
```

## 🎯 30초 선택: 어떤 모드로 시작할까?

### 옵션 1: CLI 직접 사용 (Agent용) 🤖
```bash
launch.bat cli     # Windows
./launch.sh cli    # Mac/Linux
```
**적합한 경우**: Claude Code, Cursor, Aider 등 AI Agent 사용 시

### 옵션 2: Web UI 사용 (브라우저) 🌐
```bash
launch.bat web     # Windows
./launch.sh web    # Mac/Linux
```
**적합한 경우**: 시각적 대시보드로 관리하고 싶을 때

### 옵션 3: Hybrid 모드 (추천) 🔄
```bash
launch.bat         # Windows (기본값)
./launch.sh        # Mac/Linux (기본값)
```
**적합한 경우**: 모든 기능을 활용하고 싶을 때

## ⚡ 2분 활용: 첫 번째 기능 개발

### Claude Code에서 사용하기
```bash
claude "이 프로젝트의 Dev Rules 시스템을 사용하여 JWT 인증을 개발해주세요"
```

Claude가 자동으로:
1. ✅ 테스트 먼저 작성 (TDD)
2. ✅ 구현 코드 작성
3. ✅ 커버리지 85% 확인
4. ✅ TAG 추가 (#REQ-001)

### 수동으로 사용하기
```bash
# 1. SPEC 생성
python scripts/tier1_cli.py spec "로그인 기능"

# 2. TDD 체크
python scripts/tier1_cli.py tdd --strict

# 3. 테스트 실행
python scripts/incremental_test_runner.py

# 4. TAG 추가
python scripts/tier1_cli.py tag #AUTH-001
```

## 📊 Web UI 사용 (http://localhost:8000)

1. **브라우저 열기**: launch.bat web 실행 시 자동으로 열림
2. **Agent 선택**: 왼쪽 패널에서 사용할 Agent 선택
3. **명령 실행**:
   - 빠른 버튼: [TDD Check] [Run Tests] [Extract Tags] [Clean]
   - 직접 입력: 터미널에 명령어 입력
4. **실시간 확인**: 테스트 결과, 커버리지, 에러 로그

## 🛠️ 핵심 도구 5개

| 도구 | 명령어 | 용도 |
|------|--------|------|
| **TDD 강제** | `python scripts/tier1_cli.py tdd --strict` | 테스트 없으면 실행 차단 |
| **증분 테스트** | `python scripts/incremental_test_runner.py` | 변경된 파일만 테스트 |
| **병렬 테스트** | `python scripts/selective_parallel_runner.py` | 대용량 테스트 병렬화 |
| **TAG 시스템** | `python scripts/simple_tag_system.py` | 요구사항 추적 |
| **정리** | `python scripts/evidence_cleaner.py` | 증거 파일 자동 정리 |

## 🎨 실제 시나리오

### 시나리오 1: 새 기능 개발 (TDD 방식)
```bash
# 1. SPEC 작성
python scripts/tier1_cli.py spec "사용자 프로필 API"

# 2. 테스트 작성
echo "test_user_profile.py 작성"

# 3. TDD 체크 (실패 확인)
python scripts/tier1_cli.py tdd --strict

# 4. 구현
echo "user_profile.py 구현"

# 5. 테스트 통과
python scripts/incremental_test_runner.py

# 6. TAG 추가
python scripts/tier1_cli.py tag #USER-001
```

### 시나리오 2: PRD → 자동 개발
```bash
# PRD 파일 준비
echo "프로젝트 요구사항..." > prd.txt

# Claude에게 전달
claude "prd.txt 파일의 요구사항대로 개발해주세요. Dev Rules 시스템을 사용하세요."

# Claude가 자동으로:
# - PRD 분석
# - SPEC 생성
# - TDD 사이클 실행
# - 커버리지 체크
# - TAG 관리
```

### 시나리오 3: 기존 프로젝트 통합
```bash
# 1. 초기 설정
python scripts/auto_setup.py

# 2. 테스트 커버리지 확인
python scripts/tier1_cli.py tdd --threshold 70

# 3. 증분 개선
python scripts/incremental_test_runner.py
```

## 🔧 설정 커스터마이징

### .env 파일 수정
```env
# 커버리지 목표 (기본: 85%)
COVERAGE_THRESHOLD=90

# 병렬 테스트 기준 (기본: 50개)
PARALLEL_TEST_THRESHOLD=30

# 증거 파일 보관 기간 (기본: 7일)
EVIDENCE_RETENTION_DAYS=14
```

### Agent별 설정
```bash
# Claude 설정 수정
vi .agent_configs/claude_config.json

# Cursor 설정 수정
vi .agent_configs/cursor_config.json
```

## ❓ 문제 해결

### Python 없음
```bash
# Windows
https://www.python.org/downloads/

# Mac
brew install python3

# Linux
sudo apt install python3
```

### 의존성 설치
```bash
pip install -r requirements.txt
pip install -r web/requirements.txt
```

### 포트 충돌
```bash
# 다른 포트 사용
python orchestrator/unified_system.py --web --port 8080
```

## 📚 다음 단계

1. **상세 가이드**: `docs/DUAL_MODE_USAGE_GUIDE.md`
2. **Claude 통합**: `docs/CLAUDE_INTEGRATION_GUIDE.md`
3. **Web UI 가이드**: `docs/WEB_INTERFACE_GUIDE.md`
4. **개발 워크플로우**: `docs/DEVELOPMENT_WORKFLOW.md`

## 🎉 축하합니다!

이제 Dev Rules 시스템을 사용할 준비가 완료되었습니다!

**핵심 명령어 3개만 기억하세요**:
1. `launch.bat` - 시스템 시작
2. `python scripts/tier1_cli.py tdd --strict` - TDD 강제
3. `python scripts/incremental_test_runner.py` - 테스트 실행

질문이 있으시면 Issues에 등록해주세요: https://github.com/your-org/dev-rules-starter-kit/issues

---

**Pro Tip**: Hybrid 모드를 사용하면 CLI의 속도와 Web UI의 편의성을 모두 누릴 수 있습니다! 🚀
