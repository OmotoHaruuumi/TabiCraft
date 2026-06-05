#!/usr/bin/env bash
# 旅のしおり HTML を PDF / PNG に書き出す
# 使い方: export.sh <input.html> [output.pdf | output.png]
#   拡張子が .png なら画像、それ以外は PDF を生成します。
# Google Chrome / Chromium / Microsoft Edge のヘッドレスを利用します。
set -euo pipefail

HTML="${1:?使い方: export.sh <input.html> [out.pdf|out.png]}"
OUT="${2:-${HTML%.html}.pdf}"

[ -f "$HTML" ] || { echo "入力HTMLが見つかりません: $HTML" >&2; exit 1; }

# Chrome 系バイナリを探す（macOS / Linux）
CANDIDATES=(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  "/Applications/Chromium.app/Contents/MacOS/Chromium"
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  "$(command -v google-chrome 2>/dev/null || true)"
  "$(command -v chromium 2>/dev/null || true)"
  "$(command -v chromium-browser 2>/dev/null || true)"
)
CHROME=""
for c in "${CANDIDATES[@]}"; do
  [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
done

if [ -z "$CHROME" ]; then
  echo "⚠️ Chrome/Chromium/Edge が見つかりませんでした。" >&2
  echo "   ブラウザで $HTML を開き、印刷ダイアログ（Cmd+P / Ctrl+P）→「PDFとして保存」してください。" >&2
  exit 1
fi

ABS="file://$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"

case "$OUT" in
  *.png|*.PNG)
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
      --window-size=900,3508 --screenshot="$OUT" "$ABS" >/dev/null 2>&1
    ;;
  *)
    "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
      --print-to-pdf="$OUT" "$ABS" >/dev/null 2>&1
    ;;
esac

echo "✅ 書き出しました: $OUT"
