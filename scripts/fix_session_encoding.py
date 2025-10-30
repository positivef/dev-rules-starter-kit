#!/usr/bin/env python3
"""
세션 파일 인코딩 문제 수정 스크립트
잘못된 인코딩의 세션 파일을 찾아서 수정
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def check_file_encoding(filepath):
    """파일 인코딩 확인 및 문제 위치 파악"""
    encodings = ["utf-8", "cp949", "latin-1", "iso-8859-1", "windows-1252"]

    for encoding in encodings:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                content = f.read()
                # JSON 파싱 테스트
                json.loads(content)
                return encoding, None, content
        except UnicodeDecodeError as e:
            if encoding == "utf-8":
                # UTF-8에서 실패한 정확한 위치 기록
                print(f"  UTF-8 decode error at position {e.start}: byte {filepath.read_bytes()[e.start]:02x}")
        except json.JSONDecodeError as e:
            return encoding, f"JSON error: {e}", None
        except Exception:
            continue

    return None, "No valid encoding found", None


def fix_session_files():
    """모든 세션 파일의 인코딩 문제 수정"""
    session_dir = Path("RUNS/sessions")

    if not session_dir.exists():
        print("세션 디렉토리가 없습니다.")
        return

    print("=" * 60)
    print("세션 파일 인코딩 검사 및 수정")
    print("=" * 60)

    # 백업 디렉토리 생성
    backup_dir = session_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    session_files = list(session_dir.glob("session_*.json"))
    problematic_files = []
    fixed_files = []

    print(f"\n총 {len(session_files)}개 세션 파일 검사 중...")

    for filepath in session_files:
        if filepath.name.endswith(".backup.json"):
            continue

        print(f"\n검사 중: {filepath.name}")

        # 파일 인코딩 확인
        encoding, error, content = check_file_encoding(filepath)

        if encoding is None:
            print(f"  [ERROR] 읽을 수 없는 파일: {error}")
            problematic_files.append(filepath)

            # 바이트 레벨 분석
            try:
                raw_bytes = filepath.read_bytes()
                print(f"  파일 크기: {len(raw_bytes)} bytes")

                # 문제가 되는 위치 주변 바이트 출력 (position 85 주변)
                if len(raw_bytes) > 85:
                    print(f"  Bytes 80-90: {raw_bytes[80:90]}")
                    print(f"  Byte at 85: 0x{raw_bytes[85]:02x}")

                    # CP949로 디코딩 시도
                    try:
                        # 부분적으로 읽어서 문제 부분 건너뛰기
                        text_before = raw_bytes[:85].decode("utf-8", errors="ignore")
                        text_after = raw_bytes[86:].decode("utf-8", errors="ignore")

                        # JSON 구조 복구 시도
                        combined = text_before + "?" + text_after

                        # JSON으로 파싱 가능한지 테스트
                        try:
                            # 간단한 복구 시도
                            fixed_content = combined.replace("\x8e", "").replace("\x00", "")
                            json_data = json.loads(fixed_content)

                            # 백업
                            backup_path = backup_dir / f"{filepath.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            shutil.copy2(filepath, backup_path)
                            print(f"  백업 생성: {backup_path.name}")

                            # 수정된 내용 저장
                            with open(filepath, "w", encoding="utf-8") as f:
                                json.dump(json_data, f, indent=2, ensure_ascii=False)

                            print("  [FIXED] 파일 복구 성공!")
                            fixed_files.append(filepath)

                        except json.JSONDecodeError:
                            print("  [FAIL] JSON 복구 실패")
                    except Exception as e:
                        print(f"  [FAIL] 복구 시도 실패: {e}")

            except Exception as e:
                print(f"  [ERROR] 바이트 분석 실패: {e}")

        elif encoding != "utf-8":
            print(f"  [WARNING] {encoding} 인코딩 사용 중")

            if content:
                try:
                    # JSON 파싱
                    json_data = json.loads(content)

                    # 백업
                    backup_path = backup_dir / f"{filepath.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(filepath, backup_path)
                    print(f"  백업 생성: {backup_path.name}")

                    # UTF-8로 재저장
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)

                    print("  [FIXED] UTF-8로 변환 완료")
                    fixed_files.append(filepath)

                except Exception as e:
                    print(f"  [ERROR] 변환 실패: {e}")
                    problematic_files.append(filepath)
        else:
            print("  [OK] UTF-8 정상")

    # 결과 요약
    print("\n" + "=" * 60)
    print("수정 결과")
    print("=" * 60)
    print(f"총 파일: {len(session_files)}개")
    print(f"정상: {len(session_files) - len(problematic_files) - len(fixed_files)}개")
    print(f"수정됨: {len(fixed_files)}개")
    print(f"문제 파일: {len(problematic_files)}개")

    if problematic_files:
        print("\n복구할 수 없는 파일:")
        for f in problematic_files:
            print(f"  - {f.name}")

        print("\n권장 조치:")
        print("1. 문제 파일을 삭제하거나")
        print("2. 백업에서 복구하거나")
        print("3. 새로운 세션으로 시작하세요")

        # 문제 파일 삭제 옵션
        response = input("\n문제 파일을 삭제하시겠습니까? (y/n): ")
        if response.lower() == "y":
            for f in problematic_files:
                try:
                    # 백업 후 삭제
                    backup_path = backup_dir / f"problematic_{f.name}"
                    shutil.move(str(f), str(backup_path))
                    print(f"  {f.name} -> backup/problematic_{f.name} 이동됨")
                except Exception as e:
                    print(f"  {f.name} 이동 실패: {e}")
            print("\n문제 파일들이 backup 디렉토리로 이동되었습니다.")

    if fixed_files:
        print(f"\n{len(fixed_files)}개 파일이 UTF-8로 수정되었습니다.")
        print("원본 파일은 backup 디렉토리에 보관되었습니다.")

    return len(problematic_files) == 0


def clean_invalid_sessions():
    """읽을 수 없는 세션 파일 정리"""
    session_dir = Path("RUNS/sessions")
    backup_dir = session_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    print("\n무효한 세션 파일 정리 중...")

    for filepath in session_dir.glob("session_*.json"):
        if filepath.name.endswith(".backup.json"):
            continue

        try:
            # UTF-8로 읽기 시도
            with open(filepath, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception:
            # 읽을 수 없는 파일은 백업으로 이동
            backup_path = backup_dir / f"invalid_{filepath.name}"
            shutil.move(str(filepath), str(backup_path))
            print(f"  {filepath.name} -> backup/invalid_{filepath.name}")

    print("정리 완료")


def main():
    """메인 함수"""
    success = fix_session_files()

    if success:
        print("\n✅ 모든 세션 파일이 정상입니다.")
        print("이제 대시보드를 실행할 수 있습니다:")
        print("  streamlit run scripts/session_dashboard.py")
    else:
        print("\n⚠️ 일부 파일에 문제가 있습니다.")
        print("문제 파일을 정리한 후 다시 시도하세요.")

    return success


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
