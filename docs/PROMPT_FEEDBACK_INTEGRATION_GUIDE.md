# Prompt Feedback System - Integration Guide

프롬프트 피드백 시스템을 개발 워크플로우에 통합하는 완전한 가이드입니다.

## 통합 개요

프롬프트 피드백 시스템은 4가지 방식으로 자동화할 수 있습니다:

1. **Claude Code 슬래시 커맨드** - 대화형 분석 및 개선
2. **Git Hook** - 커밋 메시지 품질 자동 분석
3. **CI/CD (GitHub Actions)** - PR 설명 자동 검사
4. **TaskExecutor 통합** - YAML 계약서 품질 게이트

---

## 1. Claude Code 슬래시 커맨드

### 사용 가능한 커맨드

#### `/analyze-prompt`
프롬프트 품질을 즉시 분석합니다.

**사용법**:
```
/analyze-prompt "fix the bug in authentication"
```

**출력 예시**:
```
Prompt Quality Analysis
======================

Score: 45/100 (Beginner)

Dimensions:
- Clarity: 40/100 (ambiguous: "the bug", "fix")
- Logic: 50/100 (no logical flow)
- Context: 35/100 (missing: where, what, why)
- Structure: 55/100 (single sentence)

Top Improvements:
1. Specify which bug (location, symptoms)
2. Add context (tech stack, current behavior)
3. Define expected outcome

Recommended MCP: --sequential (for debugging)
```

#### `/improve-prompt`
프롬프트를 3가지 레벨로 개선합니다.

**사용법**:
```
/improve-prompt "debug the API"
```

**출력 예시**:
```
Version A (Minimal) - Score 65:
"Debug the slow API response in /users endpoint"

Version B (Balanced) - Score 82:
"Debug the /users endpoint that's responding in 5+ seconds.
Expected: < 200ms response time"

Version C (Comprehensive) - Score 95:
"Using Python 3.9 and FastAPI:
1. Debug the /users endpoint (routes/users.py:45)
2. Current: 5000ms response time
3. Expected: < 200ms
4. Suspected cause: N+1 query issue
5. Add performance logging"

Recommended: Version B
MCP: --sequential, --morphllm (for optimization)
```

### 워크플로우 예시

**작업 시작 전**:
```
1. /analyze-prompt "your initial prompt"
2. 점수 확인 (목표: 70+ )
3. 점수가 낮으면: /improve-prompt "your initial prompt"
4. 개선된 버전 사용
```

---

## 2. Git Hook 통합

### 자동 커밋 메시지 분석

커밋 후 자동으로 메시지 품질을 분석하고 피드백을 제공합니다.

**수동 실행**:
```bash
python scripts/analyze_commit_message.py
```

**출력 예시**:
```
============================================================
Commit Message Quality Analysis
============================================================
Overall Score: 75/100 - Good

Your commit message is clear and provides adequate context.

Use '/improve-prompt' command in Claude Code for suggestions.
============================================================
```

### Post-commit Hook 통합

현재 post-commit hook에 자동으로 실행되도록 통합할 수 있습니다:

**`.git/hooks/post-commit`에 추가**:
```python
def analyze_commit_message():
    """커밋 메시지 품질 분석"""
    result = subprocess.run(
        ["python", "scripts/analyze_commit_message.py"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
```

### 권장 사항

**좋은 커밋 메시지 기준**:
- 점수 70+ : 명확하고 충분한 컨텍스트
- 점수 85+ : 우수한 품질, 팀 모범 사례

**개선 팁**:
```bash
# Bad (Score: 45)
git commit -m "fix bug"

# Better (Score: 72)
git commit -m "fix: resolve authentication timeout in auth.py"

# Best (Score: 88)
git commit -m "fix(auth): resolve session timeout bug in auth.py line 45

Users were getting logged out after 5 minutes instead of 30.
Root cause: SESSION_TIMEOUT configured in seconds, not minutes.

Fixes #123"
```

---

## 3. CI/CD 통합 (GitHub Actions)

### 자동 PR 설명 품질 검사

**파일**: `.github/workflows/pr-quality-check.yml`

**동작**:
- PR이 열리거나 수정될 때 자동 실행
- PR 설명의 품질을 분석
- 자동으로 코멘트 추가

**결과 예시**:

**빈 PR 설명**:
```
⚠️ No PR description provided

Please add a description that includes:
- What changes were made
- Why the changes were necessary
- How to test the changes
```

**낮은 품질 (Score < 50)**:
```
📊 Quality Score: 45/100 (Needs Improvement)

Suggestions for improvement:
- Add more specific details about what changed
- Explain WHY the changes were made
- Include test instructions
```

**좋은 품질 (Score 65-79)**:
```
✅ Quality Score: 75/100 (Good)

Good PR description with adequate detail and context.
```

**우수한 품질 (Score 80+)**:
```
🌟 Quality Score: 88/100 (Excellent)

Outstanding PR description! Clear, specific, and excellent context.
```

### PR 템플릿

**`.github/pull_request_template.md` 생성**:
```markdown
## Summary
<!-- Brief description of changes -->

## Motivation
<!-- Why these changes are necessary -->

## Changes
- [ ] Specific change 1
- [ ] Specific change 2

## Testing
<!-- How to verify the changes -->

## Screenshots (if applicable)
<!-- Visual proof of changes -->

<!-- This PR template helps achieve 80+ quality score -->
```

---

## 4. TaskExecutor 통합

### YAML 계약서에 품질 게이트 추가

**예시 파일**: `TASKS/EXAMPLE-WITH-PROMPT-QUALITY-GATE.yaml`

**게이트 타입**:

#### 1. 사전 검증 게이트
```yaml
gates:
  - type: "prompt_quality"
    min_score: 70
    dimensions:
      clarity: 65
      logic: 60
      context: 60
    target: "{{description}}"
```

#### 2. 페이즈별 검증
```yaml
phases:
  - name: "analysis"
    description: |
      Analyze the authentication flow in src/auth/
      focusing on session management and security
    gates:
      - type: "prompt_quality"
        min_score: 75
```

#### 3. 커스텀 스크립트 게이트
```yaml
gates:
  - type: "custom_script"
    command: ["python", "scripts/prompt_feedback_cli.py"]
    args: ["{{title}}", "--threshold", "70"]
```

### 실행 방법

```bash
# 계획만 확인 (게이트 검증 포함)
python scripts/task_executor.py TASKS/YOUR-TASK.yaml --plan

# 실행 (게이트 실패 시 중단)
python scripts/task_executor.py TASKS/YOUR-TASK.yaml
```

### 게이트 실패 시

```
[GATE] Checking prompt_quality gate...
[FAIL] Quality score 55/100 below minimum 70
[FAIL] Clarity score 45/100 below minimum 65

Suggestions:
1. Add specific file paths and line numbers
2. Explain WHY the change is needed
3. Define expected outcome

Gate validation failed. Please improve task description.
```

---

## 통합 워크플로우 예시

### 일반적인 개발 흐름

**1. 작업 시작**
```
1. YAML 계약서 작성
2. /analyze-prompt로 description 검증
3. 점수 < 70이면 /improve-prompt로 개선
4. TaskExecutor로 실행
```

**2. 개발 중**
```
1. 변경사항 커밋
2. Git hook이 자동으로 메시지 품질 분석
3. 점수 < 70이면 개선 팁 확인
```

**3. PR 생성**
```
1. PR 설명 작성
2. GitHub Actions가 자동 검사
3. 품질 점수 코멘트 확인
4. 필요시 설명 개선
```

**4. 학습 및 개선**
```
1. 팀 평균 점수 추적
2. 베스트 프랙티스 공유
3. 템플릿 지속 개선
```

---

## 품질 기준

### 점수 기준

| 점수 | 등급 | 의미 | 조치 |
|------|------|------|------|
| 90-100 | Expert | 완벽한 명확성과 컨텍스트 | 모범 사례로 공유 |
| 75-89 | Advanced | 명확하고 충분한 설명 | 그대로 사용 가능 |
| 60-74 | Intermediate | 기본은 갖춤, 개선 가능 | 선택적 개선 |
| 45-59 | Developing | 불명확하거나 컨텍스트 부족 | 개선 권장 |
| 0-44 | Beginner | 매우 모호하거나 부실함 | 반드시 개선 |

### 차원별 최소 기준

| 차원 | 최소 점수 | 체크 포인트 |
|------|-----------|-------------|
| Clarity | 60 | 모호한 용어 없음 |
| Logic | 55 | 논리적 흐름 존재 |
| Context | 60 | 기술 스택, 제약사항 명시 |
| Structure | 55 | 조직화된 형태 |

---

## 팀 활용 가이드

### 1. 온보딩

**신입 개발자**:
```
1. /analyze-prompt 커맨드 연습
2. 점수 70+ 달성 연습
3. 커밋 메시지 품질 개선
4. PR 템플릿 사용 습관화
```

### 2. 코드 리뷰

**리뷰어**:
```
1. PR 품질 점수 확인
2. 점수 < 65이면 설명 개선 요청
3. 좋은 PR은 모범 사례로 공유
```

### 3. 품질 추적

**팀 메트릭**:
```bash
# 주간 평균 점수
python scripts/prompt_feedback_cli.py --stats --period week

# 팀 랭킹
python scripts/prompt_feedback_cli.py --team-ranking

# 개선 추세
python scripts/prompt_feedback_cli.py --trends
```

---

## 문제 해결

### 분석이 너무 느림

```bash
# 빠른 분석 (기본 체크만)
python scripts/prompt_feedback_cli.py "text" --quick

# 타임아웃 조정
python scripts/prompt_feedback_cli.py "text" --timeout 5
```

### 점수가 너무 낮게 나옴

**일반적인 원인**:
1. 모호한 용어 사용 ("bug", "fix", "thing", "stuff")
2. 컨텍스트 부족 (where, what, why)
3. 구조 없음 (긴 문장 하나)

**해결책**:
```
Before: "fix the authentication"
After: "Fix session timeout in auth.py line 45 - users expire after 5 min instead of 30"
```

### CI/CD 검사가 실패함

**원인**: Python 환경 문제

**해결**:
```yaml
# .github/workflows/pr-quality-check.yml 수정
- name: Install dependencies
  run: |
    pip install -r requirements.txt
```

---

## 고급 사용

### 커스텀 임계값

```python
# scripts/custom_quality_gate.py
from prompt_feedback_analyzer import PromptFeedbackAnalyzer

analyzer = PromptFeedbackAnalyzer()
analysis = analyzer.analyze(prompt)

# 팀별 커스텀 기준
if analysis.clarity_score < 70:
    print("Clarity below team standard")

if "TODO" in prompt or "FIXME" in prompt:
    print("Remove placeholder comments")
```

### 배치 분석

```bash
# 모든 YAML 파일 검사
for file in TASKS/*.yaml; do
  python scripts/prompt_feedback_cli.py "$(cat $file)" --brief
done
```

### 통계 수집

```python
# scripts/collect_quality_stats.py
import json
from pathlib import Path

stats = {
    "commits": [],
    "prs": [],
    "tasks": []
}

# 커밋 메시지 분석
for commit in get_recent_commits():
    analysis = analyze(commit.message)
    stats["commits"].append({
        "hash": commit.hash,
        "score": analysis.overall_score
    })

# 결과 저장
Path("RUNS/quality_stats.json").write_text(json.dumps(stats, indent=2))
```

---

## 체크리스트

### 초기 설정

- [ ] `/analyze-prompt` 커맨드 테스트
- [ ] `/improve-prompt` 커맨드 테스트
- [ ] `analyze_commit_message.py` 실행 확인
- [ ] PR quality check 워크플로우 활성화
- [ ] YAML 계약서 품질 게이트 예시 확인

### 일상적인 사용

- [ ] 커밋 전 메시지 품질 확인
- [ ] PR 생성 시 설명 점수 70+ 확인
- [ ] YAML 작성 시 description 분석
- [ ] 낮은 점수 시 개선 제안 활용

### 팀 관리

- [ ] 주간 평균 점수 추적
- [ ] 베스트 프랙티스 공유
- [ ] 신입 온보딩에 포함
- [ ] 품질 기준 정기 리뷰

---

## 다음 단계

**Phase 2 (계획 중)**:
- 실시간 피드백 (프롬프트 작성 중)
- 팀 대시보드
- 히스토리 분석
- AI 기반 자동 개선 제안

**Phase 3 (고려 중)**:
- VS Code Extension
- Slack 통합
- 머신러닝 기반 패턴 학습

---

## 지원

**문제 보고**: GitHub Issues
**문의**: 팀 채널 #dev-quality
**문서**: docs/PROMPT_FEEDBACK_SYSTEM.md

---

**버전**: 1.0
**마지막 업데이트**: 2025-10-30
