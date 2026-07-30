(() => {
  const body = document.body;
  const menuToggle = document.querySelector('.menu-toggle');
  const panel = document.querySelector('.mobile-panel');
  const panelClose = document.querySelector('.menu-close');
  const backdrop = document.querySelector('.mobile-panel-backdrop');
  const searchToggle = document.querySelector('.search-toggle');
  const searchOverlay = document.querySelector('.search-overlay');

  const setMenu = (open) => {
    if (!panel || !menuToggle) return;
    panel.classList.toggle('is-open', open);
    panel.setAttribute('aria-hidden', String(!open));
    menuToggle.setAttribute('aria-expanded', String(open));
    body.style.overflow = open ? 'hidden' : '';
  };

  const setSearch = (open) => {
    if (!searchOverlay) return;
    searchOverlay.classList.toggle('is-open', open);
    searchOverlay.setAttribute('aria-hidden', String(!open));
    body.style.overflow = open ? 'hidden' : '';
    if (open) window.setTimeout(() => searchOverlay.querySelector('input')?.focus(), 50);
  };

  menuToggle?.addEventListener('click', () => setMenu(true));
  panelClose?.addEventListener('click', () => setMenu(false));
  backdrop?.addEventListener('click', () => setMenu(false));
  searchToggle?.addEventListener('click', () => setSearch(true));
  searchOverlay?.addEventListener('click', (event) => {
    if (event.target === searchOverlay) setSearch(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    setMenu(false);
    setSearch(false);
  });
})();
