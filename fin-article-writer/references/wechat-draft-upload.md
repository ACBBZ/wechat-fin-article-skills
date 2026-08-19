# 第 11 步：微信公众号草稿上传

这一阶段只负责把第 10 步已经通过一致性检查的内容包创建为**微信公众号草稿**。它不修改文章观点，不重新生成正文图片，也不执行群发、正式发布或删除。

## 目录

- 调用边界
- 凭据配置
- 必须先执行 dry-run
- 创建草稿
- 结果写回
- 失败隔离

## 调用边界

**必须调用子 Skill：** `wechat-draft-uploader`。

输入固定来自最终内容包：

- `output/article.md`
- `output/cover.png`（只有封面状态为 `generated` 时存在）
- `output/images/*.png`，其中至少包含两个固定正文配图
- 主标题
- 作者（可选）
- 摘要 `digest`（可选，必须与正文事实一致）

## 凭据配置

公众号凭据只能从运行环境读取，推荐文件：

```text
$HOME/.config/wechat-draft-uploader/.env
```

内容模板：

```dotenv
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=
WECHAT_TIMEOUT_SECONDS=30
```

真实 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` **不得**写入：

- `fin-article-writer` 或其他 Skill 的 `SKILL.md`；
- Skill 源码或版本元数据；
- `article-package.json`；
- 仓库中的示例配置；
- 命令行参数；
- 日志、审核报告或最终回复。

配置文件建议权限为 `600`。如果平台支持 Secrets / Secret Manager，优先用环境变量注入。

## 必须先执行 dry-run

真实上传前先执行：

```bash
uv run --project "$WECHAT_UPLOADER_SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/output/article.md" \
  --dry-run \
  --output "/absolute/path/output/draft-result.json" \
  --preview-html "/absolute/path/output/preview.html"
```

读取 `draft-result.json`，至少确认：

- `status == "dry-run"`；
- 标题合理；
- `preview.html` 已生成；
- `body_image_count >= 2`；
- 正文引用的两个固定 PNG 配图都被识别；
- Markdown 中没有不存在的本地图片路径。

只要 dry-run 失败，立即停止第 11 步，不得盲目重试真实上传。

## 创建草稿

仅在以下条件同时成立时继续：

1. dry-run 通过；
2. `cover.status == generated` 且 `output/cover.png` 存在；
3. 外部环境中存在 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`；
4. 用户没有显式设置 `wechat_draft.enabled=false`。

执行：

```bash
uv run --project "$WECHAT_UPLOADER_SKILL_DIR" wechat-draft-uploader \
  --markdown "/absolute/path/output/article.md" \
  --cover "/absolute/path/output/cover.png" \
  --title "最终主标题" \
  --author "作者名" \
  --digest "与正文一致的简短摘要" \
  --env-file "$HOME/.config/wechat-draft-uploader/.env" \
  --output "/absolute/path/output/draft-result.json" \
  --preview-html "/absolute/path/output/preview.html"
```

Uploader 会上传封面、上传 Markdown 中的本地正文图片、替换正文图片地址，然后调用微信草稿接口创建草稿。

转换 HTML 时必须把 Writer 的两个换行符保留为独立正文段落，并给每个正文段落增加明确段后间距；所有 `##` 小标题渲染为 20px、700 字重的加粗标题；固定的“信息来源”区域使用统一的紧凑样式，每条来源直接换行，不显示项目符号。

## 结果写回

成功后写入：

```yaml
wechat_draft:
  enabled: true
  status: created
  draft_media_id: "..."
  result_path: draft-result.json
  preview_path: preview.html
  body_image_count: 2
```

其他允许状态：

- `disabled`：用户显式关闭自动草稿；
- `dry_run`：只完成预览，没有进行真实上传；
- `skipped_no_cover`：封面没有成功生成；
- `skipped_no_credentials`：外部凭据未配置；
- `failed`：API、网络、图片上传或草稿创建失败。

失败时只保存**脱敏错误**。`access_token`、`AppSecret` 永远不进入 `article-package.json`。

## 失败隔离

第 11 步失败不能回滚第 0–10 步的产物。`article.md`、正文 PNG、`cover.png` 和 `article-package.json` 仍然保留。不要因为上传失败而重新改标题、改正文或重生成图片。
