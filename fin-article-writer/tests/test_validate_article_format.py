from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_article_format.py'


def run_validator(article: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(article)],
        text=True,
        capture_output=True,
    )


def test_validator_accepts_one_sentence_per_paragraph_and_clean_sources(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n'
        '第一句话。\n\n'
        '![图](images/a.png)\n\n'
        '## 小标题一\n\n'
        '第二句话。\n\n'
        '![图](images/b.png)\n\n'
        '## 小标题二\n\n'
        '第三句话。\n\n'
        '---\n\n'
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n\n'
        '- 财联社：《报道B》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_rejects_two_complete_sentences_in_one_paragraph(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n第一句话。第二句话。\n\n'
        '## 小标题一\n\n一句。\n\n## 小标题二\n\n一句。\n\n'
        '**信息来源**\n\n- 新华社：《报道A》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '一句一段' in (result.stdout + result.stderr)


def test_validator_rejects_empty_or_messy_source_items(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n一句。\n\n'
        '## 小标题一\n\n一句。\n\n## 小标题二\n\n一句。\n\n'
        '**信息来源**\n\n- \n- 新华社 报道A 2026-08-12\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert '信息来源' in output


def test_validator_requires_blank_line_after_each_body_sentence(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n'
        '第一句话。\n'
        '第二句话。\n\n'
        '## 小标题一\n\n一句。\n\n'
        '## 小标题二\n\n一句。\n\n'
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '两个换行' in (result.stdout + result.stderr)


def test_validator_rejects_plain_source_lines_without_bullets(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n'
        '第一句话。\n\n'
        '## 小标题一\n\n第二句话。\n\n'
        '## 小标题二\n\n第三句话。\n\n'
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
    article.write_text(
        '# 标题\n\n一句。\n\n'
        '## 小标题一\n\n一句。\n\n'
        '## 小标题二\n\n一句。\n\n'
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_rejects_adjacent_source_bullets_without_blank_line(tmp_path: Path):
    article = tmp_path / 'article.md'
    article.write_text(
        '# 标题\n\n一句。\n\n'
        '## 小标题一\n\n一句。\n\n'
        '## 小标题二\n\n一句。\n\n'
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n'
        '- 财联社：《报道B》，2026年8月12日。\n',
        encoding='utf-8',
    )
    result = run_validator(article)
    assert result.returncode != 0
    assert '缺少空行' in (result.stdout + result.stderr)
