/* GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_4 */
(() => {
  'use strict';
  const mq = window.matchMedia('(max-width: 760px)');
  if (!mq.matches || !document.body.classList.contains('single-product')) return;

  const section = document.querySelector('.related.products') || document.querySelector('section.related');
  if (!section) return;
  const rail = section.querySelector('ul.products');
  if (!rail) return;

  section.classList.add('g1-style-intelligence');
  section.dataset.g1StyleV14 = '1';

  const currentId = Number(document.body.className.match(/postid-(\d+)/)?.[1] || 0);
  const selectedKey = 'gramiss_style_selection_v1';
  const readSelected = () => { try { return JSON.parse(localStorage.getItem(selectedKey) || '[]'); } catch { return []; } };

  const curatedByProduct = {
    392: [
      { id: 284, kind: 'pants', meta: '01 / تعادل فرم', tag: 'تعادل فرم', reason: 'حجم بگ ذغالی، فرم باکسی تیشرت را کامل می‌کند و وزن استایل را پایین می‌آورد.' },
      { id: 435, kind: 'shoes', meta: '02 / اتصال استایل', tag: 'اتصال استایل', reason: 'کتونی حجیم، نسبت شلوار بگ و بالاتنه آزاد را به یک ترکیب منسجم تبدیل می‌کند.' },
      { id: 366, kind: 'pants-alt', meta: '03 / نسخه تمیزتر', tag: 'نسخه تمیزتر', reason: 'اگر استایل آرام‌تر می‌خواهی، افت نرم این شلوار همان فرم آزاد را با بیان مینیمال‌تری ادامه می‌دهد.' },
      { id: 403, kind: 'shoes-alt', meta: '04 / پایان مینیمال', tag: 'پایان مینیمال', reason: 'فرم تمیزتر کتونی، استایل را سبک‌تر می‌کند بدون اینکه تعادل کلی ترکیب از بین برود.' }
    ]
  };

  const nativeFallback = Array.from(rail.querySelectorAll(':scope > li.product')).map((li, index) => {
    const link = li.querySelector('a.woocommerce-LoopProduct-link, a[href]');
    const img = li.querySelector('img');
    const title = li.querySelector('.woocommerce-loop-product__title, h2, h3');
    const price = li.querySelector('.price');
    return {
      id: li.className.match(/post-(\d+)/)?.[1] || `native-${index}`,
      name: title?.textContent?.trim() || 'انتخاب پیشنهادی',
      href: link?.href || '#',
      image: img?.currentSrc || img?.src || '',
      priceText: price?.textContent?.replace(/\s+/g, ' ').trim() || '',
      kind: 'alternate',
      meta: `${String(index + 1).padStart(2,'0')} / گزینه جایگزین`,
      tag: 'گزینه جایگزین',
      reason: 'همان حال‌وهوا را با بیان متفاوت ادامه می‌دهد.'
    };
  }).filter(item => item.href && item.image);

  const cleanTitle = text => (text || '').replace(/\s*[|–-]\s*Gramiss.*$/i,'').trim();
  const hydrateFromProductPage = async spec => {
    const res = await fetch(`${location.origin}/?p=${spec.id}&g1_style_logic=1`, {
      credentials: 'same-origin',
      headers: { Accept: 'text/html', 'Cache-Control': 'no-cache' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const bodyClass = doc.body?.className || '';
    if (!bodyClass.includes(`postid-${spec.id}`)) throw new Error('product page marker missing');

    const title = cleanTitle(
      doc.querySelector('h1.product_title, .g2-pdp-title, .summary h1')?.textContent ||
      doc.querySelector('meta[property="og:title"]')?.content || ''
    );
    const image =
      doc.querySelector('meta[property="og:image"]')?.content ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.getAttribute('data-large_image') ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.src || '';
    const href =
      doc.querySelector('link[rel="canonical"]')?.href ||
      doc.querySelector('meta[property="og:url"]')?.content ||
      `${location.origin}/?p=${spec.id}`;
    const priceText = (
      doc.querySelector('.summary .price, .g2-pdp-price, .woocommerce-Price-amount')?.textContent || ''
    ).replace(/\s+/g,' ').trim();

    if (!title || !image) throw new Error('product data incomplete');
    return { ...spec, id: String(spec.id), name: title, href, image, priceText: priceText || 'مشاهده محصول' };
  };

  const hydrateCurated = async specs => {
    const settled = await Promise.allSettled(specs.map(hydrateFromProductPage));
    return settled.flatMap((result, index) => {
      if (result.status === 'fulfilled') return [result.value];
      console.info('[Gramiss Style Logic v1.4] curated page unavailable', specs[index]?.id, result.reason?.message || result.reason);
      return [];
    });
  };

  const heading = section.querySelector(':scope > h2, :scope > .g3-related-heading, h2');
  if (heading) heading.textContent = 'استایل پیشنهادی';

  let intro = section.querySelector('.g1-style-intro');
  if (!intro) {
    intro = document.createElement('div');
    intro.className = 'g1-style-intro';
    (heading || section.firstElementChild)?.after(intro);
  }
  intro.innerHTML = `<div class="g1-style-intro__eyebrow">GRAMISS / STYLE LOGIC</div><p class="g1-style-intro__copy">انتخاب‌هایی که فرم، رنگ و حال‌وهوای این آیتم را کامل می‌کنند.</p><div class="g1-style-intro__progress" aria-hidden="true"><span>01</span><i></i><span>04</span></div>`;

  let hint = section.querySelector('.g1-style-swipe-hint');
  if (!hint) {
    hint = document.createElement('p');
    hint.className = 'g1-style-swipe-hint';
    hint.textContent = 'برای دیدن انتخاب بعدی، کارت‌ها را بکش.';
    rail.after(hint);
  }

  const buildCard = (item, index) => {
    const li = document.createElement('li');
    li.className = 'product g1-style-card';
    li.dataset.productId = item.id;
    li.dataset.styleKind = item.kind || 'alternate';
    li.dataset.g1V14 = '1';

    const link = document.createElement('a');
    link.className = 'g1-style-card__link';
    link.href = item.href;
    link.setAttribute('aria-label', `مشاهده ${item.name}`);

    const media = document.createElement('div');
    media.className = 'g1-style-card__media';
    const img = document.createElement('img');
    img.src = item.image;
    img.alt = item.name;
    img.loading = index === 0 ? 'eager' : 'lazy';
    img.decoding = 'async';
    media.append(img);

    const body = document.createElement('div');
    body.className = 'g1-style-card__body';
    const meta = document.createElement('div');
    meta.className = 'g1-style-card__meta';
    meta.textContent = item.meta || `${String(index + 1).padStart(2,'0')} / انتخاب پیشنهادی`;
    const title = document.createElement('h3');
    title.className = 'g1-style-card__title';
    title.textContent = item.name;
    const price = document.createElement('div');
    price.className = 'g1-style-card__price';
    price.textContent = item.priceText || 'مشاهده محصول';
    const reason = document.createElement('p');
    reason.className = 'g1-style-card__reason';
    reason.innerHTML = `<b>${item.tag || 'چرا این انتخاب؟'}</b><span></span>`;
    reason.querySelector('span').textContent = item.reason || 'این انتخاب با فرم و حال‌وهوای محصول اصلی هماهنگ است.';
    body.append(meta, title, price, reason);
    link.append(media, body);

    const action = document.createElement('button');
    action.type = 'button';
    action.className = 'g1-style-card__add';
    action.setAttribute('aria-pressed', 'false');
    action.innerHTML = '<span class="g1-style-card__add-label">اضافه به استایل</span><span class="g1-style-card__add-orb" aria-hidden="true">+</span>';
    action._g1Item = item;

    const selected = readSelected().some(x => String(x.id) === String(item.id));
    if (selected) {
      action.classList.add('is-selected');
      action.setAttribute('aria-pressed','true');
      action.querySelector('.g1-style-card__add-label').textContent = 'به استایل اضافه شد';
      action.querySelector('.g1-style-card__add-orb').textContent = '✓';
    }

    li.append(link, action);
    return li;
  };

  const hardenRail = () => {
    rail.style.setProperty('display','flex','important');
    rail.style.setProperty('grid-template-columns','none','important');
    rail.style.setProperty('flex-flow','row nowrap','important');
    rail.style.setProperty('gap','14px','important');
    rail.style.setProperty('overflow-x','auto','important');
    rail.style.setProperty('overflow-y','hidden','important');
    rail.style.setProperty('direction','ltr','important');
    rail.style.setProperty('scroll-snap-type','x mandatory','important');
    Array.from(rail.children).forEach(card => {
      card.style.setProperty('float','none','important');
      card.style.setProperty('clear','none','important');
      card.style.setProperty('display','block','important');
      card.style.setProperty('flex','0 0 calc(100vw - 74px)','important');
      card.style.setProperty('width','calc(100vw - 74px)','important');
      card.style.setProperty('min-width','calc(100vw - 74px)','important');
      card.style.setProperty('max-width','340px','important');
      card.style.setProperty('scroll-snap-align','start','important');
      card.style.setProperty('direction','rtl','important');
    });
  };

  let applying = false;
  let activeItems = [];
  const applyItems = items => {
    if (!items?.length) return;
    applying = true;
    activeItems = items.slice(0,4);
    rail.innerHTML = '';
    activeItems.forEach((item,index) => rail.append(buildCard(item,index)));
    hardenRail();
    const last = intro.querySelector('.g1-style-intro__progress span:last-child');
    if (last) last.textContent = String(activeItems.length).padStart(2,'0');
    applying = false;
  };

  const baseItems = nativeFallback.slice(0,4);
  if (baseItems.length) applyItems(baseItems);

  const specs = curatedByProduct[currentId] || [];
  if (specs.length) {
    hydrateCurated(specs).then(items => {
      if (items.length >= 2) {
        while (items.length < 4 && nativeFallback.length) {
          const next = nativeFallback.find(n => !items.some(i => String(i.id) === String(n.id)));
          if (!next) break;
          items.push(next);
        }
        applyItems(items);
      }
    });
  }

  const observer = new MutationObserver(() => {
    if (applying || !activeItems.length) return;
    const valid = rail.children.length === activeItems.length && Array.from(rail.children).every(el => el.dataset.g1V14 === '1');
    if (!valid) setTimeout(() => applyItems(activeItems), 0);
    else hardenRail();
  });
  observer.observe(rail, { childList: true });

  const progressLine = intro.querySelector('.g1-style-intro__progress i');
  const currentLabel = intro.querySelector('.g1-style-intro__progress span:first-child');
  let raf = 0;
  const updateProgress = () => {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      const cards = Array.from(rail.querySelectorAll('.g1-style-card'));
      if (!cards.length) return;
      const step = (cards[0].getBoundingClientRect().width || 1) + 14;
      const index = Math.max(0, Math.min(cards.length - 1, Math.round(rail.scrollLeft / step)));
      if (currentLabel) currentLabel.textContent = String(index + 1).padStart(2,'0');
      progressLine?.style.setProperty('--g1-progress', `${((index + 1) / cards.length) * 100}%`);
    });
  };
  rail.addEventListener('scroll', updateProgress, { passive: true });
  requestAnimationFrame(updateProgress);
})();
