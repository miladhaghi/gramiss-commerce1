(() => {
  const HERO_SELECTOR = '.page-shell > .hero[data-node-id="15:29"]';
  const categories = [
    {
      key: "cap",
      label: "کلاه کپ",
      english: "CAPS",
      href: "/shop?category=caps",
      image: "/assets/hero-cap.webp",
    },
    {
      key: "bag",
      label: "کیف مردانه",
      english: "BAGS",
      href: "/shop?category=bags",
      image: "/assets/hero-bag.webp",
    },
    {
      key: "socks",
      label: "جوراب",
      english: "SOCKS",
      href: "/shop?category=socks",
      image: "/assets/hero-socks.webp",
    },
    {
      key: "tshirt",
      label: "تیشرت",
      english: "T-SHIRTS",
      href: "/shop?category=t-shirts",
      image: "/assets/hero-tshirt.webp",
    },
    {
      key: "sneakers",
      label: "کتونی",
      english: "SNEAKERS",
      href: "/shop?category=sneakers",
      image: "/assets/hero-sneakers.webp",
    },
    {
      key: "jeans",
      label: "شلوار جین",
      english: "JEANS",
      href: "/shop?category=trousers",
      image: "/assets/hero-jeans.webp",
    },
  ];

  function createLabel(item) {
    const label = document.createElement("span");
    label.className = "hero-category-label";
    label.dir = "rtl";
    label.innerHTML = `
      <strong>${item.label}</strong>
      <small dir="ltr">${item.english}</small>
    `;
    return label;
  }

  function createArtwork(item, eager = false) {
    const image = document.createElement("img");
    image.src = item.image;
    image.alt = "";
    image.width = 1100;
    image.height = 1100;
    image.decoding = "async";
    image.loading = eager ? "eager" : "lazy";
    image.draggable = false;
    if (eager) image.fetchPriority = "high";
    return image;
  }

  function createCategoryLink(item, className, eager = false) {
    const link = document.createElement("a");
    link.className = `${className} is-${item.key}`;
    link.href = item.href;
    link.setAttribute("aria-label", `مشاهده دسته ${item.label}`);
    link.append(createArtwork(item, eager), createLabel(item));
    return link;
  }

  function buildDesktopStage(hero) {
    const stage = document.createElement("nav");
    stage.className = "hero-product-stage";
    stage.setAttribute("aria-label", "دسته‌بندی‌های اصلی Gramiss");

    categories.forEach((item) => {
      const eager = item.key === "bag" || item.key === "tshirt" || item.key === "jeans";
      stage.append(createCategoryLink(item, "hero-product", eager));
    });

    hero.append(stage);
    return stage;
  }

  function buildMobileRail(hero) {
    const region = document.createElement("section");
    region.className = "hero-mobile-categories";
    region.setAttribute("aria-label", "دسته‌بندی‌ها؛ با کشیدن انگشت پیمایش کنید");

    const track = document.createElement("div");
    track.className = "hero-mobile-track";

    categories.forEach((item, index) => {
      track.append(createCategoryLink(item, "hero-mobile-card", index < 2));
    });

    region.append(track);
    hero.append(region);
  }

  function addParallax(hero, stage) {
    const canParallax =
      window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!canParallax) return;

    hero.addEventListener("pointermove", (event) => {
      const bounds = hero.getBoundingClientRect();
      const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
      const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
      stage.style.setProperty("--hero-shift-x", `${x * 9}px`);
      stage.style.setProperty("--hero-shift-y", `${y * 6}px`);
    });

    hero.addEventListener("pointerleave", () => {
      stage.style.setProperty("--hero-shift-x", "0px");
      stage.style.setProperty("--hero-shift-y", "0px");
    });
  }

  function enhanceHero() {
    const hero = document.querySelector(HERO_SELECTOR);
    if (!(hero instanceof HTMLElement) || hero.dataset.gramissHeroEnhanced === "true") return;

    hero.dataset.gramissHeroEnhanced = "true";
    hero.classList.add("gramiss-fashion-hero");

    const legacyStage = hero.querySelector(".hero-stage");
    if (legacyStage instanceof HTMLElement) {
      legacyStage.setAttribute("aria-hidden", "true");
    }

    const stage = buildDesktopStage(hero);
    buildMobileRail(hero);
    addParallax(hero, stage);
  }

  function run() {
    enhanceHero();
    const observer = new MutationObserver(enhanceHero);
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  } else {
    run();
  }
})();
