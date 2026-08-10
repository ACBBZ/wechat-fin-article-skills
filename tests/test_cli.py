from __future__ import annotations

import json
from pathlib import Path

from wechat_draft_uploader.cli import main


def test_dry_run_renders_markdown_without_wechat_request(tmp_path: Path) -> None:
    markdown_path = tmp_path / "article.md"
    output_path = tmp_path / "draft-result.json"
    markdown_path.write_text("# 测试标题\n\n正文 **加粗**。", encoding="utf-8")

    exit_code = main(
        [
            "--markdown",
            str(markdown_path),
            "--dry-run",
            "--output",
            str(output_path),
        ]
    )

    result = json.loads(output_path.read_text(encoding="utf-8"))
    preview = Path(result["preview_path"]).read_text(encoding="utf-8")
    assert exit_code == 0
    assert result["status"] == "dry-run"
    assert result["title"] == "测试标题"
    assert "<strong>加粗</strong>" in preview
    assert result["body_image_count"] == 0


def test_real_run_requires_wechat_credentials(tmp_path: Path) -> None:
    markdown_path = tmp_path / "article.md"
    cover_path = tmp_path / "cover.jpg"
    output_path = tmp_path / "draft-result.json"
    markdown_path.write_text("# 测试标题\n\n正文。", encoding="utf-8")
    cover_path.write_bytes(b"cover")

    exit_code = main(
        [
            "--markdown",
            str(markdown_path),
            "--cover",
            str(cover_path),
            "--output",
            str(output_path),
            "--env-file",
            str(tmp_path / "missing.env"),
        ]
    )

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert result["status"] == "failed"
    assert "WECHAT_APP_ID" in result["error"]
