#!/usr/bin/env python3
"""
Python 파일에서 문제가 되는 바이트 찾기
"""

from pathlib import Path


def check_python_files():
    """모든 Python 파일에서 byte 0x8e 찾기"""

    print("=" * 60)
    print("Checking Python files for byte 0x8e at position 85")
    print("=" * 60)

    # 대시보드 관련 파일들
    files_to_check = [
        Path("scripts/session_dashboard.py"),
        Path("scripts/session_analyzer.py"),
        Path("scripts/session_manager.py"),
        Path("scripts/task_executor_session_hook.py"),
        Path("scripts/session_report_generator.py"),
    ]

    # scripts 디렉토리의 모든 Python 파일
    scripts_dir = Path("scripts")
    for py_file in scripts_dir.glob("session*.py"):
        if py_file not in files_to_check:
            files_to_check.append(py_file)

    found_problems = []

    for filepath in files_to_check:
        if not filepath.exists():
            continue

        print(f"\nChecking: {filepath.name}")

        try:
            # 바이트로 읽기
            raw_bytes = filepath.read_bytes()

            # position 85 확인
            if len(raw_bytes) > 85:
                if raw_bytes[85] == 0x8E:
                    print("  [FOUND] Byte 0x8e at position 85!")
                    print(f"  Bytes 80-90: {raw_bytes[80:90]}")
                    found_problems.append(filepath)

                # 전체 파일에서 0x8e 검색
                positions = [i for i, b in enumerate(raw_bytes) if b == 0x8E]
                if positions:
                    print(f"  Found byte 0x8e at positions: {positions[:5]}...")

            # UTF-8 디코딩 테스트
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 라인별로 확인
                    lines = content.split("\n")
                    for i, line in enumerate(lines[:10], 1):  # 처음 10줄
                        if any(ord(c) > 127 for c in line):
                            print(f"  Line {i}: Non-ASCII characters found")
                            print(f"    {line[:100]}")

            except UnicodeDecodeError as e:
                print(f"  [ERROR] UTF-8 decode error at position {e.start}")
                print(f"  Problem byte: 0x{raw_bytes[e.start]:02x}")
                found_problems.append(filepath)

        except Exception as e:
            print(f"  Error: {e}")

    # 결과 출력
    print("\n" + "=" * 60)
    if found_problems:
        print(f"Found {len(found_problems)} problematic file(s):")
        for f in found_problems:
            print(f"  - {f}")
        print("\nSolution: Fix encoding in these files")
    else:
        print("No byte 0x8e found at position 85 in Python files")
        print("\nThe issue might be in:")
        print("  1. Streamlit's internal files")
        print("  2. Dynamic data generation")
        print("  3. System encoding settings")

    return found_problems


def check_streamlit_cache():
    """Streamlit 캐시 확인"""

    print("\n" + "=" * 60)
    print("Checking Streamlit cache")
    print("=" * 60)

    cache_dirs = [
        Path.home() / ".streamlit/cache",
        Path("~/.streamlit/cache").expanduser(),
        Path(".streamlit/cache"),
    ]

    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"Found cache: {cache_dir}")
            # 캐시 정리 권장
            print("  Recommendation: Clear Streamlit cache")
            print(f"  rmdir /s /q {cache_dir}")


def main():
    """메인 함수"""

    # Python 파일 확인
    problems = check_python_files()

    # Streamlit 캐시 확인
    check_streamlit_cache()

    # 환경 변수 확인
    print("\n" + "=" * 60)
    print("Environment variable check")
    print("=" * 60)
    import os

    pythonioencoding = os.environ.get("PYTHONIOENCODING", "Not set")
    print(f"PYTHONIOENCODING: {pythonioencoding}")

    if pythonioencoding != "utf-8":
        print("\nRecommendation: Set environment variable")
        print("  set PYTHONIOENCODING=utf-8")

    # Streamlit 실행 권장사항
    print("\n" + "=" * 60)
    print("Recommended fixes")
    print("=" * 60)
    print("1. Clear Streamlit cache (if exists)")
    print("2. Set environment variable:")
    print("   set PYTHONIOENCODING=utf-8")
    print("3. Run with explicit encoding:")
    print("   python -X utf8 -m streamlit run scripts/session_dashboard.py")
    print("4. Or use the fixed launcher:")
    print("   run_dashboard.bat")

    return len(problems) == 0


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
