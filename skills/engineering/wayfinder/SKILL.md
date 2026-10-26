---
name: wayfinder
description: "一次会话装不下、路线还看不清的工作，画成决策票地图，一次解开一张。地图和票写在 handoff/wayfinder/。"
disable-model-invocation: true
argument-hint: "终点是什么；已有地图则给出 handoff/wayfinder/<slug>/map.md"
---

# Wayfinder

把说得出终点、还说不出路线的工作，拆成一次会话能解开的决策票。地图是索引。决定写在票上。本技能规划，不写实现。

## 落点

一次努力一个目录，slug 用终点的短横线名：

- 地图：`handoff/wayfinder/<slug>/map.md`
- 票：`handoff/wayfinder/<slug>/issues/NN-<slug>.md`，从 `01` 编号，一票一文件

只建这个目录。不改 `handoff/active.md`，不建 `handoff/ctx/`，不写 `.scratch/`。

`handoff/` 是临时层。清掉它，地图和票一起消失。要在清空之后还在的结论，写进 `.agents/notes/`，票的 Answer 改成指向那份笔记的路径和一行要点。术语进 `ALIGNMENT.md`。契约进 `docs/` 里对应 topic。地图和票不抄这些正文。

## 判据

- 终点先写进地图，再写任何票。终点是整张地图的尽头，不是这一次会话的尽头。
- 票的正文是一个现在就能精确说出的问题。说不出的进地图的「还没说清」，不提前开票。
- 一张票只做一种：`grilling`、`prototype`、`research`、`task`。
- 前沿是 `Status: open`、且 `Blocked by` 列出的每一张票都已 `resolved` 的票。编号最小的先做。
- 认领先于任何工作：先把该票写成 `Status: claimed` 并保存，再开始问、查或模拟。
- 一次会话只认领一张票。画图那次只建文件，不解答。
- `grilling` 和 `prototype` 的答案由人拍板。Agent 可以给推荐，不替人写下 Answer。
- `task` 只为解开某张决策票清障，例如凭证、账号、把数据摆到能看见的地方。
- 地图的 Notes 不能把这次会话改成写实现。
- 回复里用票的标题。文件之间用相对路径。

## 四种票

| Type | 何时 | 怎么解开 |
| --- | --- | --- |
| `grilling` | 谈得清的决定。默认这一种 | 读 `clarify-decisions` 和 `domain-modeling`。人确认后才写 Answer |
| `prototype` | 要看见逻辑或交互才定得下来 | 读 `prototype`。Answer 指向 `prototypes/index.html` 和人选定的行为 |
| `research` | 决定卡在仓库外的事实上 | Agent 查完，Answer 写结论和出处路径或链接 |
| `task` | 没有决定要做，但有一件事挡住决定 | 做完那件清障的事，Answer 写做成了什么 |

`Blocked by:` 写票号，逗号分隔，如 `01, 03`。没有阻挡就留空。

## 地图骨架

```markdown
# <终点的短名>

## Destination
<整张地图结束时，手里有什么>

## Notes
<只写这次努力的约束。不写「可以开始实现」>

## Decisions so far
- <一行要点> — issues/NN-<slug>.md

## Not yet specified
- <能感到会遇到、但现在问不精确的事>

## Out of scope
- <终点之外的事>
```

## 票骨架

```markdown
# <问句>
Type: grilling
Status: open
Blocked by:

## Question
<一个问句>

## Answer
```

## 步骤

没有 `map.md` 时：

1. 问终点。人说清之前不建票。
2. 整条路线就是一个现在问得清、一次会话谈得完的问题时，停下，改走 `clarify-decisions`。
3. 否则写下地图和现在问得清的票。fog 留在「还没说清」。超出终点的写进 Out of scope，不开成 open 票。
4. 回复列出前沿票的标题和路径。本会话不写 Answer。

已有地图时：

1. 只读 `map.md` 和各票的头三行。要解开哪张，再读那一张的全文。
2. 没有前沿票：地图清空。回复给出 `map.md` 路径，下一步是 `to-spec`。本会话不写实现。
3. 认领编号最小的前沿票。
4. 按 Type 解开。人拍板的票，人确认后把答案写入 `## Answer`，`Status` 改为 `resolved`。
5. 在 Decisions so far 加一行。fog 里已经问得精确的，毕业成新票，并从「还没说清」删掉那一行。
6. 回复写这张票的标题、答案落在哪个文件，以及下一张前沿票的标题。然后停。

## 收工检查

- 画图会话：`map.md` 的 Destination 有人给的终点；每张票有 Type、`Status: open`、`## Question`；没有 `## Answer` 正文。
- 做票会话：恰好一张票从 `open` 经 `claimed` 到 `resolved`；地图多了一行带相对路径的要点。
- 回复里的票都用标题，并带上 `handoff/wayfinder/<slug>/` 路径。

## 产出

`handoff/wayfinder/<slug>/map.md`，以及 `issues/NN-<slug>.md`。
