---
name: handoff
description: "A state capsule for resuming a session: when the context is nearly full, work is interrupted, or you are stopping on purpose, distil the break point and the runtime state into a temporary handoff document so the next session picks up the same task without friction."
disable-model-invocation: true
argument-hint: "(optional) what the next session should focus on; leave empty and the agent infers it, labelled [Pending]"
---

# Handoff

Distil the current conversation into a temporary handoff document so the next session can resume the same task without friction.

The default case is the forced interruption: the context is nearly full, work stops halfway, or the thread has to survive dropping the context. All of these share one property: the user does not know the next stage's goal, so the receiver restores the scene first and decides the action second.

This skill covers session-to-session resumption only. Cross-role orchestration, such as dispatching a task from planner to worker, is out of scope: that handoff needs an explicit task package and acceptance criteria, and belongs to its own skill.

## Where it lands

- Write to the operating system's temporary directory (Windows `%TEMP%`, Linux and macOS `/tmp` or `$TMPDIR`).
- Name it `handoff-<task-slug>-<timestamp>.md`.
- Print the absolute path in the reply.

## Delivery contract: two things, every time

1. **The handoff document**, written to the temporary directory in the skeleton below.
2. **The opening block for the new session**, in the same reply, under the heading `## New session opener (copy the whole block)`. Never hand over a path alone and leave the user to compose the opening themselves.

Rules for the opening block, consistent with the no-duplication rule below:

- It holds the resumption protocol, the file's absolute path, a one-line task summary with its reliability label, and the first `Verify First` command only. When section 5 of the document already states that command, copy the path or command, never the reasoning.
- No spec body, no code blocks, no restated decisions. The handoff document is the single place those live.

## Relationship to notes

- This skill stands alone: it needs no existing notes to work.
- References run one way: the handoff may point at existing notes (for example `.agents/notes/proposed/2025-01-01-foo.md`, with its status label) but never copies their body.
- The handoff file is disposable. Nothing else should ever reference it.

## Writing discipline

1. **Record flow state, never copy static material.** No pasting of code, diffs, specs, ADRs, or issue bodies. Point at them: absolute path, relative path, or URL, such as `docs/adr/0002.md` or `src/auth/jwt.ts:40-60`.
2. **Separate facts from assumptions.** The receiving agent treats this document as an unappealable contract, so an unverified inference must never read as fact. Label every claim:
   - `[Verified Fact]`: checked by running a test or a tool.
   - `[Pending / Unverified]`: current assumption, unexplored boundary, or guess.
3. **Never fill a gap.** What the session did not record, the document does not say. A gap is itself information. This matters most for three things: the next stage's goal, the reason an option was rejected, and the root cause of a blocker. Write what was recorded; when nothing was recorded, write "no explicit record" rather than reconstructing a plausible story. The receiver cannot cross-check, so an invented line gets adopted as `[Verified Fact]`.
4. **Redact.** Strip every API key, password, token, and personal detail.
5. **Audit before you write.** Walk back each `[Verified Fact]` to its evidence: which command ran, which output was seen. Anything you cannot trace back is downgraded to `[Pending / Unverified]`.

## Document skeleton

```markdown
# Handoff: <short task name>
- **Generated**: <ISO timestamp>
- **Context / Primary Goal**: <stated by the user | [Pending / Unverified] inferred by the agent>

## 1. Where I left off
- Last completed action; last command or commit that succeeded
- Started but unfinished
- What was intended next (write "no explicit record" when none)
- Workspace state: branch, uncommitted changes

## 2. Anchors
- Pointers to specs, ADRs, standards (paths only)
- Modules and seams involved: [path and line ranges]

## 3. Decisions made
- Constraints or approaches settled
- Rejected alternatives and why (only those actually discussed in the session; otherwise "no explicit rejection on record")

## 4. Runtime state
- [Verified Fact] ... (which commands or tests ran)
- [Pending / Unverified] ... (current blocker or unverified hypothesis)

## 5. Directives for the next agent
- **Verify First**: the fact to re-check on arrival, and the exact command
- **Immediate Next Step**: the first concrete action once verification passes
- **Suggested Skills**: (optional) skills to open after verification
```

`Context / Primary Goal` sits beside the break point, never promoted to an authoritative goal: the agent usually infers it, so it carries a label, `<stated by the user>` or `[Pending / Unverified] <inferred>`.

## New session opener template

Write this into the reply verbatim, placeholders filled:

```markdown
## New session opener (copy the whole block)

You are the receiving agent, resuming the same task. Do not re-plan from scratch or repeat finished discussion.

1. **Read the handoff first**: read the document at the path below in full.
2. **Verify first**: run section 5's "Verify First" and report. Treat only `[Verified Fact]` as established; re-verify or ask about every `[Pending / Unverified]`.
3. **Then act**: after verification passes, do section 5's "Immediate Next Step". Open the suggested skills explicitly when you need them.

**Handoff file**: `<absolute path>`

**Task in one line**: `<the Context / Primary Goal label and one-line summary>`

**First re-check**: `<the first Verify First command, or "see section 5">`
```

Optional, below the block: a suggested session title, at most 80 characters, such as `Resume: <task-slug> · verify → <the next step in a phrase>`.

## Arguments

- The user passed a goal: write it into `Context / Primary Goal` labelled `<stated by the user>` and trim the document to it.
- No goal passed, which is the normal case: infer it, label it `[Pending / Unverified]`, and never stop to ask about the missing argument.
