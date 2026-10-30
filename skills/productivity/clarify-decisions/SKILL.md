---
name: clarify-decisions
description: "Adversarial interview before any code: build the design-decision tree, advance its frontier a round at a time, and settle the plan before implementation starts."
disable-model-invocation: true
argument-hint: "which plan, decision, or requirement to grill"
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## Before the interview is over

- **Write no code and make no irreversible file change** until the frontier is empty and the user has said the understanding is shared.
- Each round's question body carries the trade-off: why this branch needs a call, what each option costs.
- The interview ends when three things hold at once: every key decision on the frontier is settled (scope, core architecture, dependencies, test strategy, failure handling); you have given a compact summary of the plan and the user explicitly agreed it is the same plan you have; and you have named the skill that picks it up, usually `to-spec`.
