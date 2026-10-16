---
name: agent-ready-repository
description: >-
  Audits a repository as a working environment: entry points, authoritative
  sources, directory boundaries, workflows, templates and validation — plus
  where a human is still forced to step in. Produces a per-item adjudicable
  recommendation table in which every item carries an exit (runnable check /
  default path / explicit human bookkeeping). Read-only; stops at
  recommendations and never executes remediation. Use when the user explicitly
  asks to make a repository agent-ready, improve zero-context onboarding,
  reorganize project knowledge, validate multi-agent readiness, or asks why a
  project keeps requiring their personal attention.
disable-model-invocation: true
---

# Agent-ready repository

把仓库建设成零上下文 Agent 可安全工作的环境。目标不是“文档齐全”，而是让真实任务形成短而可靠的闭环：

`任务意图 → 唯一入口 → 最小事实集 → 正确动作 → 确认边界 → 验证 → 交付`

## 使用边界

- 只有用户明确调用本 Skill 或明确要求开展同类仓库整改时使用。
- 默认只读审计。**本技能止于建议**：不执行整改、不代排优先级、不生成“下一步 3 件事”。
- 用户接受建议后另行进入实施阶段时，整改顺序与复验清单见 [implementation-sequence.md](references/implementation-sequence.md)。
- 移动、删除目录，替换权威来源或改变模块所有权前，必须单独说明影响并取得确认。
- 不强制项目采用 `README.md`、`AGENTS.md`、`docs/topics/` 或 spec-anchor；先识别现有约定。
- 项目根有 `site.config.yaml`（已接入 spec-anchor）时，读 [spec-anchor-projects.md](references/spec-anchor-projects.md)：它说明 `init` 已铺的哪些东西不必再建议、要检查哪些是否真的接上，以及问题类别如何对齐「原则 N」。未接入时不要为完成审计在项目里执行 `spec-anchor init`。
- **不做价值判断**：“这个项目还该不该继续”“精力配比对不对”归用户 vault 的 `01-项目库/00-项目台账.base`（`is_at_risk` / `days_idle`）与 `99-项目方法论/`，不进本技能。

## 第一步：定义真实任务与仓库认知地图

选 2–5 个能代表项目日常工作的任务，覆盖：定位并修改已有功能 / 新建模块、版本、页面或业务对象 / 更新动态事实 / 跑测试、构建、发布 / 处理废弃、异常或跨模块场景。没有代表任务时先向用户确认最常见的工作，不要只检查文档是否存在。

从根入口只读识别下列角色（文件名可以不同）：总入口、全局规则、模块地图、动态索引、事实来源、工作流、模板、验证入口、废弃内容。记录 Agent 从任务描述到第一个正确事实文件的实际路径；不要先全库搜索来掩盖入口问题。

## 第二步：跑两遍零上下文基线

**第一遍 · Agent 侧**：派发不携带历史对话的 Agent 完成代表任务。提示词只描述真实目标，不泄露正确路径与预期答案；要求返回实际读取顺序、事实来源、不可推断项、结果与阻塞点；至少安排一次较轻量 Agent，观察跳读、扩读、弱推理时是否仍然安全。基线阶段不修文件。

**第二遍 · 人侧**：同一任务换到人这一侧，观察 **人在哪里被迫出手**。产出只分两桶：`能离开人的` / `不能离开人的`。

- **必须有人在环**：这一遍需要真人在场回答或执行。人不在时，记「缺源」并跳过该遍，**严禁由 Agent 模拟“人会在哪里出手”**。
- **只看不猜**：只记录实际观察到的出手点（步骤 + 位置）。缺证据时写“缺源”，**严禁推断人在哪出手**——这是最大的幻觉源。
- **不追求消除所有人工注意点**：有些缓冲迫使人看清全局，属于有意保留，应记到出口③。
- 因「缺源」跳过的条目：出口归属直接标 ③，裁决列标「待议」。

两遍基线的提示词与指标见 [acceptance-tests.md](references/acceptance-tests.md)。

## 第三步：诊断根因并逐条挂出口

按 **P0–P3** 影响分级、按**根因层级**（文档缺失 / 多权威副本 / 目录与模块边界 / 工作流默认与确认 / 模板完整性 / 机械验证）定位问题，判据见 [audit-model.md](references/audit-model.md) 与 [architecture-patterns.md](references/architecture-patterns.md)。每条建议都必须挂到下列一个出口。

## 三出口门禁

每条建议**必须有一个出口**；门禁要求的是“有出口”，**不是“必须是出口①”**。

- **出口① 造眼睛**：会跑的检查——lint / test / CI / 只读守卫。
- **出口② 收窄路**：会自己出现的默认——模板 / 目录约定 / 脚手架 / 唯一写法。
- **出口③ 人侧记账**：明确划给“必须人来”的动作。

不可机械验证的项硬塞成坏检查是反效果：只会增加噪声并制造“已验证”的假象，应改记出口③。

## 交付格式

按**可裁决表**交付，每条建议一行：

| 问题 | 影响面 P0–P3 | 出口归属 | 建议动作 | 接受代价 | 裁决 |
|------|------|------|------|------|------|

- **裁决列留空**：技能不预填、不给倾向。
- **接受代价**必须可判定，写清接受这条建议要付出的具体东西：新增或修改哪个脚本、目录约定或流程，每次改动多几步，谁需要记住什么。写不出来说明这条建议还不具体，退回重写，不要让它退化成形容词栏。
- 表前附本次目标任务与基线证据（含人侧两桶）；表后只列仍会影响工作的残留事项，不写“下一步 3 件事”。

**完成判据**（三者同时满足才算交付）：

- 表中每条建议都有出口归属（①/②/③），无空缺。
- 每条出口③都写明落在哪个人的关口动作上（例如定意图、合并审查、发版），并说明为什么归不进①或②。两样都写不出的，退回重想。
- 人侧两桶要么附观察证据，要么明确标「缺源」，不含任何推断。
- 仍会影响工作的残留事项已在表后列出。

案例见 [example-work-assistant.md](references/example-work-assistant.md)。
