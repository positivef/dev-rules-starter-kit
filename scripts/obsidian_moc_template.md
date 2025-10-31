# 개발일지 Map of Contents

> 자동 생성 MOC - 파일을 추가하면 자동으로 업데이트됩니다
>
> **마지막 업데이트**: {last_update}

---

## 📊 통계 대시보드

```dataview
TABLE WITHOUT ID
  "총 작업" AS "항목",
  length(rows) AS "개수"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
GROUP BY true
```

```dataview
TABLE WITHOUT ID
  type AS "유형",
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 라인 추가",
  sum(rows.files_changed) AS "파일 변경"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
GROUP BY type
SORT length(rows) DESC
```

---

## 📅 최근 30일 작업 (날짜별)

```dataview
TABLE
  file.link AS "작업",
  type AS "유형",
  time AS "시간",
  files_changed AS "파일",
  lines_added AS "라인 추가"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
  AND date >= date(today) - dur(30 days)
SORT date DESC, time DESC
LIMIT 30
```

---

## 🔥 진행 중인 프로젝트

```dataview
TABLE
  file.link AS "작업",
  project AS "프로젝트",
  phase AS "Phase",
  date AS "날짜"
FROM "개발일지"
WHERE contains(status, "in-progress")
  AND file.folder != "개발일지/_backup_old_structure"
GROUP BY project
SORT date DESC
```

---

## 📂 프로젝트별 작업 현황

```dataview
TABLE
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 라인",
  sum(rows.files_changed) AS "파일 수",
  min(rows.date) AS "시작일",
  max(rows.date) AS "최근 작업"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
  AND project != null
GROUP BY project
SORT max(rows.date) DESC
```

---

## 🏷️ 태그별 작업 분포

```dataview
TABLE
  length(rows) AS "작업 수",
  sum(rows.lines_added) AS "코드 라인",
  list(rows.file.link) AS "관련 작업"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
FLATTEN tags AS tag
GROUP BY tag
SORT length(rows) DESC
LIMIT 20
```

---

## 📈 이번 주 활동 (주간 요약)

```dataview
TABLE WITHOUT ID
  date AS "날짜",
  length(rows) AS "커밋 수",
  sum(rows.lines_added) AS "코드 추가",
  sum(rows.lines_deleted) AS "코드 삭제",
  sum(rows.files_changed) AS "파일 변경"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
  AND date >= date(today) - dur(7 days)
GROUP BY date
SORT date DESC
```

---

## 🔍 도메인별 작업 (Testing, Obsidian, Scripts, etc.)

```dataview
LIST
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
  AND contains(tags, "domain/")
FLATTEN tags AS domain_tag
WHERE contains(domain_tag, "domain/")
GROUP BY domain_tag
SORT length(rows) DESC
```

---

## 📝 최근 업데이트 (Last 10)

```dataview
TABLE
  file.link AS "파일",
  project AS "프로젝트",
  type AS "유형",
  date AS "날짜",
  time AS "시간"
FROM "개발일지"
WHERE file.folder != "개발일지/_backup_old_structure"
SORT date DESC, time DESC
LIMIT 10
```

---

## 💡 사용 팁

### Dataview 쿼리 커스터마이징

이 MOC는 Dataview 플러그인을 사용하여 자동으로 업데이트됩니다.

**쿼리 수정 예시**:
- 날짜 범위 조정: `dur(30 days)` → `dur(7 days)` 또는 `dur(90 days)`
- 결과 개수 제한: `LIMIT 30` → `LIMIT 50`
- 특정 태그 필터: `WHERE contains(tags, "project/q1-2026")`
- 특정 프로젝트: `WHERE project = "Q1 Test Infrastructure"`

### 추가 플러그인 권장

1. **Dataview** (필수) - 자동 쿼리 실행
2. **Charts** - 그래프/차트 시각화
3. **Tracker** - 활동 히트맵 (GitHub style)
4. **Calendar** - 달력 뷰
5. **Tag Wrangler** - 태그 관리

---

**생성일**: {creation_date}
**자동 생성**: dev-rules-starter-kit/scripts/auto_sync_obsidian.py
