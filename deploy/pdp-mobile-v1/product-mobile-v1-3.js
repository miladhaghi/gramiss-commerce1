/* GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_3 */
(() => {
  'use strict';
  const mq = window.matchMedia('(max-width: 760px)');
  if (!mq.matches || !document.body.classList.contains('single-product')) return;
  const section = document.querySelector('.related.products') || document.querySelector('section.related');
  if (!section || section.dataset.g1StyleReady === '1') return;
  const rail = section.querySelector('ul.products');
  if (!rail) return;
  section.dataset.g1StyleReady = '1';
  section.classList.add('g1-style-intelligence');

  const nativeCards = Array.from(rail.querySelectorAll(':scope > li.product')).map((li, index) => {
    const link = li.querySelector('a.woocommerce-LoopProduct-link, a[href]');
    const img = li.querySelector('img');
    const title = li.querySelector('.woocommerce-loop-product__title, h2, h3');
    const price = li.querySelector('.price');
    return { id: li.className.match(/post-(\d+)/)?.[1] || `native-${index}`, name: title?.textContent?.trim() || 'انتخاب پیشنهادی', href: link?.href || '#', image: img?.currentSrc || img?.src || '', priceText: price?.textContent?.replace(/\s+/g, ' ').trim() || '', kind: 'alternate', source: 'native' };
  }).filter(item => item.href && item.image);

  const currentId = Number(document.body.className.match(/postid-(\d+)/)?.[1] || 0);
  const bodyClasses = document.body.className.toLowerCase();
  const kinds = {
    pants: { aliases: ['pants', 'trouser', 'shalvar', 'شلوار'], tag: 'تعادل فرم', reason: 'حجم پایین‌تنه، فرم بالاتنه را کامل می‌کند.' },
    shoes: { aliases: ['sneaker', 'shoe', 'katooni', 'کتونی', 'کتانی', 'کفش'], tag: 'اتصال استایل', reason: 'وزن بصری استایل را از بالا تا پایین یکدست می‌کند.' },
    cap: { aliases: ['cap', 'hat', 'کلاه'], tag: 'جزئیات نهایی', reason: 'یک نقطه‌ی تأکید بدون شلوغ کردن ترکیب اضافه می‌کند.' },
    bag: { aliases: ['bag', 'کیف'], tag: 'کاربرد + فرم', reason: 'جزئیات کاربردی را بدون شکستن حال‌وهوای استایل اضافه می‌کند.' },
    top: { aliases: ['tshirt', 't-shirt', 'shirt', 'tee', 'تیشرت', 'پیراهن'], tag: 'لایه‌ی اصلی', reason: 'تناسب رنگ و فرم را در بالاتنه حفظ می‌کند.' },
    alternate: { aliases: [], tag: 'گزینه جایگزین', reason: 'همان حال‌وهوا را با بیان متفاوت ادامه می‌دهد.' }
  };
  const inferCurrentKind = () => Object.entries(kinds).find(([key, value]) => key !== 'alternate' && value.aliases.some(a => bodyClasses.includes(a)))?.[0] || 'top';
  const currentKind = inferCurrentKind();
  const priorityByCurrent = { top: ['pants', 'shoes', 'cap', 'bag'], pants: ['top', 'shoes', 'cap', 'bag'], shoes: ['pants', 'top', 'cap', 'bag'], cap: ['top', 'pants', 'shoes', 'bag'], bag: ['top', 'pants', 'shoes', 'cap'] };
  const desiredKinds = priorityByCurrent[currentKind] || priorityByCurrent.top;

  const existingHeading = section.querySelector(':scope > h2, :scope > .g3-related-heading, h2');
  if (existingHeading) existingHeading.textContent = 'استایل پیشنهادی';
  if (!section.querySelector('.g1-style-intro')) {
    const intro = document.createElement('div');
    intro.className = 'g1-style-intro';
    intro.innerHTML = `<div class="g1-style-intro__eyebrow">GRAMISS / STYLE LOGIC</div><p class="g1-style-intro__copy">انتخاب‌هایی که فرم، رنگ و حال‌وهوای این آیتم را کامل می‌کنند.</p><div class="g1-style-intro__progress" aria-hidden="true"><span>01</span><i></i><span>${String(Math.max(nativeCards.length, 4)).padStart(2, '0')}</span></div>`;
    (existingHeading || section.firstElementChild)?.after(intro);
  }

  const money = (product) => {
    const p = product?.prices;
    if (!p || p.price == null) return '';
    const n = Number(p.price);
    if (!Number.isFinite(n)) return '';
    const formatted = Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `${formatted}${p.currency_symbol || ' تومان'}`;
  };
  const categoryKind = (cat) => {
    const hay = `${cat?.slug || ''} ${cat?.name || ''}`.toLowerCase();
    return Object.entries(kinds).find(([key, value]) => key !== 'alternate' && value.aliases.some(a => hay.includes(a)))?.[0] || 'alternate';
  };
  const storeBase = `${location.origin}/wp-json/wc/store/v1`;
  const fetchJSON = async (url) => {
    const res = await fetch(url, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };
  const loadStylingProducts = async () => {
    try {
      const categories = await fetchJSON(`${storeBase}/products/categories?per_page=100`);
      const chosen = [];
      for (const kind of desiredKinds) {
        const cat = categories.find(c => categoryKind(c) === kind && Number(c.count || 0) > 0);
        if (!cat) continue;
        const products = await fetchJSON(`${storeBase}/products?category=${encodeURIComponent(cat.id)}&per_page=6&orderby=date&order=desc`);
        const product = products.find(p => Number(p.id) !== currentId && p.is_purchasable !== false && p.images?.[0]?.src);
        if (!product) continue;
        chosen.push({ id: String(product.id), name: product.name, href: product.permalink, image: product.images[0].src, priceText: money(product), kind, source: 'store' });
      }
      return chosen;
    } catch (err) {
      console.info('[Gramiss Style Logic] Store API fallback:', err?.message || err);
      return [];
    }
  };

  const selectedKey = 'gramiss_style_selection_v1';
  const readSelected = () => { try { return JSON.parse(localStorage.getItem(selectedKey) || '[]'); } catch { return []; } };
  const writeSelected = (items) => localStorage.setItem(selectedKey, JSON.stringify(items.slice(0, 8)));

  const buildCard = (item, index) => {
    const meta = kinds[item.kind] || kinds.alternate;
    const li = document.createElement('li');
    li.className = 'product g1-style-card';
    li.dataset.productId = item.id;
    li.dataset.styleKind = item.kind;
    const link = document.createElement('a');
    link.className = 'g1-style-card__link';
    link.href = item.href;
    link.setAttribute('aria-label', `مشاهده ${item.name}`);
    const media = document.createElement('div'); media.className = 'g1-style-card__media';
    const img = document.createElement('img'); img.src = item.image; img.alt = item.name; img.loading = index < 2 ? 'eager' : 'lazy'; img.decoding = 'async'; media.append(img);
    const body = document.createElement('div'); body.className = 'g1-style-card__body';
    const metaLine = document.createElement('div'); metaLine.className = 'g1-style-card__meta'; metaLine.textContent = `${String(index + 1).padStart(2, '0')} / ${meta.tag}`;
    const title = document.createElement('h3'); title.className = 'g1-style-card__title'; title.textContent = item.name;
    const price = document.createElement('div'); price.className = 'g1-style-card__price'; price.textContent = item.priceText || 'مشاهده محصول';
    const reason = document.createElement('p'); reason.className = 'g1-style-card__reason'; reason.textContent = meta.reason;
    body.append(metaLine, title, price, reason); link.append(media, body);
    const action = document.createElement('button'); action.type = 'button'; action.className = 'g1-style-card__add'; action.setAttribute('aria-pressed', 'false'); action.innerHTML = '<span class="g1-style-card__add-label">اضافه به استایل</span><span class="g1-style-card__add-orb" aria-hidden="true">+</span>'; action._g1Item = item;
    li.append(link, action); return li;
  };

  const ensureTray = () => {
    let tray = section.querySelector('.g1-style-tray'); if (tray) return tray;
    tray = document.createElement('div'); tray.className = 'g1-style-tray'; tray.hidden = true;
    tray.innerHTML = '<span class="g1-style-tray__count"></span><button type="button" class="g1-style-tray__open">مرور انتخاب‌ها <span aria-hidden="true">↗</span></button>';
    section.append(tray); return tray;
  };
  const ensureSheet = () => {
    let sheet = document.querySelector('.g1-style-sheet'); if (sheet) return sheet;
    sheet = document.createElement('div'); sheet.className = 'g1-style-sheet'; sheet.hidden = true;
    sheet.innerHTML = `<div class="g1-style-sheet__backdrop" data-g1-close-style></div><section class="g1-style-sheet__panel" role="dialog" aria-modal="true" aria-label="استایل شما"><div class="g1-style-sheet__handle"></div><header><div><small>GRAMISS / YOUR STYLE</small><h2>استایل شما</h2></div><button type="button" data-g1-close-style aria-label="بستن">×</button></header><div class="g1-style-sheet__items"></div></section>`;
    document.body.append(sheet);
    sheet.addEventListener('click', event => { if (event.target.closest('[data-g1-close-style]')) closeSheet(); });
    return sheet;
  };
  const tray = ensureTray(); const sheet = ensureSheet();

  const refreshSelectionUI = () => {
    const selected = readSelected();
    rail.querySelectorAll('.g1-style-card__add').forEach(btn => {
      const active = selected.some(x => String(x.id) === String(btn._g1Item?.id));
      btn.classList.toggle('is-selected', active); btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      const label = btn.querySelector('.g1-style-card__add-label'); const orb = btn.querySelector('.g1-style-card__add-orb');
      if (label) label.textContent = active ? 'به استایل اضافه شد' : 'اضافه به استایل'; if (orb) orb.textContent = active ? '✓' : '+';
    });
    tray.hidden = selected.length === 0;
    const count = tray.querySelector('.g1-style-tray__count'); if (count) count.textContent = `استایل شما · ${selected.length} انتخاب`;
  };
  const renderSheet = () => {
    const selected = readSelected(); const host = sheet.querySelector('.g1-style-sheet__items'); host.innerHTML = '';
    selected.forEach(item => {
      const row = document.createElement('article'); row.className = 'g1-style-sheet__item';
      row.innerHTML = `<img src="${item.image}" alt=""><div><strong></strong><small></small></div><a>مشاهده</a><button type="button" aria-label="حذف">×</button>`;
      row.querySelector('strong').textContent = item.name; row.querySelector('small').textContent = (kinds[item.kind] || kinds.alternate).tag; row.querySelector('a').href = item.href;
      row.querySelector('button').addEventListener('click', () => { writeSelected(readSelected().filter(x => String(x.id) !== String(item.id))); renderSheet(); refreshSelectionUI(); });
      host.append(row);
    });
  };
  const openSheet = () => { renderSheet(); sheet.hidden = false; requestAnimationFrame(() => sheet.classList.add('is-open')); document.body.classList.add('g1-style-sheet-open'); };
  const closeSheet = () => { sheet.classList.remove('is-open'); document.body.classList.remove('g1-style-sheet-open'); setTimeout(() => { sheet.hidden = true; }, 260); };
  tray.querySelector('.g1-style-tray__open')?.addEventListener('click', openSheet);
  rail.addEventListener('click', event => {
    const btn = event.target.closest('.g1-style-card__add'); if (!btn) return; event.preventDefault();
    const item = btn._g1Item; if (!item) return; const selected = readSelected(); const exists = selected.some(x => String(x.id) === String(item.id));
    writeSelected(exists ? selected.filter(x => String(x.id) !== String(item.id)) : [...selected, item]); refreshSelectionUI(); if (!exists && navigator.vibrate) navigator.vibrate(12);
  });

  const render = (items) => {
    const merged = [...items];
    for (const native of nativeCards) { if (merged.length >= 5) break; if (!merged.some(x => x.href === native.href)) merged.push(native); }
    if (!merged.length) return;
    rail.innerHTML = ''; merged.slice(0, 5).forEach((item, index) => rail.append(buildCard(item, index)));
    const end = section.querySelector('.g1-style-intro__progress span:last-child'); if (end) end.textContent = String(Math.min(merged.length, 5)).padStart(2, '0'); refreshSelectionUI();
  };
  render(nativeCards);
  loadStylingProducts().then(items => { if (items.length >= 2) render(items); });

  const progress = section.querySelector('.g1-style-intro__progress i');
  const updateProgress = () => { const max = Math.max(1, rail.scrollWidth - rail.clientWidth); const value = Math.max(0, Math.min(1, Math.abs(rail.scrollLeft) / max)); progress?.style.setProperty('--g1-progress', `${Math.max(12, value * 100)}%`); };
  rail.addEventListener('scroll', updateProgress, { passive: true }); requestAnimationFrame(updateProgress);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => { document.body.classList.toggle('g1-style-zone-active', entries.some(e => e.isIntersecting && e.intersectionRatio > 0.12)); }, { threshold: [0, .12, .3], rootMargin: '0px 0px -8% 0px' });
    observer.observe(section);
  }
})();
