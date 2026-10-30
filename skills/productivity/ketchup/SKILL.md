---
name: ketchup
description: "Catch the user up on what changed in this chat since their last message, in plain words, and list every item now waiting on them so each one is decidable from the reply alone. Use for /ketchup."
disable-model-invocation: true
argument-hint: "nothing, or the thread to catch up on"
---

# Ketchup

Catch the user up on what changed since the last message they wrote before `/ketchup`, then lay out every call waiting on them. Assume they remember their last message and nothing after it. A subagent result or a notification is not their message.

## Voice

Plain words, short sentences, the way one person catches up another. Say what changed for the user, not how you did it: "the tests pass", not "CI is green". Call each PR, branch, or agent by a name the user would know, not a label you invented. Hold the prose to the `unslop` skill: no AI tells, no generated cadence.

## Gather

Keep this turn read-only: no code changes, no starting an app or a job, no posting.

An **action item** is a call only the user can take: a product choice, an approval, an irreversible action, or access you lack. Include every one still waiting, even one raised before their last message. Work you can still do yourself is not an action item, and never invent one to fill the reply. One call can cover many items, such as each PR in a set awaiting merge.

For each item, collect its link or number, what it changes for the user, the evidence behind your pick, its risk, and your pick. Write "unknown" for a fact the call needs and you do not have.

## Write the reply

1. **One short sentence** naming what waits on the user, or saying nothing does. If nothing happened and nothing waits, say so and stop.
2. **What happened, under 100 words.** One short bullet per thing the user asked for: what came of it, and whether it is done, still running, failed, or not checked. Name any bug found and fixed on the way. Under the bullets, at most three short lines that change what the user knows or must do.
3. **The action items**, about 30 words each: ask the call the user owns, give your pick, and name anything that must happen first or cannot be undone.
4. **One line** naming work left that you can do yourself.

## Bounds

- **The reply grows with the number of items.** Never cut an item, and never replace one with a count or a link, to stay under a word count.
- **A link adds depth; the reply alone must be enough to decide.**
- **Never mark something done that still waits on the user.**
- **Leave out** hashes, file paths, commands, build numbers, and test counts unless a decision needs one. Give a fact its context or leave it out.
- **This skill looks back.** `handoff` writes forward for the next agent, and `show-me-your-work` keeps the decision log while the run is happening.

**Reply:** the four parts above, in that order, and nothing else. An item that needs a follow-up question to decide is not finished: put the missing fact in the reply, or say "unknown".
