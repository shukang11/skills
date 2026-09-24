## 编写 Agent 文档（Writing for Agents）设计说明

本技能基于 Matt Pocock 的经典 AI 文档心法，针对通用 Agent 环境（Pi Agent、OpenCode、Claude Code、Codex 等）进行了去特定工具链绑定的通用化改造。

### 核心价值
- **元技能（Meta-skill）**：指导如何产出优秀的提示词与技能规范；
- **预算控制**：严格管理 Context Load（常驻消耗）与 Cognitive Load（人类认知成本）；
- **脚手架化**：提供开箱即用的 `SKILL.md` 黄金模板，确保后续技能扩充格式稳定。
