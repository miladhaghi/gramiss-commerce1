/* GRAMISS_CHECKOUT_MOBILE_V1 */
(() => {
  'use strict';
  const mq = window.matchMedia('(max-width:760px)');
  if (!mq.matches || !document.body.classList.contains('woocommerce-checkout')) return;
  const body = document.body;
  body.classList.add('g1-checkout-mobile-v1');
  const woo = document.querySelector('.woocommerce');
  const form = document.querySelector('form.checkout');
  if (!woo || !form) return;

  const text = el => (el?.textContent || '').replace(/\s+/g,' ').trim();
  const getTotal = () => text(document.querySelector('.woocommerce-checkout-review-order-table .order-total .amount, #order_review .order-total .amount')) || '—';

  function ensureHero(){
    if (woo.querySelector('.g1-checkout-hero')) return;
    const hero = document.createElement('section');
    hero.className = 'g1-checkout-hero';
    hero.innerHTML = `
      <div class="g1-checkout-hero__eyebrow">GRAMISS / CHECKOUT</div>
      <h1>تسویه حساب</h1>
      <p>آدرس، ارسال و پرداخت؛ همه‌چیز در یک مسیر کوتاه.</p>
      <div class="g1-checkout-progress" aria-label="مراحل تسویه حساب">
        <div class="g1-checkout-progress__step is-active" data-step="info"><span class="g1-checkout-progress__dot"></span><span>اطلاعات</span></div>
        <div class="g1-checkout-progress__step" data-step="shipping"><span class="g1-checkout-progress__dot"></span><span>ارسال</span></div>
        <div class="g1-checkout-progress__step" data-step="payment"><span class="g1-checkout-progress__dot"></span><span>پرداخت</span></div>
      </div>`;
    woo.prepend(hero);
  }

  function compactOptional(){
    const extra = document.querySelector('.woocommerce-additional-fields');
    if (!extra || extra.dataset.g1Optional === '1') return;
    const fields = extra.querySelector('.woocommerce-additional-fields__field-wrapper');
    if (!fields) return;
    extra.dataset.g1Optional = '1';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'g1-checkout-optional-toggle';
    toggle.setAttribute('aria-expanded','false');
    toggle.innerHTML = '<span>یادداشت برای سفارش داری؟</span><span aria-hidden="true">+</span>';
    const heading = extra.querySelector('h3');
    heading?.after(toggle);
    fields.classList.add('g1-checkout-optional-collapsed');
    toggle.addEventListener('click',()=>{
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded',String(open));
      toggle.classList.toggle('is-open',open);
      fields.classList.toggle('g1-checkout-optional-collapsed',!open);
      if (open) setTimeout(()=>fields.querySelector('textarea,input')?.focus(),100);
    });
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
    if (y >= payTop - 80) active = 'payment';
    else if (y >= Math.min(infoBottom, reviewTop) - 120) active = 'shipping';
    document.querySelector(`.g1-checkout-progress__step[data-step="${active}"]`)?.classList.add('is-active');
  }

  function cleanLegacy(){
    document.querySelectorAll('.gramiss-cart-perks,.gramiss-cart-service-rail,.gramiss-cart-safe,.gramiss-checkout-perks,.gramiss-checkout-safe').forEach(el=>{
      if (!el.closest('.g1-checkout-trust')) el.style.display='none';
    });
  }

  function enhance(){
    ensureHero();
    compactOptional();
    ensureTrust();
    ensureSticky();
    cleanLegacy();
    updateProgress();
  }

  enhance();
  window.addEventListener('scroll',()=>requestAnimationFrame(updateProgress),{passive:true});
  document.addEventListener('updated_checkout',()=>setTimeout(enhance,30));
  if (window.jQuery) window.jQuery(document.body).on('updated_checkout payment_method_selected',()=>setTimeout(enhance,30));
  const observer = new MutationObserver(()=>{ clearTimeout(observer._g1); observer._g1=setTimeout(enhance,90); });
  observer.observe(form,{childList:true,subtree:true});
})();
