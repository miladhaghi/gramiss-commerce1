(() => {
  const GRAMISS_HOME_HERO_INTERACTION_V8 = true;
  const MOBILE_MAX = 820;
  const heroes = [...document.querySelectorAll('[data-g1-floating-hero]')];
  if (!heroes.length) return;

  heroes.forEach((hero) => {
    const track = hero.querySelector('[data-g1-floating-track]');
    const products = [...hero.querySelectorAll('[data-g1-floating-product]')];
    if (!track || !products.length) return;

    const isMobile = () => window.innerWidth <= MOBILE_MAX;

    const updateActive = () => {
      if (!isMobile()) {
        products.forEach((item) => item.classList.remove('is-active'));
        return;
      }

      const rect = track.getBoundingClientRect();
      const center = rect.left + track.clientWidth / 2;
      let best = products[0];
      let distance = Infinity;

      products.forEach((item) => {
        const itemRect = item.getBoundingClientRect();
        const itemDistance = Math.abs((itemRect.left + itemRect.width / 2) - center);
        if (itemDistance < distance) {
          distance = itemDistance;
          best = item;
        }
      });

      products.forEach((item) => item.classList.toggle('is-active', item === best));
    };

    let railFrame = 0;
    const requestActiveUpdate = () => {
      if (!isMobile()) return;
      cancelAnimationFrame(railFrame);
      railFrame = requestAnimationFrame(updateActive);
    };

    track.addEventListener('scroll', requestActiveUpdate, { passive: true });
    window.addEventListener('resize', requestActiveUpdate, { passive: true });

    products.forEach((item) => {
      item.addEventListener('dragstart', (event) => event.preventDefault());

      let pointerDown = false;
      let startX = 0;
      let startY = 0;
      let dragged = false;

      item.addEventListener('pointerdown', (event) => {
        if (!isMobile()) return;
        pointerDown = true;
        startX = event.clientX;
        startY = event.clientY;
        dragged = false;
      }, { passive: true });

      item.addEventListener('pointermove', (event) => {
        if (!pointerDown || dragged) return;
        dragged = Math.hypot(event.clientX - startX, event.clientY - startY) > 9;
      }, { passive: true });

      const finishPointer = () => {
        pointerDown = false;
      };
      item.addEventListener('pointerup', finishPointer, { passive: true });
      item.addEventListener('pointercancel', finishPointer, { passive: true });

      item.addEventListener('click', (event) => {
        if (!isMobile() || !dragged) return;
        event.preventDefault();
        event.stopPropagation();
        dragged = false;
      });
    });

    requestAnimationFrame(updateActive);
    void GRAMISS_HOME_HERO_INTERACTION_V8;
  });
})();
