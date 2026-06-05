# 🧭 Tabicraft — あなた専属の旅行プランナー for Claude Code

> *turn your wishes into a workable trip*
> 「来月ヨーロッパに親友と6泊で行きたいな」**と話しかけるだけ**。
> 好みのヒアリング → 候補提案 → 日程の作り込み → **ワンタップ地図つきの“かっこいい旅のしおり（HTML/PDF/PNG）”** まで一緒に作ります。

---

## ⚡ 使い方は、これだけ

```text
1. インストール:   ./install.sh を実行するだけ
2. 計画スタート:   Claude Code で「旅行の計画したい」と話しかけるだけ
```

スキル名も手順も覚える不要。司令塔が状況を見て次にやることを案内します。途中でやめても次に話しかければ続きから再開。

---

## ✨ こだわり（なぜ Tabicraft か）

- 🧠 **一度きりで終わらない** — 好み・こだわりを保存し、**次の旅行ではもっと賢く**なって提案する
- 🙆 **基本は指示に従うだけ** — あなたは選ぶ・決めるだけでいい
- 💡 **候補を自分から提案** — 行きたい場所・泊まりたい宿の候補を**先回りで出す**
- 🛠 **一番大変な所を代行** — あなたが選んだ「やりたいこと」を、**実現可能性チェック＋具体的なスケジュール**に組み上げる
- ⏳ **余裕のある日程** — 旅はハプニングの連続。必須は2〜3個に絞り、**「時間が余ったらコレ」を散りばめる**

---

## 🗺 フェーズと出力例（誰でも見られる見本つき）

話しかけると、内部の6スキルが順に動きます。各段階の出力イメージはこちら：

| 段階 | やること | 出力例（クリック） |
|---|---|---|
| Phase 0 プロファイル | 好みを学習・蓄積（使うほど賢く） | [profile_example.md](examples/profile_example.md) |
| 入力 wishlist | 行きたい所・食べたい物を列挙 | [wishlist_example.md](examples/wishlist_example.md) |
| Phase 1 基本情報 | 行き先・泊数・到着/帰宅を確定 | [trip-basics_example.md](examples/trip-basics_example.md) |
| Phase 2 組み合わせ | 案を多数生成＋気づき提案 | [combinations_example.md](examples/combinations_example.md) |
| Phase 3 作り込み | 余裕ある現実的な日程へ | [plan_example.md](examples/plan_example.md) |
| Phase 4 しおり | かっこいい HTML を生成 | **[brochure_example.html](examples/brochure_example.html)** |

➡️ まずは **[完成しおりの見本](examples/brochure_example.html)**（親友とローマ＆フィレンツェ5泊6日）を開いてみてください。

---

## 🖨 しおりは HTML / PDF / PNG で保存できる

- しおりを開いて右上の **🖨 PDFで保存** ボタン（ブラウザ印刷 → PDF）
- まとめて書き出し: `~/.claude/skills/trip-brochure/export.sh output/<旅行名>.html output/<旅行名>.pdf`（`.png` 指定で画像）
  ※ Chrome/Chromium/Edge のヘッドレスを利用。無ければブラウザ印刷を案内します。

---

## 🔒 個人情報は公開されません

- 個人データ（プロファイル / `wishlist.md` / `trip-basics.md` / `combinations.md` / `plans/` / `output/`）は**すべて [.gitignore](.gitignore) 済み**。
- スキルは個人ファイルを**必ず決まった名前で作成**します。「自分で書きたい」ときもスキル側が正しい名前の空ファイルを用意し、あなたは命名しない（公開事故の防止）。
- 見本は公開してよい **`_example` 名**だけ。実データを `_example` 名で保存しません。

→ **このリポジトリ内で実際の旅行を計画しても、個人情報は出ていきません。**

---

## 📦 インストール

```bash
git clone <this-repo>
cd <this-repo>
./install.sh
```

スキルを `~/.claude/skills/` へ、空テンプレを `~/.claude/travel/templates/` へ配置します。
あとは「**旅行の計画したい**」と話しかけるだけ。

### ファイル配置
```
~/.claude/travel/        ♻️ 使い回す（プロファイル・テンプレ／非公開）
<旅行フォルダ>/           📌 今回限定（作業ファイル・しおり／非公開）

このリポジトリ（公開）
├ skills/      6スキル本体
├ templates/   空テンプレ
├ examples/    _example 見本
└ install.sh
```

---

## 🛠 カスタマイズ

- しおりの見た目 → `skills/trip-brochure/assets/brochure-template.html`
- ヒアリング項目 → `templates/profile-template.md` / `templates/wishlist-template.md`
- フェーズの挙動 → 各 `skills/trip-*/SKILL.md`（編集後 `./install.sh` で再反映）

旅程は完成品ではなく**一緒に育てる叩き台**。楽しい旅を 🌍
