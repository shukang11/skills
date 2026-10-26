# 上游技能清单

这张表钉住两个合集在某一天的全部技能。以后对更新，用路径比，不要用记忆。

- 上游多出来的路径是新增。先写成「未标记」。
- 这张表有、上游没有的路径，是上游删了。在处置旁边注明。
- 「不需要」只由你改。这里没有替你划掉任何一条。
- 账记的是路径和名字。对方改了正文、路径没变，这张表看不出来。已吸收的那几条，要看内容就打开链接里钉住的那一版，再和本地比。

一个本地技能可以接住好几条上游名字。那些上游名字下次还在，就不算新增。

| | |
| --- | --- |
| 快照日 | 2026-10-26 |
| Matt Pocock | [`mattpocock/skills`](https://github.com/mattpocock/skills) @ [`5beb35b`](https://github.com/mattpocock/skills/commit/5beb35b040e3de97e54fa9e386d7e42d15c295c2)，2026-10-19，38 个 |
| poteto | [`poteto/plugins`](https://github.com/poteto/plugins) @ [`74dd229`](https://github.com/poteto/plugins/commit/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12)，2026-06-06，69 个 |
| 已吸收 | 25 |
| 未标记 | 82 |

处置只有三格：`已吸收`、`不需要`、`未标记`。

## 怎么对下一次

浅克隆两个仓库，列出每个 `SKILL.md` 的路径，和本表「路径」列比。

```bash
git clone --depth 1 https://github.com/mattpocock/skills.git
git clone --depth 1 https://github.com/poteto/plugins.git
git -C mattpocock-skills ls-files '**/SKILL.md'
git -C poteto-plugins ls-files '**/SKILL.md'
```

对上之后，把本表开头的提交号和日期改成新的。新增行放在原分组末尾。

poteto 里有两条同名不同路径，对的时候以路径为准：

- `pr-review-canvas`：`cursor-team-kit/skills/pr-review-canvas` 和 `pr-review-canvas/skills/pr-review-canvas`
- `thermo-nuclear-code-quality-review`：`cursor-team-kit/skills/thermo-nuclear-code-quality-review` 和 `thermos/skills/thermo-nuclear-code-quality-review`

## 本地有、上游没有同名的

| 本地 | 上游角色 |
| --- | --- |
| `kstack-mode` | Matt `ask-matt`、poteto `poteto-mode` |
| `how-it-works` | poteto `how` |
| `why-this-way` | poteto `why` |
| `compare-shapes` | poteto `arena`、`principle-exhaust-the-design-space` |
| `clarify-decisions` | Matt `grill-me`、`grilling`、`grill-with-docs` |
| `code-simplify` | 无 |
| `agent-ready-repository` | 无 |

四条原则在 `skills/mode/kstack-mode/principles/`，不是斜杠技能。它们接住 poteto 的 `principle-laziness-protocol`、`principle-separate-before-serializing-shared-state`、`principle-sequence-verifiable-units`、`principle-prove-it-works`。

## Matt Pocock

### engineering（20）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [ask-matt](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/ask-matt/SKILL.md) | `skills/engineering/ask-matt` | 问该用哪个技能。本地入口是 kstack-mode | `kstack-mode` | 已吸收 |
| [code-review](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/code-review/SKILL.md) | `skills/engineering/code-review` | 从固定基点审 diff，规范和规格两条线 | `code-review` | 已吸收 |
| [codebase-design](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/codebase-design/SKILL.md) | `skills/engineering/codebase-design` | 按深模块来设计或改进接口 | `codebase-design` | 已吸收 |
| [diagnosing-bugs](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/diagnosing-bugs/SKILL.md) | `skills/engineering/diagnosing-bugs` | 难 bug 和性能回退的诊断循环 | `diagnosing-bugs` | 已吸收 |
| [domain-modeling](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/domain-modeling/SKILL.md) | `skills/engineering/domain-modeling` | 术语、词汇表和架构决策记录 | `domain-modeling` | 已吸收 |
| [grill-with-docs](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/grill-with-docs/SKILL.md) | `skills/engineering/grill-with-docs` | 盘问方案，同时写下词汇表和决策 | `clarify-decisions、domain-modeling` | 已吸收 |
| [implement-spec](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/implement-spec/SKILL.md) | `skills/engineering/implement-spec` | 在一条集成分支上实现整份规格和票 | — | 未标记 |
| [implement](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/implement/SKILL.md) | `skills/engineering/implement` | 按规格或票实现一块工作 | — | 未标记 |
| [improve-codebase-architecture](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/improve-codebase-architecture/SKILL.md) | `skills/engineering/improve-codebase-architecture` | 扫可加深的模块，做成 HTML 报告再逐个盘问 | — | 未标记 |
| [pr](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/pr/SKILL.md) | `skills/engineering/pr` | 写 PR 说明 | — | 未标记 |
| [prototype](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/prototype/SKILL.md) | `skills/engineering/prototype` | 做一次性原型，检验状态或逻辑 | `prototype` | 已吸收 |
| [research](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/research/SKILL.md) | `skills/engineering/research` | 对着一手资料查问题，写成仓库里的 Markdown | — | 未标记 |
| [retro](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/retro/SKILL.md) | `skills/engineering/retro` | 对一次编码会话做回顾 | — | 未标记 |
| [setup-matt-pocock-skills](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/setup-matt-pocock-skills/SKILL.md) | `skills/engineering/setup-matt-pocock-skills` | 给仓库配 issue 跟踪、分诊标签和领域文档位置 | — | 未标记 |
| [tdd](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/tdd/SKILL.md) | `skills/engineering/tdd` | 先写失败测试再实现 | `tdd` | 已吸收 |
| [to-spec](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/to-spec/SKILL.md) | `skills/engineering/to-spec` | 把已经谈过的内容收成规格，不再访谈 | `to-spec` | 已吸收 |
| [to-tickets](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/to-tickets/SKILL.md) | `skills/engineering/to-tickets` | 把计划拆成带阻塞关系的小票 | — | 未标记 |
| [triage](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/triage/SKILL.md) | `skills/engineering/triage` | 按角色状态机给 issue 和外部 PR 分诊 | — | 未标记 |
| [wayfinder](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/wayfinder/SKILL.md) | `skills/engineering/wayfinder` | 一次会话装不下的工作，画成决策票地图 | `wayfinder` | 已吸收 |
| [wizard](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/wizard/SKILL.md) | `skills/engineering/wizard` | 生成一个 bash 向导，走只有人能做的步骤 | — | 未标记 |

### productivity（7）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [grill-me](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/grill-me/SKILL.md) | `skills/productivity/grill-me` | 把方案盘问清楚 | `clarify-decisions` | 已吸收 |
| [grilling](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/grilling/SKILL.md) | `skills/productivity/grilling` | 对计划或决定做对抗式盘问 | `clarify-decisions` | 已吸收 |
| [handoff](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/handoff/SKILL.md) | `skills/productivity/handoff` | 把当前会话压成给下一个代理的交接 | `handoff` | 已吸收 |
| [teach](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/teach/SKILL.md) | `skills/productivity/teach` | 在当前工作区里教一个概念 | — | 未标记 |
| [to-questionnaire](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/to-questionnaire/SKILL.md) | `skills/productivity/to-questionnaire` | 把答不了的决定做成给别人填的问卷 | — | 未标记 |
| [wait-what](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/wait-what/SKILL.md) | `skills/productivity/wait-what` | 上一句没说清，换个说法再讲一遍 | — | 未标记 |
| [writing-for-agents](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL.md) | `skills/productivity/writing-for-agents` | 写给代理看的技能和仓库说明 | `writing-for-agents` | 已吸收 |

### misc（4）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [git-guardrails-claude-code](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/git-guardrails-claude-code/SKILL.md) | `skills/misc/git-guardrails-claude-code` | 用 Claude Code 钩子拦住危险 git 命令 | — | 未标记 |
| [migrate-to-shoehorn](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/migrate-to-shoehorn/SKILL.md) | `skills/misc/migrate-to-shoehorn` | 测试里的 as 断言换成 shoehorn | — | 未标记 |
| [scaffold-exercises](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/scaffold-exercises/SKILL.md) | `skills/misc/scaffold-exercises` | 生成带题目、解答和讲解的练习目录 | — | 未标记 |
| [setup-pre-commit](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/misc/setup-pre-commit/SKILL.md) | `skills/misc/setup-pre-commit` | 装 Husky、lint-staged、类型检查和测试钩子 | — | 未标记 |

### in-progress（7）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [chief-of-staff](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/chief-of-staff/SKILL.md) | `skills/in-progress/chief-of-staff` | 一次会话里用子代理追一个长期目标 | — | 未标记 |
| [claude-handoff](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/claude-handoff/SKILL.md) | `skills/in-progress/claude-handoff` | 把当前对话交给一个马上开工的后台代理 | — | 未标记 |
| [loop-me](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/loop-me/SKILL.md) | `skills/in-progress/loop-me` | 围绕想做的工作流反复盘问规格 | — | 未标记 |
| [setup-ts-deep-modules](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/setup-ts-deep-modules/SKILL.md) | `skills/in-progress/setup-ts-deep-modules` | 用 dependency-cruiser 把 TypeScript 包收成深模块 | — | 未标记 |
| [writing-beats](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-beats/SKILL.md) | `skills/in-progress/writing-beats` | 把素材排成一连串节拍 | — | 未标记 |
| [writing-fragments](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-fragments/SKILL.md) | `skills/in-progress/writing-fragments` | 先挖写作素材，不急着定结构 | — | 未标记 |
| [writing-shape](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/in-progress/writing-shape/SKILL.md) | `skills/in-progress/writing-shape` | 把素材逐段收成文章 | — | 未标记 |

这些目录名是 `in-progress`。Matt 自己还没当成稳定技能。

## poteto

### pstack（34）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [architect](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/architect/SKILL.md) | `pstack/skills/architect` | 先画类型、签名和模块，再边实现边守着 | — | 未标记 |
| [arena](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/arena/SKILL.md) | `pstack/skills/arena` | 同一任务并行几个方案，选一个底，再并入落选里值得留的部分 | `compare-shapes` | 已吸收 |
| [automate-me](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/automate-me/SKILL.md) | `pstack/skills/automate-me` | 把个人习惯收成或更新一个 mode 技能 | — | 未标记 |
| [figure-it-out](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/figure-it-out/SKILL.md) | `pstack/skills/figure-it-out` | 没有更窄的 playbook 时，给大迁移或大改动写可审计的步骤 | — | 未标记 |
| [how](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/how/SKILL.md) | `pstack/skills/how` | 说明现在怎么工作、落在哪、该放哪一层 | `how-it-works` | 已吸收 |
| [interrogate](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/interrogate/SKILL.md) | `pstack/skills/interrogate` | 多模型对抗审查，找代码盲区 | — | 未标记 |
| [poteto-mode](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/poteto-mode/SKILL.md) | `pstack/skills/poteto-mode` | 统一风格的入口。本地入口是 kstack-mode | `kstack-mode` | 已吸收 |
| [principle-boundary-discipline](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-boundary-discipline/SKILL.md) | `pstack/skills/principle-boundary-discipline` | 校验和适配只放在系统边界 | — | 未标记 |
| [principle-build-the-lever](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-build-the-lever/SKILL.md) | `pstack/skills/principle-build-the-lever` | 先做能完成或证明这件事的工具 | — | 未标记 |
| [principle-encode-lessons-in-structure](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-encode-lessons-in-structure/SKILL.md) | `pstack/skills/principle-encode-lessons-in-structure` | 重复出现的教训写成结构，而不是再写一句说明 | — | 未标记 |
| [principle-exhaust-the-design-space](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-exhaust-the-design-space/SKILL.md) | `pstack/skills/principle-exhaust-the-design-space` | 没先例时做两三个对照方案再选 | `compare-shapes` | 已吸收 |
| [principle-experience-first](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-experience-first/SKILL.md) | `pstack/skills/principle-experience-first` | 产品和体验取舍时，先保用户感受 | — | 未标记 |
| [principle-fix-root-causes](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-fix-root-causes/SKILL.md) | `pstack/skills/principle-fix-root-causes` | 先复现，修产生点。本地不另建原则文件 | `diagnosing-bugs` | 已吸收 |
| [principle-foundational-thinking](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-foundational-thinking/SKILL.md) | `pstack/skills/principle-foundational-thinking` | 动笔前先定核心类型、数据结构和参与者 | — | 未标记 |
| [principle-guard-the-context-window](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-guard-the-context-window/SKILL.md) | `pstack/skills/principle-guard-the-context-window` | 上下文变满时，把大块输出交给子代理 | — | 未标记 |
| [principle-laziness-protocol](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-laziness-protocol/SKILL.md) | `pstack/skills/principle-laziness-protocol` | 改动求小，少加层、少穿信号 | `principles/laziness-protocol.md` | 已吸收 |
| [principle-make-operations-idempotent](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-make-operations-idempotent/SKILL.md) | `pstack/skills/principle-make-operations-idempotent` | 命令和循环重跑应收敛到同一结果 | — | 未标记 |
| [principle-migrate-callers-then-delete-legacy-apis](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | `pstack/skills/principle-migrate-callers-then-delete-legacy-apis` | 换内部接口时，同一轮迁完调用方并删旧的 | — | 未标记 |
| [principle-minimize-reader-load](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-minimize-reader-load/SKILL.md) | `pstack/skills/principle-minimize-reader-load` | 减少读者要穿过的层数和要记的隐藏状态 | — | 未标记 |
| [principle-never-block-on-the-human](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-never-block-on-the-human/SKILL.md) | `pstack/skills/principle-never-block-on-the-human` | 可逆的事先做，再让人纠正 | — | 未标记 |
| [principle-outcome-oriented-execution](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-outcome-oriented-execution/SKILL.md) | `pstack/skills/principle-outcome-oriented-execution` | 重写和迁移对准目标结构，不保中间平滑 | — | 未标记 |
| [principle-prove-it-works](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-prove-it-works/SKILL.md) | `pstack/skills/principle-prove-it-works` | 说做完之前，对着真实产物验证 | `principles/prove-it-works.md` | 已吸收 |
| [principle-redesign-from-first-principles](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-redesign-from-first-principles/SKILL.md) | `pstack/skills/principle-redesign-from-first-principles` | 新要求进来时，当成一开始就有它来重做设计 | — | 未标记 |
| [principle-separate-before-serializing-shared-state](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md) | `pstack/skills/principle-separate-before-serializing-shared-state` | 会写同一份状态时，先拆开再考虑加锁 | `principles/separate-before-serializing-shared-state.md` | 已吸收 |
| [principle-sequence-verifiable-units](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-sequence-verifiable-units/SKILL.md) | `pstack/skills/principle-sequence-verifiable-units` | 多步工作拆成能单独验证的小段 | `principles/sequence-verifiable-units.md` | 已吸收 |
| [principle-subtract-before-you-add](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-subtract-before-you-add/SKILL.md) | `pstack/skills/principle-subtract-before-you-add` | 先删死重和多余校验，再加新的 | — | 未标记 |
| [principle-type-system-discipline](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/principle-type-system-discipline/SKILL.md) | `pstack/skills/principle-type-system-discipline` | 用类型让不合法状态写不出来 | — | 未标记 |
| [reflect](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/reflect/SKILL.md) | `pstack/skills/reflect` | 用三个子代理看会话，把教训写回已有技能 | — | 未标记 |
| [setup-pstack](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/setup-pstack/SKILL.md) | `pstack/skills/setup-pstack` | 给 pstack 各角色选模型 | — | 未标记 |
| [show-me-your-work](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/show-me-your-work/SKILL.md) | `pstack/skills/show-me-your-work` | 长时间工作记一张决策表：做了什么、为什么、证据 | — | 未标记 |
| [tdd](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/tdd/SKILL.md) | `pstack/skills/tdd` | 先写失败测试再实现 | `tdd` | 已吸收 |
| [typescript-best-practices](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/typescript-best-practices/SKILL.md) | `pstack/skills/typescript-best-practices` | 读或改 TypeScript 时的写法约定 | — | 未标记 |
| [unslop](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/unslop/SKILL.md) | `pstack/skills/unslop` | 去掉文字里的生成腔 | — | 未标记 |
| [why](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pstack/skills/why/SKILL.md) | `pstack/skills/why` | 追溯为什么长这样，证据来自提交、笔记和文档 | `why-this-way` | 已吸收 |

### cursor-team-kit（18）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [check-compiler-errors](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/check-compiler-errors/SKILL.md) | `cursor-team-kit/skills/check-compiler-errors` | 跑编译和类型检查，报告失败 | — | 未标记 |
| [control-cli](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/control-cli/SKILL.md) | `cursor-team-kit/skills/control-cli` | 本地驱动交互式命令行，做体验检查 | — | 未标记 |
| [control-ui](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/control-ui/SKILL.md) | `cursor-team-kit/skills/control-ui` | 本地驱动浏览器或 Electron 界面 | — | 未标记 |
| [deslop](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/deslop/SKILL.md) | `cursor-team-kit/skills/deslop` | 去掉代码里的生成腔和风格噪音 | — | 未标记 |
| [fix-ci](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/fix-ci/SKILL.md) | `cursor-team-kit/skills/fix-ci` | 看失败的 PR 检查并做小修复 | — | 未标记 |
| [fix-merge-conflicts](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/fix-merge-conflicts/SKILL.md) | `cursor-team-kit/skills/fix-merge-conflicts` | 非交互地解决合并冲突并验证 | — | 未标记 |
| [get-pr-comments](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/get-pr-comments/SKILL.md) | `cursor-team-kit/skills/get-pr-comments` | 取当前 PR 的评审意见并摘要 | — | 未标记 |
| [loop-on-ci](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/loop-on-ci/SKILL.md) | `cursor-team-kit/skills/loop-on-ci` | 盯着 PR 检查，失败就修到变绿 | — | 未标记 |
| [make-pr-easy-to-review](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/make-pr-easy-to-review/SKILL.md) | `cursor-team-kit/skills/make-pr-easy-to-review` | 整理历史和说明，让 PR 好审，不改行为 | — | 未标记 |
| [new-branch-and-pr](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/new-branch-and-pr/SKILL.md) | `cursor-team-kit/skills/new-branch-and-pr` | 开新分支，做完就提 PR | — | 未标记 |
| [pr-review-canvas](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/pr-review-canvas/SKILL.md) | `cursor-team-kit/skills/pr-review-canvas` | 把 PR diff 画成可交互的评审页 | — | 未标记 |
| [review-and-ship](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/review-and-ship/SKILL.md) | `cursor-team-kit/skills/review-and-ship` | 审分支、补测试、提交并开或更新 PR | — | 未标记 |
| [run-smoke-tests](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/run-smoke-tests/SKILL.md) | `cursor-team-kit/skills/run-smoke-tests` | 跑 Playwright 冒烟测试并修失败 | — | 未标记 |
| [thermo-nuclear-code-quality-review](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md) | `cursor-team-kit/skills/thermo-nuclear-code-quality-review` | 极严的可维护性审查，盯抽象、巨文件和缠绕条件 | — | 未标记 |
| [verify-this](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/verify-this/SKILL.md) | `cursor-team-kit/skills/verify-this` | 用新的本地证据核对一个说法 | — | 未标记 |
| [weekly-review](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/weekly-review/SKILL.md) | `cursor-team-kit/skills/weekly-review` | 按修 bug、还债、新功能汇总一周提交 | — | 未标记 |
| [what-did-i-get-done](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/what-did-i-get-done/SKILL.md) | `cursor-team-kit/skills/what-did-i-get-done` | 按时间段汇总自己写过的提交 | — | 未标记 |
| [workflow-from-chats](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-team-kit/skills/workflow-from-chats/SKILL.md) | `cursor-team-kit/skills/workflow-from-chats` | 从最近的对话里抽出可复用的做法 | — | 未标记 |

### thermos（3）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [thermo-nuclear-code-quality-review](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/thermos/skills/thermo-nuclear-code-quality-review/SKILL.md) | `thermos/skills/thermo-nuclear-code-quality-review` | 极严的可维护性审查，盯抽象、巨文件和缠绕条件 | — | 未标记 |
| [thermo-nuclear-review](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/thermos/skills/thermo-nuclear-review/SKILL.md) | `thermos/skills/thermo-nuclear-review` | 对分支做安全和正确性深审 | — | 未标记 |
| [thermos](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/thermos/skills/thermos/SKILL.md) | `thermos/skills/thermos` | 同时跑两套极严审查，再合成 | — | 未标记 |

### ralph-loop（3）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [cancel-ralph](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/ralph-loop/skills/cancel-ralph/SKILL.md) | `ralph-loop/skills/cancel-ralph` | 停掉正在跑的 Ralph 循环 | — | 未标记 |
| [ralph-loop-help](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/ralph-loop/skills/ralph-loop-help/SKILL.md) | `ralph-loop/skills/ralph-loop-help` | 说明 Ralph 循环怎么用 | — | 未标记 |
| [ralph-loop](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/ralph-loop/skills/ralph-loop/SKILL.md) | `ralph-loop/skills/ralph-loop` | 开始一轮自我参照的迭代循环 | — | 未标记 |

### teaching（2）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [create-learning-path](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/teaching/skills/create-learning-path/SKILL.md) | `teaching/skills/create-learning-path` | 做一条带里程碑的学习路径 | — | 未标记 |
| [run-learning-retrospective](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/teaching/skills/run-learning-retrospective/SKILL.md) | `teaching/skills/run-learning-retrospective` | 看学习进度并调整计划 | — | 未标记 |

### create-plugin（2）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [create-plugin-scaffold](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/create-plugin/skills/create-plugin-scaffold/SKILL.md) | `create-plugin/skills/create-plugin-scaffold` | 新建一个 Cursor 插件骨架 | — | 未标记 |
| [review-plugin-submission](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/create-plugin/skills/review-plugin-submission/SKILL.md) | `create-plugin/skills/review-plugin-submission` | 检查插件能不能上架 | — | 未标记 |

### 单技能插件（7）

| 技能 | 路径 | 做什么 | 本地 | 处置 |
| --- | --- | --- | --- | --- |
| [check-agent-compatibility](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/agent-compatibility/skills/check-agent-compatibility/SKILL.md) | `agent-compatibility/skills/check-agent-compatibility` | 跑仓库对代理的兼容检查 | — | 未标记 |
| [cli-for-agents](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cli-for-agent/skills/cli-for-agents/SKILL.md) | `cli-for-agent/skills/cli-for-agents` | 把命令行设计成代理能稳定调用的样子 | — | 未标记 |
| [continual-learning](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/continual-learning/skills/continual-learning/SKILL.md) | `continual-learning/skills/continual-learning` | 从会话记录里提炼，再改 AGENTS.md | — | 未标记 |
| [cursor-sdk](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/cursor-sdk/skills/cursor-sdk/SKILL.md) | `cursor-sdk/skills/cursor-sdk` | 用 Cursor TypeScript SDK 写应用或自动化 | — | 未标记 |
| [docs-canvas](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/docs-canvas/skills/docs-canvas/SKILL.md) | `docs-canvas/skills/docs-canvas` | 把文档画成一块 Canvas | — | 未标记 |
| [orchestrate](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/orchestrate/skills/orchestrate/SKILL.md) | `orchestrate/skills/orchestrate` | 显式调用时，把大任务拆给并行的云代理 | — | 未标记 |
| [pr-review-canvas](https://github.com/poteto/plugins/blob/74dd2291e8e37b12fd6dc49b2acbd655c6bdaf12/pr-review-canvas/skills/pr-review-canvas/SKILL.md) | `pr-review-canvas/skills/pr-review-canvas` | 把 PR diff 画成可交互的评审页 | — | 未标记 |
