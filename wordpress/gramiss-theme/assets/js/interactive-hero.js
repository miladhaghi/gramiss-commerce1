(() => {
  const heroes = [...document.querySelectorAll('[data-g1-floating-hero]')];
  if (!heroes.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const GRAMISS_HOME_HERO_MOTION_V4 = true;

  heroes.forEach((hero) => {
    const track = hero.querySelector('[data-g1-floating-track]');
    const products = [...hero.querySelectorAll('[data-g1-floating-product]')];
    if (!track || !products.length) return;

    let motionFrame = 0;
    let visible = true;
    let currentX = 0;
    let currentY = 0;
    let currentStrength = 0;
    let targetX = 0;
    let targetY = 0;
    let targetStrength = 0;

    const renderMotion = () => {
      const nx = clamp(currentX, -1, 1);
      const ny = clamp(currentY, -1, 1);
      const strength = clamp(currentStrength, 0, 1);

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

    const animateToTarget = () => {
      if (reduceMotion || coarse || document.hidden || !visible) {
        motionFrame = 0;
        return;
      }

      currentX += (targetX - currentX) * .38;
      currentY += (targetY - currentY) * .38;
      currentStrength += (targetStrength - currentStrength) * .34;

      if (Math.abs(targetX - currentX) < .0005) currentX = targetX;
      if (Math.abs(targetY - currentY) < .0005) currentY = targetY;
      if (Math.abs(targetStrength - currentStrength) < .0005) currentStrength = targetStrength;

      renderMotion();

      const settled =
        Math.abs(targetX - currentX) < .001 &&
        Math.abs(targetY - currentY) < .001 &&
        Math.abs(targetStrength - currentStrength) < .001;

      if (settled) {
        motionFrame = 0;
        return;
      }

      motionFrame = requestAnimationFrame(animateToTarget);
    };

    const requestMotion = () => {
      if (!motionFrame && !reduceMotion && !coarse && visible && !document.hidden) {
        motionFrame = requestAnimationFrame(animateToTarget);
      }
    };

    const resetMotion = () => {
      targetX = 0;
      targetY = 0;
      targetStrength = 0;
      requestMotion();
    };

    if (!coarse && !reduceMotion) {
      hero.addEventListener('pointerenter', () => {
        targetStrength = 1;
        hero.classList.add('is-motion-tracking');
        requestMotion();
      }, { passive: true });

      hero.addEventListener('pointermove', (event) => {
        const rect = hero.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        targetX = clamp(((event.clientX - rect.left) / rect.width - .5) * 2, -1, 1);
        targetY = clamp(((event.clientY - rect.top) / rect.height - .5) * 2, -1, 1);
        targetStrength = 1;
        requestMotion();
      }, { passive: true });

      hero.addEventListener('pointerleave', () => {
        hero.classList.remove('is-motion-tracking');
        resetMotion();
      }, { passive: true });
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

    // Horizontal mobile category rail only. No vertical-scroll-driven hero motion.
    let railFrame = 0;
    track.addEventListener('scroll', () => {
      if (window.innerWidth > 820) return;
      cancelAnimationFrame(railFrame);
      railFrame = requestAnimationFrame(updateActive);
    }, { passive: true });

    window.addEventListener('resize', () => {
      if (window.innerWidth <= 820) updateActive();
    }, { passive: true });

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

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        const entry = entries[0];
        visible = Boolean(entry && entry.isIntersecting);
        if (!visible) {
          if (motionFrame) cancelAnimationFrame(motionFrame);
          motionFrame = 0;
        }
      }, { rootMargin: '120px 0px', threshold: 0 });
      observer.observe(hero);
    }

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        if (motionFrame) cancelAnimationFrame(motionFrame);
        motionFrame = 0;
      } else {
        requestMotion();
      }
    });

    requestAnimationFrame(updateActive);
    void GRAMISS_HOME_HERO_MOTION_V4;
  });
})();
