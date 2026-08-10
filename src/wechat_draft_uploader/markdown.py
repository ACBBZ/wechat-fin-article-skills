from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Mapping
from urllib.parse import unquote

from markdown_it import MarkdownIt


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_IMAGE_TAG = re.compile(r'<img\b[^>]*\bsrc=(["\'])(.*?)\1[^>]*>', flags=re.IGNORECASE)


def render_markdown(markdown_text: str) -> str:
    return MarkdownIt("commonmark", {"html": False, "linkify": False}).render(markdown_text)


def find_local_images(html_text: str, markdown_path: Path) -> list[Path]:
    found: list[Path] = []
    for match in _IMAGE_TAG.finditer(html_text):
        path = _resolve_image_path(match.group(2), markdown_path)
        if path is None or path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES or not path.is_file():
            continue
        if path not in found:
            found.append(path)
    return found


def replace_image_sources(
    html_text: str,
    replacements: Mapping[Path, str],
    markdown_path: Path,
) -> str:
    def replace(match: re.Match[str]) -> str:
        path = _resolve_image_path(match.group(2), markdown_path)
        url = replacements.get(path) if path is not None else None
        if not url:
            return match.group(0)
        start, end = match.span(2)
        return html_text[match.start() : start] + html.escape(url, quote=True) + html_text[end : match.end()]

    return _IMAGE_TAG.sub(replace, html_text)


def _resolve_image_path(source: str, markdown_path: Path) -> Path | None:
    source = unquote(source.strip())
    if not source or source.startswith(("http://", "https://", "data:", "#")):
        return None
    path = Path(source)
    if not path.is_absolute():
        path = markdown_path.parent / path
    return path.resolve()
