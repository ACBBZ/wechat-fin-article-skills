# wechat-draft-uploader

将一篇本地 Markdown 文章转换为微信公众号图文内容，上传到公众号草稿箱。项目只调用 `draft/add`，不执行群发。

## Install

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
cp .env.example .env
```

在 `.env` 中填写公众号凭据。`.env` 已被 Git 忽略，不要把凭据写入命令历史、日志或代码：

```text
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=复利谭谈
WECHAT_TIMEOUT_SECONDS=30
```

## Preview

先用 dry-run 检查 Markdown 转换结果，不需要公众号凭据，也不会发起网络请求：

```bash
uv run wechat-draft-uploader \
  --markdown /path/to/article.md \
  --dry-run \
  --output /path/to/draft-result.json
```

默认会在结果文件旁生成 `preview.html`。Markdown 支持标题、段落、粗体、链接、分隔线和本地 JPEG/PNG 图片。

## Create Draft

上传到草稿箱时，需要明确指定文章标题和封面：

```bash
uv run wechat-draft-uploader \
  --markdown /home/admin/wechat-gongzhonghao-article/runs/2026-08-10/codex-skill-article.md \
  --cover /path/to/cover.jpg \
  --title "今日市场观察" \
  --author "复利谭谈" \
  --digest "今日市场结构与风险偏好观察"
```

流程会按顺序获取 access token、上传封面、上传 Markdown 中引用的本地正文图片、替换图片 URL，然后创建一篇草稿。结果写入 `draft-result.json`，包括 `draft_media_id` 和上传图片数量。

当前支持 `.jpg`、`.jpeg`、`.png` 图片。远程图片 URL 会保留，不会由本工具重复上传；不存在或不支持的本地图片不会被上传。

## Safety

- 只处理命令行明确指定的 Markdown 文件。
- 只创建公众号草稿，不调用群发接口。
- API 错误会脱敏 `secret` 和 `access_token`。
- 测试只使用 fake HTTP 响应，不会访问微信接口。

## Test

```bash
uv run pytest -q
```
