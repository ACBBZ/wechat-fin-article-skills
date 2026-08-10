# WeChat Draft Uploader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a public standalone CLI that converts a local Markdown article into WeChat-compatible HTML, uploads the cover and local body images, and creates a WeChat draft without sending it.

**Architecture:** Keep the project independent from the article generator. A Markdown renderer produces safe article HTML; an asset layer resolves local images and replaces them with URLs returned by WeChat; a small API client handles token, thumbnail, body-image, and draft endpoints. The CLI orchestrates these layers, supports dry-run preview, and writes only redacted result metadata.

**Tech Stack:** Python 3.11+, `markdown-it-py`, `urllib.request`, `argparse`, `pytest`, `uv`.

## Global Constraints

- The public repository must contain no app secret, access token, API key, cookie, or private article note.
- The only publishing action is `draft/add`; never call a mass-send endpoint.
- Markdown input is explicit; do not scan or upload unrelated files.
- Local body images are limited to JPEG and PNG and must be resolved relative to the Markdown file unless explicitly absolute.
- API errors must redact `secret`, `access_token`, and configured credentials.
- Tests must use fake HTTP responses and must not call WeChat.

### Task 1: Markdown Rendering and Asset Resolution

**Files:**
- Create: `src/wechat_draft_uploader/markdown.py`
- Test: `tests/test_markdown.py`

**Interfaces:**
- `render_markdown(markdown_text: str) -> str`
- `find_local_images(html: str, markdown_path: Path) -> list[Path]`
- `replace_image_sources(html: str, replacements: dict[Path, str], markdown_path: Path) -> str`

- [ ] Write failing tests for headings/paragraphs, local image discovery, and source replacement.
- [ ] Run `uv run pytest tests/test_markdown.py -q` and observe the expected missing-module failure.
- [ ] Implement the minimum safe Markdown renderer and image replacement helpers.
- [ ] Run the focused tests and confirm they pass.

### Task 2: WeChat API Client

**Files:**
- Create: `src/wechat_draft_uploader/wechat.py`
- Test: `tests/test_wechat.py`

**Interfaces:**
- `WeChatClient.create_draft(title, author, digest, html, cover_path, body_images) -> dict[str, Any]`
- `WeChatConfig(app_id: str, app_secret: str)`

- [ ] Write failing tests for token retrieval, cover upload, body-image upload, draft creation, and secret redaction.
- [ ] Run the focused tests and observe failure before implementation.
- [ ] Implement the four required API calls with injectable HTTP opener.
- [ ] Run the focused tests and confirm fake API flow passes.

### Task 3: CLI and Configuration

**Files:**
- Create: `src/wechat_draft_uploader/cli.py`
- Create: `src/wechat_draft_uploader/__init__.py`
- Create: `tests/test_cli.py`
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

**Interfaces:**
- CLI: `uv run wechat-draft-uploader --markdown article.md --cover cover.jpg --title "标题"`
- Preview: add `--dry-run` to render HTML and skip all HTTP calls.
- Output: `draft-result.json` with status, paths, image count, and redacted error only.

- [ ] Write failing tests for argument validation, dry-run output, and secret-free metadata.
- [ ] Implement the CLI and environment-file loading.
- [ ] Run all tests and then a local dry-run against the generated article.

### Task 4: Public GitHub Repository

**Files:**
- Git repository: `/home/admin/wechat-draft-uploader`

- [ ] Run the full test suite and `git diff --check`.
- [ ] Initialize Git, commit only project files, and verify no secrets are tracked.
- [ ] Create public repository `ACBBZ/wechat-draft-uploader`.
- [ ] Push `main` and verify the remote repository URL.
