# Skills — Engineering & Agent Workflow Primitives

专为严谨软件工程、深度架构设计与 Agent 协同打造的原子化技能体系（Skills Framework）。

参考并借鉴了 Matt Pocock 等业内前沿的 Agentic Engineering 最佳实践，针对实际工程场景定制演进。

## 目录结构规划

\\\	ext
skills/
├── engineering/       # 研发核心工程规范（TDD、架构深度、排障、Seam 接口设计等）
├── productivity/      # 生产力与对齐流（Handoff 跨上下文交接、Grilling 盘问、Spec 转化等）
├── workflows/         # 复合工作流编排（多 Agent 协作、分支任务与探索流）
├── docs/              # 技能深度设计原理与指南（Theory & Manuals）
└── .claude-plugin/    # 支持 Claude Code / CLI / Pi-Agent 的插件元数据配置
\\\

## 核心设计法则

1. **分离编排与纪律**：
   - \User-invoked\（人类显式调用）：编排者（Orchestrator），设置 \disable-model-invocation: true\，零上下文损耗。
   - \Model-invoked\（模型自主调用）：工程纪律（Disciplines），精炼条件触发。
2. **渐进式展开（Progressive Disclosure）**：
   - 规则按优先级分层，能外置的推到 Reference/外部文件，杜绝 Prompt 膨胀与上下文污染。
3. **跨上下文便携与不失真（Portable Handoff）**：
   - 严格区分“已验证事实”与“待确认假设”，只传递流转状态与指针，不产生第二事实源。
