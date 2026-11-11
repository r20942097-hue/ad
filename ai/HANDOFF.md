# HANDOFF — next agent (2026-11-12)

Follow [`AGENTS.md`](../AGENTS.md) → Operating policy v3 (2026-11-04). Drive copy: `00_AI運用ルール_v3_2026-11-04`. There are no standing P0 / PUBLICATION_HOLD / NO_NEW_INTERNAL_PUSH gates. Older wording in git history is not binding.

## Current state

- `s` stays **public** so anonymous `https://raw.githubusercontent.com/r20942097-hue/s/main/<file>` subscriptions keep working. Do not rename, move, or delete those paths (including `v2/`).
- Read the live `s/main` HEAD and CI state from Git/GitHub (`git rev-parse origin/main` after fetch). Do not duplicate a commit SHA in this handoff or infer current status from historical PR numbers. The published subscription files are protected by `scripts/check_subscription_contract.py`.
- Workflow: `/workspace/repos/tools/ai_task.sh s start <slug>` then `ship "<title>"`. That creates `ai/<YYYYMMDD>-<slug>`, opens a PR, waits for CI, and squash-merges when green and revertible. Never push directly to `main`. Never force-push.
- `faaff` checks the public `s/main` source weekly and proposes a private sync PR only when imported content changes; it never auto-merges. For urgent changes, run `python ai/reimport_s.py --s-repo ../s --ref origin/main --check-content` from the faaff clone, then refresh and submit a PR only if the result is `CHANGED`. Review exact excluded paths in `faaff/ai/imports/s.json`; excluded-only changes do not require an import.

## Do not revive

- Closed s#11 (`ci: GPT1 read-only cross-platform workspace preflight`) and the disabled GitHub workflow **GPT1 workspace preflight**. It asserted the old gates as active. Subscription path/header protection already lives on main via #21.
- Other disabled leftover workflows not on main: Validate v2 filters, GPT1 Actions lock pilot, Filter Python 3.14/3.15 compatibility.

## Open items

See `PROJECT_STATE.json` `open_items`. The remaining owner-only item is the GitHub Support cache purge for pre-rewrite ZIP blobs. LICENSE / wiki / leftover disabled workflow registrations are low priority and must not break subscription URLs.

Machine-readable state: [`PROJECT_STATE.json`](PROJECT_STATE.json). Loop: [`AUTONOMOUS_LOOP.md`](AUTONOMOUS_LOOP.md).
