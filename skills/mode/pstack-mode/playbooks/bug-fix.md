# Bug fix

A signal that goes red for this bug only, before any code changes.

1. Read `how-it-works` when the subsystem is unfamiliar. Read `why-this-way` when the user says this is a regression or used to work. Skip when the symptom already lands on a specific file.
2. Read `diagnosing-bugs`. No business code changes before the red signal exists.
3. Read `codebase-design` when the fix crosses a module boundary. Skip when the change stays inside the current one.
4. When this round left no failing test and the seam is cheap, add the failing test. Skip when it already went red then green.
5. Read `principle-sequence-verifiable-units` and `principle-prove-it-works`. The failure signal comes before the fix.
6. Read `code-review` when the user asks for a review. Else skip.

Read `principle-laziness-protocol` and `principle-fix-root-causes`. The fix covers only the producing point the evidence points at.

When two fixes under the same premise have failed the same gate, read `principle-attack-the-premise`: take the census first, then decide the third fix.

When the user reports a slowdown, or this change reports a measured number, read `principle-explain-the-number`.

Done when: red before the fix, green after, and both output summaries are in the reply.
