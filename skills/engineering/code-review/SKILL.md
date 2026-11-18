---
name: code-review
description: "Review a pinned commit or working-tree change along two axes: Standards (repo conventions and code quality) and Spec (fidelity to requirements). Include staged, unstaged, and untracked task files when reviewing current work. Report the axes separately."
disable-model-invocation: true
argument-hint: "which diff, and the fixed point"
---

# Code Review

Two independent axes over a named baseline, candidate, and file scope:

- **Standards**: does the code follow this project's documented standards, and is it free of classic smells?
- **Spec**: does it faithfully implement the behaviour and acceptance criteria the spec asked for?

Review the axes independently and report them in separate sections. Never let one axis mask or outrank the other.

## Process

### 1. Pin the review scope

Use the user's baseline or the task's recorded baseline. For current uncommitted work, use `HEAD` when the task names no earlier baseline. Ask only when the intended historical comparison remains ambiguous.

- **Committed candidate:** resolve both endpoints to SHAs. Use `git diff <base-sha> <candidate-sha>`. For branch changes, resolve and record the merge-base first. An exact baseline stays exact.
- **Working-tree candidate:** include committed changes since the baseline, staged changes, unstaged changes, and non-ignored untracked files within the task scope. A clean `git diff` alone does not prove an empty scope.
- Record the selected paths and exclude unrelated concurrent work. Review a shared file's relevant changes together when they cannot be attributed safely; state the attribution limit.

For a working-tree review on POSIX with Python 3.9 or newer, capture the selected state with the bundled helper:

```bash
python3 .agents/skills/code-review/scripts/review-scope.py capture \
  --repo . --base HEAD --path src --path tests \
  --output /tmp/task-review.json
```

Replace the example paths with the task's actual files or directories. Keep the report outside the checkout and private. The helper records hashes, tracked diffs, staging, and untracked paths. It leaves Git's index unchanged.

Submodules, nested repositories, and conflicted index entries need separate review scopes; the helper rejects them. Missing local Git objects are an evidence gap, and capture does not fetch them.

Read every listed untracked file. Binary changes carry hashes and modes; inspect them with the relevant tool. The report is a manifest and diff, not a complete source archive. Recheck the viewed state before reporting:

```bash
python3 .agents/skills/code-review/scripts/review-scope.py verify \
  --report /tmp/task-review.json
```

If the state changed, review the new delta and capture a new report before declaring the candidate reviewed. A failed capture or unresolved ref is an evidence gap. On unsupported systems, record equivalent file hashes and Git state with available tools. A genuinely empty scope names both endpoints and the paths checked.

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

### 4. Behaviour evidence (when production code changes)

The diff alone cannot tell whether a test detects this change. Reuse relevant before/after evidence when it identifies the reviewed inputs. For a committed range, the script checks out the baseline in a temporary worktree, overlays only test-side files, and runs both endpoints.

```bash
node .agents/skills/code-review/scripts/fix-proof.mjs \
  --range <base-sha>..<candidate-sha> \
  --cmd '<test command per file, containing {files}>' \
  --setup '<install command>'
```

- `{files}` is replaced with the space-separated, quoted test files. No `{files}` in the command: it does not run.
- Add `--lockfile <path>` when the range diff touches exactly one lockfile; dependencies are reinstalled only when that blob changed.
- It recognises JS/TS, Go, Python, Rust, Java, and Kotlin test files by default. For anything else, replace the whole rule with `--tests '<regex>'`.
- The script accepts committed ranges only. For uncommitted changes, use isolated copies of the recorded baseline and candidate, or matching existing run evidence. Preserve staging and unrelated edits.
- Output starting with "cannot compute:" is an evidence gap. Report the cause and continue other review checks. Never interpret it as "no test changes" or use a committed `HEAD` run to certify uncommitted files.
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

For each behavioural difference, cite the applicable spec and any user-approved decision before assigning a defect:

- **Contract defect**: the implementation violates an established requirement; report `[Missing]`, `[Drift]`, or `[Scope-Creep]`.
- **Policy disagreement**: the independent expectation assumes an unsettled or different policy; report `[Policy]` with the decision needed.
- **Evidence gap**: the requirement or input meaning lacks support; report `[Evidence gap]` with the missing evidence.

An independent expectation is not itself an approved requirement. Preserve original counterexamples and cite each decision that changes the applicable policy. Keep approved policy differences visible without labelling them implementation defects.

```markdown
## Standards Review (conventions and architecture quality)
- [Hard / Heuristic] file:line - the violation or smell, with the fix you suggest.

## Spec Review (fidelity to the requirement)
- [Missing / Drift / Scope-Creep] against the spec line: what is missing, drifted, or beyond scope.
- [Policy / Evidence gap] the differing assumption, decision source, or evidence needed.
```

Name the baseline, candidate, scope, and actual checks. Close with one line per axis naming its worst issue and unresolved evidence gaps. Never produce a single cross-axis ranking.

## Why two axes

A change can pass one and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the spec asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately is what stops one axis from masking the other.
