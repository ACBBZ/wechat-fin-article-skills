from __future__ import annotations

import re
import sys
from pathlib import Path

SENTENCE_END = re.compile(r"[。！？!?]")
SOURCE_LINE = re.compile(r"^[^：\n]+：《[^》\n]+》，.+。$")
VISIBLE_BODY_MIN = 3000
VISIBLE_BODY_MAX = 3600
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^\)]+\)")
MARKDOWN_DECORATION = re.compile(r"[*_~`>]")


def _paragraphs(lines: list[str], end: int) -> list[tuple[int, str]]:
    paragraphs: list[tuple[int, str]] = []
    buffer: list[str] = []
    start_line = 1

    def flush() -> None:
        nonlocal buffer, start_line
        if buffer:
            paragraphs.append((start_line, "\n".join(buffer).strip()))
            buffer = []

    for idx, raw in enumerate(lines[:end], start=1):
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if not buffer:
            start_line = idx
        buffer.append(line)
    flush()
    return paragraphs


def _is_body_content_line(stripped: str) -> bool:
    return bool(stripped) and not stripped.startswith(("#", "![", "*图：", ">", "---"))


def _visible_body_char_count(lines: list[str], end: int) -> int:
    visible_lines: list[str] = []
    for raw in lines[:end]:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "![", "*图：", "---")):
            continue
        text = stripped.lstrip("> ")
        text = MARKDOWN_LINK.sub(r"\1", text)
        text = MARKDOWN_DECORATION.sub("", text)
        visible_lines.append(text)
    return len(re.sub(r"\s+", "", "".join(visible_lines)))


def validate_article(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    source_indexes = [idx for idx, line in enumerate(lines) if line.strip() == "**信息来源**"]
    source_index = source_indexes[-1] if source_indexes else len(lines)
    if not source_indexes:
        errors.append("信息来源缺失：文末必须包含 `**信息来源**`。")

    visible_body_chars = _visible_body_char_count(lines, source_index)
    if visible_body_chars < VISIBLE_BODY_MIN:
        errors.append(
            f"正文可见字数不足：需要 {VISIBLE_BODY_MIN}–{VISIBLE_BODY_MAX} 字，当前为 {visible_body_chars} 字。"
        )
    elif visible_body_chars > VISIBLE_BODY_MAX:
        errors.append(
            f"正文可见字数超限：需要 {VISIBLE_BODY_MIN}–{VISIBLE_BODY_MAX} 字，当前为 {visible_body_chars} 字。"
        )

    # 硬约束：正文完整句子后必须是一个空白行，也就是 Markdown 中至少两个换行符。
    for idx, raw in enumerate(lines[:source_index]):
        stripped = raw.strip()
        if not _is_body_content_line(stripped):
            continue
        if not SENTENCE_END.search(stripped):
            continue
        if idx + 1 < source_index and lines[idx + 1].strip():
            preview = re.sub(r"\s+", " ", stripped)[:80]
            errors.append(
                f"第 {idx + 1} 行句末后缺少空行：每个完整句子后必须使用两个换行符再写下一段：{preview}"
            )

    for line_no, paragraph in _paragraphs(lines, source_index):
        stripped = paragraph.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "![", "*图：", ">", "---")):
            continue
        sentence_count = len(SENTENCE_END.findall(stripped))
        if sentence_count > 1:
            preview = re.sub(r"\s+", " ", stripped)[:80]
            errors.append(
                f"第 {line_no} 行不符合一句一段：同一正文段落检测到 {sentence_count} 个完整句末标点；句子之间必须用两个换行符分隔：{preview}"
            )

    if source_indexes:
        source_lines = lines[source_index + 1 :]
        seen: set[str] = set()
        source_count = 0
        last_source_line_no: int | None = None
        for offset, raw in enumerate(source_lines, start=source_index + 2):
            stripped = raw.strip()
            if not stripped or stripped == "---":
                continue
            if not stripped.startswith("- "):
                errors.append(
                    f"信息来源第 {offset} 行必须使用 `- ` 项目符号：{stripped}"
                )
                continue
            source_text = stripped[2:].strip()
            if not source_text:
                errors.append(f"信息来源第 {offset} 行为空，请删除空项目。")
                continue
            source_count += 1
            if not SOURCE_LINE.match(source_text):
                errors.append(
                    f"信息来源第 {offset} 行格式不统一，应使用 `- 机构：《标题》，YYYY年M月D日。`：{stripped}"
                )
            if last_source_line_no is not None and offset - last_source_line_no < 2:
                errors.append(
                    f"信息来源第 {offset} 行与上一条之间缺少空行；每条来源之间必须保留一个空白行。"
                )
            normalized = re.sub(r"\s+", " ", source_text)
            if normalized in seen:
                errors.append(f"信息来源第 {offset} 行与前文重复，请去重：{stripped}")
            seen.add(normalized)
            last_source_line_no = offset
        if source_count == 0:
            errors.append("信息来源为空：至少列出 1 条实际使用的来源。")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    if len(args) != 1:
        print("用法：python validate_article_format.py /absolute/path/article.md", file=sys.stderr)
        return 2

    path = Path(args[0])
    if not path.is_file():
        print(f"文章文件不存在：{path}", file=sys.stderr)
        return 2

    errors = validate_article(path)
    if errors:
        print("公众号文章格式校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("公众号文章格式校验通过：正文 3000–3600 可见字、每句后两个换行、信息来源格式统一。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
