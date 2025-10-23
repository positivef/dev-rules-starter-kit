#!/usr/bin/env python3
"""Dev Rules Dashboard - Flask Backend

Phase D Week 1: 웹 대시보드 백엔드

주요 기능:
1. REST API (팀 통계, 파일 정보)
2. WebSocket (실시간 업데이트)
3. 파일 감시 (자동 검증)
4. 기존 컴포넌트 통합

사용 예시:
```bash
# 개발 서버 실행
python backend/app.py

# API 테스트
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/files

# 브라우저에서
http://localhost:5000
```
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# 기존 컴포넌트 import
from scripts.team_stats_aggregator import TeamStatsAggregator
from scripts.verification_cache import VerificationCache
from scripts.deep_analyzer import DeepAnalyzer
from scripts.critical_file_detector import CriticalFileDetector

# 파일 감시 시스템
from backend.file_monitor import FileMonitor

# Flask 앱 설정
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-rules-secret-key"  # 프로덕션에서는 환경변수로

# CORS 설정 (프론트엔드 개발용)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# WebSocket 설정
socketio = SocketIO(app, cors_allowed_origins="*")

# 전역 인스턴스 (나중에 의존성 주입으로 개선)
cache_dir = project_root / "RUNS" / ".cache"
evidence_dir = project_root / "RUNS" / "evidence"
stats_dir = project_root / "RUNS" / "stats"

cache = VerificationCache(cache_dir=cache_dir)
aggregator = TeamStatsAggregator(cache_dir=cache_dir, evidence_dir=evidence_dir, output_dir=stats_dir)
analyzer = DeepAnalyzer(mcp_enabled=False)
detector = CriticalFileDetector()

# 파일 감시 시스템 (나중에 시작)
file_monitor: FileMonitor | None = None


# ============================================================================
# 파일 변경 핸들러
# ============================================================================


def on_file_changed(file_path: Path):
    """파일 변경 시 자동 검증 및 WebSocket 알림

    Args:
        file_path: 변경된 파일 경로
    """
    try:
        print(f"[AutoVerify] Processing: {file_path}")

        # 1. 즉시 검증
        import time

        start = time.time()
        result = analyzer.analyze(file_path)

        # 2. 캐시 저장
        cache.put(file_path, result.ruff_result, mode="deep")

        elapsed = time.time() - start

        # 3. WebSocket으로 클라이언트에게 알림
        relative_path = file_path.relative_to(project_root)

        update_data = {
            "type": "file_updated",
            "file_path": str(relative_path),
            "quality_score": round(result.overall_score, 1),
            "passed": result.ruff_result.passed,
            "violations": len(result.ruff_result.violations),
            "verification_time": round(elapsed, 3),
            "timestamp": datetime.now().isoformat(),
        }

        # 모든 연결된 클라이언트에게 브로드캐스트
        socketio.emit("file_updated", update_data)

        print(f"[AutoVerify] Completed: {relative_path} (score: {result.overall_score:.1f}, {elapsed:.2f}s)")

    except Exception as e:
        print(f"[AutoVerify] Error processing {file_path}: {e}")


# ============================================================================
# REST API Endpoints
# ============================================================================


@app.route("/")
def index():
    """루트 페이지"""
    return jsonify(
        {
            "message": "Dev Rules Dashboard API",
            "version": "0.4.0",
            "endpoints": {
                "stats": "/api/stats",
                "files": "/api/files",
                "file_detail": "/api/files/<path>",
                "verify": "/api/verify (POST)",
                "trends": "/api/trends?days=30",
            },
        }
    )


@app.route("/api/stats")
def get_stats():
    """팀 전체 통계 반환

    Response:
        {
            "total_files": 150,
            "passed": 142,
            "failed": 8,
            "avg_quality": 8.2,
            "pass_rate": 94.7,
            "total_violations": 23,
            "last_updated": "2025-01-27T14:30:00"
        }
    """
    try:
        # 캐시에서 파일 통계 수집
        file_stats = aggregator.collector.collect_file_stats()

        # 팀 통계 계산
        team_stats = aggregator.collector.collect_team_stats(file_stats)

        # Calculate pass rate
        pass_rate = 0.0
        if team_stats.total_checks > 0:
            pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

        return jsonify(
            {
                "total_files": team_stats.total_files,
                "passed": team_stats.passed_checks,
                "failed": team_stats.failed_checks,
                "avg_quality": round(team_stats.avg_quality_score, 1),
                "pass_rate": round(pass_rate, 1),
                "total_violations": team_stats.total_violations,
                "last_updated": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files")
def get_files():
    """전체 파일 목록 및 통계

    Query Parameters:
        limit (int): 반환할 파일 수 (기본: 100)
        offset (int): 페이지네이션 오프셋 (기본: 0)
        sort_by (str): 정렬 기준 (quality_score, violations)
        order (str): 정렬 순서 (asc, desc)

    Response:
        {
            "files": [
                {
                    "path": "scripts/executor.py",
                    "quality_score": 5.2,
                    "passed": false,
                    "violations": 12,
                    "last_updated": "2025-01-27T14:00:00"
                },
                ...
            ],
            "total": 150,
            "limit": 100,
            "offset": 0
        }
    """
    try:
        # Query 파라미터
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        sort_by = request.args.get("sort_by", "quality_score")
        order = request.args.get("order", "asc")

        # 파일 통계 수집
        file_stats = aggregator.collector.collect_file_stats()

        # 정렬
        files_list = []
        for path, stats in file_stats.items():
            files_list.append(
                {
                    "path": str(path),
                    "quality_score": round(stats.avg_quality_score, 1),
                    "passed": stats.passed_checks > stats.failed_checks,
                    "violations": stats.total_violations,
                    "last_updated": stats.last_checked or "N/A",
                }
            )

        # 정렬 적용
        reverse = order == "desc"
        files_list.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

        # 페이지네이션
        total = len(files_list)
        files_page = files_list[offset : offset + limit]

        return jsonify({"files": files_page, "total": total, "limit": limit, "offset": offset})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/<path:file_path>")
def get_file_detail(file_path):
    """특정 파일 상세 정보

    Args:
        file_path: 파일 경로 (예: scripts/executor.py)

    Response:
        {
            "path": "scripts/executor.py",
            "quality_score": 5.2,
            "passed": false,
            "violations": [
                {
                    "type": "SRP",
                    "line": 25,
                    "message": "11개 메서드 (너무 많은 책임)",
                    "severity": "error"
                },
                ...
            ],
            "solid_violations": [...],
            "security_issues": [...],
            "hallucination_risks": [...],
            "recommendations": [...]
        }
    """
    try:
        # 캐시에서 검색
        full_path = project_root / file_path
        cached = cache.get(full_path)

        if cached is None:
            return jsonify({"error": "File not found in cache"}), 404

        # Deep 분석 (캐시에 없으면 실행)
        result = analyzer.analyze(full_path)

        # 상세 정보 구성
        detail = {
            "path": file_path,
            "quality_score": round(result.overall_score, 1),
            "passed": cached.passed,
            "violations": [
                {"type": v.code, "line": v.line, "message": v.message, "severity": "error"}
                for v in cached.violations[:10]  # 최대 10개
            ],
            "solid_violations": [
                {"type": v.type, "line": v.line, "message": v.message, "severity": v.severity}
                for v in result.solid_violations
            ],
            "security_issues": [
                {"type": s.type, "line": s.line, "message": s.message, "severity": s.severity}
                for s in result.security_issues
            ],
            "hallucination_risks": [
                {"type": h.type, "line": h.line, "message": h.message, "severity": h.severity}
                for h in result.hallucination_risks
            ],
            "recommendations": _generate_recommendations(result),
        }

        return jsonify(detail)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/verify", methods=["POST"])
def verify_file():
    """파일 즉시 검증

    Request Body:
        {
            "file_path": "scripts/my_module.py"
        }

    Response:
        {
            "path": "scripts/my_module.py",
            "quality_score": 8.5,
            "passed": true,
            "violations": [],
            "verification_time": 0.075
        }
    """
    try:
        data = request.get_json()
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({"error": "file_path required"}), 400

        full_path = project_root / file_path

        if not full_path.exists():
            return jsonify({"error": "File not found"}), 404

        # 즉시 검증
        import time

        start = time.time()

        result = analyzer.analyze(full_path)

        # 캐시 저장
        cache.put(full_path, result.ruff_result, mode="deep")

        elapsed = time.time() - start

        return jsonify(
            {
                "path": file_path,
                "quality_score": round(result.overall_score, 1),
                "passed": result.ruff_result.passed,
                "violations": len(result.ruff_result.violations),
                "verification_time": round(elapsed, 3),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/trends")
def get_trends():
    """품질 추세 데이터

    Query Parameters:
        days (int): 조회 기간 (기본: 30일)

    Response:
        {
            "data_points": [
                {
                    "date": "2025-01-01",
                    "avg_quality": 7.8,
                    "pass_rate": 92.0,
                    "total_violations": 25
                },
                ...
            ],
            "days": 30
        }
    """
    try:
        days = request.args.get("days", 30, type=int)

        # TrendAnalyzer에서 데이터 로드
        trends_file = stats_dir / "trends.json"

        if not trends_file.exists():
            return jsonify({"data_points": [], "days": days})

        import json

        with open(trends_file) as f:
            trend_data = json.load(f)

        # trend_data가 이미 리스트인 경우
        if isinstance(trend_data, list):
            data_points = trend_data[-days:]
        else:
            # 딕셔너리 형식인 경우
            data_points = trend_data.get("data_points", [])[-days:]

        return jsonify({"data_points": data_points, "days": days})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# WebSocket Handlers
# ============================================================================


@socketio.on("connect")
def handle_connect():
    """클라이언트 연결 시"""
    print(f"Client connected: {request.sid}")

    # 초기 데이터 전송
    file_stats = aggregator.collector.collect_file_stats()
    team_stats = aggregator.collector.collect_team_stats(file_stats)

    # Calculate pass rate
    pass_rate = 0.0
    if team_stats.total_checks > 0:
        pass_rate = (team_stats.passed_checks / team_stats.total_checks) * 100

    emit(
        "initial_data",
        {
            "total_files": team_stats.total_files,
            "avg_quality": round(team_stats.avg_quality_score, 1),
            "pass_rate": round(pass_rate, 1),
        },
    )


@socketio.on("disconnect")
def handle_disconnect():
    """클라이언트 연결 해제 시"""
    print(f"Client disconnected: {request.sid}")


@socketio.on("subscribe")
def handle_subscribe(data):
    """특정 채널 구독"""
    channel = data.get("channel", "all")
    print(f"Client {request.sid} subscribed to {channel}")

    emit("subscribed", {"channel": channel})


# ============================================================================
# Helper Functions
# ============================================================================


def _generate_recommendations(result):
    """분석 결과 기반 추천사항 생성"""
    recommendations = []

    # SOLID 위반 기반
    if result.solid_violations:
        recommendations.append(
            {
                "category": "SOLID Principles",
                "priority": "high",
                "message": f"{len(result.solid_violations)}개 SOLID 위반 발견. 리팩토링 권장.",
            }
        )

    # 보안 이슈 기반
    if result.security_issues:
        recommendations.append(
            {
                "category": "Security",
                "priority": "critical",
                "message": f"{len(result.security_issues)}개 보안 이슈 발견. 즉시 수정 필요.",
            }
        )

    # 품질 점수 기반
    if result.overall_score < 7.0:
        recommendations.append(
            {
                "category": "Quality",
                "priority": "medium",
                "message": f"품질 점수 {result.overall_score:.1f}/10. 코드 리뷰 권장.",
            }
        )

    return recommendations


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("""
==============================================================
  Dev Rules Dashboard - Backend Server
==============================================================
  Version: 0.4.0 (Phase D)
  Port:    5000
  Endpoints:
    - GET  /api/stats
    - GET  /api/files
    - GET  /api/files/<path>
    - POST /api/verify
    - GET  /api/trends?days=30
  WebSocket: http://localhost:5000
  File Monitor: scripts/ (auto-verify on change)
==============================================================
""")

    # 파일 감시 시스템 시작
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        file_monitor = FileMonitor(
            watch_path=scripts_dir,
            on_file_changed=on_file_changed,
            debounce_seconds=0.5,
        )
        file_monitor.start()
        print(f"[FileMonitor] Watching: {scripts_dir}")
    else:
        print("[FileMonitor] Warning: scripts/ directory not found")

    try:
        # 개발 서버 시작
        socketio.run(
            app,
            host="0.0.0.0",
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True,  # 개발용
        )
    finally:
        # 서버 종료 시 파일 감시 중지
        if file_monitor and file_monitor.is_running():
            print("\n[FileMonitor] Stopping...")
            file_monitor.stop()
