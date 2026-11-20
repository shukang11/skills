---
name: code-review
description: "Review a pinned commit, a working-tree change, or the current state of a project or module along two axes: Standards (repo conventions and code quality) and Spec (fidelity to requirements). Pin the scope from what the author gives, else infer it from the task and report the basis. Include staged, unstaged, and untracked task files. Report the axes separately."
disable-model-invocation: true
argument-hint: "what to review (change, files, module, or whole project), and any fixed point"
---

# Code Review

Two independent axes over one pinned review scope — baseline, candidate, and files, or the current state of the named code:

- **Standards**: does the code follow this project's documented standards, and is it free of classic smells?
- **Spec**: does it faithfully implement the behaviour and acceptance criteria the spec asked for?

Review the axes independently and report them in separate sections. Never let one axis mask or outrank the other.

## Process

### 1. Pin the review scope

Done when the report names one scope, its basis, what it includes and excludes, and its limits — before any finding. A clean `git diff` alone does not prove an empty scope.

- **The author's scope wins.** Named paths, a named baseline, a named commit range: review exactly that, even where you would have chosen differently. An inferred scope is reported as inferred, never as the author's approved scope.
- **No scope given: infer, then report.** Read this task and conversation, any plan or spec already written, and the entry points and callers the work touches. Open the report with this run's scope, basis, included and excluded paths, and limits; then review the part that is already determinate. Asking is the last resort, not the gate: ask one focused question only when every candidate scope would change the conclusion and nothing yet is determinate.
- **Change review or current-state review.** Take the kind from the request: "review this change / diff / my work" is change review; "review this project / module / this code" is current-state review of the code as it stands. A Git repository does not force change review — history existing is no reason to substitute a guessed recent range for the module the author asked about.
- **Committed candidate:** resolve both endpoints to SHAs. Use `git diff <base-sha> <candidate-sha>`. For branch changes, resolve and record the merge-base first. An exact baseline stays exact.
- **Working-tree candidate:** include committed changes since the baseline, staged changes, unstaged changes, and non-ignored untracked files within the task scope. For uncommitted work with no earlier baseline named, `HEAD` is the baseline.
- **Committed and clean tree.** A clean working tree does not mean no change. Assemble one coherent change set from commits whose messages, paths, and tests name this task, and extend along history where the change continues past them. The evidence is task relevance, code contact, and tests/specs; a file's modification time proves nothing. Do not settle for `HEAD` alone, the last N commits, an arbitrary slice by date, or the whole repository. Mark the baseline `inferred`. Where several defensible scopes would change the verdict, name the ambiguity and review the determinate intersection or the current state instead of claiming to know the author's intent.
- **No Git.** Confirm with `git rev-parse --is-inside-work-tree` from the reviewed directory. `true` reached from a nested directory may mean an accidentally entered parent repository, and `git rev-parse --show-toplevel` landing above the directory under review does not by itself prove it: when the target is a genuine subdirectory of the repository that owns it, keep using that repository's history and limit the paths to the target. Only a confirmed unrelated parent or outer repository, or a directory that is not a worktree, drops to the current-state review that follows; when the repository's ownership cannot be confirmed, derive no diff from its history — review the current state and say that is what you did. Without a repository or usable history, review the current state: organize the scope by task, entry points, modules, and specs, and widen into dependencies as findings require. A general "review this project" over a small project covers it whole; over a large one, review the core related parts and name the coverage. That directory stays read-only and unversioned — no `git init`, no commit, no baseline snapshot. With no baseline, say **baseline unavailable**: what changed, what regressed, and what the code did before are all unprovable, no diff or commit is invented to fill the gap, and every conclusion describes these files as read.

For a working-tree review on POSIX with Python 3.9 or newer, capture the selected state with the bundled helper:

```bash
python3 .agents/skills/code-review/scripts/review-scope.py capture \
  --repo . --base HEAD --path src --path tests \
  --output /tmp/task-review.json
```

Replace the example paths with the task's actual files or directories. Keep the report outside the checkout and private. The helper records hashes, tracked diffs, staging, and untracked paths. It leaves Git's index unchanged.

The helper needs a Git working tree. Outside Git, record the same manifest by hand — the selected paths with their hashes and modes, read with the tools at hand — rather than adding a scope-inference script.

Submodules, nested repositories, and conflicted index entries need separate review scopes; the helper rejects them. Missing local Git objects are an evidence gap, and capture does not fetch them.

Read every listed untracked file. Binary changes carry hashes and modes; inspect them with the relevant tool. The report is a manifest and diff, not a complete source archive. Recheck the viewed state before reporting:

```bash
python3 .agents/skills/code-review/scripts/review-scope.py verify \
  --report /tmp/task-review.json
```

If the state changed, review the new delta and capture a new report before declaring the candidate reviewed. A failed capture or unresolved ref is an evidence gap. On unsupported systems, record equivalent file hashes and Git state with available tools. A genuinely empty scope names what was checked — both endpoints and the paths, or the files read and their state when there is no second endpoint.

### 2. Find the spec

In this order:

1. A spec, requirements, or design doc the user named or pointed at.
2. A spec under `.agents/notes/proposed/` or `.agents/notes/` that matches this change.
3. A spec, requirements, or design doc under `docs/`.
4. Nothing found: say "no spec available", run the Standards axis alone, and mark the Spec axis not reviewed. The report may add that a spec review needs a spec first: `to-spec` converges requirements the discussion has already settled into one, then the review runs again. That is a route hint for a later step only. The review itself never invokes `to-spec`, never writes a spec, and never derives acceptance criteria from the current implementation, which would only certify what was already built. When the requirements themselves are still unsettled, `to-spec` cannot supply them; say so instead.

### 3. Find the standards sources

Stack these; later entries do not replace earlier ones.

1. The project root `AGENTS.md` implementation rules and forbidden zones, plus any coding-standards docs (`CODING_STANDARDS.md`, `CONTRIBUTING.md`). A standard a project tool generated is still a project rule: read it here, whatever wrote it.
2. Whatever those leave uncovered falls back to the Fowler smell baseline below.

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
- The script accepts committed ranges only. For uncommitted changes, use isolated copies of the recorded baseline and candidate, or matching existing run evidence. Preserve staging and unrelated edits. With no baseline at all — a current-state review outside history — there is no second endpoint to run: report the evidence gap and claim no regression result.
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

With no spec, the Spec section carries one line saying it was not reviewed and why, never an empty list that reads as a pass.

Name the review kind (change or current-state), the baseline or `baseline unavailable`, the candidate, the scope, whether that scope was explicit or inferred, and the actual checks. A current-state review has no candidate endpoint: name the files or directories and the state they were read in, and do not dress them as a diff. Close with one line per axis naming its worst issue and unresolved evidence gaps. Never produce a single cross-axis ranking.

## Why two axes

A change can pass one and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the spec asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately is what stops one axis from masking the other.
