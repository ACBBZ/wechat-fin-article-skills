# 第 8 步：Source-First 正文配图

正文配图的首要任务是把文章使用的**信息来源直接带到读者面前**。v3.1 默认不把 AI 生图当作常规配图方式，而是先从最终引用来源中截取、提取或下载与正文直接对应的图表、关键页面、表格、公告段落和官方图片；只有来源视觉确实不足时，才进入生成兜底。

封面不计入正文配图数量，封面仍由 `wechat-cover-generator` 独立处理。

## v3.1 核心原则

图片优先级固定为：

```text
信息来源直接截图 / 截取
↓
信息来源中的原始图片或图表
↓
基于信息来源数据制作的可核验图表
↓
AI 生成解释性视觉（最后兜底）
```

硬规则：

- **目标是正文图片 100% 来自文章信息来源。**
- 最终正文至少 3 张 `AUTO_INSERT` PNG，通常 3–5 张。
- 如果已经找到 3 张高相关、可自动使用的来源图片，可以直接以 3 张完成配图，**不得为了“更丰富”再额外生成 AI 图**。
- 如果来源图片能覆盖 4–5 个有价值的语义位置，可以全部使用来源图片。
- 默认目标 `target_source_ratio: 1.0`；只要来源条件允许，直接来源图片应占全部正文图片。
- 在必须兜底时，仍尽量保持直接来源图片占多数；对于 3 张正文图，优先做到至少 2 张为 `source_capture` / `source_asset`。
- 所有最终图片统一保存为 `.png`，并绑定 `section_anchors` 中存在的 `anchor_id`。
- AI 生成图片不能冒充新闻现场、公告原件、人物真实照片或历史档案。

## 第一步：先建立来源视觉清单

在选择任何正文图之前，先读取最终 `sources`，为**每一个实际进入文章信息来源列表的来源**建立 `source_visual_inventory`。

示例：

```yaml
image_strategy:
  mode: source_first
  target_source_ratio: 1.0
  source_visual_search_exhausted: false
  source_visual_count: 0
  selected_source_image_count: 0
  selected_ai_image_count: 0
  ai_fallback_used: false
  source_visual_inventory:
    - source_id: SRC01
      source_title: "某交易所公告"
      source_url: "https://..."
      source_type: official_primary
      inspected: true
      usable_visuals: 2
      candidate_visuals: 0
      notes: "第3页关键条款；第5页流程图"
```

### 什么叫 `inspected: true`

不能只打开来源首页看一眼。

- **HTML 页面**：检查正文中的图片、figure、图表、表格、关键证据段落和官方附件。
- **PDF / 财报 / 公告**：检查与文章引用事实对应的具体页，优先截取关键表格、图表、原文条款或整页关键证据。
- **数据页面**：检查官方图表、时间序列、统计表以及支持下载的原始视觉。
- **公司 / 产品官方页面**：检查与正文事件直接相关的官方产品图、业务图、示意图或发布图片。

只有文章最终使用的来源都完成检查，才可以把 `source_visual_search_exhausted` 设为 `true`。

## 第二步：来源视觉的四种 `origin_kind`

每张图片必须记录 `origin_kind`。

### `source_capture`

直接从文章信息来源的页面或文件中截取。

典型例子：

- 交易所公告第 3 页；
- 财报里的收入分部表；
- 监管文件关键条款；
- 官方数据网页中的图表；
- 公司公告里的原始表格；
- 来源页面中支持核心判断的一小段关键原文。

必须记录：

- `source_id`；
- `source_url`；
- `source_locator`，例如“PDF 第 8 页图 4”“公告第 3 页第二段”“网页 Revenue Breakdown 图表”。

允许合理裁掉浏览器边框、大面积空白或无关区域，也可以添加不遮挡原文的轻量框选；禁止修改来源文字、数字、时间、坐标轴或上下文。

### `source_asset`

来源页面本身提供的原始视觉资产，例如官方产品图、发布会官方图、公开图表文件、机构自己发布的图片。

它仍然必须绑定 `source_id` 与 `source_url`，不能因为下载成独立文件就丢失来源关系。

### `source_derived_chart`

来源本身没有合适视觉，但来源提供了可核验数据，此时可以制作数据图、时间线或简单机制图。

它不是“凭空生图”。所有数字、节点和标签必须能回到 `source_id` 对应的核实材料。

优先使用确定性图表方式表达，不需要为了视觉效果调用生成式图像模型。

### `ai_fallback`

只有前三类仍无法完成最低 3 张正文图时才允许使用。

每张 `ai_fallback` 必须记录 `ai_fallback_reason`，例如：

> 最终 6 个引用来源均已检查，仅找到 1 张可自动使用的来源图；来源数据不足以制作新的可核验图表，因此使用 1 张机制解释视觉补足。

不能写“为了更好看”“丰富画面”“增加视觉冲击”作为 fallback 原因。

## 第三步：选择与停止条件

完成来源视觉清单后，按下面顺序选择。

### 情况 A：来源里有 3 张或更多合适图片

- 选择最能支撑 3–5 个语义锚点的来源图；
- AI 图片数量必须为 0；
- 如果 3 张已经足够，不再继续补图；
- 如果第 4、5 张来源图能明显增加证据或理解，可以继续加入。

### 情况 B：只有 2 张合适来源图

1. 两张来源图全部优先保留；
2. 检查现有来源数据是否能制作 `source_derived_chart`；
3. 能制作时，用来源数据图补成第 3 张并停止；
4. 只有数据图也不可行时，才允许 1 张 `ai_fallback`。

### 情况 C：只有 1 张或 0 张合适来源图

1. 继续确认所有最终引用来源都已经检查；
2. 优先从来源数据制作图表、时间线或机制图；
3. 仍不足 3 张时才使用 AI 解释图补足；
4. `source_visual_search_exhausted` 必须为 `true`；
5. 内容包必须写明为什么来源图片与来源数据都不足。

**AI 只负责补“缺口”，不负责把图片数量从 3 张扩到 4–5 张。**

## 来源图片与语义锚点

Style Skill 返回类似：

```yaml
section_anchors:
  - id: anchor_event
    purpose: current_event
  - id: anchor_mechanism
    purpose: mechanism
  - id: anchor_context
    purpose: historical_or_data_context
```

来源图优先匹配读者刚产生以下问题的位置：

- 这件事真的发生了吗？
- 原文究竟怎么写？
- 这个数字从哪里来？
- 公司自己披露的数据是什么？
- 过去那次事件当时的原始资料是什么？

不要为了让三张图“角色各不相同”而把一个很强的来源证据图换成 AI 机制图。**证据价值高于视觉类型的多样性。**

## 来源视觉优先级

同一个语义锚点有多个选择时，优先级为：

1. 正文引用的 T1 / 官方一手来源中的关键截图、图表或表格；
2. 正文引用的公司、基金公司、交易所、监管、政府等官方来源资产；
3. 用户明确拥有权利或开放许可的来源视觉；
4. 正文引用的媒体来源中权利明确可用的图表或页面视觉；
5. 基于文章来源数据制作的 `source_derived_chart`；
6. `ai_fallback`。

相关性仍是前提。一个与正文锚点无关的官方大楼照片，不能因为“官方”就挤掉更能解释事实的来源数据图。

## 权利边界

### 可自动插入 `AUTO_INSERT`

优先包括：

- 使用条件明确且可追溯的政府、监管、交易所、公司公告、公司 IR、基金公司等官方公开材料；
- 用户明确拥有使用权的来源图片；
- 开放许可或公共领域来源图片；
- 基于已核实来源数据制作的原创图表；
- 在所有来源视觉检查完成后，用于补足最低图片数且明确标记的 AI 解释视觉。

### 只做候选 `CANDIDATE_ONLY`

默认包括：

- 新闻媒体摄影记者作品；
- 商业图库；
- 媒体文章中权利状态不清楚的配图或大面积页面截图；
- 带明确媒体版权标识但没有确认转载许可的图表；
- 权利范围不清楚的历史现场图。

“它就是文章的信息来源”**不等于**“图片就可以自动转载”。这类视觉即使非常相关，也先记录为候选，除非使用条件明确。

### 拒绝 `REJECT`

- 搜索引擎缩略图；
- 来源不明或二次搬运图片；
- 抹水印或通过裁切刻意隐藏版权信息；
- 时间、主体、事件对不上；
- AI 图冒充真实新闻现场或官方文件。

## PDF 与网页截图规则

### PDF

优先截取最小但完整的证据范围：

- 图表要保留标题、坐标、单位、时间和必要注释；
- 表格要保留行列标题和相关脚注；
- 条款截图要保留足够上下文，不能只截一句让语义变重；
- 如果整页上下文很重要，可以截整页再做不改变事实的裁切。

### 网页

- 优先截网页内的原始图表、figure、表格或官方图片；
- 必须截文字证据时，只截支撑正文的必要区域；
- 浏览器导航栏、广告和无关推荐可以裁掉；
- 不把第三方网页 UI 本身包装成“官方文件”。

## `generation_kind` 与 `origin_kind` 的关系

保留原有 `generation_kind`，并新增更重要的来源字段：

| `origin_kind` | `generation_kind` | 含义 |
| --- | --- | --- |
| `source_capture` | `documentary` | 直接从来源截图/截取 |
| `source_asset` | `documentary` | 来源提供的原始图片或图表 |
| `source_derived_chart` | `data_generated` | 根据来源数据制作的可核验图 |
| `ai_fallback` | `ai_explanatory` | 来源不足后的最后兜底 |

`origin_kind` 决定“图片从哪里来”；`generation_kind` 只描述“资产是什么性质”。

## GPT-Image2 的新位置

`awesome-gpt-image-2` 仍然保留，但在正文图流程中的位置后移。

只有 `origin_kind: ai_fallback` 时，才进入 GPT-Image2 Prompt-as-Code 路由。它不参与已有来源图的“美化”或风格重绘，也不能把官方截图重生成一张看起来更漂亮但失去证据属性的图片。

封面仍可以正常使用 GPT-Image2 风格路由，因为封面属于传播资产，不是正文证据图。

## 图注

每张最终图片必须有图注。

- `source_capture`：写明“来源：机构/文件名”，必要时补页码或位置；
- `source_asset`：写明原始发布机构；
- `source_derived_chart`：写明“数据来源：……；本账号整理/绘制”；
- `ai_fallback`：明确写“AI 生成解释性视觉，不代表真实现场”。

不要写“从图中可以清晰看到”这类空话。

## 机器包示例

```yaml
image_strategy:
  mode: source_first
  target_source_ratio: 1.0
  source_visual_search_exhausted: true
  source_visual_count: 3
  selected_source_image_count: 3
  selected_ai_image_count: 0
  ai_fallback_used: false
  source_visual_inventory:
    - source_id: SRC01
      source_title: "交易所公告"
      source_url: "https://..."
      source_type: official_primary
      inspected: true
      usable_visuals: 2
    - source_id: SRC02
      source_title: "公司财报"
      source_url: "https://..."
      source_type: official_primary
      inspected: true
      usable_visuals: 1

image_assets:
  - id: IMG01
    role: primary_evidence
    path: images/01-primary-evidence.png
    anchor_id: anchor_event
    origin_kind: source_capture
    generation_kind: documentary
    source_id: SRC01
    source_url: "https://..."
    source_locator: "PDF 第 3 页"
    caption: "图：交易所公告关键条款。来源：某交易所。"
    copyright_status: AUTO_INSERT
  - id: IMG02
    role: primary_evidence
    path: images/02-results-table.png
    anchor_id: anchor_mechanism
    origin_kind: source_capture
    generation_kind: documentary
    source_id: SRC02
    source_url: "https://..."
    source_locator: "2026H1 财报第 18 页表格"
    caption: "图：公司收入分部数据。来源：公司半年报。"
    copyright_status: AUTO_INSERT
  - id: IMG03
    role: historical_context
    path: images/03-history.png
    anchor_id: anchor_context
    origin_kind: source_asset
    generation_kind: documentary
    source_id: SRC01
    source_url: "https://..."
    caption: "图：官方历史安排示意。来源：某交易所。"
    copyright_status: AUTO_INSERT
```
