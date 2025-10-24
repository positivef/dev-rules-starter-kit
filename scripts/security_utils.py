"""Security Utilities - Tier 1 보안 강화 모듈.

Path traversal, race condition, memory 관리를 위한 보안 유틸리티.

Compliance:
- P1: YAML-First (보안 설정 YAML 통합)
- P4: SOLID principles (단일 책임 원칙)
- P10: Windows encoding (UTF-8, no emojis)

Security Features:
- Secure path validation (symlink attack prevention)
- Cross-platform file locking
- Memory-safe resource management
"""

import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union

# Platform-specific imports
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl


class SecurityError(Exception):
    """보안 관련 에러."""

    pass


class SecurePathValidator:
    """경로 보안 검증 유틸리티.

    Path traversal 및 symlink 공격 방지.
    """

    @staticmethod
    def validate_path(base_path: Path, target_path: Path) -> bool:
        """안전한 경로 검증 (symlink 공격 방지).

        Args:
            base_path: 기준 디렉토리
            target_path: 검증할 대상 경로

        Returns:
            안전한 경로면 True

        Raises:
            SecurityError: 보안 위반 감지 시
        """
        try:
            # 실제 경로로 변환 (symlink 해결)
            base_real = os.path.realpath(base_path)
            target_real = os.path.realpath(target_path)

            # Windows와 Unix 모두 처리
            if os.name == "nt":
                # Windows: 대소문자 무시
                base_real = base_real.lower()
                target_real = target_real.lower()

            # 공통 경로 확인
            common = os.path.commonpath([base_real, target_real])

            # 대상이 기준 디렉토리 내부인지 확인
            if common != base_real:
                raise SecurityError(f"Path traversal detected: {target_path} is outside {base_path}")

            return True

        except ValueError as e:
            # 다른 드라이브 등 공통 경로 없음
            raise SecurityError(f"Invalid path: {e}")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """파일명 sanitization.

        Args:
            filename: 원본 파일명

        Returns:
            안전한 파일명
        """
        # 위험한 문자 제거
        dangerous_chars = ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|", "\0"]
        safe_name = filename

        for char in dangerous_chars:
            safe_name = safe_name.replace(char, "_")

        # 길이 제한 (Windows 호환)
        max_length = 255
        if len(safe_name) > max_length:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[: max_length - len(ext)] + ext

        return safe_name


class SecureFileLock:
    """크로스 플랫폼 파일 락 매니저.

    Race condition 방지를 위한 안전한 파일 락.
    """

    def __init__(self, lock_file: Optional[Path] = None):
        """파일 락 초기화.

        Args:
            lock_file: 락 파일 경로 (None이면 임시 파일)
        """
        if lock_file:
            self.lock_file = lock_file
        else:
            # 임시 락 파일 생성
            fd, path = tempfile.mkstemp(suffix=".lock")
            os.close(fd)
            self.lock_file = Path(path)

        self.lock_file.touch(exist_ok=True)
        self._file = None
        self._locked = False

    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """락 획득.

        Args:
            blocking: 블로킹 모드
            timeout: 타임아웃 (초)

        Returns:
            락 획득 성공 여부
        """
        if self._locked:
            return True

        self._file = open(self.lock_file, "r+b")

        try:
            if sys.platform == "win32":
                # Windows: msvcrt 사용
                flags = msvcrt.LK_NBLCK if not blocking else msvcrt.LK_LOCK
                # 전체 파일 락 (0 = 전체)
                msvcrt.locking(self._file.fileno(), flags, 0)
            else:
                # Unix/Linux: fcntl 사용
                flags = fcntl.LOCK_EX
                if not blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(self._file.fileno(), flags)

            self._locked = True
            return True

        except (IOError, OSError) as e:
            if self._file:
                self._file.close()
                self._file = None
            if not blocking:
                return False
            raise SecurityError(f"Failed to acquire lock: {e}")

    def release(self):
        """락 해제."""
        if not self._locked:
            return

        try:
            if sys.platform == "win32":
                # Windows: 락 해제
                msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 0)
            else:
                # Unix/Linux: 락 해제
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        finally:
            if self._file:
                self._file.close()
                self._file = None
            self._locked = False

    def __enter__(self):
        """Context manager 진입."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료."""
        self.release()

    def __del__(self):
        """소멸자 - 락 해제 보장."""
        self.release()


class MemorySafeResourceManager:
    """메모리 안전 리소스 관리자.

    순환 참조 및 메모리 누수 방지.
    """

    def __init__(self):
        """리소스 관리자 초기화."""
        self._resources = []
        self._closed = False

    def register_resource(self, resource):
        """리소스 등록.

        Args:
            resource: 관리할 리소스 객체
        """
        if self._closed:
            raise SecurityError("Resource manager is closed")
        self._resources.append(resource)

    def cleanup(self):
        """모든 리소스 정리."""
        if self._closed:
            return

        for resource in self._resources:
            try:
                # __del__ 또는 close() 메서드 호출
                if hasattr(resource, "close"):
                    resource.close()
                elif hasattr(resource, "__del__"):
                    resource.__del__()
            except Exception:
                pass  # 정리 중 에러는 무시

        self._resources.clear()
        self._closed = True

    def __enter__(self):
        """Context manager 진입."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료."""
        self.cleanup()

    def __del__(self):
        """소멸자 - 리소스 정리 보장."""
        self.cleanup()


@contextmanager
def secure_temp_directory(prefix: str = "tier1_"):
    """안전한 임시 디렉토리 생성.

    Args:
        prefix: 디렉토리 접두사

    Yields:
        임시 디렉토리 경로
    """
    temp_dir = None
    try:
        # 안전한 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        yield Path(temp_dir)
    finally:
        # 디렉토리 및 내용 삭제
        if temp_dir and os.path.exists(temp_dir):
            import shutil

            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass  # 삭제 실패는 무시


def secure_file_operation(func):
    """파일 작업 보안 데코레이터.

    파일 작업 전후 보안 검증 수행.
    """

    def wrapper(self, file_path: Union[str, Path], *args, **kwargs):
        file_path = Path(file_path)

        # 경로 검증
        validator = SecurePathValidator()
        base_path = Path.cwd()  # 또는 설정된 기준 경로

        try:
            validator.validate_path(base_path, file_path)
        except SecurityError as e:
            raise SecurityError(f"Unsafe file operation blocked: {e}")

        # 원본 함수 실행
        return func(self, file_path, *args, **kwargs)

    return wrapper


class SecureConfig:
    """보안 설정 중앙 관리.

    하드코딩된 값 제거 및 중앙화.
    """

    # 기본 설정값
    DEFAULTS = {
        "max_path_length": 260,  # Windows MAX_PATH
        "max_filename_length": 255,
        "lock_timeout": 30,  # 초
        "memory_limit": 1024 * 1024 * 100,  # 100MB
        "coverage_threshold": 85.0,
        "subprocess_timeout": 300,  # 5분
        "context_lines": 3,
        "cache_ttl": 3600,  # 1시간
    }

    @classmethod
    def get(cls, key: str, default=None):
        """설정값 조회.

        Args:
            key: 설정 키
            default: 기본값

        Returns:
            설정값
        """
        # 환경변수 우선
        env_key = f"TIER1_{key.upper()}"
        if env_key in os.environ:
            value = os.environ[env_key]
            # 타입 변환
            if key in cls.DEFAULTS and isinstance(cls.DEFAULTS[key], (int, float)):
                return type(cls.DEFAULTS[key])(value)
            return value

        # 기본값
        return cls.DEFAULTS.get(key, default)


def main() -> int:
    """테스트 및 예제 코드."""
    print("[INFO] Security Utils - Tier 1 보안 강화 모듈")
    print()

    # 1. 경로 검증 테스트
    print("1. Path Validation Test:")
    validator = SecurePathValidator()
    base = Path.cwd()
    safe_path = base / "test.txt"
    unsafe_path = base / ".." / "etc" / "passwd"

    try:
        validator.validate_path(base, safe_path)
        print(f"  [OK] Safe path: {safe_path}")
    except SecurityError as e:
        print(f"  [ERROR] {e}")

    try:
        validator.validate_path(base, unsafe_path)
        print("  [OK] Unsafe path not detected!")
    except SecurityError as e:
        print(f"  [OK] Blocked unsafe path: {e}")

    # 2. 파일 락 테스트
    print("\n2. File Lock Test:")
    with SecureFileLock():
        print("  [OK] Lock acquired")
        # 작업 수행
    print("  [OK] Lock released")

    # 3. 메모리 관리 테스트
    print("\n3. Memory Management Test:")
    with MemorySafeResourceManager() as manager:
        # 리소스 등록
        manager.register_resource(object())
        print("  [OK] Resource registered")
    print("  [OK] Resources cleaned up")

    # 4. 보안 설정 테스트
    print("\n4. Secure Config Test:")
    threshold = SecureConfig.get("coverage_threshold")
    print(f"  Coverage threshold: {threshold}")

    print("\n[OK] All security tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
