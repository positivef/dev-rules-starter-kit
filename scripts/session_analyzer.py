#!/usr/bin/env python3
"""
Session Analyzer - Session data analysis and pattern detection tool

Features:
- Task pattern analysis (frequently executed tasks)
- Failure pattern detection (recurring errors)
- Hourly productivity analysis
- Performance metrics and trends
- Improvement suggestion generation
"""

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from collections import Counter, defaultdict
import statistics


class SessionAnalyzer:
    """
    세션 데이터를 분석하여 개발 패턴과 통찰을 제공
    """

    def __init__(self, sessions_dir: str = "RUNS/sessions"):
        """
        초기화

        Args:
            sessions_dir: 세션 파일 디렉토리 경로
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_data = []
        self.analysis_results = {}

    def load_sessions(self, days: int = 30) -> int:
        """
        최근 N일간의 세션 데이터 로드

        Args:
            days: 분석할 기간 (일)

        Returns:
            로드된 세션 수
        """
        self.sessions_data = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if not self.sessions_dir.exists():
            print(f"[WARN] 세션 디렉토리 없음: {self.sessions_dir}")
            return 0

        # 모든 세션 파일 로드
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                # 백업 파일 제외
                if session_file.name.endswith(".backup.json"):
                    continue

                # 파일 수정 시간 확인
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                if mtime < cutoff_date:
                    continue

                # Windows 인코딩 문제 처리
                encodings = ["utf-8", "cp949", "latin-1"]
                data = None
                for enc in encodings:
                    try:
                        with open(session_file, "r", encoding=enc) as f:
                            data = json.load(f)
                            break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue

                if data:
                    data["_file_path"] = str(session_file)
                    data["_file_mtime"] = mtime.isoformat()
                    self.sessions_data.append(data)

            except Exception as e:
                print(f"[WARN] 세션 로드 실패 {session_file.name}: {e}")

        # 시간순 정렬
        self.sessions_data.sort(key=lambda x: x.get("started_at", ""), reverse=True)

        print(f"[INFO] {len(self.sessions_data)}개 세션 로드됨 (최근 {days}일)")
        return len(self.sessions_data)

    def analyze_task_patterns(self) -> Dict[str, Any]:
        """
        작업 패턴 분석

        Returns:
            작업 패턴 분석 결과
        """
        task_counter = Counter()
        task_times = defaultdict(list)
        failed_tasks = Counter()
        command_patterns = Counter()

        for session in self.sessions_data:
            scope_data = session.get("scope_data", {})
            session_data = scope_data.get("session", {})

            # 작업 이력 분석
            task_history = session_data.get("task_history", [])
            for task in task_history:
                task_id = task.get("task_id", "unknown")
                task_counter[task_id] += 1

            # 현재/완료 작업 분석
            current_task = session_data.get("current_task", {})
            if current_task:
                task_id = current_task.get("task_id")
                if task_id:
                    task_counter[task_id] += 1
                    exec_time = current_task.get("execution_time", 0)
                    if exec_time > 0:
                        task_times[task_id].append(exec_time)

            # 완료된 작업
            completed = session_data.get("completed_tasks", [])
            for task_id in completed:
                task_counter[task_id] += 1

            # 실패한 작업
            failed = session_data.get("failed_tasks", {})
            for task_id, failure in failed.items():
                failed_tasks[task_id] += 1

            # 명령 패턴 (TEMP 스코프)
            temp_data = scope_data.get("temp", {})
            command_log = temp_data.get("command_log", [])
            for cmd in command_log:
                command = cmd.get("command", "")
                # 첫 단어만 추출 (명령어)
                cmd_name = command.split()[0] if command else ""
                if cmd_name:
                    command_patterns[cmd_name] += 1

        # 평균 실행 시간 계산
        avg_times = {}
        for task_id, times in task_times.items():
            if times:
                avg_times[task_id] = {
                    "avg": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times),
                }

        return {
            "most_frequent_tasks": task_counter.most_common(10),
            "failed_tasks": failed_tasks.most_common(10),
            "task_execution_times": avg_times,
            "command_patterns": command_patterns.most_common(10),
            "total_unique_tasks": len(task_counter),
            "total_failed_tasks": len(failed_tasks),
        }

    def analyze_productivity(self) -> Dict[str, Any]:
        """
        생산성 패턴 분석

        Returns:
            생산성 분석 결과
        """
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        session_durations = []

        for session in self.sessions_data:
            # 세션 시작 시간 분석
            started_at = session.get("started_at")
            if started_at:
                try:
                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    hour = dt.hour
                    day = dt.strftime("%A")
                    hourly_activity[hour] += 1
                    daily_activity[day] += 1
                except Exception:
                    pass

            # 세션 지속 시간 계산
            last_checkpoint = session.get("last_checkpoint")
            if started_at and last_checkpoint:
                try:
                    start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(last_checkpoint.replace("Z", "+00:00"))
                    duration = (end_dt - start_dt).total_seconds() / 60  # 분 단위
                    if duration > 0:
                        session_durations.append(duration)
                except Exception:
                    pass

        # 가장 생산적인 시간대
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]

        # 가장 활동적인 요일
        peak_days = sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:3]

        # 평균 세션 시간
        avg_session_duration = statistics.mean(session_durations) if session_durations else 0

        return {
            "peak_hours": peak_hours,
            "peak_days": peak_days,
            "avg_session_duration_minutes": avg_session_duration,
            "total_sessions": len(self.sessions_data),
            "hourly_distribution": dict(hourly_activity),
            "daily_distribution": dict(daily_activity),
        }

    def analyze_error_patterns(self) -> Dict[str, Any]:
        """
        에러 패턴 분석

        Returns:
            에러 패턴 분석 결과
        """
        error_messages = Counter()
        error_tasks = defaultdict(list)
        error_timeline = []

        for session in self.sessions_data:
            scope_data = session.get("scope_data", {})
            session_data = scope_data.get("session", {})

            # 실패한 작업들 분석
            failed_tasks = session_data.get("failed_tasks", {})
            for task_id, failure in failed_tasks.items():
                error = failure.get("error", "")
                if error:
                    # 에러 메시지 정규화 (경로, 시간 등 제거)
                    normalized_error = self._normalize_error_message(error)
                    error_messages[normalized_error] += 1
                    error_tasks[normalized_error].append(task_id)

                    # 타임라인 기록
                    timestamp = failure.get("timestamp")
                    if timestamp:
                        error_timeline.append(
                            {
                                "timestamp": timestamp,
                                "task_id": task_id,
                                "error": normalized_error[:100],  # 처음 100자
                            }
                        )

        # 타임라인 정렬
        error_timeline.sort(key=lambda x: x.get("timestamp", ""))

        return {
            "common_errors": error_messages.most_common(10),
            "error_tasks": dict(error_tasks),
            "error_timeline": error_timeline[-20:],  # 최근 20개
            "total_unique_errors": len(error_messages),
            "total_errors": sum(error_messages.values()),
        }

    def generate_insights(self) -> Dict[str, Any]:
        """
        분석 결과를 바탕으로 통찰 생성

        Returns:
            개선 제안 및 통찰
        """
        insights = {"recommendations": [], "warnings": [], "positive_patterns": []}

        # 작업 패턴 분석
        task_analysis = self.analysis_results.get("task_patterns", {})
        failed_tasks = task_analysis.get("failed_tasks", [])

        if failed_tasks:
            most_failed = failed_tasks[0] if failed_tasks else None
            if most_failed and most_failed[1] > 3:
                insights["warnings"].append(f"작업 '{most_failed[0]}'이(가) {most_failed[1]}번 실패함 - 근본 원인 분석 필요")

        # 생산성 분석
        productivity = self.analysis_results.get("productivity", {})
        avg_duration = productivity.get("avg_session_duration_minutes", 0)

        if avg_duration > 120:
            insights["positive_patterns"].append(f"평균 세션 시간이 {avg_duration:.0f}분으로 집중도가 높음")
        elif avg_duration < 30 and avg_duration > 0:
            insights["recommendations"].append("평균 세션 시간이 30분 미만 - 더 긴 집중 시간 확보 권장")

        # 에러 패턴 분석
        error_analysis = self.analysis_results.get("error_patterns", {})
        common_errors = error_analysis.get("common_errors", [])

        if common_errors:
            top_error = common_errors[0] if common_errors else None
            if top_error and top_error[1] > 5:
                insights["warnings"].append(f"반복되는 에러 패턴 감지: {top_error[1]}회 발생")

        # 실행 통계
        stats = self.analysis_results.get("execution_stats", {})
        success_rate = stats.get("success_rate", 100)

        if success_rate < 80:
            insights["warnings"].append(f"작업 성공률이 {success_rate:.1f}%로 낮음 - 프로세스 개선 필요")
        elif success_rate > 95:
            insights["positive_patterns"].append(f"작업 성공률이 {success_rate:.1f}%로 매우 높음")

        # 최적 작업 시간 제안
        peak_hours = productivity.get("peak_hours", [])
        if peak_hours:
            best_hours = [f"{h[0]}시" for h in peak_hours[:2]]
            insights["recommendations"].append(f"가장 생산적인 시간대: {', '.join(best_hours)}")

        return insights

    def _normalize_error_message(self, error: str) -> str:
        """
        에러 메시지 정규화 (경로, 타임스탬프 등 제거)

        Args:
            error: 원본 에러 메시지

        Returns:
            정규화된 에러 메시지
        """
        import re

        # 파일 경로 제거
        error = re.sub(r"[A-Za-z]:[\\\/][^\s]+", "<PATH>", error)
        error = re.sub(r"\/[^\s]+", "<PATH>", error)

        # 타임스탬프 제거
        error = re.sub(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}", "<TIME>", error)

        # 숫자 ID 제거
        error = re.sub(r"\b\d{5,}\b", "<ID>", error)

        # 라인 번호 제거
        error = re.sub(r"line \d+", "line <N>", error)

        return error.strip()

    def get_execution_stats(self) -> Dict[str, Any]:
        """
        전체 실행 통계 계산

        Returns:
            실행 통계
        """
        total_tasks = 0
        successful_tasks = 0
        failed_tasks = 0
        total_time = 0

        for session in self.sessions_data:
            scope_data = session.get("scope_data", {})
            user_data = scope_data.get("user", {})

            # 사용자 통계 (누적)
            stats = user_data.get("execution_stats", {})
            if stats:
                total_tasks += stats.get("total_executions", 0)
                successful_tasks += stats.get("successful", 0)
                failed_tasks += stats.get("failed", 0)
                total_time += stats.get("total_time", 0)

        success_rate = successful_tasks / total_tasks * 100 if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": success_rate,
            "total_execution_hours": total_time / 3600,
            "avg_execution_time": total_time / total_tasks if total_tasks > 0 else 0,
        }

    def analyze_all(self, days: int = 30) -> Dict[str, Any]:
        """
        전체 분석 실행

        Args:
            days: 분석 기간

        Returns:
            전체 분석 결과
        """
        # 세션 로드
        session_count = self.load_sessions(days)
        if session_count == 0:
            return {"error": "분석할 세션 데이터가 없습니다"}

        # 각 분석 실행
        self.analysis_results = {
            "task_patterns": self.analyze_task_patterns(),
            "productivity": self.analyze_productivity(),
            "error_patterns": self.analyze_error_patterns(),
            "execution_stats": self.get_execution_stats(),
            "insights": {},  # 나중에 채움
        }

        # 통찰 생성
        self.analysis_results["insights"] = self.generate_insights()

        return self.analysis_results

    def print_report(self, results: Optional[Dict[str, Any]] = None) -> None:
        """
        분석 보고서 출력

        Args:
            results: 분석 결과 (없으면 self.analysis_results 사용)
        """
        if results is None:
            results = self.analysis_results

        print("\n" + "=" * 70)
        print(" " * 20 + "세션 분석 보고서")
        print("=" * 70)

        # 실행 통계
        stats = results.get("execution_stats", {})
        print("\n[실행 통계]")
        print(f"총 작업 수: {stats.get('total_tasks', 0)}")
        print(f"성공: {stats.get('successful_tasks', 0)}")
        print(f"실패: {stats.get('failed_tasks', 0)}")
        print(f"성공률: {stats.get('success_rate', 0):.1f}%")
        print(f"총 실행 시간: {stats.get('total_execution_hours', 0):.1f}시간")

        # 작업 패턴
        patterns = results.get("task_patterns", {})
        print("\n[자주 실행한 작업 TOP 5]")
        for task, count in patterns.get("most_frequent_tasks", [])[:5]:
            print(f"  - {task}: {count}회")

        # 실패 패턴
        if patterns.get("failed_tasks"):
            print("\n[자주 실패한 작업]")
            for task, count in patterns.get("failed_tasks", [])[:3]:
                print(f"  - {task}: {count}회 실패")

        # 생산성
        productivity = results.get("productivity", {})
        print("\n[생산성 패턴]")
        print(f"평균 세션 시간: {productivity.get('avg_session_duration_minutes', 0):.0f}분")
        print(f"총 세션 수: {productivity.get('total_sessions', 0)}")

        peak_hours = productivity.get("peak_hours", [])
        if peak_hours:
            print(f"가장 활동적인 시간: {', '.join([f'{h[0]}시' for h in peak_hours[:3]])}")

        # 명령 패턴
        print("\n[자주 사용한 명령어]")
        for cmd, count in patterns.get("command_patterns", [])[:5]:
            print(f"  - {cmd}: {count}회")

        # 통찰 및 제안
        insights = results.get("insights", {})

        if insights.get("positive_patterns"):
            print("\n[긍정적 패턴]")
            for pattern in insights["positive_patterns"]:
                print(f"  [GOOD] {pattern}")

        if insights.get("warnings"):
            print("\n[주의사항]")
            for warning in insights["warnings"]:
                print(f"  [WARN] {warning}")

        if insights.get("recommendations"):
            print("\n[개선 제안]")
            for rec in insights["recommendations"]:
                print(f"  [TIP] {rec}")

        print("\n" + "=" * 70)

    def save_report(self, output_file: str = "RUNS/session_analysis_report.json") -> None:
        """
        분석 결과를 파일로 저장

        Args:
            output_file: 출력 파일 경로
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analysis_period_days": len(set(s.get("started_at", "")[:10] for s in self.sessions_data)),
            "total_sessions_analyzed": len(self.sessions_data),
            "results": self.analysis_results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=True)

        print(f"\n[INFO] 보고서 저장됨: {output_path}")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="세션 데이터 분석 도구")
    parser.add_argument("--days", type=int, default=30, help="분석 기간 (일, 기본값: 30)")
    parser.add_argument("--output", type=str, default="RUNS/session_analysis_report.json", help="출력 파일 경로")
    parser.add_argument("--quiet", action="store_true", help="보고서 출력 생략")

    args = parser.parse_args()

    # 분석기 생성 및 실행
    analyzer = SessionAnalyzer()
    results = analyzer.analyze_all(days=args.days)

    # 보고서 출력
    if not args.quiet:
        analyzer.print_report(results)

    # 파일 저장
    analyzer.save_report(args.output)


if __name__ == "__main__":
    main()
