---
name: prototype
description: "做一套保真的产品逻辑或交互模拟。用 HTML 双击打开，不启本地服务。左导航右内容，内容区用相对路径跳本地文件。"
disable-model-invocation: true
argument-hint: "要模拟的产品逻辑或交互是什么"
---

# Prototype

一套保真模拟，让人点得动产品逻辑或交互。模拟留在 `prototypes/`，不打进生产构建。验证过的决定写进 `docs/` 里对应 topic 的契约，再由正式代码实现。

## 判据

- 一个产品一套模拟。另一种结构方案交给 `compare-shapes`，不在这里做多套外观切换。
- 入口是 `prototypes/index.html`。左侧导航，右侧内容。内容区的链接用相对路径指向本地 HTML，跳转后导航还在。
- 双击 `index.html` 就能用。不启本地服务。
- 共用样式放 `prototypes/css/`，共用脚本放 `prototypes/js/`，共用逻辑放 `prototypes/shared/`。脚本用普通 `<script src>`，不用 `type="module"`。
- 导航只列这套模拟的页面，不列 `prototypes/compare-shapes-*`。
- 不写生产数据库，不把 `prototypes/` 打进生产构建。

## 收工检查

- 双击 `prototypes/index.html`，左导航能打开各页，内容区的本地链接能跳转，导航仍在。
- 回复里有入口路径，以及这次模拟要让人看清的那一段逻辑或交互。
- 已经确认要留下的契约，写进 `docs/` 对应 topic，不写进模拟文件里当第二份规格。

## 产出

`prototypes/index.html`、各内容页，以及用到的 `css/`、`js/`、`shared/`。
