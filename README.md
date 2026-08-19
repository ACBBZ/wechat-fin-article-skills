# wechat-fin-arcticle-skill

一套面向中文财经微信公众号的三 Skill 工作流，从选题研究、文章写作、历史脉络、标题包装、正文配图、封面生成，一直到微信公众号草稿箱上传。

> 项目内部名称：`wechat-fin-arcticle-skill`  
> 当前套件版本：`2.5.0`

## 包含的 Skill

### 1. `fin-article-writer` v2.5.0

财经公众号文章编排器。

主要能力：

- 当前事件研究与事实核查；
- 强制研究直接前史、历史异常案例、同机制案例和历史监管响应；
- 专业财经媒体式分析逻辑；
- 面向普通读者的自然中文表达；
- 8–12 个标题候选自动筛选，输出 1 个主标题 + 3 个备选；
- 正文至少生成 2 张 `.png` 配图，分别放在两个 `##` 小标题之前；
- 调用 `wechat-cover-generator` 生成封面；
- 调用 `wechat-draft-uploader` 创建微信公众号草稿；
- 最终输出 `article.md`、`article-package.json`、正文图片、封面、预览和草稿结果。

### 2. `wechat-cover-generator` v1.1.0

微信公众号财经封面生成 Skill。

支持两种视觉模式：

- `general`：通用财经、政策、产业、公司深度；
- `emotion_meme`：强情绪财经 meme，强调单主体、夸张动作/表情、财经隐喻和小图识别度。

封面默认兼顾横版与中央方形安全裁切，输出 `cover.png`；没有生图能力时自动退化为完整 Prompt。

### 3. `wechat-draft-uploader` v0.5.0

把本地 Markdown 文章转换成微信公众号图文并创建草稿。

主要能力：

- 实际上传前强制 dry-run；
- 上传 `cover.png`；
- 上传 Markdown 引用的本地 PNG/JPEG 正文图片；
- 将本地图片地址替换成微信返回的图片 URL；
- `##` 小标题渲染为 20px、700 字重；
- 正文“一句一段”，每个句子之间保留明显段间距；
- 信息来源保留 `- ` 项目符号，并在来源条目之间留空隙；
- 只调用微信公众号草稿接口，不群发、不正式发布、不删除。

## 安装

需要：

- Python 3.11+
- `uv`
- Agent Skills 兼容客户端

克隆仓库后运行：

```bash
git clone https://github.com/ACBBZ/wechat-draft-uploader.git
cd wechat-draft-uploader
bash install.sh
```

默认安装到：

```text
$HOME/.agents/skills/
├── fin-article-writer/
├── wechat-cover-generator/
└── wechat-draft-uploader/
```

自定义安装目录：

```bash
SKILLS_DIR=/your/skills/path bash install.sh
```

## 微信公众号凭据

安装脚本会在 Skill 目录之外创建：

```text
$HOME/.config/wechat-draft-uploader/.env
```

填写：

```dotenv
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=
WECHAT_TIMEOUT_SECONDS=30
```

**不要把真实 `WECHAT_APP_SECRET` 提交到 Git、写入 Skill、ZIP、`article-package.json`、命令行参数或日志。**

如果此前密钥曾经在公开位置或聊天中明文暴露，请先在微信公众平台重置，再把新密钥写入本地 `.env`。

## 完整流程

```text
选题
 ↓
fin-article-writer
 ├─ Step 0  选题审视
 ├─ Step 1  当前事件 + 历史脉络 + 反面证据
 ├─ Step 2  专业初稿
 ├─ Step 3  反向验证
 ├─ Step 4  修正
 ├─ Step 5  事实真实性核查
 ├─ Step 6  易读表达优化
 ├─ Step 7  标题包装
 ├─ Step 8  至少两张正文 PNG 配图
 ├─ Step 9  → wechat-cover-generator
 ├─ Step 10 跨资产一致性 + 打包
 └─ Step 11 → wechat-draft-uploader
               ├─ dry-run
               └─ 微信公众号草稿箱
```

## 文章排版规范

正文每个完整句子单独成段，句子之间保留一个空白行：

```markdown
第一句话。

第二句话。

第三句话。

## 小标题

第四句话。
```

文末来源严格使用下面的格式：

```markdown
---

**信息来源**

- Axios：《OpenAI to rewrite its safety rules post-Hugging Face》，2026年8月18日。

- Bloomberg Law：《OpenAI Pauses Some Work on New Astra Model on Cyber Concerns》，2026年8月7日。

- OpenAI：《OpenAI and Hugging Face partner to address security incident during model evaluation》，2026年7月21日。
```

规则：

- 每条来源必须以 `- ` 开头；
- 两条来源之间保留一个空白行；
- 统一使用 `机构：《标题》，日期。`；
- 没有具体日期时按真实资料写“2025年报告”等，不编造日期；
- 删除空项目和完全重复来源；
- URL 和来源等级写入 `article-package.json`，不塞进正文来源区。

## 正文图片规则

每篇文章至少 2 张正文图片，统一使用 `.png`：

```text
output/images/
├── 01-before-subtitle-1.png
└── 02-before-subtitle-2.png
```

第一张紧邻第一个 `##` 小标题之前，第二张紧邻第二个 `##` 小标题之前。

优先使用官方原始资料、可确认使用条件的新闻资料和基于已核实数据生成的原创图；版权状态不明确的媒体图片只作为候选，不自动进入发布稿。

## 草稿上传

`fin-article-writer` 在 Step 10 格式校验通过后调用 `wechat-draft-uploader`。

Uploader 会先执行：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --dry-run \
  --output "/absolute/path/draft-result.json" \
  --preview-html "/absolute/path/preview.html"
```

真实创建草稿时需要封面和外部凭据：

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

成功后 `draft-result.json` 会包含 `draft_media_id`，Writer 同时把状态写回 `article-package.json.wechat_draft`。

## 安全边界

- 不保存真实 AppSecret 或 access token；
- 不把未经核实的传言写成事实；
- 不把历史类比写成确定因果；
- 不把版权不明图片自动用于发布；
- 不提供具体买卖建议、收益承诺或内幕暗示；
- 微信模块只创建草稿，不执行群发或正式发布。

## 测试

Writer 格式校验测试：

```bash
cd fin-article-writer
python -m pytest -q
```

Uploader 测试：

```bash
cd wechat-draft-uploader
uv run pytest -q
```

## GitHub 仓库结构

当前 GitHub 仓库 slug 仍为 `ACBBZ/wechat-draft-uploader`，项目内容名称已经统一为 `wechat-fin-arcticle-skill`。完整三 Skill 源码和安装文件打包在 `wechat-fin-arcticle-skill-v2.5.zip` 中；三个核心 `SKILL.md` 也放在 `docs/skills/` 方便在线阅读。

```text
repository/
├── README.md
├── install.sh
├── manifest.json
├── wechat-fin-arcticle-skill-v2.5.zip
└── docs/skills/
    ├── fin-article-writer-SKILL.md
    ├── wechat-cover-generator-SKILL.md
    └── wechat-draft-uploader-SKILL.md
```

运行 `bash install.sh` 后，ZIP 会解压并把三个完整 Skill 安装到 `$HOME/.agents/skills/`。
