---
name: unslop
description: "文档与技术文本去 AI 生成腔，遵循 ASD-STE100 简明技术规范（严格控制句长、消除行话套话、单义词一致性、主动祈使句）。"
argument-hint: "待清洗或重写的文档路径、文本段落或范围"
disable-model-invocation: true
---

# Unslop：简明技术文本与去 AI 腔（ASD-STE100）

对技术文档、规范、README、PR 描述或文本输出进行脱水清洗。
核心目标：**彻底清除大模型生成腔调与虚浮噪音，严格遵循国际简明技术写作规范 ASD-STE100（Simplified Technical English），产出零歧义、低认知负荷、高信息密度的工程级文本。**

## 核心判据：ASD-STE100 结构标准

在审阅和改写任何段落时，必须满足以下 6 条硬性约束：

1. **单义词与一致性（One Word, One Meaning）**：
   - 同一个概念在全文中**只使用唯一指定的术语**，严禁同义词轮换（如在同一处混用“模块”、“组件”、“单元”；或混用“删除”、“清理”、“废弃”）。
   - 词义直白具体，严禁隐喻化或抽象修辞。
2. **句子长度硬指标（Sentence Length Limits）**：
   - **操作步骤/指示句（Procedural）**：英文 ≤ 20 词，中文 ≤ 25 字。
   - **说明/描述句（Descriptive）**：英文 ≤ 25 词，中文 ≤ 35 字。
   - **一句话只讲一个指令或一个事实**。长句、带多重嵌套从句的复合句必须拆分为独立短句。
3. **祈使句与主动语态（Active Voice & Imperative Mood）**：
   - 规则与操作步骤必须使用动词原形开头的祈使句（如：“运行构建脚本”、“更新配置字段”；严禁写成“用户应该运行……”或“构建脚本将被运行”）。
   - 描述客观过程必须指明执行主体（Actor）：“加载器解析该文件”，严禁无主句和滥用被动语态。
4. **名词串联限制（Noun String Discipline）**：
   - 严禁连续堆叠超过 3 个名词进行连环修饰。使用介词展开逻辑从属关系，避免读者解码障碍。
5. **杜绝模糊修饰与主观形容（Zero Vague Qualifiers）**：
   - 彻底删除模糊修饰词：*“适度”、“适当”、“正常”、“轻易”、“充分”、“各种各样”*（英文：*properly, adequately, sufficiently, easily, appropriate, various*）。
   - 必须替换为可衡量的具体数字、物理机制或严格边界（如：“重试达到 3 次”、“超时阈值设为 5000ms”）。
6. **消除悬空代词（No Ambiguous Pronouns）**：
   - 严禁出现指代模糊的“这”、“它”、“其”（this, it, they）。直接重复具体所指的名词。

---

## 核心判据：AI 生成腔（AI Tells）黑名单

凡发现以下 AI 模式，立即重写或删除：

### 1. 词汇与词套
- **高频 AI 行话**：*additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape（抽象场景）, pivotal, showcase, tapestry（织锦/体系）, testament, underscore, vibrant* 等。直接换为最平实的词（如 delve → investigate/read，enhance → improve/add）。
- **花哨系动词**：*“serves as”、“stands as”、“boasts”、“features”*。一律直白改用“是（is）”或“包含（has）”。
- **二元句式**：*“Not just X, but Y”（不仅……而且……）*。删掉前半句铺垫，直接陈述 Y。
- **生硬排比**：严禁无逻辑地凑齐“三个并列动词”或“三个名词短语”（Rule of Three）。依客观事实确定数量。
- **客服套话与阿谀奉承**：*“I hope this helps!”、“Let me know if...”、“Great question!”、“Certainly!”、“Of course!”* 一律彻底删除。

### 2. 格式与标点噪音
- **滥用破折号（—）**：禁止用长破折号断句。直接句号断句或用逗号。
- **滥用中句冒号（:）**：冒号仅用于列表或示例引出，严禁在句子中间充当转折连接符。
- **全篇加粗与标题滥用**：严禁每个专业名词都加粗；标题使用首字母大写（Sentence case），严禁使用装饰性 Emoji。

### 3. 内容脱水
- **谈机制与数字，不谈感觉**：
  - ❌ “数据库触手可及，让你体验极速的响应”
  - ✅ “`.toSQL()` 返回发送给数据库的原始字符串，查询耗时控制在 5ms 以内”
  - 凡是放到别的项目也“通顺可用”的空话，直接删掉。
- **删除废话前缀**：*“In order to” → “To”*；*“Due to the fact that” → “Because”*；*“It is important to note that”（值得注意的是）* → 直接删除。

---

## 先定模式（Diátaxis）

一份文档一个模式。两个问题定它：内容是在教，还是在干活；是在讲怎么做，还是在讲为什么。

| 意图 | 面向学 | 面向工作 |
|---|---|---|
| 动手做 | tutorial：手把手，每步有可见结果，不讲原理 | how-to：解决具体问题，假定已经会了 |
| 理解 | explanation：讲取舍、历史、约束，可以有观点 | reference：只描述事实，不劝、不表态 |

混了就拆。tutorial 里塞参考表、how-to 里讲原理、reference 里写「推荐这样做」，都是串味。拆不开就先砍到只剩一个模式。

## PR 描述和 commit message 也算写作

除 Diátaxis 外，上面所有判据都适用。PR 正文是一分钟能读完的简报：改了什么、为什么、怎么验。不贴日志、SHA 列表和指标表，链接过去。

## 执行流程

1. **扫描文本**：对照 ASD-STE100 六条标准与 AI Tells 黑名单逐段扫描。
2. **定点改写**：
   - 拆解超长句与复杂从句，落实主动祈使句；
   - 替换 AI 行话与花哨句型为单义平实表达；
   - 将主观形容换为机制、数字或明确判据。
3. **收工检查**：
   - 检查是否有单句超过长度限制；
   - 检查是否存在未指明的模糊代词或同义词混用；
   - 对比改写前后，含义完全保真且信息密度显著提升。

详细规则清单与词汇替换表，参阅 [references/ste-100-rules.md](references/ste-100-rules.md)。
