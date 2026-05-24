# Session Workflow Dashboard (POS-92, MVP / Phase 1)

Read-only aggregator that surfaces multi-session "tangles" for one project.
Lives in `dev-rules-starter-kit` as a cross-project meta-tool (design decision D1).

## Run

```bash
python -m workflow_dashboard.build \
  --project-path "C:/Users/user/Documents/GitHub/260404_gongpro/fieldsync-pro" \
  --project-name fieldsync-pro --open
```

Output: `workflow_dashboard/output/{model.json,index.html}` (gitignored).
The HTML is **self-contained** (model embedded) — open it directly, no server needed.

Options: `--freshness-minutes` (default 30), `--stale-days` (default 3),
`--claude-projects-dir` (default `~/.claude/projects`), `--out`, `--open`.

## What it shows

- **Slots** from `.claude/coordination/claude-*.md` (slot, status, topic, updated)
- **Sessions** from `~/.claude/projects/<slug>/*.jsonl` (id, live?, title, branch, PR)
- **Git** state of the project (branch, uncommitted, unpushed, commits/24h, worktrees)
- **Conflicts** (5 rules):

| rule | severity | condition |
|---|---|---|
| `slot_collision` | 🔴 | ≥2 sessions live (within freshness window) in the shared dir |
| `branch_divergence` | ⚠ | live sessions span ≥2 branches, or differ from git HEAD |
| `duplicate_work` | ⚠ | ≥2 coordination slots `in-progress` simultaneously |
| `stale_slot` | 🟡 | active slot untouched longer than `stale_days` |
| `uncommitted_drift` | 🟡 | git has uncommitted or unpushed changes |

## Design notes (departures from the approved design doc, intentional)

1. **Slots and sessions are separate panels** — coordination (`claude-N`) and jsonl
   (`sessionId` uuid) share no key, so they cannot be merged into one row.
2. `duplicate_work` uses "≥2 in-progress slots" instead of file-set intersection
   (`files_touched` per session deferred to Phase 2).
3. Model is **embedded** in the HTML (not `fetch`ed) so it opens via `file://`.
4. gstack timeline is treated as an optional source (absent at the expected path
   in testing → skipped by fail-safe).

## Safety

Read-only (writes nothing to sources), idempotent, fail-safe (a broken/missing
source is skipped, never crashes the build). Git output is decoded as UTF-8 to
avoid Windows cp949 crashes on Korean commit messages.

**Rollback** (zero project impact): delete `workflow_dashboard/output/`, then the
`workflow_dashboard/` folder.

## Phase 2 (next)

All 68 projects in one cross-project view + filter/search, plus file-intersection
`duplicate_work` detection.
