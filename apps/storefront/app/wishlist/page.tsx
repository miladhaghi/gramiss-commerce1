"use client";

import { Heart, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  CommerceProductCard,
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
import { shopProducts, type ShopProduct } from "../shop/shop-data";

type WishlistSort = "newest" | "price-asc" | "price-desc";

export default function WishlistPage() {
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
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [category, setCategory] = useState("all");
  const [sort, setSort] = useState<WishlistSort>("newest");
  const [quickAddProduct, setQuickAddProduct] =
    useState<ShopProduct | null>(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [toast, setToast] = useState("");
  const {
    status: networkStatus,
    retry: retryWishlist,
    checkInitialLoad,
  } = useNetworkAction("wishlist");

  const savedProducts = useMemo(
    () => shopProducts.filter((product) => wishlisted.has(product.id)),
    [wishlisted],
  );
  const visibleProducts = useMemo(() => {
    const filtered =
      category === "all"
        ? savedProducts
        : savedProducts.filter((product) => product.categoryKey === category);
    return [...filtered].sort((a, b) => {
      if (sort === "price-asc") return a.priceValue - b.priceValue;
      if (sort === "price-desc") return b.priceValue - a.priceValue;
      return b.newestRank - a.newestRank;
    });
  }, [category, savedProducts, sort]);
  const recommendations = useMemo(
    () =>
      shopProducts
        .filter((product) => !wishlisted.has(product.id) && product.inStock)
        .slice(0, 4),
    [wishlisted],
  );
  const categories = useMemo(
    () =>
      Array.from(
        new Map(
          savedProducts.map((product) => [
            product.categoryKey,
            product.category,
          ]),
        ),
      ),
    [savedProducts],
  );

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
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
    return <NetworkErrorPage loading onRetry={retryWishlist} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retryWishlist} />;
  }

  return (
    <main className="page-shell feature-wishlist-page" id="top">
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

      <header className="feature-page-hero wishlist-hero" dir="rtl">
        <p className="feature-kicker" dir="ltr">
          WISHLIST / SAVED
        </p>
        <h1>علاقه‌مندی‌های من</h1>
        <p>
          محصولاتی که برای بعد ذخیره کرده‌اید؛ آماده‌اند تا با یک حرکت وارد
          سبد خرید شوند.
        </p>
        <nav aria-label="مسیر صفحه">
          <Link href="/">خانه</Link>
          <span aria-hidden="true">/</span>
          <span aria-current="page">علاقه‌مندی‌ها</span>
        </nav>
      </header>

      {!hydrated ? (
        <section
          className="feature-product-grid wishlist-loading-grid"
          aria-label="در حال بارگذاری علاقه‌مندی‌ها"
        >
          {Array.from({ length: 4 }, (_, index) => (
            <div className="feature-product-skeleton" key={index} />
          ))}
        </section>
      ) : savedProducts.length ? (
        <>
          <section className="wishlist-toolbar" aria-label="مدیریت علاقه‌مندی‌ها">
            <strong dir="rtl">
              {savedProducts.length.toLocaleString("fa-IR")} محصول ذخیره‌شده
            </strong>
            <div className="wishlist-category-list" role="group">
              <button
                className={category === "all" ? "is-active" : ""}
                type="button"
                aria-pressed={category === "all"}
                onClick={() => setCategory("all")}
              >
                همه
              </button>
              {categories.map(([key, label]) => (
                <button
                  className={category === key ? "is-active" : ""}
                  type="button"
                  aria-pressed={category === key}
                  key={key}
                  onClick={() => setCategory(key)}
                >
                  {label}
                </button>
              ))}
            </div>
            <label>
              <span className="sr-only">مرتب‌سازی علاقه‌مندی‌ها</span>
              <select
                value={sort}
                onChange={(event) =>
                  setSort(event.target.value as WishlistSort)
                }
              >
                <option value="newest">مرتب‌سازی: جدیدترین</option>
                <option value="price-asc">ارزان‌ترین</option>
                <option value="price-desc">گران‌ترین</option>
              </select>
            </label>
            <button
              className="wishlist-clear"
              type="button"
              onClick={() => setConfirmClear(true)}
            >
              <Trash2 aria-hidden="true" size={17} />
              پاک کردن همه
            </button>
          </section>
          {visibleProducts.length ? (
            <section
              className="feature-product-grid wishlist-live-grid"
              aria-label="محصولات ذخیره‌شده"
            >
              {visibleProducts.map((product) => (
                <CommerceProductCard
                  product={product}
                  wishlisted
                  compared={compareIds.has(product.id)}
                  variant="wishlist"
                  onToggleWishlist={toggleWishlist}
                  onToggleCompare={toggleCompare}
                  onAddToCart={setQuickAddProduct}
                  extraAction={
                    <button
                      className="commerce-card-remove"
                      type="button"
                      onClick={() => toggleWishlist(product)}
                    >
                      حذف
                    </button>
                  }
                  key={product.id}
                />
              ))}
            </section>
          ) : (
            <section className="wishlist-filter-empty" dir="rtl">
              <h2>در این دسته محصول ذخیره‌شده‌ای ندارید.</h2>
              <button type="button" onClick={() => setCategory("all")}>
                نمایش همه
              </button>
            </section>
          )}
        </>
      ) : (
        <section className="wishlist-empty-state" role="status" dir="rtl">
          <div aria-hidden="true">
            <Heart size={92} strokeWidth={1.25} />
          </div>
          <h2>هنوز محصولی ذخیره نکرده‌اید</h2>
          <p>
            محصولات مورد علاقه‌تان را با لمس آیکون قلب ذخیره کنید تا بعداً
            راحت‌تر مقایسه و خرید کنید.
          </p>
          <Link href="/shop">مشاهده فروشگاه</Link>
        </section>
      )}

      {hydrated && savedProducts.length && recommendations.length ? (
        <section
          className="feature-recommendations"
          aria-labelledby="wishlist-recommendations-title"
        >
          <div className="feature-section-heading" dir="rtl">
            <h2 id="wishlist-recommendations-title">
              ممکن است این‌ها را هم دوست داشته باشید
            </h2>
            <p>پیشنهادهایی هماهنگ با انتخاب‌های ذخیره‌شده شما</p>
          </div>
          <div className="feature-product-grid">
            {recommendations.map((product) => (
              <CommerceProductCard
                product={product}
                wishlisted={false}
                compared={compareIds.has(product.id)}
                onToggleWishlist={toggleWishlist}
                onToggleCompare={toggleCompare}
                onAddToCart={setQuickAddProduct}
                key={product.id}
              />
            ))}
          </div>
        </section>
      ) : null}

      {hydrated && savedProducts.length ? (
        <section className="wishlist-smart-cta" dir="rtl">
          <span>GRAMISS CURATION</span>
          <h2>انتخاب کمتر، انتخاب بهتر</h2>
          <p>
            علاقه‌مندی‌ها فقط یک فهرست نیستند؛ نقطه شروع یک انتخاب آگاهانه‌اند.
            Gramiss پیشنهادها را بر اساس جنس، رنگ و سبک مورد علاقه شما دقیق‌تر
            می‌کند.
          </p>
          <Link href="/compare">
            <Sparkles aria-hidden="true" size={18} />
            مقایسه انتخاب‌ها
          </Link>
        </section>
      ) : null}

      <Newsletter variant="shop" />
      <Footer />

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
          title="پاک کردن همه علاقه‌مندی‌ها؟"
          description="تمام محصولات ذخیره‌شده از این فهرست حذف می‌شوند."
          confirmLabel="بله، پاک شود"
          onClose={() => setConfirmClear(false)}
          onConfirm={() => {
            setWishlisted(new Set());
            announce("فهرست علاقه‌مندی‌ها پاک شد.");
          }}
        />
      ) : null}
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}
