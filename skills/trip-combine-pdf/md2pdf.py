#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown を「同行者に見せやすい」きれいな PDF に書き出す（依存ライブラリ不要）。

使い方:
    python3 md2pdf.py <input.md> [output.pdf]

- 標準ライブラリだけで Markdown を HTML に変換する軽量コンバータを内蔵。
  （見出し・太字/斜体・インラインコード・箇条書き(ネスト)・番号付き・引用・
    水平線・GFM表・リンク・段落 に対応。combinations.md の書式を網羅。）
- 変換後の単一HTMLを Google Chrome / Chromium / Edge のヘッドレスで PDF 化する。
- Chrome 系が無い場合は HTML を残し、ブラウザ印刷を案内する。

絵文字は足さない（本リポジトリの方針）。装飾は配色・余白・タイポで表現する。
"""
import html
import os
import re
import subprocess
import sys
import base64

# 画像のソースディレクトリ（main で設定）。画像パス解決の基準。
SRC_DIR = ""

_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
         ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}

def _embed_image(srcpath: str):
    """画像パスを解決し base64 データURIで返す。見つからなければ None。"""
    candidates = [srcpath]
    if SRC_DIR:
        candidates.append(os.path.join(SRC_DIR, srcpath))
    for p in candidates:
        if os.path.isfile(p):
            ext = os.path.splitext(p)[1].lower()
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:{_MIME.get(ext, 'image/png')};base64,{b64}"
    return None


# ──────────────────────────── インライン変換 ────────────────────────────
def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    # 画像 ![alt](src) → <img>（base64埋め込み。リンク処理より前に行う）
    def _img(m):
        alt = m.group(1)
        data = _embed_image(m.group(2).strip())
        src = data if data else m.group(2).strip()
        return (f'<img src="{src}" alt="{alt}" '
                f'style="max-width:100%;height:auto;display:block;'
                f'margin:12px auto;border-radius:10px;border:1px solid var(--line)">')
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _img, text)
    # インラインコード `code`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # リンク [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  r'<a href="\2">\1</a>', text)
    # 太字 **x** / __x__
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    # 斜体 *x* （** を壊さないよう ** 処理後に単独 * を対象）
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def is_table_sep(line: str) -> bool:
    s = line.strip()
    return bool(re.match(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$", s))


def split_row(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


# ──────────────────────────── ブロック変換 ────────────────────────────
def md_to_html_body(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)
    list_stack = []  # [(tag, indent), ...]

    def close_lists(to_indent=-1):
        while list_stack and list_stack[-1][1] > to_indent:
            tag, _ = list_stack.pop()
            out.append(f"</{tag}>")

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        # 空行
        if not line.strip():
            close_lists()
            i += 1
            continue

        # 水平線
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # 見出し
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # 表（ヘッダ行 + 区切り行）
        if "|" in line and i + 1 < n and is_table_sep(lines[i + 1]):
            close_lists()
            header = split_row(line)
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(split_row(lines[i]))
                i += 1
            out.append("<table>")
            out.append("<thead><tr>"
                       + "".join(f"<th>{inline(c)}</th>" for c in header)
                       + "</tr></thead>")
            out.append("<tbody>")
            for row in body:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table>")
            continue

        # 引用
        if re.match(r"^\s*>\s?", line):
            close_lists()
            quote = []
            while i < n and re.match(r"^\s*>\s?", lines[i]):
                quote.append(inline(re.sub(r"^\s*>\s?", "", lines[i])))
                i += 1
            out.append("<blockquote>" + "<br>".join(quote) + "</blockquote>")
            continue

        # リスト（- * + / 1.）ネスト対応（インデント2スペース基準）
        lm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if lm:
            indent = len(lm.group(1).expandtabs(2))
            ordered = bool(re.match(r"\d+\.", lm.group(2)))
            tag = "ol" if ordered else "ul"
            if not list_stack or indent > list_stack[-1][1]:
                out.append(f"<{tag}>")
                list_stack.append((tag, indent))
            else:
                close_lists(indent)
                if not list_stack or list_stack[-1][1] < indent:
                    out.append(f"<{tag}>")
                    list_stack.append((tag, indent))
            out.append(f"<li>{inline(lm.group(3).strip())}</li>")
            i += 1
            continue

        # 段落（連続する非空・非ブロック行をまとめる）
        close_lists()
        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,6}\s|\s*([-*+]|\d+\.)\s|\s*>\s?|\s*([-*_])(\s*\3){2,}\s*$)",
            lines[i],
        ) and not ("|" in lines[i] and i + 1 < n and is_table_sep(lines[i + 1])):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")

    close_lists()
    return "\n".join(out)


# ──────────────────────────── HTML テンプレート ────────────────────────────
CSS = """
:root{
  --ink:#23201c; --muted:#6c6357; --line:#e6ddcf; --bg:#fbf8f2;
  --accent:#b5651d; --accent2:#3f6f5e; --soft:#fff8ec;
}
*{box-sizing:border-box}
html{font-size:14px}
body{
  margin:0; color:var(--ink); background:var(--bg);
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP",
    -apple-system,system-ui,sans-serif;
  line-height:1.75; letter-spacing:.01em;
}
.wrap{max-width:820px; margin:0 auto; padding:40px 44px;}
h1{
  font-size:1.9rem; line-height:1.35; margin:0 0 .2em;
  color:var(--ink); border-bottom:3px solid var(--accent); padding-bottom:.35em;
}
h2{
  font-size:1.32rem; margin:1.9em 0 .55em; color:var(--accent);
  border-left:6px solid var(--accent); padding-left:.55em;
  page-break-after:avoid;
}
h3{
  font-size:1.08rem; margin:1.4em 0 .4em; color:var(--accent2);
  page-break-after:avoid;
}
h4,h5,h6{font-size:1rem; margin:1.1em 0 .35em; color:var(--muted);}
p{margin:.5em 0;}
strong{color:#8a3d12; font-weight:700;}
em{color:var(--accent2); font-style:normal; background:linear-gradient(transparent 65%,#ffe9c9 65%);}
code{
  background:#f1ead c; background:#f2ecd e; font-family:"SFMono-Regular",Menlo,Consolas,monospace;
  font-size:.86em; padding:.08em .4em; border-radius:4px; border:1px solid var(--line);
}
ul,ol{margin:.4em 0 .9em; padding-left:1.5em;}
li{margin:.22em 0;}
li::marker{color:var(--accent);}
hr{border:0; border-top:1px dashed var(--line); margin:2em 0;}
blockquote{
  margin:1em 0; padding:.7em 1em; background:var(--soft);
  border-left:5px solid var(--accent2); border-radius:0 8px 8px 0; color:var(--muted);
}
table{
  border-collapse:collapse; width:100%; margin:1em 0; font-size:.92rem;
  page-break-inside:avoid;
}
th,td{border:1px solid var(--line); padding:.5em .7em; text-align:left; vertical-align:top;}
thead th{background:var(--accent); color:#fff; font-weight:700;}
tbody tr:nth-child(even){background:var(--soft);}
a{color:var(--accent2); text-decoration:none; border-bottom:1px solid #cfe0d8;}
.foot{
  margin-top:3em; padding-top:1em; border-top:1px solid var(--line);
  color:var(--muted); font-size:.8rem; text-align:center;
}
/* 案ブロック（## 案... ）を1枚に収めようとする */
@page{ size:A4; margin:14mm 12mm; }
@media print{ body{background:#fff} .wrap{padding:0} }
""".replace("#f1ead c", "#f1eadc").replace("#f2ecd e", "#f2ecde")

PAGE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{css}</style></head>
<body><div class="wrap">
{body}
<div class="foot">同行者と相談用のたたき台です。気になる案・直したい所があれば気軽にどうぞ。</div>
</div></body></html>"""


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        from shutil import which
        p = which(name)
        if p:
            candidates.append(p)
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 md2pdf.py <input.md> [output.pdf]")
    src = sys.argv[1]
    if not os.path.isfile(src):
        sys.exit(f"入力Markdownが見つかりません: {src}")
    out_pdf = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".pdf"
    os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)

    global SRC_DIR
    SRC_DIR = os.path.dirname(os.path.abspath(src))

    with open(src, encoding="utf-8") as f:
        md = f.read()

    # 先頭の H1 をタイトルに（無ければファイル名）
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    title = m.group(1).strip() if m else os.path.basename(src)

    body = md_to_html_body(md)
    page = PAGE.format(title=html.escape(title), css=CSS, body=body)

    html_path = os.path.splitext(out_pdf)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)

    chrome = find_chrome()
    if not chrome:
        print("⚠️ Chrome/Chromium/Edge が見つかりませんでした。", file=sys.stderr)
        print(f"   中間HTMLを書き出しました: {html_path}", file=sys.stderr)
        print("   このHTMLをブラウザで開き、印刷 → 「PDFとして保存」してください。", file=sys.stderr)
        sys.exit(1)

    abs_html = "file://" + os.path.abspath(html_path)
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={out_pdf}", abs_html,
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0 or not os.path.isfile(out_pdf):
        # 一部の古いビルドは --no-pdf-header-footer 非対応
        cmd2 = [chrome, "--headless=new", "--disable-gpu",
                f"--print-to-pdf={out_pdf}", abs_html]
        subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.isfile(out_pdf):
        try:
            os.remove(html_path)
        except OSError:
            pass
        print(f"✅ PDFを書き出しました: {out_pdf}")
    else:
        print(f"⚠️ PDF生成に失敗。中間HTMLを残しました: {html_path}", file=sys.stderr)
        print("   ブラウザで開いて印刷→PDF保存してください。", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
