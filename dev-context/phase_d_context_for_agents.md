# Phase D 개발 컨텍스트 (에이전트 공유용)

**작성일**: 2025-01-27
**대상**: Codex, Gemini, 다른 협업 AI 에이전트
**목적**: Phase D 웹 대시보드 개발을 위한 컨텍스트 공유

---

## 프로젝트 현황 요약

### 완료된 단계
- ✅ **Phase A**: 기초 검증 시스템 (RuffVerifier)
- ✅ **Phase B**: Constitutional AI 검증
- ✅ **Phase C Week 1**: 효율성 (Cache, CriticalFileDetector)
- ✅ **Phase C Week 2**: 심층 분석 (DeepAnalyzer, TeamStats, WorkerPool)

### 현재 상태
- 총 코드: 4,178 lines (production 1,435 + tests 1,546 + docs 1,197)
- 테스트: 83/83 통과 (100%)
- 성능: 3배 향상 (병렬 처리), 75배 캐시 히트
- 커밋: 4개 (e1d37ee, c56f277, 50f60ff, 8a4feb8)

---

## Phase D 목표

### 주요 구현 항목

1. **웹 대시보드** (Flask/FastAPI + React)
   - 실시간 품질 모니터링
   - 인터랙티브 차트/그래프
   - 파일별 상세 분석 뷰
   - 팀원별 통계

2. **MCP 서버 통합** (context7, sequential-thinking)
   - 공식 문서 기반 검증 강화
   - 복잡한 문제 단계적 분석
   - 더 정확한 추천

3. **실시간 모니터링** (WebSocket)
   - 파일 저장 시 즉시 검증
   - 브라우저 자동 갱신
   - Live 로그 스트리밍

4. **옵시디언 자동화** (토큰 최적화)
   - 최소 Daily Notes (50 tokens)
   - Git/pytest hook 연동
   - 조건부 상세화

---

## 기술 스택

### 백엔드
```python
# Flask/FastAPI
- REST API 엔드포인트
- WebSocket 지원
- CORS 설정

# 기존 컴포넌트 재사용
- DeepAnalyzer
- TeamStatsAggregator
- VerificationCache
- WorkerPool
```

### 프론트엔드
```javascript
// React
- 대시보드 컴포넌트
- 차트 라이브러리 (Chart.js/Recharts)
- 실시간 업데이트 (WebSocket)

// 상태 관리
- React Hooks (useState, useEffect)
- Context API (선택적)
```

### 인프라
```
- 개발 서버: localhost:5000 (백엔드)
- 개발 서버: localhost:3000 (프론트엔드)
- WebSocket: Socket.IO
- 파일 감시: watchdog (Python)
```

---

## 핵심 데이터 구조

### 1. 팀 통계
```python
@dataclass
class TeamStats:
    total_files: int
    passed: int
    failed: int
    avg_quality_score: float
    pass_rate: float
    total_violations: int
```

### 2. 파일 통계
```python
@dataclass
class FileStats:
    file_path: Path
    passed: bool
    quality_score: float  # 0-10
    violations: List[Violation]
    last_updated: datetime
```

### 3. 실시간 업데이트
```python
@dataclass
class FileUpdateEvent:
    file_path: str
    event_type: str  # "modified", "created", "deleted"
    verification_result: VerificationResult
    timestamp: datetime
```

---

## API 설계 (초안)

### REST API

```
GET  /api/stats
     → 팀 전체 통계 반환
     Response: TeamStats (JSON)

GET  /api/files
     → 전체 파일 목록 및 통계
     Response: List[FileStats]

GET  /api/files/<path>
     → 특정 파일 상세 정보
     Response: FileDetail (위반 사항, 추천 등)

POST /api/verify
     Body: { "file_path": "scripts/foo.py" }
     → 즉시 검증 요청
     Response: VerificationResult

GET  /api/trends?days=30
     → 품질 추세 데이터
     Response: List[TrendDataPoint]
```

### WebSocket Events

```
// Client → Server
{
  "type": "subscribe",
  "channel": "file_updates"
}

// Server → Client
{
  "type": "file_updated",
  "data": {
    "file_path": "scripts/executor.py",
    "quality_score": 5.2,
    "violations": [...]
  }
}
```

---

## 파일 구조 (예상)

```
dev-rules-starter-kit/
├── backend/
│   ├── app.py                 # Flask/FastAPI 앱
│   ├── api/
│   │   ├── stats.py          # 통계 API
│   │   ├── files.py          # 파일 API
│   │   └── websocket.py      # WebSocket 핸들러
│   ├── services/
│   │   ├── verification.py   # 검증 서비스
│   │   └── monitoring.py     # 파일 감시
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── FileList.jsx
│   │   │   ├── FileDetail.jsx
│   │   │   └── QualityChart.jsx
│   │   ├── services/
│   │   │   └── api.js        # API 호출
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── scripts/
    └── (기존 Python 스크립트들)
```

---

## 협업 요청 사항

### Codex에게

**역할**: 코드 생성 및 리뷰

**요청 사항**:
1. Flask/FastAPI 백엔드 구조 설계 리뷰
2. REST API 엔드포인트 구현 지원
3. WebSocket 통합 코드 작성
4. 에러 처리 및 로깅 패턴 제안

**컨텍스트 필요 사항**:
- 기존 DeepAnalyzer, TeamStatsAggregator 구조
- VerificationCache 데이터 포맷
- WorkerPool 병렬 처리 로직

**예시 질문**:
```
"기존 TeamStatsAggregator를 Flask API로 노출하려면 어떻게 설계해야 하나요?
현재 JSON 캐시를 사용 중인데, 실시간 업데이트를 위한 최적화 방안은?"
```

---

### Gemini에게

**역할**: 아키텍처 설계 및 최적화

**요청 사항**:
1. 웹 대시보드 아키텍처 리뷰
2. 실시간 모니터링 시스템 설계
3. 성능 최적화 전략 (캐싱, WebSocket)
4. 보안 고려사항 (CORS, 인증)

**컨텍스트 필요 사항**:
- 현재 성능: 3x speedup (병렬), 75x cache hit
- 예상 사용자: 1-10명 (소규모 팀)
- 데이터 크기: ~150 파일, ~4000 lines

**예시 질문**:
```
"파일 변경 감지를 위해 watchdog를 쓰려고 하는데,
500+ 파일에서도 성능이 괜찮을까요?
더 나은 대안이 있나요?"
```

---

## 기술적 도전 과제

### 1. 실시간 파일 감시
**문제**: 파일 수정 시 즉시 검증 + 브라우저 업데이트
**고려사항**:
- watchdog vs inotify vs polling
- 너무 잦은 업데이트 방지 (debounce)
- 병렬 검증 시 순서 보장

**현재 아이디어**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            # Debounce: 0.5초 내 중복 무시
            # WorkerPool로 검증 제출
            # WebSocket으로 결과 전송
```

### 2. WebSocket 연결 관리
**문제**: 여러 클라이언트 동시 접속
**고려사항**:
- 연결 끊김 처리 (재연결)
- 메모리 누수 방지
- 브로드캐스트 vs 개별 전송

**현재 아이디어**:
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('initial_data', get_current_stats())

@socketio.on('disconnect')
def handle_disconnect():
    # 리소스 정리
```

### 3. 프론트엔드 성능
**문제**: 대량 데이터 렌더링 (150+ 파일)
**고려사항**:
- 가상 스크롤 (react-window)
- 페이지네이션
- 검색/필터링

**현재 아이디어**:
```jsx
import { FixedSizeList } from 'react-window';

function FileList({ files }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {files[index].path} - {files[index].quality_score}
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={files.length}
      itemSize={50}
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

## 우선순위 및 일정

### Week 1: 백엔드 기초
```
Day 1-2: Flask 앱 구조
Day 3-4: REST API 구현
Day 5: WebSocket 기본
Day 6-7: 기존 컴포넌트 통합
```

### Week 2: 프론트엔드 기초
```
Day 8-9: React 프로젝트 설정
Day 10-11: Dashboard 컴포넌트
Day 12-13: Chart 통합
Day 14: WebSocket 연결
```

### Week 3: 실시간 기능
```
Day 15-16: 파일 감시 구현
Day 17-18: 실시간 업데이트
Day 19-20: 성능 최적화
Day 21: 통합 테스트
```

### Week 4: 옵시디언 자동화
```
Day 22-23: SmartObsidianUpdater
Day 24-25: Git/pytest hook
Day 26-27: 토큰 모니터링
Day 28: 최종 통합
```

---

## 기존 코드 참고 위치

### 핵심 컴포넌트
```
scripts/deep_analyzer.py          # SOLID, Security 분석
scripts/team_stats_aggregator.py  # 통계 수집/대시보드
scripts/worker_pool.py             # 병렬 처리
scripts/verification_cache.py     # 캐싱
scripts/critical_file_detector.py # 우선순위 분류
```

### 테스트
```
tests/test_deep_analyzer.py
tests/test_team_stats_aggregator.py
tests/test_worker_pool.py
tests/test_phase_c_week2_integration.py
```

### 문서
```
docs/PHASE_C_WEEK2_SUMMARY.md     # 전체 요약
docs/DEEP_ANALYZER_GUIDE.md       # DeepAnalyzer 사용법
docs/TEAM_STATS_GUIDE.md          # TeamStats 사용법
docs/SCALABILITY_GUIDE.md         # WorkerPool 사용법
RELEASE_NOTES.md                  # v0.3.0 릴리즈
```

---

## 협업 프로토콜

### 코드 리뷰 요청
```
1. 구현 완료 후 Codex에게 코드 리뷰 요청
2. Gemini에게 아키텍처 검증 요청
3. 두 에이전트의 피드백 통합
4. 개선 후 재검토
```

### 의사결정 프로세스
```
1. 기술적 선택지 나열
2. Codex: 구현 난이도 평가
3. Gemini: 장기적 유지보수성 평가
4. 종합하여 최종 결정
```

### 문서화
```
1. 주요 결정사항 기록
2. 에이전트 피드백 요약
3. 옵시디언에 최소 형식으로 저장
```

---

## 예상 질문 및 답변

### Q1: 왜 Flask/FastAPI?
**A**:
- Python 기반 (기존 코드 재사용)
- 빠른 프로토타입 (Flask)
- 고성능 필요시 FastAPI로 전환 가능
- WebSocket 지원

### Q2: React 필수인가?
**A**:
- 초기: Vanilla JS로 프로토타입 가능
- 확장: React로 전환 (컴포넌트화)
- 대안: Vue, Svelte도 가능

### Q3: MCP 서버 통합 우선순위?
**A**:
- Phase D Week 3-4 (웹 대시보드 안정화 후)
- context7: 검증 정확도 향상
- sequential-thinking: 복잡한 분석

---

## 성공 기준

### Phase D 완료 조건
- ✅ 웹 대시보드 동작 (localhost:5000)
- ✅ 실시간 파일 모니터링
- ✅ 100+ 파일에서 성능 테스트 통과
- ✅ 옵시디언 자동화 (토큰 <1000/일)
- ✅ 문서 완성 (API 문서, 사용 가이드)

### 품질 기준
- ✅ 테스트 커버리지 >80%
- ✅ API 응답 시간 <100ms
- ✅ WebSocket 지연 <50ms
- ✅ 프론트엔드 렌더링 <1초

---

## 참고 자료

### 외부 라이브러리
- Flask: https://flask.palletsprojects.com/
- FastAPI: https://fastapi.tiangolo.com/
- Socket.IO: https://socket.io/
- React: https://react.dev/
- Chart.js: https://www.chartjs.org/
- watchdog: https://github.com/gorakhargosh/watchdog

### 내부 문서
- [[Phase C Week 2 개발 학습 가이드]]
- [[Phase C Week 2 릴리즈 노트]]
- [[초보 개발자를 위한 전체 개발 흐름]]
- [[옵시디언 자동 업데이트 계획]]

---

**이 문서는 Phase D 개발 시작 시 Codex와 Gemini에게 공유됩니다.**

컨텍스트 공유 방법:
1. 이 파일을 읽어서 요약
2. 구체적 질문과 함께 에이전트에게 전달
3. 피드백을 받아 문서 업데이트

---

*Last updated: 2025-01-27*
*Next: Phase D Week 1 시작*
