"use client";

/* eslint-disable @next/next/no-img-element */

import {
  type KeyboardEvent as ReactKeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Heart,
  ShoppingBag,
  X,
  ZoomIn,
} from "lucide-react";
import Link from "next/link";
import { CompareIcon } from "../../components/commerce-ui";
import { NetworkErrorPage } from "../../components/system-states";
import {
  Drawer,
  Footer,
  Header,
  Newsletter,
  SearchDialog,
  products,
  type DrawerView,
  type Product,
} from "../../home-client";
import { useGramissStore } from "../../hooks/use-gramiss-store";
import { useNetworkAction } from "../../hooks/use-network-action";
import { productAssets } from "../product-assets";
import { shopProducts } from "../../shop/shop-data";

const catalogProduct = shopProducts.find(
  (item) => item.id === "sky-blue-cap",
);

if (!catalogProduct) {
  throw new Error("The canonical Sky Blue Cap product is missing.");
}

const product: Product = {
  ...catalogProduct,
  category: "کلاه / کالکشن روزمره",
};

const galleryItems = [
  {
    id: "front",
    label: "نمای روبه‌رو",
    thumbnail: productAssets.galleryFront,
    image: productAssets.capArtwork,
    composite: true,
  },
  {
    id: "side-a",
    label: "نمای کناری اول",
    thumbnail: productAssets.gallerySideA,
    image: productAssets.gallerySideA,
    composite: false,
  },
  {
    id: "side-b",
    label: "نمای کناری دوم",
    thumbnail: productAssets.gallerySideB,
    image: productAssets.gallerySideB,
    composite: false,
  },
  {
    id: "back",
    label: "نمای پشت",
    thumbnail: productAssets.galleryBack,
    image: productAssets.galleryBack,
    composite: false,
  },
] as const;

const colors = [
  { id: "sky", name: "آبی آسمانی", color: "#6babd1" },
  { id: "black", name: "مشکی", color: "#1c1c1a" },
  { id: "sand", name: "خاکی", color: "#c7b89b" },
  { id: "stone", name: "خاکستری روشن", color: "#e8e8e3" },
] as const;

const sizes = ["Free Size", "Adjustable"] as const;

type DetailTab = "specifications" | "material" | "care" | "shipping";

const detailTabs: Array<{ id: DetailTab; label: string }> = [
  { id: "specifications", label: "مشخصات" },
  { id: "material", label: "جنس و دوام" },
  { id: "care", label: "شستشو و نگهداری" },
  { id: "shipping", label: "ارسال و تعویض" },
];

const detailPanels: Record<
  DetailTab,
  { rows: Array<[string, string]>; note: string }
> = {
  specifications: {
    rows: [
      ["جنس اصلی", "کتان ترکیبی سبک"],
      ["نوع بسته‌شدن", "بند قابل تنظیم"],
      ["مناسب برای", "استفاده روزمره و استایل شهری"],
      ["فصل پیشنهادی", "بهار، تابستان و پاییز"],
      ["کشور تولید", "ایران"],
      ["کد محصول", "GRC-CAP-01"],
    ],
    note:
      "نکته: برای حفظ رنگ، با آب سرد و شوینده ملایم شسته شود و در معرض مستقیم آفتاب خشک نشود.",
  },
  material: {
    rows: [
      ["جنس اصلی", "کتان ترکیبی سبک"],
      ["مناسب برای", "استفاده روزمره و استایل شهری"],
      ["فصل پیشنهادی", "بهار، تابستان و پاییز"],
    ],
    note:
      "نکته: برای حفظ رنگ، با آب سرد و شوینده ملایم شسته شود و در معرض مستقیم آفتاب خشک نشود.",
  },
  care: {
    rows: [
      ["شستشو", "آب سرد و شوینده ملایم"],
      ["خشک‌کردن", "دور از معرض مستقیم آفتاب"],
    ],
    note:
      "نکته: برای حفظ رنگ، با آب سرد و شوینده ملایم شسته شود و در معرض مستقیم آفتاب خشک نشود.",
  },
  shipping: {
    rows: [
      ["ارسال", "ارسال سریع"],
      ["اصالت", "ضمانت اصالت"],
      ["تعویض", "امکان تعویض"],
    ],
    note: "ارسال سریع   ·   ضمانت اصالت   ·   امکان تعویض",
  },
};

const relatedArticles = [
  {
    number: "01",
    title: "انتخاب کلاه متناسب با فرم صورت",
    meta: "۵ دقیقه مطالعه  ←",
    href: "/#journal",
    tone: "mint",
  },
  {
    number: "02",
    title: "چطور رنگ اکسسوری را با لباس هماهنگ کنیم؟",
    meta: "۶ دقیقه مطالعه  ←",
    href: "/#journal",
    tone: "sand",
  },
  {
    number: "03",
    title: "روش صحیح شستشوی کلاه",
    meta: "۴ دقیقه مطالعه  ←",
    href: "/#journal",
    tone: "stone",
  },
] as const;

const similarProductIds = [
  "sand-cap",
  "signature-cap",
  "city-bag",
  "daily-sneaker",
];

const similarProducts = similarProductIds.flatMap((id) => {
  const item = shopProducts.find((candidate) => candidate.id === id);
  return item ? [item] : [];
});

function GalleryVisual({
  index,
  lightbox = false,
}: {
  index: number;
  lightbox?: boolean;
}) {
  const item = galleryItems[index];

  if (item.composite) {
    return (
      <span
        className={`pdp-gallery-composite ${lightbox ? "is-lightbox" : ""}`}
      >
        <img
          className="pdp-gallery-backdrop"
          src={productAssets.backdrop}
          alt=""
          aria-hidden="true"
        />
        <img
          className="pdp-gallery-product-art"
          src={item.image}
          alt={`${product.name}، ${item.label}`}
        />
      </span>
    );
  }

  return (
    <img
      className={`pdp-gallery-render ${lightbox ? "is-lightbox" : ""}`}
      src={item.image}
      alt={`${product.name}، ${item.label}`}
    />
  );
}

function ProductGallery({
  activeImage,
  setActiveImage,
  onOpenLightbox,
}: {
  activeImage: number;
  setActiveImage: (index: number) => void;
  onOpenLightbox: () => void;
}) {
  function moveSelection(delta: number) {
    setActiveImage(
      (activeImage + delta + galleryItems.length) % galleryItems.length,
    );
  }

  function onGalleryKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      moveSelection(1);
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      moveSelection(-1);
    }
    if (event.key === "Home") {
      event.preventDefault();
      setActiveImage(0);
    }
    if (event.key === "End") {
      event.preventDefault();
      setActiveImage(galleryItems.length - 1);
    }
  }

  return (
    <section
      className="pdp-gallery"
      aria-label="گالری تصاویر محصول"
      data-node-id="113:717"
    >
      <button
        className="pdp-main-media"
        type="button"
        aria-label={`بزرگ‌نمایی ${galleryItems[activeImage].label}`}
        onClick={onOpenLightbox}
      >
        <span className="pdp-product-badge">جدید</span>
        <ZoomIn
          className="pdp-zoom-icon"
          aria-hidden="true"
          size={24}
          strokeWidth={1.7}
        />
        <GalleryVisual index={activeImage} />
        <span className="pdp-editorial-label" dir="ltr">
          GRAMISS / CAP 01
        </span>
      </button>

      <div
        className="pdp-thumbnails"
        role="group"
        aria-label="انتخاب نمای محصول"
        onKeyDown={onGalleryKeyDown}
      >
        {galleryItems.map((item, index) => (
          <button
            className={index === activeImage ? "is-selected" : ""}
            type="button"
            aria-label={item.label}
            aria-pressed={index === activeImage}
            key={item.id}
            onClick={() => setActiveImage(index)}
          >
            <img src={item.thumbnail} alt="" />
          </button>
        ))}
      </div>

      <p className="pdp-gallery-hint" dir="rtl">
        برای مشاهده جزئیات، روی تصویر حرکت کنید
      </p>
    </section>
  );
}

function PurchasePanel({
  selectedColor,
  setSelectedColor,
  selectedSize,
  setSelectedSize,
  wishlisted,
  compared,
  onToggleWishlist,
  onToggleCompare,
  onAddToCart,
  panelRef,
}: {
  selectedColor: string;
  setSelectedColor: (color: string) => void;
  selectedSize: string;
  setSelectedSize: (size: string) => void;
  wishlisted: boolean;
  compared: boolean;
  onToggleWishlist: () => void;
  onToggleCompare: () => void;
  onAddToCart: () => void;
  panelRef: React.RefObject<HTMLElement | null>;
}) {
  const currentColor =
    colors.find((color) => color.id === selectedColor) ?? colors[0];

  return (
    <section
      className="pdp-purchase"
      aria-labelledby="product-title"
      ref={panelRef}
      dir="rtl"
      data-node-id="113:742"
    >
      <p className="pdp-category">{product.category}</p>
      <h1 id="product-title">{product.name}</h1>
      <p className="pdp-english-title" dir="ltr">
        {product.english}
      </p>
      <p className="pdp-rating" aria-label="امتیاز ۴.۸ از ۵، از ۱۲۸ نظر">
        <span aria-hidden="true">★★★★★</span>
        <b>۴.۸</b>
        <span aria-hidden="true">·</span>
        <span>۱۲۸ نظر</span>
      </p>
      <p className="pdp-price">{product.price}</p>

      <div className="pdp-purchase-rule" aria-hidden="true" />

      <fieldset className="pdp-option-group pdp-color-options">
        <legend>رنگ: {currentColor.name}</legend>
        <div>
          {colors.map((color) => (
            <button
              className={selectedColor === color.id ? "is-selected" : ""}
              type="button"
              aria-label={`انتخاب رنگ ${color.name}`}
              aria-pressed={selectedColor === color.id}
              title={color.name}
              key={color.id}
              style={{ "--swatch": color.color } as React.CSSProperties}
              onClick={() => setSelectedColor(color.id)}
            >
              <span aria-hidden="true" />
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset className="pdp-option-group pdp-size-options">
        <legend>اندازه</legend>
        <a href="#details-tabs">راهنمای اندازه</a>
        <div>
          {sizes.map((size) => (
            <button
              className={selectedSize === size ? "is-selected" : ""}
              type="button"
              aria-pressed={selectedSize === size}
              key={size}
              onClick={() => setSelectedSize(size)}
            >
              {size}
            </button>
          ))}
        </div>
      </fieldset>

      <p className="pdp-stock">
        <span aria-hidden="true" />
        موجود و آماده ارسال
      </p>

      <button
        className="pdp-add-button"
        type="button"
        onClick={onAddToCart}
      >
        <span>افزودن به سبد خرید</span>
        <ArrowLeft aria-hidden="true" size={21} strokeWidth={1.8} />
      </button>
      <button
        className={`pdp-wishlist-button ${wishlisted ? "is-active" : ""}`}
        type="button"
        aria-pressed={wishlisted}
        onClick={onToggleWishlist}
      >
        <Heart
          aria-hidden="true"
          size={20}
          strokeWidth={1.7}
          fill={wishlisted ? "currentColor" : "none"}
        />
        {wishlisted ? "در علاقه‌مندی‌ها ذخیره شد" : "افزودن به علاقه‌مندی‌ها"}
      </button>
      <button
        className={`pdp-compare-button ${compared ? "is-active" : ""}`}
        type="button"
        aria-pressed={compared}
        onClick={onToggleCompare}
      >
        <CompareIcon size={20} />
        {compared ? "در فهرست مقایسه است" : "افزودن به مقایسه"}
      </button>

      <div className="pdp-trust" aria-label="اطلاعات ارسال و اصالت">
        <span>ارسال سریع</span>
        <i aria-hidden="true">·</i>
        <span>ضمانت اصالت</span>
        <i aria-hidden="true">·</i>
        <span>امکان تعویض</span>
      </div>
      <div className="pdp-purchase-rule is-lower" aria-hidden="true" />
      <p className="pdp-summary">
        این محصول برای استفاده روزمره، استایل مینیمال و فرم‌های مختلف صورت
        انتخاب شده است.
      </p>
    </section>
  );
}

function WhyThisProduct() {
  const reasons = [
    ["01", "فرم متعادل", "برای بیشتر فرم‌های صورت بدون ایجاد حجم اضافه."],
    ["02", "جنس روزمره", "پارچه سبک و قابل تنفس برای استفاده طولانی."],
    [
      "03",
      "رنگ منعطف",
      "هماهنگ با سفید، طوسی، سرمه‌ای و استایل‌های خنثی.",
    ],
  ] as const;

  return (
    <section
      className="pdp-why"
      aria-labelledby="pdp-why-title"
      data-node-id="113:809"
    >
      <div className="pdp-why-intro" dir="rtl">
        <span dir="ltr">WHY THIS PRODUCT</span>
        <h2 id="pdp-why-title">چرا این کلاه انتخاب خوبی است؟</h2>
        <p>
          <bdi dir="ltr">Gramiss</bdi> فقط مشخصات را نشان نمی‌دهد؛ به تو کمک
          می‌کند بفهمی این محصول برای چه استفاده‌ای مناسب است و بعد از خرید چه
          انتظاری داشته باشی.
        </p>
      </div>
      <div className="pdp-reason-grid">
        {reasons.map(([number, title, description]) => (
          <article key={number} dir="rtl">
            <span dir="ltr">{number}</span>
            <h3>{title}</h3>
            <p>{description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function DetailsTabs({
  activeTab,
  setActiveTab,
}: {
  activeTab: DetailTab;
  setActiveTab: (tab: DetailTab) => void;
}) {
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const panel = detailPanels[activeTab];

  function onTabKeyDown(
    event: ReactKeyboardEvent<HTMLButtonElement>,
    index: number,
  ) {
    let nextIndex = index;
    if (event.key === "ArrowRight") nextIndex = index - 1;
    else if (event.key === "ArrowLeft") nextIndex = index + 1;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = detailTabs.length - 1;
    else return;

    event.preventDefault();
    nextIndex = (nextIndex + detailTabs.length) % detailTabs.length;
    setActiveTab(detailTabs[nextIndex].id);
    tabRefs.current[nextIndex]?.focus();
  }

  return (
    <section
      className="pdp-details"
      id="details-tabs"
      aria-labelledby="pdp-details-title"
      dir="rtl"
      data-node-id="113:769"
    >
      <h2 id="pdp-details-title">جزئیات، جنس و مراقبت</h2>
      <p className="pdp-details-subtitle">
        اطلاعاتی که قبل از خرید باید بدانی.
      </p>
      <div
        className="pdp-tab-list"
        role="tablist"
        aria-label="جزئیات محصول"
      >
        {detailTabs.map((tab, index) => (
          <button
            className={activeTab === tab.id ? "is-active" : ""}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            ref={(node) => {
              tabRefs.current[index] = node;
            }}
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(event) => onTabKeyDown(event, index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div
        className="pdp-tab-panel"
        id={`panel-${activeTab}`}
        role="tabpanel"
        aria-labelledby={`tab-${activeTab}`}
        key={activeTab}
      >
        <dl>
          {panel.rows.map(([label, value]) => (
            <div key={`${activeTab}-${label}`}>
              <dt>{label}</dt>
              <dd dir={value.startsWith("GRC-") ? "ltr" : "rtl"}>{value}</dd>
            </div>
          ))}
        </dl>
        <p>{panel.note}</p>
      </div>
    </section>
  );
}

function SmartGuide({ onOpen }: { onOpen: () => void }) {
  return (
    <section
      className="pdp-smart-guide"
      aria-labelledby="pdp-guide-title"
      data-node-id="113:800"
    >
      <div className="pdp-guide-copy" dir="rtl">
        <span dir="ltr">GRAMISS SMART GUIDE</span>
        <h2 id="pdp-guide-title">
          هنوز مطمئن نیستی این مدل برای تو مناسب است؟
        </h2>
        <p>
          به سه سؤال کوتاه درباره فرم صورت، سبک پوشش و موقعیت استفاده پاسخ بده
          تا <bdi dir="ltr">Gramiss</bdi> پیشنهاد دقیق‌تری ارائه دهد.
        </p>
        <button type="button" onClick={onOpen}>
          شروع راهنمای هوشمند
        </button>
      </div>
      <div className="pdp-guide-art" aria-hidden="true">
        <img src={productAssets.aiOrb} alt="" />
        <img src={productAssets.aiOrbInner} alt="" />
        <span>G</span>
      </div>
    </section>
  );
}

function RelatedKnowledge() {
  return (
    <section
      className="pdp-related"
      aria-labelledby="pdp-related-title"
      data-node-id="113:825"
    >
      <p className="pdp-section-kicker" dir="ltr">
        RELATED KNOWLEDGE
      </p>
      <h2 id="pdp-related-title" dir="rtl">
        قبل از خرید بیشتر بدان
      </h2>
      <div className="pdp-article-grid">
        {relatedArticles.map((article) => (
          <Link
            className="pdp-article-card"
            href={article.href}
            key={article.number}
            dir="rtl"
          >
            <span
              className={`pdp-article-media tone-${article.tone}`}
              aria-hidden="true"
            >
              <i dir="ltr">{article.number}</i>
            </span>
            <h3>{article.title}</h3>
            <p>{article.meta}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}

function SimilarProducts({
  wishlisted,
  compared,
  onToggleWishlist,
  onToggleCompare,
}: {
  wishlisted: Set<string>;
  compared: Set<string>;
  onToggleWishlist: (item: (typeof similarProducts)[number]) => void;
  onToggleCompare: (item: (typeof similarProducts)[number]) => void;
}) {
  return (
    <section
      className="pdp-similar"
      aria-labelledby="pdp-similar-title"
      data-node-id="113:843"
    >
      <p className="pdp-section-kicker" dir="ltr">
        YOU MAY ALSO LIKE
      </p>
      <h2 id="pdp-similar-title" dir="rtl">
        محصولات مشابه
      </h2>
      <div className="pdp-similar-grid">
        {similarProducts.map((item) => {
          const active = wishlisted.has(item.id);
          const href = `/product/${item.id}`;
          return (
            <article className="pdp-similar-card" key={item.id} dir="rtl">
              <Link
                className="pdp-similar-media"
                href={href}
                aria-label={`مشاهده ${item.name}`}
              >
                <img src={item.image} alt={item.name} loading="lazy" />
              </Link>
              <button
                className={active ? "is-active" : ""}
                type="button"
                aria-label={
                  active
                    ? `حذف ${item.name} از علاقه‌مندی‌ها`
                    : `افزودن ${item.name} به علاقه‌مندی‌ها`
                }
                aria-pressed={active}
                onClick={() => onToggleWishlist(item)}
              >
                <Heart
                  aria-hidden="true"
                  size={19}
                  strokeWidth={1.7}
                  fill={active ? "currentColor" : "none"}
                />
              </button>
              <button
                className={`pdp-similar-compare ${
                  compared.has(item.id) ? "is-active" : ""
                }`}
                type="button"
                aria-label={
                  compared.has(item.id)
                    ? `مشاهده ${item.name} در مقایسه`
                    : `افزودن ${item.name} به مقایسه`
                }
                aria-pressed={compared.has(item.id)}
                onClick={() => onToggleCompare(item)}
              >
                <CompareIcon size={18} />
              </button>
              <Link className="pdp-similar-copy" href={href}>
                <h3>{item.name}</h3>
                <p>{item.price}</p>
              </Link>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function Lightbox({
  activeImage,
  onClose,
  onPrevious,
  onNext,
}: {
  activeImage: number;
  onClose: () => void;
  onPrevious: () => void;
  onNext: () => void;
}) {
  return (
    <div
      className="pdp-lightbox"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-label={`نمای بزرگ ${galleryItems[activeImage].label}`}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button
          className="pdp-lightbox-close"
          type="button"
          aria-label="بستن تصویر"
          autoFocus
          onClick={onClose}
        >
          <X aria-hidden="true" size={22} strokeWidth={1.8} />
        </button>
        <button
          className="pdp-lightbox-nav is-previous"
          type="button"
          aria-label="تصویر قبلی"
          onClick={onPrevious}
        >
          <ChevronLeft aria-hidden="true" size={24} strokeWidth={1.8} />
        </button>
        <GalleryVisual index={activeImage} lightbox />
        <button
          className="pdp-lightbox-nav is-next"
          type="button"
          aria-label="تصویر بعدی"
          onClick={onNext}
        >
          <ChevronRight aria-hidden="true" size={24} strokeWidth={1.8} />
        </button>
        <p>
          {galleryItems[activeImage].label} · {activeImage + 1} /{" "}
          {galleryItems.length}
        </p>
      </section>
    </div>
  );
}

function GuideDialog({ onClose }: { onClose: () => void }) {
  const questions = [
    ["۱", "فرم صورتت به کدام حالت نزدیک‌تر است؟"],
    ["۲", "استایل روزمره‌ات بیشتر مینیمال است یا اسپرت؟"],
    ["۳", "این کلاه را بیشتر برای چه موقعیتی می‌خواهی؟"],
  ] as const;

  return (
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <section
        className="pdp-guide-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guide-dialog-title"
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div>
          <span dir="ltr">GRAMISS SMART GUIDE</span>
          <button
            type="button"
            aria-label="بستن راهنمای هوشمند"
            autoFocus
            onClick={onClose}
          >
            <X aria-hidden="true" size={20} strokeWidth={1.8} />
          </button>
        </div>
        <h2 id="guide-dialog-title">سه سؤال برای انتخاب دقیق‌تر</h2>
        <p>
          این نسخه فقط نمونهٔ رابط کاربری است و هنوز به سرویس هوش مصنوعی متصل
          نیست.
        </p>
        <ol>
          {questions.map(([number, question]) => (
            <li key={number}>
              <span>{number}</span>
              {question}
            </li>
          ))}
        </ol>
        <button className="pdp-dialog-done" type="button" onClick={onClose}>
          متوجه شدم
        </button>
      </section>
    </div>
  );
}

export default function SkyBlueCapPage() {
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [activeImage, setActiveImage] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [guideOpen, setGuideOpen] = useState(false);
  const [selectedColor, setSelectedColor] = useState("sky");
  const [selectedSize, setSelectedSize] = useState<string>("Free Size");
  const [activeTab, setActiveTab] = useState<DetailTab>("specifications");
  const [purchaseVisible, setPurchaseVisible] = useState(false);
  const [toast, setToast] = useState("");
  const purchaseRef = useRef<HTMLElement>(null);
  const {
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const {
    status: networkStatus,
    retry: retryProduct,
    checkInitialLoad,
  } = useNetworkAction("product");

  const hasProductModal = Boolean(lightboxOpen || guideOpen);

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  useEffect(() => {
    const node = purchaseRef.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => setPurchaseVisible(entry.isIntersecting),
      { threshold: 0.05 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!hasProductModal) return;
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      document
        .querySelector<HTMLElement>(
          '.pdp-lightbox [role="dialog"], .pdp-guide-dialog',
        )
        ?.querySelector<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled])',
        )
        ?.focus();
    }, 0);

    function onKeyDown(event: KeyboardEvent) {
      if (lightboxOpen && event.key === "ArrowRight") {
        setActiveImage((current) => (current + 1) % galleryItems.length);
      }
      if (lightboxOpen && event.key === "ArrowLeft") {
        setActiveImage(
          (current) =>
            (current - 1 + galleryItems.length) % galleryItems.length,
        );
      }
      if (event.key === "Escape") {
        event.preventDefault();
        setLightboxOpen(false);
        setGuideOpen(false);
        return;
      }
      if (event.key !== "Tab") return;
      const dialog = document.querySelector<HTMLElement>(
        '.pdp-lightbox [role="dialog"], .pdp-guide-dialog',
      );
      const controls = Array.from(
        dialog?.querySelectorAll<HTMLElement>(
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
      window.clearTimeout(focusTimer);
      document.documentElement.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
      previousFocus?.focus();
    };
  }, [hasProductModal, lightboxOpen]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function addCurrentProduct() {
    const colorName =
      colors.find((color) => color.id === selectedColor)?.name ??
      colors[0].name;
    addToCart(product, {
      color: colorName,
      size: selectedSize,
    });
    announce(`${product.name} به سبد خرید اضافه شد.`);
  }

  function toggleProductWishlist() {
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

  function toggleProductCompare() {
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

  function toggleSimilarWishlist(item: (typeof similarProducts)[number]) {
    setWishlisted((current) => {
      const next = new Set(current);
      const removing = next.has(item.id);
      if (removing) next.delete(item.id);
      else next.add(item.id);
      announce(
        removing
          ? `${item.name} از علاقه‌مندی‌ها حذف شد.`
          : `${item.name} به علاقه‌مندی‌ها اضافه شد.`,
      );
      return next;
    });
  }

  function toggleSimilarCompare(item: (typeof similarProducts)[number]) {
    if (compareIds.has(item.id)) {
      window.location.assign("/compare");
      return;
    }
    const result = addToCompare(item.id);
    if (result === "limit") {
      announce("حداکثر چهار محصول را می‌توانید مقایسه کنید.");
      return;
    }
    announce(`${item.name} به مقایسه اضافه شد.`);
    window.setTimeout(() => window.location.assign("/compare"), 220);
  }

  function openProduct(nextProduct: Product) {
    if (nextProduct.id === product.id) {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    setDrawer(null);
    setSelectedProduct(nextProduct);
  }

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  if (networkStatus === "loading") {
    return <NetworkErrorPage loading onRetry={retryProduct} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retryProduct} />;
  }

  return (
    <main
      className="page-shell product-page"
      id="top"
      data-node-id="32:2"
    >
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

      <nav className="pdp-breadcrumb" aria-label="مسیر صفحه" dir="rtl">
        <Link href="/">خانه</Link>
        <span aria-hidden="true">/</span>
        <Link href="/shop">فروشگاه</Link>
        <span aria-hidden="true">/</span>
        <Link href="/shop?category=caps">کلاه</Link>
        <span aria-hidden="true">/</span>
        <span aria-current="page">کلاه آبی آسمانی</span>
      </nav>

      <div className="pdp-top">
        <ProductGallery
          activeImage={activeImage}
          setActiveImage={setActiveImage}
          onOpenLightbox={() => setLightboxOpen(true)}
        />
        <PurchasePanel
          selectedColor={selectedColor}
          setSelectedColor={setSelectedColor}
          selectedSize={selectedSize}
          setSelectedSize={setSelectedSize}
          wishlisted={wishlisted.has(product.id)}
          compared={compareIds.has(product.id)}
          onToggleWishlist={toggleProductWishlist}
          onToggleCompare={toggleProductCompare}
          onAddToCart={addCurrentProduct}
          panelRef={purchaseRef}
        />
      </div>

      <WhyThisProduct />
      <DetailsTabs activeTab={activeTab} setActiveTab={setActiveTab} />
      <SmartGuide onOpen={() => setGuideOpen(true)} />
      <RelatedKnowledge />
      <SimilarProducts
        wishlisted={wishlisted}
        compared={compareIds}
        onToggleWishlist={toggleSimilarWishlist}
        onToggleCompare={toggleSimilarCompare}
      />
      <Newsletter variant="shop" />
      <Footer />

      {purchaseVisible ? (
        <div className="pdp-mobile-add">
          <button type="button" onClick={addCurrentProduct}>
            <ShoppingBag aria-hidden="true" size={19} strokeWidth={1.8} />
            افزودن به سبد خرید
            <span>{product.price}</span>
          </button>
        </div>
      ) : null}

      {lightboxOpen ? (
        <Lightbox
          activeImage={activeImage}
          onClose={() => setLightboxOpen(false)}
          onPrevious={() =>
            setActiveImage(
              (current) =>
                (current - 1 + galleryItems.length) % galleryItems.length,
            )
          }
          onNext={() =>
            setActiveImage((current) => (current + 1) % galleryItems.length)
          }
        />
      ) : null}
      {guideOpen ? <GuideDialog onClose={() => setGuideOpen(false)} /> : null}
      {searchOpen ? (
        <SearchDialog
          open
          catalog={products}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={openProduct}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={closeDrawer}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        onAddToCart={(nextProduct) => {
          addToCart(nextProduct);
          announce(`${nextProduct.name} به سبد خرید اضافه شد.`);
          closeDrawer();
        }}
        catalog={products}
        productsHref="/shop"
        cartCount={cartCount}
        cartItems={cartItems}
      />
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}
