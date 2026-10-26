# Skills — Engineering & Agent Workflow Primitives

专为严谨软件工程、深度架构设计与 Agent 协同打造的原子化技能体系（Skills Framework）。

参考并借鉴了 Matt Pocock 等业内前沿的 Agentic Engineering 最佳实践，针对单人多项目交付、前台模型工程化约束及与 `spec-anchor` 协同进行了深度定制演进。

---

## 技能全景（17 个技能，一个入口）

干活从 `/kstack-mode` 进。它按任务选一个 playbook，再打开下面的叶子。playbook 和四条原则跟入口在同一目录，没有单独的斜杠命令。

```text
入口  kstack-mode
  │
  ├─ playbook   feature  bug-fix  design  prototype  refactor
  │             review  simplify  handoff  authoring  repo-audit  investigate
  │
  ├─ 会交给下一步   clarify-decisions → domain-modeling → compare-shapes → to-spec
  │                → codebase-design → tdd
  │                wayfinder 清空地图后从 to-spec 接入
  │
  └─ 做到本职就停   how-it-works  why-this-way  prototype  diagnosing-bugs
                    code-review  code-simplify  handoff  writing-for-agents
                    agent-ready-repository
```

原则在 `skills/mode/kstack-mode/principles/`：`laziness-protocol`、`separate-before-serializing-shared-state`、`sequence-verifiable-units`、`prove-it-works`。步骤点名时才读。

上游对照在 `docs/upstream.md`。Matt Pocock 和 poteto 的技能路径钉在某一次提交上。处置列用来标「不需要」。下次对名单时，表里没有的路径就是新增。

---

## 安装

两种范围，两种落盘方式：

- **用户级**：符号链接，指向本仓库。改技能立即生效，只存在于这台机器。
- **项目级**：把技能目录**复制**到目标仓库的 `.agents/skills/<技能名>/`。副本不依赖本机路径，可以提交，云端 Agent 也能读到。再次执行同一命令会覆盖同名副本。

技能 `name` 是扁平命名空间，同名只加载先发现的那个。目标仓库若已通过用户级链接看到同名技能，不要再在项目里装一份。

需要 Node.js 18+。macOS / Linux 用 `scripts/install.sh`，Windows 用 `manage-skills.ps1`（转发给同一个 `scripts/install.mjs`）。

> 入口和全部叶子都设置了 `disable-model-invocation: true`。模型不会凭描述自动选技能。

### 用户级（链接）

在本仓库的克隆里执行。不带技能名时链接整库，之后新增技能不用重装：

```bash
./scripts/install.sh --user
```

```text
~/.agents/skills/shukang -> <本仓库>/skills
```

只链接其中几个时，每个技能一个链接：

```bash
./scripts/install.sh --user clarify-decisions tdd
```

```powershell
.\manage-skills.ps1 -Install all
.\manage-skills.ps1 -Install clarify-decisions,tdd
```

- **验证**：`find -L ~/.agents/skills/shukang -name SKILL.md | wc -l` 应输出 `17`，且 `test -L ~/.agents/skills/shukang`
- **卸载整库**：`./scripts/install.sh --uninstall --user`
- **卸载单个链接**：`./scripts/install.sh --uninstall --user tdd`（整库链接里的技能不会因此被拆出）

### 项目级（拷贝）

在技能仓库的克隆里，把副本写进目标仓库：

```bash
./scripts/install.sh --project /path/to/repo
./scripts/install.sh --project /path/to/repo tdd clarify-decisions
```

```powershell
.\manage-skills.ps1 -Install all -Project "D:\wiki\project\spec-anchor"
.\manage-skills.ps1 -Install tdd -Project "D:\wiki\project\spec-anchor"
```

没有克隆时，在目标仓库里用 npx（改动推到 GitHub 之后才走这条）：

```bash
npx --yes github:shukang11/skills --project .
```

落点是普通目录，不是指向技能仓库的链接：

```text
<仓库>/.agents/skills/tdd/
├── SKILL.md
└── references/    # 技能自带的参考文件会一起复制
```

- **验证**：`test ! -L <仓库>/.agents/skills/tdd && test -f <仓库>/.agents/skills/tdd/SKILL.md`
- **更新**：对同一仓库再执行一次安装命令
- **卸载**：`./scripts/install.sh --uninstall --project /path/to/repo tdd`
- **查看**：`./scripts/install.sh --list` 或 `./scripts/install.sh --list --project /path/to/repo`

---

## 日常调用姿势

1. **从入口进**（一套任务走完）：`/kstack-mode`，后面加一句任务。入口选 playbook，再按步骤读叶子。
2. **直接点叶子**（只做这一件事）：`/how-it-works`、`/why-this-way`、`/compare-shapes`、`/clarify-decisions`、`/to-spec`、`/tdd`、`/handoff`、`/agent-ready-repository` 等。这时不走 playbook。
