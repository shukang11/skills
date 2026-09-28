# Contract

Preserve observable behavior: outputs, errors, ordering, side effects,
public/exported APIs, serialized shapes, CLI flags, env vars, schemas,
config, and test expectations.

Clarity beats fewer lines. Nested ternaries, dense one-liners, and
helpers that only rename `n * n` are not simplifications.

Match the repo. Read `AGENTS.md`, `CLAUDE.md`, formatter/linter config,
decision notes, and neighboring code before preferring a generic idiom.
Local convention wins. Numbered comments that track an acceptance
checklist (①, ②, step lists tied to a decision) are WHY — keep them.
Repeated explicit protocol checks in newly landed code are often the
spec, not a smell.

Do not:

- Hunt correctness bugs (that is a different skill)
- Broaden into unrelated files
- Add dependencies, frameworks, or speculative abstraction
- Change generated files, vendor, lockfiles, snapshots, or migrations
  unless the user named them
- Modify tests to share helpers or to make a refactor pass
- Change error strings to make I/O “simpler”
- Treat a feature landing as a request to extract helpers

A simplification is done only when there is evidence behavior held:
targeted tests, types, lint, or an explicit statement of what was not run.
