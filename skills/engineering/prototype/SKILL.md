---
name: prototype
description: "Build a high-fidelity, disposable simulation that a person can click through to settle a product-logic or interaction question. Lives in prototypes/, never ships. Use before committing to a shape you cannot judge on paper."
disable-model-invocation: true
argument-hint: "the piece of logic or interaction to make visible"
---

# Prototype

A prototype is throwaway code that answers one question. The question decides the shape; getting it wrong wastes the whole prototype.

## Pick a branch

Identify the question from the prompt, the surrounding code, or by asking if the user is around.

- **"Does this logic or state model feel right?"** → [LOGIC.md](LOGIC.md). One self-contained HTML file a non-developer can drive: free-play buttons plus guided walkthroughs through the cases that are hard to reason about on paper.
- **"What should this look like?"** → [UI.md](UI.md). Several radically different variations on one route, switchable by URL parameter and a floating bottom bar.

If the question is genuinely ambiguous and nobody is reachable, default to whichever branch matches the surrounding code (backend module → logic; page or component → UI) and state the assumption at the top of the prototype.

## House rules

One simulation per product question. A second structural option is a `compare-shapes` job, not a second look inside this prototype.

- The entry is `prototypes/index.html`: navigation on the left, content on the right. Links inside the content area are relative paths to local HTML, so navigation survives the jump.
- Double-clicking `index.html` works. No local server.
- Shared styles in `prototypes/css/`, shared scripts in `prototypes/js/`, shared logic in `prototypes/shared/`. Plain `<script src>`, never `type="module"`.
- Navigation lists this simulation's pages only, never `prototypes/compare-shapes-*`.
- No production database, and `prototypes/` never enters the production build.
- Throwaway from day one and named like it: sit it next to what it prototypes so the context is obvious, and make a casual reader see at a glance that it is not production. Obey the project's existing routing convention; do not invent a new top-level structure.
- No tests, no error handling beyond what keeps it runnable, no abstractions. The point is learning fast.
- Surface the state. After every action, render the whole relevant state so the user can see what changed.

## Done when

- Double-click `prototypes/index.html`: the left nav opens each page, in-content links jump, and the nav is still there.
- The reply carries the entry path and the one piece of logic or interaction this simulation exists to make visible.
- Any decision that survives moves to the `docs/` topic that owns the contract, implemented by real code later. It does not become a second spec inside the prototype.
- The prototype itself is captured as a primary source: a throwaway branch, outside main, with a pointer to it from the implementation note.

## Output

`prototypes/index.html`, the content pages, and whatever `css/`, `js/`, `shared/` they need.
