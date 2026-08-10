from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Sequence

from .markdown import find_local_images, render_markdown
from .wechat import WeChatClient, WeChatConfig, redact_secret


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    markdown_path = args.markdown.resolve()
    output_path = (args.output or markdown_path.parent / "draft-result.json").resolve()
    preview_path = (args.preview_html or output_path.parent / "preview.html").resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    secrets: set[str] = set()

    try:
        markdown_text = markdown_path.read_text(encoding="utf-8")
        html = render_markdown(markdown_text)
        body_images = find_local_images(html, markdown_path)
        preview_path.write_text(html, encoding="utf-8")
        title = args.title or _title_from_markdown(markdown_text) or markdown_path.stem
        if args.dry_run:
            result = {
                "status": "dry-run",
                "title": title,
                "markdown_path": str(markdown_path),
                "preview_path": str(preview_path),
                "body_image_count": len(body_images),
            }
            _write_result(output_path, result)
            print(f"Dry run complete: {preview_path}")
            return 0

        env = load_env_file(args.env_file)
        app_id = env.get("WECHAT_APP_ID", os.environ.get("WECHAT_APP_ID", "")).strip()
        app_secret = env.get("WECHAT_APP_SECRET", os.environ.get("WECHAT_APP_SECRET", "")).strip()
        secrets.update({app_id, app_secret})
        if not app_id or not app_secret:
            raise MissingCredentialsError("WECHAT_APP_ID and WECHAT_APP_SECRET are required")
        if args.cover is None:
            raise ValueError("--cover is required unless --dry-run is used")
        cover_path = args.cover.resolve()
        if not cover_path.is_file():
            raise FileNotFoundError(f"cover image not found: {cover_path}")
        timeout = _int_value(args.timeout_seconds or env.get("WECHAT_TIMEOUT_SECONDS", "30"), 30)
        client = WeChatClient(WeChatConfig(app_id, app_secret), timeout=timeout)
        result = client.create_draft(
            title=title,
            author=args.author or env.get("WECHAT_AUTHOR", "公众号作者"),
            digest=args.digest,
            html=html,
            markdown_path=markdown_path,
            cover_path=cover_path,
            body_images=body_images,
        )
        result.update(
            {
                "title": title,
                "markdown_path": str(markdown_path),
                "preview_path": str(preview_path),
                "body_image_count": len(body_images),
            }
        )
        _write_result(output_path, result)
        print(f"WeChat draft created: {result['draft_media_id']}")
        return 0
    except MissingCredentialsError as exc:
        _write_failure(output_path, exc, secrets)
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        _write_failure(output_path, exc, secrets)
        print(redact_secret(str(exc), secrets), file=sys.stderr)
        return 1


class MissingCredentialsError(ValueError):
    pass


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a Markdown article to the WeChat draft box.")
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--cover", type=Path)
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--digest", default="")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preview-html", type=Path)
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _title_from_markdown(markdown_text: str) -> str:
    for line in markdown_text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match:
            return match.group(1).strip()
    return ""


def _int_value(value: str | int, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _write_result(path: Path, result: dict) -> None:
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_failure(path: Path, exc: Exception, secrets: set[str]) -> None:
    _write_result(path, {"status": "failed", "error": redact_secret(str(exc), secrets)})


if __name__ == "__main__":
    raise SystemExit(main())
