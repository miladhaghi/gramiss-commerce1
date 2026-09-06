/* GRAMISS_HOME_LOOKS_SURGICAL_V2 */
(() => {
  'use strict';

  const root = document.querySelector('[data-g1-looks]');
  if (!root) return;

  const spots = Array.from(root.querySelectorAll('[data-g1-look-spot]'));
  if (!spots.length) return;

  const closeSpot = (spot) => {
    if (!spot) return;
    spot.classList.remove('is-active');
    const button = spot.querySelector('.g1-looks__hotspot');
    if (button) button.setAttribute('aria-expanded', 'false');
  };

  const closeAll = (except = null) => {
    spots.forEach((spot) => {
      if (spot !== except) closeSpot(spot);
    });
  };

  spots.forEach((spot) => {
    const button = spot.querySelector('.g1-looks__hotspot');
    if (!button) return;

    button.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      const willOpen = !spot.classList.contains('is-active');
      closeAll(spot);
      spot.classList.toggle('is-active', willOpen);
      button.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    });
  });

  document.addEventListener('click', (event) => {
    if (!root.contains(event.target)) closeAll();
    else if (!event.target.closest('[data-g1-look-spot]')) closeAll();
  }, { passive: true });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeAll();
  });
})();
