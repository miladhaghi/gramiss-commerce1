(() => {
  const heroes = [...document.querySelectorAll('[data-g1-interactive-hero]')];
  if (!heroes.length) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarsePointer = window.matchMedia('(pointer: coarse)').matches;
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

  heroes.forEach((hero) => {
    const stage = hero.querySelector('.g1-interactive-stage');
    const art = hero.querySelector('.g1-interactive-art');
    const links = [...hero.querySelectorAll('.g1-hero-object')];
    if (!stage || !art || !links.length) return;

    let frame = 0;
    let idleFrame = 0;
    let idlePhase = Math.random() * Math.PI * 2;

    const clearNearest = () => {
      links.forEach((link) => link.classList.remove('is-near'));
    };

    const apply = (x, y, strength = 1) => {
      const clampedX = clamp(x, -1, 1);
      const clampedY = clamp(y, -1, 1);
      const rotateY = clampedX * 3.8 * strength;
      const rotateX = clampedY * -3 * strength;
      const translateX = clampedX * 3.5 * strength;
      const translateY = clampedY * 2.5 * strength;

      stage.style.setProperty('--hero-ry', `${rotateY.toFixed(2)}deg`);
      stage.style.setProperty('--hero-rx', `${rotateX.toFixed(2)}deg`);
      stage.style.setProperty('--hero-tx', `${translateX.toFixed(2)}px`);
      stage.style.setProperty('--hero-ty', `${translateY.toFixed(2)}px`);
      stage.style.setProperty('--hero-light-x', `${(50 + clampedX * 25).toFixed(1)}%`);
      stage.style.setProperty('--hero-light-y', `${(45 + clampedY * 20).toFixed(1)}%`);

      links.forEach((link) => {
        const depth = Number.parseFloat(link.dataset.depth || '1');
        link.style.setProperty('--object-parallax-x', `${(clampedX * depth * 9 * strength).toFixed(2)}px`);
        link.style.setProperty('--object-parallax-y', `${(clampedY * depth * 7 * strength).toFixed(2)}px`);
      });
    };

    const nearestObject = (event) => {
      const stageRect = stage.getBoundingClientRect();
      let nearest = null;
      let nearestDistance = Number.POSITIVE_INFINITY;

      links.forEach((link) => {
        const label = link.querySelector('.g1-object-label');
        const targetRect = label ? label.getBoundingClientRect() : link.getBoundingClientRect();
        const centerX = targetRect.left + targetRect.width / 2;
        const centerY = targetRect.top + targetRect.height / 2;
        const distance = Math.hypot(event.clientX - centerX, event.clientY - centerY);

        if (distance < nearestDistance) {
          nearest = link;
          nearestDistance = distance;
        }
      });

      const revealRadius = Math.max(92, Math.min(stageRect.width, stageRect.height) * .32);
      links.forEach((link) => link.classList.toggle('is-near', link === nearest && nearestDistance <= revealRadius));
    };

    const pointerPosition = (event) => {
      const rect = stage.getBoundingClientRect();
      if (!rect.width || !rect.height) return { x: 0, y: 0 };
      return {
        x: ((event.clientX - rect.left) / rect.width - .5) * 2,
        y: ((event.clientY - rect.top) / rect.height - .5) * 2,
      };
    };

    const reset = () => {
      stage.classList.remove('is-active');
      clearNearest();
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => apply(0, 0, 1));
    };

    stage.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      stage.classList.add('is-active');
    });

    stage.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch' || coarsePointer) return;
      const { x, y } = pointerPosition(event);
      nearestObject(event);
      if (reducedMotion) return;
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => apply(x, y, 1));
    });

    stage.addEventListener('pointerleave', (event) => {
      if (event.pointerType !== 'touch') reset();
    });

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

      idlePhase += coarsePointer ? .007 : .004;
      apply(Math.sin(idlePhase) * .14, Math.cos(idlePhase * .8) * .11, .58);
      idleFrame = requestAnimationFrame(idle);
    };

    if (!reducedMotion) idleFrame = requestAnimationFrame(idle);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && !idleFrame && !reducedMotion) idleFrame = requestAnimationFrame(idle);
    });
  });
})();
