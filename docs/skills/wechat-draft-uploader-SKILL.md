---
name: wechat-draft-uploader
description: 当需要把本地 Markdown 预览为微信公众号图文、上传到公众号草稿箱、处理正文图片或排查草稿上传失败时使用。
compatibility: 需要 Python 3.11+ 和 uv；真实上传需要能访问 api.weixin.qq.com，并通过外部环境配置 WECHAT_APP_ID 与 WECHAT_APP_SECRET。
metadata:
  language: zh-CN
  version: "0.5.0"
---

# 微信公众号草稿上传

## 目标

把用户明确指定的本地 Markdown 转换为微信公众号图文内容，并创建草稿。**只创建草稿，不执行群发、正式发布或删除。**

本集成版基于 `ACBBZ/wechat-draft-uploader` v0.2.0，并针对 `fin-article-writer` 的 `article.md + cover.png + images/*.png` 输出增加公众号排版增强：正文双换行形成带段间距的独立段落、`##` 小标题 20px 加粗、信息来源区使用项目符号，并在条目之间保留明显空隙。

## 执行前

1. 确定本 `SKILL.md` 所在目录，记为 `$SKILL_DIR`。
2. 只处理用户或上游 Writer 明确指定的 Markdown 文件。
3. 真实上传必须有本地封面；本集成流程使用 `cover.png`。
4. 凭据只从环境变量或外部环境文件读取：`WECHAT_APP_ID`、`WECHAT_APP_SECRET`、`WECHAT_AUTHOR`（可选）、`WECHAT_TIMEOUT_SECONDS`（可选）。
5. 不得在命令参数、日志、回复、源码、Skill、ZIP 或内容包中回显 `WECHAT_APP_SECRET` 或 `access_token`。
6. 本地正文图片支持 `.jpg`、`.jpeg`、`.png`；与 `fin-article-writer` 联动时正文图片统一为 `.png`。
7. Markdown 转 HTML 时，正文两个换行符形成独立段落，并为正文段落设置明显段后间距；所有 `##` 二级标题使用 20px 字号、700 字重；“信息来源”固定区使用 14px 项目列表样式，每条保留项目符号，并在条目之间留出空隙。

推荐配置文件：

```text
$HOME/.config/wechat-draft-uploader/.env
```

## 1. 先做 dry-run

真实上传前必须先执行：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --dry-run \
  --output "/absolute/path/draft-result.json" \
  --preview-html "/absolute/path/preview.html"
```

读取结果并确认：`status` 为 `dry-run`、标题合理、预览文件存在、正文图片数量符合预期。dry-run 失败时停止，不进行真实上传。

## 2. 创建公众号草稿

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

CLI 会依次获取 access token、上传封面、上传 Markdown 中的本地正文图片、替换图片 URL，然后调用草稿接口。成功结果包含 `draft_media_id`。

## 3. 凭据配置

把 `.env.example` 复制到 Skill 目录之外：

```bash
mkdir -p "$HOME/.config/wechat-draft-uploader"
cp "$SKILL_DIR/.env.example" "$HOME/.config/wechat-draft-uploader/.env"
chmod 600 "$HOME/.config/wechat-draft-uploader/.env"
```

再在该文件中填写真实凭据。不要修改 `.env.example` 为真实值。

## 失败处理

- 缺少 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`：停止真实上传并报告缺少外部配置；
- 缺少封面：真实上传不执行；
- 微信 API 返回错误：只报告脱敏后的错误码和消息，不盲目重复提交；
- dry-run 失败：先修复 Markdown、本地图片或路径；
- 上游已经生成的文章、图片和封面不得因为上传失败而删除。

## 常用检查

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader --help
uv run --project "$SKILL_DIR" pytest -q
```
