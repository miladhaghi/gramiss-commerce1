(() => {
  const body = document.body;
  const menuToggle = document.querySelector('.menu-toggle');
  const panel = document.querySelector('.mobile-panel');
  const panelClose = document.querySelector('.menu-close');
  const backdrop = document.querySelector('.mobile-panel-backdrop');
  const searchToggles = [...document.querySelectorAll('.search-toggle')];
  const searchOverlay = document.querySelector('.search-overlay');
  const searchClose = document.querySelector('.search-close');
  const siteHeader = document.querySelector('.site-header');

  const lockBody = () => {
    const hasOpenLayer = panel?.classList.contains('is-open') || searchOverlay?.classList.contains('is-open') || document.querySelector('.shop-filter-overlay.is-open');
    body.style.overflow = hasOpenLayer ? 'hidden' : '';
  };

  const focusable = (root) => root ? [...root.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')] : [];

  const trapFocus = (event, root) => {
    if (event.key !== 'Tab' || !root) return;
    const items = focusable(root).filter((item) => item.offsetParent !== null);
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  const setMenu = (open) => {
    if (!panel || !menuToggle) return;
    panel.classList.toggle('is-open', open);
    panel.setAttribute('aria-hidden', String(!open));
    menuToggle.setAttribute('aria-expanded', String(open));
    lockBody();
    if (open) window.setTimeout(() => panelClose?.focus(), 40);
  };

  const setSearch = (open) => {
    if (!searchOverlay) return;
    searchOverlay.classList.toggle('is-open', open);
    searchOverlay.setAttribute('aria-hidden', String(!open));
    searchToggles.forEach((button) => button.setAttribute('aria-expanded', String(open)));
    lockBody();
    if (open) window.setTimeout(() => searchOverlay.querySelector('input[type="search"]')?.focus(), 50);
  };

  menuToggle?.addEventListener('click', () => setMenu(true));
  panelClose?.addEventListener('click', () => setMenu(false));
  backdrop?.addEventListener('click', () => setMenu(false));
  panel?.addEventListener('keydown', (event) => trapFocus(event, panel));

  searchToggles.forEach((button) => button.addEventListener('click', () => setSearch(true)));
  searchClose?.addEventListener('click', () => setSearch(false));
  searchOverlay?.addEventListener('click', (event) => {
    if (event.target === searchOverlay) setSearch(false);
  });
  searchOverlay?.addEventListener('keydown', (event) => trapFocus(event, searchOverlay));

  const filterOverlay = document.querySelector('.shop-filter-overlay');
  const filterTrigger = document.querySelector('.shop-mobile-filter-trigger');
  const filterClose = document.querySelector('.filter-drawer-close');
  const setFilter = (open) => {
    if (!filterOverlay || !filterTrigger) return;
    filterOverlay.classList.toggle('is-open', open);
    filterOverlay.setAttribute('aria-hidden', String(!open));
    filterTrigger.setAttribute('aria-expanded', String(open));
    lockBody();
  };
  filterTrigger?.addEventListener('click', () => setFilter(true));
  filterClose?.addEventListener('click', () => setFilter(false));
  filterOverlay?.addEventListener('click', (event) => {
    if (event.target === filterOverlay) setFilter(false);
  });

  document.querySelectorAll('.shop-filter-heading').forEach((heading) => {
    heading.addEventListener('click', () => {
      const section = heading.closest('.shop-filter-section');
      const options = section?.querySelector('.shop-filter-options');
      if (!section || !options) return;
      const open = !section.classList.contains('is-open');
      section.classList.toggle('is-open', open);
      heading.setAttribute('aria-expanded', String(open));
      options.hidden = !open;
    });
  });

  document.querySelectorAll('.shop-grid-toggle button').forEach((button) => {
    button.addEventListener('click', () => {
      const grid = document.querySelector('.shop-product-grid');
      if (!grid) return;
      const columns = button.dataset.grid === '4' ? '4' : '3';
      grid.classList.remove('columns-3', 'columns-4');
      grid.classList.add(`columns-${columns}`);
      document.querySelectorAll('.shop-grid-toggle button').forEach((item) => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      try { localStorage.setItem('gramiss_shop_grid', columns); } catch (_) {}
    });
  });

  try {
    const savedGrid = localStorage.getItem('gramiss_shop_grid');
    if (savedGrid === '4') document.querySelector('.shop-grid-toggle button[data-grid="4"]')?.click();
  } catch (_) {}

  const toast = document.querySelector('.gramiss-shop-toast');
  let toastTimer;
  const announce = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 2600);
  };

  const bindStoredToggle = (selector, storageKey, successMessage) => {
    let values = [];
    try { values = JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch (_) { values = []; }

    document.querySelectorAll(selector).forEach((button) => {
      const id = button.dataset.gramissWishlist || button.dataset.gramissCompare;
      const sync = () => {
        const active = values.includes(id);
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
      };
      sync();
      button.addEventListener('click', () => {
        values = values.includes(id) ? values.filter((value) => value !== id) : [...values, id];
        try { localStorage.setItem(storageKey, JSON.stringify(values)); } catch (_) {}
        sync();
        announce(successMessage);
      });
    });
  };

  bindStoredToggle('[data-gramiss-wishlist]', 'gramiss_wc_wishlist', 'علاقه‌مندی‌ها به‌روزرسانی شد.');
  bindStoredToggle('[data-gramiss-compare]', 'gramiss_wc_compare', 'فهرست مقایسه به‌روزرسانی شد.');

  if (window.jQuery) {
    window.jQuery(document.body).on('added_to_cart', () => announce('محصول به سبد خرید اضافه شد.'));
  }

  const syncHeader = () => siteHeader?.classList.toggle('is-scrolled', window.scrollY > 10);
  syncHeader();
  window.addEventListener('scroll', syncHeader, { passive: true });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    setMenu(false);
    setSearch(false);
    setFilter(false);
  });
})();
