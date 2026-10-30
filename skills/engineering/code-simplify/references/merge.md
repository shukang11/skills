# Merge and apply

Parse each reviewer's JSON. If one block fails to parse, log it and
continue. Repair obviously truncated strings when intent is clear.

Group by `(file, old_string)`.

## Drop before the user ever sees a list

These are discarded. Count them (`not doing / discarded: N`). Do **not** put
them in follow this change or optional later:

- `risk: behavior` or `risk: scope-creep`
- Findings that would edit tests, fixtures, or error / missing / empty
  strings
- Pre-existing dual copies this diff did not diverge
- Edge-case correctness (two algorithms that current templates never
  hit) — that is bug-hunting, not simplify
- Efficiency findings that miss the efficiency threshold
- Structure / altitude except empty pass-through forwards
- Three-line cosmetics in **residue** gear
- Extracting newly written protocol steps in **residue** gear

If the user later asks “what did you throw away?”, list the discards in
an appendix. Default: name the count only.

## Keep and classify

1. Identical or equivalent `new_string` → keep higher confidence; if
   tied, quality > reuse > efficiency > structure.
2. Different `new_string`: pick the variant that preserves behavior,
   then clarity, then house conventions. If principles do not decide,
   discard both (count them).
3. Overlapping regions: prefer the principle-aligned span; if unsure,
   discard both.
4. Sort any edits you will apply top-to-bottom per file. Re-read before
   each apply. If `old_string` no longer matches, skip as subsumed.
5. Never ask the user mid-run.

User-facing buckets (not Applied / Not applied):

| Bucket | What belongs |
|---|---|
| Follow this change | Cleanup gear + user wants edits: high-confidence, in-scope, behavior-preserving residue or tidy-ups. Stale comments that are now false. Residue gear + report-only: almost always empty. |
| Optional later | Identical new-code duplication; empty forwards; diverged copies that are safe but not worth this commit; stale comments the user did not ask to fix now. |
| Not doing / discarded | Everything in “Drop before the user ever sees a list”. |

`kind` from reviewers, when present:

- `stale-comment` → follow this change only in cleanup-with-apply; else optional later
- `empty-forward` → optional later (never blocks a merge)
- `diverged-copy` → optional later, or follow this change if cleanup gear, tiny, `risk: safe`
- `identical-dup` → optional later only
- `other` → discard in residue; allow in cleanup if it still passes contract

## Apply policy

- Mode C: apply nothing.
- apply=false / evaluate / give opinions: apply nothing; still fill the verdict
  report.
- Residue gear: apply nothing unless the user explicitly asked to fix
  leftover comments / empty forwards **now**. Even then, do not extract
  protocol helpers or touch tests.
- Cleanup gear with apply: high-confidence, in-scope, behavior-preserving
  reuse / quality / efficiency only. Structure only for empty forwards.

The verdict does not block a merge unless the user treated this run as a merge gate and
a follow-this-change item remains unfixed after an apply they requested.
Simplify does not block merges over optional hygiene.
