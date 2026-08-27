/* GRAMISS_CART_MOBILE_V1 */
(() => {
  'use strict';
  const mq = window.matchMedia('(max-width:760px)');
  if (!mq.matches || !document.body.classList.contains('woocommerce-cart')) return;

  const body = document.body;
  body.classList.add('g1-cart-mobile-v1');
  const woo = document.querySelector('.woocommerce');
  if (!woo) return;

  const faNum = n => String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
  const rowSelector = 'tr.woocommerce-cart-form__cart-item, tr.cart_item';
  const getRows = () => Array.from(document.querySelectorAll(rowSelector));
  const getCount = () => {
    const rows = getRows();
    if (rows.length) return rows.reduce((sum,row) => {
      const input = row.querySelector('input.qty');
      const val = Number(input?.value || 1);
      return sum + (Number.isFinite(val) ? val : 1);
    },0);
    const badge = document.querySelector('.gramiss-cart-count');
    const val = Number((badge?.textContent || '').replace(/\D/g,''));
    return Number.isFinite(val) ? val : 0;
  };

  let hero = woo.querySelector('.g1-cart-hero');
  const ensureHero = () => {
    if (!hero) {
      hero = document.createElement('section');
      hero.className = 'g1-cart-hero';
      woo.prepend(hero);
    }
    const count = getCount();
    hero.innerHTML = `
      <div class="g1-cart-hero__eyebrow">GRAMISS / CART</div>
      <h1>سبد خرید</h1>
      <p>${count ? 'انتخاب‌هات آماده‌اند؛ فقط جزئیات نهایی مونده.' : 'فضای انتخاب‌های تو؛ از اینجا مسیر خریدت شروع می‌شه.'}</p>
      <div class="g1-cart-hero__meta"><span class="g1-cart-hero__dot"></span><span>${faNum(count)} ${count === 1 ? 'آیتم' : 'آیتم'} در سبد</span></div>`;
  };

  const scheduleUpdate = (() => {
    let timer = 0;
    return () => {
      clearTimeout(timer);
      timer = window.setTimeout(() => {
        const button = document.querySelector('button[name="update_cart"]');
        if (button) {
          button.disabled = false;
          button.click();
        }
      }, 420);
    };
  })();

  const enhanceQuantities = () => {
    document.querySelectorAll('.quantity').forEach(q => {
      const input = q.querySelector('input.qty');
      if (!input || q.dataset.g1Qty === '1') return;
      q.dataset.g1Qty = '1';
      const min = Number(input.min || 0);
      const max = input.max === '' ? Infinity : Number(input.max);
      const step = Number(input.step || 1) || 1;
      const make = (sign, label) => {
        const btn = document.createElement('button');
        btn.type = 'button'; btn.className = 'g1-cart-qty-btn'; btn.textContent = sign; btn.setAttribute('aria-label',label);
        return btn;
      };
      const minus = make('−','کم کردن تعداد');
      const plus = make('+','زیاد کردن تعداد');
      q.insertBefore(minus,input); q.appendChild(plus);
      const change = delta => {
        let value = Number(input.value || 1) + delta * step;
        value = Math.max(Number.isFinite(min) ? min : 0, value);
        if (Number.isFinite(max)) value = Math.min(max,value);
        input.value = String(value);
        input.dispatchEvent(new Event('change',{bubbles:true}));
        ensureHero(); scheduleUpdate();
      };
      minus.addEventListener('click',() => change(-1));
      plus.addEventListener('click',() => change(1));
      input.addEventListener('change',() => { ensureHero(); scheduleUpdate(); });
    });
  };

  const enhanceCoupon = () => {
    const coupon = document.querySelector('.coupon');
    if (!coupon || coupon.dataset.g1Coupon === '1') return;
    coupon.dataset.g1Coupon = '1';
    const toggle = document.createElement('button');
    toggle.type = 'button'; toggle.className = 'g1-cart-coupon-toggle'; toggle.setAttribute('aria-expanded','false');
    toggle.innerHTML = '<span>کد تخفیف داری؟</span><span aria-hidden="true">+</span>';
    coupon.prepend(toggle);
    toggle.addEventListener('click',() => {
      const open = coupon.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded',String(open));
      if (open) setTimeout(() => coupon.querySelector('input')?.focus(),150);
    });
  };

  const hideNativeTrust = () => {
    const root = document.querySelector('main') || woo.parentElement || document.body;
    const phrases = ['ارسال سریع','تعویض آسان','بازگشت و تعویض','پرداخت امن','اصالت کالا','خرید راحت','پشتیبانی اختصاصی'];
    const candidates = Array.from(root.querySelectorAll('section,div,ul')).filter(el => {
      if (el.classList.contains('g1-cart-trust') || el.closest('.g1-cart-trust')) return false;
      if (el === woo || el.contains(woo)) return false;
      const txt = (el.textContent || '').replace(/\s+/g,' ');
      const hits = phrases.filter(p => txt.includes(p)).length;
      if (hits < 2) return false;
      const childMatch = Array.from(el.children).some(ch => {
        const ct=(ch.textContent||'').replace(/\s+/g,' ');
        return phrases.filter(p=>ct.includes(p)).length >= 2;
      });
      return !childMatch;
    });
    candidates.forEach(el => el.classList.add('g1-cart-native-trust-hidden'));
  };

  const ensureTrust = () => {
    if (document.querySelector('.g1-cart-trust')) return;
    const target = document.querySelector('.cart-collaterals') || document.querySelector('.cart_totals')?.parentElement;
    if (!target) return;
    const trust = document.createElement('div');
    trust.className = 'g1-cart-trust';
    trust.innerHTML = `
      <div class="g1-cart-trust__item"><span class="g1-cart-trust__icon">↗</span><span>ارسال سریع</span></div>
      <div class="g1-cart-trust__item"><span class="g1-cart-trust__icon">↻</span><span>تعویض آسان</span></div>
      <div class="g1-cart-trust__item"><span class="g1-cart-trust__icon">✓</span><span>پرداخت امن</span></div>`;
    target.after(trust);
  };

  let sticky = null;
  const getTotal = () => {
    const el = document.querySelector('.cart_totals .order-total .amount') || document.querySelector('.cart_totals .cart-subtotal .amount') || document.querySelector('.product-subtotal .amount');
    return (el?.textContent || '').replace(/\s+/g,' ').trim();
  };
  const getCheckout = () => document.querySelector('.wc-proceed-to-checkout a.checkout-button, a.checkout-button');
  const ensureSticky = () => {
    const checkout = getCheckout();
    const total = getTotal();
    if (!checkout || !getRows().length) { sticky?.remove(); sticky = null; return; }
    if (!sticky) {
      sticky = document.createElement('div'); sticky.className = 'g1-cart-sticky';
      sticky.innerHTML = '<div class="g1-cart-sticky__total"><span class="g1-cart-sticky__label">مبلغ نهایی</span><strong class="g1-cart-sticky__amount"></strong></div><a class="g1-cart-sticky__cta" href="#">تسویه حساب <span aria-hidden="true">↗</span></a>';
      document.body.appendChild(sticky);
    }
    sticky.querySelector('.g1-cart-sticky__amount').textContent = total || '—';
    sticky.querySelector('.g1-cart-sticky__cta').href = checkout.href;
  };

  const ensureEmpty = () => {
    const nativeEmpty = document.querySelector('.cart-empty, .woocommerce-info.cart-empty');
    const textEmpty = /سبد خرید.*خالی|cart is currently empty/i.test(woo.textContent || '');
    const empty = Boolean(nativeEmpty || (!getRows().length && textEmpty));
    body.classList.toggle('g1-cart-is-empty',empty);
    if (!empty) { woo.querySelector('.g1-cart-empty')?.remove(); return false; }
    sticky?.remove(); sticky = null;
    if (!woo.querySelector('.g1-cart-empty')) {
      const shopHref = document.querySelector('.return-to-shop a')?.href || `${location.origin}/shop/`;
      const box = document.createElement('section');
      box.className = 'g1-cart-empty';
      box.innerHTML = `
        <div class="g1-cart-empty__visual" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 8h14l-1 11H6L5 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg></div>
        <div class="g1-cart-empty__eyebrow">YOUR CART / 00</div>
        <h2>هنوز چیزی انتخاب نکردی.</h2>
        <p>از بین آیتم‌ها بگرد، استایلت رو پیدا کن و انتخاب‌هایی که واقعاً می‌خوای رو اینجا نگه دار.</p>
        <a class="g1-cart-empty__primary" href="${shopHref}">شروع انتخاب <span aria-hidden="true">↗</span></a>
        <div class="g1-cart-empty__quick"><a href="${shopHref}?orderby=date">جدیدها</a><a href="${shopHref}?orderby=popularity">پرفروش‌ها</a></div>`;
      woo.appendChild(box);
    }
    return true;
  };

  let lastRemoved = '';
  document.addEventListener('click',e => {
    const remove = e.target.closest('.product-remove a.remove');
    if (remove) lastRemoved = (remove.closest(rowSelector)?.querySelector('.product-name')?.textContent || 'محصول').replace(/\s+/g,' ').trim();
  });
  const showToastFromNotice = () => {
    const notice = document.querySelector('.woocommerce-message');
    if (!notice || !/حذف شد|removed/i.test(notice.textContent || '')) return;
    const old = document.querySelector('.g1-cart-toast'); old?.remove();
    const undo = notice.querySelector('a.restore-item, a[href*="undo_item"]');
    const toast = document.createElement('div'); toast.className='g1-cart-toast';
    const msg = document.createElement('span'); msg.textContent = `${lastRemoved || 'محصول'} از سبد حذف شد.`; toast.appendChild(msg);
    if (undo) { const link=undo.cloneNode(true); link.textContent='بازگرداندن'; toast.appendChild(link); }
    document.body.appendChild(toast); setTimeout(()=>toast.remove(),5200);
    notice.style.display='none';
  };

  const enhance = () => {
    ensureHero();
    if (ensureEmpty()) { hideNativeTrust(); return; }
    enhanceQuantities(); enhanceCoupon(); hideNativeTrust(); ensureTrust(); ensureSticky(); showToastFromNotice();
  };

  enhance();
  document.addEventListener('updated_wc_div', enhance);
  if (window.jQuery) window.jQuery(document.body).on('updated_wc_div removed_from_cart added_to_cart',() => setTimeout(enhance,30));
  const observer = new MutationObserver(() => { clearTimeout(observer._t); observer._t=setTimeout(enhance,80); });
  observer.observe(woo,{childList:true,subtree:true});
})();
