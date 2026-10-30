# Agent-ready architecture patterns

## Recommended patterns

### Intent routing

The root entry answers "where do I go to do X". It carries no detail. Local entries point on to workflows and fact files.

### Single source of truth

Dynamic state, configuration contracts, and business facts each have one home. Other documents link to it or generate from it, never hand-mirror it.

### Control plane separate from fact plane

- Control plane: entries, rules, workflows, templates, verification.
- Fact plane: code, configuration, business records, data.

Rules never masquerade as business facts, and a summary page never becomes a second fact store.

### Thin overview map

The overview states composition, the main path, and the extension points. Operating detail sits next to the module that owns it.

### Local guard rails

High-risk constraints (deletion, release, migration, secrets, production) appear near the entry where the action actually happens, in addition to the global rules.

### Explicit dynamic pointers

State such as "current version", "active migration", "objects pending sync" uses an explicit pointer with a stated rule for when it moves. Never let the agent guess from dates or file names.

### Complete templates

A template can generate a valid object with no historical sample. Unknown facts take one agreed empty state; never reconstruct them by copying an old file.

### Tombstone pages

A deprecated process keeps exactly four things:

1. The deprecated status.
2. The reason.
3. The current replacement entry.
4. What would have to be true to restore it.

Delete the old inputs, cadence, steps, and acceptance so nobody follows them.

### Mechanical gates

Deterministic problems belong to a script or CI, for example:

- Broken links and missing files.
- A directory map entry missing.
- A structural template missing.
- Generated documentation out of sync with its source.
- Forbidden directories or deprecated words reappearing.

A tool must state its coverage. Never call a local check a whole-repository consistency check.

## Signals that the directories need changing rather than the docs

- One directory holds content with different owners, lifecycles, or permission boundaries.
- Finishing a single task always crosses several unrelated directories.
- One file carries the entry, dynamic state, operating steps, and history at once.
- New content has no stable home, so its placement is guessed from naming habits.
- The prose explaining "why this lives here" is more complex than the directory itself.
- Several modules reference each other into a reading cycle.

In these cases propose a module split, an ownership change, or a dependency direction before deciding the documentation entry.

## Common anti-patterns

### README as the everything page

Everything piles into the root README, so every task must read a large amount of irrelevant material.

### Multiple current states

The current version, roadmap, or live process is hand-updated in several files. It drifts, given time.

### Search papering over a missing entry

An agent can find the answer by searching the whole repository; that does not make the repository maintainable. Search is the exception path, never the default navigation.

### Golden sample instead of template

"Copy the most recent similar file" propagates whatever structure history happened to have.

### Deprecated but fully intact

The top says "do not run" while the body still holds commands and steps; a weaker agent may still follow it.

### Testing only the strong agent

A strong model repairs documentation defects by reasoning. Include a lighter agent to test whether the repository itself supplies enough constraint.

### Forcing a framework to pass the audit

Never introduce spec-anchor, a directory layout, or a new tool just to use this skill. First prove the existing structure cannot meet the goal.
