# Skills — Engineering & Agent Workflow Primitives

专为严谨软件工程、深度架构设计与 Agent 协同打造的原子化技能体系（Skills Framework）。

参考并借鉴了 Matt Pocock 等业内前沿的 Agentic Engineering 最佳实践，针对单人多项目交付、前台模型工程化约束及与 `spec-anchor` 协同进行了深度定制演进。

---

## 技能全景（59 个技能，一个入口）

干活从 `/pstack-mode` 进。它按任务选一个 playbook，再打开下面的叶子。playbook 跟入口在同一目录，判据在 `skills/judgment/`。

```text
入口  pstack-mode
  │
  ├─ playbook   feature  bug-fix  design  prototype  refactor
  │             review  simplify  handoff  authoring  repo-audit  investigate
  │
  ├─ 会交给下一步   grilling → domain-modeling → compare-shapes → to-spec
  │                → codebase-design → architect
  │                arena 与 compare-shapes 同格：候选值得各跑一整次时用它
  │                wayfinder 清空地图后从 to-spec 接入
  │                figure-it-out 没有 playbook 对得上时，自己设计一条
  │
  ├─ 判据（22） laziness-protocol  separate-before-serializing-shared-state
  │             sequence-verifiable-units  prove-it-works  attack-the-premise
  │             explain-the-number  test-behavior-not-implementation  model-the-domain
  │             exhaust-the-design-space  fix-root-causes  boundary-discipline
  │             type-system-discipline  build-the-lever
  │             encode-lessons-in-structure  guard-the-context-window
  │             minimize-reader-load  never-block-on-the-human
  │             outcome-oriented-execution  redesign-from-first-principles
  │             make-operations-idempotent  migrate-callers-then-delete-legacy-apis
  │             experience-first
  │
  └─ 做到本职就停   how  why  teach  prototype  diagnosing-bugs
                    code-review  blast-radius  code-simplify  correct
                    handoff  recall  writing-for-agents  agent-ready-repository  unslop
                    sharpen  in-your-own-words  ketchup  bro  swarm  show-me-your-work
                    reflect  typescript-best-practices  create-verification-skill
                    maintain-verification-skill  create-formal-verification-skill
                    maintain-formal-verification-skill  statechart
```

判据 22 条都在 `skills/judgment/`，都是 `principle-*` 独立技能，可以 `/` 直点：`principle-laziness-protocol`、`principle-separate-before-serializing-shared-state`、`principle-sequence-verifiable-units`、`principle-prove-it-works`、`principle-attack-the-premise`、`principle-explain-the-number`、`principle-test-behavior-not-implementation`、`principle-model-the-domain`、`principle-exhaust-the-design-space`、`principle-fix-root-causes`、`principle-boundary-discipline`、`principle-type-system-discipline`、`principle-build-the-lever`、`principle-encode-lessons-in-structure`、`principle-guard-the-context-window`、`principle-minimize-reader-load`、`principle-never-block-on-the-human`、`principle-outcome-oriented-execution`、`principle-redesign-from-first-principles`、`principle-make-operations-idempotent`、`principle-migrate-callers-then-delete-legacy-apis`、`principle-experience-first`。

跨叶子反复用、又不属于某一个叶子的放这里；只属于某一个叶子的判据写在那个叶子的正文里（`diagnosing-bugs` 的判据段、`code-review` 的 Standards 轴）。上游对照时，这 22 条和 poteto 的同名技能一一对得上。

上游对照在 `docs/upstream.md`。Matt Pocock 和 poteto 的技能路径钉在某一次提交上。处置列用来标「不需要」。下次对名单时，表里没有的路径就是新增。

---

## 技能地图（本地服务）

地图不再是仓库里的文件。它由 `scripts/serve-skill-map.py` 现算，只活在内存和一个临时目录里：

```bash
python3 scripts/serve-skill-map.py                        # http://127.0.0.1:8777，自动开浏览器
python3 scripts/serve-skill-map.py --port 9000 --no-open   # 换端口、不开浏览器
```

五个层次：入口 → playbook → 叶子 → 判据 → reference。边分 `routes`／`trigger`／`registry`／`calls`／`mentions`／`reads` 六种，全从正文读出：`` `name` ``、`../<name>/SKILL.md`、以及任何指向本技能目录内 `.md` 的路径（链接或反引号都算）。

- **默认是卡片墙**：一张卡一个技能，名字下面一句中文说它干什么，再带入／出边数和行数。这批中文只活在 `scripts/serve-skill-map.py` 的 `NOTES` 字典里，按请求注入页面，不写任何文件；键是技能名或 `pb:<playbook>`，漏掉的回落成 frontmatter 里那句英文。右上 `▦` 在卡片和关系图之间切，选择记在 localStorage。

- **点节点**：左侧详情给入出边，右侧抽屉直接显示那个文件——frontmatter 加正文，按 Markdown 渲染（标题、列表、表格、代码块、引用）。双击节点或按抽屉里的 `⤢` 全屏，`Esc` 关闭。
- **面板可调**：左栏右缘、抽屉左缘都能拖宽，左栏还能收成 `»` 再展开；宽度与收起状态存在 localStorage，刷新后保持。抽屉还能切悬浮（`⧉` 浮起、`▤` 归位）——浮起后脱离布局盖在图上，拖标题栏移动，位置和模式一并记住。
- 第一次请求前重建一次；之后轮询 `skills/` 与生成脚本（默认 0.8 秒，`--interval` 可调），一改就重建并用 SSE 让页面自己刷新。右下角徽标显示连接与重建状态。
- 端点：`/` 地图、`/doc/<id>` 单篇正文（JSON，`<id>` 可以是技能名、`pb:<playbook>`、或 `skills/…​.md` 路径）、`/graph.json` 节点与边、`/events` SSE、`/status` 上次构建的计数与 hub。
- 只监听 `127.0.0.1`，`Ctrl-C` 停。重建不写仓库；`skill-map.html` 已进 `.gitignore`。想要一份静态快照就 `python3 scripts/build-skill-map.py --out .`，但静态文件没有 `/doc`，点开节点会提示你起服务。

## 安装

两种范围，两种落盘方式：

- **用户级**：符号链接，指向本仓库。改技能立即生效，只存在于这台机器。
- **项目级**：把技能目录**复制**到目标仓库的 `.agents/skills/<技能名>/`。副本不依赖本机路径，可以提交，云端 Agent 也能读到。再次执行同一命令会覆盖同名副本。

技能 `name` 是扁平命名空间，同名只加载先发现的那个。目标仓库若已通过用户级链接看到同名技能，不要再在项目里装一份。

入口在 2026-10 从 `kstack-mode` 改名回 `pstack-mode`。旧装过的要清一次：用户级单独链过的用 `./scripts/install.sh --uninstall --user kstack-mode` 拆掉旧链接；项目级副本脚本已经找不到它了，手动 `rm -rf <仓库>/.agents/skills/kstack-mode`。

2026-11 另有三个技能改了名，向官方名对齐：`how-it-works` → `how`、`why-this-way` → `why`、`clarify-decisions` → `grilling`。用户级整库链接跟着仓库走，不用动；项目级副本要手动 `rm -rf <仓库>/.agents/skills/how-it-works <仓库>/.agents/skills/why-this-way <仓库>/.agents/skills/clarify-decisions` 再重装，否则旧名副本会和新名一起被加载。

需要 Node.js 18+。macOS / Linux 用 `scripts/install.sh`，Windows 用 `manage-skills.ps1`（转发给同一个 `scripts/install.mjs`）。

### Codex 自动加载

Codex 使用每个技能的 `agents/openai.yaml`：

```yaml
policy:
  allow_implicit_invocation: false
```

仅 4 个技能设为 `true`：`diagnosing-bugs`（故障诊断）、`typescript-best-practices`（TypeScript）、`writing-for-agents`（代理文档）、`unslop`（文字整理）。这些技能适合按明确任务自动触发。

其余 55 个设为 `false`，包括 `pstack-mode`、规划、评审、并行工作和全部 `principle-*`。它们不默认进入模型上下文，仍可用 `$技能名` 或技能选择器调用。已选流程也可按路径读取叶子。`false` 控制自动加载，不隐藏技能选择器中的条目。

白名单唯一来源是 `scripts/configure-codex-skills.py`。新增技能默认手动调用。检查或生成配置：

```bash
python3 scripts/configure-codex-skills.py
python3 scripts/configure-codex-skills.py --write
python3 scripts/configure-codex-skills.py --skills-root /path/to/repo/.agents/skills
```

生成器遇到带额外字段的自定义配置会停止并报告文件，避免覆盖 UI 或依赖设置。安装器会连同技能复制 `agents/openai.yaml`；用户级链接直接使用源配置。

`SKILL.md` 中的 `disable-model-invocation: true` 保留供 Claude Code 使用。它不能替代 Codex 配置。配置格式依据本机 Codex 随附的 `skill-creator/references/openai_yaml.md`。当前会话已收到的技能列表不会被本次文件修改撤回；在新会话中检查加载结果。

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
./scripts/install.sh --user grilling unslop
```

```powershell
.\manage-skills.ps1 -Install all
.\manage-skills.ps1 -Install grilling,unslop
```

- **验证**：`find -L ~/.agents/skills/shukang -name SKILL.md | wc -l` 应输出 `59`，且 `test -L ~/.agents/skills/shukang`
- **卸载整库**：`./scripts/install.sh --uninstall --user`
- **卸载单个链接**：`./scripts/install.sh --uninstall --user unslop`（整库链接里的技能不会因此被拆出）

### 项目级（拷贝）

在技能仓库的克隆里，把副本写进目标仓库：

```bash
./scripts/install.sh --project /path/to/repo
./scripts/install.sh --project /path/to/repo unslop grilling
```

```powershell
.\manage-skills.ps1 -Install all -Project "D:\wiki\project\spec-anchor"
.\manage-skills.ps1 -Install unslop -Project "D:\wiki\project\spec-anchor"
```

没有克隆时，在目标仓库里用 npx（改动推到 GitHub 之后才走这条）：

```bash
npx --yes github:shukang11/skills --project .
```

落点是普通目录，不是指向技能仓库的链接：

```text
<仓库>/.agents/skills/unslop/
├── SKILL.md
└── references/    # 技能自带的参考文件会一起复制
```

- **验证**：`test ! -L <仓库>/.agents/skills/unslop && test -f <仓库>/.agents/skills/unslop/SKILL.md`
- **更新**：对同一仓库再执行一次安装命令
- **卸载**：`./scripts/install.sh --uninstall --project /path/to/repo unslop`
- **查看**：`./scripts/install.sh --list` 或 `./scripts/install.sh --list --project /path/to/repo`

---

## 日常调用姿势

审查当前未提交工作时，[review](skills/mode/pstack-mode/playbooks/review.md) 会固定任务范围并检查工作树漂移。保持行为不变的结构调整走 [refactor](skills/mode/pstack-mode/playbooks/refactor.md)，使用相同输入核对前后结果。

重复错误交给 `principle-encode-lessons-in-structure` 固化防护。难以追踪的层次与状态交给 `principle-minimize-reader-load`。同一前提下两次修复失败时，用 `principle-attack-the-premise` 检查前提，再决定下一次修改。

1. **从入口进**（一套任务走完）：`/pstack-mode`，后面加一句任务。入口选 playbook，再按步骤读叶子。
2. **直接点叶子**（只做这一件事）：`/how`、`/why`、`/compare-shapes`、`/grilling`、`/to-spec`、`/unslop`、`/sharpen`、`/in-your-own-words`、`/ketchup`、`/bro`、`/handoff`、`/recall`、`/agent-ready-repository` 等。这时不走 playbook。
3. **直接点判据**（只校准一件事）：`/principle-*` 共 22 条，见上面清单。同样不走 playbook。
