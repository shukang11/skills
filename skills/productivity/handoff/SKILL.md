---
name: handoff
description: 将当前会话状态、进展与待办紧凑提炼为便携式交接胶囊（Handoff），供新会话、跨 Agent 或跨 Harness 无缝接棒。
argument-hint: "下一个会话/Agent 的具体核心目标是什么？"
disable-model-invocation: true
---

# Handoff — 会话状态交接胶囊

将当前对话上下文提炼为一份便携式的交接文档（Handoff Document），让全新的 Agent 或 Session 能够无摩擦地立刻继续工作。

## 目标与落盘位置
- 写入用户操作系统的临时目录（Windows: `%TEMP%`，Linux/macOS: `/tmp` 或 `$TMPDIR`）。
- 文件命名规范：`handoff-<task-slug>-<timestamp>.md`。
- 生成后向用户清晰打印文件的**绝对路径**。

## 核心撰写纪律（避免信息漂移与污染）

1. **只记录流转状态，不抄录静态物料（No Duplication）**：
   - 严禁大段复制黏贴已有的代码、Diff、Spec、ADR 或 Issue 内容。
   - 一律使用绝对路径、相对路径或 URL 指针引用（如 `docs/adr/0002.md`、`src/auth/jwt.ts:40-60`）。
2. **严防虚假事实传递（Facts vs. Assumptions）**：
   - 接收端的 Agent 会把交接文档视为“不可推翻的合同”。因此，**绝不能将未经测试验证的推论当成事实陈述**。
   - 明确标注：
     - `[Verified Fact]`：通过测试或工具实际验证过的事实。
     - `[Pending / Unverified]`：当前假设、待探明的边界或推测。
3. **脱敏保密（Redaction）**：
   - 彻底过滤任何 API Key、密码、Token 或敏感个人信息。
4. **下一阶段技能与动作指引（Actionable Directives）**：
   - 包含 `Suggested Skills`，指明下一任 Agent 第一步应该调用的 Skill（如 `/tdd`、`/code-review` 等）。
   - 如果用户传入了参数，将其作为下一个会话的目标并针对性裁剪交接内容。

## 交付文档标准骨架

```markdown
# Handoff: <任务简述>
- **Generated**: <ISO-Timestamp>
- **Context / Primary Goal**: <下阶段核心目标>

## 1. 架构与领域锚点 (Anchors & References)
- 相关规范/ADR: [路径]
- 核心涉及模块/Seams: [路径与行号区间]

## 2. 关键决议 (Decisions Made)
- 已拍板的约束或方案（列出明确放弃的替代方案及理由，防止接手者重新争论）

## 3. 当前运行态 (Runtime State)
- [Verified Fact] ... (跑通了哪些命令/测试)
- [Pending / Unverified] ... (当前的卡点或待验证假说)

## 4. 接棒行动指令 (Next Agent Directives)
- **Immediate Next Step**: 接手后执行的第一项具体操作
- **Suggested Skills**: 下一任 Agent 建议启动的 Skill
```
