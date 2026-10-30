---
name: sharpen
description: "Rewrite a prompt deeper, not bigger, before the work starts: what a top professional would do that the user did not ask for, the rawest material they would start from, their methods and tools, and what outside the two of you proves the result. Use for /sharpen. Returns the rewritten prompt and does not do the task."
disable-model-invocation: true
argument-hint: "the prompt to rewrite"
---

# Sharpen

The user wants a deeper version of the task, not a bigger one. Answer four questions in this order before you touch the wording:

1. What would a top professional in this field do here that the user is not asking for?
2. What is the rawest material they would start from, instead of what has already been digested for the user?
3. Which specific methods and tools would they use?
4. What, other than you or the user, would show the result is right?

Then hand back the user's prompt rewritten to ask for exactly that.

## Bounds

- **Deeper, not bigger.** Add what changes the quality of the answer: the source, the method, the check. Do not add requests that only lengthen the work.
- **Leave the user's calls open.** Product, scope, and preference choices stay as choices in the rewrite. Do not decide them for the user.
- **Do not do the task.** No code, no file edits, no research past what naming the method requires. The output is a prompt, not the work it asks for.
- **The output is the prompt.** Rewrite it in the user's voice, ready to send. Put your reasoning in at most one short line above it, not in an essay.
- This skill runs on a prompt before any playbook starts. It never runs inside one.

**Reply:** the rewritten prompt in one block, and one line naming which choices you left open and which outside check it now asks for.
