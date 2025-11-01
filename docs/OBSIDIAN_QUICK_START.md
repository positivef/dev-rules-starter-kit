# Obsidian Integration Quick Start

## 5분 빠른 시작

### 1. Dataview 플러그인 설치

1. Obsidian 열기
2. `Settings` (⚙️) → `Community plugins`
3. `Turn on community plugins` (처음이면)
4. `Browse` 클릭
5. "Dataview" 검색
6. `Install` → `Enable`

### 2. 첫 커밋 테스트

```bash
# 간단한 변경 후 커밋
git add .
git commit -m "test: Dataview integration test"
```

### 3. 결과 확인

Obsidian에서 다음 파일들 확인:

**개발일지 파일**: `개발일지/YYYY-MM-DD/작업명.md`
```yaml
---
date: 2025-11-01
time: "12:34"
project: "Test Project"
tags: [type/test, domain/testing]
---
```

**MOC 파일**: `개발일지/개발일지-MOC.md`
- Dataview 쿼리가 자동으로 실행됨
- 통계, 최근 작업, 프로젝트 현황 등 표시

## 문제 해결

### Dataview 쿼리가 보이지 않음?
→ Dataview 플러그인 활성화 확인

### YAML이 생성되지 않음?
→ `.env` 파일에 `OBSIDIAN_VAULT_PATH` 확인

### 더 자세한 가이드
→ [OBSIDIAN_DATAVIEW_GUIDE.md](OBSIDIAN_DATAVIEW_GUIDE.md)
