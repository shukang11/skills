# Design

Contracts and spec only. This playbook writes no implementation.

1. Read `how` when existing code is involved. Skip when starting from scratch.
2. Read `grilling` when the call is not settled. Skip when it is.
3. Read `domain-modeling` when terms or state do not line up. Skip when they do.
4. Read `compare-shapes` when two or more shapes remain; switch to `arena` when candidates deserve full attempts or a cross-family check. Skip when the shape is already unique.
5. Read `to-spec`. The trade-offs in `prototypes/compare-shapes-*/decision.md` go into Implementation Decisions.
6. Read `codebase-design`. When it hands a major decision back to `to-spec`, land that first and return to this step.
7. Read `principle-model-the-domain` when the contract carries state, a lifecycle, or mutually exclusive options. State machines and discriminated unions are contract, not implementation.
8. For non-trivial design read `architect`: types, signatures, and the module map are this playbook's contract deliverable. When it needs a multi-shape comparison it opens `arena` itself.

Stop at the public contract and the spec path. No implementation code. When the user moves on to implementing, switch to [feature.md](feature.md) and skip the steps already done.
