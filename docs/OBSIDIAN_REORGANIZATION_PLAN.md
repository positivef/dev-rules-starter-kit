# Obsidian Vault 재정리 계획

**분석 일자**: 2025-11-01
**현재 상태**: 중복 폴더, 산재된 파일, 일관성 없는 구조
**목표**: 체계적이고 확장 가능한 구조 구축

---

## 📊 현재 문제점 분석

### 🔴 Critical Issues (즉시 해결 필요)

#### 1. 개발일지 폴더 중복 (5곳!)
```
❌ 개발일지/                    # 새 Dataview 시스템 (유지)
❌ DevLogs/                     # 옛날 방식 (통합 필요)
❌ Dev Rules Project/개발일지/  # 중복 (통합 필요)
❌ Dev Rules Project/개발 일지/ # 공백 포함 (통합 필요)
❌ Dev Rules Project/Work Logs/ # 작업 로그 (통합 필요)
```
→ **문제**: 어디에 저장해야 할지 혼란, 검색 어려움

#### 2. Daily Notes 중복
```
❌ Daily Notes/  # 2개 파일
❌ daily/        # 1개 파일
```
→ **문제**: 일일 노트 위치 불명확

#### 3. 프로젝트 폴더 중복
```
❌ DoubleDiver 개발 프로젝트/
❌ DoubleDiver/
❌ Projects/DoubleDiver/
```
→ **문제**: 프로젝트 자료 분산

#### 4. 임시 파일 방치
```
❌ Untitled 1.base ~ Untitled 5.base
❌ Untitled.base
❌ Untitled.canvas
```
→ **문제**: Vault 정리 안 됨

#### 5. 루트 레벨 파일 산재
```
❌ 2025-10-07.md
❌ 2025-10-31.md
❌ Welcome.md
❌ Index.md
❌ 프로젝트 체계적이고 높은 퍼포먼스 서비스,제품개발을 위한 이론 아웃라인 정립.md
❌ 해결해야할일.md
```
→ **문제**: 중요 파일 찾기 어려움

### 🟡 Important Issues (개선 필요)

#### 6. MOC 파일 중복
```
⚠️ MOCs/DevRules_개발_지식맵.md
⚠️ MOCs/dev-rules-starter-kit_MOC.md
⚠️ MOCs/DevRules_Project_MOC.md
⚠️ 개발일지/개발일지-MOC.md
```
→ **문제**: 어떤 MOC가 최신인지 불명확

#### 7. 일관성 없는 네이밍
```
⚠️ DoubleDiver_개발_지식맵.md  (언더스코어)
⚠️ DoubleDiver-Dashboard.md    (하이픈)
⚠️ DoubleDiver 개발 프로젝트/  (공백)
```
→ **문제**: 검색 및 링크 불편

---

## 🎯 재정리 목표

### 목표 구조 원칙
1. **단일 출처**: 각 유형의 파일은 한 곳에만
2. **명확한 계층**: 3-depth 이내 유지
3. **일관된 네이밍**: 하이픈(-) 또는 언더스코어(_) 통일
4. **확장 가능**: 새 프로젝트 추가 쉬움
5. **Dataview 친화적**: 쿼리하기 쉬운 구조

---

## 📁 새로운 구조 (제안)

```
Obsidian Vault/
│
├── 📅 01-Daily/                    # 모든 일일 노트 통합
│   ├── 2025-09/
│   ├── 2025-10/
│   │   ├── 2025-10-07.md
│   │   ├── 2025-10-24.md
│   │   └── 2025-10-31.md
│   └── 2025-11/
│
├── 📝 02-DevLogs/                  # 개발일지 (Dataview 시스템)
│   ├── 2025-09/
│   ├── 2025-10/
│   ├── 2025-11/
│   ├── DevLog-MOC.md              # 메인 MOC
│   └── _archive/
│       ├── old-DevLogs/            # DevLogs/ 폴더 내용
│       └── backup-old-structure/   # 기존 백업
│
├── 🚀 03-Projects/                 # 프로젝트별 폴더
│   ├── DevRules/
│   │   ├── DevRules-MOC.md        # 프로젝트 MOC
│   │   ├── Architecture/
│   │   ├── Reviews/
│   │   ├── Sessions/              # Session Summary들
│   │   └── Planning/
│   │       ├── Phase-C-Week-2-Guide.md
│   │       ├── Phase-D-Progress.md
│   │       └── Development-Guides/
│   │
│   └── DoubleDiver/
│       ├── DoubleDiver-MOC.md     # 프로젝트 MOC
│       ├── Specifications/
│       │   └── A3-Enhancement-Project.md
│       ├── Development/
│       │   ├── Integration-Guides/
│       │   └── System-Complete/
│       └── Learning/
│           └── Error-Learning-Database.md
│
├── 🗺️ 04-MOCs/                     # Map of Contents (마스터 MOCs만)
│   ├── Master-Index.md            # 전체 인덱스
│   ├── Universal-Development-System-Guide.md
│   └── Cross-Project-Links.md
│
├── 📚 05-Knowledge/                # 지식 자산
│   ├── Dev-Rules/
│   │   ├── Best-Practices/
│   │   └── Constitutional-Principles/
│   ├── Concepts/
│   │   └── Theory-Outlines/
│   └── Learning/
│       └── Process-Documentation/
│
├── 📋 06-Templates/                # 템플릿
│   ├── Daily-Note-Template.md
│   ├── DevLog-Template.md
│   ├── Error-Solution-Template.md
│   ├── Weekly-Review-Template.md
│   ├── Monthly-Review-Template.md
│   └── Project-Review-Template.md
│
├── 🛠️ 07-Resources/                # 리소스 및 도구
│   ├── Guides/
│   │   ├── Obsidian-MCP-Guide.md
│   │   ├── Obsidian-Dev-Setup-Guide.md
│   │   ├── Obsidian-Zen-MCP-Synergy.md
│   │   └── ObsidianBridge.md
│   ├── Diagrams/                  # Excalidraw 파일들
│   │   └── *.excalidraw
│   └── Prompts/
│       ├── architect_role.md
│       └── planner_role.md
│
├── ⚙️ 08-System/                   # 시스템 설정 및 작업
│   ├── Config/
│   │   └── System-Config/
│   ├── Tasks/
│   │   ├── FEAT-2025-09-26-01.md
│   │   ├── INTEGRATION-2025-10-28.md
│   │   └── DoubleDiver_실행형지식자산통합.md
│   └── Handoffs/
│       └── handoff-*.md
│
├── 🗄️ _archive/                    # 아카이브 (숨김)
│   ├── 2024-old-projects/
│   ├── deprecated-templates/
│   └── migration-backup-20251101/
│
└── 📌 Index.md                     # 메인 인덱스 (시작점)
```

---

## 🔄 마이그레이션 계획

### Phase 1: 백업 및 준비 (5분)
```bash
# 전체 vault 백업
1. Obsidian vault 전체 복사 → 외부 백업
2. Git commit (현재 상태 저장)
```

### Phase 2: 구조 생성 (5분)
```bash
# 새 폴더 구조 생성
1. 01-Daily/ ~ 08-System/ 폴더 생성
2. _archive/migration-backup-20251101/ 생성
```

### Phase 3: 파일 이동 (단계별)

#### Step 1: Daily Notes 통합 (2분)
```
Daily Notes/2025-10-24.md → 01-Daily/2025-10/2025-10-24.md
Daily Notes/2025-10-28_Development_Summary.md → 01-Daily/2025-10/
daily/2025-10-24.md → 01-Daily/2025-10/
루트/2025-10-07.md → 01-Daily/2025-10/
루트/2025-10-31.md → 01-Daily/2025-10/
```

#### Step 2: DevLogs 통합 (5분)
```
개발일지/ → 02-DevLogs/ (그대로 유지, 이름만 변경)
DevLogs/* → 02-DevLogs/_archive/old-DevLogs/
Dev Rules Project/개발일지/* → 02-DevLogs/_archive/
Dev Rules Project/개발 일지/* → 02-DevLogs/_archive/
Dev Rules Project/Work Logs/* → 02-DevLogs/_archive/
```

#### Step 3: Projects 정리 (10분)
```
# DevRules 프로젝트
Dev Rules Project/Architecture/ → 03-Projects/DevRules/Architecture/
Dev Rules Project/Reviews/ → 03-Projects/DevRules/Reviews/
Dev Rules Project/Session Summary* → 03-Projects/DevRules/Sessions/
Dev Rules Project/Phase*.md → 03-Projects/DevRules/Planning/
Dev Rules Project/개발 가이드/ → 03-Projects/DevRules/Planning/Development-Guides/

# DoubleDiver 프로젝트
DoubleDiver/ → 03-Projects/DoubleDiver/Development/
DoubleDiver 개발 프로젝트/ → 03-Projects/DoubleDiver/ (내용 병합)
Projects/DoubleDiver/ → 03-Projects/DoubleDiver/ (내용 병합)
DevLogs/DoubleDiver*.md → 03-Projects/DoubleDiver/Development/
```

#### Step 4: MOCs 정리 (5분)
```
# 프로젝트별 MOC는 프로젝트 폴더로
MOCs/DevRules_Project_MOC.md → 03-Projects/DevRules/DevRules-MOC.md
MOCs/DoubleDiver*.md → 03-Projects/DoubleDiver/DoubleDiver-MOC.md
개발일지/개발일지-MOC.md → 02-DevLogs/DevLog-MOC.md

# 마스터 MOC만 MOCs/ 유지
MOCs/Universal-Development-System-Guide.md → 04-MOCs/
MOCs/* → 04-MOCs/ (통합 및 정리)
```

#### Step 5: Knowledge & Resources (5분)
```
Knowledge/Dev-Rules/ → 05-Knowledge/Dev-Rules/
Learning/Concepts/ → 05-Knowledge/Concepts/

# Guides
Obsidian MCP 도구 가이드.md → 07-Resources/Guides/
OBSIDIAN_DEV_SETUP_GUIDE.md → 07-Resources/Guides/
ObsidianBridge.md → 07-Resources/Guides/

# Diagrams
Excalidraw/ → 07-Resources/Diagrams/

# Prompts
PROMPTS/* → 07-Resources/Prompts/
```

#### Step 6: Templates & System (3분)
```
Templates/* → 06-Templates/
TASKS/* → 08-System/Tasks/
System-Config/ → 08-System/Config/
handoffs/ → 08-System/Handoffs/
```

#### Step 7: Archive & Cleanup (5분)
```
# 임시 파일 → Archive
Untitled*.base → _archive/migration-backup-20251101/
Untitled.canvas → _archive/migration-backup-20251101/

# 한글 제목 파일들 검토 후 이동
목차.base → _archive/
해결해야할일.md → 08-System/Tasks/ (내용 확인 후)
프로젝트 체계적이고...정립.md → 05-Knowledge/Concepts/Theory-Outlines/
```

### Phase 4: 링크 업데이트 (자동화)

**Obsidian 자동 링크 업데이트**:
- Obsidian Settings → Files & Links → "Automatically update internal links" 활성화
- 파일 이동 시 모든 링크 자동 업데이트

**수동 확인 필요**:
- Dataview 쿼리의 FROM 경로
- 절대 경로 사용하는 링크

### Phase 5: MOC 재생성 (10분)

#### Master Index 생성
```markdown
# Obsidian Vault Master Index

## 📊 Quick Links
- [[02-DevLogs/DevLog-MOC|개발일지 MOC]]
- [[03-Projects/DevRules/DevRules-MOC|DevRules 프로젝트]]
- [[03-Projects/DoubleDiver/DoubleDiver-MOC|DoubleDiver 프로젝트]]
- [[04-MOCs/Universal-Development-System-Guide|개발 시스템 가이드]]

## 📁 Structure
\`\`\`dataview
TABLE file.folder as "Location", length(rows) as "Files"
FROM ""
WHERE file.folder != "_archive"
GROUP BY file.folder
SORT file.folder ASC
\`\`\`

## 📅 Recent Activity
\`\`\`dataview
TABLE file.mtime as "Modified"
FROM ""
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 20
\`\`\`
```

### Phase 6: 검증 (5분)

**체크리스트**:
- [ ] 모든 파일이 새 위치에 존재
- [ ] 깨진 링크 없음 (Obsidian: Broken Links 플러그인)
- [ ] Dataview 쿼리 정상 작동
- [ ] Git 커밋 및 백업 완료

---

## 📋 실행 체크리스트

### 사전 준비
- [ ] Obsidian vault 전체 백업 (외부 드라이브)
- [ ] Git commit 생성 (현재 상태)
- [ ] Obsidian 설정 백업 (.obsidian/ 폴더)

### 마이그레이션 실행
- [ ] Phase 1: 백업 완료
- [ ] Phase 2: 새 폴더 구조 생성
- [ ] Phase 3: 파일 이동 (Step 1-7)
- [ ] Phase 4: 링크 업데이트 확인
- [ ] Phase 5: MOC 재생성
- [ ] Phase 6: 검증 완료

### 사후 정리
- [ ] 빈 폴더 삭제
- [ ] Archive 폴더 정리
- [ ] Git commit (재정리 완료)
- [ ] 개발일지에 재정리 기록

---

## 🎯 기대 효과

### Before (현재)
```
❌ 개발일지 5곳에 분산
❌ Daily notes 2곳에 분산
❌ 프로젝트 자료 3곳에 분산
❌ 임시 파일 6개 방치
❌ MOC 4개 중복
❌ 검색 시 불필요한 결과 다수
```

### After (재정리 후)
```
✅ 개발일지 1곳 통합 (02-DevLogs/)
✅ Daily notes 1곳 (01-Daily/)
✅ 프로젝트 명확한 구조 (03-Projects/)
✅ 임시 파일 정리 (_archive/)
✅ MOC 체계화 (프로젝트별 + 마스터)
✅ 빠르고 정확한 검색
✅ Dataview 쿼리 효율성 향상
✅ 새 프로젝트 추가 용이
```

---

## ⚠️ 주의사항

### 1. 백업 필수
- 마이그레이션 전 반드시 전체 백업
- Git commit으로 복구 지점 확보

### 2. 단계별 진행
- 한 번에 모든 파일 이동 X
- Phase별로 진행하며 검증

### 3. 링크 확인
- Obsidian 자동 업데이트 활성화
- Dataview 쿼리 경로 수동 확인

### 4. 협업 고려
- 다른 사용자/디바이스와 공유 시 동기화 확인
- Obsidian Sync 사용 시 충돌 주의

---

## 📅 실행 일정 제안

**총 소요 시간**: 약 50-60분

**권장 실행 시간**:
- 개발 작업 없는 시간
- 충분한 시간 확보 (중간에 중단하지 않도록)

**실행 후**:
- 하루 정도 새 구조 테스트
- 문제 발견 시 즉시 수정

---

**준비 완료 시 실행 명령어**:
```bash
# Obsidian MCP를 통한 자동 재정리 스크립트 실행
python scripts/obsidian_reorganize.py --plan-file docs/OBSIDIAN_REORGANIZATION_PLAN.md
```

또는 **수동으로 단계별 진행**도 가능합니다.
