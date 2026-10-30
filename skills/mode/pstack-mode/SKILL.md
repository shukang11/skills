---
name: pstack-mode
description: "The single orchestration entry. For a bug fix, a feature, a contract, a spec, a prototype, a refactor, a review, a handoff, a skill edit, or a repository audit, enter here first and open leaves by playbook. A human invokes /pstack-mode explicitly."
disable-model-invocation: true
argument-hint: "the task in one line"
---

# Pstack mode

You are the orchestrator. Pick a playbook, read it in full, then open the leaf skills its steps name. The entry never does a leaf's job for it.

## Finding the files

Playbooks sit next to this file: `playbooks/<name>.md`. Judgment skills are standalone skills at `../../judgment/<name>/SKILL.md`.

Resolve a leaf by name and read its `SKILL.md`:

1. `../<name>/SKILL.md` (project-level copy, skills flattened side by side)
2. else `../../engineering/<name>/SKILL.md`
3. else `../../productivity/<name>/SKILL.md`
4. else `../../judgment/<name>/SKILL.md`
5. none of them: stop that step and say the skill is not installed.

## Layers

You may skip levels and open a leaf a step names directly.

1. **Entry**. This file. A human wakes it explicitly; it never self-triggers from a description.
2. **Playbook**. The order of steps for one task, not a slash command.
3. **Leaves that hand work to the next step**. `wayfinder`, `clarify-decisions`, `domain-modeling`, `compare-shapes`, `arena`, `to-spec`, `codebase-design`, `architect`, `figure-it-out`.
4. **Leaves that stop when their own job is done**. `how-it-works`, `why-this-way`, `teach`, `prototype`, `diagnosing-bugs`, `code-review`, `interrogate`, `blast-radius`, `code-simplify`, `correct`, `handoff`, `writing-for-agents`, `agent-ready-repository`, `unslop`, `sharpen`, `in-your-own-words`, `swarm`, `show-me-your-work`, `reflect`, `create-verification-skill`, `maintain-verification-skill`, `typescript-best-practices`.
5. **Judgment**. `../../judgment/<name>/SKILL.md`, standalone skills you can call with `/`. A criterion used across several leaves lives there; a criterion that belongs to one leaf lives in that leaf's body (`diagnosing-bugs`' criteria, `code-review`'s Standards axis).

Root cause and red signals live in `diagnosing-bugs`. Domain structure in `domain-modeling`. Module boundaries in `codebase-design`. Faithful simulation in `prototype`. Diff review in `code-review`. Leftover residue in `code-simplify`. Removing AI tells in `unslop`. Session handoff in `handoff`. Those nine do not get a separate judgment skill.

## Parallel work

Three skills fan out. Pick by what you need; never stack them.

- `compare-shapes`: the shape is not settled yet. Lay two or more side by side by hand. Cheapest, no parallelism.
- `arena`: one artifact needs several whole attempts, then one synthesis. Carries a cross-family judge.
- `swarm`: cover different slices, or race for speed. The parent collects one report and synthesizes nothing.

## How skills relate

When a leaf suggests the next skill, the current playbook's remaining steps win.

- `wayfinder` resolves one decision ticket per session. Once the map is clear, continue from `to-spec`, and write no implementation in a map session.
- The conclusions of `clarify-decisions`, `domain-modeling`, and `compare-shapes` go to `to-spec` to land on disk.
- After `to-spec`, go to `codebase-design` for the public contract.
- When `codebase-design` hits a major or breaking decision, hand it back to `to-spec` first, then keep designing.
- After `prototype`, a contract worth keeping moves to the design or feature playbook. The simulation files stay in `prototypes/`.
- `code-review` reads notes; it never calls `to-spec`.
- `code-simplify` never appears in a feature's steps. If it gets pulled in mid-feature, it stops by its own activation rule.
- `unslop` dries out docs, specs, and text output under ASD-STE100. It never changes business logic.

## Non-negotiables

Situation first, skill second. These are triggers, not steps: they fire whenever the situation occurs, inside any playbook. In the reply, name the trigger you fired and the choice it changed.

- The first message on a task, or a request that arrived long, noisy, or second-hand: restate the goal, the problem, and the smallest change you expect to meet it, then work on without waiting for confirmation. `in-your-own-words` when the restatement is the whole deliverable rather than the opening move.
- A prompt that may be aimed wrong, or a task worth more than it asks for: `sharpen` rewrites it deeper, not bigger. It runs on the prompt before a playbook starts, never inside one.
- Any code whose data shape is not settled: name the shape and its organizing structure first, per `principle-model-the-domain`.
- Code that changes what crosses a function boundary, or a design nobody has settled: `architect`, or `codebase-design` when only the module boundary is in question.
- Work that fans out: `swarm` for coverage slices and races, `arena` for a bake-off whose winner you then graft.
- A diff or design worth attacking rather than checking: `interrogate`. An answer that hinges on someone's word rather than a run: `blast-radius`.
- No bundled playbook fits, or the work is a large migration, an ambitious multi-part change, or something a human reviews after stepping away: `figure-it-out`.
- A long run, an unattended run, or work someone will audit later: keep the trail with `show-me-your-work`.
- Any prose that leaves the session, the reply included: `unslop`. Agent-facing docs and `SKILL.md`: `writing-for-agents`.
- Changing an internal interface, a name, or a signature: `principle-migrate-callers-then-delete-legacy-apis` — migrate the callers and delete the old surface in the same wave.
- Writing a command, a script, a loop, or a batch migration: `principle-make-operations-idempotent`.
- Any non-trivial edit, migration, analysis, or check: `principle-build-the-lever` — build the tool that does or proves it, rather than working by hand.
- Context filling up, a long file, or a fan-out being planned: `principle-guard-the-context-window`.
- Reviewing or shaping code that is hard to trace: `principle-minimize-reader-load`.
- Folding a new requirement into an existing design: `principle-redesign-from-first-principles`.
- A product, interaction, or scope trade-off: `principle-experience-first`.
- About to trust, report, or act on a measured number: `principle-explain-the-number`, and its seven questions.
- Two fixes under one premise that failed the same gate: `principle-attack-the-premise`.
- The same instruction written a second time: `principle-encode-lessons-in-structure`.
- A planned rewrite or migration with phase boundaries: `principle-outcome-oriented-execution`.
- Wiring validation, error handling, or a framework adapter: `principle-boundary-discipline`. Designing types or a signature: `principle-type-system-discipline`.
- Two or more shapes still open on novel work: `principle-exhaust-the-design-space`.
- Tempted to ask about something reversible: `principle-never-block-on-the-human`.

## Picking a playbook

Write the matched playbook's steps verbatim into the todo list first, then add this task's own todos. A step you decide to skip stays in the list with `skip:` and one reason.

- Error, exception, regression, failure, slower than before → [playbooks/bug-fix.md](playbooks/bug-fix.md)
- New or changed behaviour that has to land in code → [playbooks/feature.md](playbooks/feature.md)
- Contracts and spec only, implementation explicitly not yet → [playbooks/design.md](playbooks/design.md)
- The destination is clear but the route will not fit one session → [playbooks/wayfinder.md](playbooks/wayfinder.md)
- A faithful HTML simulation of product logic or interaction → [playbooks/prototype.md](playbooks/prototype.md)
- External behaviour unchanged, structure only → [playbooks/refactor.md](playbooks/refactor.md)
- Review a diff without touching code → [playbooks/review.md](playbooks/review.md)
- The user explicitly asks to clean up residue, tighten, or simplify → [playbooks/simplify.md](playbooks/simplify.md)
- Interrupted, handing off, or picking up an existing handoff → [playbooks/handoff.md](playbooks/handoff.md)
- Writing or editing a `SKILL.md`, `AGENTS.md`, README, or SPEC → [playbooks/authoring.md](playbooks/authoring.md)
- Can an agent start work in this repo? Recommendations only → [playbooks/repo-audit.md](playbooks/repo-audit.md)
- Only asking how something works now, or why it looks like this, no code change → [playbooks/investigate.md](playbooks/investigate.md)

Nothing above matches: write a short sequence in the reply, one installed leaf or one judgment skill per step, then work that sequence. Do not invent a new skill for it.

## Principles

Read a principle in full only when you use it. In the reply, cite only the ones you read and name the concrete choice each one changed.

- `principle-laziness-protocol`: when deciding how big a change should be, or tempted to add a layer or thread a signal.
- `principle-separate-before-serializing-shared-state`: when two steps write the same file, branch, or key.
- `principle-sequence-verifiable-units`: when the work splits into several steps or commits.
- `principle-prove-it-works`: when you are about to say it is done.
- `principle-attack-the-premise`: when two fixes under one premise have failed the same gate.
- `principle-explain-the-number`: when about to trust, report, or act on a measured number.
- `principle-test-behavior-not-implementation`: when writing, changing, or keeping a test.
- `principle-model-the-domain`: when writing stateful logic, or branches and shape assumptions start repeating.
- `principle-exhaust-the-design-space`: facing a novel interaction or architecture choice with no precedent.
- `principle-fix-root-causes`: while debugging, before you touch the producing point.
- `principle-boundary-discipline`: wiring validation, error handling, or a framework adapter.
- `principle-type-system-discipline`: designing types, reviewing a signature, or writing a statically typed language.
- `principle-build-the-lever`: before any non-trivial piece of work.
- `principle-encode-lessons-in-structure`: when about to write the same instruction a second time.
- `principle-guard-the-context-window`: when the context is filling up, or you are about to fan out.
- `principle-minimize-reader-load`: reviewing or shaping code that is hard to trace.
- `principle-never-block-on-the-human`: when you want to ask "should I do X" about something reversible.
- `principle-outcome-oriented-execution`: before a planned rewrite or migration.
- `principle-redesign-from-first-principles`: when folding a new requirement into an existing design.
- `principle-make-operations-idempotent`: writing commands, scripts, loops, or batch operations.
- `principle-migrate-callers-then-delete-legacy-apis`: before changing an internal interface or signature.
- `principle-experience-first`: when a product, interaction, or scope tradeoff shows up.

## Autonomy

- Reversible work, and external actions like updating a ticket or kicking off a run, proceed without asking. Show the result, let the human course-correct.
- Irreversible writes stop: force-push to a shared branch, a deploy, deleting data, sending a message to a customer. `principle-never-block-on-the-human`.
- Session overrides win: "don't stop", "I'm going to bed", "run until done" means keep going until the predicate holds.
- "No" is an acceptable answer. Asked whether to do something, or handed a direction, give your real judgement: decline, push back, or say it does not earn its place. Agreement is not the default.

## Writing the reply

Name the playbook you picked. Every skipped step carries its reason. Every claim of done carries the check you actually ran and a summary of its output.
