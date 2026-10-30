# Review

Review a diff. No code changes.

1. Read `code-review`. If no fixed point was given, ask for one. With no spec, run the Standards axis alone and say so in the reply.
2. Read `typescript-best-practices` when the diff touches `.ts`/`.tsx`. Else skip.
3. Read `principle-test-behavior-not-implementation` when the diff touches tests. Else skip.
4. Read `interrogate` when you want several models trying to break it. It changes no code and returns only the findings a run proves. Else skip.
5. Read `blast-radius` when a small diff worries you, or you need the impact surface before shipping. Else skip.

Done when: the two axes' findings are listed separately. An empty review states the fixed point and either an empty diff or no findings; it never says "looks fine".
