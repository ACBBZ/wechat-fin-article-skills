# 微信财经长文 v3 写作风格设计

## 目标

把现有三 Skill 财经公众号工作流升级为四 Skill 工作流：研究与事实层、写作风格层、视觉层、发布层分离。最终正文默认 3000–3600 个可见中文字符，具有第一人称作者感、口语节奏、明确判断、反方理解和自然的历史/文化参照，同时不允许风格改写篡改已核验事实。

## 架构

```text
fin-article-writer
  研究 → 反证 → 核验 → 锁定事实
        ↓
fin-writing-style
  3000–3600 字长文 → 第一人称 → 节奏/叙事 → 四层自检
        ↓
正文图片规划 → wechat-cover-generator → wechat-draft-uploader
```

`fin-article-writer` 仍是编排器与事实权威；新增 `fin-writing-style` 只消费已锁定内容并负责表达，不重新研究事实。`wechat-cover-generator` 增加基于 `awesome-gpt-image-2` 的风格路由参考，但不复制上游全部案例数据。

## 不可妥协约束

- 正文可见文本默认 3000–3600 字，推荐 3200–3400 字；标题、图片 Markdown、图注、信息来源不计入。
- 第一人称分观察型、判断型、经历型；经历型只有在 `author_experience` 明确提供时可使用。
- Style Skill 不得新增未经上游确认的事实、数字、引语、人物关系、经历或因果关系。
- 事实锁定字段优先级高于文风，包括 `locked_numbers`、`locked_quotes`、`uncertainty_constraints`。
- 默认不使用 `##` 小标题；只有明确的 N 条经验、教程、方法论结构才允许可见分段标题。
- 正文图片默认至少 3 张、通常 3–5 张，通过语义锚点定位，不再绑定固定小标题。
- AI 生成视觉只能承担解释、机制、时间线、概念与封面表达，不能冒充新闻现场或原始证据。
- 图片 Prompt 参考 `freestylefly/awesome-gpt-image-2` 的 category → style → scene → example/template 路由思想，保存一个财经场景精选路由表，不复制全部 cases 数据。
- 原有编辑标准、反向验证、来源纪律、草稿上传安全边界继续有效。

## 新 Skill：fin-writing-style

### 定位

把经过核验的内容，写成一个真实、有判断、有好奇心的人愿意坐下来跟读者认真聊完的一篇 3000–3600 字公众号长文。

### 文章原型

保留并泛化参考写作方法：调查实验型、产品体验型、现象解读型、工具分享型、方法论分享型；新增研究判断型用于财经深度稿。

研究判断型默认推进：反常事实 → 为什么值得看 → 关键事实 → 机制 → 反面证据 → 历史/文化参照 → 第一人称判断 → 判断边界 → callback。

### 第一人称

- 观察型：基于已提供材料表达注意点，例如“我第一眼更关心的是……”
- 判断型：表达作者结论，例如“我的判断反而没那么乐观。”
- 经历型：只有用户明确提供的 `author_experience` 可写成亲历叙事。

### 风格方法

保留 HKR、扣主线、节奏波动、知识顺手掏、故意打断、疑问转向、层层剥开、反向论证、反方理解、callback、谦逊铺垫、逐一展示/升番和文化升维；删除具体博主身份、履历、固定署名、联系方式与专属经历。个人口癖改为 `restrained | natural | spicy` 三档语气强度。

### 四层自检

- L1：禁用套话、结构化 AI 腔、正文标点/词汇规则。
- L2：长短句、第一人称、疑问、停顿、扣主线、口语节奏。
- L3：观点支撑、知识输出、反方、公平类比、字数不靠重复灌水。
- L4：作者感终审——读完是否能感觉到一个具体的人在思考，而不是模型在整理材料。

## Writer 与 Style Skill 接口

Writer 在事实核验完成后构造：

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

Style Skill 返回 `styled_article_text`、`visible_char_count`、`section_anchors` 和内部 `style_quality` 结果。Writer 继续负责标题、配图、封面、内容包与上传。

## 图片与语义锚点

内容包使用 `placement_anchor` 替代固定 `before_subtitle_1/2` 语义：

```yaml
section_anchors:
  - id: anchor_event
    purpose: current_event
  - id: anchor_mechanism
    purpose: mechanism
  - id: anchor_context
    purpose: historical_or_data_context
```

每张 `AUTO_INSERT` 图片记录 `anchor_id`、`role`、`path`、来源与版权状态。默认至少 3 张可自动插入 PNG。

## GPT-Image2 风格路由

新增 `references/gpt-image2-style-routing.md`，精选财经常用方向：`infographic-engine`、`poster-layout-system`、写实摄影/概念插画等。每次生成先判断 role，再选择 category/style/scene/template，最后组装 subject、composition、style/materials、text policy、aspect ratio 和 negative constraints。

## 兼容性

Uploader 继续消费标准 Markdown 与本地图片路径，不依赖 H2 数量。信息来源仍使用现有 `- 机构：《标题》，日期。` 结构。正文风格禁用规则不作用于标题、图注、来源和机器 JSON。

## 版本

套件升级为 v3.0.0；`fin-writing-style` 初始版本 1.0.0。