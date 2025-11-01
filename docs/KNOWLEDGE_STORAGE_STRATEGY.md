# 지식 저장 전략 분석

**분석 일자**: 2025-10-29
**목적**: 프로젝트 크기 최소화 + 지식 재사용 극대화

---

## 세 가지 접근 방식

### 옵션 A: 프로젝트 중심 (현재)

```
프로젝트/
├── RUNS/error_learning_db.json    (10KB - 상세 패턴)
├── docs/EMOJI_USAGE_RULES.md      (5KB - 상세 규칙)
└── scripts/pre_execution_guard.py (5KB)

옵시디언/
└── 개발일지/*.md (문서화, 중복)
```

**장점**:
- ✅ Git 버전 관리
- ✅ 프로젝트와 함께 배포
- ✅ CI/CD 통합 가능
- ✅ 외부 의존성 없음
- ✅ 다른 개발자와 공유 쉬움

**단점**:
- ❌ 프로젝트 크기 증가 (20KB+)
- ❌ 데이터 중복 (프로젝트 + 옵시디언)
- ❌ 업데이트 시 두 곳 수정 필요

---

### 옵션 B: 옵시디언 중심 (참조만)

```
프로젝트/
├── RUNS/error_patterns.txt        (1KB - 옵시디언 링크만)
│   "See: C:/Users/user/Documents/Obsidian Vault/..."
└── scripts/pre_execution_guard.py (5KB)

옵시디언/
└── Knowledge/
    ├── Error_Patterns.md (10KB - 실제 데이터)
    └── Emoji_Rules.md (5KB)
```

**장점**:
- ✅ 프로젝트 크기 최소 (6KB)
- ✅ 단일 진실 소스
- ✅ 옵시디언에서 관리 편함
- ✅ 중복 없음

**단점**:
- ❌ 옵시디언 없으면 작동 안함
- ❌ CI/CD 통합 불가
- ❌ 다른 개발자 공유 어려움
- ❌ Git 버전 관리 불가
- ❌ 프로젝트 이식성 저하

---

### 옵션 C: 하이브리드 (권장) ⭐

```
프로젝트/
├── RUNS/
│   ├── error_patterns_core.json   (2KB - 핵심 패턴만)
│   └── obsidian_reference.json    (1KB - 상세 링크)
├── docs/
│   └── RULES_QUICK_REF.md         (2KB - 간단 참조)
└── scripts/
    └── pre_execution_guard.py     (6KB - 옵시디언 참조 기능)

옵시디언/
└── Knowledge/Dev-Rules/
    ├── Error_Database.md          (Full 10KB)
    ├── Emoji_Rules_Complete.md    (Full 5KB)
    └── Prevention_Patterns.md     (Full 8KB)
```

**장점**:
- ✅ 프로젝트 경량 (11KB vs 20KB)
- ✅ 옵시디언 있으면 상세 정보
- ✅ 옵시디언 없어도 기본 동작
- ✅ Git 버전 관리 (핵심만)
- ✅ CI/CD 통합 가능
- ✅ 중복 최소화

**단점**:
- ⚠️ 약간의 복잡도 증가
- ⚠️ 두 시스템 동기화 필요

---

## 상세 비교

| 기준 | 옵션 A | 옵션 B | 옵션 C |
|------|--------|--------|--------|
| 프로젝트 크기 | 20KB | 6KB | 11KB ⭐ |
| 외부 의존성 | 없음 ⭐ | 필수 | 선택적 ⭐ |
| Git 관리 | 전체 ⭐ | 불가 | 핵심만 ⭐ |
| CI/CD 통합 | 가능 ⭐ | 불가 | 가능 ⭐ |
| 이식성 | 높음 ⭐ | 낮음 | 높음 ⭐ |
| 중복 | 있음 | 없음 ⭐ | 최소 ⭐ |
| 관리 복잡도 | 낮음 ⭐ | 낮음 ⭐ | 중간 |

---

## 권장: 옵션 C (하이브리드)

### 핵심 원칙
```
"Essential in Project, Details in Obsidian"
```

### 구체적 구현

#### 1. 프로젝트 (핵심만)

**error_patterns_core.json** (2KB):
```json
{
  "version": "1.0",
  "patterns": [
    {
      "id": "E001",
      "pattern": "print.*emoji",
      "severity": "HIGH",
      "quick_fix": "Use [OK] instead"
    }
  ],
  "obsidian_reference": {
    "enabled": true,
    "path": "${OBSIDIAN_VAULT_PATH}/Knowledge/Dev-Rules/Error_Database.md",
    "fallback": "use_core_only"
  }
}
```

**RULES_QUICK_REF.md** (2KB):
```markdown
# Quick Reference

## E001: print() with emoji
- **Risk**: HIGH
- **Fix**: Use [OK], [X], [!]
- **Details**: See Obsidian vault

> For complete analysis, patterns, and examples:
> C:/Users/user/Documents/Obsidian Vault/Knowledge/Dev-Rules/
```

#### 2. 옵시디언 (상세)

**Error_Database.md** (10KB):
```markdown
# Complete Error Database

## E001: UnicodeEncodeError with emoji

### Detailed Analysis
- Occurred: 8 times
- Dates: 2025-10-25 ~ 2025-10-28
- Root cause: Windows cp949 encoding
- Stack traces: [링크]

### All Occurrences
1. test_obsidian_live.py:85 - print(history_section)
2. framework_validator.py:142 - print(section)
...

### Code Examples
[상세 예제 20개]

### Prevention Strategies
[5가지 전략 상세]
```

#### 3. 통합 로더

**pre_execution_guard.py** 수정:
```python
def _load_patterns(self):
    # 1. 프로젝트 핵심 로드
    core = load_json("RUNS/error_patterns_core.json")

    # 2. 옵시디언 상세 로드 (선택적)
    if obsidian_available():
        detailed = load_obsidian_patterns()
        return merge(core, detailed)

    # 3. Fallback: 핵심만으로 동작
    return core
```

---

## 실제 크기 비교

### 현재 프로젝트
```bash
$ du -sh RUNS/ docs/
20KB    RUNS/
15KB    docs/
Total: 35KB
```

### 하이브리드 적용 후
```bash
$ du -sh RUNS/ docs/
3KB     RUNS/       (-85%)
5KB     docs/       (-67%)
Total: 8KB          (-77%)

Obsidian: +23KB (별도 관리)
```

---

## 의사결정 가이드

### 선택 기준

**프로젝트가 작고 단독 사용?**
→ **옵션 A** (단순함 우선)

**팀 프로젝트 + CI/CD 필수?**
→ **옵션 A** (외부 의존성 제거)

**개인 프로젝트 + 옵시디언 활용?**
→ **옵션 C** (하이브리드)

**지식 베이스가 매우 큼 (>100KB)?**
→ **옵션 C** (프로젝트 크기 중요)

---

## 구현 단계

### Phase 1: 핵심 추출
```bash
# 현재 20KB → 핵심 3KB 추출
python scripts/extract_core_patterns.py
```

### Phase 2: 옵시디언 상세 생성
```bash
# 상세 내용을 옵시디언으로
python scripts/sync_to_obsidian.py --detailed
```

### Phase 3: 통합 로더 구현
```python
# pre_execution_guard.py 수정
# - 핵심만으로 기본 동작
# - 옵시디언 있으면 상세 로드
```

### Phase 4: 자동 동기화
```bash
# Git commit hook
# - 프로젝트 핵심 업데이트 시
# - 옵시디언 상세도 자동 업데이트
```

---

## 최종 권장

### ⭐ 옵션 C (하이브리드)

**이유**:
1. **프로젝트 크기**: 77% 감소
2. **외부 의존성**: 선택적 (없어도 작동)
3. **Git 관리**: 핵심만 (이력 관리)
4. **CI/CD**: 통합 가능
5. **지식 재사용**: 옵시디언 극대화

**Trade-off**:
- 약간의 복잡도 증가
- 두 시스템 동기화 필요

하지만 **장점이 단점을 압도**합니다.

---

## 다음 단계

1. 핵심 패턴 추출 스크립트 구현
2. 옵시디언 상세 문서 생성
3. 통합 로더 구현
4. 자동 동기화 설정
5. 문서화 및 가이드 작성

**시작할까요?**
