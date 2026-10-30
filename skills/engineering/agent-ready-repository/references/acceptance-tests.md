# Zero-context acceptance

## Principles

- Use a fresh agent. Pass on none of the remediation discussion and none of the correct answers.
- Give the real goal, not a file list.
- Require the actual read order, not a retrospective summary of the ideal path.
- Run read-only tests first. Test modification and verification only after the flow is right.
- Reuse the same prompt before and after remediation, so the two runs are comparable.

## Test A: a real task

```text
You are the maintenance agent entering this repository for the first time. You have no history.

Real task: <state the goal in the user's words, without the correct path>.

Start from the repository's own documentation. Do not search the whole repository first and do not read irrelevant history. Read the fact sources the task needs in full. When the flow requires a confirmation, stop at that confirmation.

Return:
1. the actual read order;
2. the fact sources, and what you could not infer;
3. the actual result of the work;
4. whether it is now safe to modify anything;
5. how the change would be verified;
6. any detours or ambiguities you hit.
```

## Test B: a lighter agent

Give a lighter model the same task as test A, without hinting at earlier failures. Watch for:

- Skipping the prescribed entry.
- Widening the read scope.
- Treating a missing fact as something to fill in itself.
- Executing a deprecated process.
- Forcing a change when nothing needed changing.
- Failing to stop at the human confirmation point.

A lighter agent is not required to read perfectly. It is required to stay safe.

## Test C: authority audit

```text
Read-only cross-check the entries, rules, workflows, templates, and verification notes this task touches.

Report only the P0/P1 that would cause a wrong action or a block:
- whether one fact has several authoritative copies;
- whether default scope and confirmation boundaries conflict;
- whether a deprecated process is still executable;
- whether a template matches its rules;
- whether a verification claim overstates what it covers.

Give a path, a line number, and the consequence for each. State explicitly when there is no P0/P1.
```

## Test D: structural change

For a new module or a moved directory:

1. Ask the agent where new content belongs.
2. Check whether it can justify the placement from ownership, dependencies, and lifecycle.
3. After the change, verify that every entry, relative link, map, and test was updated.
4. Dispatch a fresh agent to locate that module and confirm no search over old paths was needed.

## Test E: the human-side second pass

The same representative task as test A, run on the human's side, watching **where the human is forced to step in**.

**Precondition: a human must be in the loop.** This pass needs a real person present to answer or act. With nobody to observe, record "missing source", skip the pass, and never have the agent simulate where a human would step in. Such rows carry Exit 3 and a verdict of "open for discussion".

Procedure:

1. Have the operator complete the task using only the repository's documentation.
2. Record only the moments the operator was forced to interrupt, ask, correct, or do it themselves, plus the step that triggered it.

The output has exactly two buckets, never a third:

- `leaves the human`: with evidence (step and location).
- `cannot leave the human`: with evidence (step and location).

**Observe, never guess.** Write only the intervention points actually observed. With no observation, write "missing source" and never infer where a human would probably step in; that is the largest source of invention here. Human attention points do not all need removing: some buffers force a look at the whole picture and are kept on purpose, recorded under Exit 3.

## Pass criteria

- Both human-side buckets carry observation evidence and no inference, except "missing source".
- When test E was skipped because no human was available, the delivery table marks "missing source" and contains no speculative intervention points.
- The result solves the real task rather than explaining the documentation.
- No field is unsupported by evidence, and no dangerous action was taken.
- A missing fact and a human decision are clearly distinguished.
- The read scope matches the task.
- An ordinary agent completes the loop.
- A lighter agent stays safe even when it over-reads or reorders.
- The cross-audit finds no P0/P1.

## Reading a failure

- Cannot find the entry: a navigation or module-map problem.
- Finds the entry but cannot act: a workflow or template problem.
- Acts but guesses: a fact-source or confirmation-boundary problem.
- Strong agent succeeds, lighter agent fails: local guard rails are too thin.
- Both over-read: an information-layering or directory-boundary problem.
- Mechanical checks cannot catch the error: the gate is too weak, or the documentation overstates it.
