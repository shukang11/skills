# Skills — Engineering & Agent Workflow Primitives

专为严谨软件工程、深度架构设计与 Agent 协同打造的原子化技能体系（Skills Framework）。

参考并借鉴了 Matt Pocock 等业内前沿的 Agentic Engineering 最佳实践，针对单人多项目交付、前台模型工程化约束及与 `spec-anchor` 协同进行了深度定制演进。

---

## 技能全景矩阵（目前已收纳 10 个核心基石）

```text
                               【个人核心技能库矩阵】
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  【需求与探索战区】              【架构与实施战区】              【排错与质量战区】
• grilling (对抗盘问消除盲区)   • codebase-design (深模块设计)   • diagnosing-bugs (根因排错闭环)
• prototype (用完即扔探路原型)   • tdd (红绿契约实施/里程碑触发)   • code-review (双轴独立审查)
• domain-modeling (术语与状态机)                                • handoff (会话无损上下文交接)
• to-spec (标准化规格沉淀)
                                         │
                                         ▼
                            【元技能基座 (Meta-Skill)】
                            • writing-for-agents (编写高执行力技能)
```

---

## 本地极速开发与挂载使用（Windows Junction 机制）

为了支持在调整技能时**零复制、零构建、实时热生效**，并且支持**按需挑选安装**，本项目提供了原生的 `manage-skills.ps1` 管理脚本。

### 常用命令

#### 1. 查看当前技能及全局挂载状态
```powershell
.\manage-skills.ps1 -List
```

#### 2. 按需挂载指定技能到全局（跨所有项目生效）
挂载后，在系统内任何项目目录中启动 Agent 均可使用：
```powershell
# 安装单个或多个技能（支持逗号分隔）
.\manage-skills.ps1 -Install grilling,to-spec,codebase-design

# 或者一次性挂载所有技能
.\manage-skills.ps1 -Install all
```

#### 3. 卸载技能挂载
```powershell
# 卸载指定技能
.\manage-skills.ps1 -Uninstall prototype

# 或者全部卸载
.\manage-skills.ps1 -Uninstall all
```

#### 4. 项目级私有挂载（仅在某个项目内生效）
如果不希望某个技能污染全局，仅在特定项目（如 `spec-anchor`）内启用：
```powershell
.\manage-skills.ps1 -Install prototype -Project "D:\wiki\project\spec-anchor"
```

---

## 日常调用姿势

1. **显式唤醒（推荐，100% 遵循纪律）**：
   - `/skill:grilling`：进入对抗盘问模式；
   - `/skill:to-spec`：将上下文决策合成输出为 `.agents/notes/proposed/` 规范；
   - `/skill:prototype`：在 `prototypes/` 目录下生成可点击的探路单文件 HTML；
   - `/skill:codebase-design`：按 Ousterhout 深模块原则审查与重构模块；
   - `/skill:diagnosing-bugs`：进入单命令复现、根因定位的排错循环；
   - `/skill:handoff`：生成跨会话无损交接胶囊。
2. **自然语言隐式唤醒**：
   - 当对话中提到 *“帮我 grill 一下这个方案”*、*“用 tdd 方式实现”* 时，Agent 也会基于技能 Description 自发调起对应规范。
