(() => {
  const heroes = [...document.querySelectorAll('[data-g1-floating-hero]')];
  if (!heroes.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const GRAMISS_HOME_HERO_MOTION_V3 = true;

  heroes.forEach((hero) => {
    const track = hero.querySelector('[data-g1-floating-track]');
    const products = [...hero.querySelectorAll('[data-g1-floating-product]')];
    if (!track || !products.length) return;

    let scrollFrame = 0;
    let motionFrame = 0;
    let pointerInside = false;
    let idlePhase = Math.random() * Math.PI * 2;
    let idleResumeAt = 0;

    let currentX = 0;
    let currentY = 0;
    let targetX = 0;
    let targetY = 0;
    let currentStrength = 0;
    let targetStrength = 0;

    const renderMotion = (x, y, strength) => {
      const nx = clamp(x, -1, 1);
      const ny = clamp(y, -1, 1);

      // Move the already-rendered light layer instead of repainting its gradient.
      hero.style.setProperty('--hero-light-tx', `${(nx * 15 * strength).toFixed(2)}px`);
      hero.style.setProperty('--hero-light-ty', `${(ny * 10 * strength).toFixed(2)}px`);
      hero.style.setProperty('--copy-x', `${(-nx * 2.4 * strength).toFixed(2)}px`);
      hero.style.setProperty('--copy-y', `${(-ny * 1.6 * strength).toFixed(2)}px`);

      products.forEach((item, index) => {
        const depth = Number.parseFloat(item.dataset.depth || '1');
        const sign = index % 2 === 0 ? 1 : -1;
        item.style.setProperty('--px', `${(nx * depth * 10.5 * strength).toFixed(2)}px`);
        item.style.setProperty('--py', `${(ny * depth * 7.6 * strength).toFixed(2)}px`);
        item.style.setProperty('--tilt', `${(nx * depth * .5 * sign * strength).toFixed(2)}deg`);
      });
    };

    const motionLoop = (time) => {
      if (reduceMotion || coarse || document.hidden) {
        motionFrame = requestAnimationFrame(motionLoop);
        return;
      }

      if (!pointerInside && time >= idleResumeAt) {
        idlePhase += .0036;
        targetX = Math.sin(idlePhase) * .075;
        targetY = Math.cos(idlePhase * .78) * .052;
        targetStrength = .38;
      }

      // ~30% interpolation per frame feels connected to the pointer without looking robotic.
      const follow = pointerInside ? .34 : .18;
      currentX += (targetX - currentX) * follow;
      currentY += (targetY - currentY) * follow;
      currentStrength += (targetStrength - currentStrength) * (pointerInside ? .30 : .14);

      if (Math.abs(targetX - currentX) < .0002) currentX = targetX;
      if (Math.abs(targetY - currentY) < .0002) currentY = targetY;
      if (Math.abs(targetStrength - currentStrength) < .0002) currentStrength = targetStrength;

      renderMotion(currentX, currentY, currentStrength);
      motionFrame = requestAnimationFrame(motionLoop);
    };

    if (!coarse && !reduceMotion) {
      hero.addEventListener('pointerenter', () => {
        pointerInside = true;
        targetStrength = 1;
        hero.classList.add('is-motion-tracking');
      });

      hero.addEventListener('pointermove', (event) => {
        const rect = hero.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        targetX = clamp(((event.clientX - rect.left) / rect.width - .5) * 2, -1, 1);
        targetY = clamp(((event.clientY - rect.top) / rect.height - .5) * 2, -1, 1);
        targetStrength = 1;
      }, { passive: true });

      hero.addEventListener('pointerleave', () => {
        pointerInside = false;
        targetX = 0;
        targetY = 0;
        targetStrength = 1;
        idleResumeAt = performance.now() + 850;
        hero.classList.remove('is-motion-tracking');
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

    requestAnimationFrame(() => {
      updateActive();
      updateMobileScrollDepth();
      if (!reduceMotion && !coarse) motionFrame = requestAnimationFrame(motionLoop);
    });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && !reduceMotion && !coarse && !motionFrame) {
        motionFrame = requestAnimationFrame(motionLoop);
      }
    });

    void GRAMISS_HOME_HERO_MOTION_V3;
  });
})();
