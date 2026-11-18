---
name: to-spec
description: "Synthesize a settled discussion into one standard spec document and write it to .agents/notes/proposed/. No interview: this is convergence only. Use when requirements, boundaries, and test strategy are agreed and need to land on disk before design."
disable-model-invocation: true
argument-hint: "which settled discussion becomes the spec"
---

# To spec

Once requirements and architecture are settled in discussion (for example through `grilling`), fold every agreement, boundary, and test decision from this conversation into one rigorous spec.

## Working rules

1. **Synthesize, do not interview.** This is a convergence step: no new question batches. Mine the conversation history, the current code, and the decisions already made, and organize them into a structured document.
2. **Decide the test seams.** The spec must say which seam the tests enter at. Prefer the highest, most stable public behaviour seam (a CLI's input and output, a module's exported surface) over one welded to internal implementation. Fewer seams is better; the ideal number is one. Confirm the seams with the user.
3. **Land it in the agreed place.** Default path: `.agents/notes/proposed/<yyyy-mm-dd>-<slug>.md`, following the project's own format so downstream tooling (`spec-anchor verify`, for instance) can check it.
4. Use the project's domain glossary vocabulary throughout, and respect any ADRs in the area you are touching.

## Spec template

```markdown
# Agent Note: <spec title>

Status: proposed

## Problem Statement
- [What is the pain, in what scenario does it surface, what does it block?]

## Solution
- [The shape of the answer: core idea and how it works]

## User Stories
- [ ] 1. As a [actor], when I [action], I expect [result]
- [ ] 2. When [failure case] happens, the system should [explicit degradation or error]

## Implementation Decisions
- **Architecture and modules**: which modules, which new types or interface contracts (type signatures or function shapes, not trivial business code).
- **Trade-offs**: the alternatives rejected, and why.

## Testing Decisions
- **Seams**: the highest seam each behaviour is verified at.
- **Behaviour cases**: the normal flows and the edge failures that must be covered.

## Out of Scope
- [What this iteration deliberately does not do. This is where scope creep dies.]

## Further Notes
- [Later evolution, assumptions to watch.]
```

## Steps

1. **Extract.** Pull the agreed points, test strategy, and scope limits out of the conversation. If this round produced `prototypes/compare-shapes-<slug>/decision.md`, that file is the authority on trade-offs; write them into Implementation Decisions.
2. **Write and land.** Write the spec to `.agents/notes/proposed/<yyyy-mm-dd-slug>.md`.
3. **Report.** Give the user the path and name the next skill that can pick it up (usually `codebase-design`).

## Done when

- The spec file exists at the reported path, `Status: proposed`, with every template section either filled or explicitly empty.
- The test seams are named and the user confirmed them.
- The reply names the next skill in the chain.
