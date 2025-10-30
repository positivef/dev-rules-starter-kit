# 세션 관리 시스템 가이드

## 개요

SessionManager는 기존 개발 워크플로우를 보완하는 **선택적 보조 도구**입니다.
헌법 P11-P13에 따라 기존 원칙과의 충돌을 최소화하면서 세션 간 컨텍스트 유지를 지원합니다.

## 위치 및 우선순위

**시스템 우선순위** (헌법 기반):
1. **TaskExecutor + YAML 계약서** (P1, P2 준수) - 주요 워크플로우
2. **수동 체크포인트** - 중요 작업 전 백업
3. **SessionManager** - 보조적 자동 저장 (선택적)

## 핵심 기능

### 1. 자동 저장 메커니즘
- **30분마다 자동 체크포인트** 생성 (기존 권장 패턴 준수)
- **비정상 종료 시 복구 지원** (SIGINT, SIGTERM, atexit)
- **중요 데이터 변경 시 즉시 저장**
- **백업 관리**: 저장 실패 시 이전 백업 복원

### 2. 상태 범위 관리 (State Scoping)
```python
StateScope.SESSION  # 현재 세션만 유지
StateScope.USER     # 사용자별로 지속
StateScope.APP      # 애플리케이션 전역
StateScope.TEMP     # 임시 (저장 안 함)
```

### 3. 불변 상태 객체
- 상태 변경 시 새 객체 생성
- 데이터 일관성 보장
- 동시성 문제 방지

## 사용 시나리오

### 시나리오 1: 개발 작업 추적
```python
from scripts.session_manager import SessionManager, StateScope

# 세션 시작
session = SessionManager.get_instance()
session.start()

# 현재 작업 저장
session.set("current_feature", "authentication", StateScope.SESSION)
session.set("completed_tasks", ["setup", "database"], StateScope.SESSION)
session.set("test_coverage", 85.5, StateScope.SESSION)

# 나중에 조회
feature = session.get("current_feature", StateScope.SESSION)
tasks = session.get("completed_tasks", StateScope.SESSION)
```

### 시나리오 2: 사용자 설정 관리
```python
# 사용자별 설정 (세션 간 유지)
session.set("user:theme", "dark", StateScope.USER)
session.set("user:editor", "vscode", StateScope.USER)
session.set("user:auto_save", True, StateScope.USER)

# 다음 세션에서도 복구됨
theme = session.get("user:theme", StateScope.USER, default="light")
```

### 시나리오 3: 프로젝트 전역 설정
```python
# 프로젝트 전역 정보
session.set("project:name", "dev-rules-starter-kit", StateScope.APP)
session.set("project:version", "1.0.0", StateScope.APP)
session.set("project:constitution", {"articles": 13}, StateScope.APP)
```

### 시나리오 4: 임시 캐시 데이터
```python
# 저장하지 않을 임시 데이터
session.set("temp:analysis_cache", large_data, StateScope.TEMP)
session.set("temp:build_artifacts", build_output, StateScope.TEMP)
```

## 실제 적용 예제

### TaskExecutor와 통합
```python
#!/usr/bin/env python3
"""TaskExecutor와 SessionManager 통합 예제"""

from scripts.session_manager import SessionManager, StateScope

class EnhancedTaskExecutor:
    def __init__(self):
        self.session = SessionManager.get_instance()
        self.session.start()

    def execute_task(self, task_yaml):
        # 작업 시작 기록
        task_id = task_yaml.get("task_id")
        self.session.set("executing_task", task_id, StateScope.SESSION)
        self.session.set("task_start_time", datetime.now(), StateScope.SESSION)

        try:
            # 작업 실행
            result = self._run_task(task_yaml)

            # 성공 기록
            completed = self.session.get("completed_tasks", StateScope.SESSION, [])
            completed.append(task_id)
            self.session.set("completed_tasks", completed, StateScope.SESSION)

            return result

        except Exception as e:
            # 실패 기록
            self.session.set("last_error", str(e), StateScope.SESSION)
            self.session.set("failed_task", task_id, StateScope.SESSION)
            raise

    def get_session_summary(self):
        """세션 요약 정보"""
        return {
            "completed": self.session.get("completed_tasks", StateScope.SESSION, []),
            "current": self.session.get("executing_task", StateScope.SESSION),
            "failed": self.session.get("failed_task", StateScope.SESSION)
        }
```

### 개발 어시스턴트와 통합
```python
#!/usr/bin/env python3
"""DevAssistant와 SessionManager 통합 예제"""

from scripts.session_manager import SessionManager, StateScope

class SessionAwareDevAssistant:
    def __init__(self):
        self.session = SessionManager.get_instance()
        self.session.start()

    def on_file_change(self, file_path):
        # 변경 파일 추적
        changed_files = self.session.get("changed_files", StateScope.SESSION, set())
        changed_files.add(str(file_path))
        self.session.set("changed_files", list(changed_files), StateScope.SESSION)

        # 검증 카운트 증가
        count = self.session.get("verification_count", StateScope.SESSION, 0)
        self.session.set("verification_count", count + 1, StateScope.SESSION)

    def get_activity_summary(self):
        """활동 요약"""
        return {
            "files_changed": len(self.session.get("changed_files", StateScope.SESSION, [])),
            "verifications": self.session.get("verification_count", StateScope.SESSION, 0),
            "session_duration": self._calculate_duration()
        }
```

## CLI 명령어

```bash
# 새 세션 시작 (이전 세션 무시)
python scripts/session_manager.py start

# 마지막 세션 복구
python scripts/session_manager.py resume

# 현재 세션 정보 확인
python scripts/session_manager.py info

# 수동 체크포인트 (중요 작업 전)
python scripts/session_manager.py checkpoint
```

## 세션 파일 구조

```
RUNS/sessions/
├── session_20251026_121458_9bbf8a34.json  # 현재 세션
├── session_20251026_115023_a2c4f891.json  # 이전 세션
└── session_20251026_113512_b5d7e023.json  # 더 이전 세션
```

### 세션 파일 형식
```json
{
  "session_id": "session_20251026_121458_9bbf8a34",
  "started_at": "2025-10-26T12:14:58Z",
  "last_checkpoint": "2025-10-26T12:19:58Z",
  "context_hash": "9bbf8a34c2d1f5e8",
  "state_data": {},
  "scope_data": {
    "session": {
      "current_task": "feature_development",
      "completed_tasks": ["setup", "database", "api"]
    },
    "user": {
      "user:theme": "dark",
      "user:editor": "vscode"
    },
    "app": {
      "project:name": "dev-rules-starter-kit",
      "project:version": "1.0.0"
    },
    "temp": {}
  }
}
```

## 주의사항

### 1. 싱글톤 패턴
SessionManager는 싱글톤으로 구현되어 있어 애플리케이션 전체에서 하나의 인스턴스만 존재합니다.

```python
# 항상 같은 인스턴스 반환
session1 = SessionManager.get_instance()
session2 = SessionManager.get_instance()
assert session1 is session2  # True
```

### 2. 스레드 안전성
자동 체크포인트는 별도 스레드에서 실행되며, 모든 상태 변경은 불변 객체로 처리됩니다.

### 3. 저장 공간 관리
- 최대 10개 세션만 유지 (설정 가능)
- 오래된 세션은 자동 삭제
- 백업 파일 포함 최대 20개 파일

### 4. 비정상 종료 대응
- Ctrl+C (SIGINT): 자동 저장 후 종료
- Kill (SIGTERM): 자동 저장 후 종료
- 프로그램 충돌: atexit 핸들러가 저장
- 전원 차단: 마지막 체크포인트(30분 이내)로 복구

## 문제 해결

### Q1: 세션이 복구되지 않음
```bash
# 세션 파일 확인
ls -la RUNS/sessions/

# 수동으로 특정 세션 복구 (향후 구현)
python scripts/session_manager.py recover <session_id>
```

### Q2: 체크포인트 간격 조정 필요
```python
# 체크포인트 간격 조정 (기본 30분)
session = SessionManager.get_instance()
session.checkpoint_interval = 3600  # 60분으로 변경
# 또는
session.checkpoint_interval = 900  # 15분으로 변경
```

### Q3: 저장 공간 부족
```python
# 최대 세션 수 조정
session = SessionManager.get_instance()
session.max_sessions = 5  # 5개만 유지
```

## 성능 고려사항

- **체크포인트 크기**: JSON 직렬화 가능한 데이터만 저장
- **메모리 사용**: TEMP 스코프 데이터는 메모리에만 유지
- **I/O 부하**: 30분마다 파일 쓰기 (최적화된 주기)
- **CPU 사용**: 체크포인트 스레드는 대부분 sleep 상태

**I/O 최적화 근거**:
- 5분: 과도한 디스크 쓰기로 성능 저하 우려
- 30분: 적절한 균형 (기존 권장 패턴)
- 60분+: 데이터 손실 위험 증가

## TaskExecutor와의 통합 (구현 완료)

### 느슨한 통합 아키텍처
TaskExecutor와 SessionManager는 **의존성 없이** 연동됩니다:
- SessionManager가 없어도 TaskExecutor는 정상 작동
- 선택적으로 활성화 가능한 훅 시스템
- 자동으로 작업 상태와 메트릭 수집

### 사용 방법
```python
# TaskExecutor에서 훅 import (선택적)
from task_executor_session_hook import get_hook

# TaskExecutor 실행 시 자동 기록
hook = get_hook()
hook.on_task_start(task_data)  # 작업 시작
hook.on_command_execute(cmd, exit_code)  # 명령 실행
hook.on_task_complete(task_data, success, time)  # 작업 완료
```

### 수집되는 정보
- 작업 시작/완료 시간
- 성공/실패 상태
- 실행 시간
- 오류 메시지
- 명령 실행 로그

## 세션 분석 도구 (구현 완료)

### 기능
작업 패턴과 생산성을 분석하는 도구:
- 자주 실행하는 작업 분석
- 실패 패턴 파악
- 시간대별 생산성 측정
- 개선 제안 생성

### 사용 방법
```bash
# 최근 30일 분석 (기본값)
python scripts/session_analyzer.py

# 최근 7일 분석
python scripts/session_analyzer.py --days 7

# 조용히 실행하고 파일만 저장
python scripts/session_analyzer.py --quiet --output report.json
```

### 분석 결과
- **작업 패턴**: 자주 실행한 작업, 실패한 작업
- **생산성**: 평균 세션 시간, 활동적인 시간대
- **에러 패턴**: 반복되는 에러, 문제 작업
- **통계**: 성공률, 총 실행 시간
- **개선 제안**: 자동 생성된 인사이트

### 보고서 예시
```
[실행 통계]
총 작업 수: 50
성공: 45 (90%)
실패: 5
총 실행 시간: 5.2시간

[자주 실행한 작업]
- TEST-2025-10-26: 15회
- FEAT-2025-10-26: 12회

[개선 제안]
- 오전 9-11시가 가장 생산적
- FIX-DB 작업이 자주 실패 - 근본 원인 분석 필요
```

## 향후 개선 계획

1. **암호화 저장**: 민감한 데이터 보호
2. **압축 저장**: 큰 세션 데이터 압축
3. **원격 백업**: 클라우드 저장소 연동
4. **실시간 대시보드**: 웹 기반 실시간 모니터링
5. **AI 기반 인사이트**: 패턴 학습 및 예측

## 결론

SessionManager는 **보조 도구**로서:
- ✅ 세션 간 컨텍스트 유지를 지원합니다
- ✅ 비정상 종료 시 복구를 도와줍니다 (최대 30분 이내 작업)
- ✅ 사용자별, 프로젝트별 설정을 유지합니다
- ✅ 기존 TaskExecutor 워크플로우와 병행 사용 가능합니다

**중요**: TaskExecutor + YAML 계약서가 여전히 주요 워크플로우입니다 (헌법 P1, P2)
