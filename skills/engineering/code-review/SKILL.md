---
name: code-review
description: "针对自指定锚点（commit、branch、tag 或 HEAD~N）以来的代码变更进行【双轴独立审查】：Standards 轴（代码规范与 Martin Fowler 坏味道体检）与 Spec 轴（是否忠实满足原始需求规格）。"
argument-hint: "指定 review 的基准点（例如 main, HEAD~1, 或具体 commit SHA）及对应的 Spec 路径"
disable-model-invocation: true
---

# Code Review

针对 `HEAD` 与用户指定锚点之间的 Git Diff，开展双轴独立审查：

- **Standards 轴**：代码是否符合项目规范？是否存在经典的软件坏味道？
- **Spec 轴**：代码是否忠实实现了原始 Spec 规格中要求的行为与验收准则？

两轴彼此独立审查，结果分别呈现，严禁互相掩盖或打平。

## 审查流程

### 1. 锁定 Diff 基准点
- 获取并校验用户指定的基准点（如 `main`、`git diff <base>...HEAD`）。
- 确认 Diff 非空。

### 2. 定位 Spec 来源
按以下优先级寻找原始 Spec 规格：
1. 本地 `.agents/notes/proposed/` 或 `.agents/notes/` 下的相关 Spec 文件；
2. 本地 `docs/` 下的对应需求/规格说明；
3. 用户在参数中直接指定的 Spec 路径；
4. 若无 Spec，则注明“无 Spec 规格”，仅执行 Standards 轴审查。

### 3. 定位 Standards 来源
按以下顺序叠加，不互相替代：
1. 项目有 `.agents/skills/spec-anchor/references/evolution-principles.md` 的，逐条对照七条演进原则；违反的发现类别写「原则 N」。
2. 项目根 `AGENTS.md` 的实现原则与禁区，以及编码规范文档（如 `CODING_STANDARDS.md`、`CONTRIBUTING.md`）。
3. 上面都没有覆盖到的，套用 **Martin Fowler 重构经典坏味道基线**：
- **Mysterious Name（晦涩命名）**：命名无法直观表达其意图。
- **Duplicated Code（重复代码）**：同一逻辑形态在多处重复出现。
- **Feature Envy（依恋情结）**：某个函数/方法过度访问另一个对象的数据，而非自身。
- **Data Clumps（数据泥团）**：几个参数总是一起成群结队传递。
- **Primitive Obsession（基本类型偏执）**：用原始 string/number 替代本应独立的领域概念。
- **Shotgun Surgery（散弹式修改）**：一个逻辑特性的变动导致大量无关文件产生散落的微小修改。
- **Divergent Change（发散式修改）**：一个模块经常因为多个完全不相干的原因被修改。
- **Speculative Generality（夸夸其谈/过度抽象）**：为了当前根本不存在的需求添加泛化抽象与胶水钩子。
- **Middle Man（中间人/浅模块）**：某个类或函数除了向下透传没有任何实质功能。

### 4. 行为证据（区间里有生产代码改动时才跑）

只看 diff 分不清「测试钉住了这次变化」和「测试跟着一起改绿」。脚本在临时 worktree 里检出锚点，只把测试侧文件 overlay 上去，前后各跑一次，用红绿说话。

```bash
node .agents/skills/code-review/scripts/fix-proof.mjs \
  --range <锚点>..HEAD \
  --cmd '<按文件跑测试的命令，含 {files}>' \
  --setup '<装依赖的命令>'
```

- `{files}` 换成空格分隔、已加引号的测试文件。命令里没有 `{files}`：不跑。
- 区间 diff 里有且只有一个锁文件时加 `--lockfile <路径>`，该文件 blob 变了才重装依赖。
- 默认认 JS/TS、Go、Python、Rust、Java、Kotlin 的测试文件。本项目不是这些时，用 `--tests '<正则>'` 整段替换。
- 输出含「无法计算」：脚本算不出来，交给人，停。不要写成「没有测试改动」。
- `--per-commit` 的交界判定名（`父提交红 本提交绿` 等）与区间判定名不同，两者不互换。

判定 → 报告：

| 判定 | 写进报告 |
|---|---|
| `锚点红 HEAD 绿` | 有测试钉住这次变化，不单开发现 |
| `新增测试在锚点就绿`、`改动的测试在锚点就绿` | `[Missing]` 改动没有回归证据 |
| `无测试文件改动` | `[Missing]`，且只在区间确有生产代码改动时报。它只说明测试文件没变，不说明已有测试盖不住 |
| `已有断言被删改` | `[Drift]` 判据被改了。附 `git diff <锚点> HEAD -- <文件>` 里以 `-` 开头的行，交人裁决 |
| `加载失败` | `[Missing]`，备注写「复现未证实」 |
| `HEAD 不绿`、`超时`、`环境失败` | `[Missing]`，附备注行 |

备注行可能是栈里的任意一行（`name: 'AssertionError'` 这类）。判据是「判定」，不是备注。

### 5. 产出双轴独立报告

最终报告必须分别在两个独立小节下呈现：

```markdown
## Standards Review (规范与架构质量)
- [Hard / Heuristic] 文件名:行号 - 具体违规或坏味道描述，附改进建议。

## Spec Review (需求忠实度)
- [Missing / Drift / Scope-Creep] 对照 Spec 条目，指明遗漏、偏差或范围蔓延。
```

最后附一句话总结两轴各自的最严重问题，严禁跨轴打平评分。
