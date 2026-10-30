---
name: kstack-mode
description: "统一编排入口。修 bug、做功能、定契约、写规格、做原型、重构、审查、交接、写技能或审计仓库时，先进入本技能，再按 playbook 打开叶子。人显式调用 /kstack-mode。"
disable-model-invocation: true
argument-hint: "这次要完成的任务，一句话"
---

# Kstack mode

你是编排者。选定一个 playbook，读完它，按它的步骤打开叶子技能。入口不代替叶子做事。

## 找到文件

Playbook 跟本文件在同一目录：`playbooks/<name>.md`。判据是独立技能，在 `../../judgment/<name>/SKILL.md`。

叶子按名字解析，读到 `SKILL.md` 再执行：

1. `../<name>/SKILL.md`（项目级拷贝，技能彼此平铺）
2. 否则 `../../engineering/<name>/SKILL.md`
3. 否则 `../../productivity/<name>/SKILL.md`
4. 否则 `../../judgment/<name>/SKILL.md`
5. 都没有：停下这一步，说明该技能没装。

## 层

上面可以跳过中间，直接打开步骤点名的叶子。

1. **入口**。本文件。人显式唤醒，不凭描述自动开工。
2. **Playbook**。任务的步骤顺序，不是斜杠命令。
3. **会把工作交给下一步的叶子**。`wayfinder`、`clarify-decisions`、`domain-modeling`、`compare-shapes`、`arena`、`to-spec`、`codebase-design`、`architect`、`figure-it-out`。
4. **做到本职就停的叶子**。`how-it-works`、`why-this-way`、`teach`、`prototype`、`diagnosing-bugs`、`code-review`、`interrogate`、`blast-radius`、`code-simplify`、`correct`、`handoff`、`writing-for-agents`、`agent-ready-repository`、`unslop`、`swarm`、`show-me-your-work`、`create-verification-skill`、`maintain-verification-skill`、`typescript-best-practices`。
5. **判据**。`../../judgment/<name>/SKILL.md`，是独立技能，可以 `/` 直点。跨叶子反复要用的判据放这里；只属于某一个叶子的判据写在那个叶子的正文里（`diagnosing-bugs` 的判据段、`code-review` 的 Standards 轴）。

根因和红信号在 `diagnosing-bugs`。领域结构在 `domain-modeling`。模块边界在 `codebase-design`。保真模拟在 `prototype`。审 diff 在 `code-review`。落地后的残留在 `code-simplify`。去 AI 腔与简明表达在 `unslop`。会话交接在 `handoff`。这九件事不另建判据。

## 并行

三个都能开多个候选或多个工人。按要什么选，别叠。

- `compare-shapes`：形状还没定，手工摆两个以上对照物。成本最低，不并行。
- `arena`：同一个产物要几个完整尝试，再合成一个。带异族模型交叉评分。
- `swarm`：要覆盖不同切片、或赛马比快，父级只收一份报告，不合成产物。

## 关系

叶子末尾若建议去下一个技能，以当前 playbook 的剩余步骤为准。

- `wayfinder` 一次解开一张决策票。地图清空后从 `to-spec` 继续，不在地图会话里写实现。
- `clarify-decisions`、`domain-modeling`、`compare-shapes` 的结论交给 `to-spec` 落盘。
- `to-spec` 之后，去 `codebase-design` 产出公共契约。
- `codebase-design` 遇到重大或破坏性决策，先交回 `to-spec`，再继续设计。
- `prototype` 走完后，确认要留下的契约改走 design 或 feature playbook。模拟文件留在 `prototypes/`。
- `code-review` 读笔记，不调用 `to-spec`。
- `code-simplify` 不出现在 feature 的步骤里。功能开发中被拉起，就按它自己的激活规则停。
- `unslop` 用于文档、规范或文本输出的脱水清洗，遵循 ASD-STE100，不改动业务逻辑。

## 选 playbook

先把对上的 playbook 步骤原文写进待办，再写这个任务自己的待办。决定跳过的步骤留在列表里，写 `skip:` 和一句理由。

- 报错、异常、回归、失败、性能变差 → [playbooks/bug-fix.md](playbooks/bug-fix.md)
- 新的或改变的行为，并且要写进代码 → [playbooks/feature.md](playbooks/feature.md)
- 只要契约和规格，明确先不写实现 → [playbooks/design.md](playbooks/design.md)
- 终点说得清、路线一次会话装不下 → [playbooks/wayfinder.md](playbooks/wayfinder.md)
- 用保真 HTML 模拟一段产品逻辑或交互 → [playbooks/prototype.md](playbooks/prototype.md)
- 外部行为不变，只改结构 → [playbooks/refactor.md](playbooks/refactor.md)
- 审查一段 diff，不要改代码 → [playbooks/review.md](playbooks/review.md)
- 用户明确要求清理残留、收紧或 simplify → [playbooks/simplify.md](playbooks/simplify.md)
- 中断、交接，或接续一份已有交接 → [playbooks/handoff.md](playbooks/handoff.md)
- 写或改 `SKILL.md`、`AGENTS.md`、README、SPEC → [playbooks/authoring.md](playbooks/authoring.md)
- 仓库能否让 Agent 开工，只要建议表 → [playbooks/repo-audit.md](playbooks/repo-audit.md)
- 只问现在怎么工作，或为什么长这样，不改代码 → [playbooks/investigate.md](playbooks/investigate.md)

对不上上面任何一条：在回复里写出一条短顺序，每步一个已安装的叶子或一条判据，然后按那条顺序做。不为此新造技能。

## 判据

用到才读全文。回复里只引用这次读过的判据，并写它改变了哪一个具体选择。

- `principle-laziness-protocol`：在定改动大小，或想加一层、加一条贯穿信号时。
- `principle-separate-before-serializing-shared-state`：两个步骤会写同一个文件、分支或键时。
- `principle-sequence-verifiable-units`：工作要分成多步或多段提交时。
- `principle-prove-it-works`：准备说做完了时。
- `principle-attack-the-premise`：同一句前提下的修法连续两次没过同一道门时。
- `principle-explain-the-number`：准备相信、汇报或据此行动一个测出来的数字时。
- `principle-test-behavior-not-implementation`：写、改或保留一条测试时。
- `principle-model-the-domain`：写有状态的逻辑，或分支与形状假设开始重复时。
- `principle-exhaust-the-design-space`：面对没有先例的新交互或架构选择时。
- `principle-fix-root-causes`：调试时，准备动手改产生点之前。
- `principle-boundary-discipline`：接线校验、错误处理或框架适配层时。
- `principle-type-system-discipline`：设计类型、审函数签名，或写静态类型语言时。
- `principle-build-the-lever`：非琐碎的工作开始之前。
- `principle-encode-lessons-in-structure`：同一句指令要写第二遍，或同一个纠正再次出现时。
- `principle-guard-the-context-window`：上下文在涨，或要铺开并行时。
- `principle-minimize-reader-load`：审或改一段难追的代码时。
- `principle-never-block-on-the-human`：想问「要不要我做 X」而这件事可逆时。
- `principle-outcome-oriented-execution`：计划内的重写或迁移开始之前。
- `principle-redesign-from-first-principles`：要把新需求接进既有设计时。
- `principle-make-operations-idempotent`：写命令、脚本、循环或批量操作时。
- `principle-migrate-callers-then-delete-legacy-apis`：换内部接口、改名、改签名之前。

## 回复

点名选了哪个 playbook。跳过的步骤带理由。声称做完时带上实际跑过的检查和输出摘要。
