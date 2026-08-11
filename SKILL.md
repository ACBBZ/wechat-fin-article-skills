---
name: wechat-draft-uploader
description: 将本地 Markdown 转为微信公众号图文并创建草稿。用户需要预览公众号文章、把 Markdown 上传到公众号草稿箱、处理正文图片，或排查草稿上传失败时使用。
compatibility: 需要 Python 3.11+ 和 uv；实际上传需要能访问 api.weixin.qq.com，并配置微信公众号 WECHAT_APP_ID 与 WECHAT_APP_SECRET。
metadata:
  language: zh-CN
  version: "0.2.0"
---

# 微信公众号草稿上传

## 目标

使用本仓库已有的 Python CLI，把用户明确指定的本地 Markdown 文章预览为微信公众号图文，或上传到微信公众号草稿箱。

本 Skill **只创建草稿**，不得调用群发、发布或删除接口。

## 执行前

1. 先确定本 `SKILL.md` 所在目录，记为 `$SKILL_DIR`。不要假设当前工作目录就是 Skill 目录。
2. 只处理用户明确指定的 Markdown 文件。实际上传还必须有本地封面图片。
3. 凭据从环境变量或环境文件读取：
   - `WECHAT_APP_ID`
   - `WECHAT_APP_SECRET`
   - `WECHAT_AUTHOR`（可选）
   - `WECHAT_TIMEOUT_SECONDS`（可选）
4. 不要在命令参数、日志、回复或代码中回显 `WECHAT_APP_SECRET`、`access_token`。
5. 本地正文图片仅支持 `.jpg`、`.jpeg`、`.png`；远程图片 URL 保持原样。

推荐把凭据放在 `$HOME/.config/wechat-draft-uploader/.env`，不要把真实凭据提交到 Git。

## 工作流

### 1. 先做预览

无论用户最终是否要求上传，实际上传前先运行一次 dry-run：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --dry-run \
  --output "/absolute/path/draft-result.json"
```

读取 `draft-result.json`，确认：

- `status` 为 `dry-run`
- `title` 合理
- `preview_path` 已生成
- `body_image_count` 与文章中的本地 JPEG/PNG 图片数量相符

如果用户只要求预览，到这里结束并报告预览文件路径。

### 2. 创建公众号草稿

实际上传必须提供封面；标题、作者、摘要可按用户要求传入：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/article.md" \
  --cover "/absolute/path/cover.jpg" \
  --title "文章标题" \
  --author "作者名" \
  --digest "文章摘要" \
  --env-file "$HOME/.config/wechat-draft-uploader/.env" \
  --output "/absolute/path/draft-result.json"
```

如果没有显式 `--title`，CLI 会优先使用 Markdown 中第一个一级标题，再退回文件名。`--author` 和 `--digest` 也可以按实际需要省略。

### 3. 报告结果

成功时读取结果文件，并向用户报告：

- 草稿已创建
- `draft_media_id`
- 标题
- 正文图片数量
- 预览文件路径

不要输出凭据或 access token。

## 失败处理

- 缺少 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`：指出缺少配置，不要猜测或生成凭据。
- 缺少封面：说明实际上传需要 `--cover`。
- 微信 API 返回错误：报告脱敏后的错误码和消息，不要盲目重复上传。
- dry-run 失败：先修复本地文件、Markdown 或路径问题，再考虑实际上传。

## 常用检查

查看完整命令行参数：

```bash
uv run --project "$SKILL_DIR" wechat-draft-uploader --help
```

运行测试：

```bash
uv run --project "$SKILL_DIR" pytest -q
```
