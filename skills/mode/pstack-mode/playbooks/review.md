# Review

Review a diff. No code changes.

1. Read `code-review` to pin the baseline, candidate, and task paths. Include current staged, unstaged, and untracked task files when reviewing uncommitted work. With no spec, run the Standards axis alone and say so in the reply.
2. Read `typescript-best-practices` when the diff touches `.ts`/`.tsx`. Else skip.
3. Read `principle-test-behavior-not-implementation` when the diff touches tests. Else skip.
4. Read `blast-radius` when a small diff worries you, or you need the impact surface before shipping. Else skip.

Done when: the two axes' findings and evidence gaps are listed separately, and the reviewed state still matches the recorded candidate. An empty review names the baseline, candidate, and scope.
