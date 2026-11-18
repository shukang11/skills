# Refactor

External behaviour unchanged; structure only.

1. Read `how` for the subsystem being moved.
2. Reuse the existing public contract. Read `codebase-design` when the move changes a module boundary or the contract is missing.
3. Run the existing check for the behaviour being preserved before moving it. Keep the input and command fixed. Add a focused check only when the affected behaviour has no usable coverage.
4. Read `principle-sequence-verifiable-units` and `principle-laziness-protocol`, then move.
5. Read `principle-prove-it-works`. The check after the move is the same check as before it.
6. Read `principle-minimize-reader-load`. Show the concrete trace or state ownership the move simplified. If the structural goal is unmet, revise or remove only this task's edits.

When behaviour has to change, switch to [bug-fix.md](bug-fix.md) or [feature.md](feature.md) and say so. Do not open `code-simplify` unless the user separately asks for cleanup.

Done when: the same check ran before and after the move against identified inputs, and both summaries are in the reply. Name the structural improvement and any uncovered behaviour. An unchanged pre-existing failure is a stated limit, not a passing check.
