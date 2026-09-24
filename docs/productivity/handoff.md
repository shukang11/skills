## Handoff 机制深度设计与工程原理

`handoff` 的本质不是简单的文本总结或压缩，而是**便携式上下文流转胶囊（Portable Transit Document）**。

### 1. 为什么不是 `/compact` 或 `/clear`？

在会话边界处（Phase Boundary），我们通常有 5 种选择：
1. **Continue**：原地硬聊。缺点：上下文膨胀，容易遗忘早期指令，且 Token 成本剧增。
2. **`/compact`**：原地压缩并留在同一个 Harness/会话窗口。**购买的是压缩（Compression）**。
3. **`/clear`**：原地清空全部上下文。适合任务彻底结束。
4. **Delegate (Subagent)**：派出子代理，执行闭环小任务后收敛。
5. **`/handoff`**：**购买的是可移植性（Portability）**。把上下文转化为跨越空间、工具和时间的文件。

### 2. 核心场景矩阵

| 场景 | 运作方式 |
| :--- | :--- |
| **更换 Agent / Harness** | 从 Claude Code 切换到 Cursor / Codex / Pi-Agent，读取 handoff 文件秒速接盘 |
| **分支分流（Side Task Fork）** | 当前主设计会话不动，写出交接文件启动另一个 Agent 执行原型验证，验证完再交接回主分支 |
| **跨工作区 / 跨仓库跳跃** | 从主业务仓库跳到专用原型仓库，避免把实验性代码杂质污染主干 |
| **人类异步交接 / Code Review** | 同事或另一台设备上的 Agent 开箱即用 |

### 3. 接手协议 (Resumption Protocol)
在新会话中，接棒的 Agent 只需执行：
```text
请阅读临时交接文件 <path/to/handoff.md>，严格遵循其指示开始执行工作。
```
新 Agent 启动后将：
1. 从指针加载真正的规范源，而不是依赖二手概括。
2. 信任 `[Verified Fact]`，审视 `[Pending / Unverified]`。
3. 调用 `Suggested Skills` 指定的工程纪律。
