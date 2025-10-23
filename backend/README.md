# Dev Rules Dashboard - Backend

**Version**: 0.4.0 (Phase D Week 1)

Flask 기반 웹 대시보드 백엔드 시스템입니다.

## 주요 기능

### 1. REST API
- **GET /api/stats**: 팀 전체 통계 조회
- **GET /api/files**: 파일 목록 조회 (페이지네이션 지원)
- **GET /api/files/<path>**: 특정 파일 상세 정보
- **POST /api/verify**: 파일 즉시 검증
- **GET /api/trends**: 품질 추세 데이터 (일별)

### 2. WebSocket (Socket.IO)
- **실시간 알림**: 파일 변경 시 자동 검증 결과 전송
- **이벤트**:
  - `connect`: 클라이언트 연결 시 초기 데이터 전송
  - `file_updated`: 파일 변경 및 검증 완료 시
  - `subscribe`: 특정 채널 구독

### 3. 파일 감시 시스템
- **watchdog 기반**: scripts/ 디렉토리 실시간 감시
- **Debounce 처리**: 0.5초 내 중복 이벤트 무시
- **자동 검증**: 파일 변경 시 즉시 DeepAnalyzer 실행
- **WebSocket 알림**: 모든 클라이언트에게 브로드캐스트

## 설치 및 실행

### 의존성 설치
```bash
pip install Flask==3.0.0 flask-cors==4.0.0 flask-socketio==5.3.5 python-socketio==5.10.0 watchdog
```

### 서버 실행
```bash
cd backend
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

### API 테스트
```bash
# 팀 통계
curl http://localhost:5000/api/stats

# 파일 목록 (최대 10개)
curl "http://localhost:5000/api/files?limit=10"

# 파일 즉시 검증
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"file_path": "scripts/my_module.py"}'

# 품질 추세 (최근 7일)
curl "http://localhost:5000/api/trends?days=7"
```

## 아키텍처

### 컴포넌트 통합
```
Flask App
├── TeamStatsAggregator (통계 수집)
├── VerificationCache (캐싱)
├── DeepAnalyzer (SOLID, Security 분석)
├── CriticalFileDetector (우선순위 분류)
└── FileMonitor (파일 감시)
```

### 파일 감시 흐름
```
파일 변경 감지 (watchdog)
  ↓
Debounce 처리 (0.5초)
  ↓
DeepAnalyzer 실행
  ↓
캐시 저장
  ↓
WebSocket 알림 (file_updated)
  ↓
모든 클라이언트 업데이트
```

## API 응답 예시

### GET /api/stats
```json
{
  "total_files": 150,
  "passed": 142,
  "failed": 8,
  "avg_quality": 8.2,
  "pass_rate": 94.7,
  "total_violations": 23,
  "last_updated": "2025-01-27T14:30:00"
}
```

### GET /api/files?limit=2
```json
{
  "files": [
    {
      "path": "scripts/executor.py",
      "quality_score": 5.2,
      "passed": false,
      "violations": 12,
      "last_updated": "2025-01-27T14:00:00"
    },
    {
      "path": "scripts/analyzer.py",
      "quality_score": 9.8,
      "passed": true,
      "violations": 0,
      "last_updated": "2025-01-27T14:05:00"
    }
  ],
  "total": 150,
  "limit": 2,
  "offset": 0
}
```

### WebSocket Event: file_updated
```json
{
  "type": "file_updated",
  "file_path": "scripts/executor.py",
  "quality_score": 6.5,
  "passed": false,
  "violations": 8,
  "verification_time": 0.123,
  "timestamp": "2025-01-27T14:35:00"
}
```

## 파일 구조

```
backend/
├── app.py                 # Flask 메인 애플리케이션
├── file_monitor.py        # 파일 감시 시스템
├── requirements.txt       # Python 의존성
└── README.md             # 이 문서
```

## 개발 노트

### Phase D Week 1 완료 항목
- ✅ Flask 백엔드 기초 구조
- ✅ 5개 REST API 엔드포인트
- ✅ WebSocket 실시간 통신
- ✅ 기존 컴포넌트 통합
- ✅ 파일 감시 시스템
- ✅ 통합 테스트 (11/11 통과)

### 다음 단계 (Phase D Week 2)
- [ ] React 프론트엔드 개발
- [ ] 대시보드 UI 컴포넌트
- [ ] Chart.js 품질 그래프
- [ ] WebSocket 클라이언트 통합

## 성능

- **API 응답 시간**: <100ms (평균)
- **파일 감시 Debounce**: 0.5초
- **자동 검증 속도**: 0.05-0.15초 (파일당)
- **WebSocket 지연**: <50ms

## 테스트

```bash
# 백엔드 통합 테스트
pytest tests/test_backend_api.py -v

# 결과: 11/11 통과
```

테스트 항목:
- 루트 엔드포인트
- 팀 통계 API
- 파일 목록 API (페이지네이션 포함)
- 파일 상세 API
- 즉시 검증 API
- 품질 추세 API
- 에러 처리
- CORS 헤더

## 라이선스

MIT License (프로젝트 루트 LICENSE 파일 참조)
