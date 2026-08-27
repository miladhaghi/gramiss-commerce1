/* GRAMISS_CART_MOBILE_V1_BOOTSTRAP */
(() => {
  'use strict';
  if (!window.matchMedia('(max-width:760px)').matches) return;
  const body = document.body;
  const byClass = body.classList.contains('woocommerce-cart') || body.classList.contains('page-id-1');
  const byQuery = new URLSearchParams(location.search).get('page_id') === '1';
  const heading = Array.from(document.querySelectorAll('h1,h2')).some(el => (el.textContent || '').trim() === 'سبد خرید');
  if (byClass || byQuery || heading) body.classList.add('woocommerce-cart');
})();
