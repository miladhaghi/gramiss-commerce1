/* GRAMISS_CART_MOBILE_V2 */
(() => {
  'use strict';

  if (!window.matchMedia('(max-width:760px)').matches) return;
  if (!document.body.classList.contains('woocommerce-cart')) return;

  const body = document.body;
  const woo = document.querySelector('.woocommerce');
  if (!woo) return;

  body.classList.remove('g1-cart-mobile-v1', 'g1-cart-is-empty');
  body.classList.add('g2-cart-mobile-v2');

  let couponOpen = false;
  let updateTimer = 0;
  let stickyObserver = null;
  let stickyState = { cta: false, footer: false };

  const q = (sel, root = document) => root.querySelector(sel);
  const qa = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const clean = value => String(value || '').replace(/\s+/g, ' ').trim();
  const faNum = value => String(value).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
  const rowSelector = 'tr.woocommerce-cart-form__cart-item, tr.cart_item';
  const getRows = () => qa(rowSelector, woo);

  const getShopUrl = () => {
    const native = q('.return-to-shop a, .gramiss-cart-continue', woo);
    if (native?.href) return native.href;
    if (window.gramissV1?.shopUrl) return window.gramissV1.shopUrl;
    const headerShop = q('a[href*="page_id=9"], a[href*="/shop/"]');
    return headerShop?.href || `${location.origin}/?page_id=9`;
  };

  const getCheckoutUrl = () => {
    const link = q('.wc-proceed-to-checkout a.checkout-button, a.checkout-button', woo);
    return link?.href || `${location.origin}/?page_id=11`;
  };

  const getTotal = () => clean(
    q('.cart_totals .order-total .amount', woo)?.textContent ||
    q('.cart_totals .cart-subtotal .amount', woo)?.textContent ||
    q('.product-subtotal .amount', woo)?.textContent ||
    ''
  );

  const getSubtotal = () => clean(
    q('.cart_totals .cart-subtotal .amount', woo)?.textContent ||
    q('.product-subtotal .amount', woo)?.textContent ||
    getTotal()
  );

  const getShipping = () => {
    const methods = qa('.woocommerce-shipping-methods label', woo).map(el => clean(el.textContent)).filter(Boolean);
    if (methods.length) {
      const free = methods.find(text => /رایگان|free/i.test(text));
      return free || methods[0];
    }
    const cell = q('.woocommerce-shipping-totals td, tr.shipping td', woo);
    const text = clean(cell?.textContent);
    if (!text) return 'در مرحله بعد محاسبه می‌شود';
    if (/رایگان|free/i.test(text)) return 'رایگان';
    return text.length > 70 ? 'در مرحله بعد محاسبه می‌شود' : text;
  };

  const getCount = rows => rows.reduce((sum, row) => {
    const input = q('input.qty', row);
    const n = Number(input?.value || 1);
    return sum + (Number.isFinite(n) ? n : 1);
  }, 0);

  const extractVariations = row => {
    const dl = q('dl.variation', row);
    if (!dl) return [];
    const dts = qa('dt', dl);
    const dds = qa('dd', dl);
    const pairs = [];
    const length = Math.max(dts.length, dds.length);
    for (let i = 0; i < length; i += 1) {
      const label = clean(dts[i]?.textContent).replace(/[:：]+$/g, '');
      const value = clean(dds[i]?.textContent);
      if (!label && !value) continue;
      pairs.push(label && value ? `${label}: ${value}` : (value || label));
    }
    return pairs;
  };

  const extractRow = (row, index) => {
    const titleLink = q('td.product-name > a, .product-name a', row);
    const image = q('.product-thumbnail img', row);
    const qty = q('input.qty', row);
    const remove = q('.product-remove a.remove', row);
    const stock = clean(q('.gramiss-cart-stock', row)?.textContent) || 'موجود در انبار';
    return {
      index,
      row,
      title: clean(titleLink?.textContent) || 'محصول Gramiss',
      href: titleLink?.href || '#',
      image: image?.currentSrc || image?.src || '',
      imageAlt: image?.alt || clean(titleLink?.textContent) || 'محصول',
      variations: extractVariations(row),
      stock,
      unitPrice: clean(q('.product-price .amount', row)?.textContent || q('.product-price', row)?.textContent),
      lineTotal: clean(q('.product-subtotal .amount', row)?.textContent || q('.product-subtotal', row)?.textContent),
      qty,
      remove
    };
  };

  const removeLegacyNodes = () => {
    qa('.g1-cart-hero,.g1-cart-trust,.g1-cart-sticky,.g1-cart-empty,.g1-cart-toast').forEach(el => el.remove());
    qa('.gramiss-cart-perks,.gramiss-cart-perks--top,.gramiss-cart-service-rail,.gramiss-cart-safe,.gramiss-cart-continue').forEach(el => {
      el.setAttribute('aria-hidden', 'true');
    });
  };

  const scheduleNativeUpdate = () => {
    clearTimeout(updateTimer);
    updateTimer = window.setTimeout(() => {
      const button = q('button[name="update_cart"]', woo);
      if (!button) return;
      button.disabled = false;
      button.removeAttribute('disabled');
      button.click();
    }, 430);
  };

  const changeQty = (nativeInput, direction) => {
    if (!nativeInput) return;
    const current = Number(nativeInput.value || 1);
    const step = Number(nativeInput.step || 1) || 1;
    const rawMin = Number(nativeInput.min || 1);
    const min = Number.isFinite(rawMin) && rawMin > 0 ? rawMin : 1;
    const rawMax = nativeInput.max === '' ? Infinity : Number(nativeInput.max);
    const max = Number.isFinite(rawMax) ? rawMax : Infinity;
    let next = current + direction * step;
    next = Math.max(min, Math.min(max, next));
    if (next === current) return;
    nativeInput.value = String(next);
    nativeInput.dispatchEvent(new Event('input', { bubbles: true }));
    nativeInput.dispatchEvent(new Event('change', { bubbles: true }));
    render();
    scheduleNativeUpdate();
  };

  const buildHero = count => {
    const hero = document.createElement('section');
    hero.className = 'g2-cart-hero';
    hero.innerHTML = `
      <div class="g2-cart-eyebrow">GRAMISS / CART</div>
      <div class="g2-cart-title-row">
        <h1 class="g2-cart-title">سبد خرید</h1>
        <span class="g2-cart-count"><i></i>${faNum(count)} آیتم</span>
      </div>
      <p class="g2-cart-sub">انتخاب‌ها اینجاست؛ فقط مرور کن و برو برای تسویه.</p>
      <div class="g2-cart-progress" aria-label="مراحل خرید">
        <div class="g2-cart-step is-active">سبد خرید</div>
        <div class="g2-cart-step">اطلاعات ارسال</div>
        <div class="g2-cart-step">پرداخت</div>
      </div>`;
    return hero;
  };

  const buildItem = item => {
    const card = document.createElement('article');
    card.className = 'g2-cart-item';
    card.dataset.index = String(item.index);

    const chips = item.variations.map(value => `<span class="g2-cart-chip">${escapeHTML(value)}</span>`).join('');
    const imageMarkup = item.image
      ? `<img src="${escapeAttr(item.image)}" alt="${escapeAttr(item.imageAlt)}">`
      : '';
    const qtyValue = Number(item.qty?.value || 1);

    card.innerHTML = `
      <a class="g2-cart-media" href="${escapeAttr(item.href)}">${imageMarkup}</a>
      <div class="g2-cart-info">
        <a class="g2-cart-name" href="${escapeAttr(item.href)}">${escapeHTML(item.title)}</a>
        ${chips ? `<div class="g2-cart-meta">${chips}</div>` : ''}
        <span class="g2-cart-stock">${escapeHTML(item.stock.replace(/^✓\s*/, ''))}</span>
        <div class="g2-cart-price">قیمت واحد <strong>${escapeHTML(item.unitPrice || '—')}</strong></div>
      </div>
      <button class="g2-cart-remove" type="button" aria-label="حذف ${escapeAttr(item.title)}">×</button>
      <div class="g2-cart-bottom">
        <div class="g2-cart-qty-wrap"><small>تعداد</small><div class="g2-cart-qty">
          <button type="button" data-act="minus" aria-label="کم کردن تعداد">−</button>
          <strong>${faNum(Number.isFinite(qtyValue) ? qtyValue : 1)}</strong>
          <button type="button" data-act="plus" aria-label="زیاد کردن تعداد">+</button>
        </div></div>
        <div class="g2-cart-line-total"><small>جمع این آیتم</small><strong>${escapeHTML(item.lineTotal || item.unitPrice || '—')}</strong></div>
      </div>`;

    q('[data-act="minus"]', card)?.addEventListener('click', () => changeQty(item.qty, -1));
    q('[data-act="plus"]', card)?.addEventListener('click', () => changeQty(item.qty, 1));
    q('.g2-cart-remove', card)?.addEventListener('click', () => {
      if (item.remove?.href) {
        location.href = item.remove.href;
      } else {
        item.remove?.click();
      }
    });
    return card;
  };

  const buildCoupon = () => {
    const nativeCoupon = q('.coupon', woo);
    if (!nativeCoupon) return null;
    const wrap = document.createElement('section');
    wrap.className = `g2-cart-coupon${couponOpen ? ' is-open' : ''}`;
    wrap.innerHTML = `
      <button class="g2-cart-coupon-toggle" type="button" aria-expanded="${couponOpen}"><span>کد تخفیف داری؟</span><b>+</b></button>
      <div class="g2-cart-coupon-form">
        <input type="text" autocomplete="off" placeholder="کد تخفیف را وارد کنید">
        <button type="button">اعمال کد</button>
      </div>`;
    const toggle = q('.g2-cart-coupon-toggle', wrap);
    const input = q('.g2-cart-coupon-form input', wrap);
    const submit = q('.g2-cart-coupon-form button', wrap);
    const nativeInput = q('#coupon_code, input[name="coupon_code"]', nativeCoupon);
    const nativeButton = q('button[name="apply_coupon"], button.button', nativeCoupon);
    if (nativeInput?.value) input.value = nativeInput.value;
    toggle?.addEventListener('click', () => {
      couponOpen = !couponOpen;
      wrap.classList.toggle('is-open', couponOpen);
      toggle.setAttribute('aria-expanded', String(couponOpen));
      if (couponOpen) setTimeout(() => input?.focus(), 100);
    });
    submit?.addEventListener('click', () => {
      if (!nativeInput || !nativeButton || !input) return;
      nativeInput.value = input.value.trim();
      nativeInput.dispatchEvent(new Event('input', { bubbles: true }));
      nativeInput.dispatchEvent(new Event('change', { bubbles: true }));
      nativeButton.click();
    });
    input?.addEventListener('keydown', event => {
      if (event.key === 'Enter') {
        event.preventDefault();
        submit?.click();
      }
    });
    return wrap;
  };

  const buildSummary = () => {
    const subtotal = getSubtotal() || '—';
    const shipping = getShipping();
    const total = getTotal() || subtotal;
    const checkout = getCheckoutUrl();
    const shop = getShopUrl();
    const shippingClass = /رایگان|free/i.test(shipping) ? ' g2-cart-free' : '';
    const section = document.createElement('section');
    section.className = 'g2-cart-summary';
    section.innerHTML = `
      <div class="g2-cart-summary-head"><h2>خلاصه سفارش</h2><span>ORDER SUMMARY</span></div>
      <div class="g2-cart-summary-rows">
        <div class="g2-cart-summary-row"><span>جمع کالاها</span><strong>${escapeHTML(subtotal)}</strong></div>
        <div class="g2-cart-summary-row"><span>ارسال</span><strong class="${shippingClass.trim()}">${escapeHTML(shipping)}</strong></div>
        <div class="g2-cart-summary-row is-total"><span>مبلغ نهایی</span><strong>${escapeHTML(total)}</strong></div>
      </div>
      <a class="g2-cart-checkout" href="${escapeAttr(checkout)}">ادامه به تسویه حساب <span>↗</span></a>
      <a class="g2-cart-continue" href="${escapeAttr(shop)}">ادامه خرید <span>←</span></a>`;
    return section;
  };

  const buildTrust = () => {
    const trust = document.createElement('section');
    trust.className = 'g2-cart-trust';
    trust.innerHTML = `
      <div><i>↗</i><span>ارسال سریع</span></div>
      <div><i>↻</i><span>تعویض آسان</span></div>
      <div><i>✓</i><span>پرداخت امن</span></div>`;
    return trust;
  };

  const buildEmpty = app => {
    const shop = getShopUrl();
    const empty = document.createElement('section');
    empty.className = 'g2-cart-empty';
    empty.innerHTML = `
      <div class="g2-cart-empty-art" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 8h14l-1 11H6L5 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg></div>
      <div class="g2-cart-eyebrow">YOUR CART / 00</div>
      <h2>هنوز چیزی انتخاب نکردی.</h2>
      <p>از فروشگاه بگرد، آیتم‌هایی که واقعاً می‌خوای رو انتخاب کن و بعد برگرد همین‌جا.</p>
      <a href="${escapeAttr(shop)}">شروع انتخاب <span>↗</span></a>`;
    app.appendChild(buildHero(0));
    app.appendChild(empty);
  };

  const ensureSticky = summary => {
    q('.g2-cart-sticky')?.remove();
    stickyObserver?.disconnect();
    stickyObserver = null;
    stickyState = { cta: false, footer: false };

    if (!summary) return;
    const total = getTotal() || getSubtotal() || '—';
    const checkoutUrl = getCheckoutUrl();
    const sticky = document.createElement('div');
    sticky.className = 'g2-cart-sticky';
    sticky.innerHTML = `
      <div class="g2-cart-sticky-total"><small>مبلغ نهایی</small><strong>${escapeHTML(total)}</strong></div>
      <a href="${escapeAttr(checkoutUrl)}">تسویه حساب <span>↗</span></a>`;
    document.body.appendChild(sticky);

    const cta = q('.g2-cart-checkout', summary);
    const footer = q('.site-footer');
    const updateVisibility = () => sticky.classList.toggle('is-hidden', stickyState.cta || stickyState.footer);
    stickyObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.target === cta) stickyState.cta = entry.isIntersecting;
        if (entry.target === footer) stickyState.footer = entry.isIntersecting;
      });
      updateVisibility();
    }, { threshold: 0.05 });
    if (cta) stickyObserver.observe(cta);
    if (footer) stickyObserver.observe(footer);
  };

  const escapeHTML = value => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  const escapeAttr = escapeHTML;

  const render = () => {
    removeLegacyNodes();
    q('.g2-cart-app', woo)?.remove();
    const rows = getRows();
    const app = document.createElement('div');
    app.className = 'g2-cart-app';
    woo.prepend(app);

    if (!rows.length) {
      buildEmpty(app);
      ensureSticky(null);
      return;
    }

    const items = rows.map(extractRow);
    app.appendChild(buildHero(getCount(rows)));

    const list = document.createElement('section');
    list.className = 'g2-cart-list';
    items.forEach(item => list.appendChild(buildItem(item)));
    app.appendChild(list);

    const coupon = buildCoupon();
    if (coupon) app.appendChild(coupon);

    const summary = buildSummary();
    app.appendChild(summary);
    app.appendChild(buildTrust());
    ensureSticky(summary);
  };

  render();

  document.addEventListener('updated_wc_div', () => setTimeout(render, 30));
  if (window.jQuery) {
    window.jQuery(document.body).on('updated_wc_div removed_from_cart added_to_cart applied_coupon removed_coupon', () => {
      setTimeout(render, 40);
    });
  }
  window.addEventListener('pageshow', () => setTimeout(render, 30));
})();
