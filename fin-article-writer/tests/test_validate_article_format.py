from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_article_format.py'
TARGET_BODY_LENGTH = 3200


def run_validator(article: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(article)],
        text=True,
        capture_output=True,
    )


def body_with_length(length: int, prefix: str = '') -> str:
    if len(prefix) > length:
        raise ValueError('prefix longer than requested body length')
    return prefix + ('测' * (length - len(prefix)))


def valid_sources() -> str:
    return (
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n\n'
        '- 财联社：《报道B》，2026年8月12日。\n'
    )


def test_validator_accepts_3000_to_3600_visible_chars_without_h2(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '第一句话。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        '![图](images/a.png)\n\n'
        '*图：示意图，来源：本账号绘制。*\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_accepts_optional_h2_headings(tmp_path: Path):
    article = tmp_path / 'article.md'
    first = body_with_length(1600, '第一句话。\n\n')
    second = body_with_length(1600, '第二句话。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{first}\n\n'
        '## 可选的小标题\n\n'
        f'{second}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_rejects_body_shorter_than_3000_visible_chars(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n'
        f'{body_with_length(2999)}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '正文可见字数不足' in (result.stdout + result.stderr)


def test_validator_rejects_body_longer_than_3600_visible_chars(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n'
        f'{body_with_length(3601)}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '正文可见字数超限' in (result.stdout + result.stderr)


def test_validator_rejects_two_complete_sentences_in_one_paragraph(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '第一句话。第二句话。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '一句一段' in (result.stdout + result.stderr)


def test_validator_rejects_empty_or_messy_source_items(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '一句。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        '**信息来源**\n\n- \n- 新华社 报道A 2026-08-12\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert '信息来源' in output


def test_validator_requires_blank_line_after_each_body_sentence(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH - len('第一句话。\n第二句话。\n\n'))
    article.write_text(
        '# 标题\n\n'
        '第一句话。\n'
        '第二句话。\n\n'
        f'{body}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '两个换行' in (result.stdout + result.stderr)


def test_validator_rejects_plain_source_lines_without_bullets(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '第一句话。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        '---\n\n'
        '**信息来源**\n\n'
        '新华社：《报道A》，2026年8月12日。\n\n'
        '财联社：《报道B》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '项目符号' in (result.stdout + result.stderr)


def test_validator_accepts_source_bullets_with_blank_lines(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '一句。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        f'{valid_sources()}',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_rejects_adjacent_source_bullets_without_blank_line(tmp_path: Path):
    article = tmp_path / 'article.md'
    body = body_with_length(TARGET_BODY_LENGTH, '一句。\n\n')
    article.write_text(
        '# 标题\n\n'
        f'{body}\n\n'
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n'
        '- 财联社：《报道B》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '缺少空行' in (result.stdout + result.stderr)
