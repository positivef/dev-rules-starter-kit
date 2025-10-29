#!/usr/bin/env python3
"""
문제가 되는 세션 파일을 정확히 찾는 스크립트
"""

import json
from pathlib import Path


def find_problematic_byte():
    """바이트 0x8e가 위치 85에 있는 파일 찾기"""

    session_dir = Path("RUNS/sessions")
    print("=" * 60)
    print("Searching for byte 0x8e at position 85")
    print("=" * 60)

    for filepath in session_dir.glob("*.json"):
        if filepath.name.endswith(".backup.json"):
            continue

        try:
            # 바이트로 읽기
            raw_bytes = filepath.read_bytes()

            # position 85 확인
            if len(raw_bytes) > 85:
                if raw_bytes[85] == 0x8E:
                    print(f"\n[FOUND] Problem file: {filepath.name}")
                    print(f"  Byte at position 85: 0x{raw_bytes[85]:02x}")
                    print(f"  Bytes 80-90: {raw_bytes[80:90]}")

                    # 주변 컨텍스트 출력
                    try:
                        before = raw_bytes[:85].decode("utf-8", errors="replace")
                        after = raw_bytes[86:].decode("utf-8", errors="replace")
                        print(f"  Context before: ...{before[-20:]}")
                        print(f"  Context after: {after[:20]}...")
                    except:
                        pass

                    return filepath

            # UTF-8 디코딩 테스트
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    json.load(f)
            except UnicodeDecodeError as e:
                print(f"\n[ERROR] UTF-8 decode error in {filepath.name}")
                print(f"  Position: {e.start}")
                print(f"  Reason: {e.reason}")

                # 문제 바이트 확인
                if len(raw_bytes) > e.start:
                    print(f"  Byte at error position: 0x{raw_bytes[e.start]:02x}")
                    print(f"  Bytes around error: {raw_bytes[max(0, e.start-5):e.start+5]}")

                return filepath

        except Exception as e:
            print(f"Error checking {filepath.name}: {e}")

    print("\nNo file found with byte 0x8e at position 85")
    return None


def check_all_json_files():
    """RUNS 디렉토리의 모든 JSON 파일 확인"""

    print("\n" + "=" * 60)
    print("Checking ALL JSON files in RUNS directory")
    print("=" * 60)

    runs_dir = Path("RUNS")
    problematic_files = []

    for json_file in runs_dir.rglob("*.json"):
        if json_file.name.endswith(".backup.json"):
            continue

        try:
            # UTF-8로 읽기 시도
            with open(json_file, "r", encoding="utf-8") as f:
                json.load(f)
        except UnicodeDecodeError as e:
            print(f"\n[PROBLEM] {json_file.relative_to(runs_dir)}")
            print(f"  Error at position: {e.start}")

            # 바이트 레벨 분석
            raw_bytes = json_file.read_bytes()
            if len(raw_bytes) > e.start:
                print(f"  Problem byte: 0x{raw_bytes[e.start]:02x}")

                # position 85 확인
                if e.start == 85:
                    print("  [MATCH] This is the file causing the dashboard error!")
                    problematic_files.append(json_file)

        except json.JSONDecodeError:
            pass  # JSON 구조 에러는 무시
        except Exception as e:
            print(f"Error with {json_file}: {e}")

    if problematic_files:
        print("\n" + "=" * 60)
        print(f"Found {len(problematic_files)} problematic file(s):")
        for f in problematic_files:
            print(f"  - {f}")
        print("=" * 60)
    else:
        print("\nNo files with UTF-8 decode errors found")

    return problematic_files


def check_executio_logs():
    """execution 로그 파일 확인"""

    print("\n" + "=" * 60)
    print("Checking execution log files")
    print("=" * 60)

    # 가능한 경로들
    paths_to_check = [
        Path("RUNS/sessions"),
        Path("RUNS"),
        Path("RUNS/evidence"),
        Path("RUNS/logs"),
    ]

    for base_path in paths_to_check:
        if not base_path.exists():
            continue

        for file in base_path.glob("*execution*.json"):
            print(f"Checking: {file}")

            try:
                raw_bytes = file.read_bytes()

                # position 85 확인
                if len(raw_bytes) > 85 and raw_bytes[85] == 0x8E:
                    print("  [FOUND] Problem at position 85!")
                    return file

                # UTF-8 테스트
                with open(file, "r", encoding="utf-8") as f:
                    json.load(f)

            except UnicodeDecodeError as e:
                print(f"  [ERROR] at position {e.start}")
                if e.start == 85:
                    print("  [MATCH] This is the problem file!")
                    return file
            except:
                pass

    return None


def main():
    """메인 함수"""

    # 1. 정확한 문제 파일 찾기
    problem_file = find_problematic_byte()

    # 2. 모든 JSON 파일 확인
    all_problems = check_all_json_files()

    # 3. execution 로그 확인
    exec_problem = check_executio_logs()

    # 결과 출력
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if problem_file:
        print(f"Problem file found: {problem_file}")
        print("\nSolution: Delete or fix this file:")
        print(f"  del {problem_file}")
    elif exec_problem:
        print(f"Problem in execution log: {exec_problem}")
        print("\nSolution: Delete or fix this file:")
        print(f"  del {exec_problem}")
    elif all_problems:
        print(f"Found {len(all_problems)} problematic files")
        print("\nSolution: Delete these files:")
        for f in all_problems:
            print(f"  del {f}")
    else:
        print("No problematic files found in RUNS directory")
        print("\nThe issue might be in:")
        print("  1. SessionAnalyzer code itself")
        print("  2. Streamlit's internal handling")
        print("  3. Other data sources")

    return problem_file or exec_problem or bool(all_problems)


if __name__ == "__main__":
    import sys

    found = main()
    sys.exit(0 if not found else 1)
