# wechat-fin-article-skills

面向中文财经微信公众号的四 Skill 工作流，覆盖选题研究、事实核查、3000–3600 字作者型长文、标题包装、**来源优先正文配图**、GPT-Image2 风格路由封面和微信公众号草稿创建。

当前套件版本：`3.1.0`

## 包含的 Skill

| Skill | 版本 | 用途 |
| --- | --- | --- |
| `fin-article-writer` | 3.1.0 | 研究、反证、事实锁定，并以 Source-First 方式编排正文图片和内容包 |
| `fin-writing-style` | 1.0.0 | 把已核验内容改写成 3000–3600 字、有第一人称作者感和自然叙事节奏的长文 |
| `wechat-cover-generator` | 2.0.0 | 根据文章语义和 GPT-Image2 风格路由生成公众号财经封面或完整生图提示 |
| `wechat-draft-uploader` | 0.5.0 | 预览本地 Markdown，并安全创建微信公众号图文草稿 |

四个 Skill 可以独立安装和触发。完整工作流中，`fin-article-writer` 在事实核验完成后调用 `fin-writing-style`，再完成 Source-First 正文配图，然后调用 `wechat-cover-generator` 和 `wechat-draft-uploader`。

## v3.1：Source-First 正文配图

v3.1 的核心变化是：**正文配图优先直接来自文章实际使用的信息来源，AI 生图只作为最后兜底。**

固定顺序：

```text
信息来源直接截图 / 截取
→ 信息来源中的原始图片或图表
→ 基于信息来源数据制作的可核验图表
→ AI 生成解释性视觉（最后兜底）
```

具体规则：

- 正文仍至少 3 张 `AUTO_INSERT` PNG，通常 3–5 张；
- 默认目标是正文图片 **100% 来自最终信息来源**；
- 配图前必须逐个检查最终 `sources` 的网页、PDF、公告、财报、官方数据页和附件，并建立 `source_visual_inventory`；
- 如果已经找到至少 3 张高相关且可自动使用的来源视觉，正文 AI 图片数量必须为 **0**；
- 不得为了把 3 张图片扩充成 4–5 张而额外调用 AI 生图；
- 来源图片不足时，先基于已核实来源数据制作 `source_derived_chart`；
- 只有来源截图、来源原始资产和来源数据图仍不足最低 3 张时，才允许 `ai_fallback`；
- 使用 AI fallback 前必须确认所有最终来源都已检查，并记录具体 fallback 原因；
- 新闻媒体摄影、商业图库和权利不清的媒体视觉，即使来自文章引用来源，也默认只作为候选，不能自动转载；
- 封面仍可正常使用 GPT-Image2 风格路由，因为封面是传播资产，不承担正文证据职责。

## v3.0 长文与写作风格能力

- 正文为 **3000–3600 可见字**，推荐 3200–3400；
- 独立 `fin-writing-style` 负责第一人称、口语节奏、叙事推进、反方理解和四层“活人感”自检；
- Writer 保持事实权威，Style Skill 不得改变锁定数字、引语、因果强度、不确定性或反面证据；
- 第一人称亲历只允许来自用户明确提供的 `author_experience`；
- 默认不要求固定 `##` 小标题；
- 正文图片通过 `section_anchors` / `anchor_id` 语义定位；
- AI 解释视觉不能冒充新闻现场、公告原件或真实证据。

## 仓库结构

```text
wechat-fin-article-skills/
├── README.md
├── THIRD_PARTY_NOTICES.md
├── fin-article-writer/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/
│   ├── references/
│   └── tests/
├── fin-writing-style/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── wechat-cover-generator/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
└── wechat-draft-uploader/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── pyproject.toml
    ├── src/
    └── tests/
```

每个 Skill 都是可直接检查和安装的源码目录，不需要重组 ZIP 或 Base64 分片。

## 安装

需要：

- Agent Skills 兼容客户端；
- Python 3.11+；
- `uv`，用于运行 `wechat-draft-uploader` 和测试。

### Codex

使用 Codex 自带的 GitHub Skill 安装器，一次安装四个目录：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo ACBBZ/wechat-fin-article-skills \
  --path fin-article-writer fin-writing-style wechat-cover-generator wechat-draft-uploader
```

安装器默认写入 `${CODEX_HOME:-$HOME/.codex}/skills/`，如果同名目录已经存在会停止，不会静默覆盖。

其他 Agent Skills 客户端可以克隆本仓库，并按各自方式加载上述四个 Skill 目录。

## 微信公众号凭据

真实创建草稿前，在 Skill 目录之外创建配置文件：

```bash
mkdir -p "$HOME/.config/wechat-draft-uploader"
cp wechat-draft-uploader/.env.example "$HOME/.config/wechat-draft-uploader/.env"
chmod 600 "$HOME/.config/wechat-draft-uploader/.env"
```

填写：

```dotenv
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=
WECHAT_TIMEOUT_SECONDS=30
```

不要把真实 `WECHAT_APP_SECRET` 或 access token 提交到 Git、写入 Skill、内容包、命令行参数或日志。如果密钥曾在公开位置暴露，请先在微信公众平台重置。

## 完整流程

```text
选题
 ↓
fin-article-writer
 ├─ 当前事件、历史脉络和反面证据研究
 ├─ 专业分析稿、反向验证与事实核查
 ├─ 锁定 verified_facts / numbers / quotes / uncertainty
 ├─ → fin-writing-style
 │    ├─ 3000–3600 字作者型长文
 │    ├─ 第一人称观察/判断
 │    ├─ 节奏与叙事推进
 │    └─ section_anchors + 四层自检
 ├─ Source-First 正文配图
 │    ├─ 检查所有最终信息来源
 │    ├─ source_capture / source_asset
 │    ├─ source_derived_chart（来源不足时）
 │    └─ ai_fallback（最后兜底）
 ├─ → wechat-cover-generator
 │    └─ GPT-Image2 style_reference → Prompt-as-Code → 封面
 └─ → wechat-draft-uploader
      ├─ dry-run
      └─ 微信公众号草稿箱
```

Writer 最终生成：

```text
output/
├── article.md
├── article-package.json
├── cover.png
├── preview.html
├── draft-result.json
└── images/
    ├── 01-source-evidence.png
    ├── 02-source-data.png
    └── 03-source-context.png
```

如果来源还有第 4、5 张真正有价值的视觉，可以继续加入。已经有 3 张可用来源图时，不会为了数量或画面统一额外生成 AI 正文图。

## Source-First 机器记录

`article-package.json` 会记录来源视觉审计：

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
```

每张正文图还会记录 `origin_kind`：

- `source_capture`：直接从信息来源截图/截取；
- `source_asset`：来源提供的原始图片或图表；
- `source_derived_chart`：根据来源数据制作的可核验图；
- `ai_fallback`：前三类仍不足 3 张时的最后兜底。

## Style Skill 输入边界

完整工作流中，Writer 在事实核查后传递：

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

`author_experience` 为空时，Style Skill 不允许编造“我去过、我买过、我采访过、我和业内朋友聊过”等亲历。

## GPT-Image2 视觉参考

`wechat-cover-generator/references/gpt-image2-style-routing.md` 保存一个轻量的财经视觉路由，参考 `awesome-gpt-image-2` 的模板类别、风格标签、场景标签和 Prompt-as-Code 组织方式。

v3.1 中，GPT-Image2 对**正文图**只用于 `ai_fallback`；对**封面**仍可正常使用。仓库不复制上游完整 `cases.json` 或图片库。

第三方参考与许可说明见 `THIRD_PARTY_NOTICES.md`。

## 草稿上传

先执行 dry-run：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --dry-run \
  --output "/absolute/path/draft-result.json" \
  --preview-html "/absolute/path/preview.html"
```

确认预览后再创建草稿：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --cover "/absolute/path/cover.png" \
  --title "文章标题" \
  --author "作者名" \
  --digest "文章摘要" \
  --env-file "$HOME/.config/wechat-draft-uploader/.env" \
  --output "/absolute/path/draft-result.json" \
  --preview-html "/absolute/path/preview.html"
```

该工具只创建草稿，不群发、不正式发布、不删除已有内容。

## 验证与测试

验证 Skill 结构：

```bash
SKILLS_REF_SOURCE="git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
for skill in fin-article-writer fin-writing-style wechat-cover-generator wechat-draft-uploader; do
  uvx --from "$SKILLS_REF_SOURCE" skills-ref validate "$skill"
done
```

运行 Writer 测试：

```bash
uv run --with pytest pytest -q fin-article-writer/tests
```

运行 Uploader 测试：

```bash
uv run --project wechat-draft-uploader pytest -q wechat-draft-uploader/tests
```

GitHub Actions 会对每次 Pull Request 和主分支推送执行四个 Skill 的结构校验、Writer 测试和 Uploader 测试。
