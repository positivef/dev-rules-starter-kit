# GitHub 피드백 수집 및 반영 가이드

**목적**: 오픈소스 프로젝트에서 피드백을 효과적으로 수집하고 개선에 반영하기

---

## 📥 1. 피드백 수집 채널

### GitHub Issues (버그, 기능 요청)

**URL**: https://github.com/positivef/dev-rules-starter-kit/issues

**확인 방법**:
```bash
# 웹에서 확인
1. https://github.com/positivef/dev-rules-starter-kit/issues
2. New issue 버튼으로 사용자가 생성

# CLI로 확인 (gh 설치 필요)
gh issue list
gh issue view 123
```

**피드백 유형**:
- 🐛 **Bug**: 동작하지 않는 기능
- 💡 **Feature Request**: 새 기능 제안
- 📝 **Documentation**: 문서 개선 요청
- ❓ **Question**: 사용법 질문

---

### GitHub Discussions (일반 논의)

**URL**: https://github.com/positivef/dev-rules-starter-kit/discussions

**활성화 방법**:
```
1. Repository → Settings → Features
2. Discussions 체크박스 활성화
```

**확인 방법**:
```bash
# 웹에서 확인
https://github.com/positivef/dev-rules-starter-kit/discussions

# CLI로 확인 (gh 설치 필요)
gh api repos/positivef/dev-rules-starter-kit/discussions
```

**토론 카테고리**:
- 💬 **General**: 일반 토론
- 💡 **Ideas**: 아이디어 공유
- 🙏 **Q&A**: 질문과 답변
- 📣 **Announcements**: 공지사항
- 🎉 **Show and tell**: 사용 사례 공유

---

### GitHub Stars/Forks (관심도 지표)

**확인 방법**:
```bash
# 웹에서 확인
Repository 페이지 우측 상단
- ⭐ Stars: 관심 표시
- 🍴 Forks: 복사하여 사용 중

# CLI로 확인
gh repo view positivef/dev-rules-starter-kit --json stargazersCount,forksCount
```

**의미**:
- **Stars**: 사용자가 유용하다고 생각함
- **Forks**: 실제로 사용/수정 중

---

### Pull Requests (직접 기여)

**URL**: https://github.com/positivef/dev-rules-starter-kit/pulls

**확인 방법**:
```bash
# 웹에서 확인
https://github.com/positivef/dev-rules-starter-kit/pulls

# CLI로 확인
gh pr list
gh pr view 123
```

**PR 유형**:
- 🐛 **Bug Fix**: 버그 수정
- ✨ **Feature**: 새 기능 추가
- 📝 **Docs**: 문서 개선
- ♻️ **Refactor**: 코드 개선

---

## 📊 2. 피드백 모니터링 (주간 체크리스트)

### 매주 월요일 10분 루틴

```bash
# 1. GitHub 통계 확인
cd C:/Users/user/Documents/GitHub/dev-rules-starter-kit
echo "=== Week $(date +%U) ($(date +%Y-%m-%d)) ===" >> RUNS/observe/github_stats.txt

# 2. Stars/Forks 기록
gh repo view positivef/dev-rules-starter-kit --json stargazersCount,forksCount >> RUNS/observe/github_stats.txt

# 3. 새 Issues 확인
gh issue list --state open --json number,title,createdAt

# 4. 새 Discussions 확인 (웹에서)
# https://github.com/positivef/dev-rules-starter-kit/discussions

# 5. 새 PRs 확인
gh pr list --state open
```

**기록 템플릿** (`RUNS/observe/weekly_checklist.md`):
```markdown
## Week X/12 (YYYY-MM-DD)

### GitHub 모니터링 (5분)
- [ ] Stars: ___ (+___)
- [ ] Forks: ___ (+___)
- [ ] Issues: ___ (+___)
- [ ] Discussions: ___ (+___)
- [ ] PRs: ___ (+___)

### 새 피드백 (3분)
- [ ] Issue #___: [제목] - 우선순위: High/Medium/Low
- [ ] Discussion #___: [제목] - 주제: ___
- [ ] PR #___: [제목] - 리뷰 필요

### 액션 아이템 (2분)
- [ ] 응답 필요: Issue #___, #___
- [ ] 리뷰 필요: PR #___
- [ ] 문서 개선: ___
```

---

## 🔄 3. 피드백 분류 및 우선순위

### 피드백 트리아지 (Triage)

**우선순위 분류**:

#### 🔴 P0: 긴급 (즉시 대응)
- 보안 취약점
- 프로젝트 사용 불가능한 버그
- 데이터 손실 위험

**대응 시간**: 24시간 이내

#### 🟡 P1: 높음 (1주일 이내)
- 주요 기능 버그
- 많은 사용자가 요청하는 기능
- 문서 심각한 오류

**대응 시간**: 1주일 이내

#### 🟢 P2: 중간 (2주일 이내)
- 작은 버그
- 개선 제안
- 문서 개선 요청

**대응 시간**: 2주일 이내

#### ⚪ P3: 낮음 (다음 버전)
- Nice-to-have 기능
- 마이너한 개선
- 향후 검토 필요

**대응 시간**: 다음 메이저 버전

---

### 라벨링 시스템

**GitHub에서 Issue 라벨 생성**:

```bash
# CLI로 라벨 생성
gh label create "priority: P0" --color "d73a4a" --description "긴급"
gh label create "priority: P1" --color "fbca04" --description "높음"
gh label create "priority: P2" --color "0e8a16" --description "중간"
gh label create "priority: P3" --color "d4c5f9" --description "낮음"

gh label create "type: bug" --color "d73a4a" --description "버그"
gh label create "type: feature" --color "a2eeef" --description "새 기능"
gh label create "type: docs" --color "0075ca" --description "문서"
gh label create "type: question" --color "d876e3" --description "질문"

gh label create "status: investigating" --color "fbca04" --description "조사 중"
gh label create "status: planned" --color "0e8a16" --description "계획됨"
gh label create "status: wontfix" --color "ffffff" --description "수정 안함"
```

**라벨 적용**:
```bash
# Issue에 라벨 추가
gh issue edit 123 --add-label "priority: P1,type: bug"
```

---

## 💬 4. 피드백 응답 가이드

### Issue 응답 템플릿

#### 버그 리포트 응답
```markdown
안녕하세요 @username,

버그 리포트 감사합니다! 🐛

**현재 상황 확인**:
- [ ] 재현 가능 여부 확인
- [ ] 영향 범위 파악
- [ ] 우선순위 결정

**예상 일정**:
- 조사 시작: [날짜]
- 수정 목표: [날짜]

**임시 해결책** (있을 경우):
```
[워크어라운드 제시]
```

진행 상황을 계속 업데이트하겠습니다.

감사합니다!
```

#### 기능 요청 응답
```markdown
안녕하세요 @username,

기능 제안 감사합니다! 💡

**검토 내용**:
- Constitution 조항과의 관계: [P1-P13 중]
- 7계층 아키텍처 위치: [Layer 1-7]
- 스타터킷 정체성 부합 여부: [Yes/No]

**P12 트레이드오프 분석**:

**Option A: 추가**
- 장점: ___
- 단점: ___
- ROI: ___

**Option B: 보류**
- 장점: ___
- 단점: ___

**결정**: [추가/보류/다음 버전]

**이유**: ___

피드백에 감사드립니다!
```

#### 질문 응답
```markdown
안녕하세요 @username,

질문 감사합니다! ❓

**답변**:
[상세 답변]

**관련 문서**:
- [문서 링크]

**추가 도움**이 필요하시면 언제든지 말씀해주세요.

감사합니다!
```

---

## 🔧 5. 피드백 반영 프로세스

### Constitution 기반 의사결정 (P11, P12 적용)

#### Step 1: P11 원칙 충돌 검증

**질문**:
- 이 피드백이 과거 원칙과 충돌하나?
- NORTH_STAR.md 정체성과 부합하나?
- "템플릿" vs "완성된 제품" 방향성 확인

**예시**:
```
피드백: "자동 배포 기능 추가해주세요"

P11 검증:
- 과거 원칙: "스타터킷 = 기준 체계 템플릿"
- 충돌: 자동 배포 = 완성된 제품 기능
- 결론: 범위 밖 (튜토리얼만 제공)
```

#### Step 2: P12 트레이드오프 분석

**분석 항목**:
1. Option A vs B 명시
2. 각 옵션 장단점 (객관적 근거)
3. ROI 계산 (가능 시)
4. 추천 + 근거

**템플릿** (`RUNS/observe/feedback_analysis.md`):
```markdown
## Feedback #[번호]: [제목]

### P11 원칙 충돌 검증
- 과거 원칙: ___
- 충돌 여부: Yes/No
- 충돌 내용: ___

### P12 트레이드오프 분석

#### Option A: [반영]
**장점**:
- ___
- ___

**단점**:
- ___
- ___

**ROI**: ___ (시간 절약 예상)

#### Option B: [거절/보류]
**장점**:
- ___
- ___

**단점**:
- ___
- ___

**ROI**: ___

### 결정
- [ ] Option A 선택
- [ ] Option B 선택
- [ ] 다음 리뷰 시 재검토

**이유**: ___
```

#### Step 3: Constitution 수정 필요 시 (P13)

**P13 프로세스**:
1. 새 조항 필요성 검증
2. 타당성 분석 (P12 적용)
3. 기존 조항과 중복 확인
4. 최대 20개 조항 제한 확인
5. 사용자 승인 (나 = 프로젝트 오너)

---

## 🚀 6. 피드백 반영 워크플로우

### 전체 프로세스

```
1. 피드백 수신 (Issue/Discussion/PR)
     ↓
2. 트리아지 (우선순위, 라벨)
     ↓
3. P11 원칙 충돌 검증
     ↓
4. P12 트레이드오프 분석
     ↓
5. 결정 (반영/거절/보류)
     ↓
6. 사용자 응답 (결정 이유 설명)
     ↓
7-a. 반영 시: 개발 → PR → Merge
7-b. 거절 시: Issue 닫기 (이유 설명)
7-c. 보류 시: 다음 리뷰 추가
```

### 개발 워크플로우 (반영 결정 시)

```bash
# 1. 새 브랜치 생성
git checkout -b feature/issue-123-add-xxx

# 2. 개발
# ... 코드 작성 ...

# 3. 테스트
pytest
ruff check

# 4. 커밋 (Conventional Commits)
git commit -m "feat(scope): add xxx feature

Closes #123

- 기능 설명
- P12 분석 결과 반영
- ROI: [시간 절약 예상]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. 푸시
git push origin feature/issue-123-add-xxx

# 6. PR 생성
gh pr create --title "feat: add xxx feature (#123)" \
  --body "Closes #123

## Summary
[기능 설명]

## P12 Analysis
- Option A: 반영 (선택) ✅
- Option B: 거절
- ROI: [계산 결과]

## Checklist
- [x] Constitution 조항 부합 (P[X])
- [x] 7계층 아키텍처 유지
- [x] Tests 추가
- [x] CHANGELOG 업데이트"

# 7. PR 머지 후
git checkout main
git pull
gh issue close 123 --comment "Fixed in #[PR번호]"
```

---

## 📈 7. 피드백 분석 및 보고

### 월간 리포트 템플릿

**파일**: `RUNS/observe/monthly_report_YYYY-MM.md`

```markdown
# Monthly Report - YYYY-MM

## 📊 통계

### GitHub 성장
- Stars: [시작] → [끝] (+[증가])
- Forks: [시작] → [끝] (+[증가])
- Contributors: [수]

### 피드백 활동
- Issues: [생성] / [닫힘] / [열림]
- Discussions: [생성] / [댓글]
- PRs: [생성] / [머지] / [열림]

## 💡 주요 피드백

### Top 3 Feature Requests
1. [제목] - 요청자: @username - 상태: [반영/보류/거절]
2. ...
3. ...

### Top 3 Bugs
1. [제목] - 우선순위: P[X] - 상태: [수정/조사중]
2. ...
3. ...

## 🔄 반영된 개선사항

### v1.X.0 변경사항
- [기능 A] - Issue #[X] - ROI: [계산]
- [버그 수정 B] - Issue #[Y]
- [문서 개선 C] - Issue #[Z]

## 📝 학습 포인트

### P11 적용 사례
- [케이스 1]: [원칙 충돌 감지 내용]
- [케이스 2]: ...

### P12 적용 사례
- [케이스 1]: [트레이드오프 분석 내용]
- [케이스 2]: ...

## 🎯 다음 달 계획
- [ ] [작업 1]
- [ ] [작업 2]
```

---

## 🤝 8. 커뮤니티 참여 유도

### README 배지 추가

```markdown
# Dev Rules Starter Kit

[![GitHub stars](https://img.shields.io/github/stars/positivef/dev-rules-starter-kit?style=social)](https://github.com/positivef/dev-rules-starter-kit/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/positivef/dev-rules-starter-kit?style=social)](https://github.com/positivef/dev-rules-starter-kit/network/members)
[![GitHub issues](https://img.shields.io/github/issues/positivef/dev-rules-starter-kit)](https://github.com/positivef/dev-rules-starter-kit/issues)
[![GitHub license](https://img.shields.io/github/license/positivef/dev-rules-starter-kit)](https://github.com/positivef/dev-rules-starter-kit/blob/main/LICENSE)
```

### 외부 공유 (선택)

**조건**: Stars 10+ 도달 시

**공유 채널**:
1. **Reddit**:
   - r/programming
   - r/coding
   - r/opensource

2. **HackerNews**:
   - Show HN 포스팅

3. **Twitter/X**:
   - 개발 커뮤니티 해시태그

4. **Korean Communities**:
   - 개발자 커뮤니티
   - Slack/Discord 채널

---

## 📋 체크리스트: 피드백 시스템 설정

### 즉시 설정 (10분)
- [ ] GitHub Discussions 활성화
- [ ] Issue 라벨 생성
- [ ] RUNS/observe/ 디렉토리 생성
- [ ] weekly_checklist.md 템플릿 생성

### 필요 시 설정 (30분)
- [ ] Issue 템플릿 생성 (.github/ISSUE_TEMPLATE/)
- [ ] PR 템플릿 생성 (.github/PULL_REQUEST_TEMPLATE.md)
- [ ] CONTRIBUTING.md 작성

---

## 💡 핵심 원칙

1. **신속한 응답**: 24-48시간 내 첫 응답
2. **정중한 태도**: 모든 피드백에 감사 표현
3. **투명한 결정**: P11/P12로 이유 설명
4. **Constitution 준수**: 모든 결정은 헌법 기반
5. **증거 기반**: 추측 아닌 데이터로 판단

---

**버전**: 1.0.0
**작성일**: 2025-10-24
**업데이트**: Release & Observe 기간 중
