---
name: principle-experience-first
description: "Apply when product, UX, or feature-scope tradeoffs come up. Choose user delight over implementation convenience; ship fewer polished features over more rough ones."
disable-model-invocation: true
---

# Experience first

When implementation convenience conflicts with user delight, choose delight.

- Every feature, control, and option must be justified.
- Ship less, ship better: three polished features beat ten rough ones.
- Prototype before committing. Design decisions are cheaper in throwaway HTML than in production code.
- Get the details right: transitions, alignment, spacing, feedback, error states.
- Tighten the core loop. Every feature either serves the central workflow or gets out of the way.

The user is whoever consumes the work. For a UI that is the end user. For a library or an internal API it is the colleague who imports it. The engineer who maintains the code next is a user too. Weigh their experience the same way, and explain impact from their perspective.

Foundations should serve the experience. The `principle-model-the-domain` skill governs the *sequence* of work. This one governs the *target*.

**Reply:** name the user you optimized for, the option you cut or kept for their sake, and the detail you refused to leave rough.
