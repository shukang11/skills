---
name: to-spec
description: 将讨论充分的方案、决议与上下文，无损梳理并固化为符合工程规范的标准 Spec 文档。不进行新访谈，专注合成与收敛。
argument-hint: "本 Spec 的核心主题/文件名 slug 是什么？"
---

# To-Spec — 规格化沉淀

在需求与架构通过讨论（如 `grilling`）基本明确后，将当前上下文中的所有共识、边界和测试策略，一键沉淀为一份严谨的标准规格文档（Spec）。

## 核心工作法则

1. **专注合成，严禁二次访谈（Synthesize, Do NOT Interview）**：
   - `to-spec` 是一个收敛动作。此时**不要再向用户抛出一堆新问题**。
   - 充分检索当前对话历史、代码现状以及先前盘问的决策结论，将其组织整理为结构化文档。
2. **测试接缝决策（Test Seams）**：
   - 必须在 Spec 中明确测试策略在哪个接缝（Seam）切入。
   - 优先选择最高层次、最稳定的公共行为接缝（如外部命令输入/输出、Public API），避免将测试焊死在内部私有实现上。
3. **沉淀至本地规范目录（Local Persistence）**：
   - 默认将生成的 Spec 文档保存至本地约定目录：`.agents/notes/proposed/yyyy-mm-dd-<slug>.md`。
   - 严格遵循规范文档格式，便于后续工具（如 `spec-anchor verify`）校验。

## 标准 Spec 产出模板

```markdown
# Agent Note: <Spec 标题>

Status: proposed

## Problem Statement
- [痛点是什么？在什么场景下暴露？对系统或用户造成了什么阻碍？]

## Solution
- [高层方案综述：核心思路与运作机理]

## User Stories
- [ ] 1. 当 [角色/系统] 执行 [操作] 时，期望产生 [结果]
- [ ] 2. 当 [异常情况] 发生时，系统应 [明确的降级或错误处理]

## Implementation Decisions
- **架构与模块影响**：涉及哪些模块、新增哪些类型/接口契约（给出 TypeScript 类型或核心函数签名原型，但不贴琐碎业务代码）。
- **关键取舍**：记录已否决的替代方案及理由。

## Testing Decisions
- **测试接缝（Seams）**：明确在哪个最高接缝验证（例如：CLI 端到端命令输出、模块门面导出函数）。
- **外部行为用例**：列出核心要覆盖的正常流与边界异常流。

## Out of Scope
- [明确本次迭代坚决不做的事情，严格封死范围蔓延]

## Further Notes
- [后续演进建议、待长期观察的假设或备注]
```

## 执行流程

1. **提取信息**：解析对话中的核心共识、测试策略与范围限制。
2. **生成并落盘**：将合成好的内容写入 `.agents/notes/proposed/<yyyy-mm-dd-slug>.md`。
3. **输出摘要与路径**：向用户展示落盘文档的相对/绝对路径，并提示下一步可以衔接的技能（如 `codebase-design` 或 `tdd`）。
