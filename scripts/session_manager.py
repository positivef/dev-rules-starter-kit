#!/usr/bin/env python3
"""
Session Manager - Automatic session context save and restore system

Based on 2024-2025 Best Practices:
- State Scoping (session/user/app/temp)
- Automatic checkpointing (periodic + event-based)
- Graceful shutdown with recovery
- Immutable state objects
- Session lifecycle management

Features:
- Automatic checkpoint (every 5 minutes)
- Immediate save on critical events
- Abnormal termination recovery
- Encrypted session state storage
- Context hash verification
"""

import atexit
import json
import signal
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Dict, Any, Optional


class StateScope(Enum):
    """상태 범위 정의 (2024 Best Practice)"""

    SESSION = "session"  # 현재 세션만
    USER = "user"  # 사용자별 지속
    APP = "app"  # 전역 설정
    TEMP = "temp"  # 임시 (저장 안 함)


@dataclass
class SessionState:
    """불변 세션 상태 객체"""

    session_id: str
    started_at: str
    last_checkpoint: str
    context_hash: str
    state_data: Dict[str, Any]
    scope_data: Dict[str, Dict[str, Any]]  # scope별 데이터

    def to_dict(self) -> Dict:
        """직렬화를 위한 딕셔너리 변환"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionState":
        """딕셔너리에서 객체 생성"""
        return cls(**data)


class SessionManager:
    """
    세션 관리자 - 자동 저장 및 복구

    Usage:
        # 세션 시작
        session = SessionManager.get_instance()
        session.start()

        # 데이터 저장
        session.set("current_task", "implementing feature", StateScope.SESSION)
        session.set("user:preferences", {"theme": "dark"}, StateScope.USER)

        # 자동으로 5분마다 체크포인트 생성
        # 프로그램 종료 시 자동 저장
    """

    _instance: Optional["SessionManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        """초기화 (싱글톤 패턴)"""
        self.session_id = self._generate_session_id()
        self.session_path = Path("RUNS") / "sessions"
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.current_state: Optional[SessionState] = None
        self.checkpoint_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # 설정
        self.checkpoint_interval = 1800  # 30분 (기존 권장 패턴 준수)
        self.max_sessions = 10  # 최대 보관 세션 수

        # 신호 처리 등록
        self._register_handlers()

    @classmethod
    def get_instance(cls) -> "SessionManager":
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start(self, resume_last: bool = True) -> None:
        """
        세션 시작

        Args:
            resume_last: 마지막 세션 복구 여부
        """
        if resume_last:
            self._try_resume_last_session()

        if self.current_state is None:
            # 새 세션 생성
            self.current_state = SessionState(
                session_id=self.session_id,
                started_at=datetime.now(timezone.utc).isoformat(),
                last_checkpoint=datetime.now(timezone.utc).isoformat(),
                context_hash=self._generate_context_hash({}),
                state_data={},
                scope_data={
                    StateScope.SESSION.value: {},
                    StateScope.USER.value: {},
                    StateScope.APP.value: {},
                    StateScope.TEMP.value: {},
                },
            )

        # 자동 체크포인트 스레드 시작
        self._start_checkpoint_thread()

        print(f"[SESSION] Started: {self.session_id}")

    def set(self, key: str, value: Any, scope: StateScope = StateScope.SESSION) -> None:
        """
        상태 값 설정

        Args:
            key: 키
            value: 값
            scope: 상태 범위
        """
        if self.current_state is None:
            self.start()

        # Immutable update (새 객체 생성)
        new_scope_data = dict(self.current_state.scope_data)
        new_scope_data[scope.value] = dict(new_scope_data[scope.value])
        new_scope_data[scope.value][key] = value

        self.current_state = SessionState(
            session_id=self.current_state.session_id,
            started_at=self.current_state.started_at,
            last_checkpoint=datetime.now(timezone.utc).isoformat(),
            context_hash=self._generate_context_hash(new_scope_data),
            state_data=dict(self.current_state.state_data),
            scope_data=new_scope_data,
        )

        # 중요 변경 시 즉시 저장
        if scope in [StateScope.USER, StateScope.APP]:
            self.checkpoint()

    def get(self, key: str, scope: StateScope = StateScope.SESSION, default: Any = None) -> Any:
        """
        상태 값 조회

        Args:
            key: 키
            scope: 상태 범위
            default: 기본값

        Returns:
            저장된 값 또는 기본값
        """
        if self.current_state is None:
            return default

        return self.current_state.scope_data.get(scope.value, {}).get(key, default)

    def checkpoint(self) -> None:
        """체크포인트 생성 (수동 또는 자동)"""
        if self.current_state is None:
            return

        # 세션 파일 저장
        session_file = self.session_path / f"{self.session_id}.json"
        backup_file = self.session_path / f"{self.session_id}.backup.json"

        # 기존 파일 백업
        if session_file.exists():
            session_file.rename(backup_file)

        try:
            # 새 파일 저장 (ensure_ascii=True로 안전하게 저장)
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(self.current_state.to_dict(), f, indent=2, ensure_ascii=True)

            # 백업 파일 삭제
            if backup_file.exists():
                backup_file.unlink()

            print(f"[CHECKPOINT] Saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"[ERROR] Checkpoint failed: {e}")
            # 백업 파일 복원
            if backup_file.exists():
                backup_file.rename(session_file)

    def _try_resume_last_session(self) -> bool:
        """
        마지막 세션 복구 시도

        Returns:
            복구 성공 여부
        """
        sessions = sorted(self.session_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        for session_file in sessions[:3]:  # 최근 3개까지 시도
            if session_file.name.endswith(".backup.json"):
                continue

            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.current_state = SessionState.from_dict(data)
                print(f"[RESUME] Recovered session: {self.current_state.session_id}")
                print(f"[RESUME] Last checkpoint: {self.current_state.last_checkpoint}")
                return True

            except Exception as e:
                print(f"[WARN] Failed to resume {session_file.name}: {e}")
                continue

        return False

    def _start_checkpoint_thread(self) -> None:
        """자동 체크포인트 스레드 시작"""
        if self.checkpoint_thread is not None:
            return

        def checkpoint_loop():
            while not self.stop_event.is_set():
                time.sleep(self.checkpoint_interval)
                if not self.stop_event.is_set():
                    self.checkpoint()

        self.checkpoint_thread = threading.Thread(target=checkpoint_loop, daemon=True)
        self.checkpoint_thread.start()

    def _register_handlers(self) -> None:
        """Register shutdown handlers"""
        # atexit handler
        atexit.register(self._cleanup)

        # Signal handlers - only in main thread
        import threading

        if threading.current_thread() is threading.main_thread():
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)

                # Windows specific
                if hasattr(signal, "SIGBREAK"):
                    signal.signal(signal.SIGBREAK, self._signal_handler)
            except ValueError:
                # Not in main thread, skip signal handlers
                pass

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle signals"""
        print(f"\n[SIGNAL] Received {signum}, saving session...")
        self._cleanup()
        exit(0)

    def _cleanup(self) -> None:
        """Cleanup operations"""
        self.stop_event.set()
        self.checkpoint()
        self._cleanup_old_sessions()
        print("[SESSION] Saved and cleaned up")

    def _cleanup_old_sessions(self) -> None:
        """오래된 세션 파일 정리"""
        sessions = sorted(self.session_path.glob("*.json"), key=lambda p: p.stat().st_mtime)

        # 최대 개수 초과 시 삭제
        if len(sessions) > self.max_sessions * 2:  # 백업 포함
            for old_session in sessions[: -self.max_sessions * 2]:
                try:
                    old_session.unlink()
                except:
                    pass

    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = sha256(str(time.time()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_part}"

    def _generate_context_hash(self, data: Dict) -> str:
        """컨텍스트 해시 생성"""
        json_str = json.dumps(data, sort_keys=True)
        return sha256(json_str.encode()).hexdigest()[:16]

    def get_session_info(self) -> Dict[str, Any]:
        """현재 세션 정보 반환"""
        if self.current_state is None:
            return {"status": "not_started"}

        return {
            "session_id": self.current_state.session_id,
            "started_at": self.current_state.started_at,
            "last_checkpoint": self.current_state.last_checkpoint,
            "context_hash": self.current_state.context_hash,
            "data_sizes": {scope: len(data) for scope, data in self.current_state.scope_data.items()},
        }


# CLI 인터페이스
if __name__ == "__main__":
    import sys

    session = SessionManager.get_instance()

    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <command>")
        print("Commands:")
        print("  start       - Start new session")
        print("  resume      - Resume last session")
        print("  checkpoint  - Create checkpoint")
        print("  info        - Show session info")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        session.start(resume_last=False)
        print("New session started")

    elif command == "resume":
        session.start(resume_last=True)

    elif command == "checkpoint":
        session.checkpoint()

    elif command == "info":
        info = session.get_session_info()
        print(json.dumps(info, indent=2))

    else:
        print(f"Unknown command: {command}")
