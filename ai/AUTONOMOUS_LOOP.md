# Autonomous workflow — public s

Read [../AGENTS.md](../AGENTS.md) → **Operating policy v4 (2026-11-12)** for current scope and owner-only boundaries. Old v3 gates and handoff snapshots are historical. Read current Git/GitHub state instead of copied SHAs.

## Select and verify work
1. Prioritize the user's active task, then relevant failed CI or actual unresolved filter issues. Do not automatically execute old work queues or dormant workflows.
2. Determine which subscription paths or rule generators a change touches. `filter-profiles.json` defines generated lists; keep the existing public file paths and license headers.
3. For network-rule edits, run applicable tests, `python scripts/validate_lists.py`, `python scripts/generate_lists.py --check`, and `python scripts/check_subscription_contract.py --json`. Use actual engine checks when dependencies/environment permit. Do not label unavailable checks PASS.

## Branch, review and downstream
- Use a fresh branch and an appropriately scoped PR, not a direct push to `main`. Inspect PR CI, current HEAD and diff. A self-authored revertible PR may be squash-merged after required checks succeed; avoid force-push.
- After a public `s` merge, compare the pinned import in `faaff` if that repository is accessible: `python ai/reimport_s.py --s-repo ../s --ref origin/main --check-content` from its root. An excluded-only change does not need a downstream PR; imported-content changes require a reviewed private update.
- Helpers such as `/workspace/repos/tools/ai_task.sh`, pre-commit hooks and engine directories are optional; use a legitimate available alternative when absent. Do not block an unrelated task on a specific box or browser.
- Update [PROJECT_STATE.json](PROJECT_STATE.json) and [HANDOFF.md](HANDOFF.md) only for material changes. Report actual checks, public subscription impact, unknowns and commit/PR in the format appropriate to the current task; do not enforce a fixed reporting language.
- Owner-only approval boundaries are defined **only** in [../AGENTS.md](../AGENTS.md). Do not duplicate them here or revive historic stop gates.
