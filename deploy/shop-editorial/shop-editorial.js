/* GRAMISS_SHOP_EDITORIAL_V1 */
(function(){
  'use strict';

  function $(sel, root){ return (root || document).querySelector(sel); }
  function $all(sel, root){ return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function buildToolbar(products){
    if ($('.gse-catalog-toolbar')) return;

    var nativeOrdering = $('.woocommerce-ordering');
    var nativeSelect = nativeOrdering ? $('select.orderby', nativeOrdering) : null;
    var resultCount = $('.woocommerce-result-count');

    var toolbar = document.createElement('section');
    toolbar.className = 'gse-catalog-toolbar';
    toolbar.setAttribute('aria-label','کنترل فروشگاه');

    var count = document.createElement('div');
    count.className = 'gse-count';
    var countText = resultCount ? resultCount.textContent.trim() : '';
    var matches = countText.match(/[۰-۹0-9]+/g);
    count.textContent = matches && matches.length ? matches[matches.length - 1] + ' محصول' : 'محصولات';

    var searchWrap = document.createElement('div');
    searchWrap.className = 'gse-search-wrap';
    var search = document.createElement('input');
    search.type = 'search';
    search.className = 'gse-search-input';
    search.placeholder = 'جست‌وجو در محصولات…';
    search.setAttribute('aria-label','جست‌وجو در محصولات');
    var currentParams = new URLSearchParams(window.location.search);
    if (currentParams.get('s')) search.value = currentParams.get('s');
    search.addEventListener('keydown', function(ev){
      if (ev.key !== 'Enter') return;
      ev.preventDefault();
      var params = new URLSearchParams(window.location.search);
      var q = search.value.trim();
      if (q) params.set('s', q); else params.delete('s');
      params.set('post_type','product');
      params.delete('paged');
      params.delete('product-page');
      window.location.href = window.location.pathname + '?' + params.toString();
    });
    searchWrap.appendChild(search);

    var tabs = document.createElement('div');
    tabs.className = 'gse-sort-tabs';
    tabs.setAttribute('role','group');
    tabs.setAttribute('aria-label','مرتب‌سازی محصولات');

    var choices = [
      ['menu_order','پیش‌فرض'],
      ['date','جدیدترین'],
      ['price','ارزان‌ترین'],
      ['price-desc','گران‌ترین'],
      ['popularity','پرفروش‌ترین']
    ];

    var activeValue = nativeSelect && nativeSelect.value ? nativeSelect.value : (currentParams.get('orderby') || 'menu_order');

    choices.forEach(function(pair){
      var value = pair[0], label = pair[1];
      if (nativeSelect && !$('option[value="'+ value.replace(/"/g,'\\"') +'"]', nativeSelect)) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'gse-sort-button' + (activeValue === value ? ' is-active' : '');
      btn.dataset.orderby = value;
      btn.textContent = label;
      btn.addEventListener('click', function(){
        if (nativeSelect) {
          nativeSelect.value = value;
          nativeSelect.dispatchEvent(new Event('change', {bubbles:true}));
          var form = nativeSelect.closest('form');
          if (form) {
            if (typeof form.requestSubmit === 'function') form.requestSubmit();
            else form.submit();
            return;
          }
        }
        var params = new URLSearchParams(window.location.search);
        if (value === 'menu_order') params.delete('orderby'); else params.set('orderby', value);
        params.delete('paged');
        params.delete('product-page');
        window.location.href = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
      });
      tabs.appendChild(btn);
    });

    toolbar.appendChild(count);
    toolbar.appendChild(searchWrap);
    toolbar.appendChild(tabs);
    products.parentNode.insertBefore(toolbar, products);
  }

  function markProducts(products){
    var items = $all(':scope > li.product', products);
    items.forEach(function(item, index){
      item.classList.add('gse-corner-card');
      item.classList.remove('gse-large-right','gse-large-left','gse-small');
      var cycle = index % 8;
      if (cycle === 0) item.classList.add('gse-large-right');
      else if (cycle === 4) item.classList.add('gse-large-left');
      else item.classList.add('gse-small');
    });
  }

  function init(){
    var products = $('ul.products');
    if (!products) return;
    document.body.classList.add('gse-shop-ready');
    products.classList.add('gse-products');
    markProducts(products);
    buildToolbar(products);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
})();
