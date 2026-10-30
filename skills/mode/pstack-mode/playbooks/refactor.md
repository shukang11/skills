# Refactor

外部行为不变，只改结构。

1. 读 `how-it-works`，范围是要动的子系统。
2. 读 `codebase-design`，先写移动后的公共契约。
3. 在搬动代码之前把当前行为钉在接缝测试上。已有能钉住该行为的测试则 skip。
4. 读 `principle-sequence-verifiable-units` 和 `principle-laziness-protocol`，再搬。
5. 读 `principle-prove-it-works`。搬完后的检查与搬之前是同一条。

行为要变时，改走 [bug-fix.md](bug-fix.md) 或 [feature.md](feature.md)，并说明切换。不打开 `code-simplify`，除非用户另外要求清理。

收工：同一条检查在搬动前后都实际跑过，输出摘要在回复里。
