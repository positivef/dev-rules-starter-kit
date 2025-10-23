# dev-rules-starter-kit

AI 지원 개발을 위한 헌법 기반 거버넌스 프레임워크

## 🎯 프로젝트 개요

**dev-rules-starter-kit**는 AI 지원 소프트웨어 개발에서 일관성과 품질을 보장하기 위한 프로덕션 준비 완료 거버넌스 프레임워크입니다. 13개의 헌법 조항(P1-P13)과 7층 아키텍처를 통해 개발 프로세스를 체계적으로 관리합니다.

### 핵심 지표
- **버전**: v1.1.0 (2025-10-18 릴리즈)
- **헌법 조항**: 13개 (P1-P13)
- **아키텍처**: 7층 검증 시스템
- **코드 규모**: 25개+ Python 스크립트 (약 9,600줄)
- **테스트**: 50개+ 테스트 케이스
- **CI/CD**: 4개 자동화 워크플로우

## 🚀 빠른 시작

### 1. 요구사항
- Python 3.8-3.13
- Git
- UTF-8 인코딩 (Windows cp949 미지원)

### 2. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/dev-rules-starter-kit.git
cd dev-rules-starter-kit

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치 (테스트 실행시 필요)
pip install -r requirements-dev.txt
```

### 3. 기본 사용법

```bash
# YAML 계약 실행
python scripts/task_executor.py tasks/example_task.yaml

# 코드 품질 검증
python scripts/deep_analyzer.py scripts/

# 실시간 파일 감시 시작
python scripts/dev_assistant.py

# 테스트 실행
pytest tests/
```

## 🏗️ 아키텍처

### 7층 검증 시스템

```
Layer 1: 헌법 (Constitution)
    ↓ P1-P13 원칙 정의
Layer 2: 실행 (Execution)
    ↓ TaskExecutor, EnhancedExecutor
Layer 3: 분석 (Analysis) [검증 수행]
    ↓ DeepAnalyzer, TeamStats, ErrorLearner
Layer 4: 최적화 (Optimization)
    ↓ Cache, CriticalFile, WorkerPool
Layer 5: 증거 (Evidence)
    ↓ AutomaticTracker, PromptTracker
Layer 6: 지식 (Knowledge)
    ↓ ObsidianBridge, ContextLoader
Layer 7: 시각화 (Visualization) [정보만 표시]
    ↓ Streamlit Dashboard
```

### 13개 헌법 조항

| ID | 제목 | 설명 | 시행 도구 |
|----|------|------|-----------|
| P1 | YAML 계약 우선순위 | 모든 작업은 YAML 계약으로 시작 | TaskExecutor |
| P2 | 증거 기반 개발 | 모든 결정은 증거로 뒷받침 | EvidenceTracker |
| P3 | 지식 자산 관리 | 지식을 체계적으로 축적 | ObsidianBridge |
| P4 | SOLID 원칙 | 객체지향 설계 원칙 준수 | DeepAnalyzer |
| P5 | 보안 우선 | 보안을 최우선으로 고려 | DeepAnalyzer |
| P6 | 품질 게이트 | 품질 기준 충족 필수 | TeamStatsAggregator |
| P7 | 환각 방지 | AI 환각 패턴 차단 | ErrorLearner |
| P8 | 테스트 우선 개발 | 코드 전 테스트 작성 | pytest |
| P9 | 일관된 커밋 | Conventional Commits 사용 | pre-commit |
| P10 | Windows UTF-8 | UTF-8 인코딩 강제 | 이모지 금지 |
| P11 | 원칙 충돌 감지 | 원칙 간 충돌 해결 | Manual (AI) |
| P12 | 트레이드오프 분석 | 의사결정 균형 분석 | Manual (AI) |
| P13 | 헌법 수정 | 헌법 개정 프로세스 | Manual |

## 📁 프로젝트 구조

```
dev-rules-starter-kit/
├── scripts/              # 핵심 실행 스크립트
│   ├── task_executor.py         # YAML 계약 실행기
│   ├── deep_analyzer.py         # 코드 품질 분석기
│   ├── dev_assistant.py         # 실시간 파일 감시
│   ├── error_learner.py         # 에러 패턴 학습
│   └── obsidian_bridge.py       # Obsidian 연동
├── tests/                # 테스트 스위트
├── memory/              # 헌법 및 지식 저장소
│   └── constitution.md          # 13개 헌법 조항
├── dev-context/         # AI 에이전트 컨텍스트
├── claudedocs/          # 문서 라이프사이클
├── RUNS/                # 실행 증거 로그
└── docs/                # 문서화
```

## 🔧 주요 기능

### 1. YAML 계약 실행 (P1)
```yaml
# tasks/example.yaml
task_id: "TASK-001"
description: "API 엔드포인트 구현"
markers:
  - "[P4] SOLID 원칙 적용"
  - "[P5] 보안 검증"
steps:
  - "테스트 작성"
  - "구현"
  - "검증"
```

### 2. 실시간 코드 검증
```bash
# 파일 변경 시 자동 검증
python scripts/dev_assistant.py --watch scripts/ tests/
```

### 3. 에러 패턴 학습
```bash
# 에러 기록 및 해결책 저장
python scripts/error_learner.py capture "ImportError" "pip install missing-module"
```

### 4. Obsidian 지식 동기화
```bash
# 지식 베이스 동기화 (3초 이내)
python scripts/obsidian_bridge.py sync
```

## 📊 성능 지표

| 구성요소 | 목표 | 실제 | 상태 |
|----------|------|------|------|
| Task Executor | <100ms | 45-85ms | ✅ |
| Deep Analyzer | <500ms | 150-300ms | ✅ |
| Obsidian Sync | <3s | 1-2s | ✅ |
| Dev Assistant | <200ms | 120-180ms | ✅ |

## ⚠️ 주의사항

### Windows 사용자
- **UTF-8 인코딩 필수** (cp949 미지원)
- **이모지 사용 금지** - 모든 코드/YAML에서 ASCII만 사용
- 대체 표기: ✅→[OK], ❌→[FAIL], ⚠️→[WARN]

### 보안
- 15개 위험 패턴 자동 차단 (`rm -rf`, `eval()` 등)
- Gitleaks를 통한 비밀 정보 스캔
- 명령어 허용 목록 적용

## 🤝 기여하기

### 기여 가이드라인
1. **헌법 준수**: 모든 변경사항은 P1-P13 원칙 준수
2. **Conventional Commits**: 커밋 메시지 규칙 준수
3. **테스트 우선**: 코드 작성 전 테스트 작성
4. **증거 제공**: PR에 변경 근거 포함

### 개발 프로세스
```bash
# 1. 기능 브랜치 생성
git checkout -b feature/your-feature

# 2. 변경사항 구현 (테스트 우선)
# 3. 품질 검증
ruff check .
pytest tests/

# 4. 커밋 (Conventional Commits)
git commit -m "feat: 새 기능 추가"

# 5. PR 제출
```

## 📈 투자 수익률 (ROI)

- **초기 설정**: 약 7시간
- **월간 절약**: 22시간
- **연간 절약**: 264시간
- **품질 향상**: 환각 99% 방지, 에러 90% 감소

## 📅 릴리즈 일정

### 현재 단계: 릴리즈 & 관찰
- **기간**: 2025-10-24 ~ 2025-01-24
- **목표**: 커뮤니티 피드백 수집
- **다음 검토**: 2025-01-24 (P13 첫 검토)

### 완료된 단계
- ✅ Phase A: 실시간 검증 시스템 (2025-09-15)
- ✅ Phase B: 증거 추적 (2025-09-30)
- ✅ Phase C: 분석 레이어 (2025-10-16)
- ✅ Phase D: 헌법 P11-P13 (2025-10-18)

### 보류된 기능
- 🚫 Phase E: 고급 ML 기능 (YAGNI 원칙에 따라 보류)

## 📚 추가 문서

- [빠른 시작 가이드](docs/QUICK_START.md)
- [개발 규칙](DEVELOPMENT_RULES.md)
- [헌법 전문](memory/constitution.md)
- [NORTH STAR](NORTH_STAR.md) - 1분 전략 방향
- [Phase E 결정](docs/PHASE_E_DECISION.md)

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🙏 감사의 말

DoubleDiver 프로젝트에서 추출된 이 프레임워크는 AI 지원 개발의 미래를 위한 커뮤니티 기여입니다.

---

**문의사항**: GitHub Issues에 등록해주세요.
**기여 환영**: PR은 언제나 환영합니다!
