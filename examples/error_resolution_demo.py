#!/usr/bin/env python3
"""
Hybrid Error Resolution 사용 예제

이 파일은 UnifiedErrorResolver를 직접 사용하는 방법을 보여줍니다.
"""

import sys
from pathlib import Path

# UnifiedErrorResolver import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from unified_error_resolver import UnifiedErrorResolver


def example_1_basic_usage():
    """예제 1: 기본 사용법 - ModuleNotFoundError"""
    print("=" * 70)
    print("예제 1: 기본 사용법")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # 에러 발생 시뮬레이션
    error_msg = "ModuleNotFoundError: No module named 'requests'"
    context = {"tool": "Python", "script": "app.py", "command": "import requests"}

    print(f"\n에러: {error_msg}")
    print("해결 시도 중...\n")

    # 해결 시도
    solution = resolver.resolve_error(error_msg, context)

    # 결과 처리
    if solution:
        print("\n[SUCCESS] 자동 해결됨!")
        print(f"솔루션: {solution}")
        print("\n이제 이 명령을 실행하면 됩니다:")
        print(f"  $ {solution}")
    else:
        print("\n[CONFIRM] 사용자 확인 필요")
        print("AI가 제안을 했지만 확인이 필요합니다.")

    # 통계 확인
    stats = resolver.get_statistics()
    print("\n[STATS] 통계:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']}")
    print(f"  - Tier 2 Auto: {stats['tier2_auto']}")
    print(f"  - Tier 3 (User): {stats['tier3']}")
    print(f"  - 자동화율: {stats['automation_rate']:.0%}")


def example_2_medium_confidence():
    """예제 2: MEDIUM confidence - 사용자 확인 필요"""
    print("\n\n" + "=" * 70)
    print("예제 2: MEDIUM Confidence - 사용자 확인")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # ImportError는 MEDIUM confidence
    error_msg = "ImportError: cannot import name 'SpecialClass' from 'mymodule'"
    context = {"tool": "Python", "script": "app.py", "line": 42}

    print(f"\n에러: {error_msg}")
    print("해결 시도 중...\n")

    solution = resolver.resolve_error(error_msg, context)

    if solution:
        print(f"\n✅ 자동 해결: {solution}")
    else:
        print("\n⚠️ 사용자 확인 필요!")
        print("Context7가 제안했지만 신뢰도가 MEDIUM입니다.")
        print("\n제안된 솔루션: pip install mymodule")
        print("적용할까요? (y/n)")

        # 실제로는 여기서 사용자 입력을 받음
        user_input = "y"  # 시뮬레이션

        if user_input.lower() == "y":
            # 사용자가 확인하면 Obsidian에 저장
            resolver.save_user_solution(error_msg, "pip install mymodule", context)
            print("\n✅ 솔루션 저장됨! 다음번엔 자동으로 해결됩니다.")


def example_3_low_confidence():
    """예제 3: LOW confidence - 완전한 사용자 개입"""
    print("\n\n" + "=" * 70)
    print("예제 3: LOW Confidence - 사용자 개입")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # 비즈니스 로직 에러는 LOW confidence
    error_msg = "ValidationError: Payment amount exceeds daily limit"
    context = {"tool": "Python", "script": "payment.py", "function": "process_payment"}

    print(f"\n에러: {error_msg}")
    print("해결 시도 중...\n")

    solution = resolver.resolve_error(error_msg, context)

    if solution:
        print(f"\n✅ 자동 해결: {solution}")
    else:
        print("\n❌ 자동 해결 불가능")
        print("이 에러는 비즈니스 로직 관련으로 사람의 판단이 필요합니다.")
        print("\n어떻게 해결하시겠습니까?")

        # 실제로는 여기서 사용자가 솔루션을 입력
        user_solution = "Check payment config: MAX_DAILY_LIMIT in .env"

        # 사용자 솔루션 저장
        resolver.save_user_solution(error_msg, user_solution, context)
        print(f"\n✅ 솔루션 저장: {user_solution}")
        print("다음번 동일한 에러 발생 시 즉시 해결됩니다!")


def example_4_statistics():
    """예제 4: 통계 확인"""
    print("\n\n" + "=" * 70)
    print("예제 4: 통계 확인")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # 여러 에러 처리
    errors = [
        ("ModuleNotFoundError: No module named 'numpy'", {}),
        ("ModuleNotFoundError: No module named 'pandas'", {}),
        ("ImportError: cannot import from 'scipy'", {}),
    ]

    for error, ctx in errors:
        solution = resolver.resolve_error(error, ctx)
        if solution:
            print(f"✅ {error[:50]}... → {solution}")
        else:
            print(f"❓ {error[:50]}... → 사용자 확인 필요")

    # 최종 통계
    stats = resolver.get_statistics()

    print("\n\n📊 최종 통계:")
    print(f"총 해결 시도: {stats['total']}")
    print("\nTier별 분포:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']} ({stats['tier1_percentage']:.0%})")
    print(f"  - Tier 2 (Context7): {stats['tier2']} ({stats['tier2_percentage']:.0%})")
    print(f"    - AUTO 적용: {stats['tier2_auto']}")
    print(f"    - 사용자 확인: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']} ({stats['tier3_percentage']:.0%})")
    print(f"\n자동화율: {stats['automation_rate']:.0%}")
    print("\n평균 속도:")
    print(f"  - Tier 1: {stats['tier1_avg_time']:.2f}ms")
    print(f"  - Tier 2: {stats['tier2_avg_time']:.2f}ms")


def example_5_circuit_breaker():
    """예제 5: Circuit Breaker 테스트"""
    print("\n\n" + "=" * 70)
    print("예제 5: Circuit Breaker 안전장치")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Circuit breaker 상태 확인
    if resolver.circuit_breaker:
        print(f"Circuit Breaker 활성화: {resolver.circuit_breaker.enabled}")
        print(f"최대 실패 허용: {resolver.circuit_breaker.max_failures}번")

        # 실패 시뮬레이션
        print("\n실패 3번 시뮬레이션...")
        resolver.circuit_breaker.record_auto_apply(False)
        print("  1번 실패 기록")
        resolver.circuit_breaker.record_auto_apply(False)
        print("  2번 실패 기록")
        resolver.circuit_breaker.record_auto_apply(False)
        print("  3번 실패 기록")

        # 상태 확인
        if not resolver.circuit_breaker.is_auto_apply_allowed():
            print("\n⚠️ Circuit Breaker 작동!")
            print("자동 적용이 일시 중단되었습니다.")
            print("모든 솔루션이 사용자 확인 모드로 전환됩니다.")

        # 리셋
        resolver.circuit_breaker.reset()
        print("\n🔄 Circuit Breaker 리셋 완료")
        print("자동 적용이 다시 활성화되었습니다.")


def example_6_custom_config():
    """예제 6: 설정 커스터마이징"""
    print("\n\n" + "=" * 70)
    print("예제 6: 설정 확인")
    print("=" * 70)

    print("\n현재 설정 파일:")
    print("  config/error_resolution_config.yaml")

    print("\n주요 설정:")
    print("  confidence_thresholds:")
    print("    auto_apply: 0.95  (95% 이상 자동 적용)")
    print("    ask_confirm: 0.70 (70-95% 사용자 확인)")

    print("\n  circuit_breaker:")
    print("    enabled: true")
    print("    max_failures: 3  (3번 실패 시 비활성화)")

    print("\n  블랙리스트 (절대 자동 적용 안 됨):")
    print("    - sudo")
    print("    - rm -rf")
    print("    - database")
    print("    - payment")
    print("    - auth")

    print("\n  화이트리스트 (자동 적용 허용):")
    print("    - pip install pandas")
    print("    - pip install numpy")
    print("    - npm install react")
    print("    - chmod +x")


def main():
    """모든 예제 실행"""
    print("\n")
    print("=" * 70)
    print(" " * 10 + "Hybrid Error Resolution 사용 예제")
    print("=" * 70)

    try:
        example_1_basic_usage()
        example_2_medium_confidence()
        example_3_low_confidence()
        example_4_statistics()
        example_5_circuit_breaker()
        example_6_custom_config()

        print("\n\n" + "=" * 70)
        print("모든 예제 완료!")
        print("=" * 70)
        print("\n📚 더 많은 정보:")
        print("  - Quick Start: docs/HYBRID_ERROR_RESOLUTION_QUICKSTART.md")
        print("  - README: README.md (line 371-502)")
        print("  - 위험 분석: claudedocs/HYBRID_RESOLUTION_RISK_ANALYSIS.md")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
