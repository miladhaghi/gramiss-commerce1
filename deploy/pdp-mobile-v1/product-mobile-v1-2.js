/* GRAMISS_PDP_MOBILE_UX_V1_2_POLISH */
(() => {
  'use strict';

  const mobile = window.matchMedia('(max-width: 760px)');
  if (!mobile.matches) return;

  const faNumber = (value) => {
    try {
      return new Intl.NumberFormat('fa-IR').format(Number(value));
    } catch (_) {
      return String(value);
    }
  };

  const polishReset = () => {
    document.querySelectorAll('body.single-product .reset_variations').forEach((link) => {
      const label = 'پاک کردن انتخاب‌ها';
      if (link.getAttribute('aria-label') !== label) link.setAttribute('aria-label', label);
      if (link.getAttribute('title') !== label) link.setAttribute('title', label);
    });
  };

  const polishStock = () => {
    const selectors = [
      'body.single-product .woocommerce-variation-availability .stock',
      'body.single-product .single_variation .stock'
    ].join(',');

    document.querySelectorAll(selectors).forEach((stock) => {
      const text = (stock.textContent || '').replace(/\s+/g, ' ').trim();
      if (!text || text.startsWith('فقط ')) return;

      const match = text.match(/([0-9۰-۹٠-٩]+)\s*عدد\s*در\s*انبار/);
      if (!match) return;

      const latin = match[1]
        .replace(/[۰-۹]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
        .replace(/[٠-٩]/g, (d) => '٠١٢٣٤٥٦٧٨٩'.indexOf(d));
      const count = Number(latin);
      if (!Number.isFinite(count)) return;

      const next = `فقط ${faNumber(count)} عدد باقی مانده`;
      if (stock.textContent !== next) stock.textContent = next;
    });
  };

  let queued = false;
  const polish = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      polishReset();
      polishStock();
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', polish, { once: true });
  } else {
    polish();
  }

  if (window.jQuery) {
    window.jQuery(document).on(
      'found_variation reset_data woocommerce_variation_has_changed',
      () => window.setTimeout(polish, 0)
    );
  }

  const observer = new MutationObserver(polish);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true
  });
})();
