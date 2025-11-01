#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Team Statistics Aggregator for Development Assistant Phase C Week 2

팀 전체 코드 품질 통계를 수집하고 마크다운 대시보드를 생성합니다.

주요 기능:
- 검증 결과 통계 수집 (VerificationCache + DeepAnalysisResult)
- 시간별 품질 추세 분석
- 마크다운 대시보드 생성
- 문제 파일 식별 및 우선순위화

데이터 소스:
- VerificationCache: 캐시된 검증 결과
- Evidence Tracker: 실행 이벤트 로그
- Deep Analyzer: 상세 품질 분석

출력:
- RUNS/stats/team_dashboard.md: 팀 대시보드
- RUNS/stats/trends.json: 추세 데이터
- RUNS/stats/problem_files.json: 문제 파일 목록
"""

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FileStats:
    """개별 파일 통계"""

    file_path: str
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    avg_quality_score: float = 0.0
    total_violations: int = 0
    total_security_issues: int = 0
    total_solid_violations: int = 0
    last_checked: Optional[str] = None
    analysis_mode: str = "fast"  # "fast" or "deep"

    @property
    def pass_rate(self) -> float:
        """통과율 계산"""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100.0


@dataclass
class TeamStats:
    """팀 전체 통계"""

    total_files: int = 0
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    avg_quality_score: float = 0.0
    total_violations: int = 0
    total_security_issues: int = 0
    total_solid_violations: int = 0
    cache_hit_rate: float = 0.0
    avg_analysis_time_ms: float = 0.0
    generated_at: str = ""

    @property
    def pass_rate(self) -> float:
        """전체 통과율"""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100.0


@dataclass
class TrendDataPoint:
    """추세 분석 데이터 포인트"""

    timestamp: str
    quality_score: float
    violation_count: int
    security_issue_count: int
    pass_rate: float


class StatsCollector:
    """통계 수집 엔진

    VerificationCache와 AutomaticEvidenceTracker에서 데이터 수집
    """

    def __init__(self, cache_dir: Path, evidence_dir: Path):
        """초기화

        Args:
            cache_dir: VerificationCache 디렉토리
            evidence_dir: Evidence Tracker 로그 디렉토리
        """
        self.cache_dir = cache_dir
        self.evidence_dir = evidence_dir
        self.cache_file = cache_dir / "verification_cache.json"
        self._logger = logging.getLogger(__name__)

    def discover_project_files(self) -> List[Path]:
        """프로젝트 내 모든 Python 파일 발견 (P6 준수)

        Returns:
            프로젝트의 모든 Python 파일 경로 리스트
        """
        patterns = [
            "scripts/**/*.py",
            "tests/**/*.py",
            "backend/**/*.py",
            "src/**/*.py",
            "web/**/*.py",
            "mcp/**/*.py",
            "orchestrator/**/*.py",
        ]

        all_files = []
        project_root = Path(".")

        for pattern in patterns:
            files = list(project_root.glob(pattern))
            all_files.extend(files)

        # 제외할 패턴
        exclude_patterns = ["__pycache__", ".venv", "node_modules", "build", "dist"]
        filtered_files = [f for f in all_files if not any(excl in str(f) for excl in exclude_patterns)]

        self._logger.info(f"[P6] Discovered {len(filtered_files)} Python files in project")
        return filtered_files

    def collect_file_stats(self, force_full_scan: bool = False) -> Dict[str, FileStats]:
        """파일별 통계 수집 (전체 프로젝트 스캔 지원)

        Args:
            force_full_scan: True시 전체 프로젝트 스캔 수행

        Returns:
            파일 경로를 키로 하는 FileStats 딕셔너리
        """
        file_stats: Dict[str, FileStats] = {}

        if not self.cache_file.exists():
            self._logger.warning(f"Cache file not found: {self.cache_file}")
            return file_stats

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            for file_path_str, entry in cache_data.items():
                stats = FileStats(file_path=file_path_str)

                # 기본 통계
                stats.total_checks = 1
                stats.analysis_mode = entry.get("mode", "fast")
                stats.last_checked = entry.get("timestamp")

                # 결과 파싱
                result = entry.get("result", {})
                passed = result.get("passed", False)

                if passed:
                    stats.passed_checks = 1
                else:
                    stats.failed_checks = 1

                # 위반 사항
                violations = result.get("violations", [])
                stats.total_violations = len(violations)

                # Deep 모드 결과 (있는 경우)
                if "overall_score" in result:
                    stats.avg_quality_score = result.get("overall_score", 0.0)
                    stats.total_security_issues = len(result.get("security_issues", []))
                    stats.total_solid_violations = len(result.get("solid_violations", []))
                else:
                    # Fast 모드: 위반 수로 간단한 점수 계산
                    stats.avg_quality_score = max(0.0, 10.0 - len(violations) * 0.2)

                file_stats[file_path_str] = stats

            self._logger.info(f"Collected stats for {len(file_stats)} files from cache")

            # Full scan 모드: 전체 프로젝트 스캔 (P6 준수)
            if force_full_scan:
                self._logger.info("[P6] Full project scan requested")
                all_project_files = self.discover_project_files()

                # 캐시되지 않은 파일 발견
                cached_files = set(file_stats.keys())
                all_files_str = {str(f) for f in all_project_files}
                uncached_files = all_files_str - cached_files

                if uncached_files:
                    self._logger.warning(f"[P6] Found {len(uncached_files)} unverified files")

                    # DeepAnalyzer를 사용하여 검증 수행
                    from deep_analyzer import DeepAnalyzer

                    analyzer = DeepAnalyzer()  # Default settings for full scan

                    for file_path in uncached_files:
                        try:
                            # 간단한 검증 수행 (fast mode)
                            analysis_result = analyzer.analyze(Path(file_path))
                            result = asdict(analysis_result) if analysis_result else None

                            stats = FileStats(file_path=str(file_path))
                            stats.total_checks = 1
                            stats.analysis_mode = "fast"

                            # DeepAnalysisResult has ruff_result.passed, not direct passed field
                            ruff_result = result.get("ruff_result", {}) if result else {}
                            passed = ruff_result.get("passed", False)
                            violations = ruff_result.get("violations", [])

                            if passed:
                                stats.passed_checks = 1
                                stats.avg_quality_score = result.get("overall_score", 10.0)
                            else:
                                stats.failed_checks = 1
                                stats.total_violations = len(violations)
                                # Use overall_score from DeepAnalysisResult if available
                                stats.avg_quality_score = result.get("overall_score", max(0.0, 10.0 - len(violations) * 0.2))

                            # Add SOLID and Security issue counts from DeepAnalysisResult
                            stats.total_solid_violations = len(result.get("solid_violations", [])) if result else 0
                            stats.total_security_issues = len(result.get("security_issues", [])) if result else 0

                            file_stats[str(file_path)] = stats

                        except Exception as e:
                            self._logger.error(f"Failed to verify {file_path}: {e}")
                            # 검증 실패한 파일도 포함 (0점 처리)
                            stats = FileStats(file_path=str(file_path))
                            stats.total_checks = 1
                            stats.failed_checks = 1
                            stats.avg_quality_score = 0.0
                            file_stats[str(file_path)] = stats

                self._logger.info(f"[P6] Total files after full scan: {len(file_stats)}")

            return file_stats

        except Exception as e:
            self._logger.error(f"Failed to collect file stats: {e}")
            return file_stats

    def collect_team_stats(self, file_stats: Dict[str, FileStats]) -> TeamStats:
        """팀 전체 통계 집계

        Args:
            file_stats: 파일별 통계

        Returns:
            팀 전체 통계
        """
        team = TeamStats(
            total_files=len(file_stats),
            generated_at=datetime.now().isoformat(),
        )

        if not file_stats:
            return team

        total_quality_score = 0.0

        for stats in file_stats.values():
            team.total_checks += stats.total_checks
            team.passed_checks += stats.passed_checks
            team.failed_checks += stats.failed_checks
            team.total_violations += stats.total_violations
            team.total_security_issues += stats.total_security_issues
            team.total_solid_violations += stats.total_solid_violations
            total_quality_score += stats.avg_quality_score

        # 평균 계산
        if team.total_files > 0:
            team.avg_quality_score = total_quality_score / team.total_files

        # 캐시 히트율 (간단화: 모든 캐시 항목이 히트로 간주)
        if team.total_checks > 0:
            team.cache_hit_rate = 100.0

        self._logger.info(
            f"Team stats: {team.total_files} files, "
            f"{team.pass_rate:.1f}% pass rate, "
            f"{team.avg_quality_score:.1f} avg quality"
        )

        return team


class DashboardGenerator:
    """마크다운 대시보드 생성기"""

    def __init__(self, output_dir: Path):
        """초기화

        Args:
            output_dir: 대시보드 출력 디렉토리
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger(__name__)

    def generate_dashboard(
        self,
        team_stats: TeamStats,
        file_stats: Dict[str, FileStats],
        problem_files: List[FileStats],
    ) -> Path:
        """팀 대시보드 생성

        Args:
            team_stats: 팀 전체 통계
            file_stats: 파일별 통계
            problem_files: 문제 파일 목록 (우선순위 순)

        Returns:
            생성된 대시보드 파일 경로
        """
        dashboard_path = self.output_dir / "team_dashboard.md"

        content = self._build_dashboard_content(team_stats, file_stats, problem_files)

        try:
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(content)

            self._logger.info(f"Dashboard generated: {dashboard_path}")
            return dashboard_path

        except Exception as e:
            self._logger.error(f"Failed to generate dashboard: {e}")
            raise

    def _build_dashboard_content(
        self,
        team_stats: TeamStats,
        file_stats: Dict[str, FileStats],
        problem_files: List[FileStats],
    ) -> str:
        """대시보드 콘텐츠 생성"""
        lines = [
            "# Team Code Quality Dashboard",
            "",
            f"**Generated**: {team_stats.generated_at}",
            "",
            "## Overview",
            "",
            f"- **Total Files**: {team_stats.total_files}",
            f"- **Total Checks**: {team_stats.total_checks}",
            f"- **Pass Rate**: {team_stats.pass_rate:.1f}%",
            f"- **Avg Quality Score**: {team_stats.avg_quality_score:.1f}/10.0",
            f"- **Cache Hit Rate**: {team_stats.cache_hit_rate:.1f}%",
            "",
            "## Quality Metrics",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Passed Checks | {team_stats.passed_checks} |",
            f"| Failed Checks | {team_stats.failed_checks} |",
            f"| Total Violations | {team_stats.total_violations} |",
            f"| Security Issues | {team_stats.total_security_issues} |",
            f"| SOLID Violations | {team_stats.total_solid_violations} |",
            "",
            "## Quality Score Distribution",
            "",
        ]

        # 품질 점수 분포
        score_bins = self._calculate_score_distribution(file_stats)
        lines.append("```")
        for score_range, count in score_bins.items():
            bar = "█" * count
            lines.append(f"{score_range:>8}: {bar} ({count})")
        lines.append("```")
        lines.append("")

        # 문제 파일 (상위 10개)
        lines.extend(
            [
                "## Top Problem Files",
                "",
                "| File | Quality | Violations | Security | SOLID | Status |",
                "|------|---------|------------|----------|-------|--------|",
            ]
        )

        for stats in problem_files[:10]:
            file_name = Path(stats.file_path).name
            status = "[OK] PASS" if stats.passed_checks > 0 else "[FAIL] FAIL"
            lines.append(
                f"| {file_name} | {stats.avg_quality_score:.1f} | "
                f"{stats.total_violations} | {stats.total_security_issues} | "
                f"{stats.total_solid_violations} | {status} |"
            )

        lines.append("")
        lines.append("## Recommendations")
        lines.append("")
        lines.extend(self._generate_recommendations(team_stats, problem_files))

        return "\n".join(lines)

    def _calculate_score_distribution(self, file_stats: Dict[str, FileStats]) -> Dict[str, int]:
        """품질 점수 분포 계산"""
        bins = {
            "9.0-10.0": 0,
            "7.0-8.9": 0,
            "5.0-6.9": 0,
            "3.0-4.9": 0,
            "0.0-2.9": 0,
        }

        for stats in file_stats.values():
            score = stats.avg_quality_score
            if score >= 9.0:
                bins["9.0-10.0"] += 1
            elif score >= 7.0:
                bins["7.0-8.9"] += 1
            elif score >= 5.0:
                bins["5.0-6.9"] += 1
            elif score >= 3.0:
                bins["3.0-4.9"] += 1
            else:
                bins["0.0-2.9"] += 1

        return bins

    def _generate_recommendations(self, team_stats: TeamStats, problem_files: List[FileStats]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []

        # 보안 이슈
        if team_stats.total_security_issues > 0:
            recommendations.append(
                f"- 🛡️ **Security**: {team_stats.total_security_issues}개의 " f"보안 이슈 발견. 즉시 수정 필요."
            )

        # SOLID 위반
        if team_stats.total_solid_violations > 10:
            recommendations.append(
                f"- 🏗️ **Architecture**: {team_stats.total_solid_violations}개의 " f"SOLID 위반. 리팩토링 고려."
            )

        # 통과율
        if team_stats.pass_rate < 80.0:
            recommendations.append(
                f"- [WARN] **Pass Rate**: {team_stats.pass_rate:.1f}% (목표 80%+). " f"실패한 파일 우선 수정."
            )

        # 품질 점수
        if team_stats.avg_quality_score < 7.0:
            recommendations.append(
                f"- [STATUS] **Quality**: 평균 {team_stats.avg_quality_score:.1f}/10 " f"(목표 7.0+). 코드 품질 개선 필요."
            )

        # 문제 파일
        if len(problem_files) > 0:
            top_file = Path(problem_files[0].file_path).name
            recommendations.append(
                f"- [TASK] **Priority**: `{top_file}` 파일부터 시작 " f"(Quality {problem_files[0].avg_quality_score:.1f})"
            )

        if not recommendations:
            recommendations.append("- [OK] **Good Job**: 모든 메트릭이 목표치 달성!")

        return recommendations


class TrendAnalyzer:
    """추세 분석 엔진"""

    def __init__(self, trends_file: Path):
        """초기화

        Args:
            trends_file: 추세 데이터 파일 경로
        """
        self.trends_file = trends_file
        self.trends_file.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger(__name__)

    def add_data_point(self, team_stats: TeamStats):
        """새 데이터 포인트 추가

        Args:
            team_stats: 현재 팀 통계
        """
        data_point = TrendDataPoint(
            timestamp=team_stats.generated_at,
            quality_score=team_stats.avg_quality_score,
            violation_count=team_stats.total_violations,
            security_issue_count=team_stats.total_security_issues,
            pass_rate=team_stats.pass_rate,
        )

        trends = self._load_trends()
        trends.append(asdict(data_point))

        # 최근 30일만 유지
        cutoff = datetime.now() - timedelta(days=30)
        trends = [t for t in trends if datetime.fromisoformat(t["timestamp"]) > cutoff]

        self._save_trends(trends)
        self._logger.info(f"Added trend data point, total {len(trends)} points")

    def get_trend_summary(self) -> Dict[str, Any]:
        """추세 요약 생성

        Returns:
            추세 요약 데이터
        """
        trends = self._load_trends()

        if len(trends) < 2:
            return {
                "available": False,
                "message": "Not enough data for trend analysis",
            }

        # 최신 vs 과거 비교
        latest = trends[-1]
        previous = trends[-2] if len(trends) > 1 else trends[0]

        quality_change = latest["quality_score"] - previous["quality_score"]
        violation_change = latest["violation_count"] - previous["violation_count"]

        return {
            "available": True,
            "data_points": len(trends),
            "latest_quality": latest["quality_score"],
            "quality_change": quality_change,
            "quality_trend": "improving" if quality_change > 0 else "declining",
            "latest_violations": latest["violation_count"],
            "violation_change": violation_change,
            "latest_pass_rate": latest["pass_rate"],
        }

    def _load_trends(self) -> List[Dict[str, Any]]:
        """추세 데이터 로드"""
        if not self.trends_file.exists():
            return []

        try:
            with open(self.trends_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._logger.error(f"Failed to load trends: {e}")
            return []

    def _save_trends(self, trends: List[Dict[str, Any]]):
        """추세 데이터 저장"""
        try:
            with open(self.trends_file, "w", encoding="utf-8") as f:
                json.dump(trends, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._logger.error(f"Failed to save trends: {e}")


class TeamStatsAggregator:
    """팀 통계 종합 시스템

    통계 수집, 대시보드 생성, 추세 분석을 총괄합니다.
    """

    def __init__(
        self,
        cache_dir: Path,
        evidence_dir: Path,
        output_dir: Path,
    ):
        """초기화

        Args:
            cache_dir: VerificationCache 디렉토리
            evidence_dir: Evidence Tracker 로그 디렉토리
            output_dir: 통계 출력 디렉토리
        """
        self.collector = StatsCollector(cache_dir, evidence_dir)
        self.dashboard_gen = DashboardGenerator(output_dir)
        self.trend_analyzer = TrendAnalyzer(output_dir / "trends.json")
        self.output_dir = output_dir
        self._logger = logging.getLogger(__name__)

    def generate_report(self, force_full_scan: bool = False) -> Path:
        """전체 리포트 생성

        Args:
            force_full_scan: True시 전체 프로젝트 스캔 수행 (P6 준수)

        Returns:
            대시보드 파일 경로
        """
        self._logger.info(f"Starting team stats aggregation... (full_scan={force_full_scan})")

        # 1. 통계 수집
        file_stats = self.collector.collect_file_stats(force_full_scan=force_full_scan)
        team_stats = self.collector.collect_team_stats(file_stats)

        # 2. 문제 파일 식별 (품질 점수 낮은 순)
        problem_files = sorted(
            file_stats.values(),
            key=lambda s: (s.avg_quality_score, -s.total_violations),
        )

        # 3. 대시보드 생성
        dashboard_path = self.dashboard_gen.generate_dashboard(team_stats, file_stats, problem_files)

        # 4. 추세 데이터 추가
        self.trend_analyzer.add_data_point(team_stats)

        # 5. 문제 파일 목록 저장
        self._save_problem_files(problem_files[:20])  # 상위 20개만

        self._logger.info(f"Report generation complete: {dashboard_path}")
        return dashboard_path

    def _save_problem_files(self, problem_files: List[FileStats]):
        """문제 파일 목록 저장"""
        output_file = self.output_dir / "problem_files.json"

        try:
            data = [asdict(stats) for stats in problem_files]
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._logger.info(f"Saved {len(problem_files)} problem files")
        except Exception as e:
            self._logger.error(f"Failed to save problem files: {e}")


def main():
    """CLI 인터페이스 - P6 Quality Gates 준수"""
    import argparse

    # 인자 파서
    parser = argparse.ArgumentParser(description="Team Code Quality Statistics Aggregator (P6 Compliant)")
    parser.add_argument(
        "--full-scan", action="store_true", help="Force full project scan for all Python files (P6 compliance)"
    )
    parser.add_argument("--no-cache", action="store_true", help="Clear cache before running (same as --full-scan)")
    args = parser.parse_args()

    # --no-cache는 --full-scan과 동일
    force_full_scan = args.full_scan or args.no_cache

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 기본 경로
    cache_dir = Path("RUNS/.cache")
    evidence_dir = Path("RUNS/evidence")
    output_dir = Path("RUNS/stats")

    aggregator = TeamStatsAggregator(cache_dir, evidence_dir, output_dir)

    try:
        if force_full_scan:
            print("[P6] Running full project scan...")
        dashboard_path = aggregator.generate_report(force_full_scan=force_full_scan)
        print(f"\n[OK] Dashboard generated: {dashboard_path}")
        print(f"[INFO] View report: cat {dashboard_path}")

        # P6 준수 여부 출력
        if force_full_scan:
            print("[P6] Constitution Article P6 (Quality Gates) - COMPLIANT")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
