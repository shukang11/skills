# Implementation and re-verification

> This skill itself stops at recommendations and executes no remediation. When the user accepts the recommendations and moves to implementation separately, follow this order and this checklist.

## Step six: implement in small rounds

Split the work into rounds in this order:

1. Remove P0 conflicts and dangerous paths.
2. Converge the authoritative sources and the dynamic pointers.
3. Fill in task entries, workflow defaults, and human confirmation boundaries.
4. Complete the templates, the directory map, and the verification notes.
5. Delete duplicated explanations and quarantine deprecated content.
6. Last, handle expression problems that do not affect work.

Each round solves one class of problem. Run the project's existing verification right after each change. Never widen the scope on the way.

## Step seven: re-verify

After implementation, re-run the same real tasks as the baseline and add a cross-audit:

- Can an ordinary agent produce the result on its own?
- Does a lighter agent still avoid dangerous actions when it reorders or over-reads?
- Can the auditing agent find authoritative-source conflicts and overstated verification?
- Can the agent tell a missing fact apart from a decision only a human can make?
- Can the agent correctly choose to change nothing?

The prompts and metrics are in [acceptance-tests.md](acceptance-tests.md).

## Done when

All of these hold at once:

- The agent reaches the right fact source from the task intent without searching the whole repository first.
- Each class of dynamic fact has exactly one authoritative source.
- Fields that cannot be inferred, default behaviour, and human confirmation boundaries are stated.
- Deprecated content cannot be followed.
- A new object can be created without peeking at historical files to assemble it.
- After a change, the verification command, the pass criteria, and the failure handling are all locatable.
- An ordinary agent completes the real task.
- A lighter agent, even imperfect, produces no dangerous change.
