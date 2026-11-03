---
name: create-formal-verification-skill
description: "Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least, in any language, with whichever tool the repo can actually run. Use for /create-formal-verification-skill, \"model-check this race\", \"prove this invariant\", or when concurrency, retries, state machines, parsers, or unsafe code need more than tests."
disable-model-invocation: true
argument-hint: "the area, promise, or bug to verify"
---

# Create a formal verification skill

A test checks the cases someone thought to write. Formal verification checks every case in a stated scope: every order of steps in a model, every input up to a bound, or every input. This skill finds the part of the repo where that matters most, verifies one property of it, and leaves a project-local skill that lets the next agent recheck a change against that property. Write that skill for an agent who reads it cold, mid-change, and has never seen your work. The user must be able to trust the result and act on it without learning the verification language.

## Pick the target from the code

Answer from the codebase, and ask the user only what you cannot observe. If the user named an area, a promise, or a bug, start there.

A good target is a promise the code makes where a break harms users and tests rarely reach the case that breaks it. Choose the strongest such target in the repo, not the one that is easiest to verify, and say in one sentence why this promise rather than the next one down.

## Let the question choose the tool

Inventory what the repo and the machine can already run before you name a tool. Then match the question:

- **Whether events can happen in a bad order** (two writers on one record, a lease that expires mid-write, a retry that overlaps the first attempt): model-check a small model of the design. TLA+ with TLC is the default for that in any language.
- **Whether the code itself behaves for every input** (memory safety, overflow, a data-structure invariant, a parser that must not loop): verify the code. A race detector, a sanitizer, a fuzz target, or a solver-backed verifier, whichever this language has.
- **Whether a property holds at every size**, where a bound is not enough: a proof.

Prefer, in this order: a tool already wired into the repo (a spec under `specs/`, a property-test suite, a fuzz target, `-race`, `loom`, `kani`), a tool already on the machine, then a new one.

If no verifier runs on this language, say so, and test the real code with generated inputs. Never let a hand-written model of a function stand in for the function.

## Provisioning

Name the tool, what it costs to install, how long its first run takes, and whether it needs the network. Then ask once before you install anything on the machine or add a dependency to the repo. Do not install silently, and say which file you touched when you do. If the user declines, or the tool will not install, take the generated-input fallback and record that choice in the hand-off. A check nobody agreed to install is a check nobody reruns.

## What makes it good

- **True to the code.** Every part of the model or proof points to code a reviewer can open. What the verification treats as one indivisible step is one indivisible step in the code. Names come from this repo.
- **Able to fail.** A check you have never seen fail proves nothing. Show each property failing on a broken variant of the code it guards: a removed check, a reordered step, a widened type.
- **Findings stay findings.** When the current code breaks the property, report it with the counterexample in the code's terms. Do not weaken the property or the model until it passes, and do not change product code unless the user asks.
- **Honest about scope.** Say what is verified, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, not the whole system.
- **Readable without the tool.** State the property and the harm in one plain sentence each. Tell a counterexample as a short sequence of steps in the code's words. When the break is a bad order of events, hand the sequence over through the `statechart` skill, which draws it as states and arrows in the reader's words.
- **Cheap to rerun.** One command, a pinned tool version, and a run short enough that the next agent uses it on every relevant change.
- **Kept in step with the code.** Record which files and functions each check covers, and the commit at which you last confirmed the verification describes them.

## Generate the skill

Write `.agents/verify/<app>-formal/SKILL.md`, named `verify-<app>-formal`. It sits beside the driving skill `create-verification-skill` builds, and stays outside `skills/` for the same reason: it is read by path, not registered as a slash command. Sections, each grounded in what this repo actually has:

- **Property** — one plain sentence, and the harm in another. No tool words, no variable names.
- **Scope** — the files and functions covered, the bounds, the assumptions, and what each one costs to change.
- **Run** — one command, the pinned tool version, and what a pass and a fail print.
- **Read the result** — how to tell a counterexample from a modeling error, and what to do with each.
- **Re-check when** — the paths that make the check stale. Merges and refactors that skip this skill go to `maintain-formal-verification-skill`.
- **Not covered** — what the check does not say.

## Prove it before handing it over

1. Run it as written. When the current code breaks the property, report that as a finding, with the counterexample in the code's terms, and keep the property as stated.
2. Break the code on purpose in a scratch copy: remove the check, reorder the step, widen the type. The check must fail.
3. Restore, rerun, confirm it passes, and record the commit that is now in sync with the code.
4. A check that never failed is a draft, not a deliverable. Do not hand it over.

## Hand off

Say what is verified, with which tool and which bounds, what the check found, what it does not cover, and the one command that reruns it.

**Reply:** the property in one plain sentence, the tool and why it rather than the alternative, the finding or the pass with its command and output, what the generated skill covers and leaves out, and what you installed or declined to install.
