(() => {
  const reveal = (elements) => {
    if (!('IntersectionObserver' in window)) {
      elements.forEach((el) => el.classList.add('is-visible'));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px' });
    elements.forEach((el) => observer.observe(el));
  };

  reveal([...document.querySelectorAll('.g1-reveal')]);

  const setupProductCarousel = (carousel) => {
    const track = carousel.querySelector('[data-g1-carousel-track]');
    const cards = [...carousel.querySelectorAll('[data-g1-carousel-card]')];
    const previous = carousel.querySelector('[data-g1-carousel-prev]');
    const next = carousel.querySelector('[data-g1-carousel-next]');
    const current = carousel.querySelector('[data-g1-carousel-current]');

    if (!track || cards.length === 0) return;

    carousel.classList.add('is-carousel-enhanced');

    let activeIndex = cards.length > 2 ? 1 : 0;
    let frame = 0;

    const activate = (index, shouldScroll = false) => {
      activeIndex = Math.max(0, Math.min(index, cards.length - 1));
      cards.forEach((card, cardIndex) => {
        const isActive = cardIndex === activeIndex;
        card.classList.toggle('is-carousel-active', isActive);
        if (isActive) card.setAttribute('aria-current', 'true');
        else card.removeAttribute('aria-current');
      });

      if (current) current.textContent = String(activeIndex + 1).padStart(2, '0');
      if (previous) previous.disabled = activeIndex === 0;
      if (next) next.disabled = activeIndex === cards.length - 1;

      if (shouldScroll) {
        const card = cards[activeIndex];
        const target = card.offsetLeft - ((track.clientWidth - card.offsetWidth) / 2);
        track.scrollTo({ left: target, behavior: 'smooth' });
      }
    };

    const updateFromScroll = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const trackCenter = track.getBoundingClientRect().left + (track.clientWidth / 2);
        let closestIndex = 0;
        let closestDistance = Number.POSITIVE_INFINITY;

        cards.forEach((card, index) => {
          const bounds = card.getBoundingClientRect();
          const distance = Math.abs((bounds.left + (bounds.width / 2)) - trackCenter);
          if (distance < closestDistance) {
            closestDistance = distance;
            closestIndex = index;
          }
        });

        if (closestIndex !== activeIndex) activate(closestIndex);
      });
    };

    activate(activeIndex);
    requestAnimationFrame(() => {
      if (activeIndex > 0) {
        const card = cards[activeIndex];
        track.scrollLeft = card.offsetLeft - ((track.clientWidth - card.offsetWidth) / 2);
      }
      updateFromScroll();
    });

    track.addEventListener('scroll', updateFromScroll, { passive: true });
    window.addEventListener('resize', updateFromScroll, { passive: true });
    previous?.addEventListener('click', () => activate(activeIndex - 1, true));
    next?.addEventListener('click', () => activate(activeIndex + 1, true));
    cards.forEach((card, index) => {
      card.addEventListener('focusin', () => activate(index, true));
    });
  };

  document.querySelectorAll('[data-g1-product-carousel]').forEach(setupProductCarousel);

  document.querySelectorAll('[data-g1-submit-search]').forEach((trigger) => {
    trigger.addEventListener('click', () => trigger.closest('form')?.requestSubmit());
  });
})();
