# trillion-bank-demo-lp

株式会社Trillion Bank のコーポレートサイト（プロトタイプ）です。

- トップ：`index.html`。下のページは business / airreach / adctor / usecases / media / news / company の各 `.html`
- 階層構造：`SITEMAP.md`
- 共通部品（ヘッダー・フッター・お問い合わせ）は `partials/`、下のページの中身は `pages_src/`。`python3 tools/build_pages.py` で全ページを組み立てる
- メンバーは `members/members.json` を直し、`python3 tools/build_members.py`（写真は `members/src/` に置く。この リポジトリには含めない）→ `tools/build_pages.py` の順に実行

## ニュース・コラムの投稿

1. `content/news/_template.md` をコピーして、`content/news/2026-12-01-英数字の名前.md` として保存
2. 先頭の `---` のあいだ（タイトル・日付・分類・表紙の色・説明）と、本文を書く
3. `main` に push する

push すると GitHub Actions が `tools/build_pages.py` と `tools/build_news.py` を実行し、一覧（news.html）・記事のページ（news-名前.html）・トップの News を更新して、GitHub Pages に公開します。手元で確かめるときは、同じ2つのスクリプトを実行してから index.html を開きます。
