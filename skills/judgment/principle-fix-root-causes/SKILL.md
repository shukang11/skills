---
name: principle-fix-root-causes
description: "Apply when debugging. Trace each symptom to its root cause and fix it there; reproduce first, ask why until you reach it, and keep a guard only when the state it handles is legitimate."
disable-model-invocation: true
---

# Fix Root Causes

When debugging, do not fix symptoms. Trace every problem to its root cause and fix it there.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about, and the real bug remains. Root-cause fixes are slower upfront but reduce total debugging time.

**Pattern:**
- Reproduce first
- Ask "why" until you hit the root cause
- Do not add guards. A guard is a fix only when the state it handles is legitimate. A nil check that silences a crash, where the null came from a bug upstream, moves the error instead of fixing it.
- If a workaround needs a paragraph-long comment to justify it, the code is wrong (fix the code, not the comment)
- Check for the pattern, not just the instance (grep for the same pattern, fix all instances)
- When stuck, instrument. Don't guess (add logging, read the actual error)

**Restart bugs: suspect state before code**

When something "fails after restart," suspect stale persistent state first: config files, caches, lock files, serialized state. If clearing a state file restores behavior, prioritize state validation as the fix.

Building the reproduction loop is the `diagnosing-bugs` skill's job.

**Reply:** name the producing point, the symptom point, and how many other places share the pattern. For a guard you kept, say whether it blocks an impossible state or only moves the error. Fixes that live outside this change become todos, not claims.
