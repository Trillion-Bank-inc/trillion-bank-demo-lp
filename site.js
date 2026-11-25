/* =========================================================================
   site.js：複数ページで共通の小さな動き
   ========================================================================= */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // 下からふわっと現れる（同じ並びの中で少しずつ遅らせる）
  const items = Array.from(document.querySelectorAll('.pair__card, .flow4__list li, .price__list li, .cant__list li, .values__list li, .profile2__dl > div, .toll__steps li, .ppc__kinds li, .git__o, .git__text, .band-link__inner > *, .phero__actions .orb, .chips li'));
  if (!reduce && 'IntersectionObserver' in window) {
    items.forEach((el) => {
      const sibs = Array.from(el.parentElement.children);
      el.style.setProperty('--rd', `${Math.min(sibs.indexOf(el), 6) * 0.08}s`);
      el.classList.add('rv');
    });
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }), { threshold: 0.15 });
    items.forEach((el) => io.observe(el));
    const share = document.querySelector('.share');
    if (share) {
      const io2 = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { share.classList.add('is-in'); io2.disconnect(); } }), { threshold: 0.3 });
      io2.observe(share);
    }
  } else {
    const share = document.querySelector('.share');
    if (share) share.classList.add('is-in');
  }
})();

/* Adctor の構造図：画面に入ると、番号の順に矢印が伸び、記録の件数が増えていく */
(() => {
  const fig = document.querySelector('.pfm__fig');
  if (!fig) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) { fig.classList.add('is-on'); return; }
  const n = fig.querySelector('.pfm__count em');
  let c = 1248; let t = 0;
  new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) {
      fig.classList.add('is-on');
      if (!t) t = setInterval(() => { c += 1; n.textContent = c.toLocaleString('ja-JP'); }, 900);
    } else if (t) { clearInterval(t); t = 0; }
  }), { threshold: 0.3 }).observe(fig);
})();

/* カード全体を押せるように（写真・名前・説明のどこを押しても、詳しい内容が開く） */
(() => {
  const wire = (cardSel, targetSel) => {
    document.querySelectorAll(cardSel).forEach((card) => {
      const target = card.querySelector(targetSel);
      if (!target) return;
      card.classList.add('is-clickable');
      card.addEventListener('click', (e) => {
        if (e.target.closest('a, button') || window.getSelection().toString()) return;
        target.click();
      });
    });
  };
  wire('.has-dialog .lead__card', '.lead__open');
  wire('.uc__card', '.uc__cta');
})();

/* News：新着の切り替え・年と分類の絞り込み・リンクのコピー */
(() => {
  const feat = document.querySelector('.nfeat');
  if (feat) {
    const slides = Array.from(feat.querySelectorAll('.nfeat__slide'));
    const dots = Array.from(feat.querySelectorAll('.nfeat__dot'));
    let cur = 0; let t = 0;
    const go = (i) => {
      cur = (i + slides.length) % slides.length;
      slides.forEach((s, k) => { s.classList.toggle('is-on', k === cur); s.setAttribute('aria-hidden', String(k !== cur)); });
      dots.forEach((d, k) => d.classList.toggle('is-on', k === cur));
    };
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const start = () => { if (!reduce && slides.length > 1 && !t) t = setInterval(() => go(cur + 1), 5000); };
    const stop = () => { clearInterval(t); t = 0; };
    dots.forEach((d, k) => d.addEventListener('click', () => { stop(); go(k); }));
    feat.addEventListener('pointerenter', stop);
    feat.addEventListener('pointerleave', start);
    feat.addEventListener('focusin', stop);
    go(0); start();
  }
  const filter = document.querySelector('.nfilter');
  if (filter) {
    const cards = Array.from(document.querySelectorAll('.nlist .nlc'));
    const status = filter.querySelector('.nfilter__status');
    const state = { year: 'all', cat: 'all' };
    const apply = () => {
      let n = 0;
      cards.forEach((c) => {
        const show = (state.year === 'all' || c.dataset.year === state.year) && (state.cat === 'all' || c.dataset.cat === state.cat);
        c.hidden = !show; if (show) n += 1;
      });
      status.textContent = n ? `${n}件` : '該当する記事はありません';
    };
    filter.querySelectorAll('.npill').forEach((b) => b.addEventListener('click', () => {
      const key = b.dataset.year !== undefined ? 'year' : 'cat';
      state[key] = b.dataset[key];
      filter.querySelectorAll(`.npill[data-${key}]`).forEach((x) => { const on = x === b; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', String(on)); });
      apply();
    }));
  }
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const label = b.querySelector('span');
    try { await navigator.clipboard.writeText(b.dataset.copy); label.textContent = 'コピーしました'; } catch (e) { label.textContent = b.dataset.copy; }
    setTimeout(() => { label.textContent = 'リンクをコピー'; }, 2200);
  }));
})();

/* 押したときの波紋（押した場所から広がる） */
(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const SEL = '.orb, .pill, .uc__cta, .ab__links a, .price__list a, .cov__pill, .npill, .ashare__btn, .nfeat__dot, .pair__card, .crumbs a, .ucx__index a';
  document.querySelectorAll(SEL).forEach((el) => el.classList.add('rip-host'));
  document.addEventListener('pointerdown', (e) => {
    const host = e.target.closest && e.target.closest('.rip-host');
    if (!host) return;
    const r = host.getBoundingClientRect();
    const d = Math.hypot(Math.max(e.clientX - r.left, r.right - e.clientX), Math.max(e.clientY - r.top, r.bottom - e.clientY)) * 2;
    const s = document.createElement('span');
    s.className = 'rip';
    s.style.cssText = `left:${e.clientX - r.left}px;top:${e.clientY - r.top}px;width:${d}px;height:${d}px`;
    host.appendChild(s);
    setTimeout(() => s.remove(), 700);
  });
})();
