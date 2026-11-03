# Autonomous agent loop

Governance lives in [`../AGENTS.md`](../AGENTS.md) → "Operating policy v3 (2026-11-04)". It supersedes every older gate (P0 / PUBLICATION_HOLD / NO_NEW_INTERNAL_PUSH, two-tier approvals). Newest dated policy wins; older docs are history.

## 0. Start (1–2 min)
1. `git fetch --all --prune`; trust Git/GitHub over any document SHA.
2. `python3 /workspace/repos/tools/repo_health.py` (or `faaff/ai/repo_health.py`) — open PRs, failing CI, NO_GO, orphan branches.
3. Read `ai/HANDOFF.md` / `ai/PROJECT_STATE.json` for blockers (only the parts dated after 2026-11-04 are binding).
4. On the Grok Bot box: `bash /workspace/repos/bootstrap.sh` (idempotent: tools, clone/fetch, all tests).

## 1. Pick work (in order)
1. Owner's latest request.
2. Failing CI on any PR → fix on a branch.
3. Duplicate / superseded PRs → close with a reason, or consolidate.
4. `open_items` in `ai/PROJECT_STATE.json`.
5. Small quality wins (tests, stale docs).

Prefer improving an existing PR over opening a new one. Bundle related changes; keep the PR count low.

## 2. Implement
- Branch: `proposal/<topic>-<YYYYMMDD>`. Never push to `main` directly; never force-push.
- Minimal, purposeful diffs.

## 3. Verify locally before the PR
```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_lists.py
python scripts/generate_lists.py --check
# real engines (deps / engine / filter changes; Node 24)
python scripts/prepare_engine.py --directory ../work/filter-engine
npm ci --prefix verification/ghostery --ignore-scripts --no-audit --no-fund
node scripts/check_engine.mjs --engine-dir ../work/filter-engine --ghostery-entry verification/ghostery/node_modules/@ghostery/adblocker/dist/esm/index.js
```
- Dependency bumps: update `verification/ghostery/package*.json` **and** `verification/engine-lock.json` (`secondary_engine`) together.
- After merging anything here, re-import into faaff: `cd ../faaff && python3 ai/reimport_s.py --s-repo ../s`, then PR + merge.
- `s` is public (anonymous filter subscriptions). Merging here updates live lists — keep subscription paths stable and add only filter content/tooling.

## 4. PR → self-check → merge
1. Open the PR (template: `.github/pull_request_template.md`): what/why, commands run + results, rollback.
2. `gh pr checks <n> --watch`. On failure: read logs, push a fix commit (no force-push). Two identical failures → stop, record cause and alternatives in the PR, move on.
3. When **all checks are green, the PR is mergeable, and the change is revertible**: merge it yourself
   `bash /workspace/repos/tools/safe_merge.sh <s|faaff> <n>` (squash, pinned to the head SHA).
4. After merging: delete the branch (auto-delete is on), close PRs it supersedes, run follow-ups (e.g. faaff re-import of `s`).

## 5. Hand off
- Update `ai/HANDOFF.md` / `ai/PROJECT_STATE.json` when state meaningfully changes (no secrets).
- Report to the owner in Japanese, short. Ask only for the items listed under "Still requires the owner" in `AGENTS.md`.

## Needs the owner (only these)
| Action | Why |
|---|---|
| Force-push / history rewrite on `main` | Irrecoverable |
| Deleting a repository | Irrecoverable |
| Production deploy (Vercel prod, store submission) | External effect |
| Making anything public (repo → public, Release, Pages, public hosting) | Exposure |
| Spending money, creating/widening credentials | Cost / security |
