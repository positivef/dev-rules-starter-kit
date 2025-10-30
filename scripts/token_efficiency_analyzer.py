#!/usr/bin/env python3
"""
Token Efficiency Analyzer
실제 토큰 소비 패턴을 분석하고 최적화 방안 제시
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class TokenEfficiencyAnalyzer:
    """토큰 효율성 분석기"""

    # 토큰 변환 비율 (경험적 데이터)
    BYTES_TO_TOKENS_RATIO = 0.25  # 1 byte ≈ 0.25 tokens (영어)
    BYTES_TO_TOKENS_RATIO_KR = 0.5  # 1 byte ≈ 0.5 tokens (한글)

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.cache_dir = self.project_root / ".smart_cache"
        self.cache_dir.mkdir(exist_ok=True)

    def analyze_file_reading_cost(self) -> Dict:
        """파일 읽기 토큰 비용 분석"""

        results = {"timestamp": datetime.now().isoformat(), "file_reading_costs": {}, "optimization_potential": {}}

        # 1. 프로젝트 파일 분석
        project_files = []
        for ext in [".py", ".yaml", ".md", ".json"]:
            project_files.extend(self.project_root.glob(f"**/*{ext}"))

        total_size = 0
        file_categories = {
            "small": [],  # < 1KB
            "medium": [],  # 1KB - 10KB
            "large": [],  # 10KB - 50KB
            "huge": [],  # > 50KB
        }

        for file in project_files[:100]:  # 상위 100개만 분석
            if file.is_file():
                size = file.stat().st_size
                total_size += size
                tokens = int(size * self.BYTES_TO_TOKENS_RATIO)

                if size < 1024:
                    file_categories["small"].append((file.name, size, tokens))
                elif size < 10240:
                    file_categories["medium"].append((file.name, size, tokens))
                elif size < 51200:
                    file_categories["large"].append((file.name, size, tokens))
                else:
                    file_categories["huge"].append((file.name, size, tokens))

        # 2. 카테고리별 토큰 소비
        results["file_reading_costs"] = {
            "small_files": {
                "count": len(file_categories["small"]),
                "avg_tokens": sum(t for _, _, t in file_categories["small"]) // max(len(file_categories["small"]), 1),
                "total_tokens": sum(t for _, _, t in file_categories["small"]),
            },
            "medium_files": {
                "count": len(file_categories["medium"]),
                "avg_tokens": sum(t for _, _, t in file_categories["medium"]) // max(len(file_categories["medium"]), 1),
                "total_tokens": sum(t for _, _, t in file_categories["medium"]),
            },
            "large_files": {
                "count": len(file_categories["large"]),
                "avg_tokens": sum(t for _, _, t in file_categories["large"]) // max(len(file_categories["large"]), 1),
                "total_tokens": sum(t for _, _, t in file_categories["large"]),
            },
            "huge_files": {
                "count": len(file_categories["huge"]),
                "avg_tokens": sum(t for _, _, t in file_categories["huge"]) // max(len(file_categories["huge"]), 1),
                "total_tokens": sum(t for _, _, t in file_categories["huge"]),
            },
        }

        # 3. 최적화 가능성 계산
        total_tokens = sum(cat["total_tokens"] for cat in results["file_reading_costs"].values())

        # 요약 사용 시 예상 토큰 (80% 절감)
        summary_tokens = int(total_tokens * 0.2)

        # 캐시 사용 시 예상 토큰 (95% 절감)
        cache_tokens = int(total_tokens * 0.05)

        results["optimization_potential"] = {
            "current_total_tokens": total_tokens,
            "with_summaries": summary_tokens,
            "with_cache": cache_tokens,
            "savings_with_summaries": f"{(1 - summary_tokens/max(total_tokens, 1)) * 100:.1f}%",
            "savings_with_cache": f"{(1 - cache_tokens/max(total_tokens, 1)) * 100:.1f}%",
        }

        return results

    def analyze_session_recording_cost(self) -> Dict:
        """세션 기록 토큰 비용 분석"""

        # 실제 세션 시뮬레이션
        typical_session = {
            "messages": 50,  # 평균 메시지 수
            "avg_message_size": 500,  # 평균 메시지 크기 (bytes)
            "code_blocks": 10,  # 코드 블록 수
            "avg_code_size": 2000,  # 평균 코드 크기
            "file_operations": 20,  # 파일 작업 수
            "tool_calls": 30,  # 도구 호출 수
        }

        # 전체 기록 토큰 계산
        full_recording_tokens = (
            typical_session["messages"] * typical_session["avg_message_size"] * self.BYTES_TO_TOKENS_RATIO
            + typical_session["code_blocks"] * typical_session["avg_code_size"] * self.BYTES_TO_TOKENS_RATIO
            + typical_session["file_operations"] * 100  # 메타데이터
            + typical_session["tool_calls"] * 50  # 도구 호출 로그
        )

        # 최적화된 기록 (핵심만)
        optimized_recording = {
            "key_decisions": 500,  # 주요 결정사항
            "file_changes": 300,  # 파일 변경 요약
            "error_logs": 200,  # 에러 로그
            "final_state": 500,  # 최종 상태
        }

        optimized_tokens = sum(optimized_recording.values())

        return {
            "full_recording": {
                "tokens": int(full_recording_tokens),
                "size_mb": full_recording_tokens * 4 / 1024 / 1024,  # 토큰당 약 4바이트
            },
            "optimized_recording": {"tokens": optimized_tokens, "size_mb": optimized_tokens * 4 / 1024 / 1024},
            "savings": f"{(1 - optimized_tokens/full_recording_tokens) * 100:.1f}%",
        }

    def calculate_obsidian_sync_cost(self) -> Dict:
        """옵시디언 동기화 토큰 비용 계산"""

        # 옵시디언 파일 시뮬레이션
        obsidian_patterns = {
            "daily_notes": {
                "count": 30,  # 30일분
                "avg_size": 2000,  # bytes
                "frequency": "daily",
            },
            "project_docs": {"count": 20, "avg_size": 5000, "frequency": "weekly"},
            "knowledge_base": {"count": 100, "avg_size": 3000, "frequency": "rarely"},
        }

        # 빈도별 토큰 계산
        daily_tokens = (
            obsidian_patterns["daily_notes"]["count"]
            * obsidian_patterns["daily_notes"]["avg_size"]
            * self.BYTES_TO_TOKENS_RATIO
        )
        weekly_tokens = (
            obsidian_patterns["project_docs"]["count"]
            * obsidian_patterns["project_docs"]["avg_size"]
            * self.BYTES_TO_TOKENS_RATIO
            * 0.2
        )  # 20% 업데이트
        rarely_tokens = (
            obsidian_patterns["knowledge_base"]["count"]
            * obsidian_patterns["knowledge_base"]["avg_size"]
            * self.BYTES_TO_TOKENS_RATIO
            * 0.05
        )  # 5% 업데이트

        total_obsidian_tokens = daily_tokens + weekly_tokens + rarely_tokens

        # 최적화: 변경된 파일만 동기화
        optimized_tokens = total_obsidian_tokens * 0.1  # 10%만 실제 변경

        return {
            "full_sync_tokens": int(total_obsidian_tokens),
            "incremental_sync_tokens": int(optimized_tokens),
            "savings": f"{(1 - optimized_tokens/total_obsidian_tokens) * 100:.1f}%",
        }

    def generate_optimization_strategy(self) -> Dict:
        """종합 최적화 전략 생성"""

        file_cost = self.analyze_file_reading_cost()
        session_cost = self.analyze_session_recording_cost()
        obsidian_cost = self.calculate_obsidian_sync_cost()

        # 총 토큰 계산
        total_unoptimized = (
            file_cost["optimization_potential"]["current_total_tokens"]
            + session_cost["full_recording"]["tokens"]
            + obsidian_cost["full_sync_tokens"]
        )

        total_optimized = (
            file_cost["optimization_potential"]["with_cache"]
            + session_cost["optimized_recording"]["tokens"]
            + obsidian_cost["incremental_sync_tokens"]
        )

        strategy = {
            "summary": {
                "total_unoptimized_tokens": total_unoptimized,
                "total_optimized_tokens": total_optimized,
                "total_savings": f"{(1 - total_optimized/max(total_unoptimized, 1)) * 100:.1f}%",
                "cost_savings_per_session": f"${(total_unoptimized - total_optimized) * 0.00002:.2f}",  # GPT-4 가격 기준
            },
            "breakdown": {"file_reading": file_cost, "session_recording": session_cost, "obsidian_sync": obsidian_cost},
            "recommendations": self.generate_recommendations(file_cost, session_cost, obsidian_cost),
        }

        return strategy

    def generate_recommendations(self, file_cost, session_cost, obsidian_cost) -> List[Dict]:
        """최적화 권장사항 생성"""

        recommendations = []

        # 1. 파일 읽기 최적화
        if file_cost["optimization_potential"]["current_total_tokens"] > 10000:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "File Reading",
                    "action": "Implement file caching system",
                    "impact": file_cost["optimization_potential"]["savings_with_cache"],
                    "implementation": """
# 구현 예시
cache = FileCache()
if cache.is_valid(file_path):
    return cache.get_summary(file_path)
else:
    content = read_file(file_path)
    cache.update(file_path, content)
    return content
""",
                }
            )

        # 2. 세션 기록 최적화
        if session_cost["full_recording"]["tokens"] > 20000:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Session Recording",
                    "action": "Use differential recording",
                    "impact": session_cost["savings"],
                    "implementation": """
# 구현 예시
def save_session_efficiently():
    return {
        'key_decisions': extract_decisions(),
        'file_changes': get_git_diff(),
        'final_state': get_current_state()
    }
""",
                }
            )

        # 3. 옵시디언 최적화
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "Obsidian Sync",
                "action": "Implement incremental sync",
                "impact": obsidian_cost["savings"],
                "implementation": """
# 구현 예시
def sync_obsidian_incremental():
    changed_files = get_modified_since_last_sync()
    return sync_only(changed_files)
""",
            }
        )

        # 4. 종합 전략
        recommendations.append(
            {
                "priority": "CRITICAL",
                "category": "Overall Strategy",
                "action": "Implement 3-tier caching",
                "impact": "90% token reduction",
                "implementation": """
# 3-Tier Caching Strategy
Level 1: In-memory cache (hot data) - 100% savings
Level 2: File summaries (warm data) - 80% savings
Level 3: Full content (cold data) - 0% savings

def smart_load(file_path):
    if in_memory_cache.has(file_path):
        return in_memory_cache.get(file_path)
    elif summary_cache.has(file_path):
        return summary_cache.get(file_path)
    else:
        return load_full_content(file_path)
""",
            }
        )

        return recommendations


def main():
    """메인 실행 함수"""
    print("Token Efficiency Analyzer v1.0")
    print("=" * 60)

    analyzer = TokenEfficiencyAnalyzer()

    # 분석 실행
    print("\n1. Analyzing file reading costs...")
    analyzer.analyze_file_reading_cost()

    print("\n2. Analyzing session recording costs...")
    analyzer.analyze_session_recording_cost()

    print("\n3. Analyzing Obsidian sync costs...")
    analyzer.calculate_obsidian_sync_cost()

    print("\n4. Generating optimization strategy...")
    strategy = analyzer.generate_optimization_strategy()

    # 결과 출력
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    print(f"\nTotal Unoptimized Tokens: {strategy['summary']['total_unoptimized_tokens']:,}")
    print(f"Total Optimized Tokens: {strategy['summary']['total_optimized_tokens']:,}")
    print(f"Total Savings: {strategy['summary']['total_savings']}")
    print(f"Cost Savings per Session: {strategy['summary']['cost_savings_per_session']}")

    print("\n" + "=" * 60)
    print("TOP RECOMMENDATIONS")
    print("=" * 60)

    for rec in strategy["recommendations"]:
        if rec["priority"] in ["HIGH", "CRITICAL"]:
            print(f"\n[{rec['priority']}] {rec['category']}")
            print(f"Action: {rec['action']}")
            print(f"Impact: {rec['impact']}")

    # JSON 파일로 저장
    output_file = Path("RUNS") / "token_efficiency_analysis.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed analysis saved to: {output_file}")

    return strategy


if __name__ == "__main__":
    main()
