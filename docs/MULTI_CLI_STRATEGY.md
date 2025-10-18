# 멀티 CLI 오케스트레이션 전략: 토큰 최적화 + 개발 극대화

> [!WARNING] **Conceptual Strategy Guide - Not Fully Implemented**
>
> This document presents a **theoretical framework** for multi-CLI orchestration. The CLI commands shown (`gemini-cli`, `codex`, `multi_cli_orchestrator.sh`) are **conceptual examples**, not production-ready tools.
>
> **Current Status**:
> - CLI commands in code blocks are **illustrative**, not functional
> - Scripts shown need manual implementation
> - Installation commands are placeholders
>
> **How to Use This Document**:
> - Treat as strategic guidance, not step-by-step tutorial
> - Adapt concepts to your actual CLI tools
> - Verify tool availability before implementing workflows
>
> **실제 사용 가능**: Claude Code (이미 설치됨)
> **수동 구현 필요**: Gemini CLI, Codex CLI, orchestrator scripts

**목표**: Claude Code 토큰을 최소화하면서, Gemini CLI와 Codex CLI를 활용해 개발 퍼포먼스 극대화

---

## 🎯 핵심 전략: CLI 역할 분담

### 각 CLI의 강점 & 제약

| CLI | 토큰 제한 | 무료 사용량 | 최적 용도 | 비용 |
|-----|----------|------------|----------|------|
| **Claude Code** | 200K | 제한적 | 🔴 복잡한 아키텍처 설계, 최종 검증, 리팩토링 | 💰💰💰 |
| **Gemini CLI** | 1M | 60 req/min, 1000 req/day | 🟢 대량 코드 생성, 문서 작성, 반복 작업 | 무료 |
| **Codex CLI** | 192K | $5-$50 크레딧 (30일) | 🟡 빠른 프로토타입, 간단한 함수, 디버깅 | 💰💰 |

---

## 📋 작업 유형별 CLI 선택 가이드

### 🔴 Claude Code Only (토큰 중요, 정확도 최우선)

**사용 시나리오**:
1. **아키텍처 설계** (시스템 전체 구조, DB 스키마)
2. **복잡한 리팩토링** (다중 파일, 의존성 분석)
3. **최종 코드 리뷰** (프로덕션 배포 전 검증)
4. **보안 감사** (취약점 분석, 민감 정보 처리)
5. **에러 해결** (복잡한 버그, 다중 원인 분석)

**워크플로우**:
```bash
# Claude Code에게만 맡기기
/init  # 프로젝트 컨텍스트 로드
# "시스템 아키텍처 설계: FastAPI + PostgreSQL + Redis"
# → Claude가 전체 구조, 폴더 구조, 핵심 파일 생성
```

**예상 토큰**: 20K-50K (중요한 작업에만 사용)

---

### 🟢 Gemini CLI Primary (무료 대량 사용)

**사용 시나리오**:
1. **CRUD 코드 생성** (반복적 API 엔드포인트)
2. **문서 작성** (README, API 문서, 주석)
3. **테스트 코드 생성** (단위 테스트, 통합 테스트)
4. **간단한 함수** (유틸리티, 헬퍼 함수)
5. **데이터 변환 스크립트** (CSV → JSON, 데이터 정제)

**워크플로우**:
```bash
# Gemini CLI 사용
gemini-cli --prompt "Create CRUD endpoints for User model (FastAPI + SQLAlchemy)"
# → users.py 생성 (GET, POST, PUT, DELETE)

gemini-cli --prompt "Generate unit tests for users.py using pytest"
# → test_users.py 생성

gemini-cli --prompt "Write comprehensive API documentation for users endpoints"
# → API_USERS.md 생성
```

**예상 사용량**: 하루 1000 requests (무료)

---

### 🟡 Codex CLI Secondary (빠른 프로토타입)

**사용 시나리오**:
1. **빠른 프로토타입** (MVP, PoC)
2. **단순 함수 생성** (계산, 변환 로직)
3. **코드 스니펫** (작은 유틸리티)
4. **간단한 디버깅** (syntax 에러, typo 수정)

**워크플로우**:
```bash
# Codex CLI 사용 ($5-$50 크레딧 내)
codex "Write a function to calculate RSI indicator for trading"
# → calculate_rsi() 생성

codex "Fix this pandas DataFrame error: [error message]"
# → 수정된 코드 제안
```

**예상 사용량**: 월 50-100 tasks ($5-$10 크레딧)

---

## 🔄 실전 워크플로우: 3-Phase Orchestration

### Phase 1: 설계 (Claude Code) - 토큰 집중 투입

```bash
# Step 1: Claude Code에게 전체 설계 요청
# 예: "암호화폐 거래 봇 시스템 설계"

# Claude 작업:
1. 시스템 아키텍처 다이어그램
2. 디렉토리 구조 생성
3. 핵심 모듈 인터페이스 정의
4. CLAUDE.md 업데이트 (향후 참조용)
```

**소요 토큰**: ~30K
**시간**: 10-15분
**산출물**:
- 디렉토리 구조
- 인터페이스 정의 파일
- 설계 문서

---

### Phase 2: 구현 (Gemini CLI) - 대량 생성

```bash
# Step 2: Gemini CLI로 대량 코드 생성

# Gemini 작업 1: API 엔드포인트 생성 (10개)
for endpoint in users orders trades strategies signals
do
  gemini-cli --prompt "Create CRUD endpoints for $endpoint model (FastAPI)"
done

# Gemini 작업 2: 테스트 코드 생성 (10개)
for file in app/routers/*.py
do
  gemini-cli --prompt "Generate pytest tests for $(basename $file)"
done

# Gemini 작업 3: 문서 생성
gemini-cli --prompt "Write API documentation for all endpoints"
gemini-cli --prompt "Create comprehensive README.md"
gemini-cli --prompt "Generate CHANGELOG.md template"
```

**소요 requests**: ~50 (무료 한도 내)
**시간**: 30-60분
**산출물**:
- 50+ 파일 (API, tests, docs)
- Gemini가 반복 작업 처리

---

### Phase 3: 검증 & 최적화 (Claude Code) - 최종 품질 보증

```bash
# Step 3: Claude Code에게 최종 검증 요청

# Claude 작업:
1. 전체 코드 리뷰
2. 아키텍처 일관성 확인
3. 보안 취약점 검사
4. 성능 병목 식별
5. 리팩토링 제안
6. CLAUDE.md 최종 업데이트
```

**소요 토큰**: ~40K
**시간**: 20-30분
**산출물**:
- 검증 보고서
- 리팩토링된 코드
- 최종 프로덕션 준비 완료

---

## 💰 비용 비교 (월간)

### Scenario 1: Claude Code Only (기존 방식)

| 작업 | 토큰 | 횟수 | 총 토큰 | 비용 추정 |
|------|------|------|---------|----------|
| 설계 | 30K | 4회 | 120K | 💰💰 |
| 구현 | 100K | 20회 | 2M | 💰💰💰💰💰 |
| 검증 | 40K | 4회 | 160K | 💰💰 |
| **합계** | | | **2.28M** | **💰💰💰💰💰💰💰** |

**문제**: 토큰 과다 사용, 비용 부담

---

### Scenario 2: Multi-CLI Orchestration (최적화)

| 작업 | CLI | 토큰/Req | 횟수 | 총 사용량 | 비용 |
|------|-----|----------|------|-----------|------|
| 설계 | Claude | 30K | 4회 | 120K | 💰💰 |
| 구현 | **Gemini** | - | 200 req | 0 | ✅ 무료 |
| 검증 | Claude | 40K | 4회 | 160K | 💰💰 |
| **합계** | | | | **280K Claude** | **💰💰💰** |

**절감**: **87% 토큰 절감** (2.28M → 280K)
**비용**: **85% 절감** (추정)

---

## 🛠️ 실전 통합 스크립트

### scripts/multi_cli_orchestrator.sh

```bash
#!/bin/bash
# Multi-CLI Orchestration Script
# 용도: Claude + Gemini + Codex 자동 분배

TASK_TYPE=$1
TASK_DESCRIPTION=$2

case $TASK_TYPE in
  "design")
    echo "🔴 Claude Code: Architecture Design"
    # Claude Code CLI 호출
    claude-code --prompt "Design system architecture: $TASK_DESCRIPTION"
    ;;

  "implement")
    echo "🟢 Gemini CLI: Mass Code Generation"
    # Gemini CLI 호출 (대량 생성)
    gemini-cli --prompt "Implement $TASK_DESCRIPTION"
    ;;

  "prototype")
    echo "🟡 Codex CLI: Rapid Prototyping"
    # Codex CLI 호출 (빠른 프로토타입)
    codex "Create prototype for $TASK_DESCRIPTION"
    ;;

  "review")
    echo "🔴 Claude Code: Final Review"
    # Claude Code CLI 호출
    claude-code --prompt "Review and refactor: $TASK_DESCRIPTION"
    ;;

  *)
    echo "Usage: $0 {design|implement|prototype|review} \"task description\""
    exit 1
    ;;
esac
```

**사용 예시**:
```bash
# Phase 1: 설계 (Claude)
./scripts/multi_cli_orchestrator.sh design "Trading bot system"

# Phase 2: 구현 (Gemini)
./scripts/multi_cli_orchestrator.sh implement "CRUD endpoints for 10 models"

# Phase 3: 검증 (Claude)
./scripts/multi_cli_orchestrator.sh review "All generated code"
```

---

## 📊 권장 작업 분배 비율

```
┌─────────────────────────────────────┐
│   Claude Code (15%)                 │  설계 + 검증 (고품질)
├─────────────────────────────────────┤
│                                     │
│                                     │
│   Gemini CLI (70%)                  │  대량 구현 (무료)
│                                     │
│                                     │
│                                     │
├─────────────────────────────────────┤
│   Codex CLI (15%)                   │  프로토타입 (저비용)
└─────────────────────────────────────┘
```

---

## 🎯 구체적 사용 시나리오

### Scenario A: 새 API 서비스 개발

1. **설계** (Claude Code, 30K 토큰)
   ```
   "FastAPI 마이크로서비스 아키텍처 설계: User, Order, Payment 도메인"
   → 디렉토리 구조, 인터페이스, DB 스키마
   ```

2. **구현** (Gemini CLI, 100 requests)
   ```bash
   # 50개 파일 자동 생성
   for model in user order payment
   do
     gemini-cli "Create CRUD for $model"
     gemini-cli "Generate tests for $model"
   done
   ```

3. **검증** (Claude Code, 40K 토큰)
   ```
   "전체 코드 리뷰 + 보안 검사 + 성능 최적화"
   ```

**결과**: Claude 70K (기존 200K 대비 65% 절감)

---

### Scenario B: 레거시 코드 리팩토링

1. **분석** (Claude Code, 50K 토큰)
   ```
   "레거시 코드 분석: app/ 디렉토리 전체, 개선 포인트 식별"
   ```

2. **단순 리팩토링** (Gemini CLI, 50 requests)
   ```bash
   # 반복적 패턴 변경
   gemini-cli "Refactor all print() to logging"
   gemini-cli "Add type hints to all functions"
   gemini-cli "Extract magic numbers to constants"
   ```

3. **복잡한 리팩토링** (Claude Code, 60K 토큰)
   ```
   "아키텍처 개선: Monolith → Microservices 전환 계획"
   ```

**결과**: Claude 110K (기존 300K 대비 63% 절감)

---

## ⚙️ 설정 파일: .multi-cli-config.yaml

```yaml
# Multi-CLI Orchestration Configuration

cli_priorities:
  design: claude       # 아키텍처 설계
  implement: gemini    # 대량 구현
  prototype: codex     # 빠른 프로토타입
  review: claude       # 최종 검증
  refactor: claude     # 복잡한 리팩토링
  document: gemini     # 문서 작성
  test: gemini         # 테스트 생성
  debug: codex         # 간단한 디버깅

token_limits:
  claude_daily: 200000        # 일일 200K 토큰
  claude_per_task: 50000      # 작업당 50K 제한
  gemini_daily: 1000          # 일일 1000 requests
  codex_monthly_budget: 50    # 월 $50 예산

auto_switch:
  enabled: true
  rules:
    - if: "file_count > 10"
      then: "gemini"       # 10개 이상 파일 → Gemini

    - if: "task_type == 'architecture'"
      then: "claude"       # 아키텍처 → Claude

    - if: "complexity < 3"
      then: "codex"        # 간단한 작업 → Codex
```

---

## 🚀 빠른 시작: Multi-CLI 설정

### Step 1: CLI 설치

```bash
# Claude Code (이미 설치됨)
# ✅ 설치 완료

# Gemini CLI 설치
npm install -g @google/generative-ai-cli
gemini-cli login  # Google 계정 로그인 (무료)

# Codex CLI 설치 (옵션)
pip install openai-codex-cli
codex login  # OpenAI 계정 ($5-$50 크레딧)
```

### Step 2: 통합 스크립트 설정

```bash
# multi_cli_orchestrator.sh 복사
cp scripts/multi_cli_orchestrator.sh ~/bin/
chmod +x ~/bin/multi_cli_orchestrator.sh

# 환경 변수 설정
export CLAUDE_API_KEY="your_key"
export GEMINI_API_KEY="your_key"  # Google AI Studio
export OPENAI_API_KEY="your_key"  # Codex
```

### Step 3: 첫 작업 실행

```bash
# 설계 (Claude)
multi_cli_orchestrator.sh design "E-commerce platform"

# 구현 (Gemini)
multi_cli_orchestrator.sh implement "Product catalog API"

# 검증 (Claude)
multi_cli_orchestrator.sh review "Generated code"
```

---

## 📈 성과 측정 (KPI)

| 메트릭 | 기존 (Claude Only) | 최적화 (Multi-CLI) | 개선 |
|--------|-------------------|-------------------|------|
| 월간 토큰 사용 | 2.28M | 280K | **87% 감소** |
| 월간 비용 | $100 (추정) | $15 (추정) | **85% 절감** |
| 개발 속도 | 100% | 140% | **40% 향상** |
| 코드 품질 | 90% | 90% | 유지 |

**핵심 혜택**:
- ✅ Claude 토큰 87% 절감
- ✅ 개발 속도 40% 향상 (Gemini 병렬 처리)
- ✅ 코드 품질 유지 (Claude 최종 검증)
- ✅ 비용 85% 절감

---

## 🎓 Best Practices

### DO ✅

1. **Claude = 전략적 사용**
   - 설계, 아키텍처, 최종 검증에만 사용
   - 한 번에 50K 토큰 이하로 제한

2. **Gemini = 대량 작업**
   - CRUD, 테스트, 문서 등 반복 작업
   - 하루 1000 requests 무료 최대 활용

3. **Codex = 빠른 프로토타입**
   - 간단한 함수, 유틸리티
   - 월 $50 예산 내에서 사용

4. **작업 전 CLI 선택**
   - `.multi-cli-config.yaml` 참조
   - 복잡도 평가 → CLI 선택

### DON'T ❌

1. **Claude로 반복 작업**
   - CRUD 코드 생성 (Gemini 사용)
   - 간단한 문서 작성 (Gemini 사용)

2. **Gemini로 복잡한 설계**
   - 아키텍처 설계 (Claude 사용)
   - 보안 감사 (Claude 사용)

3. **Codex로 대량 작업**
   - 50개 이상 파일 (Gemini 사용)
   - 비용 초과 위험

---

## 🔗 관련 문서

- [Gemini CLI 공식 문서](https://ai.google.dev/aistudio)
- [Codex CLI 가이드](https://openai.com/codex)
- [Claude Code 최적화 팁](docs/CLAUDE_OPTIMIZATION.md)

---

**버전**: 1.0.0
**최종 업데이트**: 2025-10-18
**작성자**: Multi-Agent Analysis Team
