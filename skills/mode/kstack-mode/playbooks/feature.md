# Feature

新的或改变的行为，写进代码。按顺序打开技能，不在这里重写它们的判据。

1. 读 `how-it-works`，范围是这次要动的子系统。没有既有代码则 skip。
2. 产品或结构决策还没拍板时读 `clarify-decisions`。已经拍板则 skip。盘问结束前不写实现。
3. 术语或状态对不齐时读 `domain-modeling`。对齐了则 skip。
4. 仍有两个以上实现形状时读 `compare-shapes`。形状已经唯一则 skip。产物是选定的形状，不是生产实现。
5. 共识还没落成 `.agents/notes/proposed/` 里对得上的 spec 时读 `to-spec`。已有则 skip。`prototypes/compare-shapes-*/decision.md` 里的取舍由 `to-spec` 写进 Implementation Decisions。
6. 读 `codebase-design`。它若把重大决策交回 `to-spec`，先落盘再回到本步，直到公共契约写出来。
7. 读 `tdd` 实现。同时读 `principles/sequence-verifiable-units.md` 和 `principles/laziness-protocol.md`。
8. 读 `principles/prove-it-works.md`，跑 spec 里写的接缝。
9. 用户要求审查，或这次 diff 要留给别人看时，读 `code-review`。否则 skip。

两个步骤会写同一文件时，先读 `principles/separate-before-serializing-shared-state.md`。不打开 `code-simplify`。

收工：spec 路径、契约、红过又绿的检查命令和输出摘要都在回复里。
