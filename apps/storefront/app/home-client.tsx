"use client";

// The Home implementation remains isolated so its visual structure is preserved.

/* eslint-disable @next/next/no-img-element */

import {
  FormEvent,
  ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ArrowLeft,
  Heart,
  Menu,
  Search,
  ShoppingBag,
  UserRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { CompareIcon } from "./components/commerce-ui";
import {
  formatToman,
  getCartItemHref,
  type CartItem,
  useGramissStore,
} from "./hooks/use-gramiss-store";
import { useDemoAuth } from "./hooks/use-demo-auth";
import {
  normalizeSearchText,
  readRecentSearches,
  saveRecentSearch,
} from "./lib/search-utils";
import type { Product } from "./lib/product-types";
import { shopProducts } from "./shop/shop-data";

type FeaturedCategory = {
  number: string;
  english: string;
  persian: string;
  description: string;
  image: string;
  dark?: boolean;
};

export type { Product } from "./lib/product-types";

export type DrawerView = "menu" | "wishlist" | "account" | "cart" | null;

export function getProductHref(
  product: Pick<Product, "id" | "productHref">,
  _fallback = "/shop",
) {
  void _fallback;
  return product.productHref ?? `/product/${product.id}`;
}

const featuredCategories: FeaturedCategory[] = [
  {
    number: "01",
    english: "SNEAKERS",
    persian: "کتونی",
    description: "حرکت، راحتی و استایل روزمره",
    image: "/assets/category-sneakers.png",
    dark: true,
  },
  {
    number: "02",
    english: "T-SHIRTS",
    persian: "تیشرت",
    description: "پایه‌ای ساده برای ترکیب‌های بی‌نهایت",
    image: "/assets/category-shirts.png",
  },
  {
    number: "03",
    english: "CAPS",
    persian: "کلاه",
    description: "جزئی کوچک با تأثیری بزرگ",
    image: "/assets/category-caps.png",
  },
  {
    number: "04",
    english: "BAGS",
    persian: "کیف",
    description: "کاربرد روزانه با فرم مینیمال",
    image: "/assets/category-bags.png",
  },
];

const allCategories = [
  ["01", "کیف", "BAGS"],
  ["02", "کلاه", "CAPS"],
  ["03", "کتونی", "SNEAKERS"],
  ["04", "جوراب", "SOCKS"],
  ["05", "تیشرت", "T-SHIRTS"],
  ["06", "پیراهن", "SHIRTS"],
  ["07", "شلوار", "TROUSERS"],
  ["08", "لباس زیر", "UNDERWEAR"],
  ["09", "کمربند", "BELTS"],
  ["10", "جاکلیدی", "KEYCHAINS"],
] as const;

const featuredProductIds = new Set([
  "daily-sneaker",
  "essential-tshirt",
  "sky-blue-cap",
  "crossbody-bag",
]);

export const products: Product[] = shopProducts.filter((product) =>
  featuredProductIds.has(product.id),
);

const reasons = [
  [
    "01",
    "راهنمای خرید واقعی",
    "اطلاعات کاربردی درباره جنس، دوام، قواره و نحوه استفاده؛ درست در کنار محصول.",
  ],
  [
    "02",
    "انتخاب بدون فشار",
    "مسیر خرید کوتاه و شفاف، بدون فروشندگی تهاجمی و بدون ترس از قضاوت شدن.",
  ],
  [
    "03",
    "کیفیت قبل از قیمت",
    "تمرکز بر ارزش واقعی محصول و چیزی که بعد از خرید و استفاده برایت باقی می‌ماند.",
  ],
  [
    "04",
    "پیشنهاد هوشمند",
    "زیرساختی برای پیشنهاد محصول متناسب با نیاز، استایل و موقعیت استفاده تو.",
  ],
] as const;

const primaryNavigation = [
  ["Shop", "/shop"],
  ["Collections", "/#collections"],
  ["Journal", "/#journal"],
  ["About", "/#about"],
] as const;

export function Button({
  children,
  variant = "primary",
  href,
  onClick,
  className = "",
}: {
  children: ReactNode;
  variant?: "primary" | "secondary" | "accent";
  href?: string;
  onClick?: () => void;
  className?: string;
}) {
  const classes = `button button-${variant} ${className}`.trim();

  if (href) {
    return (
      <a className={classes} href={href} onClick={onClick}>
        {children}
      </a>
    );
  }

  return (
    <button className={classes} type="button" onClick={onClick}>
      {children}
    </button>
  );
}

export function Header({
  cartCount,
  wishlistCount = 0,
  onSearch,
  onDrawer,
}: {
  cartCount: number;
  wishlistCount?: number;
  onSearch: () => void;
  onDrawer: (view: Exclude<DrawerView, null>) => void;
}) {
  const { hydrated, isAuthenticated, profile } = useDemoAuth();
  const accountHref = hydrated && isAuthenticated ? "/account" : "/login";
  const accountLabel =
    hydrated && isAuthenticated && profile.fullName
      ? `حساب کاربری ${profile.fullName}`
      : "حساب کاربری";

  return (
    <header
      className="site-header"
      aria-label="ناوبری اصلی"
      data-node-id="15:3"
    >
      <div className="header-desktop">
        <div className="header-left-cluster">
          <Link className="wordmark" href="/" aria-label="Gramiss، صفحه اصلی">
            GRAMISS
          </Link>
          <nav className="desktop-nav" aria-label="فهرست اصلی" dir="ltr">
            {primaryNavigation.map(([label, href]) => (
              <a href={href} key={label}>
                {label}
              </a>
            ))}
          </nav>
        </div>
        <div className="header-actions">
          <button
            className="search-trigger"
            type="button"
            aria-label="باز کردن جست‌وجو"
            onClick={onSearch}
          >
            <Search aria-hidden="true" size={18} strokeWidth={1.8} />
            <span>Search products, styles, guides</span>
          </button>
          <span className="header-divider" aria-hidden="true" />
          <Link
            className="icon-button header-wishlist-button"
            href="/wishlist"
            aria-label={`علاقه‌مندی‌ها، ${wishlistCount.toLocaleString("fa-IR")} محصول`}
          >
            <Heart aria-hidden="true" size={19} strokeWidth={1.8} />
            {wishlistCount ? (
              <span className="wishlist-count">{wishlistCount}</span>
            ) : null}
          </Link>
          <Link
            className="icon-button"
            href={accountHref}
            aria-label={accountLabel}
            title={profile.fullName || undefined}
          >
            <UserRound aria-hidden="true" size={19} strokeWidth={1.8} />
          </Link>
          <button
            className="cart-button"
            type="button"
            aria-label={`سبد خرید، ${cartCount} کالا`}
            onClick={() => onDrawer("cart")}
          >
            <ShoppingBag
              className="cart-glyph"
              aria-hidden="true"
              size={19}
              strokeWidth={1.8}
            />
            <span className="cart-count">{cartCount}</span>
          </button>
        </div>
      </div>

      <div className="header-mobile">
        <div className="mobile-leading-actions">
          <button
            className="mobile-action"
            type="button"
            aria-label="باز کردن منو"
            onClick={() => onDrawer("menu")}
          >
            <Menu aria-hidden="true" size={20} strokeWidth={1.8} />
          </button>
          <button
            className="mobile-action"
            type="button"
            aria-label="جست‌وجو"
            onClick={onSearch}
          >
            <Search aria-hidden="true" size={19} strokeWidth={1.8} />
          </button>
        </div>
        <Link className="wordmark" href="/" aria-label="Gramiss، صفحه اصلی">
          GRAMISS
        </Link>
        <div className="mobile-actions">
          <Link
            className="mobile-action header-wishlist-button"
            href="/wishlist"
            aria-label={`علاقه‌مندی‌ها، ${wishlistCount.toLocaleString("fa-IR")} محصول`}
          >
            <Heart aria-hidden="true" size={19} strokeWidth={1.8} />
            {wishlistCount ? (
              <span className="wishlist-count">{wishlistCount}</span>
            ) : null}
          </Link>
          <Link
            className="mobile-action"
            href={accountHref}
            aria-label={accountLabel}
            title={profile.fullName || undefined}
          >
            <UserRound aria-hidden="true" size={19} strokeWidth={1.8} />
          </Link>
          <button
            className="mobile-action mobile-cart"
            type="button"
            aria-label={`سبد خرید، ${cartCount} کالا`}
            onClick={() => onDrawer("cart")}
          >
            <ShoppingBag aria-hidden="true" size={19} strokeWidth={1.8} />
            <span>{cartCount}</span>
          </button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section
      className="hero home-section"
      aria-labelledby="hero-title"
      data-node-id="15:29"
    >
      <div className="hero-content" dir="rtl">
        <p className="eyebrow-pill">
          <span aria-hidden="true" />
          انتخابی هوشمند برای استایل روزمره
        </p>
        <h1 id="hero-title">
          خرید پوشاک،
          <br />
          بدون تردید و حدس
        </h1>
        <p className="hero-description">
          <bdi dir="ltr">Gramiss</bdi> به تو کمک می‌کند جنس، کیفیت و انتخاب مناسب
          را قبل از خرید بهتر بفهمی؛ سریع، بی‌قضاوت و دقیق.
        </p>
        <div className="hero-actions">
        <Button href="/shop">شروع خرید</Button>
          <Button href="#journal" variant="secondary">
            راهنمای انتخاب
          </Button>
        </div>
        <div className="hero-proof" aria-label="مزیت‌های Gramiss">
          <div>
            <strong>۳ دسته اصلی</strong>
            <span>کیف، جوراب، کلاه</span>
          </div>
          <div>
            <strong>تصمیم سریع‌تر</strong>
            <span>راهنمای خرید</span>
          </div>
          <div>
            <strong>خرید مطمئن‌تر</strong>
            <span>تمرکز بر کیفیت</span>
          </div>
        </div>
      </div>
      <img
        className="hero-stage"
        src="/assets/hero-stage.png"
        width="560"
        height="680"
        alt="کلاه آبی آسمانی، محصول منتخب Gramiss"
        fetchPriority="high"
      />
    </section>
  );
}

function SectionHeading({
  eyebrow,
  title,
  link,
  linkHref,
}: {
  eyebrow: string;
  title: string;
  link: string;
  linkHref: string;
}) {
  return (
    <div className="section-heading">
      <div dir="rtl">
        <p>{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      <a href={linkHref}>
        {link}
        <span aria-hidden="true"> ←</span>
      </a>
    </div>
  );
}

function FeaturedCategoryCard({
  item,
}: {
  item: FeaturedCategory;
}) {
  return (
    <a
      className={`featured-category ${item.dark ? "is-dark" : ""}`}
      href="#all-categories"
      aria-label={`مشاهده دسته ${item.persian}`}
    >
      <span className="card-index">{item.number}</span>
      <span className="featured-artwork">
        <img
          src={item.image}
          width="180"
          height="140"
          alt=""
          loading="lazy"
        />
      </span>
      <span className="category-copy" dir="rtl">
        <span className="latin-label" dir="ltr">
          {item.english}
        </span>
        <strong>{item.persian}</strong>
        <span>{item.description}</span>
      </span>
    </a>
  );
}

function FeaturedCategories() {
  return (
    <section
      className="featured home-section"
      id="shop"
      aria-labelledby="featured-title"
      data-node-id="17:29"
    >
      <SectionHeading
        eyebrow="انتخاب‌های برجسته"
        title="دسته‌هایی برای شروع استایل"
        link="مشاهده همه دسته‌ها"
        linkHref="/shop"
      />
      <div
        className="featured-grid"
        aria-label="دسته‌های برجسته؛ در موبایل به صورت افقی قابل پیمایش است"
      >
        {featuredCategories.map((item) => (
          <FeaturedCategoryCard item={item} key={item.english} />
        ))}
      </div>
    </section>
  );
}

function AllCategoryCard({
  number,
  persian,
  english,
}: {
  number: string;
  persian: string;
  english: string;
}) {
  return (
    <a
      className="browse-card"
      href="#products"
      aria-label={`مشاهده محصولات ${persian}`}
    >
      <span className="browse-top" dir="ltr">
        <span>{number}</span>
        <span className="browse-arrow" aria-hidden="true">
          ↗
        </span>
      </span>
      <span className="browse-labels" dir="rtl">
        <strong>{persian}</strong>
        <span className="latin-label" dir="ltr">
          {english}
        </span>
      </span>
    </a>
  );
}

function BrowseCategories() {
  return (
    <section
      className="browse home-section"
      id="all-categories"
      aria-labelledby="all-categories-title"
      data-node-id="17:79"
    >
      <div className="browse-heading">
        <h2 id="all-categories-title" dir="rtl">
          همه دسته‌بندی‌ها
        </h2>
        <p dir="rtl">از پوشاک اصلی تا جزئیات تکمیل‌کننده استایل</p>
      </div>
      <div className="browse-grid">
        {allCategories.map(([number, persian, english]) => (
          <AllCategoryCard
            key={english}
            number={number}
            persian={persian}
            english={english}
          />
        ))}
      </div>
    </section>
  );
}

export function ProductCard({
  product,
  active,
  compared,
  onToggleWishlist,
  onToggleCompare,
}: {
  product: Product;
  active: boolean;
  compared: boolean;
  onToggleWishlist: (product: Product) => void;
  onToggleCompare: (product: Product) => void;
}) {
  const productHref = getProductHref(product, "");

  return (
    <article
      className="product-card"
      id={`product-${product.id}`}
      data-product-id={product.id}
    >
      <a
        className="product-media"
        href={productHref}
        aria-label={`مشاهده ${product.name}`}
      >
        <span className="product-badge" dir="rtl">
          {product.badge}
        </span>
        <img
          src={product.image}
          width="221"
          height="235"
          alt={product.name}
          loading="lazy"
        />
      </a>
      <button
        className={`wishlist-button ${active ? "is-active" : ""}`}
        type="button"
        aria-label={
          active
            ? `حذف ${product.name} از علاقه‌مندی‌ها`
            : `افزودن ${product.name} به علاقه‌مندی‌ها`
        }
        aria-pressed={active}
        onClick={() => onToggleWishlist(product)}
      >
        <Heart
          aria-hidden="true"
          size={21}
          strokeWidth={1.8}
          fill={active ? "currentColor" : "none"}
        />
      </button>
      <button
        className={`compare-button ${compared ? "is-active" : ""}`}
        type="button"
        aria-label={
          compared
            ? `مشاهده ${product.name} در مقایسه`
            : `افزودن ${product.name} به مقایسه`
        }
        aria-pressed={compared}
        onClick={() => onToggleCompare(product)}
      >
        <CompareIcon />
      </button>
      <a
        className="product-info"
        href={productHref}
        dir="rtl"
      >
        <span className="product-category">{product.category}</span>
        <strong>{product.name}</strong>
        <span className="latin-label" dir="ltr">
          {product.english}
        </span>
        <b>{product.price}</b>
      </a>
    </article>
  );
}

function FeaturedProducts({
  wishlisted,
  compared,
  onToggleWishlist,
  onToggleCompare,
}: {
  wishlisted: Set<string>;
  compared: Set<string>;
  onToggleWishlist: (product: Product) => void;
  onToggleCompare: (product: Product) => void;
}) {
  return (
    <section
      className="products home-section"
      id="products"
      aria-labelledby="products-title"
      data-node-id="18:29"
    >
      <SectionHeading
        eyebrow="CURATED FOR GRAMISS"
        title="محصولات منتخب"
        link="مشاهده همه محصولات"
        linkHref="/shop"
      />
      <div className="products-grid">
        {products.map((product) => (
          <ProductCard
            product={product}
            active={wishlisted.has(product.id)}
            compared={compared.has(product.id)}
            onToggleWishlist={onToggleWishlist}
            onToggleCompare={onToggleCompare}
            key={product.id}
          />
        ))}
      </div>
    </section>
  );
}

function CampaignSection() {
  return (
    <section
      className="campaign home-section"
      id="collections"
      aria-labelledby="campaign-title"
      data-node-id="22:29"
    >
      <span className="campaign-rule" aria-hidden="true" />
      <div className="campaign-content">
        <p className="campaign-label">GRAMISS / CAPSULE 01</p>
        <h2 id="campaign-title" dir="rtl">
          <span>کالکشن شهری؛</span>
          <span>کمتر انتخاب کن، بهتر بپوش</span>
        </h2>
        <p className="campaign-description" dir="rtl">
          ترکیبی محدود از کتونی، تیشرت، کیف و کلاه برای ساخت یک استایل مینیمال
          و هماهنگ در استفاده روزمره.
        </p>
        <div className="campaign-tags" dir="rtl">
          <span>۴ محصول منتخب</span>
          <span>عرضه محدود</span>
          <span>استایل شهری</span>
        </div>
        <Button href="#products" variant="accent" className="campaign-button">
          مشاهده کالکشن
          <span aria-hidden="true">↗</span>
        </Button>
      </div>
      <img
        className="campaign-stage"
        src="/assets/campaign-stage.png"
        width="640"
        height="520"
        alt="محصولات کالکشن محدود شهری Gramiss"
        loading="lazy"
      />
    </section>
  );
}

function WhyGramissCard({
  number,
  title,
  description,
  dark,
}: {
  number: string;
  title: string;
  description: string;
  dark: boolean;
}) {
  return (
    <article className={`reason-card ${dark ? "is-dark" : ""}`} dir="rtl">
      <div className="reason-meta" dir="ltr">
        <span>{number}</span>
        <i aria-hidden="true" />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  );
}

function WhyGramiss() {
  return (
    <section
      className="why home-section"
      id="about"
      aria-labelledby="why-title"
      data-node-id="23:2"
    >
      <p className="why-eyebrow">WHY GRAMISS</p>
      <div className="why-intro" dir="rtl">
        <h2 id="why-title">خرید پوشاک، با تصمیمی روشن‌تر</h2>
        <p>
          <bdi dir="ltr">Gramiss</bdi> فقط محصول نمایش نمی‌دهد؛ اطلاعات لازم برای
          انتخاب بهتر را هم در اختیارت می‌گذارد تا بدون فشار، سردرگمی یا قضاوت
          خرید کنی.
        </p>
      </div>
      <span className="why-divider" aria-hidden="true" />
      <div className="reason-grid">
        {reasons.map(([number, title, description], index) => (
          <WhyGramissCard
            key={number}
            number={number}
            title={title}
            description={description}
            dark={index === 3}
          />
        ))}
      </div>
    </section>
  );
}

function ArticleCard({
  type,
}: {
  type: "featured" | "care" | "size";
}) {
  if (type === "featured") {
    return (
      <a
        className="article-featured"
        href="#journal"
        aria-label="مطالعه راهنمای پارچه"
      >
        <img
          className="fabric-accent"
          src="/assets/fabric-accent.png"
          width="360"
          height="270"
          alt=""
          loading="lazy"
        />
        <span className="article-tag">راهنمای پارچه</span>
        <span className="article-number">01</span>
        <span className="fabric-folds" aria-hidden="true">
          <i />
          <i />
          <i />
          <i />
          <i />
        </span>
        <h3 dir="rtl">
          پنبه، پلی‌استر یا ویسکوز؟
          <br />
          تفاوتی که بعد از شست‌وشو دیده می‌شود
        </h3>
        <p dir="rtl">
          راهنمای ساده تشخیص جنس پارچه، دوام، تنفس‌پذیری و انتخاب مناسب برای
          استفاده روزمره.
        </p>
        <small dir="rtl">۷ دقیقه مطالعه　•　دانش پایه</small>
      </a>
    );
  }

  if (type === "care") {
    return (
      <a
        className="article-small article-care"
        href="#journal"
        aria-label="مطالعه راهنمای مراقبت و شست‌وشو"
      >
        <span className="article-small-copy" dir="rtl">
          <span className="article-tag">مراقبت و شست‌وشو</span>
          <span className="article-number">02</span>
          <strong>چطور لباس مشکی را دیرتر بور کنیم؟</strong>
          <span className="article-description">
            ۵ اصل ساده برای حفظ رنگ، فرم و بافت لباس بعد از شست‌وشو.
          </span>
          <span className="article-arrow" aria-hidden="true">
            ←
          </span>
        </span>
        <img
          src="/assets/article-care.png"
          width="206"
          height="223"
          alt=""
          loading="lazy"
        />
      </a>
    );
  }

  return (
    <a
      className="article-small article-size"
      href="#journal"
      aria-label="مطالعه راهنمای سایز"
    >
      <span className="article-small-copy" dir="rtl">
        <span className="article-tag">راهنمای سایز</span>
        <span className="article-number">03</span>
        <strong>قواره مناسب را بدون پرو پیدا کن</strong>
        <span className="article-description">
          اندازه‌گیری درست بدن و تشخیص تفاوت قواره‌های اسلیم، رگولار و اورسایز.
        </span>
        <span className="article-arrow" aria-hidden="true">
          ←
        </span>
      </span>
      <span className="size-art" aria-hidden="true">
        <i />
        <b />
        <em />
      </span>
    </a>
  );
}

function KnowledgeGuides() {
  const topics = [
    "پارچه و دوام",
    "راهنمای سایز",
    "مراقبت از محصول",
    "ترند و استایل",
    "انتخاب برای موقعیت",
  ];

  return (
    <section
      className="journal home-section"
      id="journal"
      aria-labelledby="journal-title"
      data-node-id="24:29"
    >
      <p className="journal-eyebrow">GRAMISS JOURNAL</p>
      <h2 id="journal-title" dir="rtl">
        راهنمای انتخاب و استایل
      </h2>
      <p className="journal-subtitle" dir="rtl">
        پیش از خرید، چیزی یاد بگیر که انتخابت را دقیق‌تر و ماندگارتر کند.
      </p>
      <a className="journal-link" href="#journal" dir="rtl">
        مشاهده همه مقاله‌ها
        <span aria-hidden="true"> ←</span>
      </a>
      <div className="journal-grid">
        <ArticleCard type="featured" />
        <div className="journal-small-stack">
          <ArticleCard type="care" />
          <ArticleCard type="size" />
        </div>
      </div>
      <nav className="topic-list" aria-label="موضوعات ژورنال">
        {topics.map((topic) => (
          <a href="#journal" key={topic}>
            {topic}
          </a>
        ))}
      </nav>
    </section>
  );
}

export function NewsletterForm({
  idPrefix = "newsletter",
}: {
  idPrefix?: string;
}) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    if (!validEmail) {
      setStatus("error");
      return;
    }

    setStatus("loading");
    window.setTimeout(() => setStatus("success"), 650);
  }

  const inputId = `${idPrefix}-email`;
  const statusId = `${idPrefix}-status`;

  return (
    <div className="newsletter-form-wrap">
      <form className="newsletter-form" onSubmit={submit} noValidate>
        <label className="sr-only" htmlFor={inputId}>
          ایمیل
        </label>
        <input
          id={inputId}
          name="email"
          type="email"
          placeholder="example@email.com"
          autoComplete="email"
          required
          dir="ltr"
          value={email}
          aria-invalid={status === "error"}
          aria-describedby={statusId}
          onChange={(event) => {
            setEmail(event.target.value);
            if (status !== "idle") setStatus("idle");
          }}
        />
        <button type="submit" disabled={status === "loading"}>
          {status === "loading"
            ? "در حال ثبت"
            : status === "success"
              ? "ثبت شد"
              : "عضویت"}
        </button>
      </form>
      <p
        className={`newsletter-status status-${status}`}
        id={statusId}
        role="status"
      >
        {status === "error"
          ? "لطفاً یک ایمیل معتبر وارد کنید."
          : status === "success"
            ? "عضویت شما با موفقیت ثبت شد."
            : "بدون اسپم  •  لغو اشتراک در هر زمان"}
      </p>
    </div>
  );
}

export function Newsletter({
  variant = "home",
}: {
  variant?: "home" | "shop" | "account";
}) {
  if (variant === "account") {
    return (
      <section
        className="account-newsletter"
        id="newsletter"
        aria-labelledby="account-newsletter-title"
      >
        <div className="account-newsletter-copy" dir="rtl">
          <span>GRAMISS JOURNAL</span>
          <h2 id="account-newsletter-title">انتخاب بهتر، خرید هوشمندتر</h2>
          <p>
            راهنماهای پوشاک، مراقبت محصول و کالکشن‌های تازه را دریافت کنید.
          </p>
        </div>
        <NewsletterForm idPrefix="account-newsletter" />
      </section>
    );
  }

  if (variant === "shop") {
    return (
      <section
        className="shop-newsletter"
        id="newsletter"
        aria-labelledby="shop-newsletter-title"
        data-node-id="30:252"
      >
        <div className="shop-newsletter-copy" dir="rtl">
          <h2 id="shop-newsletter-title">
            به خانواده <bdi dir="ltr">Gramiss</bdi> بپیوند.
          </h2>
          <p>
            جدیدترین کالکشن‌ها و راهنماهای استایل را قبل از همه دریافت کن.
          </p>
        </div>
        <NewsletterForm idPrefix="shop-newsletter" />
      </section>
    );
  }

  return (
    <section
      className="newsletter home-section"
      id="newsletter"
      aria-labelledby="newsletter-title"
      data-node-id="27:27"
    >
      <span className="newsletter-label">PRIVATE EDIT</span>
      <span className="newsletter-monogram" aria-hidden="true">
        G
      </span>
      <div className="newsletter-copy" dir="rtl">
        <h2 id="newsletter-title">
          به خانواده <bdi dir="ltr">Gramiss</bdi> بپیوند.
        </h2>
        <p>
          جدیدترین کالکشن‌ها، راهنماهای استایل و پیشنهادهای اختصاصی را قبل از
          همه دریافت کنید.
        </p>
        <NewsletterForm />
      </div>
    </section>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { label: string; href: string }[];
}) {
  return (
    <nav className="footer-column" aria-label={title} dir="rtl">
      <h3>{title}</h3>
      {links.map(({ label, href }) => (
        <a href={href} key={label}>
          {label}
        </a>
      ))}
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="footer home-section" data-node-id="27:37">
      <div className="footer-brand" dir="ltr">
        <Link className="wordmark" href="/">
          GRAMISS
        </Link>
        <p>Gramiss helps people make better fashion decisions.</p>
      </div>
      <div className="footer-columns">
        <FooterColumn
          title="فروشگاه"
          links={[
            { label: "کتونی", href: "/shop?category=sneakers" },
            { label: "کیف", href: "/shop?category=bags" },
            { label: "جوراب", href: "/shop?category=socks" },
            { label: "کلاه", href: "/shop?category=caps" },
            { label: "لباس", href: "/shop?category=t-shirts" },
          ]}
        />
        <FooterColumn
          title="راهنما"
          links={[
            { label: "پیگیری سفارش", href: "/track-order" },
            { label: "وبلاگ", href: "/#journal" },
            { label: "راهنمای سایز", href: "/#journal" },
            { label: "راهنمای پارچه", href: "/#journal" },
            { label: "سوالات متداول", href: "/#about" },
          ]}
        />
        <FooterColumn
          title="ارتباط"
          links={[
            { label: "Instagram", href: "/#newsletter" },
            { label: "Telegram", href: "/#newsletter" },
            { label: "Email", href: "mailto:hello@gramiss.com" },
          ]}
        />
      </div>
      <div className="footer-promise" dir="rtl">
        <p>انتخاب بهتر، بدون فشار.</p>
        <span dir="ltr">A calmer way to shop fashion.</span>
      </div>
      <div className="footer-bottom" dir="ltr">
        <span>© 2026 Gramiss</span>
        <nav aria-label="قوانین">
          <Link href="/#about">Privacy</Link>
          <Link href="/#about">Terms</Link>
          <Link href="/#about">Cookies</Link>
        </nav>
      </div>
    </footer>
  );
}

export function SearchDialog({
  open,
  onClose,
  onOpenProduct,
  catalog = products,
}: {
  open: boolean;
  onClose: () => void;
  onOpenProduct: (product: Product) => void;
  catalog?: Product[];
}) {
  const dialogRef = useRef<HTMLElement>(null);
  const [query, setQuery] = useState("");
  const [recent, setRecent] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const normalizedQuery = normalizeSearchText(query);

  const results = useMemo(() => {
    if (!normalizedQuery) return catalog.slice(0, 5);
    return catalog
      .filter((product) =>
        [
          product.name,
          product.english,
          product.category,
          product.badge,
          product.description,
          product.material,
          product.color,
          ...(product.colors ?? []),
          ...(product.tags ?? []),
        ].some((value) =>
          normalizeSearchText(value ?? "").includes(normalizedQuery),
        ),
      )
      .slice(0, 5);
  }, [catalog, normalizedQuery]);

  useEffect(() => {
    if (!open) return;
    const stateTimer = window.setTimeout(() => {
      setRecent(readRecentSearches());
      setActiveIndex(-1);
    }, 0);
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(
        dialogRef.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? [],
      );
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.clearTimeout(stateTimer);
      window.removeEventListener("keydown", onKeyDown);
      document.documentElement.style.overflow = previousOverflow;
      previousFocus?.focus();
    };
  }, [onClose, open]);

  if (!open) return null;

  function submitSearch(value = query) {
    const next = value.trim();
    if (!next) return;
    setRecent(saveRecentSearch(next));
    onClose();
    window.location.assign(`/search?q=${encodeURIComponent(next)}`);
  }

  function openSuggestion(product: Product) {
    setRecent(saveRecentSearch(query || product.name));
    onOpenProduct(product);
    onClose();
    window.location.assign(getProductHref(product));
  }

  return (
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <section
        className="search-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-title"
        ref={dialogRef}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="dialog-heading search-dialog-heading" dir="rtl">
          <div>
            <span>GRAMISS SMART SEARCH</span>
            <h2 id="search-title">دنبال چه چیزی هستی؟</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="بستن جست‌وجو">
            <X aria-hidden="true" size={20} strokeWidth={1.8} />
          </button>
        </div>
        <form
          className="search-dialog-form"
          role="search"
          onSubmit={(event) => {
            event.preventDefault();
            if (activeIndex >= 0 && results[activeIndex]) {
              openSuggestion(results[activeIndex]);
              return;
            }
            submitSearch();
          }}
        >
          <label className="search-field" dir="rtl">
            <Search aria-hidden="true" size={20} strokeWidth={1.8} />
            <input
              autoFocus
              type="search"
              placeholder="نام محصول، دسته‌بندی یا جنس را بنویسید"
              value={query}
              aria-controls="header-search-suggestions"
              aria-activedescendant={
                activeIndex >= 0
                  ? `header-search-suggestion-${results[activeIndex]?.id}`
                  : undefined
              }
              onChange={(event) => {
                setQuery(event.target.value);
                setActiveIndex(-1);
              }}
              onKeyDown={(event) => {
                if (event.key === "ArrowDown") {
                  event.preventDefault();
                  setActiveIndex((current) =>
                    Math.min(results.length - 1, current + 1),
                  );
                } else if (event.key === "ArrowUp") {
                  event.preventDefault();
                  setActiveIndex((current) => Math.max(-1, current - 1));
                }
              }}
            />
            {query ? (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  setActiveIndex(-1);
                }}
              >
                پاک کردن
              </button>
            ) : null}
          </label>
        </form>
        <div className="search-dialog-grid" dir="rtl">
          <section className="search-dialog-discovery">
            <div>
              <h3>جست‌وجوهای اخیر</h3>
              {recent.length ? (
                <div className="search-dialog-chips">
                  {recent.slice(0, 4).map((item) => (
                    <button
                      type="button"
                      key={item}
                      onClick={() => submitSearch(item)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              ) : (
                <p>هنوز جست‌وجویی ثبت نشده است.</p>
              )}
            </div>
            <div>
              <h3>دسته‌بندی‌های محبوب</h3>
              <nav className="search-dialog-categories">
                <Link href="/search?q=کلاه" onClick={onClose}>
                  کلاه
                </Link>
                <Link href="/search?q=کیف" onClick={onClose}>
                  کیف
                </Link>
                <Link href="/search?q=جوراب" onClick={onClose}>
                  جوراب
                </Link>
                <Link href="/search?q=کتونی" onClick={onClose}>
                  کتونی
                </Link>
              </nav>
            </div>
          </section>
          <section className="search-results" aria-label="پیشنهادهای محصول">
            <div className="search-result-heading">
              <h3>{query ? "پیشنهادهای مرتبط" : "محصولات پیشنهادی"}</h3>
              {query ? (
                <button type="button" onClick={() => submitSearch()}>
                  مشاهده همه
                </button>
              ) : null}
            </div>
            <div id="header-search-suggestions" role="listbox">
              {results.length ? (
                results.map((product, index) => (
                  <button
                    className={activeIndex === index ? "is-active" : ""}
                    id={`header-search-suggestion-${product.id}`}
                    type="button"
                    role="option"
                    aria-selected={activeIndex === index}
                    key={product.id}
                    onMouseEnter={() => setActiveIndex(index)}
                    onClick={() => openSuggestion(product)}
                  >
                    <img src={product.image} width="72" height="72" alt="" />
                    <span>
                      <strong>{product.name}</strong>
                      <small dir="ltr">{product.english}</small>
                    </span>
                    <b>{product.price}</b>
                  </button>
                ))
              ) : (
                <div className="search-dialog-empty">
                  <p>نتیجه‌ای برای «{query}» پیدا نشد.</p>
                  <button type="button" onClick={() => submitSearch()}>
                    جست‌وجوی کامل
                  </button>
                </div>
              )}
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}

export function Drawer({
  view,
  onClose,
  wishlisted,
  selectedProduct,
  onAddToCart,
  catalog = products,
  productsHref = "/shop",
  cartCount = 2,
  cartItems = [],
}: {
  view: DrawerView;
  onClose: () => void;
  wishlisted: Set<string>;
  selectedProduct: Product | null;
  onAddToCart: (product: Product) => void;
  catalog?: Product[];
  productsHref?: string;
  cartCount?: number;
  cartItems?: CartItem[];
}) {
  const dialogRef = useRef<HTMLElement>(null);
  const open = Boolean(view || selectedProduct);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      dialogRef.current
        ?.querySelector<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled])',
        )
        ?.focus();
    }, 0);

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(
        dialogRef.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? [],
      );
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      window.removeEventListener("keydown", onKeyDown);
      document.documentElement.style.overflow = previousOverflow;
      previousFocus?.focus();
    };
  }, [onClose, open]);

  if (!open) return null;

  const wishlistProducts = catalog.filter((product) =>
    wishlisted.has(product.id),
  );
  const cartSubtotal = cartItems.reduce(
    (total, item) => total + item.unitPrice * item.quantity,
    0,
  );
  const title =
    selectedProduct?.name ??
    {
      menu: "منوی Gramiss",
      wishlist: "علاقه‌مندی‌ها",
      account: "حساب کاربری",
      cart: "سبد خرید",
    }[view ?? "menu"];

  return (
    <div className="overlay drawer-overlay" role="presentation" onMouseDown={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        ref={dialogRef}
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="drawer-heading">
          <h2 id="drawer-title">{title}</h2>
          <button type="button" onClick={onClose} aria-label="بستن پنل">
            <X aria-hidden="true" size={20} strokeWidth={1.8} />
          </button>
        </div>

        {selectedProduct ? (
          <div className="product-drawer">
            <div className="product-drawer-media">
              <img
                src={selectedProduct.image}
                width="221"
                height="235"
                alt={selectedProduct.name}
              />
            </div>
            <span>{selectedProduct.category}</span>
            <h3>{selectedProduct.name}</h3>
            <p dir="ltr">{selectedProduct.english}</p>
            <strong>{selectedProduct.price}</strong>
            <Button onClick={() => onAddToCart(selectedProduct)}>
              افزودن به سبد خرید
            </Button>
          </div>
        ) : null}

        {view === "menu" && !selectedProduct ? (
          <nav className="drawer-nav" aria-label="منوی موبایل">
            {primaryNavigation.map(([label, href]) => (
              <a href={href} key={label} onClick={onClose}>
                <span>{label === "Shop" ? "فروشگاه" : label}</span>
                <ArrowLeft aria-hidden="true" size={18} strokeWidth={1.8} />
              </a>
            ))}
          </nav>
        ) : null}

        {view === "wishlist" && !selectedProduct ? (
          wishlistProducts.length ? (
            <div className="drawer-list">
              {wishlistProducts.map((product) => (
                <a
                  href={getProductHref(product, productsHref)}
                  key={product.id}
                  onClick={onClose}
                >
                  <img src={product.image} width="72" height="72" alt="" />
                  <span>
                    <strong>{product.name}</strong>
                    <small>{product.price}</small>
                  </span>
                </a>
              ))}
            </div>
          ) : (
            <div className="drawer-empty">
              <Heart aria-hidden="true" size={48} strokeWidth={1.5} />
              <p>هنوز محصولی را به علاقه‌مندی‌ها اضافه نکرده‌ای.</p>
              <Button href={productsHref} onClick={onClose}>
                دیدن محصولات
              </Button>
            </div>
          )
        ) : null}

        {view === "account" && !selectedProduct ? (
          <div className="account-panel">
            <p>
              برای ذخیره انتخاب‌ها و پیگیری سفارش‌ها وارد حساب Gramiss شو.
            </p>
            <Button href="/login" onClick={onClose}>
              ورود به حساب
            </Button>
            <Button href="/register" variant="secondary" onClick={onClose}>
              ساخت حساب
            </Button>
          </div>
        ) : null}

        {view === "cart" && !selectedProduct ? (
          <div className="cart-panel">
            {cartItems.length ? (
              <div className="cart-items-list" aria-label="محصولات سبد خرید">
                {cartItems.map((item) => (
                  <a
                    href={getCartItemHref(item)}
                    key={item.lineId}
                    onClick={onClose}
                  >
                    <img
                      src={item.image}
                      width="64"
                      height="64"
                      alt={item.name}
                    />
                    <span>
                      <strong>{item.name}</strong>
                      {item.color || item.size ? (
                        <small>
                          {[item.color, item.size].filter(Boolean).join(" · ")}
                        </small>
                      ) : null}
                      <small>
                        {item.quantity.toLocaleString("fa-IR")} × {item.price}
                      </small>
                    </span>
                  </a>
                ))}
              </div>
            ) : (
              <div className="drawer-empty cart-drawer-empty">
                <ShoppingBag aria-hidden="true" size={48} strokeWidth={1.5} />
                <p>سبد خریدت خالی است.</p>
              </div>
            )}
            {cartItems.length ? (
              <div className="cart-line">
                <span>{cartCount.toLocaleString("fa-IR")} محصول منتخب</span>
                <strong>{formatToman(cartSubtotal)}</strong>
              </div>
            ) : null}
            <Button href="/cart" onClick={onClose}>
              مشاهده سبد خرید
            </Button>
            <Button href="/shop" variant="secondary" onClick={onClose}>
              ادامه خرید
            </Button>
          </div>
        ) : null}
      </aside>
    </div>
  );
}

export default function Home() {
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const {
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [toast, setToast] = useState("");

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function toggleWishlist(product: Product) {
    setWishlisted((current) => {
      const next = new Set(current);
      const removing = next.has(product.id);
      if (removing) next.delete(product.id);
      else next.add(product.id);
      announce(
        removing
          ? `${product.name} از علاقه‌مندی‌ها حذف شد.`
          : `${product.name} به علاقه‌مندی‌ها اضافه شد.`,
      );
      return next;
    });
  }

  function toggleCompare(product: Product) {
    if (compareIds.has(product.id)) {
      window.location.assign("/compare");
      return;
    }
    const result = addToCompare(product.id);
    if (result === "limit") {
      announce("حداکثر چهار محصول را می‌توانید مقایسه کنید.");
      return;
    }
    announce(`${product.name} به مقایسه اضافه شد.`);
    window.setTimeout(() => window.location.assign("/compare"), 220);
  }

  function openProduct(product: Product) {
    setDrawer(null);
    setSelectedProduct(product);
  }

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  return (
    <main className="page-shell" id="top">
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => {
          setDrawer(null);
          setSearchOpen(true);
        }}
        onDrawer={(view) => {
          setSelectedProduct(null);
          setDrawer(view);
        }}
      />
      <Hero />
      <FeaturedCategories />
      <BrowseCategories />
      <FeaturedProducts
        wishlisted={wishlisted}
        compared={compareIds}
        onToggleWishlist={toggleWishlist}
        onToggleCompare={toggleCompare}
      />
      <CampaignSection />
      <WhyGramiss />
      <KnowledgeGuides />
      <Newsletter />
      <Footer />

      {searchOpen ? (
        <SearchDialog
          open
          onClose={() => setSearchOpen(false)}
          onOpenProduct={openProduct}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={closeDrawer}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        cartCount={cartCount}
        cartItems={cartItems}
        productsHref="/shop"
        onAddToCart={(product) => {
          addToCart(product);
          announce(`${product.name} به سبد خرید اضافه شد.`);
          closeDrawer();
        }}
      />
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}
