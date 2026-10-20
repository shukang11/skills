## To-Spec 机制深度设计与工程原理

`to-spec` 负责在长对话接近尾声时，将散落在上下文各处的决策碎片收拢，形成单一真源（Single Source of Truth）。

### 1. 为什么禁止在 `to-spec` 中二次提问？

很多大模型在收到“帮我写个 Spec”时，会反过来问用户“请问这块你想怎么做？”。
`to-spec` 从设计上严禁这种行为：
- 提问是 `grilling` 阶段的职责。
- `to-spec` 是**确定性的收敛器**：它必须假定所有重大分歧在之前的对话中已经解决。如果有微小未决点，它应记录在 `Further Notes` 或 `Out of Scope` 中，而不是阻断文档的产出。

### 2. 测试接缝（Test Seams）的重要性

在 Spec 中尽早规定测试接缝，可以防止后续写出脆弱且重构成本极高的单元测试。
- 优先选择行为级接缝：测输入与最终输出，把内部辅助函数当成黑盒；
- 降低代码重构时测试用例大规模崩塌的风险。

### 3. 与 spec-anchor 协同

生成的文件落盘于 `.agents/notes/proposed/` 目录下，天生满足 `spec-anchor` 的笔记命名契约（`Status: proposed`、`Agent Note:` 标题格式），不仅能被版本管理跟踪，还能通过 `spec-anchor verify` 自动化门禁。
