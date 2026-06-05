#!/usr/bin/env python3
"""しおりHTML内の images/... 参照を base64 データURIに埋め込み、単一ファイル化する。

使い方:
    python3 embed_images.py <input.html> [output.html]

- <img src="images/xxx"> を data:URI に置換（相対パスは入力HTMLの場所基準で解決）。
- 出力省略時は <input>_単一ファイル.html。
- 依存なし（標準ライブラリのみ）。スマホ共有用に1ファイルで完結させる目的。
"""
import base64
import os
import re
import sys

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}


def main():
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 embed_images.py <input.html> [output.html]")
    src = sys.argv[1]
    if not os.path.isfile(src):
        sys.exit(f"入力HTMLが見つかりません: {src}")
    base = os.path.dirname(os.path.abspath(src))
    if len(sys.argv) > 2:
        out = sys.argv[2]
    else:
        root, ext = os.path.splitext(src)
        out = root + "_単一ファイル" + ext

    html = open(src, encoding="utf-8").read()
    missing = []

    def repl(m):
        rel = m.group(1)
        path = rel if os.path.isabs(rel) else os.path.join(base, rel)
        if not os.path.isfile(path):
            missing.append(rel)
            return m.group(0)
        ext = os.path.splitext(path)[1].lower()
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'src="data:{MIME.get(ext, "image/jpeg")};base64,{b64}"'

    out_html = re.sub(r'src="(images/[^"]+)"', repl, html)
    with open(out, "w", encoding="utf-8") as f:
        f.write(out_html)

    remaining = len(re.findall(r'src="images/', out_html))
    print(f"✅ 単一ファイル化しました: {out}")
    if missing:
        print("⚠️ 見つからず埋め込めなかった画像:", ", ".join(sorted(set(missing))))
    print(f"   残りの images/ 参照: {remaining}")


if __name__ == "__main__":
    main()
