# Scope

Never silently expand to the whole repository.

## Resolve mode in this order

1. If the user named paths, a directory, a module, or “the X I just
   wrote” → **mode B**.
2. Else if they asked to map / assess / prioritize the **project** for
   cleanup, without naming a module → **mode C**.
3. Else → **mode A** (current diff).

A focus hint (“memory”, “naming”, “stop applying”) is not a path.
`apply=false` / “只评估不要改” / “提出意见” forces report-only after
reviews. “评估相关改动” is still mode A, not mode C.

## Resolve gear: residue vs cleanup

**Cleanup** when the user named a small scope and asked to tidy it
(“收干净”, “simplify this file”, “polish X”), **and** eligible source
files ≤ 12 and review size ≤ ~800 lines.

**Residue** when any of:

- Mode A or B eligible source files > 12 or review size > ~800 lines
- The user asked to evaluate / 评估 / 提出意见 on the current change
  without asking to tidy a named small scope
- The diff is clearly one feature landing (new protocol, many templates,
  tests + impl + docs together)

In residue gear, do not ingest the whole tree with four extract-helpers
lenses. Switch to residue even if mode is A. Mode B over the size cap:
do not four-lens the whole module; use residue, or split only if the
user named a subset and asked to 收干净 that subset.

## Residue means

Only look for leftovers after the landing, not “could new code be
shorter?”:

1. **Stale comments or docs** — code already moved on (previous slice’s
   comment still in place).
2. **Empty forwards** — a wrapper left by evolution that only calls one
   other function.
3. **Diverged copies** — this diff introduced or edited two copies that
   no longer match. Pre-existing dual tracks that this diff updated in
   lockstep are **not** residue.

Treat as **optional later**, never must-fix with the feature:

- Identical repetition in newly written code (same `replace`, same
  check listed N times). That is often required explicitness.

Never suggest in residue:

- Extracting newly written protocol / validation / prompt steps into
  helpers or generators
- Editing tests to share fixtures
- Changing error strings
- Merging directories or adding abstractions
- Cosmetic three-line refactors (`is_some()` twice, local style)

## Mode A — diff

- `git status --short` for untracked files.
- `git diff HEAD` for staged + unstaged tracked changes.
- If that diff is empty and `HEAD~1` exists, use `git diff HEAD~1..HEAD`.
- Append untracked files as synthetic additions (full contents).
- Eligible: changed source, comments, docs. Exclude generated/vendor/
  lockfiles/snapshots/migrations unless requested.
- Count eligible **source** files (not docs/lockfiles) for the gear cap.
- Stop if nothing eligible remains.

## Mode B — module

- Unit = module source + its tests.
- Grep public entry points and external call sites to judge boundaries.
  Do not edit callers unless a finding only switches them to an existing
  helper inside scope.
- Over the size cap → residue (see above), unless the user named a
  smaller subset to 收干净.
- Exclude the same generated/vendor set as mode A.

## Mode C — project map (read-only)

- Identify modules (directories, packages, obvious aggregates).
- Light hotspot scan only: duplication, deep nesting, oversized public
  API, wrong-layer special cases.
- Output a table: module | why simplify | main lens | risk | next step.
- Next step is “run mode B on X”, never “rewrite the repo”.
- Stop. No edits.

## Hard stops

- Empty eligible set → say so and stop.
- User named a module but resolved paths escape that module without
  being call-site references → drop the escape, do not follow it.
