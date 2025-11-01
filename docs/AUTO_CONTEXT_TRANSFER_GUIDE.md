# 🔄 AI Agent 컨텍스트 자동 전달 시스템

## 현재 상태 vs 개선된 시스템

### ❌ 기존 (수동 방식)
```bash
# 작업 완료 후 수동으로 실행해야 함
python scripts/create_handoff_report.py \
  --author "Claude" \
  --summary "수동으로 작성" \
  --instructions "수동으로 작성"
```

### ✅ 개선 (자동 방식) - 3가지 옵션

---

## 옵션 1: 🟢 완전 자동화 (Auto Handoff)

**특징**: 세션 종료 시 자동으로 Handoff 생성

### 설정 방법
```python
# 세션 시작 시 한 번만 실행
from scripts.auto_handoff import track

# 작업할 때마다 간단히 기록
track("User API 구현 완료")
track("버그 #123 수정")
track("테스트 추가")

# 세션 종료 시 자동으로 Handoff Report 생성!
```

### 동작 방식
1. **자동 추적**: 작업 내용을 `track()` 함수로 기록
2. **세션 종료 감지**: Python 종료 시 자동 실행
3. **Git 체크**: Uncommitted changes 확인
4. **Handoff 생성**: 자동으로 HANDOFF_REPORT.md 생성

### 장점
- ✅ 가장 간단함
- ✅ 까먹을 수 없음
- ✅ 작업 내용 자동 요약

---

## 옵션 2: 🟡 반자동 (Context Tracker)

**특징**: 파일 변경 자동 감지 + 30분마다 자동 체크포인트

### 설정 방법
```bash
# 백그라운드에서 실행
python scripts/auto_context_tracker.py --watch

# 또는 Python에서
from scripts.auto_context_tracker import AutoContextManager
manager = AutoContextManager()
manager.run()
```

### 동작 방식
1. **파일 감시**: 코드 파일 변경 자동 감지
2. **자동 추적**:
   - 수정된 파일 목록
   - 실행한 명령어
   - 테스트 결과
3. **30분 체크포인트**: 자동 Handoff 생성
4. **컨텍스트 파일**: `RUNS/context/current_context.json` 실시간 업데이트

### 장점
- ✅ 완전 자동 추적
- ✅ 30분마다 자동 백업
- ✅ 상세한 활동 로그

---

## 옵션 3: 🔵 Git Hooks 자동화

**특징**: Git 작업 시 자동 실행

### 설정 방법
```bash
# Git hooks 설치
python scripts/install_handoff_hooks.py install
```

### 동작 방식
1. **pre-commit**: Constitution 검증
2. **post-commit**: Agent sync board 업데이트
3. **pre-push**: Handoff Report 자동 생성

### 장점
- ✅ Git workflow와 통합
- ✅ 강제성 있음
- ✅ 표준 프로세스

---

## 🎯 추천 사용 시나리오

### Claude Code 사용자
```python
# .claude/init.py에 추가
from scripts.auto_handoff import track

# 작업하면서
track("기능 A 구현")
track("버그 B 수정")
# 세션 종료 시 자동 handoff
```

### Codex 사용자
```python
# 시작
>>> from scripts.auto_handoff import *
>>> from scripts.auto_context_tracker import track_command

# 작업 추적
>>> track("API endpoint 추가")
>>> track_command("pytest tests/")

# 자동으로 handoff 생성됨
```

### Gemini 사용자
```python
# 시작
>>> from scripts.gemini_auto_init import *
>>> from scripts.auto_handoff import track

# 작업 + 분석
>>> analyze()  # Gemini 특화 기능
>>> track("분석 결과 기반 리팩토링")

# 세션 종료 시 자동
```

---

## 📊 자동 전달되는 컨텍스트 내용

### 자동으로 수집되는 정보
1. **작업 내역**
   - 수정된 파일 목록
   - 실행한 명령어
   - 작업 설명 (track으로 추가)

2. **Git 정보**
   - 최신 commit hash
   - 변경된 파일들
   - Branch 정보

3. **Context Hash**
   - 프로젝트 상태 식별자
   - 설정 동기화 확인

4. **테스트 결과**
   - pytest 실행 결과
   - 성공/실패 통계

### 수동으로 추가하는 정보
- **Instructions**: 다음 Agent를 위한 지시사항
- **특별 참고사항**: 주의할 점, 미완성 부분

---

## 🔧 빠른 설정 (1분 완료)

### Step 1: 전역 설정
```bash
# .bashrc 또는 .zshrc에 추가
export PYTHONSTARTUP=~/.python_startup.py

# ~/.python_startup.py 생성
echo "from scripts.auto_handoff import track" > ~/.python_startup.py
```

### Step 2: 테스트
```python
# Python 실행
>>> track("테스트 작업")
✅ Tracked: 테스트 작업

# 종료 (Ctrl+D)
🤖 AUTO-HANDOFF: Session ending, creating handoff...
```

---

## ⚡ Quick Commands

### 즉시 Handoff 생성
```python
from scripts.auto_handoff import manual_handoff
manual_handoff("다음 작업: 테스트 작성")
```

### 현재 컨텍스트 확인
```bash
cat RUNS/context/current_context.json
```

### 수동 Handoff (기존 방식)
```bash
python scripts/create_handoff_report.py --author "YourName" ...
```

---

## 📈 효과

### Before (수동)
- 컨텍스트 전달 잊음: 50% 확률
- 작성 시간: 5-10분
- 정보 누락: 자주 발생

### After (자동)
- 컨텍스트 전달: 100% 보장
- 작성 시간: 0분 (자동)
- 정보 누락: 거의 없음

---

## 🎉 결론

이제 **따로 명시하지 않아도** 자동으로 컨텍스트가 전달됩니다!

1. **옵션 1 (Auto Handoff)**: 가장 간단, 추천 ⭐
2. **옵션 2 (Context Tracker)**: 가장 상세
3. **옵션 3 (Git Hooks)**: Git 통합

선택하여 사용하시면 됩니다!
