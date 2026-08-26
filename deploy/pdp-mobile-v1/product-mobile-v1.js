/* GRAMISS_PDP_MOBILE_UX_V1 */
(function () {
  'use strict';

  var media = window.matchMedia('(max-width: 760px)');
  if (!media.matches) return;

  function one(root, selector) {
    return (root || document).querySelector(selector);
  }

  function all(root, selector) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function dispatchChange(input) {
    if (!input) return;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function productRoot() {
    return one(document, '.g1-product-page, .gramiss-pdp-v2, .gramiss-pdp-runtime-v3, body.single-product') || document;
  }

  function purchaseForm(root) {
    return one(root, '.g1-pdp-summary form.cart, .g2-pdp-cart form.cart, .g3-summary-slot form.cart, .summary form.cart, form.cart');
  }

  function optionKind(select) {
    var key = String((select && (select.name + ' ' + select.id)) || '').toLowerCase();
    if (key.indexOf('color') !== -1 || key.indexOf('رنگ') !== -1) return 'color';
    if (key.indexOf('size') !== -1 || key.indexOf('clothing-size') !== -1 || key.indexOf('سایز') !== -1) return 'size';
    return 'option';
  }

  function createBuyBar(root) {
    var form = purchaseForm(root);
    if (!form || one(document, '.g1-mobile-buybar')) return;

    var nativeButton = one(form, '.single_add_to_cart_button');
    if (!nativeButton) return;

    var qtyInput = one(form, '.quantity input.qty');
    var bar = document.createElement('div');
    bar.className = 'g1-mobile-buybar';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'افزودن محصول به سبد خرید');

    var cta = document.createElement('button');
    cta.type = 'button';
    cta.className = 'g1-mobile-buybar__cta';
    cta.innerHTML = '<span>افزودن به سبد خرید</span><span aria-hidden="true">↗</span>';

    var qty = document.createElement('div');
    qty.className = 'g1-mobile-buybar__qty';
    qty.setAttribute('aria-label', 'تعداد');
    var minus = document.createElement('button');
    minus.type = 'button';
    minus.setAttribute('aria-label', 'کم کردن تعداد');
    minus.textContent = '−';
    var output = document.createElement('output');
    output.setAttribute('aria-live', 'polite');
    var plus = document.createElement('button');
    plus.type = 'button';
    plus.setAttribute('aria-label', 'زیاد کردن تعداد');
    plus.textContent = '+';
    qty.appendChild(minus);
    qty.appendChild(output);
    qty.appendChild(plus);

    bar.appendChild(cta);
    bar.appendChild(qty);
    document.body.appendChild(bar);

    function quantityValue() {
      if (!qtyInput) return 1;
      var value = parseFloat(qtyInput.value || '1');
      return Number.isFinite(value) ? value : 1;
    }

    function quantityBounds() {
      var min = qtyInput ? parseFloat(qtyInput.getAttribute('min') || '1') : 1;
      var maxRaw = qtyInput ? qtyInput.getAttribute('max') : '';
      var max = maxRaw === '' || maxRaw === null ? Infinity : parseFloat(maxRaw);
      var step = qtyInput ? parseFloat(qtyInput.getAttribute('step') || '1') : 1;
      return {
        min: Number.isFinite(min) ? min : 1,
        max: Number.isFinite(max) ? max : Infinity,
        step: Number.isFinite(step) && step > 0 ? step : 1
      };
    }

    function setQuantity(next) {
      if (!qtyInput) return;
      var bounds = quantityBounds();
      next = Math.max(bounds.min, Math.min(bounds.max, next));
      qtyInput.value = String(next);
      output.textContent = String(next);
      dispatchChange(qtyInput);
      sync();
    }

    function selectionState() {
      var selects = all(form, 'select[name^="attribute_"]');
      var missing = selects.filter(function (select) { return !select.value; });
      var kinds = missing.map(optionKind);
      var nativeDisabled = !!nativeButton.disabled || nativeButton.classList.contains('disabled') || nativeButton.classList.contains('wc-variation-selection-needed');
      var ready = missing.length === 0 && !nativeDisabled;
      var label = 'افزودن به سبد خرید';
      if (!ready && missing.length) {
        var hasColor = kinds.indexOf('color') !== -1;
        var hasSize = kinds.indexOf('size') !== -1;
        if (hasColor && hasSize) label = 'انتخاب رنگ و سایز';
        else if (hasSize) label = 'انتخاب سایز';
        else if (hasColor) label = 'انتخاب رنگ';
        else label = 'انتخاب گزینه‌ها';
      } else if (!ready) {
        label = 'انتخاب گزینه‌ها';
      }
      return { ready: ready, label: label };
    }

    function sync() {
      var state = selectionState();
      one(cta, 'span').textContent = state.label;
      cta.disabled = !state.ready;
      cta.setAttribute('aria-disabled', state.ready ? 'false' : 'true');
      output.textContent = String(quantityValue());
      var bounds = quantityBounds();
      minus.disabled = quantityValue() <= bounds.min;
      plus.disabled = quantityValue() >= bounds.max;
    }

    minus.addEventListener('click', function () {
      var bounds = quantityBounds();
      setQuantity(quantityValue() - bounds.step);
    });
    plus.addEventListener('click', function () {
      var bounds = quantityBounds();
      setQuantity(quantityValue() + bounds.step);
    });

    cta.addEventListener('click', function () {
      sync();
      if (cta.disabled) return;
      nativeButton.click();
    });

    all(form, 'select[name^="attribute_"]').forEach(function (select) {
      select.addEventListener('change', function () {
        window.setTimeout(sync, 0);
        window.setTimeout(sync, 100);
      });
    });

    if (qtyInput) {
      qtyInput.addEventListener('input', sync);
      qtyInput.addEventListener('change', sync);
    }

    if (window.jQuery) {
      var $form = window.jQuery(form);
      $form.on('woocommerce_variation_select_change found_variation reset_data hide_variation check_variations', function () {
        window.setTimeout(sync, 0);
        window.setTimeout(sync, 120);
      });
    }

    var observer = new MutationObserver(function () { sync(); });
    observer.observe(form, { subtree: true, attributes: true, attributeFilter: ['class', 'disabled', 'selected', 'value'] });

    document.body.classList.add('g1-mobile-pdp-ready');
    sync();
  }

  function accordionLabel(nav, panel, index) {
    var id = panel.id;
    if (nav && id) {
      var anchor = one(nav, 'a[href="#' + CSS.escape(id) + '"]');
      if (anchor && anchor.textContent.trim()) return anchor.textContent.trim();
    }
    if (id && id.indexOf('description') !== -1) return 'توضیحات محصول';
    if (id && id.indexOf('additional') !== -1) return 'مشخصات محصول';
    if (id && id.indexOf('review') !== -1) return 'دیدگاه‌ها';
    return 'اطلاعات محصول ' + (index + 1);
  }

  function createAccordions(root) {
    all(root, '.woocommerce-tabs').forEach(function (tabs) {
      if (tabs.dataset.g1MobileAccordion === '1') return;
      var nav = one(tabs, 'ul.tabs');
      var panels = all(tabs, '.woocommerce-Tabs-panel');
      if (!panels.length) return;

      tabs.dataset.g1MobileAccordion = '1';
      panels.forEach(function (panel, index) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'g1-mobile-accordion-button';
        button.textContent = accordionLabel(nav, panel, index);
        button.setAttribute('aria-expanded', 'false');
        if (!panel.id) panel.id = 'g1-mobile-product-panel-' + index;
        button.setAttribute('aria-controls', panel.id);
        panel.parentNode.insertBefore(button, panel);
        panel.classList.remove('g1-mobile-panel-open');

        button.addEventListener('click', function () {
          var open = button.getAttribute('aria-expanded') === 'true';
          button.setAttribute('aria-expanded', open ? 'false' : 'true');
          panel.classList.toggle('g1-mobile-panel-open', !open);
        });
      });
    });
  }

  function galleryElements(root) {
    var stage = one(root, '.g2-pdp-stage, .g3-dual-stage, .woocommerce-product-gallery .flex-viewport');
    var main = one(root, '#g2-pdp-main-image, .g2-pdp-main-image, .g3-dual-image-primary, .woocommerce-product-gallery__image img');
    var thumbs = all(root, '[data-g2-pdp-thumb]');
    if (!thumbs.length) thumbs = all(root, '.flex-control-thumbs li');
    return { stage: stage, main: main, thumbs: thumbs };
  }

  function activeThumbIndex(items) {
    for (var i = 0; i < items.length; i += 1) {
      var item = items[i];
      if (item.classList.contains('is-active')) return i;
      if (item.getAttribute('aria-pressed') === 'true') return i;
      var img = one(item, 'img');
      if (img && img.classList.contains('flex-active')) return i;
    }
    return 0;
  }

  function activateThumb(item) {
    if (!item) return;
    var clickable = item.matches('button') ? item : (one(item, 'img') || item);
    clickable.click();
    if (item.scrollIntoView) item.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }

  function createViewer(root) {
    var gallery = galleryElements(root);
    if (!gallery.stage || !gallery.main) return;

    var viewer = document.createElement('div');
    viewer.className = 'g1-mobile-image-viewer';
    viewer.setAttribute('role', 'dialog');
    viewer.setAttribute('aria-modal', 'true');
    viewer.setAttribute('aria-label', 'نمایش بزرگ تصویر محصول');
    var close = document.createElement('button');
    close.type = 'button';
    close.className = 'g1-mobile-image-viewer__close';
    close.setAttribute('aria-label', 'بستن تصویر');
    close.textContent = '×';
    var image = document.createElement('img');
    image.alt = gallery.main.alt || 'تصویر محصول';
    viewer.appendChild(close);
    viewer.appendChild(image);
    document.body.appendChild(viewer);

    function currentMain() {
      return one(root, '#g2-pdp-main-image, .g2-pdp-main-image, .g3-dual-image-primary, .woocommerce-product-gallery__image img') || gallery.main;
    }

    function openViewer() {
      var current = currentMain();
      image.src = current.getAttribute('data-full') || current.currentSrc || current.src;
      image.alt = current.alt || 'تصویر محصول';
      viewer.classList.add('is-open');
      document.documentElement.style.overflow = 'hidden';
      close.focus({ preventScroll: true });
    }

    function closeViewer() {
      viewer.classList.remove('is-open');
      document.documentElement.style.overflow = '';
    }

    close.addEventListener('click', closeViewer);
    viewer.addEventListener('click', function (event) {
      if (event.target === viewer) closeViewer();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && viewer.classList.contains('is-open')) closeViewer();
    });

    var startX = 0;
    var startY = 0;
    var suppressClickUntil = 0;
    gallery.stage.addEventListener('touchstart', function (event) {
      if (!event.touches || event.touches.length !== 1) return;
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    }, { passive: true });

    gallery.stage.addEventListener('touchend', function (event) {
      if (!event.changedTouches || event.changedTouches.length !== 1) return;
      var dx = event.changedTouches[0].clientX - startX;
      var dy = event.changedTouches[0].clientY - startY;
      if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy) * 1.25) return;
      var current = activeThumbIndex(gallery.thumbs);
      var next = dx < 0 ? current + 1 : current - 1;
      next = Math.max(0, Math.min(gallery.thumbs.length - 1, next));
      if (next !== current) activateThumb(gallery.thumbs[next]);
      suppressClickUntil = Date.now() + 350;
    }, { passive: true });

    gallery.stage.addEventListener('click', function () {
      if (Date.now() < suppressClickUntil) return;
      openViewer();
    });
  }

  function boot() {
    if (!media.matches) return;
    var root = productRoot();
    createBuyBar(root);
    createAccordions(root);
    createViewer(root);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  window.addEventListener('load', function () { window.setTimeout(boot, 120); });
})();
