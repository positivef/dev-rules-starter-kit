# Obsidian Dataview 실전 활용 가이드

## 📚 목차

1. [기본 활용법](#기본-활용법)
2. [일일 루틴](#일일-루틴)
3. [주간 리뷰](#주간-리뷰)
4. [프로젝트 추적](#프로젝트-추적)
5. [고급 활용법](#고급-활용법)
6. [실전 시나리오](#실전-시나리오)

---

## 기본 활용법

### 자동화된 워크플로우

```
코딩 → 커밋 → 자동 동기화 → Obsidian에서 확인
```

**매일 하는 일**:
1. 평소처럼 코딩
2. `git commit -m "feat: 기능 추가"`
3. 끝! (나머지는 자동)

**자동으로 생성되는 것**:
- ✅ 개발일지 파일 (날짜 폴더 안에)
- ✅ YAML frontmatter (메타데이터)
- ✅ MOC 링크 추가
- ✅ Git 통계 (파일 수, 라인 수)

---

## 일일 루틴

### 🌅 아침 - 오늘 할 일 확인

**1. 개발일지-MOC.md 열기**

```dataview
// 최근 3일 작업 확인
TABLE date, project, type, files_changed
FROM "개발일지"
WHERE date >= date(today) - dur(3 days)
SORT date DESC
```

**활용법**:
- 어제 무엇을 했는지 빠르게 회상
- 오늘 이어서 할 작업 파악
- 진행 중인 프로젝트 상태 체크

---

### 🌆 저녁 - 오늘 한 일 정리

**1. 오늘 커밋한 작업 확인**

Obsidian에서 `개발일지/YYYY-MM-DD/` 폴더 열기

**2. 회고 작성** (5분)

각 파일 하단의 템플릿 채우기:

```markdown
## [TIP] 배운 점 & 인사이트

### 성공 사례
- 오늘 잘 된 점
- 효과적이었던 접근법

### 개선 필요 영역
- 어려웠던 부분
- 다음에 다르게 할 점

## 🔧 시행착오 및 해결

- 문제: [무엇이 문제였나?]
- 시도: [어떻게 해결하려 했나?]
- 해결: [최종 해결 방법]
- 교훈: [배운 점]
```

**3. 다음 단계 업데이트**

```markdown
## 📋 다음 단계

### 즉시 수행
- [ ] 코드 리뷰 반영
- [ ] 테스트 추가

### 단기 (1-2일)
- [ ] 성능 최적화
- [ ] 문서 업데이트

### 장기 (1주일+)
- [ ] 리팩토링 계획
```

---

## 주간 리뷰

### 📊 금요일 오후 - 주간 회고 (30분)

**1. 주간 통계 확인**

MOC에서 자동 쿼리 실행:

```dataview
// 이번 주 작업 요약
TABLE WITHOUT ID
  date AS "날짜",
  length(rows) AS "커밋 수",
  sum(rows.lines_added) AS "코드 추가",
  sum(rows.files_changed) AS "파일 변경"
FROM "개발일지"
WHERE date >= date(today) - dur(7 days)
GROUP BY date
SORT date DESC
```

**분석 포인트**:
- 📈 생산성 추이 (어느 날 가장 많이 작업했나?)
- 🎯 프로젝트 진행도 (목표 대비 진척도)
- ⚖️ 균형 (feature vs fix vs refactor 비율)

**2. 프로젝트별 현황**

```dataview
// 프로젝트별 이번 주 작업
TABLE
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 라인",
  list(rows.file.link) AS "작업 목록"
FROM "개발일지"
WHERE date >= date(today) - dur(7 days)
GROUP BY project
SORT length(rows) DESC
```

**질문**:
- ✅ 완료한 프로젝트는?
- 🔄 진행 중인 프로젝트는?
- 🚨 블로킹 이슈는?

**3. 주간 회고 노트 작성**

새 파일 생성: `개발일지/Weekly-Review-YYYY-WXX.md`

```markdown
# 주간 회고 - 2025년 11월 1주차

## 📊 주간 통계
- 총 커밋: 25개
- 코드 추가: 2,450 라인
- 파일 변경: 87개

## 🎯 목표 달성도
- [x] Q1 테스트 인프라 Phase 3 완료
- [x] Obsidian Dataview 통합
- [ ] 문서화 완료 (80%)

## 💡 배운 점
1. Dataview 쿼리 문법 숙달
2. YAML frontmatter 활용법
3. ...

## 🔄 다음 주 계획
1. Phase 4 unit test 시작
2. 성능 최적화
3. ...
```

---

## 프로젝트 추적

### 🎯 프로젝트 대시보드 만들기

**예시: Q1 2026 테스트 인프라**

새 파일: `개발일지/Project-Q1-Test-Infrastructure.md`

```markdown
# Q1 2026 Test Infrastructure Project

> 프로젝트 대시보드 - Dataview 자동 업데이트

## 📊 프로젝트 현황

\`\`\`dataview
TABLE
  date AS "날짜",
  type AS "유형",
  phase AS "Phase",
  files_changed AS "파일",
  lines_added AS "라인"
FROM "개발일지"
WHERE contains(tags, "project/q1-2026")
SORT date DESC
\`\`\`

## 📈 진행도

\`\`\`dataview
TABLE WITHOUT ID
  phase AS "Phase",
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 라인",
  min(rows.date) AS "시작일",
  max(rows.date) AS "최근 작업"
FROM "개발일지"
WHERE contains(tags, "project/q1-2026")
GROUP BY phase
SORT phase
\`\`\`

## 🎯 목표

- [x] Phase 1: 기본 테스트 (29 tests)
- [x] Phase 2: 고급 테스트 (22 tests)
- [x] Phase 3: 성능 최적화 (2.3x speedup)
- [ ] Phase 4: Unit test 프레임워크
- [ ] Phase 5: 15% coverage 달성

## 📝 관련 작업

\`\`\`dataview
LIST
FROM "개발일지"
WHERE contains(tags, "project/q1-2026")
SORT date DESC
\`\`\`
```

**활용법**:
- 프로젝트 진행상황 한눈에 파악
- Phase별 작업량 추적
- 관련 모든 작업 빠르게 찾기

---

## 고급 활용법

### 1. 커스텀 태그 전략

**계층적 태그 설계**:

```
type/          → 작업 유형
  - feature    → 새 기능
  - fix        → 버그 수정
  - refactor   → 리팩토링
  - docs       → 문서화
  - test       → 테스트

domain/        → 기술 도메인
  - frontend   → 프론트엔드
  - backend    → 백엔드
  - testing    → 테스트
  - infra      → 인프라

project/       → 프로젝트명
  - q1-2026    → Q1 2026 프로젝트
  - strategy-b → Strategy B

priority/      → 우선순위
  - high       → 높음
  - medium     → 중간
  - low        → 낮음

status/        → 상태
  - completed  → 완료
  - in-progress → 진행중
  - blocked    → 블로킹
```

**활용 예시**:

```dataview
// 높은 우선순위의 미완료 백엔드 작업
TABLE date, project, summary
FROM "개발일지"
WHERE contains(tags, "priority/high")
  AND contains(tags, "domain/backend")
  AND contains(tags, "status/in-progress")
SORT date DESC
```

### 2. 시각화 대시보드

**월간 생산성 차트**

새 파일: `개발일지/Dashboard-Monthly.md`

```markdown
# 월간 개발 대시보드

## 📊 일별 커밋 수

\`\`\`dataview
TABLE WITHOUT ID
  dateformat(date, "MM-dd") AS "날짜",
  length(rows) AS "커밋"
FROM "개발일지"
WHERE date >= date(today) - dur(30 days)
GROUP BY date
SORT date DESC
\`\`\`

## 📈 프로젝트별 코드 라인

\`\`\`dataview
TABLE WITHOUT ID
  project AS "프로젝트",
  sum(rows.lines_added) AS "추가",
  sum(rows.lines_deleted) AS "삭제",
  (sum(rows.lines_added) - sum(rows.lines_deleted)) AS "순증가"
FROM "개발일지"
WHERE date >= date(today) - dur(30 days)
GROUP BY project
SORT sum(rows.lines_added) DESC
\`\`\`

## 🏷️ 작업 유형 분포

\`\`\`dataview
TABLE WITHOUT ID
  type AS "유형",
  length(rows) AS "개수",
  round(length(rows) / 100 * 100, 1) + "%" AS "비율"
FROM "개발일지"
WHERE date >= date(today) - dur(30 days)
GROUP BY type
SORT length(rows) DESC
\`\`\`
```

### 3. 지식 연결 - Zettelkasten

**관련 작업 자동 링크**

```markdown
# 성능 최적화 학습 노트

## 관련 작업

\`\`\`dataview
LIST
FROM "개발일지"
WHERE contains(tags, "performance") OR contains(file.name, "performance")
SORT date DESC
\`\`\`

## 학습 내용

- Parallel execution: pytest-xdist
- 2.3x speedup 달성
- ...
```

---

## 실전 시나리오

### 시나리오 1: 버그 추적

**문제**: 며칠 전에 수정한 인증 버그, 어떻게 고쳤더라?

**해결**:

1. MOC에서 검색:
```dataview
LIST
FROM "개발일지"
WHERE contains(tags, "type/fix")
  AND contains(file.name, "auth")
SORT date DESC
```

2. 파일 열어서 "시행착오 및 해결" 섹션 확인
3. 해결 방법 재확인 → 유사한 버그에 적용

---

### 시나리오 2: 월말 보고

**필요**: 이번 달 작업 요약 리포트

**해결**:

```dataview
// 이번 달 전체 통계
TABLE WITHOUT ID
  "항목" AS "구분",
  "값" AS "통계"
WHERE false
LIMIT 0

TABLE WITHOUT ID
  "총 커밋 수" AS "항목",
  length(rows) AS "값"
FROM "개발일지"
WHERE date >= date(today) - dur(30 days)
GROUP BY true

TABLE WITHOUT ID
  "코드 추가" AS "항목",
  sum(rows.lines_added) AS "값"
FROM "개발일지"
WHERE date >= date(today) - dur(30 days)
GROUP BY true
```

→ 자동으로 숫자 집계, 리포트 작성 시간 90% 단축!

---

### 시나리오 3: 새 팀원 온보딩

**필요**: 프로젝트 히스토리 빠르게 공유

**해결**:

1. 프로젝트 대시보드 공유
2. MOC에서 주요 마일스톤 필터:

```dataview
LIST
FROM "개발일지"
WHERE contains(tags, "milestone") OR contains(tags, "release")
SORT date DESC
```

3. 각 마일스톤 파일 읽으면서 컨텍스트 파악

---

### 시나리오 4: 성과 평가 준비

**필요**: 분기별 성과 정리

**해결**:

```dataview
// Q1 2026 프로젝트 성과
TABLE
  project AS "프로젝트",
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 기여",
  min(rows.date) AS "시작일",
  max(rows.date) AS "완료일"
FROM "개발일지"
WHERE date >= date("2026-01-01") AND date < date("2026-04-01")
GROUP BY project
SORT sum(rows.lines_added) DESC
```

→ 구체적인 숫자로 성과 증명!

---

## 💡 Pro Tips

### Tip 1: 스마트 검색

**태그 조합으로 정확한 검색**:
```dataview
// 높은 우선순위 + 테스트 + 진행중
FROM "개발일지"
WHERE contains(tags, "priority/high")
  AND contains(tags, "domain/testing")
  AND contains(tags, "status/in-progress")
```

### Tip 2: 템플릿 활용

**자주 쓰는 쿼리를 템플릿으로 저장**:

`개발일지/Templates/Query-Recent-Work.md`
```dataview
TABLE date, project, type, files_changed
FROM "개발일지"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

→ 다른 노트에서 `![[Query-Recent-Work]]`로 임베드

### Tip 3: 모바일 활용

**간단한 쿼리만 사용**:
```dataview
// PC에서는 복잡한 쿼리 OK
// 모바일에서는 이런 간단한 쿼리만
LIST
FROM "개발일지"
WHERE date = date(today)
```

### Tip 4: 정기 리뷰 습관

- **매일 저녁**: 5분 회고
- **주 1회 (금요일)**: 30분 주간 리뷰
- **월 1회 (말일)**: 1시간 월간 리뷰
- **분기 1회**: 2시간 분기 회고

---

## 🎯 추천 워크플로우

### 초급 (첫 1주)
1. 평소처럼 커밋만 하기
2. 저녁에 개발일지 확인
3. 간단한 회고만 추가

### 중급 (1개월 후)
1. 주간 리뷰 시작
2. 프로젝트 대시보드 만들기
3. 커스텀 쿼리 2-3개 작성

### 고급 (3개월 후)
1. 월간 대시보드 운영
2. 태그 전략 세분화
3. Zettelkasten 스타일 지식 연결
4. 자동화 추가 (Charts, Tracker 플러그인)

---

## 📚 참고 자료

- [OBSIDIAN_DATAVIEW_GUIDE.md](OBSIDIAN_DATAVIEW_GUIDE.md) - 기술 가이드
- [OBSIDIAN_QUICK_START.md](OBSIDIAN_QUICK_START.md) - 5분 시작 가이드
- [Dataview 공식 문서](https://blacksmithgu.github.io/obsidian-dataview/)

---

**최종 업데이트**: 2025-11-01
**작성**: dev-rules-starter-kit
