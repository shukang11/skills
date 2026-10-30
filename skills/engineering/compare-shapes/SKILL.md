---
name: compare-shapes
description: "Lay at least two shapes for the same task side by side, pick one base against criteria written down first, then graft in what the losers were worth. Use when the shape is not settled and one attempt would lock in the wrong one."
disable-model-invocation: true
argument-hint: "the artifact being compared, such as a module contract or a state model"
---

# Compare shapes

Stop the first shape you write from becoming the final shape. Stop when the comparison is done; do not carry the candidates into production.

Hand-built, no parallelism, no full attempts. When a candidate deserves a whole attempt, or the pick needs a second opinion from another model family, use `arena` instead.

## Criteria

- Write down the artifact and 3 to 6 checkable criteria before you start. Criteria describe an observable difference, never "better".
- Fewer than two candidates: stop. When the shape is already unique, hand the work back to `codebase-design` or `prototype`.
- One directory per candidate: `prototypes/compare-shapes-<slug>/candidate-<n>/`. A candidate written later never edits an earlier candidate's directory.
- Write the candidates one at a time, then compare. Spawning one subagent per candidate to run full attempts is not this skill; that is `arena`.
- Score criterion by criterion, never on overall feel. Two candidates tied: take the smaller public surface as the base.
- Grafting means rewriting what is worth keeping into the base's one model. Never paste two drafts together. When the candidates converged on one shape, record the convergence and graft nothing.
- Candidates that contradict each other so badly you cannot score them mean the criteria were unclear. Rewrite the criteria and run another round; never average the contradiction away.

## Done when

- `prototypes/compare-shapes-<slug>/decision.md` names the base, the score per criterion, what was grafted in, and what was rejected.
- `.agents/notes/` is untouched. The trade-offs go to `to-spec`, which writes them into Implementation Decisions.

## Output

The chosen artifact, plus `decision.md`.
