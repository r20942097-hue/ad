# Repository Instructions — ad (legacy identifier: s)

> Canonical instruction file for `r20942097-hue/ad`. [CLAUDE.md](CLAUDE.md), [.cursor/rules/agents.mdc](.cursor/rules/agents.mdc), and [.github/copilot-instructions.md](.github/copilot-instructions.md) are thin entrypoints referencing this file. Keep shared rules here.

## 1. Quick Start (Vibe Coding & Verification)

- Run all offline checks in one command:
  ```sh
  python scripts/verify.py
  ```
  Useful flags: `python scripts/verify.py --list`, `python scripts/verify.py --check <pattern>`.
- Regenerate derived filter lists after editing `filter-profiles.json`:
  ```sh
  python scripts/generate_lists.py --write
  ```
- Technical context & engine commands: [ai/PROJECT_CONTEXT.md](ai/PROJECT_CONTEXT.md), [ai/PROJECT_STATE.json](ai/PROJECT_STATE.json).

## 2. Editable Sources vs Generated Outputs

- **Editable paths**:
  - `filter-profiles.json` — canonical generator source for `ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, and `v2/strict.txt`.
  - `ad-ubo.txt`, `japanese-text-softener.txt`, `japanese-text-softener-deep.txt`, `twitch-custom-optional.txt` — directly maintained filter files.
  - `scripts/`, `tests/`, `verification/` — generator, validation, contract, upstream audit, and engine verification scripts/locks.
- **Generated / compatibility constraints**:
  - Never hand-edit generated files (`ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, `v2/strict.txt`) without running `python scripts/generate_lists.py --write`.
  - Preserve existing subscription paths and `https://raw.githubusercontent.com/r20942097-hue/s/main/` URL compatibility headers (`python scripts/check_subscription_contract.py --json`).

## 3. Working Rules

- Verify facts directly from current source, git state, and tests rather than historical assumptions.
- Act directly on clearly scoped filter/tooling tasks without unnecessary confirmation turns; keep changes minimal, deterministic, and passing `python scripts/verify.py`.
- Never commit secrets, credentials, tokens, personal data, binary executables, or tracked `.zip` / `.7z` archives (rejected by CI).
- Ask before irreversible or external-impact actions: force-push or history rewrite on `main`, deleting repositories, widening credentials, or breaking live public subscription URLs.
