"use client";

/* eslint-disable @next/next/no-img-element */

import {
  Check,
  ChevronDown,
  GitCompareArrows,
  Heart,
  Plus,
  Search,
  ShoppingBag,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import Link from "next/link";
import {
  type CSSProperties,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ConfirmDialog,
  QuickAddModal,
} from "../components/commerce-ui";
import { NetworkErrorPage } from "../components/system-states";
import {
  Drawer,
  Footer,
  Header,
  Newsletter,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import { useGramissStore } from "../hooks/use-gramiss-store";
import { useNetworkAction } from "../hooks/use-network-action";
import { getProductDetails, getProductRoute } from "../lib/catalog";
import { normalizeSearchText } from "../lib/search-utils";
import {
  quickCategories,
  shopProducts,
  type CategoryKey,
  type ShopProduct,
} from "../shop/shop-data";

type ComparisonRow = {
  key: string;
  label: string;
  value: (product: ShopProduct) => string;
};

const comparisonRows: ComparisonRow[] = [
  {
    key: "availability",
    label: "موجودی",
    value: (product) => getProductDetails(product).availability,
  },
  {
    key: "rating",
    label: "امتیاز کاربران",
    value: (product) =>
      `${getProductDetails(product).rating.toLocaleString("fa-IR", {
        maximumFractionDigits: 1,
      })} از ۵`,
  },
  {
    key: "colors",
    label: "رنگ‌های موجود",
    value: (product) => getProductDetails(product).colors.join("، "),
  },
  {
    key: "sizes",
    label: "اندازه‌های موجود",
    value: (product) => product.sizes.join("، "),
  },
  {
    key: "material",
    label: "جنس",
    value: (product) => product.material,
  },
  {
    key: "durability",
    label: "دوام",
    value: (product) => getProductDetails(product).durability,
  },
  {
    key: "use",
    label: "مناسب برای",
    value: (product) => getProductDetails(product).recommendedUse,
  },
  {
    key: "shipping",
    label: "اطلاعات ارسال",
    value: (product) => getProductDetails(product).shipping,
  },
];

function ProductSelector({
  compared,
  onSelect,
  onClose,
}: {
  compared: Set<string>;
  onSelect: (product: ShopProduct) => void;
  onClose: () => void;
}) {
  const ref = useRef<HTMLElement>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<"all" | CategoryKey>("all");
  const normalized = normalizeSearchText(query);
  const products = useMemo(
    () =>
      shopProducts.filter((product) => {
        if (category !== "all" && product.categoryKey !== category) {
          return false;
        }
        if (!normalized) return true;
        return [
          product.name,
          product.english,
          product.category,
          product.color,
          product.material,
        ].some((value) => normalizeSearchText(value).includes(normalized));
      }),
    [category, normalized],
  );

  useEffect(() => {
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const timer = window.setTimeout(() => ref.current?.querySelector("input")?.focus());

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(
        ref.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled]), a[href]',
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
      window.clearTimeout(timer);
      window.removeEventListener("keydown", onKeyDown);
      document.documentElement.style.overflow = previousOverflow;
      previousFocus?.focus();
    };
  }, [onClose]);

  return (
    <div
      className="feature-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="compare-selector"
        role="dialog"
        aria-modal="true"
        aria-labelledby="compare-selector-title"
        ref={ref}
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="feature-dialog-heading">
          <div>
            <span>ADD PRODUCT</span>
            <h2 id="compare-selector-title">افزودن محصول به مقایسه</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="بستن">
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <label className="compare-selector-search">
          <Search aria-hidden="true" size={19} />
          <input
            type="search"
            value={query}
            placeholder="نام محصول را جست‌وجو کنید"
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <div className="compare-selector-categories" role="group">
          {quickCategories.map((item) => (
            <button
              className={category === item.key ? "is-active" : ""}
              type="button"
              aria-pressed={category === item.key}
              key={item.key}
              onClick={() => setCategory(item.key)}
            >
              {item.persian}
            </button>
          ))}
        </div>
        <div className="compare-selector-results">
          {products.map((product) => {
            const selected = compared.has(product.id);
            return (
              <button
                className={selected ? "is-selected" : ""}
                type="button"
                disabled={selected}
                key={product.id}
                onClick={() => onSelect(product)}
              >
                <img src={product.image} alt="" />
                <span>
                  <strong>{product.name}</strong>
                  <small dir="ltr">{product.english}</small>
                </span>
                {selected ? <Check aria-hidden="true" size={18} /> : <Plus aria-hidden="true" size={18} />}
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}

export default function ComparePage() {
  const {
    hydrated,
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    removeFromCompare,
    clearCompare,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectorOpen, setSelectorOpen] = useState(false);
  const [quickAddProduct, setQuickAddProduct] =
    useState<ShopProduct | null>(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [highlightDifferences, setHighlightDifferences] = useState(true);
  const [onlyDifferences, setOnlyDifferences] = useState(false);
  const [toast, setToast] = useState("");
  const {
    status: networkStatus,
    retry: retryCompare,
    checkInitialLoad,
  } = useNetworkAction("compare");

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  const products = useMemo(
    () => shopProducts.filter((product) => compareIds.has(product.id)),
    [compareIds],
  );
  const slots = useMemo(
    () =>
      Array.from(
        { length: 4 },
        (_, index) => products[index] ?? null,
      ),
    [products],
  );
  const visibleRows = useMemo(
    () =>
      comparisonRows.filter((row) => {
        if (!onlyDifferences || products.length < 2) return true;
        return (
          new Set(products.map((product) => row.value(product))).size > 1
        );
      }),
    [onlyDifferences, products],
  );

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function addProduct(product: ShopProduct) {
    const result = addToCompare(product.id);
    if (result === "limit") {
      announce("حداکثر چهار محصول را می‌توانید مقایسه کنید.");
      return;
    }
    if (result === "duplicate") {
      announce("این محصول از قبل در مقایسه است.");
      return;
    }
    announce(`${product.name} به مقایسه اضافه شد.`);
    setSelectorOpen(false);
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

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  if (networkStatus === "loading") {
    return <NetworkErrorPage loading onRetry={retryCompare} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retryCompare} />;
  }

  return (
    <main className="page-shell compare-page" id="top">
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

      <header className="feature-page-hero compare-hero" dir="rtl">
        <nav aria-label="مسیر صفحه">
          <Link href="/">خانه</Link>
          <span aria-hidden="true">/</span>
          <span aria-current="page">مقایسه محصولات</span>
        </nav>
        <h1>مقایسه محصولات</h1>
        <p>ویژگی‌ها، کیفیت، قیمت و کاربرد محصولات منتخب را کنار هم ببینید.</p>
      </header>

      <section className="compare-controls" aria-label="تنظیمات مقایسه">
        <div dir="rtl">
          <strong>
            {products.length.toLocaleString("fa-IR")} محصول انتخاب‌شده
          </strong>
          <span>برای مقایسه مفید، دست‌کم دو محصول انتخاب کنید.</span>
        </div>
        <label>
          <input
            type="checkbox"
            checked={highlightDifferences}
            onChange={(event) => setHighlightDifferences(event.target.checked)}
          />
          برجسته‌سازی تفاوت‌ها
        </label>
        <label>
          <input
            type="checkbox"
            checked={onlyDifferences}
            onChange={(event) => setOnlyDifferences(event.target.checked)}
          />
          فقط تفاوت‌ها
        </label>
        <button type="button" onClick={() => setSelectorOpen(true)}>
          <Plus aria-hidden="true" size={18} />
          افزودن محصول
        </button>
        {products.length ? (
          <button
            className="compare-clear"
            type="button"
            onClick={() => setConfirmClear(true)}
          >
            <Trash2 aria-hidden="true" size={17} />
            پاک کردن همه
          </button>
        ) : null}
      </section>

      {!hydrated ? (
        <div className="compare-loading" aria-label="در حال بارگذاری مقایسه" />
      ) : (
        <section
          className="compare-table-shell"
          aria-label="جدول مقایسه محصولات"
        >
          <div
            className="compare-table"
            style={{ "--compare-columns": 4 } as CSSProperties}
          >
            <div className="compare-label compare-label-head" dir="rtl">
              <GitCompareArrows aria-hidden="true" size={26} />
              <strong>مقایسه</strong>
              <span>ویژگی‌های کلیدی را کنار هم ببینید.</span>
            </div>
            {slots.map((product, index) =>
              product ? (
                <article
                  className="compare-product-head"
                  key={product.id}
                  dir="rtl"
                >
                  <div className="compare-product-media">
                    <Link href={getProductRoute(product)}>
                      <img src={product.image} alt={product.name} />
                    </Link>
                    <button
                      type="button"
                      aria-label={`حذف ${product.name} از مقایسه`}
                      onClick={() => {
                        removeFromCompare(product.id);
                        announce(`${product.name} از مقایسه حذف شد.`);
                      }}
                    >
                      <X aria-hidden="true" size={18} />
                    </button>
                  </div>
                  <Link href={getProductRoute(product)}>{product.name}</Link>
                  <small dir="ltr">{product.english}</small>
                  <strong>{product.price}</strong>
                  <div>
                    <button
                      className={
                        wishlisted.has(product.id) ? "is-active" : ""
                      }
                      type="button"
                      aria-pressed={wishlisted.has(product.id)}
                      onClick={() => toggleWishlist(product)}
                    >
                      <Heart
                        aria-hidden="true"
                        size={18}
                        fill={
                          wishlisted.has(product.id) ? "currentColor" : "none"
                        }
                      />
                      علاقه‌مندی
                    </button>
                    <button
                      type="button"
                      onClick={() => setQuickAddProduct(product)}
                    >
                      <ShoppingBag aria-hidden="true" size={18} />
                      افزودن به سبد
                    </button>
                  </div>
                </article>
              ) : (
                <button
                  className="compare-empty-head"
                  type="button"
                  key={`empty-${index}`}
                  onClick={() => setSelectorOpen(true)}
                >
                  <span>
                    <Plus aria-hidden="true" size={26} />
                  </span>
                  افزودن محصول
                </button>
              ),
            )}

            {visibleRows.map((row) => {
              const values = products.map((product) => row.value(product));
              const isDifferent = new Set(values).size > 1;
              return (
                <div className="compare-row" key={row.key}>
                  <div className="compare-label" dir="rtl">
                    {row.label}
                  </div>
                  {slots.map((product, index) => (
                    <div
                      className={
                        highlightDifferences && isDifferent
                          ? "compare-value is-different"
                          : "compare-value"
                      }
                      key={`${row.key}-${product?.id ?? index}`}
                      dir="rtl"
                    >
                      {product ? row.value(product) : "—"}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </section>
      )}

      <section className="compare-smart-guide" dir="rtl">
        <div>
          <span>GRAMISS SMART GUIDE</span>
          <h2>هنوز بین انتخاب‌ها مردد هستید؟</h2>
          <p>
            راهنمای هوشمند Gramiss تفاوت‌های مهم را به زبان ساده جمع‌بندی
            می‌کند تا انتخاب متناسب‌تری داشته باشید.
          </p>
        </div>
        <button
          type="button"
          onClick={() =>
            announce("راهنمای هوشمند در نسخه بعدی شخصی‌سازی می‌شود.")
          }
        >
          <Sparkles aria-hidden="true" size={18} />
          دریافت پیشنهاد Gramiss
          <ChevronDown aria-hidden="true" size={17} />
        </button>
      </section>

      <Newsletter variant="shop" />
      <Footer />

      {selectorOpen ? (
        <ProductSelector
          compared={compareIds}
          onSelect={addProduct}
          onClose={() => setSelectorOpen(false)}
        />
      ) : null}
      {quickAddProduct ? (
        <QuickAddModal
          product={quickAddProduct}
          onClose={() => setQuickAddProduct(null)}
          onConfirm={(selection) => {
            addToCart(quickAddProduct, selection);
            announce(`${quickAddProduct.name} به سبد خرید اضافه شد.`);
            setQuickAddProduct(null);
          }}
        />
      ) : null}
      {confirmClear ? (
        <ConfirmDialog
          title="پاک کردن مقایسه؟"
          description="تمام محصولات انتخاب‌شده از جدول مقایسه حذف می‌شوند."
          confirmLabel="بله، پاک شود"
          onClose={() => setConfirmClear(false)}
          onConfirm={() => {
            clearCompare();
            announce("فهرست مقایسه پاک شد.");
          }}
        />
      ) : null}
      {searchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={(product) => setSelectedProduct(product)}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={closeDrawer}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        cartCount={cartCount}
        cartItems={cartItems}
        catalog={shopProducts}
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
