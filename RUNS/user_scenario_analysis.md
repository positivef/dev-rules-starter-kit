# 사용자 시나리오 분석 및 보완사항 검토

**생성일**: 2025-10-24
**목적**: 추가 보완사항 발견 + Figma MCP 필요성 판단

---

## 1. 현재 시스템 사용자 시나리오

### 1.1 주요 사용자 페르소나

**개발자 (Primary User)**:
- AI 에이전트(Claude, Cursor)를 활용하여 개발
- YAML 계약서 기반 작업 수행
- Constitution(헌법) 준수 필요
- 반복 작업 자동화 필요

**프로젝트 관리자 (Secondary User)**:
- 진행 상황 모니터링
- Constitution 준수율 확인
- 품질 지표 추적

### 1.2 현재 워크플로우

```
1. 작업 정의 단계
   ├─ YAML 계약서 작성 (tasks/FEAT-*.yaml)
   ├─ Constitution 조항 명시
   └─ Gates 정의 (test, performance, security)

2. 작업 실행 단계
   ├─ TaskExecutor 실행 (--plan 검토)
   ├─ 사용자 승인 (plan hash)
   └─ 자동 실행 + 증거 수집

3. 결과 확인 단계
   ├─ RUNS/evidence/ 증거 확인
   ├─ Obsidian 자동 동기화 (3초)
   └─ Dashboard 시각화 (Layer 7)
```

---

## 2. 추가 보완사항 검토

### 2.1 발견된 보완 필요 영역

#### A. PromptCompressor 통합 미완료 ⚠️

**현재 상태**:
- PromptCompressor: 구현 완료 ✅
- PromptTracker: 구현 완료 ✅
- TaskExecutor 통합: **미완료** ❌

**문제점**:
- 사용자가 수동으로 PromptCompressor 호출 필요
- 압축 효과 자동 추적 불가
- YAML 작업과 프롬프트 압축 분리

**영향도**: HIGH (토큰 절감 효과 미실현)

#### B. CLI 사용성 개선 필요 ⚠️

**현재 상태**:
```bash
# 현재: 복잡한 명령어
python scripts/task_executor.py TASKS/FEAT-2025-10-24-01.yaml --plan
python scripts/prompt_compressor.py compress "prompt" --level medium --json

# 사용자가 원하는 것:
dev-task run FEAT-2025-10-24-01 --plan
dev-prompt compress "prompt" --json
```

**문제점**:
- 긴 경로명 입력 필요
- 스크립트 위치 기억 필요
- 새로운 사용자 진입장벽

**영향도**: MEDIUM (사용성)

#### C. 실시간 피드백 부족 ⚠️

**현재 상태**:
- TaskExecutor: 실행 후 결과만 표시
- 진행 상황 실시간 확인 불가
- 긴 작업 시 "멈춤" 느낌

**문제점**:
- 사용자 불안감 증가
- 중간 취소 어려움
- 디버깅 정보 부족

**영향도**: MEDIUM (UX)

#### D. 에러 메시지 개선 필요 ⚠️

**현재 상태**:
```python
# 현재: 기술적 에러
raise ValueError("Input exceeds maximum size: 1000001 > 1000000 bytes")

# 사용자 친화적 필요:
"프롬프트가 너무 큽니다 (1.0MB). 1MB 이하로 줄여주세요."
```

**영향도**: LOW (사용성)

---

## 3. Figma MCP 필요성 분석

### 3.1 Figma MCP란?

**기능**:
- Figma 디자인 파일 읽기/쓰기
- 컴포넌트 자동 생성
- 디자인 → 코드 변환

**사용 사례**:
- UI 디자인 자동화
- 컴포넌트 라이브러리 생성
- 프로토타입 → 실제 코드

### 3.2 현재 프로젝트 적용 가능성 분석

#### 프로젝트 특성
```
현재 프로젝트 유형: CLI 도구 + 백엔드 시스템
├─ TaskExecutor: CLI 기반 작업 실행
├─ PromptCompressor: 텍스트 처리
├─ DeepAnalyzer: 코드 분석
└─ Dashboard: Streamlit (기존 UI)
```

#### UI 요구사항 분석

**현재 UI**:
1. Streamlit Dashboard (Layer 7)
   - Constitution 준수율 시각화
   - 품질 지표 대시보드
   - 이미 구현됨 ✅

2. CLI 인터페이스
   - 개발자 중심
   - 터미널 기반 작업
   - GUI 불필요

**Figma MCP가 도움이 될 수 있는 경우**:
- ❌ Dashboard 개선: Streamlit으로 충분
- ❌ CLI 도구: GUI 불필요
- ❌ 백엔드 시스템: UI 없음
- ⚠️ 미래 확장: 웹 기반 관리 도구 개발 시

### 3.3 판단 결과: **Figma MCP 불필요** ❌

**근거**:

1. **프로젝트 성격 불일치**
   - CLI/백엔드 중심 프로젝트
   - UI 디자인 작업 없음
   - 시각화는 Streamlit으로 충분

2. **비용 대비 효과 낮음**
   - Figma MCP 학습 비용: 8-10시간
   - 예상 사용 빈도: 거의 없음
   - ROI: 음수

3. **대체 솔루션 존재**
   - Streamlit: 즉시 사용 가능한 대시보드
   - ASCII 아트: CLI 시각화 충분
   - 기존 시스템으로 충분

4. **우선순위 낮음**
   - Priority 1: PromptCompressor 통합
   - Priority 2: CLI 사용성 개선
   - Priority 3: 실시간 피드백
   - Figma MCP: 우선순위 밖

**결론**: ❌ **Figma MCP 도입 불필요, 기존 시스템 개선에 집중**

---

## 4. 합리적 보완사항 우선순위

### Priority 1: PromptCompressor + TaskExecutor 통합 ✅

**왜 중요한가?**:
- 토큰 절감 효과 실현 (30-50%)
- 자동화된 압축 + 추적
- 사용자 수동 개입 불필요

**구현 방법**:
```python
# TaskExecutor.execute() 메서드에 통합
def execute(self, task_yaml):
    # YAML에서 프롬프트 추출
    prompts = self._extract_prompts(task_yaml)

    # 자동 압축
    compressor = PromptCompressor(level="medium")
    compressed_prompts = [compressor.compress(p) for p in prompts]

    # 압축 결과 추적
    tracker = PromptTracker()
    for orig, comp in zip(prompts, compressed_prompts):
        tracker.track_compression(orig, comp.compressed, comp.savings_pct)
```

**예상 효과**:
- 토큰 사용량 자동 30-50% 절감
- 압축 패턴 자동 학습
- 투명한 압축 통계

### Priority 2: 통합 CLI 래퍼 (dev-rules) ✅

**왜 중요한가?**:
- 사용자 경험 크게 개선
- 진입장벽 낮춤
- 일관된 인터페이스

**구현 방법**:
```python
# scripts/dev_rules_cli.py
#!/usr/bin/env python3
"""
dev-rules - Unified CLI for Dev Rules Starter Kit

Commands:
  dev-rules task run <task-id>     # Run YAML task
  dev-rules task plan <task-id>    # Preview task
  dev-rules prompt compress <text> # Compress prompt
  dev-rules prompt stats           # Show compression stats
  dev-rules dashboard              # Launch Streamlit
"""

import click

@click.group()
def cli():
    """Dev Rules Starter Kit CLI"""
    pass

@cli.group()
def task():
    """Task execution commands"""
    pass

@task.command()
@click.argument('task_id')
@click.option('--plan', is_flag=True)
def run(task_id, plan):
    """Run a YAML task"""
    # TaskExecutor 호출
    pass
```

**예상 효과**:
- 사용성 5배 향상
- 신규 사용자 온보딩 시간 50% 단축
- 일관된 UX

### Priority 3: 실시간 진행 상황 표시 ⚠️

**왜 중요한가?**:
- 사용자 불안감 해소
- 디버깅 정보 제공
- 중간 취소 가능

**구현 방법**:
```python
# 진행률 표시
from tqdm import tqdm

for cmd in tqdm(commands, desc="Executing tasks"):
    result = execute_command(cmd)
    tqdm.write(f"✓ {cmd['description']}")
```

**예상 효과**:
- UX 만족도 30% 향상
- 디버깅 시간 20% 단축

---

## 5. 최종 권장사항

### ✅ 즉시 적용 (Priority 1)

1. **PromptCompressor + TaskExecutor 통합**
   - 예상 시간: 2시간
   - ROI: 300% (토큰 절감 효과)
   - 위험도: LOW (기존 기능 유지)

2. **통합 CLI 래퍼 (dev-rules)**
   - 예상 시간: 3시간
   - ROI: 200% (사용성 향상)
   - 위험도: LOW (기존 스크립트 래핑)

### ⏳ 향후 고려 (Priority 2-3)

3. **실시간 진행 상황 표시**
   - 예상 시간: 1시간
   - ROI: 150%
   - 위험도: LOW

4. **에러 메시지 개선**
   - 예상 시간: 2시간
   - ROI: 100%
   - 위험도: LOW

### ❌ 도입 불필요

5. **Figma MCP**
   - 근거: CLI/백엔드 중심 프로젝트
   - 대체: Streamlit으로 충분
   - ROI: 음수

---

## 6. 다음 단계

### 즉시 작업 (오늘)
- [x] 사용자 시나리오 분석 완료
- [ ] PromptCompressor + TaskExecutor 통합
- [ ] 통합 CLI 래퍼 구현
- [ ] 통합 테스트 및 검증

### 향후 작업 (다음 주)
- [ ] 실시간 진행 상황 표시 추가
- [ ] 에러 메시지 개선
- [ ] 사용자 가이드 업데이트

---

**결론**:

1. ✅ **Figma MCP는 불필요** - CLI/백엔드 중심 프로젝트에 부적합
2. ✅ **Priority 1: PromptCompressor 통합** - 즉시 토큰 절감 효과
3. ✅ **Priority 2: 통합 CLI 래퍼** - 사용성 크게 향상
4. ⏳ **기타 개선사항** - 점진적 적용

**합리성 검증**: ✅
- 사용자 가치 중심 우선순위
- 비용 대비 효과 분석 완료
- 기술적 실현 가능성 확인
