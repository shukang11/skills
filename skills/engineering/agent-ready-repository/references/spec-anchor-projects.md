# 已接入 spec-anchor 的项目

本文件回答：项目已接入 spec-anchor 时，审计要多查什么、少建议什么。判定已接入的依据是：项目根有 `site.config.yaml`（spec-anchor CLI 也按它定位项目根）。

## 已铺的不重复建议

`spec-anchor init` 已经铺好下面这些：演进原则、技能入口、修复提交规则、锚段之外的「项目检查」一节、`docs/` 分层；`spec-anchor skills install` 已经装好同捆技能。「写一份原则」「加一条修复规则」这类建议不再提。要查的是这些东西有没有真的接上，下表每一项不通过，都按一条问题入表。

| 查什么 | 怎么查 | 不通过时的类别 |
|--------|--------|----------------|
| 锚段在不在 | 根 `AGENTS.md` 里有没有独占一行的 `<!-- spec-anchor:docs-framework -->`。没有时可能是项目有意自写，裁决列标「待议」，不当缺陷；下面两条锚段相关的检查改为对照它自写的等价段落 | 原则 6 |
| 锚段是不是旧版 | 在临时目录跑 `spec-anchor init --no-skills`，对比两份锚段 `<!-- spec-anchor:docs-framework -->` 到 `<!-- /spec-anchor:docs-framework -->` 之间的内容；锚段不会自动刷新 | 原则 6 |
| 「项目检查」一节填了没有 | 根 `AGENTS.md` 锚段之外的「项目检查」，还是 `<命令>` 占位，或者整节不存在 | 原则 2 |
| 项目检查的命令下次一定会跑吗 | 钩子目录取 `git config core.hooksPath`，未设置时是 `.git/hooks/`；读里面可执行的钩子，看是否真的跑了这组命令。只有 `commit-msg` 这类检查提交信息的钩子不算。再看 CI 配置是否跑同一组命令 | 原则 2 |
| 同捆技能是不是当前版本、有没有被改写 | `spec-anchor skills check` | 原则 6 |
| 文档门禁通不通过 | `spec-anchor verify --verbose` | 原则 1 |
| 修复提交有没有带证据 | 先看钩子里有没有强制它（例如 `commit-msg` 拒收不带测试也不带 `Tested:` 的 `fix` 提交）；有就记为已接上，再确认 `core.hooksPath` 真的指向它。没有就抽近期标题以 `fix` 开头的提交，看是否带测试改动或 `Tested:` trailer | 原则 1 |

## 类别对齐演进原则

违反某条演进原则的问题，在可裁决表的「问题」列开头写「原则 N」，与 `code-review` 和周期审查用同一个口径。原则全文与检验问题见 `.agents/skills/spec-anchor/references/evolution-principles.md`。不对应任何一条原则的问题照常描述，不硬套。

## 出口落点

- 出口① 采纳后，命令写进「项目检查」一节；那一节是项目声明提交前全绿命令的唯一位置。
- 出口③ 的关口优先用原则 7 的三个：定意图、合并审查、收版本。
