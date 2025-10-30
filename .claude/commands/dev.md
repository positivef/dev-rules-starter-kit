# Enhanced Dev Pipeline - 6-Stage Natural Language to Execution

Execute the enhanced 6-stage pipeline for development tasks with academic verification.

## Pipeline Stages:
1. **Natural Language Input** - Gather and clarify requirements
2. **Requirements Analysis** - Structure with requirements-analyst skill
3. **Academic Verification** - Multi-source research validation (5 DBs)
4. **YAML Refinement** - Generate verified contract
5. **Execution & Validation** - Run with Constitution checks
6. **Documentation** - Sync to Obsidian with references

## Usage:
`/dev "create JWT authentication API with refresh tokens"`

---

## Instructions for Claude:

When `/dev` is invoked with a natural language request, execute the following 6-stage pipeline:

### Stage 1: Interactive Gathering
Use the `interactive_gather` MCP tool to:
- Parse the user's request
- Identify ambiguities
- Ask up to 3 clarifying questions if needed
- Structure the requirements

### Stage 2: Requirements Analysis
Use the `generate_yaml` MCP tool with `use_requirements_analyst: true` to:
- Convert structured requirements to YAML
- Include suggested Constitution articles
- Add acceptance criteria

### Stage 3: Academic Verification
Use the `verify_with_research` MCP tool to:
- Query 5 academic sources in parallel:
  - Semantic Scholar (30% weight)
  - arXiv (25% weight)
  - Crossref (20% weight)
  - PubMed (15% weight)
  - OpenAlex (10% weight)
- Calculate weighted consensus
- Only mark verified=true if confidence >= 0.65
- Include partial verification mode for fallback

### Stage 4: YAML Refinement
Re-call `generate_yaml` with verification results to:
- Incorporate academic references
- Add verification confidence to metadata
- Apply any Constitution fixes if needed
- Validate schema

### Stage 5: Execute & Validate
Use `execute_task_enhanced` to:
- Execute the YAML contract
- Run Constitution validation
- Auto-fix violations and retry (max 2 attempts)
- Collect evidence

### Stage 6: Documentation
Use `sync_to_obsidian_enhanced` to:
- Create comprehensive documentation
- Include academic references with links
- Add confidence scores
- Save to Evidence folder
- Auto-tag based on verification status

## Policies:
- ✅ Verified only if weighted_confidence >= 0.65
- ⚠️ Partial verification (0.4-0.65) proceeds with warnings
- ❌ Low confidence (<0.4) requires manual review
- 🔄 Constitution failures trigger auto-fix and retry
- 📁 All evidence saved to RUNS/evidence/

## Example Flow:

```
User: /dev "create login API with JWT"

Claude:
1️⃣ Gathering requirements...
   - Need clarification: OAuth2 or simple JWT?
   - Database preference?

2️⃣ Analyzing with requirements-analyst...
   - Functional: Auth endpoints, token generation
   - Non-functional: Security, performance

3️⃣ Verifying with academic research...
   - Semantic Scholar: 15 papers found
   - arXiv: 8 papers found
   - Weighted consensus: 0.78 ✅

4️⃣ Refining YAML with verification...
   - Added RFC 7519 references
   - Confidence: 0.78 (verified)

5️⃣ Executing task...
   - Constitution check: P5, P7, P8 ✅
   - Tests created and passing

6️⃣ Documented to Obsidian...
   - Path: 개발일지/2025-10-28_jwt_api.md
   - Tags: #verified #high-confidence #jwt
```

## Error Handling:
- If academic verification fails → Partial verification mode
- If Constitution fails → Auto-fix and retry
- If execution fails → Fallback with evidence
- All failures logged to RUNS/evidence/

This pipeline ensures hallucination-free, academically-verified development with full Constitution compliance.
