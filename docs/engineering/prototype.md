## Prototype

一套保真的产品逻辑或交互模拟，不是生产代码，也不是多套外观草稿。

- 入口 `prototypes/index.html`：左导航，右内容。双击打开，不启本地服务。
- 内容区用相对路径跳本地 HTML，跳转后导航还在。
- 共用样式、脚本、逻辑分别放 `prototypes/css/`、`prototypes/js/`、`prototypes/shared/`。
- 另一种结构方案走 `compare-shapes`。确认后的契约写进 `docs/` 对应 topic，模拟文件留在 `prototypes/`。
