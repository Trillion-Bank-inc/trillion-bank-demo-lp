# trillion-bank-demo-lp

株式会社Trillion Bank のコーポレートサイト（プロトタイプ）です。

- トップ：`index.html`。下のページは business / airreach / adctor / usecases / media / news / company の各 `.html`
- 階層構造：`SITEMAP.md`
- 共通部品（ヘッダー・フッター・お問い合わせ）は `partials/`、下のページの中身は `pages_src/`。`python3 tools/build_pages.py` で全ページを組み立てる
- メンバーは `members/members.json` を直し、`python3 tools/build_members.py`（写真は `members/src/` に置く。この リポジトリには含めない）→ `tools/build_pages.py` の順に実行
