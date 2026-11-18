---
name: recall
description: "Rebuild recent working context from the session stores this machine actually has, plus the shared record, and hand back a current-state brief. Use for 'recall my work on X', 'where did I leave off', 'what have I been working on', before starting or resuming work that is not already in this chat."
disable-model-invocation: true
argument-hint: "topic, window, or environment; default is this workspace, the last 7 days, every store that exists"
---

# Recall

**Before you start or resume work, rebuild the recent working context and hand back a tight brief of where things stand and the single next move.**

Read only what the scoped threads need, then stop. The brief is the deliverable. Do not start the work it recommends.

Two records. Your own sessions hold what you did and decided, and they are not all in one product. The shared record holds what happened around the same code under other names: symptoms, fixes that shipped and got reverted, errors still firing. That second record is what `why` searches. A feature with a long bug tail keeps most of its story there, so do not reconstruct it from transcripts alone.

## Bounds

- **This chat since the user's last message** is `ketchup`. **Writing a capsule forward for the next agent** is `handoff`. A handoff path the user already gave is the handoff playbook. Recall is the other direction: earlier sessions, before you act.
- **The user already handed a full state capsule** (paths, branch, the change): use it and skip the mining.
- **Scope is stated before the search, and it is not widened in silence.** "All" does not become "recent N". Another project's sessions stay unread unless the user asked.
- **A store you cannot key to the workspace stays out.** Say so. Do not mine a global pile and hope.
- **Redact.** No API keys, tokens, passwords, or personal data in the brief or in anything a subagent returns.

## Steps

1. Lock the scope in one line, then search. Pin the window ("recent" means a range, default the last 7 days), the topic if one was named, the workspace (default the active cwd), and the environments (default every store whose home exists; one name if the user named one). Done when that line is written down, before any transcript is opened.
2. Read [references/stores.md](references/stores.md) and inventory. For each named store, record one of: home missing, present but not a transcript, or readable. Done when every named store has one of those three, including the ones you will not open.
3. Mine the readable stores. One or two sessions: search them yourself. More than that: one subagent per store, in one message. Each subagent orders candidates by modification time, never by id, greps the topic first, then reads only the matching sessions and only the regions that match. It skips this conversation, subagent runs, and eval or test sessions. It returns one block per session: environment, session id, time, the user's goal, decisions, open threads, corrections, and artifacts (PRs, branches, paths), each citing the session file. Raw transcripts stay in the subagent. Done when every in-scope session is either a block or a stated skip.
4. Sweep the shared record when the topic names a feature, file, subsystem, area, or bug. This is the default. "My work on X" does not skip it. Hand the question to `why`, steered from "why was this built this way" to "what is the current state, what was tried and did not hold, what are people still reporting". Run it in parallel with step 3. Inherit `why`'s rule: one investigator per source, an empty source is a finding, a missing tool is named. Skip this step only for pure activity recall with no named target ("what did I do this week"). Done when the sweep's findings are folded in, or the skip reason is written.
5. Check live state. Take the PRs, branches, and tickets the mining and the sweep named and check them with `git` and `gh`. When the answer hinges on what an agent actually did, read that transcript, not only the subagent's block. Done when each artifact in the brief is tagged from the live check, not from the transcript's claim.
6. Write the brief to the contract below. Group by thread, not by environment. The same effort in two stores is one thread, and both sources are named.

## Output contract

Lead with the capsule, then the threads, then the problems, then the next move, then the sources. Cut detail before you cut a thread.

- **Capsule.** At most 5 bullets. What this work is and where it stands.
- **Threads.** One line each, prefixed with exactly one tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`. A thread with no tag is not done.
- **Problems.** At most 5, the recurring ones. Include a symptom that keeps coming back and any fix that shipped and was reverted.
- **Next move.** One concrete action.
- **Sources.** One line per store from step 2: how many sessions matched, "not installed", "present, not a transcript", or "empty in this window". Name a session as its environment plus its id.

An adjacent feature stays out unless it blocks this one. Write the brief through `unslop`. Cite a chat finding by environment and session id, and a shared-record finding by its source (PR, ticket, note path).

**Reply:** the brief, to the contract above, and nothing else.
