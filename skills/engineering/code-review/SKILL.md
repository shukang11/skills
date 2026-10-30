---
name: code-review
description: "Review the diff between HEAD and a fixed point along two axes: Standards (does the code follow this repo's documented standards and avoid classic smells?) and Spec (does it faithfully implement what the spec asked for?). Reports the axes separately; never reranks them against each other."
disable-model-invocation: true
argument-hint: "which diff, and the fixed point"
---

# Code Review

Two independent axes over the diff between `HEAD` and the fixed point the user supplies:

- **Standards**: does the code follow this project's documented standards, and is it free of classic smells?
- **Spec**: does it faithfully implement the behaviour and acceptance criteria the spec asked for?

Review the axes independently and report them in separate sections. Never let one axis mask or outrank the other.

## Process

### 1. Pin the fixed point

- Take the fixed point the user gave (`main`, a branch, a tag, `HEAD~5`, a SHA). If none was given, ask.
- Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Note the commit list with `git log <fixed-point>..HEAD --oneline`.
- Confirm the ref resolves and the diff is non-empty before going further. A bad ref or an empty diff fails here, not halfway through the review.

### 2. Find the spec

In this order:

1. A spec under `.agents/notes/proposed/` or `.agents/notes/` that matches this change.
2. A spec or requirements doc under `docs/`.
3. A path the user passed in the argument.
4. Nothing found: say "no spec available" and run the Standards axis alone.

### 3. Find the standards sources

Stack these; later entries do not replace earlier ones.

1. If the project has `.agents/skills/spec-anchor/references/evolution-principles.md`, check the diff against each of the seven evolution principles. Name the violated one as "principle N" in the finding.
2. The project root `AGENTS.md` implementation rules and forbidden zones, plus any coding-standards docs (`CODING_STANDARDS.md`, `CONTRIBUTING.md`).
3. Whatever those leave uncovered falls back to the Fowler smell baseline below.

Two rules bind the baseline:

- **The repo overrides.** A documented project standard always wins. Where it endorses something the baseline would flag, drop the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Skip anything tooling already enforces.

Match each smell against the diff: what it is → how to fix it.

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together, a type wanting to be born. → bundle them into one type and pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same switch or if-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. → gather what changes together into one module.
- **Divergent Change**: one file or module gets edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Behaviour evidence (only when the range contains production code changes)

The diff alone cannot tell "a test pins this change" from "the test went green along with it". The script checks out the fixed point in a temporary worktree, overlays only the test-side files, and runs the suite twice, so red and green do the talking.

```bash
node .agents/skills/code-review/scripts/fix-proof.mjs \
  --range <fixed-point>..HEAD \
  --cmd '<test command per file, containing {files}>' \
  --setup '<install command>'
```

- `{files}` is replaced with the space-separated, quoted test files. No `{files}` in the command: it does not run.
- Add `--lockfile <path>` when the range diff touches exactly one lockfile; dependencies are reinstalled only when that blob changed.
- It recognises JS/TS, Go, Python, Rust, Java, and Kotlin test files by default. For anything else, replace the whole rule with `--tests '<regex>'`.
- Output containing "无法计算" (cannot compute) means the script gave up: hand it to the human and stop. Never write that up as "no test changes".
- The per-commit verdict names differ from the range verdict names. Do not interchange them.

Verdict → what goes in the report:

| Verdict | Report |
|---|---|
| `anchor red, HEAD green` | a test pins this change; no separate finding |
| `new test already green at anchor`, `changed test already green at anchor` | `[Missing]`: the change has no regression evidence |
| `no test file changes` | `[Missing]`, and only when the range really does change production code. It says the test files did not change, not that existing tests cover the change |
| `existing assertions deleted or edited` | `[Drift]`: the criterion itself was changed. Quote the `-` lines from `git diff <anchor> HEAD -- <file>` and hand it to the human |
| `load failure` | `[Missing]`, note says "reproduction not proven" |
| `HEAD not green`, `timeout`, `environment failure` | `[Missing]`, with the note line |

The note line can be any line from the stack, such as `name: 'AssertionError'`. The criterion is the verdict, not the note.

### 5. Report both axes, separately

```markdown
## Standards Review (conventions and architecture quality)
- [Hard / Heuristic] file:line - the violation or smell, with the fix you suggest.

## Spec Review (fidelity to the requirement)
- [Missing / Drift / Scope-Creep] against the spec line: what is missing, drifted, or beyond scope.
```

Close with one line per axis naming that axis's worst issue. Never produce a single cross-axis ranking.

## Why two axes

A change can pass one and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the spec asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately is what stops one axis from masking the other.
