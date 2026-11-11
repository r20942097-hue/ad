# HANDOFF — next agent (2026-11-12)

Follow [`AGENTS.md`](../AGENTS.md) → Operating policy v4 (2026-11-12). The v3 Drive copy and older gate names (P0 / PUBLICATION_HOLD / NO_NEW_INTERNAL_PUSH) are historical, not current approval requirements.

## Current state

- `s` stays **public** so anonymous `https://raw.githubusercontent.com/r20942097-hue/s/main/<file>` subscriptions keep working. Do not rename, move, or delete those paths (including `v2/`).
- Read the live `s/main` HEAD and CI state from Git/GitHub (`git rev-parse origin/main` after fetch). Do not duplicate a commit SHA in this handoff or infer current status from historical PR numbers. The published subscription files are protected by `scripts/check_subscription_contract.py`.
- Use a fresh branch, scoped PR and relevant verified CI. Box-specific `/workspace/...` scripts are optional, not required. Never push directly to `main` or force-push.
- `faaff` checks the public `s/main` source weekly and proposes a private sync PR only when imported content changes; it never auto-merges. For urgent changes, run `python ai/reimport_s.py --s-repo ../s --ref origin/main --check-content` from the faaff clone, then refresh and submit a PR only if the result is `CHANGED`. Review exact excluded paths in `faaff/ai/imports/s.json`; excluded-only changes do not require an import.

## Do not revive

- Closed s#11 (`ci: GPT1 read-only cross-platform workspace preflight`) and the disabled GitHub workflow **GPT1 workspace preflight**. It asserted the old gates as active. Subscription path/header protection already lives on main via #21.
- Other disabled leftover workflows not on main: Validate v2 filters, GPT1 Actions lock pilot, Filter Python 3.14/3.15 compatibility.

## Open items

See `PROJECT_STATE.json` `open_items`. The remaining owner-only assessment is whether the pre-rewrite ZIP content qualifies as sensitive data for a GitHub Support purge. GitHub does not purge non-sensitive content on request; this is NOT GUARANTEED and should not block routine development. LICENSE, wiki settings and disabled workflow registrations are archived non-actionable notes, not tasks to execute without a relevant request; subscription URLs remain protected.

Machine-readable state: [`PROJECT_STATE.json`](PROJECT_STATE.json). Loop: [`AUTONOMOUS_LOOP.md`](AUTONOMOUS_LOOP.md).
