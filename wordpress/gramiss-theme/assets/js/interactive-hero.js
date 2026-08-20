(() => {
  const heroes = [...document.querySelectorAll('[data-g1-floating-hero]')];
  if (!heroes.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const GRAMISS_HOME_HERO_V2 = true;

  heroes.forEach((hero) => {
    const track = hero.querySelector('[data-g1-floating-track]');
    const products = [...hero.querySelectorAll('[data-g1-floating-product]')];
    if (!track || !products.length) return;

    let pointerFrame = 0;
    let scrollFrame = 0;
    let idleFrame = 0;
    let pointerInside = false;
    let idlePhase = Math.random() * Math.PI * 2;

    const setProductMotion = (x, y, strength = 1) => {
      const nx = clamp(x, -1, 1);
      const ny = clamp(y, -1, 1);

      hero.style.setProperty('--hero-light-x', `${(50 + nx * 8).toFixed(1)}%`);
      hero.style.setProperty('--hero-light-y', `${(31 + ny * 5).toFixed(1)}%`);
      hero.style.setProperty('--copy-x', `${(-nx * 2.2 * strength).toFixed(2)}px`);
      hero.style.setProperty('--copy-y', `${(-ny * 1.5 * strength).toFixed(2)}px`);

      products.forEach((item, index) => {
        const depth = Number.parseFloat(item.dataset.depth || '1');
        const sign = index % 2 === 0 ? 1 : -1;
        item.style.setProperty('--px', `${(nx * depth * 8.5 * strength).toFixed(2)}px`);
        item.style.setProperty('--py', `${(ny * depth * 6.2 * strength).toFixed(2)}px`);
        item.style.setProperty('--tilt', `${(nx * depth * .45 * sign * strength).toFixed(2)}deg`);
      });
    };

    const resetPointerMotion = () => {
      if (pointerFrame) cancelAnimationFrame(pointerFrame);
      pointerFrame = requestAnimationFrame(() => setProductMotion(0, 0, 1));
    };

    if (!coarse && !reduceMotion) {
      hero.addEventListener('pointerenter', () => {
        pointerInside = true;
      });

      hero.addEventListener('pointermove', (event) => {
        const rect = hero.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        const x = ((event.clientX - rect.left) / rect.width - .5) * 2;
        const y = ((event.clientY - rect.top) / rect.height - .5) * 2;
        cancelAnimationFrame(pointerFrame);
        pointerFrame = requestAnimationFrame(() => setProductMotion(x, y, 1));
      });

      hero.addEventListener('pointerleave', () => {
        pointerInside = false;
        resetPointerMotion();
      });
    }

    const updateActive = () => {
      if (window.innerWidth > 820) return;
      const rect = track.getBoundingClientRect();
      const center = rect.left + track.clientWidth / 2;
      let best = products[0];
      let distance = Infinity;

      products.forEach((item) => {
        const itemRect = item.getBoundingClientRect();
        const d = Math.abs((itemRect.left + itemRect.width / 2) - center);
        if (d < distance) {
          distance = d;
          best = item;
        }
      });

      products.forEach((item) => item.classList.toggle('is-active', item === best));
    };

    const updateMobileScrollDepth = () => {
      if (reduceMotion || window.innerWidth > 820) return;
      const rect = hero.getBoundingClientRect();
      const viewportCenter = window.innerHeight / 2;
      const heroCenter = rect.top + rect.height / 2;
      const progress = clamp((heroCenter - viewportCenter) / Math.max(window.innerHeight, 1), -1, 1);

      products.forEach((item) => {
        const depth = Number.parseFloat(item.dataset.depth || '1');
        const media = item.querySelector('.g1-floating-product-media');
        if (!media) return;
        media.style.setProperty('--mobile-drift', `${(progress * depth * -5).toFixed(2)}px`);
      });
    };

    const onScroll = () => {
      cancelAnimationFrame(scrollFrame);
      scrollFrame = requestAnimationFrame(() => {
        updateActive();
        updateMobileScrollDepth();
      });
    };

    track.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });

    products.forEach((item) => {
      item.addEventListener('dragstart', (event) => event.preventDefault());
      let startX = 0;
      let startY = 0;
      let dragged = false;

      item.addEventListener('pointerdown', (event) => {
        startX = event.clientX;
        startY = event.clientY;
        dragged = false;
      });

      item.addEventListener('pointermove', (event) => {
        if (Math.hypot(event.clientX - startX, event.clientY - startY) > 9) dragged = true;
      });

      item.addEventListener('click', (event) => {
        if (dragged) {
          event.preventDefault();
          event.stopPropagation();
        }
      });
    });

    const idle = () => {
      if (reduceMotion || document.hidden || coarse || pointerInside) {
        idleFrame = requestAnimationFrame(idle);
        return;
      }

      idlePhase += .0045;
      const x = Math.sin(idlePhase) * .10;
      const y = Math.cos(idlePhase * .78) * .075;
      setProductMotion(x, y, .48);
      idleFrame = requestAnimationFrame(idle);
    };

    requestAnimationFrame(() => {
      updateActive();
      updateMobileScrollDepth();
      if (!reduceMotion && !coarse) idleFrame = requestAnimationFrame(idle);
    });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && !reduceMotion && !coarse && !idleFrame) {
        idleFrame = requestAnimationFrame(idle);
      }
    });

    void GRAMISS_HOME_HERO_V2;
  });
})();
