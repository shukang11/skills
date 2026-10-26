---
name: kstack-mode
description: "统一编排入口。修 bug、做功能、定契约、写规格、做原型、重构、审查、交接、写技能或审计仓库时，先进入本技能，再按 playbook 打开叶子。人显式调用 /kstack-mode。"
disable-model-invocation: true
argument-hint: "这次要完成的任务，一句话"
---

# Kstack mode

你是编排者。选定一个 playbook，读完它，按它的步骤打开叶子技能。入口不代替叶子做事。

## 找到文件

原则和 playbook 跟本文件在同一目录：`playbooks/<name>.md`，`principles/<name>.md`。

叶子按名字解析，读到 `SKILL.md` 再执行：

1. `../<name>/SKILL.md`（项目级拷贝，技能彼此平铺）
2. 否则 `../../engineering/<name>/SKILL.md`
3. 否则 `../../productivity/<name>/SKILL.md`
4. 三处都没有：停下这一步，说明该技能没装。

## 层

上面可以跳过中间，直接打开步骤点名的叶子。

1. **入口**。本文件。人显式唤醒，不凭描述自动开工。
2. **Playbook**。任务的步骤顺序，不是斜杠命令。
3. **会把工作交给下一步的叶子**。`wayfinder`、`clarify-decisions`、`domain-modeling`、`compare-shapes`、`to-spec`、`codebase-design`。`tdd` 只在接缝不清时读 `codebase-design`。
4. **做到本职就停的叶子**。`how-it-works`、`why-this-way`、`prototype`、`diagnosing-bugs`、`code-review`、`code-simplify`、`handoff`、`writing-for-agents`、`agent-ready-repository`。
5. **原则**。没有斜杠命令。步骤点名时才读 `principles/` 里的那一份。

根因和红信号在 `diagnosing-bugs`。红绿和行为测试在 `tdd`。领域结构在 `domain-modeling`。模块边界在 `codebase-design`。保真模拟在 `prototype`。审 diff 在 `code-review`。落地后的残留在 `code-simplify`。会话交接在 `handoff`。这八件事不另建原则文件。

## 关系

叶子末尾若建议去下一个技能，以当前 playbook 的剩余步骤为准。

- `wayfinder` 一次解开一张决策票。地图清空后从 `to-spec` 继续，不在地图会话里写实现。
- `clarify-decisions`、`domain-modeling`、`compare-shapes` 的结论交给 `to-spec` 落盘。
- `to-spec` 之后，要契约就去 `codebase-design`，契约已经清楚就去 `tdd`。
- `codebase-design` 遇到重大或破坏性决策，先交回 `to-spec`，再继续设计。
- `tdd` 只在接口或接缝不清时读 `codebase-design`，读完回到实现。
- `prototype` 走完后，确认要留下的契约改走 design 或 feature playbook。模拟文件留在 `prototypes/`。
- `diagnosing-bugs` 没留下便宜的失败测试时，才补一次 `tdd`。
- `code-review` 读笔记，不调用 `to-spec`。
- `code-simplify` 不出现在 feature 的步骤里。功能开发中被拉起，就按它自己的激活规则停。

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

对不上上面任何一条：在回复里写出一条短顺序，每步一个已安装的叶子或一份原则，然后按那条顺序做。不为此新造技能。

## 原则

用到才读全文。回复里只引用这次读过的原则，并写它改变了哪一个具体选择。

- [principles/laziness-protocol.md](principles/laziness-protocol.md)：在定改动大小，或想加一层、加一条贯穿信号时。
- [principles/separate-before-serializing-shared-state.md](principles/separate-before-serializing-shared-state.md)：两个步骤会写同一个文件、分支或键时。
- [principles/sequence-verifiable-units.md](principles/sequence-verifiable-units.md)：工作要分成多步或多段提交时。
- [principles/prove-it-works.md](principles/prove-it-works.md)：准备说做完了时。

## 回复

点名选了哪个 playbook。跳过的步骤带理由。声称做完时带上实际跑过的检查和输出摘要。
