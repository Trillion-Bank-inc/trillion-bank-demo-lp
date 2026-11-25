#!/usr/bin/env python3
"""ニュース・コラムを作る。

content/news/*.md（先頭が「_」のファイルは公開しない）から、次を作る。
  - news.html                … 一覧（いちばん新しい記事を大きく、年と分類で絞り込み、3列のカード）
  - news-<名前>.html         … 記事のページ
  - assets/news/<名前>.svg   … 表紙の画像（画像を指定しない記事だけ。ロゴの形と青で、自動で作る）
  - index.html のトップの「News」の4枚のカード
共通のヘッダー・フッターは tools/build_pages.py のものを使う。
"""
import glob
import html as H
import importlib.util
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731
spec = importlib.util.spec_from_file_location('bp', P('tools', 'build_pages.py'))
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)
E = H.escape

COLORS = {  # 表紙：背景・文字・アクセント
    'blue': ('#164bff', '#ffffff', '#c2d1ff'),
    'navy': ('#10182b', '#ffffff', '#ff8a3d'),
    'sky': ('#e4ebff', '#10182b', '#164bff'),
    'paper': ('#f4f1ea', '#10182b', '#164bff'),
}


# ---------------- 記事を読む ----------------
def parse(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m:
        raise SystemExit(f'{path}：先頭の --- 〜 --- がありません')
    meta = dict((k.strip(), v.strip()) for k, v in re.findall(r'^(\w+):\s*(.*)$', m.group(1), re.M))
    for k in ('title', 'date', 'category', 'description'):
        if not meta.get(k):
            raise SystemExit(f'{path}：{k} がありません')
    name = os.path.splitext(os.path.basename(path))[0]
    meta['slug'] = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)
    meta['body_md'] = re.sub(r'<!--.*?-->', '', m.group(2), flags=re.S).strip()
    meta['cover'] = meta.get('cover', 'blue') if meta.get('cover', 'blue') in COLORS else 'blue'
    meta['url'] = f"news-{meta['slug']}.html"
    meta['img'] = f"assets/news/{meta['image']}" if meta.get('image') else f"assets/news/{meta['slug']}.svg"
    return meta


def inline(s):
    s = E(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\[(.+?)\]\((.+?)\)', lambda m: f'<a href="{m.group(2)}"' + (' target="_blank" rel="noopener noreferrer"' if m.group(2).startswith('http') else '') + f'>{m.group(1)}</a>', s)
    return s


def md(text):
    """見出し（##・###）・段落・箇条書き（-）・引用（>）・太字・リンクだけの、小さな変換。"""
    out, toc = [], []
    for block in re.split(r'\n\s*\n', text):
        lines = [l for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        if lines[0].startswith('### '):
            out.append(f'<h3>{inline(lines[0][4:])}</h3>')
            rest = lines[1:]
        elif lines[0].startswith('## '):
            hid = f'h{len(toc) + 1}'
            toc.append((hid, lines[0][3:]))
            out.append(f'<h2 id="{hid}">{inline(lines[0][3:])}</h2>')
            rest = lines[1:]
        else:
            rest = lines
        if not rest:
            continue
        if all(l.startswith('- ') for l in rest):
            out.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in rest) + '</ul>')
        elif all(l.startswith('> ') for l in rest):
            out.append('<blockquote><p>' + '<br>'.join(inline(l[2:]) for l in rest) + '</p></blockquote>')
        else:
            out.append('<p>' + '<br>'.join(inline(l) for l in rest) + '</p>')
    return '\n'.join(out), toc


# ---------------- 表紙の画像（オリジナル） ----------------
def cover_svg(a):
    bg, fg, ac = COLORS[a['cover']]
    en = E(a.get('cover_en') or a['category'])
    size = 92 if len(en) <= 10 else 72 if len(en) <= 16 else 58
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 750">
  <rect width="1200" height="750" fill="{bg}"/>
  <g fill="none" stroke="{fg}" stroke-opacity=".12" stroke-width="2">
    <circle cx="980" cy="160" r="260"/><circle cx="980" cy="160" r="340"/><circle cx="980" cy="160" r="420"/>
  </g>
  <g transform="translate(760 210) scale(.95)" fill="none" stroke="{fg}" stroke-width="14" stroke-linejoin="round" opacity=".9">
    <path d="M103 74 L168 42 L168 214 L103 247 Z"/><path d="M183 97 L248 64 L248 236 L183 268 Z"/><path d="M263 108 L327 75 L327 248 L263 281 Z"/>
  </g>
  <path transform="translate(760 210) scale(.95)" d="M25 165 H105 C130 165 140 137 166 137 C200 137 216 191 256 191 C286 191 296 165 322 165 H389" fill="none" stroke="{ac}" stroke-width="16" stroke-linecap="round"/>
  <text x="80" y="128" fill="{ac}" font-family="Google Sans Flex, Noto Sans JP, sans-serif" font-size="30" font-weight="700" letter-spacing="3">TRILLION BANK · {E(a['category'])}</text>
  <text x="76" y="640" fill="{fg}" font-family="Google Sans Flex, Noto Sans JP, sans-serif" font-size="{size}" font-weight="600" letter-spacing="-2">{en}</text>
</svg>
'''


# ---------------- 部品 ----------------
def ymd(d):
    return d.replace('-', '.')


def card(a, cls='nlc'):
    return f'''<li class="{cls}" data-cat="{E(a['category'])}" data-year="{a['date'][:4]}">
          <a href="{a['url']}">
            <span class="{cls}__img"><img src="{a['img']}" alt="" width="1200" height="750" loading="lazy" decoding="async"></span>
            <span class="{cls}__tag">{E(a['category'])}</span>
            <span class="{cls}__title">{E(a['title'])}</span>
            <time class="{cls}__date" datetime="{a['date']}">{ymd(a['date'])}</time>
          </a>
        </li>'''


def page(title, desc, page_id, body, extra_head=''):
    out = bp.HEAD.format(title=E(title), desc=E(desc), page=page_id, body=body)
    out = out.replace('</head>', extra_head + '</head>', 1)
    return bp.fill_markers(out, 'news')


def list_page(arts):
    feat = arts[:3]
    slides = '\n'.join(f'''<li class="nfeat__slide{' is-on' if i == 0 else ''}" data-i="{i}">
          <a href="{a['url']}">
            <span class="nfeat__img"><img src="{a['img']}" alt="" width="1200" height="750" decoding="async"></span>
            <span class="nfeat__body"><span class="nlc__tag">{E(a['category'])}</span><span class="nfeat__title">{E(a['title'])}</span><time datetime="{a['date']}">{ymd(a['date'])}</time></span>
          </a>
        </li>''' for i, a in enumerate(feat))
    dots = ''.join(f'<button type="button" class="nfeat__dot{" is-on" if i == 0 else ""}" data-i="{i}" aria-label="{i + 1}件目"><span>{i + 1:02d}</span></button>' for i in range(len(feat)))
    years = sorted({a['date'][:4] for a in arts}, reverse=True)
    cats = []
    for a in arts:
        if a['category'] not in cats:
            cats.append(a['category'])
    pill = lambda key, val, label, on=False: f'<button type="button" class="npill{" is-on" if on else ""}" data-{key}="{E(val)}" aria-pressed="{"true" if on else "false"}">{E(label)}</button>'  # noqa: E731
    body = f'''<section class="phero" aria-labelledby="ph-title">
  <div class="phero__inner">
    {bp.crumbs('News')}
    <p class="phero__en" aria-hidden="true">News</p>
    <h1 class="phero__title" id="ph-title">ニュース・コラム</h1>
    <p class="phero__lead">AI検索・AIデータ権利・技術解説のコラムを中心に、Trillion Bankの取り組みをお届けします。</p>
  </div>
</section>

<section class="nl" aria-label="記事の一覧">
  <div class="nl__inner">
    <div class="nfeat" aria-roledescription="カルーセル" aria-label="新着の記事">
      <ul class="nfeat__list">
        {slides}
      </ul>
      <div class="nfeat__nav">{dots}</div>
    </div>

    <div class="nfilter" role="group" aria-label="記事を絞り込む">
      <div class="nfilter__row">{pill('year', 'all', 'All', True)}{''.join(pill('year', y, y + '年') for y in years)}</div>
      <div class="nfilter__row">{pill('cat', 'all', 'All', True)}{''.join(pill('cat', c, c) for c in cats)}</div>
      <p class="nfilter__status" aria-live="polite">{len(arts)}件</p>
    </div>

    <ul class="nlist">
        {chr(10).join(card(a) for a in arts)}
    </ul>
  </div>
</section>

{{{{contact}}}}'''
    return page('ニュース・コラム｜株式会社Trillion Bank', 'Trillion Bankのニュースと、AI検索・AIデータ権利・用語集などのコラムです。', 'news', body)


def article_page(a, arts):
    body_html, toc = md(a['body_md'])
    toc_html = ''.join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t in toc)
    others = [x for x in arts if x is not a][:3]
    url_abs = f"https://trillion-bank-inc.github.io/trillion-bank-demo-lp/{a['url']}"
    share = (f'<a class="ashare__btn" href="https://x.com/intent/post?url={E(url_abs)}&amp;text={E(a["title"])}" target="_blank" rel="noopener noreferrer"><span>X</span><span class="sr">（新しいタブで開きます）</span></a>'
             f'<a class="ashare__btn" href="https://www.facebook.com/sharer/sharer.php?u={E(url_abs)}" target="_blank" rel="noopener noreferrer"><span>Facebook</span><span class="sr">（新しいタブで開きます）</span></a>'
             f'<button type="button" class="ashare__btn" data-copy="{E(url_abs)}"><span>リンクをコピー</span></button>')
    body = f'''<article class="art" aria-labelledby="art-title">
  <div class="art__inner">
    <p class="art__back"><a href="news.html"><i aria-hidden="true"></i>News</a></p>
    <h1 class="art__title" id="art-title">{E(a['title'])}</h1>
    <p class="art__meta"><span class="nlc__tag">{E(a['category'])}</span><time datetime="{a['date']}">{ymd(a['date'])}</time></p>
    {bp.crumbs('News|news.html;' + a['title'])}
    <figure class="art__cover"><img src="{a['img']}" alt="" width="1200" height="750"></figure>
    {f'<nav class="art__toc" aria-label="この記事の目次"><p>目次</p><ol>{toc_html}</ol></nav>' if len(toc) > 1 else ''}
    <div class="art__body">
{body_html}
    </div>
    <div class="ashare"><p class="ashare__h">Share On</p><div class="ashare__btns">{share}</div></div>
  </div>
</article>

<section class="nl nl--more" aria-labelledby="more-title">
  <div class="nl__inner">
    <h2 class="sec-h" id="more-title"><span class="sec-h__en" aria-hidden="true">More News</span><span class="sec-h__ja">ほかの記事</span></h2>
    <ul class="nlist">
        {chr(10).join(card(x) for x in others)}
    </ul>
    <p class="nl__all"><a class="pill pill--blue" href="news.html">記事の一覧へ</a></p>
  </div>
</section>

{{{{contact}}}}'''
    head = (f'<meta property="og:type" content="article">\n<meta property="og:title" content="{E(a["title"])}">\n'
            f'<meta property="og:description" content="{E(a["description"])}">\n<link rel="canonical" href="{E(url_abs)}">\n')
    return page(f"{a['title']}｜Trillion Bank", a['description'], 'news', body, head)


def main():
    arts = [parse(p) for p in glob.glob(P('content', 'news', '*.md')) if not os.path.basename(p).startswith('_')]
    arts.sort(key=lambda a: (a['date'], a['slug']), reverse=True)
    if not arts:
        raise SystemExit('記事がありません')
    contact = '<!-- SITE:contact -->\n<!-- /SITE:contact -->'
    for a in arts:
        if not a.get('image'):
            open(P('assets', 'news', a['slug'] + '.svg'), 'w', encoding='utf-8').write(cover_svg(a))
        out = article_page(a, arts).replace('{{contact}}', '')
        open(P(a['url']), 'w', encoding='utf-8').write(bp.fill_markers(out.replace('<!-- SITE:contact -->\n<!-- /SITE:contact -->\n</main>', contact + '\n</main>'), 'news'))
    out = list_page(arts).replace('{{contact}}', '')
    open(P('news.html'), 'w', encoding='utf-8').write(bp.fill_markers(out, 'news'))
    # トップの「News」：新しい4件
    idx = open(P('index.html'), encoding='utf-8').read()
    cards = '\n'.join(f'''        <li class="reveal"><a class="ncard" href="{a['url']}" data-cursor="Read">
          <span class="ncard__img ncard__img--photo" aria-hidden="true"><img src="{a['img']}" alt="" width="1200" height="750" loading="lazy" decoding="async"></span>
          <span class="ncard__row"><span class="tag tag--blue">{E(a['category'])}</span><time datetime="{a['date']}">{ymd(a['date'])}</time></span>
          <h3>{E(a['title'])}</h3>
        </a></li>''' for a in arts[:4])
    idx, n = re.subn(r'(<ul class="ncards">\n).*?(\n\s*</ul>)', lambda m: m.group(1) + cards + m.group(2), idx, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('index.html に <ul class="ncards"> が見つかりません')
    idx = re.sub(r'(<a class="more" href=")[^"]*("[^>]*>すべて見る)', r'\1news.html\2', idx)
    open(P('index.html'), 'w', encoding='utf-8').write(idx)
    print(f'ニュース：{len(arts)}件（news.html・記事のページ・トップの4件を更新）')


if __name__ == '__main__':
    main()
