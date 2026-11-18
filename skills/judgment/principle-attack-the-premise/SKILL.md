---
name: principle-attack-the-premise
description: "Apply when two fixes sharing an assumption fail the same check. State the assumption and test it with the smallest counterexample before attempting another fix. Use per-actor counts when the failure concerns imbalance."
disable-model-invocation: true
---

# Attack the Premise

After two fixes fail the same check, examine the assumption they share before adding another patch.

1. State the common assumption in one sentence. Identify the failed check and the two attempts.
2. Separate a behaviour failure from a missing tool, transport failure, or invalid test setup. Fill an evidence gap before treating it as a code defect.
3. Test the assumption with the smallest reproducible observation or counterexample. Reuse an existing probe, or build one per [Build the Lever](../principle-build-the-lever/SKILL.md).
4. If the evidence contradicts the assumption, revise it and test the revised explanation. If it holds, keep the evidence and investigate another cause.

For imbalance or fairness problems, count which actors hold the imbalance across repeated runs. If the same actors hold it, trace the assignment and consider removing the asymmetry. An even distribution does not establish that assumption as the cause.

This principle checks a fact the current design assumes. [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md) handles a new requirement that changes the design.

**Done when:** name the assumption, the probe and result, and whether the evidence retained or rejected it. State the next evidence needed when the result is inconclusive.
