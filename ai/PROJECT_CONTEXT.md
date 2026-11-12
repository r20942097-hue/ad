# Current repository context — public ad filters (not global instructions)

This file describes technical interfaces and verification entrypoints for the active public repository `r20942097-hue/ad`. It is not a standing artifact-protection policy. Recheck the state when a task requires changing the product.

## Repository identity and compatibility

The active public repository is `r20942097-hue/ad`. The older names `s` and `faaff` occur in historical migration/import records and in the established raw subscription paths. They are not the current repository identity.

The `s/main` raw URLs remain an existing downstream compatibility contract. Do not change those URLs, generated filter metadata, profile scopes, or corresponding contract checks as part of a naming/documentation cleanup. A URL migration requires a separate compatibility plan and verification of actual subscribers and redirects.

## Current implementation
- `filter-profiles.json` is the generator input for `ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, and `v2/strict.txt`; [scripts/generate_lists.py](../scripts/generate_lists.py) checks generated output. Other lists have separate source ownership.
- Current list syntax, license, and subscription metadata are declared in the list headers and checked by the repository validators.
- This repository publishes browser filter lists. It is not an addon source or build-artifact repository; its product-specific rules do not impose global constraints on other projects.

## Verification entrypoints
- `python -m unittest discover -s tests -p 'test_*.py' -v`
- `python scripts/validate_lists.py`
- `python scripts/generate_lists.py --check`
- `python scripts/check_subscription_contract.py --json`
- `.github/workflows/japanese-text-softener.yml`: filter validation and engine checks.
- `.github/workflows/codeql.yml`: security scan when supported and enabled.

## Evidence boundaries
- Current Git tree, actual CI logs, and a particular validation run determine current status. Historical product versions, STOP/NO_GO labels, fixed counts, and old Drive policies do not carry forward as global commands.
- Treat old repository names in historic notes as migration context. They are not current instructions unless a task explicitly requires migration compatibility work.
