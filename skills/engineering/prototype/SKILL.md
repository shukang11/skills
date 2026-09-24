---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a specific question**. The question decides the shape.

## 1. Pick a Branch

Identify which question is being answered:

- **"Does this logic / state model feel right?"** → **Logic Prototype**
  - Build a single, self-contained, zero-dependency HTML file.
  - Save to `prototypes/<topic>-prototype.html` (aligned with `spec-anchor` preview conventions).
  - Include:
    1. **Visible intro**: 1 paragraph stating the exact question being answered.
    2. **State panel**: clean, human-readable display of the current internal state (not raw JSON).
    3. **Free-play buttons**: 1 button per action/event to trigger state transitions in any order.
    4. **Guided walkthroughs**: tabbed scenarios representing tricky edge cases with step-by-step ordered buttons.
  - **Portable module constraint**: Keep the core logic (reducer/state machine/pure functions) in a clean, pure `<script>` block without DOM references, so it can be lifted directly into production code later.

- **"What should this look like?"** → **UI Prototype**
  - Generate 3 radically different UI structural variants (not just different colors/tweaks).
  - Mount on an existing page/route via `?variant=A/B/C`, or create a throwaway preview under `prototypes/`.
  - Provide a floating bottom-center switcher bar with keyboard arrow navigation (`←` / `→`) to flip between variants seamlessly.

## 2. Core Rules (Throwaway Discipline)

1. **Throwaway from day one**: Code is written under prototype constraints (skip tests, skip deep error handling, skip abstractions).
2. **Trivial to run**: Double-click to open in browser, or run zero-config in `spec-anchor dev`.
3. **No production persistence**: In-memory state only. Never mutate production databases.
4. **Extract only the validated core**:
   - For logic prototypes: lift only the validated reducer / state machine into production.
   - For UI prototypes: take the winning structural elements and rewrite cleanly into the production component.
5. **No production pollution**: Prototypes stay in `prototypes/` as primary source evidence, and must never be bundled into production builds.
