"use client";

/* eslint-disable @next/next/no-img-element */

import {
  ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Columns3,
  Columns4,
  Heart,
  SlidersHorizontal,
  X,
} from "lucide-react";
import Link from "next/link";
import { CompareIcon } from "../components/commerce-ui";
import {
  Button,
  Drawer,
  Footer,
  getProductHref,
  Header,
  Newsletter,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import { useGramissStore } from "../hooks/use-gramiss-store";
import {
  quickCategories,
  shopProducts,
  type CategoryKey,
  type ProductArtwork,
  type ShopProduct,
} from "./shop-data";

type SortMode = "newest" | "price-asc" | "price-desc";
type GridMode = 3 | 4;
type FilterSection =
  | "category"
  | "price"
  | "color"
  | "size"
  | "material"
  | "availability"
  | "discount";

type Filters = {
  category: CategoryKey | null;
  minPrice: number;
  maxPrice: number;
  colors: string[];
  sizes: string[];
  materials: string[];
  inStock: boolean;
  discounted: boolean;
};

const MIN_PRICE = 500_000;
const MAX_PRICE = 5_000_000;
const PAGE_SIZE = 9;

const emptyFilters = (): Filters => ({
  category: null,
  minPrice: MIN_PRICE,
  maxPrice: MAX_PRICE,
  colors: [],
  sizes: [],
  materials: [],
  inStock: false,
  discounted: false,
});

const categoryLabels = Object.fromEntries(
  quickCategories
    .filter((category) => category.key !== "all")
    .map((category) => [category.key, category.persian]),
) as Record<CategoryKey, string>;

function formatNumber(value: number) {
  return value.toLocaleString("fa-IR");
}

function toggleListValue(list: string[], value: string) {
  return list.includes(value)
    ? list.filter((item) => item !== value)
    : [...list, value];
}

function ProductArtworkView({
  artwork,
  image,
  name,
}: {
  artwork: ProductArtwork;
  image: string;
  name: string;
}) {
  if (artwork === "cap") {
    return (
      <span className="shop-artwork shop-artwork-cap">
        <img src={image} width="210" height="235" alt={name} loading="lazy" />
      </span>
    );
  }

  return (
    <span
      className={`shop-artwork shop-artwork-${artwork}`}
      aria-hidden="true"
    >
      <span />
      <span />
      {artwork === "shirt" || artwork === "socks" ? <span /> : null}
    </span>
  );
}

function ShopProductCard({
  product,
  wishlisted,
  compared,
  onToggleWishlist,
  onToggleCompare,
  onAddToCart,
}: {
  product: ShopProduct;
  wishlisted: boolean;
  compared: boolean;
  onToggleWishlist: (product: ShopProduct) => void;
  onToggleCompare: (product: ShopProduct) => void;
  onAddToCart: (product: ShopProduct) => void;
}) {
  const productHref = getProductHref(product, "/shop");

  return (
    <article
      className="shop-product-card"
      id={`product-${product.id}`}
      data-product-id={product.id}
      dir="rtl"
    >
      <a
        className="shop-product-media"
        href={productHref}
        aria-label={`مشاهده ${product.name}`}
      >
        {product.badge ? (
          <span className="shop-product-badge">{product.badge}</span>
        ) : null}
        <ProductArtworkView
          artwork={product.artwork}
          image={product.image}
          name={product.name}
        />
      </a>
      <button
        className={`shop-wishlist ${wishlisted ? "is-active" : ""}`}
        type="button"
        aria-label={
          wishlisted
            ? `حذف ${product.name} از علاقه‌مندی‌ها`
            : `افزودن ${product.name} به علاقه‌مندی‌ها`
        }
        aria-pressed={wishlisted}
        onClick={() => onToggleWishlist(product)}
      >
        <Heart
          aria-hidden="true"
          size={20}
          strokeWidth={1.7}
          fill={wishlisted ? "currentColor" : "none"}
        />
      </button>
      <button
        className={`shop-compare ${compared ? "is-active" : ""}`}
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
        className="shop-product-copy"
        href={productHref}
      >
        <span>{product.category}</span>
        <strong>{product.name}</strong>
        <small dir="ltr">{product.english}</small>
      </a>
      <div className="shop-product-buy">
        <b>{product.price}</b>
        <button
          type="button"
          aria-label={`افزودن ${product.name} به سبد خرید`}
          onClick={() => onAddToCart(product)}
        >
          افزودن
        </button>
      </div>
    </article>
  );
}

function FilterSectionBlock({
  id,
  title,
  summary,
  children,
  expanded,
  mobile,
  onToggle,
}: {
  id: FilterSection;
  title: string;
  summary: string;
  children: ReactNode;
  expanded: boolean;
  mobile: boolean;
  onToggle: (section: FilterSection) => void;
}) {
  const contentId = `${mobile ? "mobile" : "desktop"}-filter-${id}`;

  return (
    <section className={`shop-filter-section ${expanded ? "is-open" : ""}`}>
      <button
        type="button"
        className="shop-filter-heading"
        aria-expanded={expanded}
        aria-controls={contentId}
        onClick={() => onToggle(id)}
      >
        <span>{title}</span>
        <ChevronDown aria-hidden="true" size={17} strokeWidth={1.8} />
      </button>
      <p className="shop-filter-summary">{summary}</p>
      <div className="shop-filter-options" id={contentId} hidden={!expanded}>
        {children}
      </div>
    </section>
  );
}

function FilterPanel({
  filters,
  onChange,
  onClear,
  onApply,
  mobile = false,
}: {
  filters: Filters;
  onChange: (next: Filters) => void;
  onClear: () => void;
  onApply: () => void;
  mobile?: boolean;
}) {
  const [openSections, setOpenSections] = useState<Set<FilterSection>>(
    () => new Set(),
  );

  function toggleSection(section: FilterSection) {
    setOpenSections((current) => {
      const next = new Set(current);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  }

  function updateList(
    key: "colors" | "sizes" | "materials",
    value: string,
  ) {
    onChange({
      ...filters,
      [key]: toggleListValue(filters[key], value),
    });
  }

  return (
    <div
      className={`shop-filter-panel ${mobile ? "is-mobile" : ""}`}
      dir="rtl"
      data-node-id={mobile ? undefined : "92:89"}
    >
      <div className="shop-filter-title">
        <h2>{mobile ? "فیلتر محصولات" : "فیلترها"}</h2>
        <button type="button" onClick={onClear}>
          پاک کردن همه
        </button>
      </div>

      <FilterSectionBlock
        id="category"
        title="دسته‌بندی"
        summary="کتونی، کیف، کلاه، جوراب"
        expanded={openSections.has("category")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <div className="shop-filter-choice-list">
          {quickCategories
            .filter((category) => category.key !== "all")
            .map((category) => (
              <label key={category.key}>
                <input
                  type="radio"
                  name={mobile ? "mobile-category" : "desktop-category"}
                  checked={filters.category === category.key}
                  onChange={() =>
                    onChange({
                      ...filters,
                      category:
                        filters.category === category.key
                          ? null
                          : (category.key as CategoryKey),
                    })
                  }
                />
                <span>{category.persian}</span>
              </label>
            ))}
        </div>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="price"
        title="محدوده قیمت"
        summary="از ۵۰۰ هزار تا ۵ میلیون"
        expanded={openSections.has("price")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <div className="shop-price-fields">
          <label>
            <span>از</span>
            <input
              type="number"
              min={MIN_PRICE}
              max={filters.maxPrice}
              step="100000"
              value={filters.minPrice}
              onChange={(event) =>
                onChange({
                  ...filters,
                  minPrice: Math.min(
                    Number(event.target.value) || MIN_PRICE,
                    filters.maxPrice,
                  ),
                })
              }
            />
          </label>
          <label>
            <span>تا</span>
            <input
              type="number"
              min={filters.minPrice}
              max={MAX_PRICE}
              step="100000"
              value={filters.maxPrice}
              onChange={(event) =>
                onChange({
                  ...filters,
                  maxPrice: Math.max(
                    Number(event.target.value) || MAX_PRICE,
                    filters.minPrice,
                  ),
                })
              }
            />
          </label>
        </div>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="color"
        title="رنگ"
        summary="مشکی، سفید، آبی، خاکی"
        expanded={openSections.has("color")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <div className="shop-filter-choice-list">
          {["مشکی", "سفید", "آبی", "خاکی"].map((color) => (
            <label key={color}>
              <input
                type="checkbox"
                checked={filters.colors.includes(color)}
                onChange={() => updateList("colors", color)}
              />
              <span>{color}</span>
            </label>
          ))}
        </div>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="size"
        title="سایز"
        summary="S  M  L  XL"
        expanded={openSections.has("size")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <div className="shop-size-choices" dir="ltr">
          {["S", "M", "L", "XL"].map((size) => (
            <label key={size}>
              <input
                type="checkbox"
                checked={filters.sizes.includes(size)}
                onChange={() => updateList("sizes", size)}
              />
              <span>{size}</span>
            </label>
          ))}
        </div>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="material"
        title="جنس"
        summary="پنبه، پلی‌استر، چرم"
        expanded={openSections.has("material")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <div className="shop-filter-choice-list">
          {["پنبه", "پلی‌استر", "چرم", "کتان ترکیبی سبک"].map((material) => (
            <label key={material}>
              <input
                type="checkbox"
                checked={filters.materials.includes(material)}
                onChange={() => updateList("materials", material)}
              />
              <span>{material}</span>
            </label>
          ))}
        </div>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="availability"
        title="موجودی"
        summary="فقط کالاهای موجود"
        expanded={openSections.has("availability")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <label className="shop-filter-switch">
          <input
            type="checkbox"
            checked={filters.inStock}
            onChange={(event) =>
              onChange({ ...filters, inStock: event.target.checked })
            }
          />
          <span>فقط کالاهای موجود نمایش داده شود</span>
        </label>
      </FilterSectionBlock>

      <FilterSectionBlock
        id="discount"
        title="تخفیف"
        summary="محصولات تخفیف‌دار"
        expanded={openSections.has("discount")}
        mobile={mobile}
        onToggle={toggleSection}
      >
        <label className="shop-filter-switch">
          <input
            type="checkbox"
            checked={filters.discounted}
            onChange={(event) =>
              onChange({ ...filters, discounted: event.target.checked })
            }
          />
          <span>فقط محصولات دارای تخفیف</span>
        </label>
      </FilterSectionBlock>

      <button className="shop-filter-apply" type="button" onClick={onApply}>
        اعمال فیلترها
      </button>
    </div>
  );
}

function ActiveFilters({
  filters,
  onChange,
  onClear,
}: {
  filters: Filters;
  onChange: (next: Filters) => void;
  onClear: () => void;
}) {
  const chips: Array<{ key: string; label: string; remove: () => void }> = [];

  if (filters.category) {
    chips.push({
      key: `category-${filters.category}`,
      label: categoryLabels[filters.category],
      remove: () => onChange({ ...filters, category: null }),
    });
  }

  if (filters.minPrice !== MIN_PRICE || filters.maxPrice !== MAX_PRICE) {
    chips.push({
      key: "price",
      label: `${formatNumber(filters.minPrice)} تا ${formatNumber(filters.maxPrice)}`,
      remove: () =>
        onChange({
          ...filters,
          minPrice: MIN_PRICE,
          maxPrice: MAX_PRICE,
        }),
    });
  }

  filters.colors.forEach((color) =>
    chips.push({
      key: `color-${color}`,
      label: color,
      remove: () =>
        onChange({
          ...filters,
          colors: filters.colors.filter((item) => item !== color),
        }),
    }),
  );
  filters.sizes.forEach((size) =>
    chips.push({
      key: `size-${size}`,
      label: size,
      remove: () =>
        onChange({
          ...filters,
          sizes: filters.sizes.filter((item) => item !== size),
        }),
    }),
  );
  filters.materials.forEach((material) =>
    chips.push({
      key: `material-${material}`,
      label: material,
      remove: () =>
        onChange({
          ...filters,
          materials: filters.materials.filter((item) => item !== material),
        }),
    }),
  );

  if (filters.inStock) {
    chips.push({
      key: "in-stock",
      label: "فقط موجود",
      remove: () => onChange({ ...filters, inStock: false }),
    });
  }

  if (filters.discounted) {
    chips.push({
      key: "discounted",
      label: "تخفیف‌دار",
      remove: () => onChange({ ...filters, discounted: false }),
    });
  }

  return (
    <div className="shop-active-filters" dir="rtl">
      <h2>فیلترهای فعال</h2>
      <div className="shop-active-filter-list">
        {chips.length ? (
          <>
            {chips.map((chip, index) => (
              <button
                className={index === 0 ? "is-primary" : ""}
                type="button"
                key={chip.key}
                onClick={chip.remove}
                aria-label={`حذف فیلتر ${chip.label}`}
              >
                <span>{chip.label}</span>
                <X aria-hidden="true" size={14} strokeWidth={2} />
              </button>
            ))}
            <button className="clear-all" type="button" onClick={onClear}>
              حذف همه
            </button>
          </>
        ) : (
          <span className="shop-no-active-filter">بدون فیلتر فعال</span>
        )}
      </div>
    </div>
  );
}

function SortControl({
  value,
  onChange,
  mobile = false,
}: {
  value: SortMode;
  onChange: (value: SortMode) => void;
  mobile?: boolean;
}) {
  return (
    <label className={`shop-sort ${mobile ? "is-mobile" : ""}`}>
      <span className="sr-only">مرتب‌سازی محصولات</span>
      <select
        value={value}
        aria-label="مرتب‌سازی محصولات"
        onChange={(event) => onChange(event.target.value as SortMode)}
      >
        <option value="newest">
          {mobile ? "جدیدترین" : "مرتب‌سازی: جدیدترین"}
        </option>
        <option value="price-asc">
          {mobile ? "ارزان‌ترین" : "قیمت: کم به زیاد"}
        </option>
        <option value="price-desc">
          {mobile ? "گران‌ترین" : "قیمت: زیاد به کم"}
        </option>
      </select>
      <ChevronDown aria-hidden="true" size={16} strokeWidth={1.8} />
    </label>
  );
}

function GridToggle({
  value,
  onChange,
}: {
  value: GridMode;
  onChange: (value: GridMode) => void;
}) {
  return (
    <div className="shop-grid-toggle" aria-label="تعداد ستون‌های محصولات">
      <button
        type="button"
        className={value === 3 ? "is-active" : ""}
        aria-label="نمای سه ستونه"
        aria-pressed={value === 3}
        onClick={() => onChange(3)}
      >
        <Columns3 aria-hidden="true" size={19} strokeWidth={1.8} />
      </button>
      <button
        type="button"
        className={value === 4 ? "is-active" : ""}
        aria-label="نمای چهار ستونه"
        aria-pressed={value === 4}
        onClick={() => onChange(4)}
      >
        <Columns4 aria-hidden="true" size={19} strokeWidth={1.8} />
      </button>
    </div>
  );
}

export default function ShopPage() {
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [sortMode, setSortMode] = useState<SortMode>("newest");
  const [gridMode, setGridMode] = useState<GridMode>(3);
  const [page, setPage] = useState(1);
  const [toast, setToast] = useState("");
  const closeFilterButtonRef = useRef<HTMLButtonElement>(null);
  const {
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    cartItems,
    cartCount,
    addToCart: storeAddToCart,
  } =
    useGramissStore();

  useEffect(() => {
    const queryTimer = window.setTimeout(() => {
      const queryCategory = new URLSearchParams(window.location.search).get(
        "category",
      );
      if (
        queryCategory &&
        quickCategories.some(
          (category) =>
            category.key !== "all" && category.key === queryCategory,
        )
      ) {
        setFilters((current) => ({
          ...current,
          category: queryCategory as CategoryKey,
        }));
        setPage(1);
      }
    }, 0);

    return () => window.clearTimeout(queryTimer);
  }, []);

  const filteredProducts = useMemo(() => {
    const filtered = shopProducts.filter((product) => {
      if (filters.category && product.categoryKey !== filters.category) {
        return false;
      }
      if (
        product.priceValue < filters.minPrice ||
        product.priceValue > filters.maxPrice
      ) {
        return false;
      }
      if (
        filters.colors.length &&
        !filters.colors.includes(product.color)
      ) {
        return false;
      }
      if (
        filters.sizes.length &&
        !filters.sizes.some((size) =>
          product.sizes.includes(size as ShopProduct["sizes"][number]),
        )
      ) {
        return false;
      }
      if (
        filters.materials.length &&
        !filters.materials.includes(product.material)
      ) {
        return false;
      }
      if (filters.inStock && !product.inStock) return false;
      if (filters.discounted && !product.discounted) return false;
      return true;
    });

    return [...filtered].sort((a, b) => {
      if (sortMode === "price-asc") return a.priceValue - b.priceValue;
      if (sortMode === "price-desc") return b.priceValue - a.priceValue;
      return b.newestRank - a.newestRank;
    });
  }, [filters, sortMode]);

  const totalPages = Math.max(
    1,
    Math.ceil(filteredProducts.length / PAGE_SIZE),
  );
  const currentPage = Math.min(page, totalPages);
  const visibleProducts = filteredProducts.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );
  useEffect(() => {
    if (!filterOpen) return;

    const previousOverflow = document.documentElement.style.overflow;
    const previouslyFocused = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";

    const focusTimer = window.setTimeout(() => {
      closeFilterButtonRef.current?.focus();
    }, 0);

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setFilterOpen(false);
        return;
      }

      if (event.key !== "Tab") return;
      const dialog = document.querySelector<HTMLElement>(
        ".filter-drawer",
      );
      if (!dialog) return;
      const controls = Array.from(
        dialog.querySelectorAll<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((control) => !control.hasAttribute("hidden"));
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
      previouslyFocused?.focus();
    };
  }, [filterOpen]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function updateFilters(next: Filters) {
    setFilters(next);
    setPage(1);
  }

  function updateSort(next: SortMode) {
    setSortMode(next);
    setPage(1);
  }

  function clearFilters() {
    setFilters(emptyFilters());
    setPage(1);
    announce("همه فیلترها پاک شدند.");
  }

  function toggleWishlist(product: ShopProduct) {
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

  function addToCart(product: Product) {
    storeAddToCart(product);
    announce(`${product.name} به سبد خرید اضافه شد.`);
  }

  function toggleCompare(product: ShopProduct) {
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
    <main className="page-shell shop-page" id="top" data-node-id="30:2">
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => {
          setDrawer(null);
          setFilterOpen(false);
          setSearchOpen(true);
        }}
        onDrawer={(view) => {
          setSearchOpen(false);
          setFilterOpen(false);
          setSelectedProduct(null);
          setDrawer(view);
        }}
      />

      <section
        className="shop-intro"
        aria-labelledby="shop-title"
        data-node-id="30:56"
      >
        <div className="shop-intro-copy" dir="rtl">
          <p className="shop-kicker" dir="ltr">
            SHOP / COLLECTION
          </p>
          <h1 id="shop-title">فروشگاه</h1>
          <p>
            محصولات منتخب <bdi dir="ltr">Gramiss</bdi> با تمرکز بر کیفیت، دوام
            و استایل روزمره.
          </p>
        </div>
        <nav className="shop-breadcrumb" aria-label="مسیر صفحه" dir="rtl">
          <Link href="/">خانه</Link>
          <span aria-hidden="true">/</span>
          <span aria-current="page">فروشگاه</span>
        </nav>
      </section>

      <section className="shop-quick-categories" aria-labelledby="quick-title">
        <h2 id="quick-title">دسته‌بندی سریع</h2>
        <div
          className="shop-quick-scroll"
          aria-label="فیلتر سریع دسته‌بندی‌ها"
        >
          {quickCategories.map((category) => {
            const active =
              category.key === "all"
                ? filters.category === null
                : filters.category === category.key;
            return (
              <button
                type="button"
                className={active ? "is-active" : ""}
                aria-pressed={active}
                key={category.key}
                onClick={() =>
                  updateFilters({
                    ...filters,
                    category:
                      category.key === "all" ? null : category.key,
                  })
                }
              >
                <span>{category.persian}</span>
                <span className="sr-only"> — {category.english}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section className="shop-catalog" aria-label="محصولات فروشگاه">
        <div className="shop-catalog-toolbar">
          <p className="shop-product-count" role="status" dir="rtl">
            {formatNumber(filteredProducts.length)} محصول
          </p>
          <div className="shop-desktop-controls">
            <SortControl value={sortMode} onChange={updateSort} />
            <GridToggle value={gridMode} onChange={setGridMode} />
          </div>
          <div className="shop-mobile-controls">
            <SortControl
              value={sortMode}
              onChange={updateSort}
              mobile
            />
            <button
              type="button"
              className="shop-mobile-filter-trigger"
              aria-haspopup="dialog"
              aria-expanded={filterOpen}
              onClick={() => setFilterOpen(true)}
            >
              <SlidersHorizontal
                aria-hidden="true"
                size={17}
                strokeWidth={1.8}
              />
              <span>فیلتر</span>
            </button>
          </div>
        </div>

        <div className="shop-catalog-layout">
          <aside className="shop-desktop-filter" aria-label="فیلتر محصولات">
            <FilterPanel
              filters={filters}
              onChange={updateFilters}
              onClear={clearFilters}
              onApply={() => announce("فیلترها اعمال شدند.")}
            />
          </aside>

          <div className="shop-results">
            <ActiveFilters
              filters={filters}
              onChange={updateFilters}
              onClear={clearFilters}
            />
            {visibleProducts.length ? (
              <div
                className={`shop-product-grid columns-${gridMode}`}
                aria-live="polite"
              >
                {visibleProducts.map((product) => (
                  <ShopProductCard
                    product={product}
                    wishlisted={wishlisted.has(product.id)}
                    compared={compareIds.has(product.id)}
                    onToggleWishlist={toggleWishlist}
                    onToggleCompare={toggleCompare}
                    onAddToCart={addToCart}
                    key={product.id}
                  />
                ))}
              </div>
            ) : (
              <div className="shop-empty-results" dir="rtl">
                <h3>محصولی با این فیلترها پیدا نشد.</h3>
                <p>فیلترها را تغییر بده یا همه را پاک کن.</p>
                <Button onClick={clearFilters}>پاک کردن فیلترها</Button>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="shop-smart-cta" aria-labelledby="smart-cta-title">
        <div dir="rtl">
          <h2 id="smart-cta-title">هنوز مطمئن نیستی؟</h2>
          <p>
            به چند سؤال کوتاه پاسخ بده تا <bdi dir="ltr">Gramiss</bdi>{" "}
            مناسب‌ترین گزینه را براساس استایل و نیازت پیشنهاد دهد.
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() =>
            announce("راهنمای هوشمند در نسخه بعدی Gramiss تکمیل می‌شود.")
          }
        >
          شروع راهنمای هوشمند
        </Button>
      </section>

      <nav className="shop-pagination" aria-label="صفحه‌بندی محصولات">
        <button
          type="button"
          aria-label="صفحه قبلی"
          disabled={currentPage === 1}
          onClick={() => setPage(Math.max(1, currentPage - 1))}
        >
          <ChevronLeft aria-hidden="true" size={18} strokeWidth={1.8} />
        </button>
        {Array.from({ length: totalPages }, (_, index) => index + 1).map(
          (pageNumber) => (
            <button
              type="button"
              className={pageNumber === currentPage ? "is-active" : ""}
              aria-current={pageNumber === currentPage ? "page" : undefined}
              key={pageNumber}
              onClick={() => setPage(pageNumber)}
            >
              {formatNumber(pageNumber)}
            </button>
          ),
        )}
        <button
          type="button"
          aria-label="صفحه بعدی"
          disabled={currentPage === totalPages}
          onClick={() => setPage(Math.min(totalPages, currentPage + 1))}
        >
          <ChevronRight aria-hidden="true" size={18} strokeWidth={1.8} />
        </button>
      </nav>

      <section className="shop-buying-guide" aria-labelledby="guide-cta-title">
        <div dir="rtl">
          <h2 id="guide-cta-title">
            نمی‌دانی چه انتخابی برایت مناسب‌تر است؟
          </h2>
          <p>
            راهنماهای خرید <bdi dir="ltr">Gramiss</bdi> درباره جنس، سایز، دوام
            و استایل به تو کمک می‌کنند مطمئن‌تر انتخاب کنی.
          </p>
        </div>
        <Button href="/#journal">مشاهده راهنمای خرید</Button>
      </section>

      <Newsletter variant="shop" />
      <Footer />

      {filterOpen ? (
        <div
          className="shop-filter-overlay"
          role="presentation"
          onMouseDown={() => setFilterOpen(false)}
        >
          <aside
            className="filter-drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby="mobile-filter-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="filter-drawer-heading">
              <h2 id="mobile-filter-title">فیلتر محصولات</h2>
              <button
                ref={closeFilterButtonRef}
                type="button"
                aria-label="بستن فیلترها"
                onClick={() => setFilterOpen(false)}
              >
                <X aria-hidden="true" size={21} strokeWidth={1.8} />
              </button>
            </div>
            <FilterPanel
              mobile
              filters={filters}
              onChange={updateFilters}
              onClear={clearFilters}
              onApply={() => {
                setFilterOpen(false);
                announce("فیلترها اعمال شدند.");
              }}
            />
          </aside>
        </div>
      ) : null}

      {searchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={openProduct}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={closeDrawer}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        onAddToCart={(product) => {
          addToCart(product);
          closeDrawer();
        }}
        catalog={shopProducts}
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
