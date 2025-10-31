# Obsidian Dataview Integration Guide

## 개요

dev-rules-starter-kit의 Obsidian 통합은 Dataview 플러그인을 활용하여 자동화된 개발일지 관리를 제공합니다.

## 주요 기능

### 1. YAML Frontmatter 자동 생성

모든 Git 커밋 시 자동으로 YAML frontmatter가 생성됩니다:

```yaml
---
date: 2025-10-31
time: "23:49"
project: "Feature Name"
topic: "Feature-Name"
commit: "22fed781"
type: feature
phase: 1
status: completed
tags: [type/feat, domain/testing, project/q1-2026, status/completed]
files_changed: 3
lines_added: 150
lines_deleted: 20
---
```

### 2. Dataview 자동 MOC

개발일지-MOC.md는 10개 이상의 Dataview 쿼리를 포함합니다:

- **통계 대시보드**: 전체 작업 현황
- **최근 30일 작업**: 날짜별 정렬
- **진행 중인 프로젝트**: in-progress 상태 추적
- **프로젝트별 현황**: 코드 라인, 파일 수 통계
- **태그별 분포**: 작업 유형 분석
- **주간 활동**: 최근 7일 요약
- **도메인별 작업**: testing, obsidian, scripts 등

### 3. 계층적 태그 시스템

```
type/
  - feature, fix, test, docs, refactor, chore
domain/
  - testing, documentation, scripts, config, obsidian
project/
  - q1-2026, strategy-b
status/
  - completed, in-progress, blocked
```

## 설치 방법

### 1. Obsidian Dataview 플러그인 설치

1. Obsidian 열기
2. Settings (⚙️) → Community plugins
3. Browse 클릭
4. "Dataview" 검색
5. Install → Enable

### 2. 추가 플러그인 (선택사항)

- **Charts**: 그래프/차트 시각화
- **Tracker**: GitHub-style 히트맵
- **Calendar**: 달력 뷰
- **Tag Wrangler**: 태그 관리

## 사용 방법

### 기본 사용

1. 코드 작업
2. Git 커밋
3. 자동으로 개발일지 생성 + YAML frontmatter 추가
4. Obsidian에서 MOC 열기 → Dataview 쿼리 자동 실행

### 커스텀 쿼리 예시

#### 특정 프로젝트 작업 조회

```dataview
TABLE date, type, files_changed, lines_added
FROM "개발일지"
WHERE contains(tags, "project/q1-2026")
SORT date DESC
```

#### 이번 주 테스트 작업

```dataview
LIST
FROM "개발일지"
WHERE contains(tags, "domain/testing")
  AND date >= date(today) - dur(7 days)
SORT date DESC
```

#### 월별 코드 통계

```dataview
TABLE
  sum(rows.lines_added) AS "코드 추가",
  sum(rows.files_changed) AS "파일 변경"
FROM "개발일지"
GROUP BY dateformat(date, "yyyy-MM")
SORT date DESC
```

## 시각화 활용

### Graph View 설정

1. Settings → Graph View → Groups
2. 태그별 색상 설정:
   - `tag:#project/q1-2026` → 파란색
   - `tag:#domain/testing` → 초록색
   - `tag:#type/feature` → 보라색

### Charts 플러그인

```chart
type: bar
labels: [Q1, Q2, Q3, Q4]
series:
  - title: 코드 라인
    data: [1200, 1500, 1800, 2000]
```

### Tracker 플러그인

```tracker
searchType: tag
searchTarget: daily-commit
folder: 개발일지
month:
    startWeekOn: Monday
    threshold: 1
    color: green
```

## 문제 해결

### Dataview 쿼리가 실행되지 않음

- Dataview 플러그인 활성화 확인
- Settings → Dataview → Enable JavaScript Queries 체크
- 쿼리 문법 검증 (공식 문서 참조)

### YAML frontmatter 생성 안됨

- `.env` 파일에 `OBSIDIAN_VAULT_PATH` 설정 확인
- Git hook 설치 확인: `python scripts/install_obsidian_auto_sync.py --check`
- 커밋 메시지가 트리거 조건 충족하는지 확인 (feat:, fix:, test: 등)

### MOC가 템플릿으로 생성되지 않음

- 기존 MOC 백업 후 삭제
- 테스트 커밋 실행
- `scripts/obsidian_moc_template.md` 파일 존재 확인

## 참고 자료

- [Dataview 공식 문서](https://blacksmithgu.github.io/obsidian-dataview/)
- [Obsidian 커뮤니티 플러그인](https://obsidian.md/plugins)
- [OBSIDIAN_SYNC_RULES.md](../OBSIDIAN_SYNC_RULES.md)
- [auto_sync_obsidian.py](../scripts/auto_sync_obsidian.py)

---

**생성일**: 2025-10-31
**작성자**: dev-rules-starter-kit
**버전**: 1.0.0
