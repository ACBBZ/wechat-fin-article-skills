---
name: fin-writing-style
description: 当已经有经过研究、核验或结构化整理的中文财经/商业内容，需要改写成 3000–3600 字、有第一人称作者感、口语节奏、明确判断和自然叙事推进的微信公众号长文时使用。该 Skill 只负责表达，不重新发明事实；用户明确要求写长文、扩写、改成公众号风格、增加作者感或第一人称时也可独立使用，但任何个人经历都必须来自用户明确提供的真实素材。
---

# 财经公众号长文写作风格器

## 定位

把已经确认的事实、观点和素材，写成一篇像“一个有见识、有好奇心、愿意承认局限的人在认真跟朋友聊一件真正关心的事”的公众号长文。

本 Skill 是**表达层**，不是事实研究器。与 `fin-article-writer` 联用时，上游 Writer 对事实、数字、引语、因果强度和不确定性拥有最终权威；本 Skill 不得为了节奏、情绪或传播性改动这些内容。

## 不可妥协的规则

开始写作前必须读取 `references/style-principles.md` 与 `references/first-person-voice.md`。

- 正文可见文本默认 **3000–3600 字**，推荐 3200–3400 字；标题、图片 Markdown、图注和信息来源不计入。
- 不为了凑字数重复观点、堆同义句、增加无证据背景或空泛升华。
- 不新增未经输入确认的事实、数字、引语、人物关系、因果关系或事件状态。
- `locked_numbers`、`locked_quotes`、`uncertainty_constraints`、`verified_facts` 不得被风格改写改变。
- 第一人称可以表达“我注意到什么、我如何判断、我为什么不确定”，但**不得编造亲历**。
- 只有 `author_experience` 明确提供的经历，才允许写成“我做过 / 我见过 / 我当时……”的经历型第一人称。
- 默认不用 `##` 小标题；只有明确的 N 条经验、教程或方法论文章才允许可见分段标题。
- 不使用“首先、其次、最后”“综上所述”“值得注意的是”“不难发现”“让我们来看看”“随着……发展”等报告式套话。
- 不把历史、文化或文学类比写成证据；类比必须保留与当前事件的差异边界。
- 对立观点要先讲到对方也会认可的程度，再表达不同判断；不能靠嘲讽替代论证。
- 正文风格规则不作用于标题、图注、来源列表、URL 和机器 JSON 字段。

## 输入

推荐由 `fin-article-writer` 传入：

```yaml
style_context:
  article_type: research_analysis
  target_length:
    min: 3000
    ideal: 3300
    max: 3600
  core_question: ""
  core_judgment: ""
  reader_stake: ""
  verified_facts: []
  locked_numbers: []
  locked_quotes: []
  counter_evidence: []
  historical_context: []
  uncertainty_constraints: []
  author_experience: []
  author_opinions: []
  style:
    first_person: true
    conversational: true
    tone_intensity: natural
```

`tone_intensity` 支持：

- `restrained`：政策、监管、重大风险、争议主体，口语化但克制；
- `natural`：默认档，像朋友聊天，有判断、有停顿、有自然情绪；
- `spicy`：轻松产品、工具、市场趣闻，可使用更强吐槽和情绪标点，但不能歪曲事实。

如果独立使用且缺少结构化字段，只能从用户提供的文字中提取事实与观点；不确定的地方明确保留，不自行补成确定事实。

## 工作流程

### 第 1 步：吃透素材，不急着写

读取 `references/style-principles.md`。先确认核心问题、核心判断、读者利益、反面材料、可用作者经历和不能改动的事实锁。

使用 HKR 作为表达价值检查：

- H / Happy：有没有让人愿意继续读的好奇、反常或情绪张力；
- K / Knowledge：读者是否得到新的事实、机制、知识或视角；
- R / Resonance：读者是否能在处境或情绪上产生连接。

HKR 只决定表达重点，不允许覆盖事实纪律。

### 第 2 步：选择文章原型

读取 `references/article-archetypes.md`，在以下原型中选择一个主原型：

- 调查实验型；
- 产品体验型；
- 现象解读型；
- 工具分享型；
- 方法论分享型；
- 研究判断型。

财经新闻、政策、公司、市场深度稿默认优先 `research_analysis`（研究判断型）。

### 第 3 步：搭叙事主线

读取 `references/rhythm-and-narrative.md`。先写一句能回答“这篇到底在追什么问题”的主线，再安排：具体切入 → 背景 → 第一层解释 → 新事实/反证 → 更深问题 → 判断 → 边界 → callback。

知识、历史和案例可以短暂偏离主线，但偏出去后必须用一句“扣主线句”拉回来。

### 第 4 步：写第一人称长文

读取 `references/first-person-voice.md` 与 `references/language-patterns.md`。

优先使用：

- 观察型第一人称：我第一眼注意到……
- 判断型第一人称：我的判断是…… / 我更倾向于……
- 边界型第一人称：我现在还不愿意把它叫作……

经历型第一人称只能来自 `author_experience`。

知识要像“聊着聊着顺手掏出来”，不要出现“下面介绍一下”“接下来科普”。允许长短句交替、短句独立成段、疑问句刹车、自然自嘲和不完美停顿。

### 第 5 步：控制 3000–3600 字

先保证论证完整，再调长度：

- 少于 3000：优先补机制、反面证据、历史边界、真实案例或读者处境；
- 超过 3600：优先删重复解释、第二遍结论、无关背景和只起装饰作用的类比；
- 目标不是“写满”，而是在 3000–3600 字内让每一段都推进主线。

### 第 6 步：四层自检

读取 `references/quality-gates.md`，依次执行：

1. L1 硬规则与 AI 套话扫描；
2. L2 风格、节奏、第一人称和心流检查；
3. L3 内容支撑、反方、公平类比和字数质量检查；
4. L4 作者感终审。

任何风格修复都不能改写锁定事实。发现事实问题时返回上游 Writer，而不是在本 Skill 内自行修补。

## 输出契约

返回或交付以下语义：

```yaml
style_result:
  styled_article_text: ""
  visible_char_count: 3300
  article_type: research_analysis
  tone_intensity: natural
  section_anchors:
    - id: anchor_event
      purpose: current_event
    - id: anchor_mechanism
      purpose: mechanism
    - id: anchor_context
      purpose: historical_or_data_context
  style_quality:
    l1: pass
    l2: pass
    l3: pass
    l4: pass
```

`section_anchors` 是给上游配图规划使用的机器语义，不要求变成正文可见标题。

## 必读参考

- 风格底线与 HKR：`references/style-principles.md`
- 六种文章原型：`references/article-archetypes.md`
- 第一人称真实性边界：`references/first-person-voice.md`
- 节奏、叙事、callback：`references/rhythm-and-narrative.md`
- 口语模式与禁用表达：`references/language-patterns.md`
- 改写示例：`references/style-examples.md`
- 四层质量闸门：`references/quality-gates.md`
