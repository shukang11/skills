# Projects already wired into spec-anchor

This file answers: when the project already uses spec-anchor, what does the audit check more of, and what does it stop recommending. "Wired in" means the project root has `site.config.yaml`; the spec-anchor CLI also locates the project root by that file.

## What `init` already laid down, so stop recommending it

`spec-anchor init` already lays down: the evolution principles, the skill entry, fix-commit rules, the "project checks" section next to the anchor block, and the `docs/` layering. `spec-anchor skills install` already installed the bundled skills. Stop recommending "write a principles doc" or "add a fix-commit rule". What to check is whether these are actually connected; every row below that fails becomes one problem row.

| What to check | How | Category when it fails |
|---|---|---|
| Is the anchor block there | Does the root `AGENTS.md` contain `<!-- spec-anchor:docs-framework -->` on its own line. When it is absent the project may have written its own on purpose: mark the verdict "open for discussion" rather than a defect, and check the next two rows against its own equivalent section | Principle 6 |
| Is the anchor block stale | Run `spec-anchor init --no-skills` in a temporary directory and diff the block between `<!-- spec-anchor:docs-framework -->` and `<!-- /spec-anchor:docs-framework -->`. The block does not refresh itself | Principle 6 |
| Is the project-checks section filled in | The "project checks" section in the root `AGENTS.md`, outside the anchor block: still `<command>` placeholders, or missing entirely | Principle 2 |
| Will those commands actually run next time | Hook directory from `git config core.hooksPath`, else `.git/hooks/`. Read the executable hooks and see whether they run that command set. A `commit-msg` hook that only checks the message does not count. Then check whether CI runs the same set | Principle 2 |
| Are the bundled skills current and unmodified | `spec-anchor skills check` | Principle 6 |
| Does the docs gate pass | `spec-anchor verify --verbose` | Principle 1 |
| Do fix commits carry evidence | First look for a hook enforcing it (a `commit-msg` hook that rejects a `fix` commit carrying neither a test nor a `Tested:` trailer). If one exists, record it as connected, then confirm `core.hooksPath` really points at it. Otherwise sample recent commits whose subject starts with `fix` and see whether they carry a test change or a `Tested:` trailer | Principle 1 |

## Aligning categories with the evolution principles

A problem that violates an evolution principle starts its Problem cell with "Principle N", the same wording `code-review` and the periodic review use. The principle texts and their test questions are in `.agents/skills/spec-anchor/references/evolution-principles.md`. A problem matching no principle is described plainly; never force it into one.

## Where exits land

- After an Exit 1 is adopted, the command goes into the "project checks" section. That section is the single place the project declares the commands that must be green before a commit.
- Exit 3 gates prefer the three from principle 7: deciding intent, merge review, cutting a version.
