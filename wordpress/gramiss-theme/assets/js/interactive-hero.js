(() => {
  const heroes = [...document.querySelectorAll('[data-g1-interactive-hero]')];
  if (!heroes.length) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarsePointer = window.matchMedia('(pointer: coarse)').matches;

  heroes.forEach((hero) => {
    const stage = hero.querySelector('.g1-interactive-stage');
    const art = hero.querySelector('.g1-interactive-art');
    const links = [...hero.querySelectorAll('.g1-hero-object')];
    if (!stage || !art) return;

    const legacyHeroImage = art.style.getPropertyValue('--hero-image');
    if (legacyHeroImage && !hero.style.getPropertyValue('--hero-image')) {
      hero.style.setProperty('--hero-image', legacyHeroImage);
    }

    let frame = 0;
    let activePointer = null;
    let pointerStartX = 0;
    let pointerStartY = 0;
    let dragged = false;
    let suppressClickUntil = 0;
    let idlePhase = Math.random() * Math.PI * 2;
    let idleFrame = 0;

    const apply = (x, y, strength = 1) => {
      const clampedX = Math.max(-1, Math.min(1, x));
      const clampedY = Math.max(-1, Math.min(1, y));
      const rotateY = clampedX * 7 * strength;
      const rotateX = clampedY * -5.5 * strength;
      const translateX = clampedX * 8 * strength;
      const translateY = clampedY * 6 * strength;
      const lightX = 50 + clampedX * 22;
      const lightY = 45 + clampedY * 18;

      stage.style.setProperty('--hero-ry', `${rotateY.toFixed(2)}deg`);
      stage.style.setProperty('--hero-rx', `${rotateX.toFixed(2)}deg`);
      stage.style.setProperty('--hero-tx', `${translateX.toFixed(2)}px`);
      stage.style.setProperty('--hero-ty', `${translateY.toFixed(2)}px`);
      stage.style.setProperty('--hero-light-x', `${lightX.toFixed(1)}%`);
      stage.style.setProperty('--hero-light-y', `${lightY.toFixed(1)}%`);
    };

    const reset = () => {
      stage.classList.remove('is-active');
      stage.classList.remove('is-dragging');
      activePointer = null;
      dragged = false;
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => apply(0, 0, 1));
    };

    const pointerPosition = (event) => {
      const rect = stage.getBoundingClientRect();
      if (!rect.width || !rect.height) return { x: 0, y: 0 };
      return {
        x: ((event.clientX - rect.left) / rect.width - 0.5) * 2,
        y: ((event.clientY - rect.top) / rect.height - 0.5) * 2,
      };
    };

    stage.addEventListener('pointerenter', (event) => {
      if (reducedMotion || event.pointerType === 'touch') return;
      stage.classList.add('is-active');
    });

    stage.addEventListener('pointermove', (event) => {
      if (reducedMotion) return;
      if (event.pointerType === 'touch' && activePointer !== event.pointerId) return;

      if (activePointer === event.pointerId) {
        const distance = Math.hypot(event.clientX - pointerStartX, event.clientY - pointerStartY);
        if (!dragged && distance > 10) {
          dragged = true;
          stage.classList.add('is-dragging');
          try { stage.setPointerCapture(event.pointerId); } catch (_) {}
        }
      }

      const { x, y } = pointerPosition(event);
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => apply(x, y, event.pointerType === 'touch' ? 0.52 : 1));
    });

    stage.addEventListener('pointerleave', (event) => {
      if (event.pointerType !== 'touch' && activePointer === null) reset();
    });

    stage.addEventListener('pointerdown', (event) => {
      activePointer = event.pointerId;
      pointerStartX = event.clientX;
      pointerStartY = event.clientY;
      dragged = false;
      stage.classList.add('is-active');
      if (reducedMotion) return;
      const { x, y } = pointerPosition(event);
      apply(x, y, event.pointerType === 'touch' ? 0.52 : 1);
    });

    stage.addEventListener('pointerup', (event) => {
      if (activePointer !== event.pointerId) return;
      if (dragged) suppressClickUntil = performance.now() + 450;
      try { stage.releasePointerCapture(event.pointerId); } catch (_) {}

      stage.classList.remove('is-dragging');
      activePointer = null;
      dragged = false;

      if (event.pointerType === 'touch') {
        window.setTimeout(reset, 160);
      } else if (!stage.matches(':hover')) {
        reset();
      }
    });

    stage.addEventListener('pointercancel', reset);

    stage.addEventListener('click', (event) => {
      const link = event.target.closest('.g1-hero-object');
      if (!link || performance.now() >= suppressClickUntil) return;
      event.preventDefault();
      event.stopImmediatePropagation();
    }, true);

    links.forEach((link) => {
      link.addEventListener('focus', () => link.classList.add('is-hovered'));
      link.addEventListener('blur', () => link.classList.remove('is-hovered'));
      link.addEventListener('pointerenter', () => link.classList.add('is-hovered'));
      link.addEventListener('pointerleave', () => link.classList.remove('is-hovered'));
      link.addEventListener('dragstart', (event) => event.preventDefault());
    });

    const idle = () => {
      if (reducedMotion || document.hidden || stage.matches(':hover') || stage.classList.contains('is-active')) {
        idleFrame = requestAnimationFrame(idle);
        return;
      }

      idlePhase += coarsePointer ? 0.007 : 0.004;
      apply(Math.sin(idlePhase) * 0.16, Math.cos(idlePhase * 0.8) * 0.12, 0.6);
      idleFrame = requestAnimationFrame(idle);
    };

    if (!reducedMotion) idleFrame = requestAnimationFrame(idle);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && !idleFrame && !reducedMotion) idleFrame = requestAnimationFrame(idle);
    });
  });
})();
