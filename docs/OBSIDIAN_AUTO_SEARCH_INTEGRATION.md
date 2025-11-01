# Obsidian Auto-Search Integration Guide

**Status**: IMPLEMENTED
**Date**: 2025-11-01
**Purpose**: Enable bidirectional knowledge flow - AI automatically references past solutions

---

## Problem Statement

**Before**:
```
User: "auth.py에서 401 error 발생"
AI: [처음부터 분석 시작] Sequential 분석... 30분 소요
```

**After** (with Auto-Search):
```
User: "auth.py에서 401 error 발생"
AI: [자동 Obsidian 검색]
    → 과거 해결책 발견: "AUTH_SECRET 누락"
    → 2분 내 해결 (93% 시간 단축)
```

---

## How It Works

### 1. Automatic Detection

`scripts/auto_obsidian_context.py` detects debugging questions:

```python
class AutoObsidianContext:
    def should_search_obsidian(self, user_query: str) -> bool:
        """Detect if Obsidian search is needed"""
        debug_indicators = [
            "error", "bug", "fail", "fix", "solve",
            "problem", "issue", "broken"
        ]
        for indicator in debug_indicators:
            if indicator in user_query.lower():
                return True
        return False
```

**Triggers**:
- Error keywords: "401 error", "bug", "broken"
- Tech keywords: "React", "auth", "payment"
- How-to questions: "how to", "how do"

### 2. Keyword Extraction

```python
def extract_keywords(self, user_query: str) -> List[str]:
    """Extract search keywords"""
    keywords = []

    # Error codes (e.g., "401", "500")
    error_match = re.search(r"(\d{3})", user_query)
    if error_match:
        keywords.append(error_match.group(1))

    # Tech stack (e.g., "react", "auth")
    for pattern in ["react", "vue", "auth", "payment"]:
        if re.search(pattern, user_query.lower()):
            keywords.append(pattern)

    return keywords
```

### 3. MCP Search Execution

When keywords detected, Claude Code should:

```python
# Auto-triggered by Claude Code
keywords = ["401", "auth", "debug"]

# Execute MCP search
mcp__obsidian__obsidian_simple_search(
    query="401 auth debug",
    context_length=200
)

# Use results in answer
# → If past solution found: Use it
# → If not found: Proceed with normal analysis
```

---

## Integration with Claude Code

### Method 1: Manual Workflow (Current)

**When user asks debugging question**:

1. Claude Code detects keywords (mental check)
2. Manually invoke: `mcp__obsidian__obsidian_simple_search`
3. Incorporate findings into answer

**Example**:
```
User: "React Hook 렌더링 문제"
Claude: [Thinks: "React Hook" detected]
        → Searches Obsidian for "React Hook"
        → Finds past solution
        → "과거에 useEffect dependency 문제였습니다. [[React-Hook-Dependencies]] 참고"
```

### Method 2: Hook Integration (Future)

Add to `.claude/CLAUDE.md`:

```markdown
## Auto Obsidian Search

When user asks about:
- Errors (401, 500, bug, fail)
- Tech problems (React, auth, payment)
- How-to questions

ALWAYS search Obsidian first:
1. Extract keywords from question
2. Run: mcp__obsidian__obsidian_simple_search(query=keywords)
3. Check if past solution exists
4. If found: Prioritize past solution
5. If not: Proceed with normal analysis

Script: scripts/auto_obsidian_context.py
```

---

## Testing the Integration

### Test Case 1: 401 Auth Error

```bash
# User question
"auth.py에서 401 error 발생"

# Expected flow
1. Detect: ["401", "auth", "error"]
2. Search: mcp__obsidian__obsidian_simple_search(query="401 auth")
3. Find: Knowledge-Compound-Effect.md
   → "과거 해결: AUTH_SECRET 누락"
   → "해결 시간: 2분 (93% 단축)"
4. Answer: "과거에 같은 문제가 있었습니다. .env 파일에 AUTH_SECRET을 추가하세요."
```

### Test Case 2: React Performance

```bash
# User question
"React 성능 최적화 방법?"

# Expected flow
1. Detect: ["react", "how to"]
2. Search: mcp__obsidian__obsidian_simple_search(query="React optimization")
3. Find: Resources/Guides/React-Performance.md (if exists)
4. Answer: Links to past guides or Context7 official docs
```

### Test Case 3: New Problem (No History)

```bash
# User question
"GraphQL subscriptions not working"

# Expected flow
1. Detect: ["graphql", "not working"]
2. Search: mcp__obsidian__obsidian_simple_search(query="GraphQL subscriptions")
3. Find: Nothing
4. Answer: [Normal Sequential analysis]
   → Save result to Obsidian for future
```

---

## Verification

### 1. Test Script

```bash
python scripts/auto_obsidian_context.py
```

**Expected output**:
```
=== Auto Obsidian Context Demo ===

User Question: auth.py에서 401 error 발생
Should search Obsidian? True
Extracted keywords: ['401', 'auth', 'debug']

>>> Triggering MCP Obsidian search...
>>> mcp__obsidian__obsidian_simple_search(query='401 auth debug')
```

### 2. Manual Test with Claude Code

**Prompt to Claude**:
```
"auth.py에서 401 error가 발생했어요. 과거에 비슷한 문제 있었나요?"
```

**Expected Claude behavior**:
1. Recognizes debugging question
2. Searches Obsidian: `mcp__obsidian__obsidian_simple_search(query="auth 401")`
3. Finds: Knowledge-Compound-Effect.md with past solution
4. Answers: "과거에 AUTH_SECRET 누락 문제가 있었습니다. [[Debug-Auth-401-Missing-Env]] 참고하세요."

---

## ROI Analysis

### Before Auto-Search

| Scenario | Time | Repeated? |
|----------|------|-----------|
| First occurrence | 30 min | Yes (no memory) |
| Second occurrence | 30 min | Yes (no memory) |
| Third occurrence | 30 min | Yes (no memory) |
| **Total (3x)** | **90 min** | **100% repetition** |

### After Auto-Search

| Scenario | Time | Repeated? |
|----------|------|-----------|
| First occurrence | 30 min | Saved to Obsidian |
| Second occurrence | 2 min | Found in Obsidian (93% ↓) |
| Third occurrence | 2 min | Found in Obsidian (93% ↓) |
| **Total (3x)** | **34 min** | **62% time saved** |

### Compound Effect (1 Year)

Assumptions:
- 5 debugging sessions/day
- 30% are repeated problems
- Each repeated problem saves 28 minutes (30 → 2)

**Calculation**:
```
Daily savings: 5 sessions × 30% repeat × 28 min = 42 min/day
Annual savings: 42 min × 250 workdays = 10,500 min = 175 hours/year

ROI: 175 hours saved / 8 hours setup = 2,188% ROI
```

---

## Next Steps

### Phase 1: Manual Integration (Current)

- [x] Create `auto_obsidian_context.py` script
- [x] Test keyword detection
- [x] Verify MCP Obsidian search works
- [ ] Document workflow in CLAUDE.md

### Phase 2: Behavioral Integration (Next)

- [ ] Add to `.claude/CLAUDE.md` as standard practice
- [ ] Train Claude Code to search Obsidian automatically
- [ ] Create examples in documentation

### Phase 3: Full Automation (Future)

- [ ] Pre-commit hook triggers auto-search
- [ ] Suggest related past solutions during coding
- [ ] Auto-link similar problems in Obsidian

---

## Troubleshooting

### Issue 1: Search returns too many results

**Solution**: Use more specific keywords
```python
# Too broad
mcp__obsidian__obsidian_simple_search(query="error")

# Better
mcp__obsidian__obsidian_simple_search(query="auth 401 error")
```

### Issue 2: No results found

**Reason**: Problem not yet documented
**Solution**: Proceed with normal analysis, then save to Obsidian for next time

### Issue 3: Windows encoding errors

**Cause**: Emojis in Python code
**Solution**: Use ASCII alternatives
```python
# Wrong (Windows crashes)
print("✅ Success")

# Correct
print("[OK] Success")
```

---

## Maintenance

### Weekly

- Check Dataview queries for most searched topics
- Review duplicate documentation
- Update keyword patterns if new tech added

### Monthly

- Analyze search hit rate
- Optimize keyword extraction
- Clean up stale documentation

---

## Success Metrics

Track these in `MCP-Dashboard.md`:

```dataview
TABLE
  count(rows) AS "Search triggered",
  length(filter(rows, (r) => r.found = "yes")) AS "Solution found",
  avg(rows.time_saved) AS "Avg time saved (min)"
FROM ""
WHERE contains(tags, "auto-search")
GROUP BY date
```

**Target metrics**:
- Search trigger rate: >30% of debugging questions
- Solution found rate: >60% for repeated problems
- Time saved: >20 minutes average per successful search

---

## References

- `scripts/auto_obsidian_context.py` - Main implementation
- `Knowledge-Compound-Effect.md` - Concept explanation
- `MCP-Context7-Integration-Guide.md` - MCP integration details
- `Quick-Start-MCP-Obsidian.md` - 5-minute guide

---

**Status**: Ready for use
**Next action**: Add behavioral pattern to `.claude/CLAUDE.md`
