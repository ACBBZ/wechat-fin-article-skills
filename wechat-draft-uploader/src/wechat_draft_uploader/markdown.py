from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Mapping
from urllib.parse import unquote

from markdown_it import MarkdownIt

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_IMAGE_TAG = re.compile(r'<img\b[^>]*\bsrc=(["\'])(.*?)\1[^>]*>', flags=re.IGNORECASE)
_H2_TAG = re.compile(r'<h2>(.*?)</h2>', flags=re.IGNORECASE | re.DOTALL)
_BARE_P_TAG = re.compile(r'<p>(.*?)</p>', flags=re.IGNORECASE | re.DOTALL)
_SOURCE_SECTION = re.compile(
    r'<p><strong>信息来源</strong></p>\s*(.*)\Z',
    flags=re.IGNORECASE | re.DOTALL,
)

_H2_STYLE = (
    "font-size:20px;"
    "font-weight:700;"
    "line-height:1.5;"
    "margin:28px 0 14px;"
)
_BODY_PARAGRAPH_STYLE = "margin:0 0 1em;line-height:1.75;"
_SOURCE_SECTION_STYLE = (
    "margin-top:28px;"
    "padding-top:16px;"
    "border-top:1px solid #e5e5e5;"
)
_SOURCE_TITLE_STYLE = "margin:0 0 10px;font-size:16px;line-height:1.6;"
_SOURCE_TEXT_STYLE = "font-size:14px;line-height:1.75;color:#666;"
_SOURCE_LIST_STYLE = "margin:0;padding-left:1.4em;"
_SOURCE_ITEM_STYLE = "margin:0 0 12px;"


def render_markdown(markdown_text: str) -> str:
    """把 Markdown 渲染成更适合微信公众号草稿的 HTML。

    Writer 使用两个换行符把完整句子拆成独立段落；这里给正文段落增加显式
    段后间距。二级标题使用更大的粗体样式；“信息来源”使用带项目符号且
    条目之间留出明显空隙的列表。来源会去除空项目并自动去重。
    """
    renderer = MarkdownIt(
        "commonmark",
        {"html": False, "linkify": False, "breaks": True},
    )
    rendered = renderer.render(markdown_text)
    rendered = _style_h2_headings(rendered)
    rendered = _style_information_sources(rendered)
    return _style_body_paragraphs(rendered)


def _style_h2_headings(html_text: str) -> str:
    return _H2_TAG.sub(
        lambda match: f'<h2 style="{_H2_STYLE}">{match.group(1)}</h2>',
        html_text,
    )


def _extract_source_items(source_html: str) -> list[str]:
    list_items = re.findall(
        r"<li>(.*?)</li>",
        source_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if list_items:
        candidates = list_items
    else:
        normalized_html = re.sub(r"<br\s*/?>", "\n", source_html, flags=re.IGNORECASE)
        normalized_html = re.sub(r"</p>\s*<p>", "\n", normalized_html, flags=re.IGNORECASE)
        normalized_html = re.sub(r"</?p>", "", normalized_html, flags=re.IGNORECASE)
        candidates = normalized_html.splitlines()

    items: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        plain_text = re.sub(r"<[^>]+>", "", candidate)
        normalized = re.sub(r"\s+", " ", html.unescape(plain_text)).strip()
        normalized = re.sub(r"^[-•·]\s*", "", normalized)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        items.append(normalized)
    return items


def _style_information_sources(html_text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        items = _extract_source_items(match.group(1))
        item_html = "\n".join(
            f'<li data-source-item="true" style="{_SOURCE_ITEM_STYLE}">{html.escape(item)}</li>'
            for item in items
        )
        return (
            f'<section data-section="information-sources" style="{_SOURCE_SECTION_STYLE}">\n'
            f'<p style="{_SOURCE_TITLE_STYLE}"><strong style="font-weight:700;">信息来源</strong></p>\n'
            f'<ul data-source-list="true" style="{_SOURCE_TEXT_STYLE}{_SOURCE_LIST_STYLE}">\n{item_html}\n</ul>\n'
            "</section>\n"
        )

    return _SOURCE_SECTION.sub(replace, html_text)


def _style_body_paragraphs(html_text: str) -> str:
    return _BARE_P_TAG.sub(
        lambda match: (
            f'<p data-role="body-paragraph" style="{_BODY_PARAGRAPH_STYLE}">'
            f'{match.group(1)}</p>'
        ),
        html_text,
    )


def find_local_images(html_text: str, markdown_path: Path) -> list[Path]:
    found: list[Path] = []
    for match in _IMAGE_TAG.finditer(html_text):
        path = _resolve_image_path(match.group(2), markdown_path)
        if path is None or path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES or not path.is_file():
            continue
        if path not in found:
            found.append(path)
    return found


def replace_image_sources(html_text: str, replacements: Mapping[Path, str], markdown_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        path = _resolve_image_path(match.group(2), markdown_path)
        url = replacements.get(path) if path is not None else None
        if not url:
            return match.group(0)
        start, end = match.span(2)
        return html_text[match.start():start] + html.escape(url, quote=True) + html_text[end:match.end()]

    return _IMAGE_TAG.sub(replace, html_text)


def _resolve_image_path(source: str, markdown_path: Path) -> Path | None:
    source = unquote(source.strip())
    if not source or source.startswith(("http://", "https://", "data:", "#")):
        return None
    path = Path(source)
    if not path.is_absolute():
        path = markdown_path.parent / path
    return path.resolve()
