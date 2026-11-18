# Feature

New or changed behaviour that lands in code. Open the skills in order; do not restate their criteria here.

1. Read `how` for the subsystem this touches. Skip when there is no existing code.
2. Read `grilling` when the product or structural call is not settled. Skip when it is. No implementation before the interview closes.
3. Read `domain-modeling` when terms or state do not line up. Skip when they do.
4. Read `compare-shapes` when two or more implementation shapes remain; switch to `arena` when a candidate deserves a whole attempt, or the pick needs another model family. Skip when the shape is already unique. The deliverable is the chosen shape, not production code.
5. Read `to-spec` when the agreement is not yet a matching spec under `.agents/notes/proposed/`. Skip when it is. The trade-offs in `prototypes/compare-shapes-*/decision.md` go into Implementation Decisions.
6. Read `codebase-design`. If it hands a major decision back to `to-spec`, land that first and return to this step until the public contract exists.
7. For non-trivial work read `architect` first: sketch types and signatures, then fill against the sketch; deviations get surfaced, not silently absorbed. Read `typescript-best-practices` when reading or editing `.ts`/`.tsx`. While implementing, read `principle-sequence-verifiable-units` and `principle-laziness-protocol`. Read `principle-model-the-domain` for stateful logic, or when branches and shape assumptions start repeating.
8. Read `principle-prove-it-works`, and run the seams the spec named.
9. Read `code-review` when the user asks, or when this diff is going in front of someone. Else skip.

When two steps write the same file, read `principle-separate-before-serializing-shared-state` first. Do not open `code-simplify`.

When this change reports a measured number in the reply or the PR body, read `principle-explain-the-number`.

Done when: the spec path, the contract, the check commands, and their output summaries are all in the reply.
