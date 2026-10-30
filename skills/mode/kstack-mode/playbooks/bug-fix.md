# Bug fix

先有只为这个 bug 飘红的信号，再改代码。

1. 子系统不熟时读 `how-it-works`。用户说这是回归，或以前不是这样时，读 `why-this-way`。症状已经落到具体文件则 skip。
2. 读 `diagnosing-bugs`。红信号之前不改业务代码。
3. 修复要跨过模块边界时读 `codebase-design`。改动留在原边界内则 skip。
4. 本轮没有留下失败测试，并且接缝便宜时，补上失败测试。已经红过又绿了则 skip。
5. 读 `principle-sequence-verifiable-units` 和 `principle-prove-it-works`。失败信号先于修复。
6. 用户要求审查时读 `code-review`。否则 skip。

读 `principle-laziness-protocol` 和 `principle-fix-root-causes`。修复只覆盖证据指向的产生点。

同一句前提下的修法连续两次没过同一道门时，读 `principle-attack-the-premise`：先普查，再决定第三个修法。

用户报的是性能变差，或这次要报一个测出来的数字时，读 `principle-explain-the-number`。

收工：修复前红、修复后绿，两次输出摘要都在回复里。
