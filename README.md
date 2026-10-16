# Skills — Engineering & Agent Workflow Primitives

专为严谨软件工程、深度架构设计与 Agent 协同打造的原子化技能体系（Skills Framework）。

参考并借鉴了 Matt Pocock 等业内前沿的 Agentic Engineering 最佳实践，针对单人多项目交付、前台模型工程化约束及与 `spec-anchor` 协同进行了深度定制演进。

---

## 技能全景矩阵（目前已收纳 7 个核心基石）

```text
                               【个人核心技能库矩阵】
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  【需求与探索战区】              【架构与实施战区】              【排错与质量战区】
• grilling (对抗盘问消除盲区)   • codebase-design (深模块设计)   • handoff (会话无损上下文交接)
                                • tdd (红绿契约实施/里程碑触发)
                                • code-simplify (残留清理/收敛)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
          【项目治理战区】                          【元技能基座 (Meta-Skill)】
• agent-ready-repository                  • writing-for-agents
  (仓库环境 + 人侧注意力审计)                 (编写高执行力技能)
```

---

## macOS / Linux 安装（软链接，推荐）

整层软链接，仓库即真源，改动**实时生效、零复制**：

```bash
ln -sfn "/Volumes/Storage/Documents/project/skills/skills" "$HOME/.agents/skills/shukang"
```

安装后布局（`shukang` 为链接，指向本仓库 `skills/`）：

```text
~/.agents/skills/
└── shukang -> /Volumes/Storage/Documents/project/skills/skills
    ├── engineering/
    │   ├── code-simplify/  codebase-design/  tdd/
    │   └── agent-ready-repository/
    └── productivity/
        ├── grilling/  handoff/  writing-for-agents/
```

- **验证**：`find -L ~/.agents/skills/shukang -name SKILL.md | wc -l` 应输出 `7`
- **卸载**：`rm ~/.agents/skills/shukang`
- **注意**：pi 递归发现任意深度的 `SKILL.md`；但技能 `name` 是**全局扁平命名空间**，同名技能只加载先发现的那个。
- **`to-spec` / `prototype` / `diagnosing-bugs` / `domain-modeling` / `code-review` 不在本库**：它们引用 spec-anchor 契约或产出被其复核，随引擎同捆，经 `spec-anchor skills install` 装进项目的 `.agents/skills/`。本库不再保留同名副本，避免 pi 加载到旧版。

> `handoff` 与 `agent-ready-repository` 设置了 `disable-model-invocation: true`，不会出现在模型自动路由列表中，需显式唤醒（`/skill:handoff`、`/skill:agent-ready-repository`）。后者是高成本、高破坏面的项目级元操作，不应被模型自动路由。

---

## Windows 挂载使用（Junction 机制）

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
.\manage-skills.ps1 -Install grilling,tdd,codebase-design

# 或者一次性挂载所有技能
.\manage-skills.ps1 -Install all
```

#### 3. 卸载技能挂载
```powershell
# 卸载指定技能
.\manage-skills.ps1 -Uninstall tdd

# 或者全部卸载
.\manage-skills.ps1 -Uninstall all
```

#### 4. 项目级私有挂载（仅在某个项目内生效）
如果不希望某个技能污染全局，仅在特定项目（如 `spec-anchor`）内启用：
```powershell
.\manage-skills.ps1 -Install tdd -Project "D:\wiki\project\spec-anchor"
```

---

## 日常调用姿势

1. **显式唤醒（推荐，100% 遵循纪律）**：
   - `/skill:grilling`：进入对抗盘问模式；
   - `/skill:codebase-design`：按 Ousterhout 深模块原则审查与重构模块；
   - `/skill:handoff`：生成跨会话无损交接胶囊；
   - `/skill:agent-ready-repository`：对某个仓库跑"环境 + 人侧注意力"两遍基线审计，产出逐条可裁决的建议表（只读，止于建议）。
2. **自然语言隐式唤醒**：
   - 当对话中提到 *“帮我 grill 一下这个方案”*、*“用 tdd 方式实现”* 时，Agent 也会基于技能 Description 自发调起对应规范。
