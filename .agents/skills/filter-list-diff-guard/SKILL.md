---
name: filter-list-diff-guard
description: Compare old vs new generated ad-block filter lists to catch unintended rule drops, duplicates, or overly broad blocking rules. Use when editing filter-profiles.json, generator scripts, or ad-block filter lists.
---

# Filter List Differential Guard

1. Capture the current generated filter output as a baseline before modifying `filter-profiles.json`, generator scripts, or source rules.
2. After changes, run `python -B scripts/generate_lists.py --write` (using `C:\Users\vanro\AppData\Local\Programs\Python\Python315\python.exe -B` if `python` is not on `PATH`) and diff old vs new outputs (line counts, added rules, removed rules, duplicate count).
3. Flag any overly broad wildcard/domain rule or unexpected deletion for explicit human approval before committing.
4. Run `python -B scripts/verify.py` and confirm zero secrets/credentials/tokens and zero trailing whitespace on all modified files.
