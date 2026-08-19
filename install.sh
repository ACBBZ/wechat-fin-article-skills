#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

python3 - "$ROOT_DIR" "$TMP_DIR" <<'PY'
from __future__ import annotations

import base64
import hashlib
import sys
import zipfile
from io import BytesIO
from pathlib import Path

root = Path(sys.argv[1])
tmp = Path(sys.argv[2])
expected_sha256 = "cd57214724966e047dd063194c37ef79b781a6dd919a46be25bf6df710f2108d"
parts = [
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-00",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-01a",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-01b",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-01c",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-02",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-03",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-04",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-05",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-06a",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-06b",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-06c",
    "bundle/wechat-fin-arcticle-skill-v2.5.zip.b64.part-06d",
]

missing = [name for name in parts if not (root / name).is_file()]
if missing:
    raise SystemExit("缺少安装包分片：" + ", ".join(missing))

encoded = "".join((root / name).read_text(encoding="utf-8") for name in parts)
try:
    bundle = base64.b64decode(encoded, validate=True)
except Exception as exc:
    raise SystemExit(f"安装包 Base64 解码失败：{exc}") from exc

actual_sha256 = hashlib.sha256(bundle).hexdigest()
if actual_sha256 != expected_sha256:
    raise SystemExit(
        "安装包 SHA256 校验失败："
        f"expected={expected_sha256}, actual={actual_sha256}"
    )

with zipfile.ZipFile(BytesIO(bundle)) as archive:
    archive.testzip_result = archive.testzip()
    if archive.testzip_result is not None:
        raise SystemExit(f"安装包 ZIP 完整性校验失败：{archive.testzip_result}")
    archive.extractall(tmp)

print("安装包分片重组、SHA256 与 ZIP 完整性校验通过。")
PY

bash "$TMP_DIR/install.sh"
