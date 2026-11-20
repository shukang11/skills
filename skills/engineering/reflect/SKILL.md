---
name: reflect
description: "Mine this session's transcript with three reviewer lenses, then route each learning to a concrete skill edit. Read-only until the human approves row by row; never edits a skill on its own. Use for /reflect."
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Resolve at the first of these that yields a complete transcript of *this* conversation:

1. **A path or id you were handed.** The author named a transcript, session id, or export; or the current harness exposed this session's id or log path to you. Open that file directly, with no directory scan.
2. **The store the current harness writes.** Read [references/session-locator.md](references/session-locator.md) and take the row for the harness you are running in. The session's own metadata decides, not file recency: its id, its project path, and the first user request together.
3. **A digest.** When no store holds a complete, matching transcript, continue on a tight digest of what this conversation already carries, and say `partial` in the reply.

Partial evidence stays labeled. A digest run cites no transcript line number, no tool result, and no file read that the digest does not show; a skill counts as read or used only when the evidence is there. An archived conversation from an earlier day is a different session, however close its topic.

Done when the transcript handed to the reviewers is either a matched file path or an explicitly partial digest.

## 2. Spawn three reviewers in parallel

One message, three reviewers in parallel, on different model families when you have them. Read-only: they must not edit files. When a read-only subagent cannot reach the MCP tools the transcript calls for, run that reviewer as a normal subagent and put "write nothing, edit nothing, commit nothing" in its brief instead.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. When you pass a digest, say in the same brief that it is partial and may have dropped turns, so reviewers quote what they can see and mark the rest unverified. Reviewers return findings in the response body.

## 3. Synthesize

One reviewer call on the strongest model you have, read-only. It spot-checks citations, using whatever MCP the environment actually has. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply, only after the human approves

**Nothing in this skill changes a skill on its own initiative.** The run up to here is read-only. Present the synthesizer's full Accepted / Rejected / Backlog output, then stop and wait.

Skill edits change how every future agent in this repository works, so the human authorizes them line by line:

- Wait for explicit approval. A general "looks good" is not approval of specific rows; ask which rows to apply.
- Apply only the approved rows. Anything outside that set is out of scope, including a one-line fix you noticed on the way.
- Rows the human skips stay unapplied. Report them as skipped rather than folding them in silently.
- If the human approves a row whose routing needs a substantive rewrite, hand it to the `writing-for-agents` skill and follow its rules; do not invent the shape ad hoc.
- Backlog items are notes, not edits. Write them to `.agents/notes/` when the human says to keep them; otherwise leave them in the reply.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Skipped: one line per approved-set row the human declined.
- Dropped: one line per rejected finding + reason from the synthesizer.
