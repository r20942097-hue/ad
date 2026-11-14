# Current repository context — public ad filters (legacy s; not global instructions)

This file describes technical interfaces and validation entrypoints **as observed**, not live GitHub status or a standing artifact-protection policy. Recheck the source and present task before changing the product.

## Existing interfaces and implementation
- [`r20942097-hue/ad`](https://github.com/r20942097-hue/ad) is the current public filter-source repository (legacy name `s`). Existing `raw.githubusercontent.com/r20942097-hue/s/main/` subscription URLs remain compatibility interfaces and must not be casually renamed. [scripts/check_subscription_contract.py](../scripts/check_subscription_contract.py) validates the actual URL contract; query current GitHub for the live HEAD.
- `filter-profiles.json` is the generator input for `ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, and `v2/strict.txt`; [scripts/generate_lists.py](../scripts/generate_lists.py) checks the generated output. Other filter lists have separate source ownership.
- Current list/license information is in the list headers, not in the general agent policy. Compatibility or migration decisions follow the specific user request and verified integration effects.
- Private [`r20942097-hue/01`](https://github.com/r20942097-hue/01) (legacy `faaff`) tracks an `s`-identified pinned snapshot through its `ai/imports/s.json` manifest. Its `refresh-pinned-s.yml` checks periodically and can propose a separate PR when imported content changes; inspect the live workflow and manifest instead of assuming an automatic merge or a current commit from this description.
- This public `ad` repository is a filter-list product, not the runtime source of unrelated addons. Its current content and tests are evidence for this product only; they do not establish global restrictions on other projects.

## Verification entrypoints
- `python -m unittest discover -s tests -p 'test_*.py' -v`
- `python scripts/validate_lists.py`
- `python scripts/generate_lists.py --check`
- `python scripts/check_subscription_contract.py --json`
- `.github/workflows/japanese-text-softener.yml`: public filter validation/engine jobs and agent-state guard.
- `.github/workflows/codeql.yml`: security scan if available.

## Evidence boundaries
- The current Git tree, actual CI logs and a particular validation run determine the status of that task. Historical product versions, STOP/NO_GO labels, fixed counts and old Drive policies do not carry forward as global commands.
