# 第 10 步：跨资产检查与最终内容包

最后一步不重新发明观点，而是检查正文、标题、历史材料、正文图片和封面是否互相一致。

## 目录

- 跨资产一致性
- 发布前强制格式校验
- 文章交付检查
- 图片数量不足时的处理
- 最终文件结构
- `article.md` 最低结构
- 信息来源排版规范
- 机器内容包
- 封面失败
- 第 11 步上传产物

## 跨资产一致性

至少检查：

- 正文 ↔ 主标题；
- 正文 ↔ 3 个备选标题；
- 正文 ↔ 历史案例；
- 正文 ↔ 正文配图；
- 正文 ↔ 封面；
- 标题 ↔ 封面。

典型错误包括：正文写“征求意见”，标题写“正式落地”；历史案例只是有限类比，封面却把历史事件画成当前主事件。

## 发布前强制格式校验

在进入第 11 步前必须运行：

```bash
python "$SKILL_DIR/scripts/validate_article_format.py" "/absolute/path/output/article.md"
```

退出码必须为 `0`。如果校验失败，先按错误提示修正文，再重新运行；不得绕过校验直接上传草稿。

## 文章交付检查

- 总字数不超过 1500 字；
- 有且只有 2 个 `##` 小标题；
- 两个小标题都有具体判断或问题指向；
- 至少 2 张 `AUTO_INSERT` 正文图片；
- 所有正文图片路径以 `.png` 结尾；
- **配图 1 紧邻第一个 `##` 小标题之前；配图 2 紧邻第二个 `##` 小标题之前；**
- 图片图注、来源和权利状态齐全；
- 历史案例仍保留可比与不可比边界；
- 第 6 步没有把不确定性润色掉；
- 文末来源真实存在；
- 正文每个完整句子后必须写入两个换行符（`\n\n`），形成独立段落和段间空行；
- 信息来源格式统一，每条使用 `- ` 项目符号，且条目之间保留一个空白行；
- 没有具体投资建议、收益承诺或未公开信息暗示；
- 没有明显 AI 主持人式语言。

## 图片数量不足时的处理

如果真实新闻图通过权利闸门后少于 2 张，不能直接交付。必须基于已核实事实或数据生成原创 PNG 数据图、机制图或时间线图，直到至少有两张 `AUTO_INSERT` 配图。版权不明确的媒体图片仍只保留为候选。

## 最终文件结构

```text
output/
├── article.md
├── cover.png                    # 封面成功时存在
├── images/
│   ├── 01-before-subtitle-1.png
│   ├── 02-before-subtitle-2.png
│   ├── 03-extra.png             # 可选
│   └── 04-extra.png             # 可选
└── article-package.json
```

## `article.md` 最低结构

```markdown
# 主标题

开篇……

![配图1](images/01-before-subtitle-1.png)

*图：……来源：……*

## 第一个有判断感的小标题

正文……

![配图2](images/02-before-subtitle-2.png)

*图：……来源：……*

## 第二个有判断感的小标题

正文……

---

**信息来源**

- 机构：《标题》，YYYY年M月D日。

- 机构：《标题》，YYYY年M月D日。
```

## 信息来源排版规范

`article.md` 结尾的信息来源必须满足：

- 统一格式：`机构：《标题》，YYYY年M月D日。`
- 只有年份或报告期时如实写成“2025年报告”，不得编造日期；
- 每条来源必须以 `- ` 开头；
- 两条来源之间必须保留一个空白行；
- **禁止 `•`、数字编号、空白项目或仅含标点的来源行**；
- 同一来源重复支撑多处正文时只列一次，除非是同一机构的不同文件；
- 优先按正文首次出现顺序排列，格式必须一致；
- URL、证据层级和内部核查信息保留在 `article-package.json`，正文来源区保持干净。

正确示例：

```markdown
---

**信息来源**

- 中国民用航空局：《重点型号审查成果：C919大型客机》，2022年及后续更新。

- 新华社：《C919首条国际航线将于8月12日开通》，2026年7月18日。

- 香港民航处：《Flight Standards and Airworthiness》，2025年报告。
```

## 机器内容包

`article-package.json` 至少保存：选题、主标题、3 个备选标题、核心事件、核心判断、读者利益、当前研究、历史研究、反面证据、文章路径和字数、正文图片资产、封面状态和来源清单。

所有 `AUTO_INSERT` 正文图片必须记录 `path`、`placement`、`role`、来源、图注和权利状态。候选图片可以继续留在包里，但不能出现在 `article.md`。

## 封面失败

封面为 `prompt_only` 或 `failed` 时，文章和至少两张正文 PNG 图片仍然正常交付。封面失败不能成为跳过正文配图要求的理由。

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
  body_image_count: 2
```

允许状态为 `disabled | dry_run | created | failed | skipped_no_cover | skipped_no_credentials`。失败时只能记录脱敏错误，不得保存 `WECHAT_APP_SECRET` 或 `access_token`。
