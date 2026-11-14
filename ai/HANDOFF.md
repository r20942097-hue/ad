# Handoff

Follow [../AGENTS.md](../AGENTS.md) and [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Current state

- Read the active branch, HEAD commit, PR, and CI status directly from Git/GitHub (`git status -sb`, `git rev-parse HEAD`); do not store live commit SHAs here.

## Verification

- Run `python scripts/verify.py` (and `python scripts/generate_lists.py --write` first when modifying `filter-profiles.json`). Optional loop: [AUTONOMOUS_LOOP.md](AUTONOMOUS_LOOP.md).
