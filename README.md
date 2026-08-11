# wechat-draft-uploader

一个中文 Agent Skill：把本地 Markdown 文章转换成微信公众号图文内容，并上传到公众号草稿箱。

底层仍使用本仓库的 Python CLI，只调用微信公众号 `draft/add` 草稿接口，不执行群发或发布。

## 作为 Skill 安装

Agent Skills 兼容客户端可以把这个仓库直接作为一个 Skill 目录使用，因为仓库根目录包含 `SKILL.md`。

用户级安装：

```bash
git clone https://github.com/ACBBZ/wechat-draft-uploader.git \
  ~/.agents/skills/wechat-draft-uploader

uv sync --project ~/.agents/skills/wechat-draft-uploader
```

项目级安装：

```bash
git clone https://github.com/ACBBZ/wechat-draft-uploader.git \
  .agents/skills/wechat-draft-uploader

uv sync --project .agents/skills/wechat-draft-uploader
```

安装后，Agent 可以在这些场景触发本 Skill：

- “把这篇 Markdown 预览成公众号图文。”
- “把 `/path/article.md` 上传到公众号草稿箱，封面是 `/path/cover.jpg`。”
- “检查这篇公众号 Markdown 的本地图片并创建草稿。”
- “帮我排查微信公众号草稿上传失败。”

## 配置公众号凭据

需要 Python 3.11+ 和 `uv`。

建议把凭据放在仓库之外，例如：

```bash
mkdir -p ~/.config/wechat-draft-uploader
cp .env.example ~/.config/wechat-draft-uploader/.env
```

编辑：

```text
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=复利谭谈
WECHAT_TIMEOUT_SECONDS=30
```

不要把真实凭据提交到 Git，也不要把 `WECHAT_APP_SECRET` 放进命令历史或日志。

## 手动预览

dry-run 不需要公众号凭据，也不会访问微信接口：

```bash
uv run --project . wechat-draft-uploader \
  --markdown /path/to/article.md \
  --dry-run \
  --output /path/to/draft-result.json
```

默认会在结果文件旁生成 `preview.html`。

## 手动创建草稿

实际上传必须提供封面：

```bash
uv run --project . wechat-draft-uploader \
  --markdown /path/to/article.md \
  --cover /path/to/cover.jpg \
  --title "今日市场观察" \
  --author "复利谭谈" \
  --digest "今日市场结构与风险偏好观察" \
  --env-file ~/.config/wechat-draft-uploader/.env
```

标题可以省略：CLI 会优先使用 Markdown 中第一个一级标题，再退回文件名。

上传流程会依次获取 access token、上传封面、上传 Markdown 中引用的本地正文图片、替换正文图片 URL，然后创建一篇草稿。结果写入 `draft-result.json`，包含 `draft_media_id` 等信息。

## Markdown 和图片支持

当前支持：

- 标题
- 段落
- 粗体
- 链接
- 分隔线
- 本地 JPEG/PNG 图片

远程图片 URL 会保留，不会重复上传；不存在或不支持的本地图片不会上传。

## 安全边界

- 只处理命令行明确指定的 Markdown 文件。
- 只创建公众号草稿，不调用群发或发布接口。
- API 错误会脱敏 `secret` 和 `access_token`。
- 测试使用 fake HTTP 响应，不会访问微信接口。
- 建议实际上传前始终先做一次 dry-run。

## 测试

```bash
uv run pytest -q
```
