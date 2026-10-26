# Bug fix

先有只为这个 bug 飘红的信号，再改代码。

1. 子系统不熟时读 `how-it-works`。用户说这是回归，或以前不是这样时，读 `why-this-way`。症状已经落到具体文件则 skip。
2. 读 `diagnosing-bugs`。红信号之前不改业务代码。
3. 修复要跨过模块边界时读 `codebase-design`。改动留在原边界内则 skip。
4. 本轮没有留下失败测试，并且接缝便宜时，读 `tdd` 补上。已经红过又绿了则 skip。
5. 读 `principles/sequence-verifiable-units.md` 和 `principles/prove-it-works.md`。失败信号先于修复。
6. 用户要求审查时读 `code-review`。否则 skip。

读 `principles/laziness-protocol.md`。修复只覆盖证据指向的产生点。

收工：修复前红、修复后绿，两次输出摘要都在回复里。
