# Audit model

## The one question

Hold one question through the whole audit:

> Can a zero-context agent complete a real task safely using only what the repository contains?

Never substitute file counts, heading completeness, or tidy Markdown for this judgement.

## The eight dimensions

### 1. Locating

- Does the root entry state the project's purpose and boundaries?
- Can a user's intent be mapped to a specific module or fact source?
- Is a repository-wide search required before knowing where to start?

### 2. Authority

- Does each class of dynamic fact have exactly one authoritative source?
- Do summary pages copy state that will drift?
- On conflict, is it stated which source wins?

### 3. Scope

- Does the workflow define the default scan and change scope?
- Can the agent avoid reading irrelevant history, modules, or external data?
- When the user narrows the scope, is there an explicit override rule?

### 4. Safety

- Are the fields that cannot be inferred listed?
- Do high-risk actions (state changes, releases, deletions, migrations) require confirmation?
- Do forbidden paths carry a guard rail close to the dangerous action, not only in the global rules?

### 5. Executability

- Does the workflow have inputs, outputs, steps, and acceptance?
- Can the template generate a complete object on its own?
- Can the agent produce a real result instead of restating the rules?

### 6. Verification

- Is there a command anyone can copy and run?
- Are the pass criteria, the capability boundary, and the failure handling stated?
- Does the documentation overstate what the check actually covers?

### 7. Evolution

- Are decision records separated from current facts?
- Has deprecated material become an unexecutable tombstone?
- When a directory or module changes, are references and maps updated with it?

### 8. Robustness

- Does an ordinary agent succeed?
- Does a lighter agent stay safe when it skips, reorders, or over-reads?
- Does a critical guard rail exist only in one entry that is easy to skip?

## Evidence requirements

Every P0 or P1 problem carries at least:

- The real task that triggered it.
- File path and line numbers, or command output.
- What the agent actually did, not what it plausibly would do.
- The concrete consequence.
- The layer where it should be solved.

With no evidence, mark it a hypothesis and change no structure.

## Grades

- **P0**: can cause an irreversible or expensive error.
- **P1**: the task cannot be completed independently, or requires guessing.
- **P2**: completable, but context, time, or output is wasted.
- **P3**: a pure expression preference.

Clear P0 before touching P1. P2 needs real cost evidence. Never expand documentation without limit just to kill every P3.

## Exit assignment

Every recommendation lands on one exit. Nothing is "without an exit".

- **Exit 1, build the eyes**: a check that catches the error on its own (lint, test, CI, read-only guard).
- **Exit 2, narrow the path**: the wrong option disappears from the default route (template, directory convention, scaffold, one blessed way).
- **Exit 3, human bookkeeping**: not mechanically verifiable, explicitly assigned to a human, naming the action it lands on.

The gate requires *an exit*, not *exit 1*. Forcing something unverifiable into a bad check backfires: it adds noise and manufactures a false sense of "verified". Record it under Exit 3.

## Suggested metrics

Set no universal hard threshold; record the change between baseline and remediation:

- Time and number of hops to the first correct fact file.
- The gap between files that must be read and files actually read.
- Share of irrelevant files read.
- Number of clarification questions asked up front.
- Number of changes proposed without evidence.
- Whether the agent can find the handling entry after a verification failure.
- Safe-pass rate for an ordinary agent and for a lighter agent.
