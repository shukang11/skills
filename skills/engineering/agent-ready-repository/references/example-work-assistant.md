# Case: a work-assistant repository

## First symptoms

The repository already had a root entry, directory READMEs, workflows, and check scripts, yet a zero-context agent still:

- Could not tell which weekly record was the current sync target.
- Read the template, the whole DSL, the history, and the summary table for an ordinary sync.
- Chained a normal sync together with a milestone inspection.
- Kept asking about the default scope across several versions and hotfixes.
- Knew that "verification" existed but could not find the full command and the pass criteria.
- Could enter an old process belonging to a directory that had already been deleted.

## Root causes

- Current state was written in prose, with no explicit working pointer.
- The onboarding order and workflow state were repeated in several places.
- The workflow had no default scope and no condition for promoting to the summary table.
- The template covered only some sections, so a historical file had to be consulted.
- The deprecated process kept its full executable body.
- A check tool existed, but no operator entry aimed at a maintainer.

## Remediation in rounds

### Round one: safety and authority

- The root entry became the single source for onboarding order.
- Workflow validity is read only from the index.
- Forbidden directories gained guard rails near the root rules, the index, and the executing entry.
- Dynamic state became an explicit "current sync target" pointer with a stated rule for when it moves.

### Round two: closing the workflow

- Inputs, outputs, states, default scope, and confirmation points were stated.
- A week touching both the main version and a hotfix defaults to listing both.
- The summary table is read only when a package number, date, or person-day is actually written.
- A gap reminder no longer expands into a data-filling task.

### Round three: templates and deprecated material

- The new-version template became a complete skeleton that can be copied on its own.
- Unknown fields share one value: "to be supplied".
- The deprecated process shrank to a tombstone page with the old steps deleted.
- The verification command, pass criteria, and false-positive handling moved into one tool entry.

## What acceptance found

An ordinary agent completed locating, recommending, confirming, and verifying. The lighter agent reordered and over-read, but:

- It invented no numbers.
- It executed no deprecated process.
- It forced no change when nothing differed.
- It stopped correctly at the human confirmation point.

So the acceptance question is not "did it read perfectly" but "was imperfect reading still safe".

## Transferable conclusions

1. File count is not the metric; a closed task loop is.
2. Guard rails belong near the dangerous action, not only in the root entry.
3. Dynamic facts keep exactly one authoritative source.
4. When the explanations keep growing, check the directory and module boundaries.
5. A strong agent tests completability; a lighter agent tests the repository's own robustness.
