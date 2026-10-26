# Design

只要契约和规格。本 playbook 不写实现。

1. 要动既有代码时读 `how-it-works`。从零开始则 skip。
2. 决策还没拍板时读 `clarify-decisions`。已经拍板则 skip。
3. 术语或状态对不齐时读 `domain-modeling`。对齐了则 skip。
4. 仍有两个以上形状时读 `compare-shapes`。形状已经唯一则 skip。
5. 读 `to-spec`。`prototypes/compare-shapes-*/decision.md` 里的取舍写进 Implementation Decisions。
6. 读 `codebase-design`。重大决策交回 `to-spec` 时先落盘再回到本步。

停在公共契约和 spec 路径。不打开 `tdd`。用户接着要实现时，改走 [feature.md](feature.md)，已完成的步骤 skip。
