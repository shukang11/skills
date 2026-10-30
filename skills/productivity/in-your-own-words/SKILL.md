---
name: in-your-own-words
description: "Restate the goals you think the user has and the problem they are trying to solve, before any work starts. Use for /in-your-own-words, or as the first move on a task that arrived noisy, long, or second-hand."
disable-model-invocation: true
argument-hint: "the message, thread, or ticket to restate"
---

# In your own words

Restate what you think the user's goals are and what problem they are trying to solve.

## Shape

- **Goal** in one or two sentences: what changes, and for whom.
- **Problem** in one or two sentences: what is wrong or missing now, and why the goal is not already met.
- **Smallest change**, when the task ships something: the least you expect to meet the goal. Say what it does not cover.
- **Assumptions** you had to make, one line each, marked as yours rather than the user's.

Use the user's own nouns. Where you replaced one, say which word you replaced and why.

## Bounds

- **This skill produces a restatement and stops.** No questions, no plan, no spec, no code. A restatement that turns into an interview is `clarify-decisions`; one that lands on disk is `to-spec`.
- **Do not ask for confirmation.** The point is to surface a misreading where it costs one message, so write it down and let the user correct it.
- **Keep fact and inference apart.** Mark anything you inferred, so a wrong inference is visible instead of buried.
- **Do not pad.** Two short paragraphs and the assumption lines. A restatement longer than the request it restates is not a restatement.

**Reply:** the restatement, nothing else. When the request was clear and the restatement adds nothing, say what you are about to do in one sentence instead.
