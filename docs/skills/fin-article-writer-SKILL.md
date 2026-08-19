---
name: fin-article-writer
description: 当需要把中文财经或投资选题写成经过研究、核查、标题包装、正文配图和封面包装的微信公众号文章时使用。
---

# 财经公众号文章写作编排器

## 定位

把一个财经选题加工成可发布的微信公众号内容包。分析层保持专业财经媒体式的严谨、证据意识和反向验证；表达层负责把复杂问题讲清楚、讲自然；传播层负责标题；证据层负责真实新闻图、官方资料图和数据图；视觉层通过独立的 `wechat-cover-generator` 生成封面；交付层通过独立的 `wechat-draft-uploader` 把最终文章、正文 PNG 配图和封面创建为微信公众号草稿。

## 不可妥协的规则

开始研究或写作前，必须读取 `references/editorial-standards.md`。真实性、推断纪律、不确定性标注和不构成投资建议等规则，高于点击率、故事性、标题刺激度、配图效果和封面表现。

- 对时效性财经事实必须使用当前公开资料核验，不能凭记忆写最新数据、政策状态、公司职务、行情和事件进展。
- 不得编造事件、数字、引语、因果关系、历史关联、图片来源或版权状态。
- 每篇文章都必须研究历史脉络，但只有通过 `references/research-history.md` 相关度闸门的历史材料才能进入正文。
- 最终正文不超过 **1500 字**，且有且只有 **2 个**有判断感的 `##` 小标题。
- **每个完整句子单独成段并留空行**：正文中的一个完整陈述句、问句或感叹句结束后，必须写入两个换行符（`\n\n`），让下一句成为新的 Markdown 段落；不要只换一行，也不要把两个完整句子挤在同一段。
- 正文必须至少插入 **2 张**可自动使用的配图，统一保存为 **`.png`**。
- 两张必需配图分别放在**两个 `##` 小标题之前**：第一张紧邻第一个小标题之前，第二张紧邻第二个小标题之前。可以有第 3、4 张图，但不得破坏这两个固定语义锚点。
- 如果找不到两张版权与来源都可自动使用的真实新闻图，不得用版权不明图片凑数；应使用已核实事实或数据生成原创 PNG 数据图、机制图、时间线图，补足到至少 2 张。
- 第 6 步只允许降低理解门槛，不得改变事实、数字、因果强度、不确定性或核心判断。
- 权利状态不明确的图片不能自动进入发布稿。
- 封面生成失败不影响文章本身交付。
- 第 11 步只允许创建微信公众号草稿，不得群发、正式发布或删除；实际上传前必须先 dry-run。
- 微信公众号 `AppID` / `AppSecret` 只能从外部环境变量或 `$HOME/.config/wechat-draft-uploader/.env` 读取，绝不能写进 Skill、ZIP、`article-package.json`、日志或命令参数。

## 工作流程

### 第 0 步：选题审视

读取 `references/research-history.md`。检查读者价值、同质化程度、证据可得性和可辩护角度。用户已经给出明确角度或明确要求直接写时，可以沿用户方向继续；否则先给出选题建议并等待确认。

### 第 1 步：当前事件、历史脉络与反面证据研究

读取 `references/credible_sources.md` 与 `references/research-history.md`。建立 `research_context`，至少包括：当前事件、原始文件、关键事实、直接前史、历史异常案例、同机制案例、历史应对、反面证据、核心问题和暂定判断。

### 第 2 步：专业初稿

读取 `references/writing-expression.md`。以核实事实和显式推理链写初稿。正文设置恰好两个 `##` 小标题，副标题必须指向具体问题或判断，不能用“一、二”或“市场分析”这类空标题。正文实行“**一句一段 + 段间空行**”：每个完整句子结束后必须写入两个换行符（空一行）再写下一句。

### 第 3 步：反向验证

读取 `references/verification.md`。主动攻击自己的文章：找证据薄弱处、遗漏反面材料、因果跳步、历史类比越界、数据口径冲突、AI 式结构和无支撑断言。

### 第 4 步：修正

逐项执行第 3 步的修正，不得在修正过程中顺手添加未经研究的新事实。

### 第 5 步：事实真实性核查

使用当前网页资料配合 `references/verification.md`，核对日期、数字、主体、引语、来源、因果措辞和历史关系。无法达到证据门槛的内容必须删除、改写或降低确定性。

### 第 6 步：读者表达优化

读取 `references/writing-expression.md`。只改术语解释、句子长度、节奏和自然度；与第 5 步版本逐项对照，保证事实和判断强度不变。删除“值得注意的是”“问题就出在这里”“这背后其实”等主持人式 AI 过渡，直接说事实或判断。

### 第 7 步：标题包装

读取 `references/title-packaging.md`。内部生成 8–12 个候选，执行事实一票否决和加权评分，最终交付 1 个主标题 + 3 个备选标题。

### 第 8 步：正文配图

读取 `references/article-images.md` 与 `references/compliance_guide.md`。最终正文必须至少有 2 张 `AUTO_INSERT` 图片，统一转换或生成成 `.png`。第一张放在第一个 `##` 小标题之前，第二张放在第二个 `##` 小标题之前。优先顺序是：当前事件原始证据、官方公开资料、历史新闻证据、基于已核实数据生成的原创图。

### 第 9 步：封面生成

**必须调用子 Skill：** `wechat-cover-generator`。

按照 `references/cover-contract.md` 生成 `cover_context`，调用封面 Skill，并记录 `generated | prompt_only | failed`。正文配图规则与封面规则互不替代：封面不计入“至少 2 张正文配图”。

### 第 10 步：跨资产一致性与打包

读取 `references/output-contract.md`。检查正文、标题、历史材料、正文图片和封面是否互相一致，再写出人类可读的文章和机器可读的内容包。交付前必须运行 `python "$SKILL_DIR/scripts/validate_article_format.py" "/absolute/path/output/article.md"`；只有校验通过，才允许进入第 11 步。校验器会硬检查：每个正文完整句子后至少两个换行符、恰好两个 `##` 小标题、信息来源使用 `- ` 项目符号、条目之间留一个空白行、无空项目与重复、格式统一。

### 第 11 步：微信草稿上传

**必须调用子 Skill：** `wechat-draft-uploader`。

读取 `references/wechat-draft-upload.md`。默认在第 10 步通过后执行：先对 `output/article.md` 做 dry-run，确认标题、预览文件和正文图片数量正确；只有 dry-run 通过、`output/cover.png` 存在且外部凭据可用时，才允许创建公众号草稿。成功后把 `draft_media_id`、正文图片数量、预览路径和结果文件路径写回 `article-package.json.wechat_draft`。

如果用户显式设置 `wechat_draft.enabled=false`，记录 `status: disabled` 并跳过。封面不是 `generated` 时记录 `skipped_no_cover`；缺少外部凭据时记录 `skipped_no_credentials`；API 或上传失败记录 `failed` 和脱敏错误。任何上传失败都不能删除或破坏已经完成的文章、配图和封面。

## 必读参考文件

- 编辑底线与推断纪律：`references/editorial-standards.md`
- 可信来源与证据层级：`references/credible_sources.md`
- 选题、当前研究与历史研究：`references/research-history.md`
- 写作与表达优化：`references/writing-expression.md`
- 反向验证与事实核查：`references/verification.md`
- 标题包装：`references/title-packaging.md`
- 正文配图：`references/article-images.md`
- 合规与图片权利：`references/compliance_guide.md`
- 封面交接契约：`references/cover-contract.md`
- 最终内容包：`references/output-contract.md`
- 微信草稿上传：`references/wechat-draft-upload.md`
- 机器校验规则：`references/article-package.schema.json`
- 发布前格式校验器：`scripts/validate_article_format.py`

## 最终输出

至少写出：

- `output/article.md`
- `output/article-package.json`
- `output/images/01-before-subtitle-1.png`
- `output/images/02-before-subtitle-2.png`
- 当封面子 Skill 成功生成时写出 `output/cover.png`
- 第 11 步运行后写出 `output/draft-result.json` 和 `output/preview.html`

可以再增加第 3、4 张正文配图，但所有正文配图必须是 PNG。标题评分、未采用历史案例、图片权利审核、候选图片和内部核查日志放进结构化内容包，不要默认倾倒给普通读者。
