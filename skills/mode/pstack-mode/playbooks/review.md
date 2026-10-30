# Review

审查一段 diff。不改代码。

1. 读 `code-review`。基准点没给时先向用户要。没有 Spec 就只走 Standards 轴，并在回复里写明。
2. diff 里有 `.ts`/`.tsx` 时读 `typescript-best-practices`。否则 skip。
3. 这次 diff 动到测试时，读 `principle-test-behavior-not-implementation`。否则 skip。
4. 要多个模型对抗审查时，读 `interrogate`。它不改代码，只出四桶结论。否则 skip。
5. 小 diff 不放心，或上线前要算影响面时，读 `blast-radius`。否则 skip。

收工：两轴的发现分开列。没有发现时写明基准点和空 diff 或空发现，不写「看起来没问题」。
