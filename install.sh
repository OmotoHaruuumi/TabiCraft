#!/usr/bin/env bash
# Tabicraft インストーラ
# skills を ~/.claude/skills へ、空テンプレを ~/.claude/travel/templates へ配置します。
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DST="$HOME/.claude/skills"
SHARED="$HOME/.claude/travel"

echo "▶ スキルを $SKILLS_DST へインストールします"
mkdir -p "$SKILLS_DST"
for s in trip-plan trip-profile trip-basics trip-combine trip-combine-pdf trip-refine trip-brochure; do
  rm -rf "$SKILLS_DST/$s"
  cp -R "$SRC/skills/$s" "$SKILLS_DST/$s"
  echo "  ✔ $s"
done

echo "▶ 共有データ領域を用意します: $SHARED"
mkdir -p "$SHARED/profiles" "$SHARED/templates"
cp "$SRC/templates/"*.md "$SHARED/templates/"
echo "  ✔ templates / profiles"

cat <<'EOF'

✅ インストール完了！

使い方はこれだけ：
  Claude Code で「旅行の計画したい」または「〇〇に△△と□泊で行きたい」と話しかけるだけ。
  あとは司令塔スキル (trip-plan) が順番に案内してくれます。

EOF
