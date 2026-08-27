/* GRAMISS_CART_DESKTOP_V1 */
(() => {
  'use strict';

  if (!window.matchMedia('(min-width:761px)').matches) return;
  if (!document.body.classList.contains('woocommerce-cart')) return;

  const body = document.body;
  body.classList.add('g3-cart-desktop-v1');

  let updateTimer = 0;
  let updating = false;

  const q = (selector, root = document) => root.querySelector(selector);
  const qa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const makeTrustRail = () => {
    if (q('.g3-cart-trust')) return;

    const trust = document.createElement('section');
    trust.className = 'g3-cart-trust';
    trust.setAttribute('aria-label', 'مزایای خرید از Gramiss');
    trust.innerHTML = `
      <div class="g3-cart-trust__item">
        <span class="g3-cart-trust__icon" aria-hidden="true">↗</span>
        <span class="g3-cart-trust__copy"><strong>ارسال سریع و رایگان</strong><small>برای سفارش‌های واجد شرایط</small></span>
      </div>
      <div class="g3-cart-trust__item">
        <span class="g3-cart-trust__icon" aria-hidden="true">↻</span>
        <span class="g3-cart-trust__copy"><strong>بازگشت و تعویض آسان</strong><small>تا ۷ روز پس از دریافت کالا</small></span>
      </div>
      <div class="g3-cart-trust__item">
        <span class="g3-cart-trust__icon" aria-hidden="true">✦</span>
        <span class="g3-cart-trust__copy"><strong>تضمین اصالت کالا</strong><small>محصولات منتخب و کنترل‌شده</small></span>
      </div>
      <div class="g3-cart-trust__item">
        <span class="g3-cart-trust__icon" aria-hidden="true">✓</span>
        <span class="g3-cart-trust__copy"><strong>پرداخت امن و مطمئن</strong><small>حفاظت از اطلاعات پرداخت</small></span>
      </div>`;

    const legacyTop = q('.gramiss-cart-perks--top') || q('.gramiss-cart-perks');
    if (legacyTop) {
      legacyTop.replaceWith(trust);
    } else {
      const form = q('form.woocommerce-cart-form');
      const notices = q('.woocommerce-notices-wrapper');
      if (form?.parentNode) {
        form.parentNode.insertBefore(trust, form);
      } else if (notices?.parentNode) {
        notices.parentNode.insertBefore(trust, notices.nextSibling);
      }
    }

    qa('.gramiss-cart-service-rail, .gramiss-cart-safe').forEach(el => {
      el.hidden = true;
      el.setAttribute('aria-hidden', 'true');
    });
  };

  const addSyncState = () => {
    if (q('.g3-cart-sync-state')) return;
    const state = document.createElement('div');
    state.className = 'g3-cart-sync-state';
    state.setAttribute('role', 'status');
    state.setAttribute('aria-live', 'polite');
    state.textContent = 'در حال به‌روزرسانی سبد';
    body.appendChild(state);
  };

  const fallbackNativeUpdate = () => {
    const button = q('form.woocommerce-cart-form button[name="update_cart"]');
    if (!button) {
      window.location.reload();
      return;
    }
    body.classList.remove('g3-cart-updating');
    button.disabled = false;
    button.removeAttribute('disabled');
    button.click();
  };

  const replaceIfPresent = (currentSelector, nextDoc) => {
    const current = q(currentSelector);
    const next = q(currentSelector, nextDoc);
    if (current && next) {
      current.replaceWith(next);
      return true;
    }
    return false;
  };

  const refreshFragments = () => {
    if (window.jQuery) {
      window.jQuery(document.body).trigger('updated_wc_div');
      window.jQuery(document.body).trigger('wc_fragment_refresh');
    }
    document.body.dispatchEvent(new CustomEvent('gramiss:cart-updated'));
  };

  const updateCart = async () => {
    if (updating) return;

    const form = q('form.woocommerce-cart-form');
    if (!form) return;

    const nativeButton = q('button[name="update_cart"]', form);
    const formData = new FormData(form);
    formData.set('update_cart', nativeButton?.value || 'به‌روزرسانی سبد خرید');

    updating = true;
    body.classList.add('g3-cart-updating');

    try {
      const response = await fetch(form.action || window.location.href, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Cache-Control': 'no-cache'
        },
        redirect: 'follow'
      });

      if (!response.ok) throw new Error(`cart update failed: ${response.status}`);

      const html = await response.text();
      const nextDoc = new DOMParser().parseFromString(html, 'text/html');
      const nextForm = q('form.woocommerce-cart-form', nextDoc);

      if (!nextForm) {
        window.location.assign(response.url || window.location.href);
        return;
      }

      const currentForm = q('form.woocommerce-cart-form');
      if (!currentForm) throw new Error('live cart form disappeared');
      currentForm.replaceWith(nextForm);

      replaceIfPresent('.cart_totals', nextDoc);
      replaceIfPresent('.woocommerce-notices-wrapper', nextDoc);

      const currentCount = q('.site-header .cart-count, .header-cart-count, .gramiss-cart-count');
      const nextCount = q('.site-header .cart-count, .header-cart-count, .gramiss-cart-count', nextDoc);
      if (currentCount && nextCount) currentCount.textContent = nextCount.textContent;

      refreshFragments();
    } catch (error) {
      console.warn('[Gramiss Cart Desktop] AJAX update fallback', error);
      updating = false;
      fallbackNativeUpdate();
      return;
    } finally {
      updating = false;
      body.classList.remove('g3-cart-updating');
    }
  };

  const scheduleUpdate = (delay = 430) => {
    window.clearTimeout(updateTimer);
    updateTimer = window.setTimeout(updateCart, delay);
  };

  const changeQuantity = (button) => {
    const quantity = button.closest('.quantity');
    const input = q('input.qty', quantity || undefined);
    if (!input) return false;

    const text = String(button.textContent || '').trim();
    const isMinus = button.classList.contains('minus') || button.matches('[data-action="minus"], [data-act="minus"]') || /[−–-]/.test(text);
    const isPlus = button.classList.contains('plus') || button.matches('[data-action="plus"], [data-act="plus"]') || /\+/.test(text);
    if (!isMinus && !isPlus) return false;

    const current = Number(input.value || 1);
    const step = Number(input.step || 1) || 1;
    const parsedMin = Number(input.min || 1);
    const min = Number.isFinite(parsedMin) ? parsedMin : 1;
    const parsedMax = input.max === '' ? Infinity : Number(input.max);
    const max = Number.isFinite(parsedMax) ? parsedMax : Infinity;
    const next = Math.max(min, Math.min(max, current + (isMinus ? -step : step)));

    if (next === current) return true;
    input.value = String(next);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  };

  document.addEventListener('click', event => {
    const button = event.target.closest('.quantity button, .quantity .plus, .quantity .minus');
    if (!button) return;
    if (!button.closest('form.woocommerce-cart-form')) return;

    if (changeQuantity(button)) {
      event.preventDefault();
      event.stopPropagation();
      scheduleUpdate(380);
    }
  }, true);

  document.addEventListener('input', event => {
    if (!event.target.matches('form.woocommerce-cart-form input.qty')) return;
    scheduleUpdate(520);
  });

  document.addEventListener('change', event => {
    if (!event.target.matches('form.woocommerce-cart-form input.qty')) return;
    scheduleUpdate(360);
  });

  makeTrustRail();
  addSyncState();
})();