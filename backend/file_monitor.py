#!/usr/bin/env python3
"""파일 감시 시스템

Phase D Week 1: 실시간 파일 변경 감지 및 자동 검증

주요 기능:
1. Python 파일 변경 감지 (watchdog)
2. Debounce 처리 (0.5초 내 중복 무시)
3. 자동 검증 실행
4. WebSocket 실시간 알림
"""

import time
from pathlib import Path
from typing import Callable, Dict
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CodeFileHandler(FileSystemEventHandler):
    """Python 파일 변경 핸들러

    Features:
    - .py 파일만 감시
    - Debounce 처리 (0.5초)
    - 수정/생성 이벤트 감지
    """

    def __init__(
        self,
        on_file_changed: Callable[[Path], None],
        debounce_seconds: float = 0.5,
    ):
        """초기화

        Args:
            on_file_changed: 파일 변경 시 호출할 콜백
            debounce_seconds: Debounce 시간 (초)
        """
        super().__init__()
        self.on_file_changed = on_file_changed
        self.debounce_seconds = debounce_seconds
        self.last_modified: Dict[str, float] = {}

    def _should_process(self, file_path: str) -> bool:
        """파일을 처리해야 하는지 확인

        Debounce 로직:
        - 같은 파일이 0.5초 내에 여러 번 변경되면 첫 번째만 처리
        """
        now = time.time()
        last_time = self.last_modified.get(file_path, 0)

        if now - last_time < self.debounce_seconds:
            return False

        self.last_modified[file_path] = now
        return True

    def on_modified(self, event):
        """파일 수정 이벤트"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Python 파일만 처리
        if file_path.suffix != ".py":
            return

        # 임시 파일 무시
        if file_path.name.startswith(".") or "__pycache__" in str(file_path):
            return

        # Debounce 체크
        if not self._should_process(str(file_path)):
            return

        print(f"[FileMonitor] Detected change: {file_path}")
        self.on_file_changed(file_path)

    def on_created(self, event):
        """파일 생성 이벤트"""
        # 수정과 동일하게 처리
        self.on_modified(event)


class FileMonitor:
    """파일 감시 시스템

    Features:
    - 특정 디렉토리 감시
    - 재귀적 하위 디렉토리 포함
    - 시작/중지 제어
    """

    def __init__(
        self,
        watch_path: Path,
        on_file_changed: Callable[[Path], None],
        debounce_seconds: float = 0.5,
    ):
        """초기화

        Args:
            watch_path: 감시할 디렉토리
            on_file_changed: 파일 변경 콜백
            debounce_seconds: Debounce 시간
        """
        self.watch_path = watch_path
        self.on_file_changed = on_file_changed
        self.debounce_seconds = debounce_seconds

        self.observer: Observer | None = None
        self.handler: CodeFileHandler | None = None
        self._running = False

    def start(self) -> None:
        """감시 시작"""
        if self._running:
            print("[FileMonitor] Already running")
            return

        if not self.watch_path.exists():
            raise ValueError(f"Watch path does not exist: {self.watch_path}")

        self.handler = CodeFileHandler(
            on_file_changed=self.on_file_changed,
            debounce_seconds=self.debounce_seconds,
        )

        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.watch_path), recursive=True)
        self.observer.start()
        self._running = True

        print(f"[FileMonitor] Started watching: {self.watch_path}")

    def stop(self) -> None:
        """감시 중지"""
        if not self._running:
            return

        if self.observer:
            self.observer.stop()
            self.observer.join()

        self._running = False
        print("[FileMonitor] Stopped")

    def is_running(self) -> bool:
        """실행 중인지 확인"""
        return self._running


# 사용 예시
if __name__ == "__main__":

    def on_change(file_path: Path):
        """파일 변경 콜백 예시"""
        print(f"File changed: {file_path}")
        print(f"Timestamp: {datetime.now().isoformat()}")

    # 현재 디렉토리의 scripts 폴더 감시
    project_root = Path(__file__).parent.parent
    watch_dir = project_root / "scripts"

    monitor = FileMonitor(
        watch_path=watch_dir,
        on_file_changed=on_change,
        debounce_seconds=0.5,
    )

    try:
        monitor.start()
        print("Monitoring files... Press Ctrl+C to stop")

        # 무한 대기
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()
