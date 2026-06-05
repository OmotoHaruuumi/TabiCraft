---
name: trip-combine-pdf
description: combinations.md（プラン案の組み合わせ一覧）を、同行者に見てもらうための読みやすいPDFに書き出す。Markdownを内蔵コンバータできれいなHTMLにし、Chromeヘッドレスで output/combinations.pdf を生成（依存ライブラリ不要）。「案をPDFにして」「combinationsを共有用に書き出して」などで起動。Phase 2の補助。
---

# trip-combine-pdf — 組み合わせ案を共有用PDFに書き出す

`combinations.md` は同行者に「どの案がいい？」と相談するのにそのまま使える。
Markdown のままだと見せにくいので、**読みやすい単一PDF**に書き出して共有できるようにする。

## 入力
- `combinations.md`（trip-combine が生成する案一覧。必須）
- 変換スクリプト: スキルフォルダ内 `md2pdf.py`（標準ライブラリのみ・追加インストール不要）

## 出力
- `output/combinations.pdf`（`output/` は gitignore 済みなので公開されない。`*.pdf` も明示除外済み）

## 手順

### 1. 前提確認
- `combinations.md` が無ければ trip-combine（Phase 2）に戻す。「まず案を作りますか？」と案内。
- 既に `output/combinations.pdf` がある場合は上書きしてよいか一言添える（基本は上書きでOK）。

### 2. 書き出し方の確認（AskUserQuestion）
着手前に **おまかせ（このまま整形してPDF化） / 案を絞ってから（不要な案を外す・並べ替える） / 一度止めて相談する** を提示。
- 「案を絞ってから」なら、先に combinations.md を編集（または一時コピーを作って編集）してから変換。
- **「一度止めて相談する」は常に選択肢に含める**（選ばれたら自動進行を止めて会話する）。

### 3. PDF 生成
Bash で内蔵スクリプトを実行する（出力先フォルダは自動作成される）:
```
mkdir -p output
python3 ~/.claude/skills/trip-combine-pdf/md2pdf.py combinations.md output/combinations.pdf
```
- 配色・余白・タイポで整形した A4 縦の単一PDFができる。**絵文字は足さない**（本リポジトリの方針）。
- Chrome / Chromium / Edge のヘッドレスを使う。見つからない場合はスクリプトが中間HTMLを残すので、
  「ブラウザで開いて 印刷 → PDFとして保存」を案内する。
- 別ファイルを変換したいときは第1引数を差し替える（汎用Markdown→PDFとしても使える）。

### 4. 共有の案内
```
組み合わせ案を output/combinations.pdf に書き出しました。
このPDFを同行者に共有して「どの案がいい？」と相談できます。
（output/ と *.pdf は gitignore 済みなので、うっかり公開されません。）
案を増やす/減らす・順番を変えるなどあれば、combinations.md を直してまた書き出せます。
```

## 注意
- combinations.md の内容は勝手に作り替えない（整形・PDF化のみ）。案の取捨選択はユーザー合意のうえで。
- スマホで見る同行者も多いので、文字は詰め込みすぎず、案ごとに見出し（## 案…）で区切られている前提で整形する。
- 1案＝なるべく見開きで追えるよう、表・見出しはページ途中で割れにくいCSSにしてある（スクリプト側で対応済み）。
