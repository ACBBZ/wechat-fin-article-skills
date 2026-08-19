from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .markdown import replace_image_sources

API_BASE = "https://api.weixin.qq.com/cgi-bin"
IMAGE_CONTENT_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


class WeChatAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class WeChatConfig:
    app_id: str
    app_secret: str


class WeChatClient:
    def __init__(self, config: WeChatConfig, opener: Callable[[Request, int], Any] | None = None, timeout: int = 30) -> None:
        self.config = config
        self.opener = opener or _default_opener
        self.timeout = timeout

    def create_draft(self, title: str, author: str, digest: str, html: str, markdown_path: Path, cover_path: Path, body_images: Sequence[Path]) -> dict[str, Any]:
        access_token = self.fetch_access_token()
        thumb_media_id = self.upload_thumb(access_token, cover_path)
        replacements: dict[Path, str] = {}
        body_image_urls: list[str] = []
        for image_path in body_images:
            image_url = self.upload_article_image(access_token, image_path)
            replacements[image_path.resolve()] = image_url
            body_image_urls.append(image_url)
        content = replace_image_sources(html, replacements, markdown_path)
        draft_media_id = self.add_draft(access_token, title, author, digest, content, thumb_media_id)
        return {
            "status": "wechat-draft-created",
            "draft_media_id": draft_media_id,
            "thumb_media_id": thumb_media_id,
            "body_image_urls": body_image_urls,
        }

    def fetch_access_token(self) -> str:
        query = urlencode({"grant_type": "client_credential", "appid": self.config.app_id, "secret": self.config.app_secret})
        payload = self._request_json(Request(f"{API_BASE}/token?{query}", method="GET"))
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise self._error("access_token missing from response", payload)
        return token

    def upload_thumb(self, access_token: str, cover_path: Path) -> str:
        return self._upload_file("material/add_material", {"access_token": access_token, "type": "thumb"}, cover_path, "media_id", {access_token})

    def upload_article_image(self, access_token: str, image_path: Path) -> str:
        return self._upload_file("media/uploadimg", {"access_token": access_token}, image_path, "url", {access_token})

    def add_draft(self, access_token: str, title: str, author: str, digest: str, content: str, thumb_media_id: str) -> str:
        body = json.dumps({"articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }]}, ensure_ascii=False).encode("utf-8")
        request = Request(
            f"{API_BASE}/draft/add?{urlencode({'access_token': access_token})}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        payload = self._request_json(request, secrets={access_token})
        media_id = payload.get("media_id")
        if not isinstance(media_id, str) or not media_id:
            raise self._error("draft media_id missing from response", payload, {access_token})
        return media_id

    def _upload_file(self, endpoint: str, query: dict[str, str], file_path: Path, response_key: str, secrets: set[str]) -> str:
        content_type = IMAGE_CONTENT_TYPES.get(file_path.suffix.lower())
        if content_type is None:
            raise WeChatAPIError(f"unsupported image type: {file_path.name}")
        boundary = "----wechat-draft-uploader-" + uuid.uuid4().hex
        body = _multipart_file_body(boundary, "media", file_path.name, content_type, file_path.read_bytes())
        request = Request(
            f"{API_BASE}/{endpoint}?{urlencode(query)}",
            data=body,
            method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        payload = self._request_json(request, secrets=secrets)
        value = payload.get(response_key)
        if not isinstance(value, str) or not value:
            raise self._error(f"{response_key} missing from response", payload, secrets)
        return value

    def _request_json(self, request: Request, secrets: set[str] | None = None) -> dict[str, Any]:
        all_secrets = {self.config.app_secret, *(secrets or set())}
        try:
            with self.opener(request, self.timeout) as response:
                raw = response.read().decode("utf-8")
        except Exception as exc:
            raise WeChatAPIError(redact_secret(str(exc), all_secrets)) from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WeChatAPIError(redact_secret(raw, all_secrets)) from exc
        if not isinstance(payload, dict):
            raise WeChatAPIError("wechat response must be a JSON object")
        errcode = payload.get("errcode", 0)
        if errcode not in (0, "0"):
            raise self._error("wechat api error", payload, all_secrets)
        return payload

    def _error(self, message: str, payload: dict[str, Any], secrets: set[str] | None = None) -> WeChatAPIError:
        safe_payload = {key: value for key, value in payload.items() if key != "access_token"}
        return WeChatAPIError(redact_secret(
            f"{message}: {json.dumps(safe_payload, ensure_ascii=False)}",
            {self.config.app_secret, *(secrets or set())},
        ))


def redact_secret(text: str, secrets: set[str]) -> str:
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***")
    redacted = re.sub(r"(access_token=)[^&\s]+", r"\1***", redacted)
    redacted = re.sub(r"(secret=)[^&\s]+", r"\1***", redacted)
    return redacted


def _multipart_file_body(boundary: str, field_name: str, filename: str, content_type: str, content: bytes) -> bytes:
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return head + content + tail


def _default_opener(request: Request, timeout: int):
    return urlopen(request, timeout=timeout)
