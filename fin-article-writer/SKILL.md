---
name: fin-article-writer
description: 当需要把中文财经或投资选题写成经过研究、核查、作者型长文表达、标题包装、正文配图和封面包装的微信公众号文章时使用。
---

# 财经公众号文章写作编排器

## 定位

把一个财经选题加工成可发布的微信公众号内容包。研究层保持专业财经媒体式的严谨、证据意识和反向验证；表达层通过独立的 `fin-writing-style` 生成 3000–3600 字、具有第一人称作者感和自然叙事节奏的长文；传播层负责标题；证据层负责真实新闻图、官方资料图和数据图；视觉层通过独立的 `wechat-cover-generator` 生成封面；交付层通过独立的 `wechat-draft-uploader` 把最终文章、正文 PNG 配图和封面创建为微信公众号草稿。

## 不可妥协的规则

开始研究或写作前，必须读取 `references/editorial-standards.md`。真实性、推断纪律、不确定性标注和不构成投资建议等规则，高于点击率、故事性、第一人称、标题刺激度、配图效果和封面表现。

- 对时效性财经事实必须使用当前公开资料核验，不能凭记忆写最新数据、政策状态、公司职务、行情和事件进展。
- 不得编造事件、数字、引语、因果关系、历史关联、个人经历、图片来源或版权状态。
- 每篇文章都必须研究历史脉络，但只有通过 `references/research-history.md` 相关度闸门的历史材料才能进入正文。
- 最终正文可见文本必须为 **3000–3600 字**，推荐 3200–3400 字；标题、图片 Markdown、图注和信息来源不计入。
- 默认**不要求 `##` 小标题**。只有明确的 N 条经验、教程或方法论文章才允许按表达需要使用可见分段标题。
- 正文仍实行“每个完整句子单独成段并留空行”的移动端排版规则；完整句子结束后使用两个换行符（`\n\n`）。
- 正文必须至少插入 **3 张**可自动使用的配图，通常 3–5 张，统一保存为 **`.png`**。
- 配图通过 `section_anchors` / `anchor_id` 与文章语义绑定，不再依赖固定小标题位置。
- 如果找不到足够版权与来源都可自动使用的真实新闻图，不得用版权不明图片凑数；应使用已核实事实或数据生成原创 PNG 数据图、机制图、时间线图，补足到至少 3 张。
- 第 6 步 Style Skill 只允许改变表达，不得改变事实、数字、因果强度、不确定性、反面证据或核心判断。
- 第一人称观察与判断可以增强作者感；第一人称亲历只允许来自用户明确提供的 `author_experience`，不得自行编造。
- 权利状态不明确的图片不能自动进入发布稿。
- AI 生成图片不能冒充新闻现场、公告原件或真实证据。
- 封面生成失败不影响文章本身交付。
- 第 11 步只允许创建微信公众号草稿，不得群发、正式发布或删除；实际上传前必须先 dry-run。
- 微信公众号 `AppID` / `AppSecret` 只能从外部环境变量或 `$HOME/.config/wechat-draft-uploader/.env` 读取，绝不能写进 Skill、仓库、`article-package.json`、日志或命令参数。

## 工作流程

### 第 0 步：选题审视

读取 `references/research-history.md`。检查读者价值、同质化程度、证据可得性和可辩护角度。用户已经给出明确角度或明确要求直接写时，可以沿用户方向继续；否则先给出选题建议。

### 第 1 步：当前事件、历史脉络与反面证据研究

读取 `references/credible_sources.md` 与 `references/research-history.md`。建立 `research_context`，至少包括：当前事件、原始文件、关键事实、直接前史、历史异常案例、同机制案例、历史应对、反面证据、核心问题和暂定判断。

### 第 2 步：专业分析稿

读取 `references/writing-expression.md`。先以核实事实和显式推理链写“事实优先”的专业分析稿，不追求最终文风。这里的任务是把事实、机制、反证和判断边界写完整，给后续 Style Skill 一个稳定底稿。

### 第 3 步：反向验证

读取 `references/verification.md`。主动攻击自己的文章：找证据薄弱处、遗漏反面材料、因果跳步、历史类比越界、数据口径冲突和无支撑断言。

### 第 4 步：修正

逐项执行第 3 步的修正，不得在修正过程中顺手添加未经研究的新事实。

### 第 5 步：事实真实性核查与事实锁定

使用当前网页资料配合 `references/verification.md`，核对日期、数字、主体、引语、来源、因果措辞和历史关系。无法达到证据门槛的内容必须删除、改写或降低确定性。

完成后建立不可被文风修改的事实锁：

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

`author_experience` 只记录用户明确提供且可安全使用的真实经历。没有就保持空数组。

### 第 6 步：作者型长文表达

**必须调用子 Skill：** `fin-writing-style`。

把第 5 步锁定后的 `style_context` 和专业分析稿交给 Style Skill。默认生成 3000–3600 字正文，优先研究判断型；允许第一人称观察、判断和边界表达，默认不使用 `##` 小标题。

Style Skill 返回：

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

逐项对照第 5 步事实锁。数字、引语、不确定性、反面证据或核心判断发生变化时，Style 版本无效，必须按事实锁修正；不得把变化当成“文风调整”。

### 第 7 步：标题包装

读取 `references/title-packaging.md`。内部生成 8–12 个候选，执行事实一票否决和加权评分，最终交付 1 个主标题 + 3 个备选标题。

### 第 8 步：正文配图

读取 `references/article-images.md` 与 `references/compliance_guide.md`。基于第 6 步返回的 `section_anchors` 规划图片。最终正文必须至少有 3 张 `AUTO_INSERT` PNG，通常 3–5 张。

优先顺序：当前事件原始证据、官方公开资料、历史新闻证据、基于已核实数据生成的原创图、用于机制解释的原创视觉。生成图必须标明其解释性角色，不得伪装成真实新闻证据。

### 第 9 步：封面生成

**必须调用子 Skill：** `wechat-cover-generator`。

按照 `references/cover-contract.md` 生成 `cover_context`，调用封面 Skill，并记录 `generated | prompt_only | failed`。Cover Skill 使用 `awesome-gpt-image-2` 的结构化风格路由思想选择模板与视觉语言，但事实约束和禁用视觉始终优先。

正文配图规则与封面规则互不替代：封面不计入“至少 3 张正文配图”。

### 第 10 步：跨资产一致性与打包

读取 `references/output-contract.md`。检查正文、标题、历史材料、正文图片和封面是否互相一致，再写出人类可读的文章和机器可读的内容包。

交付前必须运行：

```bash
python "$SKILL_DIR/scripts/validate_article_format.py" "/absolute/path/output/article.md"
```

只有校验通过才允许进入第 11 步。校验器会硬检查：正文 3000–3600 可见字、每个正文完整句子后至少两个换行符、信息来源使用 `- ` 项目符号、条目之间留一个空白行、无空项目与重复、格式统一。

### 第 11 步：微信草稿上传

**必须调用子 Skill：** `wechat-draft-uploader`。

读取 `references/wechat-draft-upload.md`。默认在第 10 步通过后执行：先对 `output/article.md` 做 dry-run，确认标题、预览文件和正文图片数量正确；只有 dry-run 通过、`output/cover.png` 存在且外部凭据可用时，才允许创建公众号草稿。成功后把 `draft_media_id`、正文图片数量、预览路径和结果文件路径写回 `article-package.json.wechat_draft`。

如果用户显式设置 `wechat_draft.enabled=false`，记录 `status: disabled` 并跳过。封面不是 `generated` 时记录 `skipped_no_cover`；缺少外部凭据时记录 `skipped_no_credentials`；API 或上传失败记录 `failed` 和脱敏错误。任何上传失败都不能删除或破坏已经完成的文章、配图和封面。

## 必读参考文件

- 编辑底线与推断纪律：`references/editorial-standards.md`
- 可信来源与证据层级：`references/credible_sources.md`
- 选题、当前研究与历史研究：`references/research-history.md`
- 专业分析稿与 Style 交接：`references/writing-expression.md`
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
- `output/images/01-primary-evidence.png`
- `output/images/02-mechanism.png`
- `output/images/03-context.png`
- 当封面子 Skill 成功生成时写出 `output/cover.png`
- 第 11 步运行后写出 `output/draft-result.json` 和 `output/preview.html`

可以增加第 4、5 张正文配图，但所有正文配图必须是 PNG。标题评分、未采用历史案例、图片权利审核、候选图片和内部核查日志放进结构化内容包，不要默认倾倒给普通读者。
