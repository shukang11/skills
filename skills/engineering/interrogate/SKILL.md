---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Adversaries from different model families try to break a change or a design, and only a finding a run proves survives."
disable-model-invocation: true
argument-hint: "the diff, branch, file, or design to attack"
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings and change no code.

## Frame

The scope is what the user named. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent per the `in-your-own-words` skill, from the user's message, the commits, and the PR description. Ask the user when the intent is not clear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of the `arena` skill, with four changes:

1. **Two adversaries is the floor, three when the change is large or the intent is contested.** Each sits on a different model family, per Phase A step 3.
2. **Copy the scope's uncommitted changes into each worktree**, so every adversary attacks the same bytes rather than its own checkout.
3. **Drop the rubric.** The gradeable-criteria half of Phase A has nothing to grade here. Give each adversary the scope, the intent, and the brief below.
4. **Ask for repros, not readings.** An adversary that reports a suspicion without running it has produced nothing yet.

The brief, verbatim:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or a plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and every risk that needs a future change to matter. No findings is a valid result.

## Verify

Verify each finding per arena Phase F: rerun its command yourself, in the same worktree. Keep a finding when the output shows the failure and that failure breaks the intent. Drop the rest. Merge findings that share a root cause into one.

A claim that a test pins the change is a finding too, and it has its own check: `../code-review/scripts/fix-proof.mjs` reruns the changed tests at the anchor and at the range end. A test that stays green at the anchor pins nothing.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding instead of one adversary's list, and there is no base to pick or graft.

## Output

- **Intent**: the restatement, in a sentence or two.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Write "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why they went.

**Reply:** the three sections, and one line naming what you verified by running and what you dropped for want of a run. A finding offered without its command and output is not a finding: go back and run it.
