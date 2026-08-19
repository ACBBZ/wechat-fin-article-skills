from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

from wechat_draft_uploader.markdown import render_markdown, find_local_images, replace_image_sources
from wechat_draft_uploader.wechat import redact_secret, WeChatClient, WeChatConfig


def test_markdown_images_and_dry_run(tmp_path: Path):
    (tmp_path / 'images').mkdir()
    img1 = tmp_path / 'images' / 'a.png'; img1.write_bytes(b'png-a')
    img2 = tmp_path / 'images' / 'b.png'; img2.write_bytes(b'png-b')
    md = tmp_path / 'article.md'
    md.write_text('# 标题\n\n![A](images/a.png)\n\n正文\n\n![B](images/b.png)\n', encoding='utf-8')
    html = render_markdown(md.read_text(encoding='utf-8'))
    assert find_local_images(html, md) == [img1.resolve(), img2.resolve()]
    replaced = replace_image_sources(html, {img1.resolve(): 'https://wx.example/a', img2.resolve(): 'https://wx.example/b'}, md)
    assert 'https://wx.example/a' in replaced and 'https://wx.example/b' in replaced

    out = tmp_path / 'draft-result.json'
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path(__file__).resolve().parents[1] / 'src')
    proc = subprocess.run([
        sys.executable, '-m', 'wechat_draft_uploader.cli',
        '--markdown', str(md), '--dry-run', '--output', str(out)
    ], env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(out.read_text(encoding='utf-8'))
    assert result['status'] == 'dry-run'
    assert result['body_image_count'] == 2
    assert Path(result['preview_path']).is_file()


def test_redacts_secret_and_access_token():
    secret = 's3cr3t-value'
    text = redact_secret(f'https://api.weixin.qq.com?secret={secret}&access_token=abc', {secret, 'abc'})
    assert secret not in text and 'abc' not in text
    assert '***' in text


def test_create_draft_uses_expected_wechat_endpoints(tmp_path: Path):
    class FakeResponse:
        def __init__(self, payload): self.payload = json.dumps(payload).encode('utf-8')
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return self.payload

    calls = []
    responses = iter([
        {'access_token': 'token-123', 'expires_in': 7200},
        {'media_id': 'thumb-1'},
        {'url': 'https://mmbiz.example/a'},
        {'url': 'https://mmbiz.example/b'},
        {'media_id': 'draft-1'},
    ])
    def opener(request, timeout):
        calls.append(request.full_url)
        return FakeResponse(next(responses))

    (tmp_path / 'images').mkdir()
    cover = tmp_path / 'cover.png'; cover.write_bytes(b'cover')
    a = tmp_path / 'images' / 'a.png'; a.write_bytes(b'a')
    b = tmp_path / 'images' / 'b.png'; b.write_bytes(b'b')
    md = tmp_path / 'article.md'; md.write_text('# T\n\n![A](images/a.png)\n![B](images/b.png)\n', encoding='utf-8')
    html = render_markdown(md.read_text(encoding='utf-8'))
    client = WeChatClient(WeChatConfig('appid', 'secret-value'), opener=opener)
    result = client.create_draft('标题', '作者', '摘要', html, md, cover, [a, b])
    assert result['status'] == 'wechat-draft-created'
    assert result['draft_media_id'] == 'draft-1'
    assert len(result['body_image_urls']) == 2
    assert any('/token?' in u for u in calls)
    assert any('/material/add_material?' in u for u in calls)
    assert sum('/media/uploadimg?' in u for u in calls) == 2
    assert any('/draft/add?' in u for u in calls)


def test_render_markdown_preserves_single_line_breaks_and_styles_h2():
    html = render_markdown('第一句。\n第二句。\n\n## 小标题\n\n第三句。\n')
    assert '<br />' in html
    assert '<h2 style=' in html
    assert 'font-size:20px' in html
    assert 'font-weight:700' in html


def test_render_markdown_styles_information_sources():
    html = render_markdown(
        '**信息来源**\n\n'
        '- 中国民用航空局：《文件A》，2026年8月12日。\n'
        '- 新华社：《报道B》，2026年8月12日。\n'
    )
    assert 'data-section="information-sources"' in html
    assert 'font-size:14px' in html
    assert '中国民用航空局' in html
    assert '新华社' in html


def test_render_markdown_cleans_empty_and_duplicate_sources():
    html = render_markdown(
        '**信息来源**\n\n'
        '- \n'
        '- 新华社：《报道B》，2026年8月12日。\n'
        '- \n'
        '- 新华社：《报道B》，2026年8月12日。\n'
    )
    assert '<li style="margin:0 0 6px;"></li>' not in html
    assert html.count('新华社：《报道B》，2026年8月12日。') == 1


def test_render_markdown_uses_visible_paragraph_spacing_for_two_newlines():
    html = render_markdown('第一句。\n\n第二句。\n')
    assert html.count('data-role="body-paragraph"') == 2
    assert 'margin:0 0 1em;' in html
    assert '<br />' not in html


def test_render_markdown_sources_keep_bullets_with_spacing():
    html = render_markdown(
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n\n'
        '- 财联社：《报道B》，2026年8月12日。\n'
    )
    assert 'data-section="information-sources"' in html
    assert '<ul' in html
    assert '<li' in html
    assert 'margin:0 0 12px;' in html
    assert '新华社：《报道A》，2026年8月12日。' in html
    assert '财联社：《报道B》，2026年8月12日。' in html


def test_render_markdown_bullet_sources_are_deduplicated_and_keep_bullets():
    html = render_markdown(
        '**信息来源**\n\n'
        '- 新华社：《报道A》，2026年8月12日。\n'
        '- 新华社：《报道A》，2026年8月12日。\n'
        '- 财联社：《报道B》，2026年8月12日。\n'
    )
    assert '<ul' in html
    assert '<li' in html
    assert html.count('新华社：《报道A》，2026年8月12日。') == 1
    assert html.count('财联社：《报道B》，2026年8月12日。') == 1
