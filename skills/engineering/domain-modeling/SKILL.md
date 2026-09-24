---
name: domain-modeling
description: 构建与校准项目的领域模型（Domain Model）。当讨论代码库术语、定义状态机实体、维护领域词汇表（docs/glossary.md 或 docs/domain-models.md）以及提炼核心架构决策记录（ADR）时使用。
argument-hint: "你想建立或澄清哪个领域概念/名词/实体？"
---

# Domain Modeling

在方案设计与架构推演中，主动构建并锐化项目的领域模型。这是一个**主动纠偏**纪律：挑战模糊术语、推演边缘场景，并在概念一旦结晶时即刻更新词汇表与决策记录。

## 文档组织契约

优先将领域知识收敛至项目文档目录：

```
/
├── docs/
│   ├── glossary.md          ← 统一领域词汇表（或 domain-models.md）
│   └── adr/                 ← 系统级不可逆决策记录
│       ├── 0001-record.md
│       └── 0002-record.md
└── src/
```

- **延迟创建**：仅在有实际概念需要沉淀时才创建对应文档。
- **纯粹性**：`docs/glossary.md` 仅存放领域名词与概念定义，严禁塞入具体的实现细节或临时草稿。

## 运行准则

### 1. 对照既有词汇表就地纠偏（Challenge against the glossary）
当上下文或用户使用的术语与 `docs/glossary.md` 中的既有定义冲突时，Agent 必须立即指明并对齐：“词汇表将 X 定义为 A，但当前用法似乎指向 B，请问以哪个为准？”

### 2. 锐化模糊语言（Sharpen fuzzy language）
当出现多义、笼统的名词时，提炼出精准的规范术语（例如：“你说的 'Account' 指的是 Customer 还是 User？”）。

### 3. 用极限场景推演边界（Discuss concrete scenarios）
讨论领域实体关系时，设计具体极限场景施压测试（例如：“如果订单处于 '已支付待发货' 状态，用户发起部分退款，系统状态机该如何流转？”）。

### 4. 与代码自查对照（Cross-reference with code）
检查当前代码事实是否与领域描述相符，发现矛盾主动指出。

### 5. 即时更新词汇表（Update inline）
一旦某个领域概念达成共识，立即就地同步更新 `docs/glossary.md`，不积压到最后。

### 6. ADR 极简三铁律（Offer ADRs sparingly）
只有当且仅当满足以下全部 3 个条件时，才建议建立 ADR（落地至 `docs/adr/` 或 `.agents/notes/proposed/`）：
1. **极难逆转**：推翻决策的成本和代价极大；
2. **缺乏背景会令人意外**：未来维护者阅读代码会困惑“为什么当初采用这种方案”；
3. **真实权衡的结果**：在多个可行方案中做了深度 Trade-off。
