---
description: Create or update the project constitution with development principles and governance rules
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `/memory/constitution.md`. This file defines the immutable principles governing all development.

Follow this execution flow:

1. **Load existing constitution**:
   - Read `/memory/constitution.md`
   - Identify current version and principles
   - Check if constitution already exists

2. **Collect/derive values for updates**:
   - If user input supplies changes, apply them
   - Otherwise maintain existing principles
   - For governance dates:
     - `RATIFICATION_DATE`: Original adoption date (if unknown, use today)
     - `LAST_AMENDED_DATE`: Today if changes made, otherwise keep previous
   - `VERSION` must increment according to semantic versioning:
     - **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
     - **MINOR**: New principle/section added or materially expanded guidance
     - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

3. **Draft updated constitution**:
   - Apply requested changes
   - Ensure all 10 principles are present:
     - I. Library-First Development
     - II. CLI Interface Mandate
     - III. Test-First Development (NON-NEGOTIABLE)
     - IV. Integration-First Testing
     - V. Windows Encoding Compliance (CRITICAL)
     - VI. Observability & Structured Logging
     - VII. Simplicity & YAGNI
     - VIII. Anti-Abstraction & Framework Trust
     - IX. Specification-Driven Development (SDD)
     - X. Conventional Commits & Semantic Versioning
   - Ensure Governance section includes:
     - Amendment process
     - Compliance enforcement (automated + manual)
     - Exception handling
   - Maintain Document Lifecycle section
   - Keep Quick Decision Tree current

4. **Consistency validation**:
   - Check that all principles are testable and enforceable
   - Verify governance rules are clear and actionable
   - Ensure no contradictions between principles
   - Confirm examples are correct and helpful

5. **Produce Sync Impact Report** (prepend as HTML comment):
   ```html
   <!--
   CONSTITUTION UPDATE REPORT
   ==========================
   Version: [old] → [new]
   Date: [YYYY-MM-DD]

   Modified Principles:
   - [List any changed principles]

   Added Sections:
   - [List any new sections]

   Removed Sections:
   - [List any removed sections]

   Templates Requiring Updates:
   - [ ] DEVELOPMENT_RULES.md (sync with Article V, X)
   - [ ] .pre-commit-config.yaml (sync with Article III, V)
   - [ ] CLAUDE.md (sync with Article IX)

   Follow-up TODOs:
   - [List any deferred items]
   -->
   ```

6. **Validation before final output**:
   - No remaining unexplained placeholders
   - Version line matches report
   - Dates in ISO format (YYYY-MM-DD)
   - Principles are declarative and testable
   - All examples are correct

7. **Write updated constitution** back to `/memory/constitution.md` (overwrite)

8. **Output summary to user**:
   - New version and bump rationale
   - Any files flagged for manual follow-up
   - Suggested commit message:
     ```
     docs(constitution): amend to vX.Y.Z (principle additions + governance update)
     ```

## Formatting & Style Requirements

- Use Markdown headings exactly as in the template
- Keep lines readable (<100 chars ideally)
- Maintain single blank line between sections
- Avoid trailing whitespace
- Use consistent bullet/numbering styles

## If Critical Information Missing

If critical info is unknown (e.g., ratification date), insert `TODO(<FIELD_NAME>): explanation` and include in Sync Impact Report under deferred items.

## Important Notes

- This constitution supersedes all other development practices
- When conflicts arise, constitution prevails
- All development decisions must pass constitutional compliance checks
- Quarterly review cycle (every 3 months)
