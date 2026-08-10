from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from wechat_draft_uploader.wechat import WeChatAPIError, WeChatClient, WeChatConfig, redact_secret


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_create_draft_uploads_cover_body_image_and_rewrites_html(tmp_path: Path) -> None:
    cover = tmp_path / "cover.jpg"
    body_image = tmp_path / "chart.png"
    cover.write_bytes(b"cover")
    body_image.write_bytes(b"chart")
    seen = []

    def opener(request, timeout=30):
        seen.append(request)
        if "/token?" in request.full_url:
            return FakeResponse({"access_token": "TOKEN123", "expires_in": 7200})
        if "material/add_material" in request.full_url:
            return FakeResponse({"media_id": "THUMB123"})
        if "media/uploadimg" in request.full_url:
            return FakeResponse({"url": "https://mmbiz.qpic.cn/chart"})
        if "draft/add" in request.full_url:
            return FakeResponse({"media_id": "DRAFT123"})
        raise AssertionError(request.full_url)

    client = WeChatClient(WeChatConfig("APPID", "SECRET"), opener=opener)

    result = client.create_draft(
        title="测试标题",
        author="作者",
        digest="摘要",
        html='<p>正文</p><img src="chart.png" alt="chart">',
        markdown_path=tmp_path / "article.md",
        cover_path=cover,
        body_images=[body_image],
    )

    assert parse_qs(urlparse(seen[0].full_url).query)["appid"] == ["APPID"]
    assert b'filename="cover.jpg"' in seen[1].data
    assert b'filename="chart.png"' in seen[2].data
    draft = json.loads(seen[3].data.decode("utf-8"))["articles"][0]
    assert draft["title"] == "测试标题"
    assert draft["author"] == "作者"
    assert draft["digest"] == "摘要"
    assert "https://mmbiz.qpic.cn/chart" in draft["content"]
    assert "src=\"chart.png\"" not in draft["content"]
    assert result == {
        "status": "wechat-draft-created",
        "draft_media_id": "DRAFT123",
        "thumb_media_id": "THUMB123",
        "body_image_urls": ["https://mmbiz.qpic.cn/chart"],
    }


def test_wechat_api_error_redacts_credentials_and_access_token() -> None:
    def opener(request, timeout=30):
        return FakeResponse({"errcode": 40164, "errmsg": "invalid ip", "access_token": "TOKEN123"})

    client = WeChatClient(WeChatConfig("APPID", "SECRET"), opener=opener)

    with pytest.raises(WeChatAPIError) as error:
        client.fetch_access_token()

    message = str(error.value)
    assert "40164" in message
    assert "SECRET" not in message
    assert "TOKEN123" not in message


def test_redact_secret_masks_query_values() -> None:
    assert redact_secret("secret=SECRET&access_token=TOKEN", {"SECRET", "TOKEN"}) == (
        "secret=***&access_token=***"
    )
