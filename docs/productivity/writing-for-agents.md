## 编写 Agent 文档（Writing for Agents）设计说明

本技能基于 Matt Pocock 的经典 AI 文档心法，针对通用 Agent 环境（Pi Agent、OpenCode、Claude Code、Codex 等）进行了去特定工具链绑定的通用化改造。

### 核心价值
- **元技能（Meta-skill）**：指导如何产出优秀的提示词与技能规范；
- **预算控制**：严格管理 Context Load（常驻消耗）与 Cognitive Load（人类认知成本）；
- **判据优先**：默认结构是意图、判据、收工检查、产出；步骤只在顺序猜不到或错一步代价很大时才写，能写成脚本的写成脚本。只写原则、不给判据与检查的技能会流于形式。
