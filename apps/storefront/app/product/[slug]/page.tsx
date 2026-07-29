"use client";

/* eslint-disable @next/next/no-img-element */

import { GitCompareArrows, Heart, ShoppingBag } from "lucide-react";
import Link from "next/link";
import { notFound, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { QuickAddModal } from "../../components/commerce-ui";
import { NetworkErrorPage } from "../../components/system-states";
import {
  Drawer,
  Footer,
  Header,
  Newsletter,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../../home-client";
import { useGramissStore } from "../../hooks/use-gramiss-store";
import { useNetworkAction } from "../../hooks/use-network-action";
import { getProductDetails } from "../../lib/catalog";
import { shopProducts, type ShopProduct } from "../../shop/shop-data";

export default function CatalogProductPage() {
  const params = useParams<{ slug: string }>();
  const product = shopProducts.find((item) => item.id === params.slug);
  const {
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
  const [quickAddProduct, setQuickAddProduct] =
    useState<ShopProduct | null>(null);
  const [toast, setToast] = useState("");
  const {
    status: networkStatus,
    retry: retryProduct,
    checkInitialLoad,
  } = useNetworkAction("product");

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  if (!product) {
    notFound();
  }

  if (networkStatus === "loading") {
    return <NetworkErrorPage loading onRetry={retryProduct} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retryProduct} />;
  }

  const details = getProductDetails(product);
  const activeProduct = product;
  const isWishlisted = wishlisted.has(product.id);
  const isCompared = compareIds.has(product.id);

  function toggleWishlist() {
    setWishlisted((current) => {
      const next = new Set(current);
      if (next.has(activeProduct.id)) next.delete(activeProduct.id);
      else next.add(activeProduct.id);
      return next;
    });
    announce(
      isWishlisted
        ? `${activeProduct.name} از علاقه‌مندی‌ها حذف شد.`
        : `${activeProduct.name} به علاقه‌مندی‌ها اضافه شد.`,
    );
  }

  function toggleCompare() {
    if (isCompared) {
      window.location.assign("/compare");
      return;
    }
    const result = addToCompare(activeProduct.id);
    if (result === "limit") {
      announce("حداکثر چهار محصول را می‌توانید مقایسه کنید.");
      return;
    }
    announce(`${activeProduct.name} به مقایسه اضافه شد.`);
    window.setTimeout(() => window.location.assign("/compare"), 220);
  }

  return (
    <main className="page-shell generic-product-page">
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => setSearchOpen(true)}
        onDrawer={setDrawer}
      />
      <nav className="generic-product-breadcrumb" aria-label="مسیر صفحه" dir="rtl">
        <Link href="/">خانه</Link>
        <span>/</span>
        <Link href="/shop">فروشگاه</Link>
        <span>/</span>
        <span>{product.name}</span>
      </nav>
      <section className="generic-product-top" dir="rtl">
        <div className="generic-product-art">
          {product.badge ? <span>{product.badge}</span> : null}
          <img src={product.image} alt={product.name} />
        </div>
        <div className="generic-product-purchase">
          <small>{product.category}</small>
          <h1>{product.name}</h1>
          <p dir="ltr">{product.english}</p>
          <strong>{product.price}</strong>
          <p>{details.description}</p>
          <span className={product.inStock ? "is-in-stock" : "is-out-of-stock"}>
            {details.availability}
          </span>
          <button type="button" onClick={() => setQuickAddProduct(product)}>
            <ShoppingBag aria-hidden="true" size={19} />
            افزودن به سبد خرید
          </button>
          <div>
            <button
              className={isWishlisted ? "is-active" : ""}
              type="button"
              aria-pressed={isWishlisted}
              onClick={toggleWishlist}
            >
              <Heart
                aria-hidden="true"
                size={19}
                fill={isWishlisted ? "currentColor" : "none"}
              />
              علاقه‌مندی
            </button>
            <button
              className={isCompared ? "is-active" : ""}
              type="button"
              aria-pressed={isCompared}
              onClick={toggleCompare}
            >
              <GitCompareArrows aria-hidden="true" size={19} />
              مقایسه
            </button>
          </div>
        </div>
      </section>
      <section className="generic-product-details" dir="rtl">
        <h2>مشخصات محصول</h2>
        <dl>
          <div>
            <dt>جنس</dt>
            <dd>{product.material}</dd>
          </div>
          <div>
            <dt>رنگ</dt>
            <dd>{details.colors.join("، ")}</dd>
          </div>
          <div>
            <dt>اندازه</dt>
            <dd>{product.sizes.join("، ")}</dd>
          </div>
          <div>
            <dt>دوام</dt>
            <dd>{details.durability}</dd>
          </div>
          <div>
            <dt>مناسب برای</dt>
            <dd>{details.recommendedUse}</dd>
          </div>
          <div>
            <dt>ارسال</dt>
            <dd>{details.shipping}</dd>
          </div>
        </dl>
      </section>
      <Newsletter variant="shop" />
      <Footer />

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
      {searchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={setSelectedProduct}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={() => {
          setDrawer(null);
          setSelectedProduct(null);
        }}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        cartCount={cartCount}
        cartItems={cartItems}
        catalog={shopProducts}
        onAddToCart={(item) => {
          addToCart(item);
          announce(`${item.name} به سبد خرید اضافه شد.`);
        }}
      />
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}
