# 第 10 步：跨资产检查与最终内容包

最后一步不重新发明观点，而是检查正文、标题、历史材料、Style 结果、Source-First 正文图片和封面是否互相一致。

## 跨资产一致性

至少检查：

- 第 5 步事实锁 ↔ 第 6 步 Style 正文；
- 正文 ↔ 主标题与 3 个备选标题；
- 正文 ↔ 历史案例；
- 正文 ↔ `section_anchors`；
- 正文最终来源 ↔ `image_strategy.source_visual_inventory`；
- 正文配图 ↔ `source_id` / `source_locator` / 图注；
- 正文 ↔ 封面；
- 标题 ↔ 封面。

典型错误包括：正文写“征求意见”，标题写“正式落地”；Style 为了口语化把 17.3% 写成“接近 20%”；截图只保留一句而裁掉改变含义的上下文；已经找到 3 张可用来源图，却仍然为了“更丰富”生成 AI 正文图。

## 发布前强制格式校验

进入第 11 步前必须运行：

```bash
python "$SKILL_DIR/scripts/validate_article_format.py" "/absolute/path/output/article.md"
```

退出码必须为 `0`。如果校验失败，先修正文再重新运行，不得绕过校验直接上传草稿。

## 文章交付检查

- 正文可见文本 3000–3600 字，推荐 3200–3400；
- 默认不要求 `##` 小标题；
- 至少 3 张 `AUTO_INSERT` 正文 PNG 图片，通常 3–5 张；
- 每张自动插入图片绑定有效 `anchor_id`；
- `image_strategy.mode` 必须为 `source_first`；
- 最终 `sources` 中每一个来源都进入 `source_visual_inventory`，并完成视觉检查；
- `source_capture` / `source_asset` / `source_derived_chart` 都能通过 `source_id` 回到最终来源；
- `source_capture` 还必须记录 `source_locator`，如 PDF 页码、表格名、网页图表名或条款位置；
- 如果找到至少 3 张可用来源视觉，`selected_ai_image_count` 必须为 0；
- AI 正文图只能是 `origin_kind: ai_fallback`，不能用于单纯扩充 3 张到 4–5 张；
- `ai_fallback_used: true` 时，`source_visual_search_exhausted` 必须为 `true`，并记录具体 `ai_fallback_reason`；
- 媒体摄影、商业图库或权利不清楚的媒体页面视觉不得因为“是文章来源”就自动转载；
- AI 解释视觉明确不冒充新闻现场、官方文件或原始证据；
- 历史案例保留可比与不可比边界；
- Style 没有改变 `locked_numbers`、`locked_quotes`、反面证据和不确定性；
- 没有输入中不存在的第一手经历；
- 文末来源真实存在且格式统一；
- 没有具体投资建议、收益承诺或未公开信息暗示。

## v3.1 图片不足时的处理

图片不足不是直接进入 AI 生图的条件。

固定补足顺序：

```text
source_capture
→ source_asset
→ source_derived_chart
→ ai_fallback
```

具体执行：

1. 先检查最终所有信息来源的网页、PDF、公告、财报、数据页和附件；
2. 有 3 张合适来源视觉时立即满足最低要求，AI 正文图为 0；
3. 只有 2 张来源视觉时，优先用已核实来源数据制作第 3 张图；
4. 来源截图、来源原始资产与来源数据图合计仍不足 3 张时，才允许 AI 补最低数量缺口；
5. AI 不用于把已经满足最低要求的 3 张图扩充成 4–5 张。

## 最终文件结构

```text
output/
├── article.md
├── cover.png                    # 封面成功时存在
├── images/
│   ├── 01-source-evidence.png
│   ├── 02-source-data.png
│   ├── 03-source-context.png
│   ├── 04-source-extra.png      # 有额外来源视觉时可选
│   └── 05-source-extra.png      # 有额外来源视觉时可选
└── article-package.json
```

如果某张确实需要 AI fallback，文件名可以清楚标识，例如 `03-ai-fallback.png`，不要把生成图伪装成 `source-*`。

## `article.md` 最低结构

正文默认可以没有 H2：

```markdown
# 主标题

开篇正文……

![配图1](images/01-source-evidence.png)

*图：交易所公告关键条款。来源：某交易所。*

正文继续……

![配图2](images/02-source-data.png)

*图：公司半年报收入分部表。来源：公司半年报。*

正文继续……

![配图3](images/03-source-context.png)

*图：历史安排原始材料。来源：某官方机构。*

结尾……

---

**信息来源**

- 机构：《标题》，YYYY年M月D日。

- 机构：《标题》，YYYY年M月D日。
```

图片实际插入位置由 `section_anchors` 的语义决定。

## 信息来源排版规范

`article.md` 结尾的信息来源必须满足：

- 统一格式：`机构：《标题》，YYYY年M月D日。`
- 只有年份或报告期时如实写成“2025年报告”，不得编造日期；
- 每条来源必须以 `- ` 开头；
- 两条来源之间必须保留一个空白行；
- 禁止 `•`、数字编号、空白项目或仅含标点的来源行；
- 同一来源重复支撑多处正文时只列一次，除非是同一机构的不同文件；
- 优先按正文首次出现顺序排列；
- URL、证据层级和内部核查信息保留在 `article-package.json`；
- 机器包中的最终来源最好包含稳定 `id`，供图片的 `source_id` 回指。

## 机器内容包

`article-package.json` 至少保存：

- 选题、主标题、3 个备选标题；
- 核心事件、核心判断、读者利益；
- 当前研究、历史研究、反面证据；
- `style` 与 `article.visible_char_count`；
- `section_anchors`；
- `image_strategy`；
- 正文 `images` 资产；
- 封面状态、`cover_context` 和 `style_reference`；
- 带稳定 `id` 的来源清单；
- 微信草稿状态。

Source-First 示例：

```yaml
image_strategy:
  mode: source_first
  target_source_ratio: 1.0
  source_visual_search_exhausted: true
  source_visual_count: 4
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
      source_title: "公司半年报"
      source_url: "https://..."
      source_type: official_primary
      inspected: true
      usable_visuals: 2
images:
  - id: IMG01
    path: images/01-source-evidence.png
    anchor_id: anchor_event
    role: primary_evidence
    origin_kind: source_capture
    generation_kind: documentary
    source_id: SRC01
    source_url: "https://..."
    source_locator: "PDF 第 3 页"
    copyright_status: AUTO_INSERT
  - id: IMG02
    path: images/02-source-data.png
    anchor_id: anchor_mechanism
    role: primary_evidence
    origin_kind: source_capture
    generation_kind: documentary
    source_id: SRC02
    source_url: "https://..."
    source_locator: "半年报第 18 页收入分部表"
    copyright_status: AUTO_INSERT
```

如果使用 `origin_kind: ai_fallback`，该图片必须记录 `ai_fallback_reason`，同时顶层 `image_strategy` 也必须记录 fallback 原因和来源搜索已耗尽状态。

## 封面失败

封面为 `prompt_only` 或 `failed` 时，文章和至少 3 张正文 PNG 图片仍然正常交付。封面是否 AI 生成与正文 Source-First 规则相互独立。

## 第 11 步上传产物

第 10 步内容包通过后，第 11 步调用 `wechat-draft-uploader`。必须先 dry-run，再决定是否创建真实草稿。

上传阶段新增：

```text
output/
├── draft-result.json
└── preview.html
```

`article-package.json` 增加 `wechat_draft`：

```yaml
wechat_draft:
  enabled: true
  status: created
  draft_media_id: "..."
  result_path: draft-result.json
  preview_path: preview.html
  body_image_count: 3
```

允许状态为 `disabled | dry_run | created | failed | skipped_no_cover | skipped_no_credentials`。失败时只能记录脱敏错误，不得保存 `WECHAT_APP_SECRET` 或 `access_token`。
