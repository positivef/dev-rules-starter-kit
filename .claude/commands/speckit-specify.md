---
description: Create feature specification from natural language description with automatic branch creation
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/speckit-specify` **is** the feature description. Assume you always have it available even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate concise short name** (2-4 words) for the branch:
   - Analyze feature description and extract meaningful keywords
   - Create 2-4 word short name capturing essence of feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep concise but descriptive enough to understand at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"

2. **Create feature branch**:
   ```bash
   # Generate branch name
   BRANCH_NAME="feat/$(echo "{short-name}" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"

   # Create and checkout branch
   git checkout -b "$BRANCH_NAME"
   ```

3. **Create specs directory**:
   ```bash
   # Create directory for this feature's specs
   FEATURE_DIR="specs/$BRANCH_NAME"
   mkdir -p "$FEATURE_DIR"
   mkdir -p "$FEATURE_DIR/contracts"
   ```

4. **Load spec template**:
   - Read `templates/spec-template.md` to understand required sections

5. **Execute specification workflow**:
   a. Parse user description from Input
      - If empty: ERROR "No feature description provided"

   b. Extract key concepts from description
      - Identify: actors, actions, data, constraints

   c. For unclear aspects:
      - Make informed guesses based on context and industry standards
      - Only mark with `[NEEDS CLARIFICATION: specific question]` if:
        - Choice significantly impacts feature scope or user experience
        - Multiple reasonable interpretations exist with different implications
        - No reasonable default exists
      - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
      - Prioritize clarifications by impact: scope > security/privacy > UX > technical details

   d. Fill User Scenarios & Testing section
      - If no clear user flow: ERROR "Cannot determine user scenarios"
      - **IMPORTANT**: User stories must be:
        - **PRIORITIZED** as user journeys ordered by importance (P1, P2, P3...)
        - **INDEPENDENTLY TESTABLE** - each story should be a viable MVP
        - **STANDALONE** - can be developed, tested, deployed independently

   e. Generate Functional Requirements
      - Each requirement must be testable
      - Use reasonable defaults for unspecified details
      - Document assumptions in Assumptions section

   f. Define Success Criteria
      - Create measurable, technology-agnostic outcomes
      - Include quantitative metrics (time, performance, volume)
      - Include qualitative measures (user satisfaction, task completion)
      - Each criterion must be verifiable without implementation details

   g. Identify Key Entities (if data involved)

6. **Write specification** to `$FEATURE_DIR/spec.md` using template structure, replacing placeholders with concrete details while preserving section order and headings

7. **Specification Quality Validation**:

   a. Create Spec Quality Checklist at `$FEATURE_DIR/checklists/requirements.md`:

   ```markdown
   # Specification Quality Checklist: [FEATURE NAME]

   **Purpose**: Validate specification completeness and quality before proceeding to planning
   **Created**: [DATE]
   **Feature**: [Link to spec.md]

   ## Content Quality

   - [ ] No implementation details (languages, frameworks, APIs)
   - [ ] Focused on user value and business needs
   - [ ] Written for non-technical stakeholders
   - [ ] All mandatory sections completed

   ## Requirement Completeness

   - [ ] No [NEEDS CLARIFICATION] markers remain
   - [ ] Requirements are testable and unambiguous
   - [ ] Success criteria are measurable
   - [ ] Success criteria are technology-agnostic
   - [ ] All acceptance scenarios are defined
   - [ ] Edge cases are identified
   - [ ] Scope is clearly bounded
   - [ ] Dependencies and assumptions identified

   ## Feature Readiness

   - [ ] All functional requirements have clear acceptance criteria
   - [ ] User scenarios cover primary flows
   - [ ] Feature meets measurable outcomes defined in Success Criteria
   - [ ] No implementation details leak into specification

   ## Notes

   - Items marked incomplete require spec updates before `/speckit-plan`
   ```

   b. Run Validation Check: Review spec against each checklist item
      - For each item, determine if it passes or fails
      - Document specific issues found

   c. Handle Validation Results:
      - **If all items pass**: Mark checklist complete, proceed to step 7
      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List failing items and specific issues
        2. Update spec to address each issue
        3. Re-run validation (max 3 iterations)
        4. If still failing after 3 iterations, document in checklist notes and warn user
      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all markers from spec
        2. **LIMIT CHECK**: If >3 markers exist, keep only 3 most critical
        3. For each clarification (max 3), present options in this format:

        ```markdown
        ## Question [N]: [Topic]

        **Context**: [Quote relevant spec section]

        **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

        **Suggested Answers**:

        | Option | Answer | Implications |
        |--------|--------|--------------|
        | A      | [First answer] | [What this means] |
        | B      | [Second answer] | [What this means] |
        | C      | [Third answer] | [What this means] |
        | Custom | Provide your own answer | [How to provide custom input] |

        **Your choice**: _[Wait for user response]_
        ```

        4. **CRITICAL**: Ensure markdown tables are properly formatted with consistent spacing
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting
        7. Wait for user responses (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update spec by replacing markers with user's answers
        9. Re-run validation after all clarifications resolved

   d. Update Checklist: After each validation iteration, update checklist file

8. **Report completion**:
   - Branch name created
   - Spec file path
   - Checklist results
   - Readiness for next phase:
     ```bash
     # If [NEEDS CLARIFICATION] markers resolved:
     echo "Ready for: /speckit-plan"

     # If clarifications still needed:
     echo "Resolve clarifications above before proceeding"
     ```

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**
- Avoid HOW to implement (no tech stack, APIs, code structure)
- Written for business stakeholders, not developers
- DO NOT create any embedded checklists (separate command)

## Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, tools
3. **User-focused**: Describe outcomes from user/business perspective
4. **Verifiable**: Can be tested/validated without knowing implementation

**Good examples**:
- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"

**Bad examples** (implementation-focused):
- "API response time is under 200ms" (too technical)
- "Database can handle 1000 TPS" (implementation detail)
- "React components render efficiently" (framework-specific)

## Common Areas Needing Clarification

Only ask about these if no reasonable default exists:
- Feature scope and boundaries (include/exclude specific use cases)
- User types and permissions (if multiple conflicting interpretations)
- Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask):
- Data retention: Industry-standard practices
- Performance targets: Standard web/mobile app expectations
- Error handling: User-friendly messages with fallbacks
- Authentication method: Standard session-based or OAuth2
- Integration patterns: RESTful APIs

## Template Structure Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant
- When section doesn't apply, remove it entirely (don't leave as "N/A")
