/* GRAMISS_CHECKOUT_MOBILE_V1 */
/* GRAMISS_CHECKOUT_MOBILE_V2 */
(() => {
  'use strict';
  const mq = window.matchMedia('(max-width:760px)');
  if (!mq.matches || !document.body.classList.contains('woocommerce-checkout')) return;

  const body = document.body;
  body.classList.add('g1-checkout-mobile-v1','g1-checkout-mobile-v2');
  const woo = document.querySelector('.woocommerce');
  const form = document.querySelector('form.checkout');
  if (!woo || !form) return;

  const text = el => (el?.textContent || '').replace(/\s+/g,' ').trim();
  const getTotal = () => text(document.querySelector('.woocommerce-checkout-review-order-table .order-total .amount, #order_review .order-total .amount')) || '—';

  function guardViewport(){
    let node = woo.parentElement;
    while (node && node !== body) {
      node.classList.add('g1-checkout-shell');
      node = node.parentElement;
    }
    document.documentElement.style.overflowX = 'hidden';
    body.style.overflowX = 'hidden';
  }

  function ensureHero(){
    if (woo.querySelector('.g1-checkout-hero')) return;
    const hero = document.createElement('section');
    hero.className = 'g1-checkout-hero';
    hero.innerHTML = `
      <div class="g1-checkout-hero__eyebrow">GRAMISS / CHECKOUT</div>
      <h1>تسویه حساب</h1>
      <p>آدرس، ارسال و پرداخت؛ در یک مسیر کوتاه.</p>
      <div class="g1-checkout-progress" aria-label="مراحل تسویه حساب">
        <div class="g1-checkout-progress__step is-active" data-step="info"><span class="g1-checkout-progress__dot"></span><span>اطلاعات</span></div>
        <div class="g1-checkout-progress__step" data-step="shipping"><span class="g1-checkout-progress__dot"></span><span>ارسال</span></div>
        <div class="g1-checkout-progress__step" data-step="payment"><span class="g1-checkout-progress__dot"></span><span>پرداخت</span></div>
      </div>`;
    woo.prepend(hero);
  }

  function enhanceCoupon(){
    const coupon = document.querySelector('form.checkout_coupon');
    if (!coupon) return;
    coupon.classList.add('g1-coupon-form');

    const input = coupon.querySelector('input[name="coupon_code"], #coupon_code');
    if (input) input.setAttribute('placeholder','کد تخفیف');
    const apply = coupon.querySelector('button[name="apply_coupon"], button');
    if (apply) apply.textContent = 'اعمال';

    let trigger = document.querySelector('.g1-coupon-trigger');
    if (!trigger) {
      trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'g1-coupon-trigger';
      trigger.setAttribute('aria-expanded','false');
      trigger.innerHTML = '<span>کد تخفیف داری؟</span><span class="g1-coupon-trigger__plus" aria-hidden="true">+</span>';
      coupon.before(trigger);
      trigger.addEventListener('click',()=>{
        const open = trigger.getAttribute('aria-expanded') !== 'true';
        trigger.setAttribute('aria-expanded',String(open));
        trigger.classList.toggle('is-open',open);
        coupon.classList.toggle('is-open',open);
        if (open) setTimeout(()=>input?.focus(),80);
      });
    }
  }

  function compactAddressLine2(prefix){
    const field = document.querySelector(`#${prefix}_address_2_field`);
    if (!field || field.dataset.g1Compact === '1') return;
    field.dataset.g1Compact = '1';
    const input = field.querySelector('input');
    const hasValue = Boolean(input?.value?.trim());
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'g1-address2-toggle';
    toggle.setAttribute('aria-expanded',String(hasValue));
    toggle.innerHTML = '<span>جزئیات آدرس؛ واحد، طبقه و...</span><span aria-hidden="true">+</span>';
    field.before(toggle);
    field.classList.toggle('g1-address2-collapsed',!hasValue);
    toggle.classList.toggle('is-open',hasValue);
    toggle.addEventListener('click',()=>{
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded',String(open));
      toggle.classList.toggle('is-open',open);
      field.classList.toggle('g1-address2-collapsed',!open);
      if (open) setTimeout(()=>input?.focus(),80);
    });
  }

  function compactOptional(){
    const extra = document.querySelector('.woocommerce-additional-fields');
    if (!extra || extra.dataset.g1Optional === '1') return;
    const fields = extra.querySelector('.woocommerce-additional-fields__field-wrapper');
    if (!fields) return;
    extra.dataset.g1Optional = '1';
    const textarea = fields.querySelector('textarea,input');
    const hasValue = Boolean(textarea?.value?.trim());
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'g1-checkout-optional-toggle';
    toggle.setAttribute('aria-expanded',String(hasValue));
    toggle.innerHTML = '<span>یادداشت سفارش (اختیاری)</span><span aria-hidden="true">+</span>';
    const heading = extra.querySelector('h3');
    heading?.after(toggle);
    fields.classList.toggle('g1-checkout-optional-collapsed',!hasValue);
    toggle.classList.toggle('is-open',hasValue);
    toggle.addEventListener('click',()=>{
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded',String(open));
      toggle.classList.toggle('is-open',open);
      fields.classList.toggle('g1-checkout-optional-collapsed',!open);
      if (open) setTimeout(()=>textarea?.focus(),80);
    });
  }

  function compactOrderReview(){
    const table = document.querySelector('.woocommerce-checkout-review-order-table');
    if (!table || table.dataset.g1CompactOrder === '1') return;
    table.dataset.g1CompactOrder = '1';
    table.classList.add('g1-order-details-collapsed');
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'g1-order-details-toggle';
    toggle.setAttribute('aria-expanded','false');
    toggle.innerHTML = '<span>مشاهده جزئیات سفارش</span><span aria-hidden="true">+</span>';
    table.before(toggle);
    toggle.addEventListener('click',()=>{
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded',String(open));
      toggle.classList.toggle('is-open',open);
      table.classList.toggle('g1-order-details-collapsed',!open);
    });
  }

  function normalizeWooText(){
    document.querySelectorAll('.woocommerce-checkout-review-order-table td, .woocommerce-checkout-review-order-table th').forEach(el=>{
      if (text(el) === 'Free shipping') el.textContent = 'رایگان';
    });
    const shippingTitle = document.querySelector('#ship-to-different-address span');
    if (shippingTitle) shippingTitle.setAttribute('aria-label','ارسال به آدرس دیگری؟');
  }

  function ensureTrust(){
    if (document.querySelector('.g1-checkout-trust')) return;
    const target = document.querySelector('#order_review') || form;
    const trust = document.createElement('div');
    trust.className = 'g1-checkout-trust';
    trust.innerHTML = `
      <div class="g1-checkout-trust__item"><span class="g1-checkout-trust__icon">↗</span><span>ارسال مطمئن</span></div>
      <div class="g1-checkout-trust__item"><span class="g1-checkout-trust__icon">✓</span><span>پرداخت امن</span></div>
      <div class="g1-checkout-trust__item"><span class="g1-checkout-trust__icon">↻</span><span>تعویض آسان</span></div>`;
    target.after(trust);
  }

  let sticky;
  function ensureSticky(){
    const place = document.querySelector('#place_order');
    if (!place) return;
    if (!sticky){
      sticky = document.createElement('div');
      sticky.className = 'g1-checkout-sticky';
      sticky.innerHTML = '<div class="g1-checkout-sticky__total"><span class="g1-checkout-sticky__label">مبلغ نهایی</span><strong class="g1-checkout-sticky__amount">—</strong></div><button class="g1-checkout-sticky__cta" type="button">ثبت سفارش <span aria-hidden="true">↗</span></button>';
      document.body.appendChild(sticky);
      sticky.querySelector('.g1-checkout-sticky__cta').addEventListener('click',()=>{
        const current = document.querySelector('#place_order');
        if (current && !current.disabled){ current.click(); }
        else document.querySelector('.woocommerce-NoticeGroup-checkout, form.checkout')?.scrollIntoView({behavior:'smooth',block:'start'});
      });
    }
    sticky.querySelector('.g1-checkout-sticky__amount').textContent = getTotal();
    const cta = sticky.querySelector('.g1-checkout-sticky__cta');
    cta.disabled = Boolean(place.disabled);
    cta.style.opacity = place.disabled ? '.55' : '1';
  }

  function updateProgress(){
    const info = document.querySelector('#customer_details, .woocommerce-billing-fields');
    const payment = document.querySelector('#payment');
    const review = document.querySelector('#order_review');
    const y = window.scrollY + Math.min(window.innerHeight * .38, 260);
    const steps = Array.from(document.querySelectorAll('.g1-checkout-progress__step'));
    steps.forEach(s=>s.classList.remove('is-active'));
    let active = 'info';
    const payTop = payment ? payment.getBoundingClientRect().top + window.scrollY : Infinity;
    const reviewTop = review ? review.getBoundingClientRect().top + window.scrollY : Infinity;
    const infoBottom = info ? info.getBoundingClientRect().bottom + window.scrollY : 0;
    if (y >= payTop - 70) active = 'payment';
    else if (y >= Math.min(infoBottom, reviewTop) - 100) active = 'shipping';
    document.querySelector(`.g1-checkout-progress__step[data-step="${active}"]`)?.classList.add('is-active');
  }

  function cleanLegacy(){
    document.querySelectorAll('.gramiss-cart-perks,.gramiss-cart-service-rail,.gramiss-cart-safe,.gramiss-checkout-perks,.gramiss-checkout-safe').forEach(el=>{
      if (!el.closest('.g1-checkout-trust')) el.style.display='none';
    });
  }

  function enhance(){
    guardViewport();
    ensureHero();
    enhanceCoupon();
    compactAddressLine2('billing');
    compactAddressLine2('shipping');
    compactOptional();
    compactOrderReview();
    normalizeWooText();
    ensureTrust();
    ensureSticky();
    cleanLegacy();
    updateProgress();
  }

  enhance();
  window.addEventListener('scroll',()=>requestAnimationFrame(updateProgress),{passive:true});
  window.addEventListener('resize',guardViewport,{passive:true});
  document.addEventListener('updated_checkout',()=>setTimeout(enhance,30));
  if (window.jQuery) {
    window.jQuery(document.body).on('updated_checkout payment_method_selected',()=>setTimeout(enhance,30));
    window.jQuery(document.body).on('applied_coupon_in_checkout',()=>{
      document.querySelector('.g1-coupon-trigger')?.classList.remove('is-open');
      document.querySelector('.g1-coupon-trigger')?.setAttribute('aria-expanded','false');
      document.querySelector('form.checkout_coupon.g1-coupon-form')?.classList.remove('is-open');
    });
  }
  const observer = new MutationObserver(()=>{ clearTimeout(observer._g1); observer._g1=setTimeout(enhance,90); });
  observer.observe(form,{childList:true,subtree:true});
})();
