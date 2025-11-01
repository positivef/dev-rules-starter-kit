# Obsidian 구조 최적화 비교

**분석 일자**: 2025-11-01
**목적**: Dataview 기반 시스템에 최적화된 구조 도출

---

## 🔍 구조 옵션 비교

### Option A: 숫자 Prefix 방식 (원래 제안)

```
01-Daily/
02-DevLogs/
03-Projects/
04-MOCs/
05-Knowledge/
06-Templates/
07-Resources/
08-System/
_archive/
```

**장점**:
- ✅ 명확한 순서 (01, 02, 03...)
- ✅ 파일 탐색기에서 정렬 일관성
- ✅ 전통적인 폴더 구조 (직관적)

**단점**:
- ❌ 폴더 깊이 증가 → Dataview 쿼리 복잡
- ❌ 숫자가 의미 없음 (01이 왜 Daily인지 불명확)
- ❌ Zettelkasten 철학과 충돌 (우리가 구현한 시스템)
- ❌ Graph View에서 폴더 구조가 방해
- ❌ 폴더 이동 시 번호 재할당 필요

**Dataview 쿼리 예시**:
```dataview
FROM "02-DevLogs/2025-11"  # 경로 복잡
WHERE contains(tags, "domain/testing")
```

---

### Option B: PARA + Zettelkasten 하이브리드 ⭐ **추천**

```
📁 Vault Root/
│
├── Daily/                    # 일일 노트 (날짜 폴더)
│   ├── 2025-10/
│   └── 2025-11/
│
├── Projects/                 # 프로젝트 (각 프로젝트 = 1폴더)
│   ├── DevRules/
│   │   ├── _MOC-DevRules.md
│   │   ├── Architecture/
│   │   └── Planning/
│   │
│   └── DoubleDiver/
│       └── _MOC-DoubleDiver.md
│
├── Resources/                # 재사용 가능한 자산
│   ├── Templates/
│   ├── Guides/
│   └── Diagrams/
│
├── _System/                  # 시스템 설정 (숨김)
│   ├── Config/
│   ├── Tasks/
│   └── Handoffs/
│
├── _Archive/                 # 아카이브 (숨김)
│
├── Index.md                  # 메인 인덱스
├── DevLog-MOC.md            # 개발일지 MOC (폴더 없음!)
└── Knowledge-MOC.md         # 지식 MOC (폴더 없음!)
```

**핵심 차이점**:
1. **개발일지는 폴더 없이 Dataview로 관리**
2. **MOC는 루트에 위치** (빠른 접근)
3. **Knowledge는 태그로 관리** (폴더 불필요)
4. **숫자 prefix 제거** (의미 있는 이름만)

**장점**:
- ✅ Zettelkasten 철학 유지 (링크 > 폴더)
- ✅ Dataview 쿼리 단순화
- ✅ Graph View 최적화
- ✅ 폴더 깊이 최소화 (2-depth 이내)
- ✅ 빠른 검색 (경로 짧음)
- ✅ 확장 용이 (새 프로젝트 = 새 폴더만)

**Dataview 쿼리 예시**:
```dataview
FROM ""  # 전체에서 검색
WHERE date >= date(today) - dur(7 days)
  AND contains(tags, "type/feature")
SORT date DESC
```
→ 폴더 구조와 무관하게 YAML 태그로 필터링!

---

### Option C: Flat Structure (극단적 Zettelkasten)

```
📁 Vault Root/
├── Index.md
├── 2025-10-20-DevLog-Phase1.md
├── 2025-10-21-DevLog-Phase2.md
├── DevRules-MOC.md
├── DoubleDiver-MOC.md
└── _Archive/
```

**장점**:
- ✅ 최대한 단순
- ✅ Dataview가 모든 조직화 담당
- ✅ Graph View 최적

**단점**:
- ❌ 파일 수 많아지면 탐색 어려움
- ❌ 프로젝트별 격리 불가능
- ❌ 협업 시 혼란
- ❌ 너무 극단적

---

## 🎯 최종 추천: Option B (PARA + Zettelkasten)

### 이유

#### 1. 우리 시스템과 완벽한 호환
```yaml
# 이미 구축된 YAML frontmatter
date: 2025-11-01
tags: [type/feature, domain/testing, project/q1-2026]
```
→ 폴더 대신 **태그가 분류 기준**

#### 2. Dataview 쿼리 최적화
```dataview
# 폴더 구조 무시하고 조건으로만 필터링
TABLE date, project, type
FROM ""
WHERE contains(tags, "domain/testing")
  AND date >= date(today) - dur(30 days)
SORT date DESC
```
→ 폴더 깊이와 무관

#### 3. MOC가 실제 네비게이션
```markdown
# DevLog-MOC.md (루트에 위치)

## 최근 7일
\`\`\`dataview
FROM "" WHERE date >= date(today) - dur(7 days)
\`\`\`

## 프로젝트별
\`\`\`dataview
GROUP BY project
\`\`\`

## 도메인별
\`\`\`dataview
GROUP BY tags
\`\`\`
```
→ MOC = 가상 폴더

#### 4. Graph View 최적화
- 폴더 구조가 단순 → 그래프 깔끔
- 링크 중심 연결 강조
- 태그 노드로 자동 클러스터링

---

## 📊 구조별 비교표

| 특성 | Option A (숫자) | Option B (PARA+Zettel) ⭐ | Option C (Flat) |
|------|----------------|--------------------------|-----------------|
| 폴더 깊이 | 3-4 depth | 2-3 depth | 1 depth |
| Dataview 효율 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 파일 탐색 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Graph View | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 초보자 친화성 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 확장성 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Zettelkasten | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 협업 편의성 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 🔄 Option B 상세 구조

### 최종 권장 구조

```
Obsidian Vault/
│
├── 📅 Daily/                         # 일일 노트만
│   ├── 2025-09/
│   ├── 2025-10/
│   │   ├── 2025-10-07.md
│   │   ├── 2025-10-24.md
│   │   └── 2025-10-31.md
│   └── 2025-11/
│
├── 🚀 Projects/                      # 프로젝트 (격리)
│   │
│   ├── DevRules/
│   │   ├── _MOC-DevRules.md         # 프로젝트 MOC
│   │   ├── Architecture/
│   │   │   └── system-design.md
│   │   ├── Planning/
│   │   │   ├── Phase-C-Week-2.md
│   │   │   └── Phase-D-Progress.md
│   │   ├── Reviews/
│   │   │   └── session-summaries/
│   │   └── Development/
│   │       └── guides/
│   │
│   └── DoubleDiver/
│       ├── _MOC-DoubleDiver.md
│       ├── Specifications/
│       ├── Development/
│       └── Learning/
│
├── 📚 Resources/                     # 재사용 가능한 자산
│   ├── Templates/
│   │   ├── daily-note.md
│   │   ├── devlog.md
│   │   ├── error-solution.md
│   │   └── weekly-review.md
│   │
│   ├── Guides/
│   │   ├── Obsidian-MCP-Guide.md
│   │   ├── Obsidian-Dev-Setup.md
│   │   └── ObsidianBridge.md
│   │
│   └── Diagrams/
│       └── *.excalidraw
│
├── ⚙️ _System/                       # 시스템 (숨김)
│   ├── Config/
│   ├── Tasks/
│   │   ├── FEAT-2025-09-26-01.md
│   │   └── INTEGRATION-2025-10-28.md
│   ├── Handoffs/
│   └── Prompts/
│       ├── architect_role.md
│       └── planner_role.md
│
├── 🗄️ _Archive/                      # 아카이브 (숨김)
│   ├── 2024-old/
│   ├── deprecated/
│   └── migration-20251101/
│
├── 📌 Index.md                       # 메인 대시보드
├── 📝 DevLog-MOC.md                  # 개발일지 MOC (루트!)
├── 🗺️ Knowledge-MOC.md               # 지식 MOC (루트!)
└── 🎓 Universal-Development-Guide.md # 마스터 가이드

# 개발일지는 어디에? → 어디든 가능! (YAML로 찾음)
# Projects/DevRules/DevLog-Phase3.md
# Daily/2025-11/devlog-obsidian.md
# 루트/DevLog-Quick-Fix.md
# → 모두 DevLog-MOC.md의 Dataview로 자동 집계
```

### 핵심 개념: "물리적 위치 < 논리적 분류"

**개발일지 예시**:
```yaml
---
date: 2025-11-01
tags: [type/feature, domain/testing, project/q1-2026]
project: "Q1 Test Infrastructure"
---
```

**DevLog-MOC.md**에서:
```dataview
# 파일이 어디에 있든 상관없이 태그로 찾음
FROM ""
WHERE contains(tags, "type/feature")
SORT date DESC
```

---

## 🎯 Option B의 특별한 장점

### 1. 프로젝트 격리
```
Projects/DevRules/         # DevRules 관련 모든 것
Projects/DoubleDiver/      # DoubleDiver 관련 모든 것
```
→ Git 서브모듈, 협업 시 프로젝트 단위 공유 가능

### 2. 개발일지 유연성
```
# 어디에 저장하든 DevLog-MOC가 자동 집계
Projects/DevRules/devlog-phase3.md    ✅
Daily/2025-11-01.md 안에 개발일지     ✅
루트/urgent-fix-log.md                ✅
```

### 3. MOC = 네비게이션
```
Index.md → 전체 대시보드
DevLog-MOC.md → 개발일지 허브
Knowledge-MOC.md → 학습 허브
Projects/DevRules/_MOC-DevRules.md → 프로젝트 허브
```

### 4. 검색 최적화
```
# 짧은 경로 = 빠른 검색
Resources/Templates/daily.md  (OK)
vs
01-Daily/02-Templates/03-Standard/daily.md  (너무 김)
```

---

## 🔄 마이그레이션 차이점

### Option A → Option B 변경사항

**제거되는 것**:
- ❌ 숫자 prefix (01-, 02-, ...)
- ❌ 독립적인 DevLogs/ 폴더
- ❌ 독립적인 Knowledge/ 폴더
- ❌ 독립적인 MOCs/ 폴더

**추가/변경**:
- ✅ MOC를 루트로 이동 (빠른 접근)
- ✅ 개발일지를 논리적으로만 관리 (Dataview)
- ✅ Knowledge는 태그로 분류 (폴더 불필요)
- ✅ _System, _Archive로 숨김 처리

---

## 📋 최종 비교: A vs B

### 파일 찾기 시나리오

**시나리오**: "Q1 2026 Phase 3 테스트 작업 찾기"

**Option A (숫자 폴더)**:
```
1. 02-DevLogs/ 열기
2. 날짜 폴더 찾기 (2025-10-25?)
3. 파일명에서 Phase 3 찾기
```

**Option B (Dataview)**:
```
1. DevLog-MOC.md 열기
2. Dataview 쿼리가 자동 표시:
   \`\`\`dataview
   WHERE contains(tags, "project/q1-2026")
     AND phase = 3
   \`\`\`
3. 클릭 한 번에 접근
```

---

## ✅ 최종 권장: Option B

**이유**:
1. ✅ Dataview 시스템과 완벽한 시너지
2. ✅ YAML frontmatter 활용 극대화
3. ✅ Zettelkasten 철학 유지
4. ✅ Graph View 최적화
5. ✅ 확장성과 유연성
6. ✅ 초보자도 이해 가능한 단순성

**Option A는 언제 좋을까?**:
- Dataview 없이 폴더만 사용
- 전통적인 파일 시스템 선호
- 숫자 순서가 중요한 경우

**우리는 이미 Dataview를 구축했으므로 → Option B가 최적입니다!**
