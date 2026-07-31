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

  document.querySelectorAll('[data-g1-submit-search]').forEach((trigger) => {
    trigger.addEventListener('click', () => trigger.closest('form')?.requestSubmit());
  });
})();
