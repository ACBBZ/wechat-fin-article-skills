# wechat-fin-article-skills

面向中文财经微信公众号的三 Skill 工作流，覆盖选题研究、文章写作、事实核查、标题包装、正文配图、封面生成和微信公众号草稿创建。

当前套件版本：`2.5.0`

## 包含的 Skill

| Skill | 版本 | 用途 |
| --- | --- | --- |
| `fin-article-writer` | 2.5.0 | 研究并编排财经公众号文章，生成正文、标题、图片和内容包 |
| `wechat-cover-generator` | 1.1.0 | 根据文章语义生成公众号财经封面或完整生图提示词 |
| `wechat-draft-uploader` | 0.5.0 | 预览本地 Markdown，并安全创建微信公众号图文草稿 |

三个 Skill 可以独立安装和触发。`fin-article-writer` 在完整工作流中会调用另外两个 Skill。

## 仓库结构

```text
wechat-fin-article-skills/
├── README.md
├── fin-article-writer/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/
│   ├── references/
│   └── tests/
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
- `uv`，用于运行 `wechat-draft-uploader`。

### Codex

使用 Codex 自带的 GitHub Skill 安装器，一次安装三个目录：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo ACBBZ/wechat-fin-article-skills \
  --path fin-article-writer wechat-cover-generator wechat-draft-uploader
```

安装器默认写入 `${CODEX_HOME:-$HOME/.codex}/skills/`，如果同名目录已经存在会停止，不会静默覆盖。

其他 Agent Skills 客户端可以克隆本仓库，并按各自的安装方式加载上述三个 Skill 目录。

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
 ├─ 初稿、反向验证与事实核查
 ├─ 易读表达、标题包装和正文配图
 ├─ → wechat-cover-generator
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
    ├── 01-before-subtitle-1.png
    └── 02-before-subtitle-2.png
```

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
for skill in fin-article-writer wechat-cover-generator wechat-draft-uploader; do
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

GitHub Actions 会对每次推送和 Pull Request 自动执行以上结构校验与测试。
