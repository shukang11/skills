---
name: maintain-formal-verification-skill
description: "Bring a project's formal verification back in line with the code after the code changes: find the commits that touched verified code, update the model, harness, or properties to describe the code as it is now, rerun, and say whether each failure is drift in the verification or a bug in the code. Use for /maintain-formal-verification-skill, \"is the model still true to the code\", or after merges and refactors that touched verified code without rechecking it."
disable-model-invocation: true
argument-hint: "the verify skill, property, or area to reconcile"
---

# Maintain a formal verification skill

A formal check proves a property of what it describes. When the code moves and the verification does not, the check can keep passing while it describes code that no longer exists. That pass is the dangerous case, because it looks like a proof. This skill is the upkeep loop for a skill that `create-formal-verification-skill` generated, or for any project-local skill that runs a model checker, a prover, or a code-level verifier against named code. The project-local skill handles a change an agent makes while it uses that skill. This skill handles the changes that skipped it: merges, edits made without the skill, and drift that builds up across many commits.

## Outcomes

Give each check one outcome, and say which:

- **in sync** — nothing since the recorded commit changes what the check describes, and the check passes.
- **updated** — the code changed, the verification now describes the new code, and the check passes.
- **bug** — the verification describes the current code, and the code breaks the property. This is a finding about the code, not drift.
- **blocked** — the check could not be brought back in line, or could not run. Say exactly why.

A check can be both updated and bug: the update makes the verification describe the code again, and then the property fails on that description.

These four line up with `maintain-verification-skill`, which reconciles a feature map rather than a property. `in sync` and `clean` are the same outcome for different objects, `updated` and `changed` likewise, and `blocked` means the same in both. `bug` has no counterpart there, because a feature map has no property to break. Do not invent a fifth word.

## Edit scope

Edit only the verification: models, harnesses, property files, and the verify skill itself. Never edit product code during a run unless the user asks. When a property fails on the current code, do not weaken the property or the model to make it pass. Report the failure.

## Pass

1. **Find the checks.** A verify skill has no fixed name, so find it by what it does: a project skill that runs a model checker, a prover, or another verifier against named code. Read each one you find, or the one the user named. For each check, collect the property, the code it covers, the bounds and assumptions, the command that runs it, and the commit where it was last confirmed to describe the code. If no verify skill exists, stop and point at `create-formal-verification-skill`. If a skill does not record a sync commit, use the last commit that changed its verification files, and say that you did.
2. **Run it as it is.** Run each check once before you change anything, and record the result. A pass here does not tell you that the code is correct. It tells you that the old description still holds. A failure here can be drift or a bug, and you do not decide which until step 4.
3. **Diff the covered code** since that commit, with `git log` and `git diff` over the files and functions the check names. A change to an indivisible step, a new interleaving, a widened type, or a new caller all matter. A comment, or a rename inside a step the check does not name, does not.
4. **Decide drift or bug** for each relevant change. Read the current code and decide whether it still does what the model says. When it does not, the verification is the thing to update, and it must describe the code as it is now, not as it was.
5. **Rerun, and prove the update can still fail.** A check you updated and never saw fail is unverified. Break the code in a scratch copy; the check must fail. Restore it.
6. **Record the new sync commit** in the skill, with the date and what you confirmed.

## Ship or stop

At most one commit, confined to the verification files. A bug found here goes to the `bug-fix` playbook as a finding, never as a drive-by fix in this run. When every check is `in sync`, ship nothing and say what you ran. When a check is `blocked`, ship the rest and name the blocker.

**Reply:** one line per check with its outcome, the commit it is now in sync at, the command and output behind the outcome, and for a bug the counterexample in the code's terms.
