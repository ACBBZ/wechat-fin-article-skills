from __future__ import annotations

from pathlib import Path

from wechat_draft_uploader.markdown import (
    find_local_images,
    render_markdown,
    replace_image_sources,
)


def test_render_markdown_supports_article_basics_without_raw_html() -> None:
    rendered = render_markdown("# 标题\n\n正文 **加粗**。\n\n[来源](https://example.test)")

    assert "<h1>标题</h1>" in rendered
    assert "<p>正文 <strong>加粗</strong>。</p>" in rendered
    assert '<a href="https://example.test">来源</a>' in rendered


def test_find_local_images_resolves_only_existing_supported_files(tmp_path: Path) -> None:
    article = tmp_path / "article.md"
    image = tmp_path / "images" / "chart.png"
    image.parent.mkdir()
    image.write_bytes(b"png")
    (tmp_path / "images" / "unsupported.svg").write_text("<svg></svg>", encoding="utf-8")
    article.write_text(
        "![chart](images/chart.png) ![remote](https://example.test/chart.png) ![svg](images/unsupported.svg)",
        encoding="utf-8",
    )

    html = render_markdown(article.read_text(encoding="utf-8"))

    assert find_local_images(html, article) == [image.resolve()]


def test_replace_image_sources_preserves_other_html(tmp_path: Path) -> None:
    article = tmp_path / "article.md"
    image = (tmp_path / "chart.png").resolve()
    html = '<p><img src="chart.png" alt="chart"></p><p>正文</p>'

    replaced = replace_image_sources(html, {image: "https://mmbiz.qpic.cn/chart"}, article)

    assert 'src="https://mmbiz.qpic.cn/chart"' in replaced
    assert "<p>正文</p>" in replaced
