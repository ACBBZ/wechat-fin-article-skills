# 第 8 步：正文证据图与解释性视觉

正文配图的任务不是装饰，而是增加证据感、现场感、机制理解和历史纵深。封面不计入正文配图数量。

## 数量与位置

- **最终正文至少 3 张 `AUTO_INSERT` 配图，通常 3–5 张。**
- 所有最终正文图片统一保存为 **`.png`**。
- 不再把必需图片固定到第一个、第二个 `##` 小标题之前。
- 第 6 步 `fin-writing-style` 返回 `section_anchors`，第 8 步根据文章语义选择图片并绑定 `anchor_id`。
- 默认至少覆盖三个语义角色：当前事件/主证据、机制解释、历史或数据语境。

推荐文件名：

```text
output/images/01-primary-evidence.png
output/images/02-mechanism.png
output/images/03-context.png
output/images/04-extra.png
output/images/05-extra.png
```

## 语义锚点

Style Skill 可以返回：

```yaml
section_anchors:
  - id: anchor_event
    purpose: current_event
  - id: anchor_mechanism
    purpose: mechanism
  - id: anchor_context
    purpose: historical_or_data_context
```

锚点是机器层语义，不需要变成正文可见标题。

插图应放在读者自然产生以下问题的位置：

- 这件事真的发生了吗？
- 这个数字从哪里来？
- 这个机制到底怎么运转？
- 过去发生过什么？
- 两组数据放在一起是什么关系？

图片绑定锚点后，由最终排版在该语义段落附近插入，不要求精确到固定段号。

## 图片角色

### `current_event`

证明“这件事正在发生”的当前事件图片。优先官方活动、产品、业务现场或机构公开图片，必须和正文事件直接对应。

### `primary_evidence`

原始证据图：交易所公告关键页、监管文件、公司公告、基金公告、财报、招股书、官方数据页面等。可以合理裁切空白或框选重点，但不能修改原始文字或制造误导上下文。

### `historical_context`

只用于已经通过历史相关度闸门并实际进入正文的案例。必须核对事件、日期、主体和图注，不能用另一次“看起来差不多”的事件替代。

### `explanatory_data`

基于第 1、5 步已核实数据生成的原创数据图，例如价格与净值、溢价率、成交额、规模、现金流、资本开支等。

### `mechanism_explainer`

解释业务、政策、资金或制度传导机制的原创图。适合“谁影响谁、资金怎么流、条件怎么触发”的问题。

### `timeline`

把已核实的事件节点按时间组织成时间线。不能把推测节点画成已经发生。

### `explanatory_visual`

用于解释抽象概念、对比或文章核心隐喻的原创 AI 视觉。它是表达资产，不是证据资产。

## 三类生成方式

机器包中的 `generation_kind`：

- `documentary`：真实官方/公开资料或可授权证据；
- `data_generated`：基于已核实事实或数据生成的图表、时间线、机制图；
- `ai_explanatory`：AI 生成的概念解释视觉。

`ai_explanatory` **绝不能**伪装成新闻现场、人物真实照片、公告原件或历史档案。

## GPT-Image2 视觉参考

需要生成 `mechanism_explainer`、`timeline` 或 `explanatory_visual` 时，采用和 `wechat-cover-generator` 一致的 Prompt-as-Code 思路：

1. 先判断图片角色和读者问题；
2. 再匹配输出类别，例如 infographic / poster / realistic / illustration；
3. 再匹配 style 和 scene；
4. 参考 `awesome-gpt-image-2` 中最接近的 template / example case；
5. 最后组装主体、构图、信息层级、材质/风格、文字、比例和负面约束。

对于财经解释图，优先 `infographic-engine` 一类的结构化信息图模板；对于纯概念视觉，再考虑插画、写实或海报方向。不要为了“更好看”把数据图变成无法核对的艺术图。

## 至少三张图的补足规则

真实新闻图只有在来源、事件匹配和使用条件都清楚时才能自动插入。如果最终能自动使用的真实图少于 3 张：

1. 不得用版权不明的媒体摄影、搜索缩略图或二手截图凑数；
2. 优先生成原创数据图、时间线图或机制图；
3. 原创图必须基于已核实事实或数据；
4. 仍不足时，可以生成明确标注为解释性资产的 AI 视觉；
5. 最终必须形成至少 3 张 `AUTO_INSERT` PNG，并分别绑定有效 `anchor_id`。

## 图片搜索顺序

每张证据型图片按以下顺序寻找：

1. 正文事实对应的原始来源；
2. 原始页面是否有可用图片、公告或图表；
3. 官方机构、公司、基金公司公开材料；
4. 权威媒体高度相关的历史新闻图；
5. 搜索引擎只用于发现，必须回到原网页核实。

先找事件，再找图。搜索结果缩略图不是可发布资产。

## 权利状态

### 可自动插入 `AUTO_INSERT`

满足使用条件并能追溯来源的官方公开材料、用户明确拥有使用权的图片、开放许可/公共领域图片、基于已核实数据自行生成的原创图，以及明确作为解释性资产生成且不冒充真实证据的 AI 视觉。

### 仅作为候选 `CANDIDATE_ONLY`

新闻媒体摄影、商业图库、带明确媒体版权标识但无法确认转载许可的图片、权利状态不清楚的现场图。

### 拒绝 `REJECT`

来源不明、时间无法确认、二次搬运、抹水印、事件不匹配、AI 图冒充新闻现场、无法追溯原网页的搜索缩略图。

## 格式转换

最终正文只引用 PNG。已经确认可用的源图片可以做无事实改变的格式转换；格式转换不会改变版权状态。不得通过裁水印、镜像、改色等方式“洗图”。

## 图注

每张最终图片都必须有图注，至少说明“这是什么 + 为什么与正文有关 + 来源/生成方式”。

- 真实证据图：写明机构/原始来源；
- 原创数据图：写“数据来源 + 本账号整理/绘制”；
- AI 解释视觉：明确“AI 生成解释性视觉，不代表真实现场”。

不要写“从图中可以清晰看到”这类空话。

## 资产记录

```yaml
section_anchors:
  - id: anchor_event
    purpose: current_event
  - id: anchor_mechanism
    purpose: mechanism
  - id: anchor_context
    purpose: historical_or_data_context

image_assets:
  - id: IMG01
    role: primary_evidence
    path: images/01-primary-evidence.png
    anchor_id: anchor_event
    generation_kind: documentary
    subject: ""
    source: ""
    source_url: ""
    event_date: ""
    caption: ""
    copyright_status: AUTO_INSERT
  - id: IMG02
    role: mechanism_explainer
    path: images/02-mechanism.png
    anchor_id: anchor_mechanism
    generation_kind: data_generated
    caption: ""
    copyright_status: AUTO_INSERT
  - id: IMG03
    role: historical_context
    path: images/03-context.png
    anchor_id: anchor_context
    generation_kind: documentary
    caption: ""
    copyright_status: AUTO_INSERT
```
