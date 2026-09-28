---
name: handoff
description: 会话续聊的状态交接胶囊。在上下文将满、被迫中断或主动收工时，把当前会话中断点与运行态提炼为临时交接文档，供下一个 Session 无缝接续同一任务。
disable-model-invocation: true
argument-hint: "（可选）下一 Session 想聚焦的目标；留空则由 Agent 从会话推断并标注为 [Pending]"
---

# Handoff — 会话状态交接胶囊

将当前对话上下文提炼为一份临时交接文档（Handoff Document），让下一个 Session 能够无摩擦地接续**同一个任务**。

**默认场景是「被迫中断」**：上下文将满、任务做到一半要收工、需要甩掉上下文包袱但保留线程。这类场景的共同特征是——用户并不知道下阶段目标，接手方需要先恢复现场、再决定动作。

> 本技能只负责 Session 续聊。**跨角色编排（Planner → Worker 的任务派发）不属于本技能范围**，那类交接需要明确的任务包与验收标准，应另用专用技能。

## 目标与落盘位置
- 写入用户操作系统的临时目录（Windows: `%TEMP%`，Linux/macOS: `/tmp` 或 `$TMPDIR`）。
- 文件命名规范：`handoff-<task-slug>-<timestamp>.md`。
- 生成后向用户清晰打印文件的**绝对路径**。

## 与笔记 (notes) 的关系
- **本技能 standalone**：不要求事先存在笔记，没有笔记也一样能生成交接文档。
- **单向引用**：交接文档可以用指针引用已有笔记（如 `.agents/notes/proposed/2025-01-01-foo.md`，**带状态标签**），但不抄录正文。
- 本文件是临时耗材，**不应被其他任何文档引用**。

## 核心撰写纪律（避免信息漂移与污染）

1. **只记录流转状态，不抄录静态物料（No Duplication）**：
   - 严禁大段复制黏贴已有的代码、Diff、Spec、ADR 或 Issue 内容。
   - 一律使用绝对路径、相对路径或 URL 指针引用（如 `docs/adr/0002.md`、`src/auth/jwt.ts:40-60`）。
2. **严防虚假事实传递（Facts vs. Assumptions）**：
   - 接收端的 Agent 会把交接文档视为“不可推翻的合同”。因此，**绝不能将未经测试验证的推论当成事实陈述**。
   - 明确标注：
     - `[Verified Fact]`：通过测试或工具实际验证过的事实。
     - `[Pending / Unverified]`：当前假设、待探明的边界或推测。
3. **禁止补齐（No Fabrication）**：
   - 会话内没有明确记录的内容，**不写**。空缺本身就是有效信息。
   - 尤其针对：下阶段目标、否决某项方案的理由、卡点的根因。**有记录则写，无记录则显式写「无明确记录」，严禁推断编造或事后合理化。**
   - 原因：接收方无法交叉核对，编造的内容会被当作 `[Verified Fact]` 直接采信，危害远大于留白。
4. **脱敏保密（Redaction）**：
   - 彻底过滤任何 API Key、密码、Token 或敏感个人信息。
5. **生成前自检（Self-Audit）**：
   - 逐条回溯每个 `[Verified Fact]` 的验证证据（跑过哪条命令、看过哪个输出）。
   - **无法回溯的，一律降级为 `[Pending / Unverified]`。**

## 交付文档标准骨架

```markdown
# Handoff: <任务简述>
- **Generated**: <ISO-Timestamp>
- **Context / Primary Goal**: <用户明示 | [Pending / Unverified] Agent 推断>

## 1. 中断点 (Where I Left Off)
- 最后完成的操作 / 最后成功的命令或提交
- 进行中但未完成的事项
- 中断前原本打算做的下一步（无记录则写「无明确记录」）
- 工作区状态：分支、是否有未提交改动

## 2. 架构与领域锚点 (Anchors & References)
- 相关规范/ADR/Spec 指针（仅路径，不抄正文）
- 核心涉及模块/Seams: [路径与行号区间]

## 3. 关键决议 (Decisions Made)
- 已拍板的约束或方案
- 放弃的替代方案及理由（**仅限会话内明确讨论过的**；无则写「无明确否决记录」）

## 4. 当前运行态 (Runtime State)
- [Verified Fact] ... (跑通了哪些命令/测试)
- [Pending / Unverified] ... (当前的卡点或待验证假说)

## 5. 接棒指令 (Next Agent Directives)
- **Verify First**: 接手后先复验的 Fact 及具体命令（确认 `[Verified Fact]` 是否仍然成立）
- **Immediate Next Step**: 验证通过后的第一项具体操作
- **Suggested Skills**: （可选）验证通过后再考虑启动的 Skill
```

> `Context / Primary Goal` 与中断点并列，不单独置顶为权威目标——它常由 Agent 推断，必须带可靠性标签：`<用户明示>` 或 `[Pending / Unverified] <推断>`。

## 参数处理
- 用户传入了目标：写入 `Context / Primary Goal` 并标为 `<用户明示>`，据此裁剪交接内容。
- **未传入（常态）**：从会话推断并标为 `[Pending / Unverified]`，**不得因为参数缺失而停下来追问用户**。
