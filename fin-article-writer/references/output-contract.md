# 第 10 步：跨资产检查与最终内容包

最后一步不重新发明观点，而是检查正文、标题、历史材料、正文图片、Style 结果和封面是否互相一致。

## 跨资产一致性

至少检查：

- 第 5 步事实锁 ↔ 第 6 步 Style 正文；
- 正文 ↔ 主标题；
- 正文 ↔ 3 个备选标题；
- 正文 ↔ 历史案例；
- 正文 ↔ 正文配图；
- 正文 ↔ 封面；
- 标题 ↔ 封面。

典型错误包括：正文写“征求意见”，标题写“正式落地”；历史案例只是有限类比，封面却把历史事件画成当前主事件；Style 为了口语化把 17.3% 写成“接近 20%”；AI 解释图被图注写成真实现场。

## 发布前强制格式校验

进入第 11 步前必须运行：

```bash
python "$SKILL_DIR/scripts/validate_article_format.py" "/absolute/path/output/article.md"
```

退出码必须为 `0`。如果校验失败，先按错误提示修正文，再重新运行；不得绕过校验直接上传草稿。

## 文章交付检查

- 正文可见文本 3000–3600 字，推荐 3200–3400；
- 默认不要求 `##` 小标题，使用小标题时必须来自文章原型需要，而不是机器模板；
- 至少 3 张 `AUTO_INSERT` 正文图片，通常 3–5 张；
- 所有正文图片路径以 `.png` 结尾；
- 每张自动插入图片绑定存在于 `section_anchors` 中的 `anchor_id`；
- 图片角色、图注、来源、生成方式和权利状态齐全；
- AI 解释视觉明确不冒充新闻现场或原始证据；
- 历史案例保留可比与不可比边界；
- Style 没有改变 `locked_numbers`、`locked_quotes`、反面证据和不确定性；
- 没有输入中不存在的第一手经历；
- 文末来源真实存在；
- 正文每个完整句子后写入两个换行符（`\n\n`），形成独立段落和段间空行；
- 信息来源格式统一，每条使用 `- ` 项目符号，且条目之间保留一个空白行；
- 没有具体投资建议、收益承诺或未公开信息暗示；
- 没有明显 AI 主持人式语言。

## 图片数量不足时

如果真实新闻图通过权利闸门后少于 3 张，不能用版权不明素材凑数。优先基于已核实事实或数据生成原创 PNG 数据图、机制图或时间线图；必要时增加明确标记为解释性资产的 AI 视觉，直到至少有 3 张 `AUTO_INSERT` 图片。

## 最终文件结构

```text
output/
├── article.md
├── cover.png                    # 封面成功时存在
├── images/
│   ├── 01-primary-evidence.png
│   ├── 02-mechanism.png
│   ├── 03-context.png
│   ├── 04-extra.png             # 可选
│   └── 05-extra.png             # 可选
└── article-package.json
```

## `article.md` 最低结构

正文默认可以没有 H2：

```markdown
# 主标题

开篇正文……

![配图1](images/01-primary-evidence.png)

*图：……来源：……*

正文继续……

![配图2](images/02-mechanism.png)

*图：……本账号整理/绘制。*

正文继续……

![配图3](images/03-context.png)

*图：……来源：……*

结尾……

---

**信息来源**

- 机构：《标题》，YYYY年M月D日。

- 机构：《标题》，YYYY年M月D日。
```

图片实际插入位置由 `section_anchors` 的语义决定，不以这个示例的固定顺序为硬约束。

## 信息来源排版规范

`article.md` 结尾的信息来源必须满足：

- 统一格式：`机构：《标题》，YYYY年M月D日。`
- 只有年份或报告期时如实写成“2025年报告”，不得编造日期；
- 每条来源必须以 `- ` 开头；
- 两条来源之间必须保留一个空白行；
- 禁止 `•`、数字编号、空白项目或仅含标点的来源行；
- 同一来源重复支撑多处正文时只列一次，除非是同一机构的不同文件；
- 优先按正文首次出现顺序排列；
- URL、证据层级和内部核查信息保留在 `article-package.json`。

## 机器内容包

`article-package.json` 至少保存：

- 选题、主标题、3 个备选标题；
- 核心事件、核心判断、读者利益；
- 当前研究、历史研究、反面证据；
- `style`：Skill、状态、文章原型、tone、第一人称设置和质量结果；
- `article.path` 与 `article.visible_char_count`；
- `section_anchors`；
- 正文图片资产；
- 封面状态、`cover_context` 和 `style_reference`；
- 来源清单；
- 微信草稿状态。

示例：

```yaml
style:
  skill: fin-writing-style
  status: generated
  article_type: research_analysis
  tone_intensity: natural
  first_person: true
  quality:
    l1: pass
    l2: pass
    l3: pass
    l4: pass
article:
  path: article.md
  visible_char_count: 3318
section_anchors:
  - id: anchor_event
    purpose: current_event
  - id: anchor_mechanism
    purpose: mechanism
  - id: anchor_context
    purpose: historical_or_data_context
```

所有 `AUTO_INSERT` 正文图片必须记录 `path`、`anchor_id`、`role`、`generation_kind`、来源/生成说明、图注和权利状态。候选图片可以继续留在包里，但不能出现在 `article.md`。

## 封面失败

封面为 `prompt_only` 或 `failed` 时，文章和至少 3 张正文 PNG 图片仍然正常交付。封面失败不能成为跳过正文配图要求的理由。

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
