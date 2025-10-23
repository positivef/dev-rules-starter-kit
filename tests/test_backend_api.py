#!/usr/bin/env python3
"""Flask 백엔드 API 통합 테스트

Phase D Week 1: 백엔드 API 엔드포인트 검증

테스트 항목:
1. GET /api/stats - 팀 통계 조회
2. GET /api/files - 파일 목록 조회
3. GET /api/files/<path> - 파일 상세 정보
4. POST /api/verify - 즉시 검증
5. GET /api/trends - 품질 추세 데이터
"""

import pytest
import json
from pathlib import Path


# Flask app을 테스트 모드로 임포트
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from app import app


@pytest.fixture
def client():
    """Flask 테스트 클라이언트"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_endpoint(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["version"] == "0.4.0"
    assert "endpoints" in data
    assert "/api/stats" in data["endpoints"]["stats"]


def test_stats_endpoint(client):
    """팀 통계 API 테스트"""
    response = client.get("/api/stats")
    assert response.status_code == 200

    data = json.loads(response.data)

    # 필수 필드 확인
    assert "total_files" in data
    assert "passed" in data
    assert "failed" in data
    assert "avg_quality" in data
    assert "pass_rate" in data
    assert "total_violations" in data
    assert "last_updated" in data

    # 타입 확인
    assert isinstance(data["total_files"], int)
    assert isinstance(data["avg_quality"], (int, float))
    assert isinstance(data["pass_rate"], (int, float))


def test_files_endpoint(client):
    """파일 목록 API 테스트"""
    response = client.get("/api/files?limit=5")
    assert response.status_code == 200

    data = json.loads(response.data)

    # 필수 필드 확인
    assert "files" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

    # files 리스트 확인
    assert isinstance(data["files"], list)
    assert len(data["files"]) <= 5

    # 각 파일 항목 확인
    if data["files"]:
        file_item = data["files"][0]
        assert "path" in file_item
        assert "quality_score" in file_item
        assert "passed" in file_item
        assert "violations" in file_item
        assert "last_updated" in file_item


def test_files_pagination(client):
    """파일 목록 페이지네이션 테스트"""
    # 첫 페이지
    response1 = client.get("/api/files?limit=2&offset=0")
    data1 = json.loads(response1.data)

    # 두 번째 페이지
    response2 = client.get("/api/files?limit=2&offset=2")
    data2 = json.loads(response2.data)

    # 다른 파일들이어야 함
    if data1["files"] and data2["files"]:
        assert data1["files"][0]["path"] != data2["files"][0]["path"]


def test_verify_endpoint(client):
    """즉시 검증 API 테스트"""
    # 실제 존재하는 파일로 테스트
    test_file = "scripts/critical_file_detector.py"

    response = client.post("/api/verify", data=json.dumps({"file_path": test_file}), content_type="application/json")

    assert response.status_code == 200

    data = json.loads(response.data)

    # 필수 필드 확인
    assert "path" in data
    assert "quality_score" in data
    assert "passed" in data
    assert "violations" in data
    assert "verification_time" in data

    # 값 확인
    assert data["path"] == test_file
    assert isinstance(data["quality_score"], (int, float))
    assert isinstance(data["passed"], bool)
    assert isinstance(data["verification_time"], (int, float))


def test_verify_missing_file(client):
    """존재하지 않는 파일 검증 테스트"""
    response = client.post(
        "/api/verify", data=json.dumps({"file_path": "nonexistent/file.py"}), content_type="application/json"
    )

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_verify_missing_parameter(client):
    """file_path 파라미터 누락 테스트"""
    response = client.post("/api/verify", data=json.dumps({}), content_type="application/json")

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_trends_endpoint(client):
    """품질 추세 API 테스트"""
    response = client.get("/api/trends?days=7")
    assert response.status_code == 200

    data = json.loads(response.data)

    # 필수 필드 확인
    assert "data_points" in data
    assert "days" in data

    # 타입 확인
    assert isinstance(data["data_points"], list)
    assert data["days"] == 7


def test_trends_default_days(client):
    """품질 추세 기본 일수 테스트"""
    response = client.get("/api/trends")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["days"] == 30  # 기본값


def test_api_error_handling(client):
    """API 에러 처리 테스트"""
    # 존재하지 않는 엔드포인트
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_cors_headers(client):
    """CORS 헤더 테스트"""
    response = client.get("/api/stats")

    # CORS 헤더 확인
    assert "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
