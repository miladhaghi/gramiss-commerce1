(() => {
  const categories = [
    { key: "cap", label: "کلاه کپ", english: "CAPS", href: "/shop?category=caps" },
    { key: "bag", label: "کیف مردانه", english: "BAGS", href: "/shop?category=bags" },
    { key: "socks", label: "جوراب", english: "SOCKS", href: "/shop?category=socks" },
    { key: "tshirt", label: "تیشرت", english: "T-SHIRTS", href: "/shop?category=t-shirts" },
    { key: "sneakers", label: "کتونی", english: "SNEAKERS", href: "/shop?category=sneakers" },
    { key: "jeans", label: "شلوار جین", english: "JEANS", href: "/shop?category=trousers" },
  ];

  function createCategoryLink(item, className) {
    const link = document.createElement("a");
    link.className = `${className} is-${item.key}`;
    link.href = item.href;
    link.setAttribute("aria-label", `مشاهده دسته ${item.label}`);
    link.innerHTML = `
      <span class="hero-category-label" dir="rtl">
        <strong>${item.label}</strong>
        <small dir="ltr">${item.english}</small>
      </span>
    `;
    return link;
  }

  function enhanceHero() {
    const hero = document.querySelector(".hero");
    if (!(hero instanceof HTMLElement) || hero.dataset.gramissHeroEnhanced === "true") return;

    hero.dataset.gramissHeroEnhanced = "true";
    hero.classList.add("gramiss-fashion-hero");

    const hotspots = document.createElement("nav");
    hotspots.className = "hero-category-hotspots";
    hotspots.setAttribute("aria-label", "دسته‌بندی‌های اصلی Gramiss");
    categories.forEach((item) => hotspots.append(createCategoryLink(item, "hero-hotspot")));
    hero.append(hotspots);

    const mobileRail = document.createElement("div");
    mobileRail.className = "hero-mobile-categories";
    mobileRail.setAttribute("role", "region");
    mobileRail.setAttribute("aria-label", "دسته‌بندی‌ها؛ با کشیدن انگشت پیمایش کنید");

    const mobileTrack = document.createElement("div");
    mobileTrack.className = "hero-mobile-track";
    categories.forEach((item) => mobileTrack.append(createCategoryLink(item, "hero-mobile-card")));
    mobileRail.append(mobileTrack);
    hero.append(mobileRail);

    const canParallax = window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (canParallax) {
      hero.addEventListener("pointermove", (event) => {
        const bounds = hero.getBoundingClientRect();
        const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
        const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
        hero.style.setProperty("--hero-shift-x", `${x * 10}px`);
        hero.style.setProperty("--hero-shift-y", `${y * 7}px`);
      });
      hero.addEventListener("pointerleave", () => {
        hero.style.setProperty("--hero-shift-x", "0px");
        hero.style.setProperty("--hero-shift-y", "0px");
      });
    }
  }

  async function loadHeroArtwork() {
    const partUrls = Array.from(
      { length: 6 },
      (_, index) => `/assets/hero-fashion.part${String(index).padStart(2, "0")}.txt`,
    );

    try {
      const responses = await Promise.all(partUrls.map((url) => fetch(url)));
      if (responses.some((response) => !response.ok)) return;
      const parts = await Promise.all(responses.map((response) => response.text()));
      const dataUri = `url("data:image/webp;base64,${parts.join("")}")`;
      document.documentElement.style.setProperty("--gramiss-hero-art", dataUri);
    } catch {
      // The layout and calls to action stay usable if artwork loading is interrupted.
    }
  }

  function run() {
    enhanceHero();
    void loadHeroArtwork();
    const observer = new MutationObserver(enhanceHero);
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  } else {
    run();
  }
})();
