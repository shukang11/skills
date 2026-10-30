---
name: agent-ready-repository
description: >-
  Audits a repository as a working environment: entry points, authoritative
  sources, directory boundaries, workflows, templates and validation — plus
  where a human is still forced to step in. Produces a per-item adjudicable
  recommendation table in which every item carries an exit (runnable check /
  default path / explicit human bookkeeping). Read-only; stops at
  recommendations and never executes remediation. Use when the user explicitly
  asks to make a repository agent-ready, improve zero-context onboarding,
  reorganize project knowledge, validate multi-agent readiness, or asks why a
  project keeps requiring their personal attention.
disable-model-invocation: true
---

# Agent-ready repository

Build the repository into a place where a zero-context agent can work safely. The goal is not "complete documentation" but a short, reliable loop for a real task:

`task intent → one entry → minimum fact set → correct action → confirmed boundary → verification → delivery`

## Scope

- Use this skill only when the user calls it or explicitly asks for this kind of repository remediation.
- Read-only audit by default. **This skill stops at recommendations**: it executes no remediation, sequences no priorities, and produces no "next three things".
- When the user accepts the recommendations and moves to implementation, the round order and the re-verification checklist are in [implementation-sequence.md](references/implementation-sequence.md).
- Before moving or deleting a directory, replacing an authoritative source, or changing module ownership, state the impact separately and get confirmation.
- Do not force the project onto `README.md`, `AGENTS.md`, `docs/topics/`, or spec-anchor. Identify the existing convention first.
- When the project root has `site.config.yaml` (spec-anchor is wired in), read [spec-anchor-projects.md](references/spec-anchor-projects.md): it says what `init` already laid down so you stop recommending it, what to check is actually connected, and how problem categories map to "principle N". When it is not wired in, do not run `spec-anchor init` just to finish an audit.
- **No value judgements**: "should this project continue", "is the effort split right" belong to the user's vault (`01-项目库/00-项目台账.base` with `is_at_risk` / `days_idle`, and `99-项目方法论/`), never to this skill.

## Step 1: Define real tasks and the repository's cognitive map

Pick 2 to 5 tasks that represent the project's daily work, covering: locating and changing an existing feature / creating a module, version, page, or business object / updating a dynamic fact / running tests, builds, and releases / handling deprecation, failure, or a cross-module case. With no representative task, ask the user what the most common work is. Never settle for checking whether documents exist.

From the root entry, read-only, identify these roles (file names may differ): overall entry, global rules, module map, dynamic index, fact sources, workflows, templates, verification entry, deprecated material. Record the actual path an agent takes from the task description to the first correct fact file. Do not start with a repository-wide search; that hides an entry-point problem instead of finding it.

## Step 2: Run the zero-context baseline twice

**Pass one, the agent side**: dispatch an agent with no conversation history to complete a representative task. The prompt states the real goal only; it leaks neither the correct path nor the expected answer. Require back the actual read order, the fact sources, what it could not infer, the result, and the blockers. Include at least one lighter agent to see whether skipping, over-reading, and weak inference stay safe. Change no files during the baseline.

**Pass two, the human side**: run the same task on the human's side and watch **where the human is forced to step in**. The output has exactly two buckets: `leaves the human` and `cannot leave the human`.

- **A human must be in the loop.** This pass needs a real person present to answer or act. With nobody available, record "missing source", skip the pass, and **never have the agent simulate where a human would step in**.
- **Observe, never guess.** Record only the intervention points actually observed, with the step and the location. Without evidence write "missing source". **Never infer where the human steps in**; that is the largest source of invention here.
- **Do not aim to remove every human attention point.** Some buffers force a look at the whole picture and are kept on purpose. Record those under Exit 3.
- An item skipped for "missing source" gets Exit 3 and a verdict column reading "open for discussion".

The prompts and metrics for both passes are in [acceptance-tests.md](references/acceptance-tests.md).

## Step 3: Diagnose root causes, then attach one exit to each item

Grade impact **P0 to P3** and locate the problem by **root-cause layer** (missing document / multiple authoritative copies / directory and module boundaries / workflow defaults and confirmations / template completeness / mechanical verification). The criteria are in [audit-model.md](references/audit-model.md) and [architecture-patterns.md](references/architecture-patterns.md). Every recommendation carries exactly one of the exits below.

## The three-exit gate

Every recommendation **must carry one exit**. The gate requires *an exit*, **not exit 1**.

- **Exit 1, build the eyes**: a check that runs on its own. Lint, test, CI, read-only guard.
- **Exit 2, narrow the path**: the default that appears without being asked for. Template, directory convention, scaffold, one blessed way to write it.
- **Exit 3, human bookkeeping**: an action explicitly assigned to a person.

Forcing something that cannot be verified mechanically into a bad check backfires: it adds noise and manufactures a false sense of "verified". Record those under Exit 3 instead.

## Delivery format

Deliver the **decidable table**, one row per recommendation:

| Problem | Impact P0–P3 | Exit | Suggested action | Accepted cost | Verdict |
|---|---|---|---|---|---|

- **Leave the verdict column empty**: the skill neither prefills it nor leans it.
- **Accepted cost must be decidable.** State exactly what accepting the recommendation costs: which script, convention, or process gets added or changed, how many extra steps each change takes, and who has to remember what. If you cannot write it, the recommendation is not concrete yet; rewrite it rather than letting the column degenerate into adjectives.
- Before the table, state this run's target task and the baseline evidence, including the human side's two buckets. After the table, list only the residue that still affects work. No "next three things".

**Completion criteria** (all four, or it is not delivered):

- Every row carries an exit (1, 2, or 3), with none blank.
- Every Exit 3 row names the human gate it lands on (deciding intent, merge review, cutting a release, for example) and says why it fits neither Exit 1 nor Exit 2. If neither can be written, think again.
- The human side's two buckets either carry observation evidence or are explicitly marked "missing source". No inference anywhere in them.
- The residue that still affects work is listed after the table.

A worked case is in [example-work-assistant.md](references/example-work-assistant.md).
