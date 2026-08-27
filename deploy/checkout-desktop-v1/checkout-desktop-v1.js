/* GRAMISS_CHECKOUT_DESKTOP_V1 */
(() => {
  'use strict';
  const mq = window.matchMedia('(min-width:761px)');
  if (!mq.matches || !document.body.classList.contains('woocommerce-checkout') || document.body.classList.contains('woocommerce-order-received')) return;

  const body = document.body;
  const woo = document.querySelector('.woocommerce');
  const form = document.querySelector('form.checkout');
  if (!woo || !form) return;
  body.classList.add('g1-checkout-desktop-v1');

  const text = el => (el?.textContent || '').replace(/\s+/g,' ').trim();

  function ensureHero(){
    if (woo.querySelector('.g1-checkout-desktop-hero')) return;
    const hero = document.createElement('section');
    hero.className = 'g1-checkout-desktop-hero';
    hero.innerHTML = `
      <div class="g1-checkout-desktop-hero__copy">
        <div class="g1-checkout-desktop-hero__eyebrow">GRAMISS / CHECKOUT</div>
        <h1>تسویه حساب</h1>
        <p>اطلاعات، ارسال و پرداخت؛ یک مسیر کوتاه تا تکمیل سفارش.</p>
      </div>
      <div class="g1-checkout-desktop-progress" aria-label="مراحل تسویه حساب">
        <div class="g1-checkout-desktop-progress__step is-active" data-step="info"><span class="g1-checkout-desktop-progress__dot"></span><span>اطلاعات</span></div>
        <div class="g1-checkout-desktop-progress__step" data-step="shipping"><span class="g1-checkout-desktop-progress__dot"></span><span>ارسال</span></div>
        <div class="g1-checkout-desktop-progress__step" data-step="payment"><span class="g1-checkout-desktop-progress__dot"></span><span>پرداخت</span></div>
      </div>`;
    woo.prepend(hero);
  }

  function enhanceCoupon(){
    const coupon = document.querySelector('form.checkout_coupon');
    if (!coupon) return;
    coupon.classList.add('g1-desktop-coupon-form');
    const input = coupon.querySelector('input[name="coupon_code"],#coupon_code');
    const apply = coupon.querySelector('button[name="apply_coupon"],button');
    if (input) input.placeholder = 'کد تخفیف';
    if (apply) apply.textContent = 'اعمال';

    let wrap = document.querySelector('.g1-desktop-coupon-wrap');
    if (!wrap){
      wrap = document.createElement('div');
      wrap.className = 'g1-desktop-coupon-wrap';
      coupon.before(wrap);
      wrap.appendChild(coupon);
    }
    if (!wrap.querySelector('.g1-desktop-coupon-trigger')){
      const trigger = document.createElement('button');
      trigger.type='button'; trigger.className='g1-desktop-coupon-trigger'; trigger.setAttribute('aria-expanded','false');
      trigger.innerHTML='<span>کد تخفیف داری؟</span><span class="g1-desktop-coupon-trigger__plus" aria-hidden="true">+</span>';
      wrap.prepend(trigger);
      trigger.addEventListener('click',()=>{
        const open = trigger.getAttribute('aria-expanded') !== 'true';
        trigger.setAttribute('aria-expanded',String(open)); trigger.classList.toggle('is-open',open); coupon.classList.toggle('is-open',open);
        if(open) setTimeout(()=>input?.focus(),70);
      });
    }
  }

  function ensureGrid(){
    let grid = form.querySelector(':scope > .g1-checkout-desktop-grid');
    if (!grid){
      grid = document.createElement('div'); grid.className='g1-checkout-desktop-grid';
      const main=document.createElement('section'); main.className='g1-checkout-desktop-main';
      const aside=document.createElement('aside'); aside.className='g1-checkout-desktop-summary';
      grid.append(main,aside); form.appendChild(grid);
    }
    const main=grid.querySelector('.g1-checkout-desktop-main');
    const aside=grid.querySelector('.g1-checkout-desktop-summary');
    const customer=document.querySelector('#customer_details');
    const heading=document.querySelector('#order_review_heading');
    const review=document.querySelector('#order_review');
    if(customer && customer.parentElement!==main) main.appendChild(customer);
    if(heading && heading.parentElement!==aside) aside.appendChild(heading);
    if(review && review.parentElement!==aside) aside.appendChild(review);
    ensureSummaryCard(aside,heading,review);
  }

  function productCount(){
    const rows=document.querySelectorAll('.woocommerce-checkout-review-order-table tbody .cart_item');
    let count=0;
    rows.forEach(row=>{ const m=text(row.querySelector('.product-name')).match(/×\s*(\d+)/); count += m ? Number(m[1]) : 1; });
    return count || rows.length || 0;
  }

  function ensureSummaryCard(aside,heading,review){
    if(!aside || !review) return;
    let card=aside.querySelector('.g1-checkout-summary-card');
    if(!card){
      card=document.createElement('div'); card.className='g1-checkout-summary-card';
      const head=document.createElement('div'); head.className='g1-checkout-summary-head';
      head.innerHTML='<div><div class="g1-checkout-summary-head__eyebrow">GRAMISS / ORDER</div><h2>خلاصه سفارش</h2></div><span class="g1-checkout-summary-head__count"></span>';
      card.appendChild(head); aside.appendChild(card);
    }
    if(heading && heading.parentElement!==card) card.appendChild(heading);
    if(review.parentElement!==card) card.appendChild(review);
    const count=productCount();
    const countEl=card.querySelector('.g1-checkout-summary-head__count');
    if(countEl) countEl.textContent=count ? `${count} آیتم` : '';
  }

  function compactAddressLine2(prefix){
    const field=document.querySelector(`#${prefix}_address_2_field`);
    if(!field || field.dataset.g1DesktopCompact==='1') return;
    field.dataset.g1DesktopCompact='1';
    const input=field.querySelector('input'); const has=Boolean(input?.value?.trim());
    const toggle=document.createElement('button'); toggle.type='button'; toggle.className='g1-desktop-address2-toggle'; toggle.setAttribute('aria-expanded',String(has));
    toggle.innerHTML='<span>جزئیات آدرس؛ واحد، طبقه و...</span><span aria-hidden="true">+</span>';
    field.before(toggle); field.classList.toggle('g1-desktop-collapsed',!has); toggle.classList.toggle('is-open',has);
    toggle.addEventListener('click',()=>{ const open=toggle.getAttribute('aria-expanded')!=='true'; toggle.setAttribute('aria-expanded',String(open)); toggle.classList.toggle('is-open',open); field.classList.toggle('g1-desktop-collapsed',!open); if(open)setTimeout(()=>input?.focus(),70); });
  }

  function compactNotes(){
    const extra=document.querySelector('.woocommerce-additional-fields');
    if(!extra || extra.dataset.g1DesktopNotes==='1') return;
    const fields=extra.querySelector('.woocommerce-additional-fields__field-wrapper'); if(!fields)return;
    extra.dataset.g1DesktopNotes='1';
    const control=fields.querySelector('textarea,input'); const has=Boolean(control?.value?.trim());
    const toggle=document.createElement('button'); toggle.type='button'; toggle.className='g1-desktop-notes-toggle'; toggle.setAttribute('aria-expanded',String(has));
    toggle.innerHTML='<span>یادداشت سفارش (اختیاری)</span><span aria-hidden="true">+</span>';
    const heading=extra.querySelector('h3'); (heading || extra).after ? heading?.after(toggle) : extra.prepend(toggle);
    if(!heading) extra.prepend(toggle);
    fields.classList.toggle('g1-desktop-collapsed',!has); toggle.classList.toggle('is-open',has);
    toggle.addEventListener('click',()=>{ const open=toggle.getAttribute('aria-expanded')!=='true'; toggle.setAttribute('aria-expanded',String(open)); toggle.classList.toggle('is-open',open); fields.classList.toggle('g1-desktop-collapsed',!open); if(open)setTimeout(()=>control?.focus(),70); });
  }

  function normalizeText(){
    document.querySelectorAll('.woocommerce-checkout-review-order-table th,.woocommerce-checkout-review-order-table td').forEach(el=>{ if(text(el)==='Free shipping') el.textContent='رایگان'; });
  }

  function ensurePaymentTrust(){
    const payment=document.querySelector('#payment'); if(!payment) return;
    let trust=payment.querySelector('.g1-checkout-payment-trust');
    if(!trust){
      trust=document.createElement('div'); trust.className='g1-checkout-payment-trust';
      trust.innerHTML='<span>ثبت امن سفارش</span><span>اطلاعات پرداخت در مرحله بعد</span><span>پشتیبانی در صورت نیاز</span>';
      const place=payment.querySelector('.form-row.place-order');
      place?.before(trust);
    }
  }

  function updatePaymentCTA(){
    const place=document.querySelector('#place_order'); if(!place) return;
    const selected=document.querySelector('input[name="payment_method"]:checked')?.value;
    place.textContent = selected==='gramiss_card_transfer' ? 'ثبت سفارش و دریافت اطلاعات پرداخت' : 'ثبت سفارش';
  }

  function cleanLegacy(){
    document.querySelectorAll('.gramiss-checkout-perks,.gramiss-checkout-safe,.g1-checkout-sticky').forEach(el=>el.style.display='none');
  }

  function updateProgress(){
    const steps=[...document.querySelectorAll('.g1-checkout-desktop-progress__step')]; if(!steps.length)return;
    steps.forEach(s=>s.classList.remove('is-active'));
    const payment=document.querySelector('#payment'); const main=document.querySelector('.g1-checkout-desktop-main');
    const marker=window.scrollY+Math.min(window.innerHeight*.38,300); let active='info';
    if(payment && marker >= payment.getBoundingClientRect().top+window.scrollY-120) active='payment';
    else if(main && marker >= main.getBoundingClientRect().top+window.scrollY+Math.min(420,main.offsetHeight*.45)) active='shipping';
    document.querySelector(`.g1-checkout-desktop-progress__step[data-step="${active}"]`)?.classList.add('is-active');
  }

  function enhance(){
    if(!mq.matches) return;
    body.classList.add('g1-checkout-desktop-v1');
    ensureHero(); enhanceCoupon(); ensureGrid(); compactAddressLine2('billing'); compactAddressLine2('shipping'); compactNotes(); normalizeText(); ensurePaymentTrust(); updatePaymentCTA(); cleanLegacy(); updateProgress();
  }

  enhance();
  window.addEventListener('scroll',()=>requestAnimationFrame(updateProgress),{passive:true});
  document.addEventListener('change',e=>{ if(e.target?.name==='payment_method') setTimeout(()=>{updatePaymentCTA();ensurePaymentTrust();},20); });
  if(window.jQuery){
    window.jQuery(document.body).on('updated_checkout payment_method_selected',()=>setTimeout(enhance,30));
    window.jQuery(document.body).on('applied_coupon_in_checkout',()=>{ const t=document.querySelector('.g1-desktop-coupon-trigger'); const c=document.querySelector('form.checkout_coupon.g1-desktop-coupon-form'); t?.classList.remove('is-open');t?.setAttribute('aria-expanded','false');c?.classList.remove('is-open'); });
  }
})();
