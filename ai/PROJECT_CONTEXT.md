# Current repository context — public s filters (not global instructions)

This file describes today's technical interfaces and validation entrypoints. It is not a standing artifact-protection policy. Recheck the state when the user's task requires changing the product.

## Existing interfaces and implementation
- `s/main` currently publishes browser filter subscriptions over public `raw.githubusercontent.com` paths. Changes to those paths can affect downstream subscribers; [scripts/check_subscription_contract.py](../scripts/check_subscription_contract.py) reports the present compatibility contract.
- `filter-profiles.json` is the generator input for `ad.txt`, `tracking.txt`, `v2/ad.txt`, `v2/tracking.txt`, and `v2/strict.txt`; [scripts/generate_lists.py](../scripts/generate_lists.py) checks the generated output. Other filter lists have separate source ownership.
- Current list/license information is in the list headers, not in the general agent policy. Compatibility or migration decisions follow the specific user request and verified integration effects.
- Private `r20942097-hue/faaff` tracks an `s` source snapshot through its `ai/imports/s.json` manifest. Its `refresh-pinned-s.yml` workflow checks weekly and proposes a private PR only if imported content or exclusions changed; it does not automatically merge.
- The public `s` repo is not an addon source or build-artifact repository. Its contents should be evaluated as this product's current implementation, not as a global ban on developing other projects.

## Verification entrypoints
- `python -m unittest discover -s tests -p 'test_*.py' -v`
- `python scripts/validate_lists.py`
- `python scripts/generate_lists.py --check`
- `python scripts/check_subscription_contract.py --json`
- `.github/workflows/japanese-text-softener.yml`: public filter validation/engine jobs and agent-state guard.
- `.github/workflows/codeql.yml`: security scan if available.

## Evidence boundaries
- The current Git tree, actual CI logs and a particular validation run determine the status of that task. Historical product versions, STOP/NO_GO labels, fixed counts and old Drive policies do not carry forward as global commands.
