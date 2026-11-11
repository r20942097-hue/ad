# Optional engineering loop

[AGENTS.md](../AGENTS.md) contains general guidance. These are optional task steps, not another policy or an automatic work queue.

1. Read the current request and affected source/tests. Consult [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) only for observed technical facts and available checks that relate to the task.
2. Compare relevant current Git/GitHub state, test evidence and dependencies with the intended change.
3. Make a focused, reviewable change on an isolated branch, run applicable tests and inspect actual CI results.
4. Before merging a self-authored reversible PR, verify the current head, mergeability and all relevant required checks.
5. Update [PROJECT_STATE.json](PROJECT_STATE.json) and [HANDOFF.md](HANDOFF.md) only for material new information; do not copy live SHAs or historical no-go status as active instructions.

No fixed model/effort, reporting language, tool, environment path, test count, asset rule, or publication verdict is defined here. Product-specific facts are in the project context, not the shared rules.
