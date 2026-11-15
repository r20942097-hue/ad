# Project Context — r20942097-hue/ad (legacy s)

Public filter-list distribution repository (`r20942097-hue/ad`).

## Repository identity and compatibility

The active public repository is `r20942097-hue/ad`. The older names `s` and `faaff` occur in historical migration/import records and in the established raw subscription paths; they are not the current repository identity.

Public `raw.githubusercontent.com/r20942097-hue/s/main/` URLs remain an existing downstream compatibility contract. Do not change those URLs, generated filter metadata, profile scopes, or corresponding contract checks as part of a naming or documentation cleanup. A URL migration requires a separate compatibility plan and verification of actual subscribers and redirects.

## Architecture & Interfaces

- **Subscription URL contract**: [scripts/check_subscription_contract.py](../scripts/check_subscription_contract.py) enforces stable paths, license headers, and `! Subscription:` URLs.
- **Filter generation**: [filter-profiles.json](../filter-profiles.json) generates `ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, and `v2/strict.txt` via `python scripts/generate_lists.py --write`. Other root filter lists (`ad-ubo.txt`, `japanese-text-softener*.txt`, `twitch-custom-optional.txt`) are maintained directly.
- **Licenses & scope**: Root lists declare `CC0-1.0`; `v2/*.txt` declare `GPL-3.0-only`. This repository publishes browser filter lists; its product-specific rules do not impose global constraints on other projects.
- **Downstream hub**: Private `r20942097-hue/01` (legacy `faaff`) mirrors a pinned snapshot of this repository via `01/ai/imports/s.json` and proposes updates via `refresh-pinned-s.yml` PRs.

## Verification Entrypoints

- **All offline checks (1 command)**: `python scripts/verify.py` (`--list`, `--check <pattern>`).
- **Individual offline checks**:
  - `python -m unittest discover -s tests -p 'test_*.py' -v`
  - `python scripts/validate_lists.py`
  - `python scripts/generate_lists.py --check`
  - `python scripts/check_subscription_contract.py --json`
- **Optional engine / upstream checks (Node.js 26 Active LTS + first-time fetch)**:
  - `python scripts/prepare_engine.py --directory ../work/filter-engine`
  - `node scripts/check_engine.mjs --engine-dir ../work/filter-engine`
  - `python scripts/audit_upstream.py --cache ../work/upstream-audit --fetch --report ../work/upstream-audit.json`
- **CI workflows**: `.github/workflows/japanese-text-softener.yml`, `.github/workflows/codeql.yml`, and `.github/workflows/zizmor.yml`.
