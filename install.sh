#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$ROOT_DIR/wechat-fin-arcticle-skill-v2.5.zip"
if [[ ! -f "$BUNDLE" ]]; then
  echo "未找到安装包：$BUNDLE" >&2
  exit 2
fi
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
unzip -q "$BUNDLE" -d "$TMP_DIR"
bash "$TMP_DIR/install.sh"
