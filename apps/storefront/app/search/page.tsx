"use client";

/* eslint-disable @next/next/no-img-element */

import {
  ArrowLeft,
  ChevronLeft,
  Search,
  SlidersHorizontal,
  Sparkles,
  X,
} from "lucide-react";
import Link from "next/link";
import {
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  CommerceProductCard,
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
import {
  getProductSearchFields,
  getProductRoute,
} from "../lib/catalog";
import {
  clearRecentSearches,
  normalizeSearchText,
  readRecentSearches,
  removeRecentSearch,
  saveRecentSearch,
} from "../lib/search-utils";
import {
  quickCategories,
  shopProducts,
  type CategoryKey,
  type ShopProduct,
} from "../shop/shop-data";

type SearchSort = "relevance" | "newest" | "price-asc" | "price-desc";
const PAGE_SIZE = 8;
const MAX_PRICE = 5_000_000;

function relevanceScore(product: ShopProduct, query: string) {
  if (!query) return product.newestRank;
  const title = normalizeSearchText(product.name);
  const english = normalizeSearchText(product.english);
  let score = 0;
  if (title === query || english === query) score += 100;
  if (title.startsWith(query) || english.startsWith(query)) score += 45;
  if (title.includes(query) || english.includes(query)) score += 30;
  for (const field of getProductSearchFields(product)) {
    if (normalizeSearchText(field).includes(query)) score += 8;
  }
  return score + product.newestRank / 100;
}

function SearchFilterDrawer({
  open,
  category,
  minPrice,
  maxPrice,
  onCategory,
  onMinPrice,
  onMaxPrice,
  onClear,
  onClose,
}: {
  open: boolean;
  category: "all" | CategoryKey;
  minPrice: number;
  maxPrice: number;
  onCategory: (category: "all" | CategoryKey) => void;
  onMinPrice: (value: number) => void;
  onMaxPrice: (value: number) => void;
  onClear: () => void;
  onClose: () => void;
}) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const timer = window.setTimeout(() => ref.current?.querySelector("button")?.focus());

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(
        ref.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled])',
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
  }, [onClose, open]);

  if (!open) return null;

  return (
    <div
      className="feature-overlay search-filter-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <aside
        className="search-filter-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-filter-title"
        ref={ref}
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="feature-dialog-heading">
          <h2 id="search-filter-title">فیلتر نتایج</h2>
          <button type="button" onClick={onClose} aria-label="بستن">
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <fieldset>
          <legend>دسته‌بندی</legend>
          <div className="search-filter-categories">
            {quickCategories.map((item) => (
              <button
                className={category === item.key ? "is-active" : ""}
                type="button"
                aria-pressed={category === item.key}
                key={item.key}
                onClick={() => onCategory(item.key)}
              >
                {item.persian}
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset>
          <legend>بازه قیمت</legend>
          <label>
            حداقل
            <input
              type="range"
              min="0"
              max={MAX_PRICE}
              step="100000"
              value={minPrice}
              onChange={(event) => onMinPrice(Number(event.target.value))}
            />
            <span>{minPrice.toLocaleString("fa-IR")} تومان</span>
          </label>
          <label>
            حداکثر
            <input
              type="range"
              min="0"
              max={MAX_PRICE}
              step="100000"
              value={maxPrice}
              onChange={(event) => onMaxPrice(Number(event.target.value))}
            />
            <span>{maxPrice.toLocaleString("fa-IR")} تومان</span>
          </label>
        </fieldset>
        <div className="search-filter-actions">
          <button type="button" onClick={onClear}>
            پاک کردن فیلترها
          </button>
          <button type="button" onClick={onClose}>
            نمایش نتایج
          </button>
        </div>
      </aside>
    </div>
  );
}

export default function SearchPage() {
  const {
    hydrated,
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [headerSearchOpen, setHeaderSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [draftQuery, setDraftQuery] = useState("");
  const [query, setQuery] = useState("");
  const [recent, setRecent] = useState<string[]>([]);
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState<"all" | CategoryKey>("all");
  const [sort, setSort] = useState<SearchSort>("relevance");
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(MAX_PRICE);
  const [page, setPage] = useState(1);
  const [filterOpen, setFilterOpen] = useState(false);
  const [quickAddProduct, setQuickAddProduct] =
    useState<ShopProduct | null>(null);
  const [toast, setToast] = useState("");
  const {
    status: networkStatus,
    attempt: attemptSearch,
    retry: retrySearch,
    checkInitialLoad,
  } = useNetworkAction("search");

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  useEffect(() => {
    function syncFromUrl() {
      const value = new URLSearchParams(window.location.search).get("q") ?? "";
      setDraftQuery(value);
      setQuery(value.trim());
      setCategory("all");
      setMinPrice(0);
      setMaxPrice(MAX_PRICE);
      setPage(1);
      setLoading(false);
    }

    const timer = window.setTimeout(() => {
      syncFromUrl();
      setRecent(readRecentSearches());
      setInitialized(true);
    }, 0);
    window.addEventListener("popstate", syncFromUrl);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("popstate", syncFromUrl);
    };
  }, []);

  useEffect(() => {
    if (!initialized) return;
    const loadingTimer = window.setTimeout(() => setLoading(true), 0);
    const timer = window.setTimeout(() => {
      const next = draftQuery.trim();
      setQuery(next);
      setPage(1);
      setLoading(false);
    }, 280);
    return () => {
      window.clearTimeout(loadingTimer);
      window.clearTimeout(timer);
    };
  }, [draftQuery, initialized]);

  const normalizedQuery = normalizeSearchText(query);
  const matchingProducts = useMemo(() => {
    const filtered = shopProducts.filter((product) => {
      if (
        normalizedQuery &&
        !getProductSearchFields(product).some((field) =>
          normalizeSearchText(field).includes(normalizedQuery),
        )
      ) {
        return false;
      }
      if (category !== "all" && product.categoryKey !== category) return false;
      if (product.priceValue < minPrice || product.priceValue > maxPrice) {
        return false;
      }
      return true;
    });

    return [...filtered].sort((a, b) => {
      if (sort === "newest") return b.newestRank - a.newestRank;
      if (sort === "price-asc") return a.priceValue - b.priceValue;
      if (sort === "price-desc") return b.priceValue - a.priceValue;
      return (
        relevanceScore(b, normalizedQuery) -
        relevanceScore(a, normalizedQuery)
      );
    });
  }, [category, maxPrice, minPrice, normalizedQuery, sort]);
  const totalPages = Math.max(1, Math.ceil(matchingProducts.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const visibleProducts = matchingProducts.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );
  const liveSuggestions = useMemo(() => {
    const normalized = normalizeSearchText(draftQuery);
    if (!normalized) return [];
    return shopProducts
      .filter((product) =>
        getProductSearchFields(product).some((field) =>
          normalizeSearchText(field).includes(normalized),
        ),
      )
      .slice(0, 4);
  }, [draftQuery]);
  const recommended = useMemo(
    () => [...shopProducts].sort((a, b) => b.newestRank - a.newestRank).slice(0, 4),
    [],
  );
  const priceFiltered = minPrice > 0 || maxPrice < MAX_PRICE;

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function submitSearch(event?: FormEvent<HTMLFormElement>, value = draftQuery) {
    event?.preventDefault();
    const next = value.trim();
    if (!next) return;
    attemptSearch(() => {
      setDraftQuery(next);
      setQuery(next);
      setRecent(saveRecentSearch(next));
      setPage(1);
      const url = `/search?q=${encodeURIComponent(next)}`;
      window.history.pushState({}, "", url);
    });
  }

  function clearFilters() {
    setCategory("all");
    setMinPrice(0);
    setMaxPrice(MAX_PRICE);
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

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  if (networkStatus === "loading") {
    return <NetworkErrorPage loading onRetry={retrySearch} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retrySearch} />;
  }

  return (
    <main className="page-shell search-page" id="top">
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => {
          setDrawer(null);
          setHeaderSearchOpen(true);
        }}
        onDrawer={(view) => {
          setSelectedProduct(null);
          setDrawer(view);
        }}
      />

      <header className="search-page-hero" dir="rtl">
        <span>جست‌وجوی هوشمند Gramiss</span>
        <h1>دنبال چه چیزی هستید؟</h1>
        <form role="search" onSubmit={submitSearch}>
          <Search aria-hidden="true" size={24} strokeWidth={1.7} />
          <input
            type="search"
            value={draftQuery}
            placeholder="کلاه، کیف، جوراب یا جنس موردنظر"
            aria-label="جست‌وجوی محصولات"
            onChange={(event) => setDraftQuery(event.target.value)}
          />
          {draftQuery ? (
            <button
              type="button"
              onClick={() => {
                setDraftQuery("");
                setQuery("");
              }}
            >
              پاک کردن
            </button>
          ) : null}
        </form>
        {draftQuery && liveSuggestions.length ? (
          <div className="search-page-suggestions" aria-label="پیشنهادها">
            {liveSuggestions.map((product) => (
              <Link href={getProductRoute(product)} key={product.id}>
                <img src={product.image} alt="" />
                <span>
                  <strong>{product.name}</strong>
                  <small>{product.price}</small>
                </span>
              </Link>
            ))}
          </div>
        ) : null}
      </header>

      {!query && initialized ? (
        <section className="search-empty-query">
          <div className="search-discovery-grid">
            <article dir="rtl">
              <div>
                <h2>جست‌وجوهای اخیر</h2>
                {recent.length ? (
                  <button
                    type="button"
                    onClick={() => {
                      clearRecentSearches();
                      setRecent([]);
                    }}
                  >
                    پاک کردن
                  </button>
                ) : null}
              </div>
              {recent.length ? (
                <ul>
                  {recent.map((item) => (
                    <li key={item}>
                      <button
                        type="button"
                        onClick={() => submitSearch(undefined, item)}
                      >
                        {item}
                      </button>
                      <button
                        type="button"
                        aria-label={`حذف جست‌وجوی ${item}`}
                        onClick={() => setRecent(removeRecentSearch(item))}
                      >
                        <X aria-hidden="true" size={15} />
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>جست‌وجوهای شما فقط روی همین دستگاه نمایش داده می‌شوند.</p>
              )}
            </article>
            <article dir="rtl">
              <h2>جست‌وجوهای محبوب</h2>
              <div className="search-popular-links">
                {["کلاه آبی", "کیف دوشی", "جوراب نخی", "کتونی سفید"].map(
                  (item) => (
                    <button
                      type="button"
                      key={item}
                      onClick={() => submitSearch(undefined, item)}
                    >
                      {item}
                    </button>
                  ),
                )}
              </div>
            </article>
            <article dir="rtl">
              <h2>دسته‌بندی‌ها</h2>
              <div className="search-popular-links">
                {quickCategories.slice(1).map((item) => (
                  <Link href={`/search?q=${encodeURIComponent(item.persian)}`} key={item.key}>
                    {item.persian}
                  </Link>
                ))}
              </div>
            </article>
          </div>
          <div className="feature-section-heading" dir="rtl">
            <h2>پیشنهاد Gramiss برای شروع</h2>
            <p>محصولات منتخب و آماده ارسال</p>
          </div>
          <div className="feature-product-grid">
            {recommended.map((product) => (
              <CommerceProductCard
                product={product}
                wishlisted={wishlisted.has(product.id)}
                compared={compareIds.has(product.id)}
                onToggleWishlist={toggleWishlist}
                onToggleCompare={toggleCompare}
                onAddToCart={setQuickAddProduct}
                key={product.id}
              />
            ))}
          </div>
        </section>
      ) : (
        <section className="search-results-section">
          <div className="search-category-chips" role="group">
            {quickCategories.map((item) => (
              <button
                className={category === item.key ? "is-active" : ""}
                type="button"
                aria-pressed={category === item.key}
                key={item.key}
                onClick={() => {
                  setCategory(item.key);
                  setPage(1);
                }}
              >
                {item.persian}
              </button>
            ))}
          </div>
          <div className="search-results-toolbar" dir="rtl">
            <div>
              <h2>
                نتایج جست‌وجو برای «{query}»
              </h2>
              <span>{matchingProducts.length.toLocaleString("fa-IR")} نتیجه</span>
            </div>
            <label>
              <span className="sr-only">مرتب‌سازی</span>
              <select
                value={sort}
                onChange={(event) => {
                  setSort(event.target.value as SearchSort);
                  setPage(1);
                }}
              >
                <option value="relevance">مرتبط‌ترین</option>
                <option value="newest">جدیدترین</option>
                <option value="price-asc">ارزان‌ترین</option>
                <option value="price-desc">گران‌ترین</option>
              </select>
            </label>
            <button type="button" onClick={() => setFilterOpen(true)}>
              <SlidersHorizontal aria-hidden="true" size={18} />
              فیلتر
            </button>
          </div>

          {category !== "all" || priceFiltered ? (
            <div className="search-active-filters" dir="rtl">
              <span>فیلترهای فعال:</span>
              {category !== "all" ? (
                <button type="button" onClick={() => setCategory("all")}>
                  {
                    quickCategories.find((item) => item.key === category)
                      ?.persian
                  }
                  <X aria-hidden="true" size={14} />
                </button>
              ) : null}
              {priceFiltered ? (
                <button
                  type="button"
                  onClick={() => {
                    setMinPrice(0);
                    setMaxPrice(MAX_PRICE);
                  }}
                >
                  بازه قیمت
                  <X aria-hidden="true" size={14} />
                </button>
              ) : null}
              <button type="button" onClick={clearFilters}>
                پاک کردن همه
              </button>
            </div>
          ) : null}

          {loading || !hydrated ? (
            <div className="feature-product-grid" aria-label="در حال جست‌وجو">
              {Array.from({ length: 8 }, (_, index) => (
                <div className="feature-product-skeleton" key={index} />
              ))}
            </div>
          ) : visibleProducts.length ? (
            <>
              <div className="feature-product-grid search-product-grid">
                {visibleProducts.map((product) => (
                  <CommerceProductCard
                    product={product}
                    wishlisted={wishlisted.has(product.id)}
                    compared={compareIds.has(product.id)}
                    onToggleWishlist={toggleWishlist}
                    onToggleCompare={toggleCompare}
                    onAddToCart={setQuickAddProduct}
                    key={product.id}
                  />
                ))}
              </div>
              {totalPages > 1 ? (
                <nav className="feature-pagination" aria-label="صفحه‌بندی">
                  <button
                    type="button"
                    disabled={currentPage === 1}
                    onClick={() => setPage((current) => Math.max(1, current - 1))}
                  >
                    <ChevronLeft aria-hidden="true" size={18} />
                  </button>
                  {Array.from({ length: totalPages }, (_, index) => index + 1).map(
                    (number) => (
                      <button
                        className={currentPage === number ? "is-active" : ""}
                        type="button"
                        aria-current={currentPage === number ? "page" : undefined}
                        key={number}
                        onClick={() => setPage(number)}
                      >
                        {number.toLocaleString("fa-IR")}
                      </button>
                    ),
                  )}
                  <button
                    type="button"
                    disabled={currentPage === totalPages}
                    onClick={() =>
                      setPage((current) => Math.min(totalPages, current + 1))
                    }
                  >
                    <ChevronLeft
                      aria-hidden="true"
                      size={18}
                      className="is-next"
                    />
                  </button>
                </nav>
              ) : null}
              <div className="search-related" dir="rtl">
                <strong>جست‌وجوهای مرتبط</strong>
                {["استایل روزمره", "انتخاب رنگ", "راهنمای جنس"].map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => submitSearch(undefined, item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div className="search-no-results" dir="rtl">
              <div>
                <Search aria-hidden="true" size={48} strokeWidth={1.35} />
              </div>
              <h2>برای «{query}» محصولی پیدا نشد</h2>
              <p>
                فیلترها را حذف کنید، عبارت کوتاه‌تری بنویسید یا از
                دسته‌بندی‌های پیشنهادی کمک بگیرید.
              </p>
              {(category !== "all" || priceFiltered) && (
                <button type="button" onClick={clearFilters}>
                  حذف فیلترها
                </button>
              )}
              <div className="search-no-result-categories">
                {quickCategories.slice(1, 4).map((item) => (
                  <button
                    type="button"
                    key={item.key}
                    onClick={() => submitSearch(undefined, item.persian)}
                  >
                    {item.persian}
                  </button>
                ))}
              </div>
              <Link href="/shop">
                بازگشت به فروشگاه
                <ArrowLeft aria-hidden="true" size={18} />
              </Link>
              <div className="feature-section-heading">
                <h3>محصولات محبوب</h3>
              </div>
              <div className="feature-product-grid">
                {recommended.slice(0, 4).map((product) => (
                  <CommerceProductCard
                    product={product}
                    wishlisted={wishlisted.has(product.id)}
                    compared={compareIds.has(product.id)}
                    onToggleWishlist={toggleWishlist}
                    onToggleCompare={toggleCompare}
                    onAddToCart={setQuickAddProduct}
                    key={product.id}
                  />
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      <section className="search-smart-guide" dir="rtl">
        <div>
          <span>GRAMISS SMART GUIDE</span>
          <h2>نتیجه دقیق‌تر می‌خواهید؟</h2>
          <p>
            راهنمای هوشمند براساس کاربرد، رنگ، بودجه و سبک مدنظر شما مسیر
            انتخاب را کوتاه‌تر می‌کند.
          </p>
        </div>
        <button
          type="button"
          onClick={() =>
            announce("راهنمای هوشمند در نسخه بعدی Gramiss فعال می‌شود.")
          }
        >
          <Sparkles aria-hidden="true" size={18} />
          شروع راهنمای هوشمند
        </button>
      </section>

      <Newsletter variant="shop" />
      <Footer />

      <SearchFilterDrawer
        open={filterOpen}
        category={category}
        minPrice={minPrice}
        maxPrice={maxPrice}
        onCategory={(value) => {
          setCategory(value);
          setPage(1);
        }}
        onMinPrice={(value) => {
          setMinPrice(Math.min(value, maxPrice));
          setPage(1);
        }}
        onMaxPrice={(value) => {
          setMaxPrice(Math.max(value, minPrice));
          setPage(1);
        }}
        onClear={clearFilters}
        onClose={() => setFilterOpen(false)}
      />
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
      {headerSearchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setHeaderSearchOpen(false)}
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
