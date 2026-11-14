# Engineering Verification Loop

Follow [../AGENTS.md](../AGENTS.md) for working boundaries and [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for repository interfaces.

1. Inspect the request, `filter-profiles.json`, target filter/script files, and live Git/GitHub state.
2. Make a minimal, focused edit on a branch. If `filter-profiles.json` changed, run `python scripts/generate_lists.py --write`.
3. Run `python scripts/verify.py` (plus engine checks in CI or locally with Node.js 24 when modifying rules or engine scripts) and confirm all checks pass before merging.
