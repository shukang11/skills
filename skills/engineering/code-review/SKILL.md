---
name: code-review
description: "针对自指定锚点（commit、branch、tag 或 HEAD~N）以来的代码变更进行【双轴独立审查】：Standards 轴（代码规范与 Martin Fowler 坏味道体检）与 Spec 轴（是否忠实满足原始需求规格）。"
argument-hint: "指定 review 的基准点（例如 main, HEAD~1, 或具体 commit SHA）及对应的 Spec 路径"
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
优先遵循项目根目录的编码规范文档（如 `CODING_STANDARDS.md`、`CONTRIBUTING.md`）。
若无，则自动套用 **Martin Fowler 重构经典坏味道基线**：
- **Mysterious Name（晦涩命名）**：命名无法直观表达其意图。
- **Duplicated Code（重复代码）**：同一逻辑形态在多处重复出现。
- **Feature Envy（依恋情结）**：某个函数/方法过度访问另一个对象的数据，而非自身。
- **Data Clumps（数据泥团）**：几个参数总是一起成群结队传递。
- **Primitive Obsession（基本类型偏执）**：用原始 string/number 替代本应独立的领域概念。
- **Shotgun Surgery（散弹式修改）**：一个逻辑特性的变动导致大量无关文件产生散落的微小修改。
- **Divergent Change（发散式修改）**：一个模块经常因为多个完全不相干的原因被修改。
- **Speculative Generality（夸夸其谈/过度抽象）**：为了当前根本不存在的需求添加泛化抽象与胶水钩子。
- **Middle Man（中间人/浅模块）**：某个类或函数除了向下透传没有任何实质功能。

### 4. 产出双轴独立报告

最终报告必须分别在两个独立小节下呈现：

```markdown
## Standards Review (规范与架构质量)
- [Hard / Heuristic] 文件名:行号 - 具体违规或坏味道描述，附改进建议。

## Spec Review (需求忠实度)
- [Missing / Drift / Scope-Creep] 对照 Spec 条目，指明遗漏、偏差或范围蔓延。
```

最后附一句话总结两轴各自的最严重问题，严禁跨轴打平评分。
