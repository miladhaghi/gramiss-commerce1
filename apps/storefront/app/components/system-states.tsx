"use client";

import {
  CircleAlert,
  Headphones,
  PackageOpen,
  RotateCw,
  Search,
  SearchX,
  ShoppingBag,
} from "lucide-react";
import Link from "next/link";
import { type ReactNode, useState } from "react";
import {
  Drawer,
  Footer,
  Header,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import { useGramissStore } from "../hooks/use-gramiss-store";
import { shopProducts } from "../shop/shop-data";

export function GramissSkeleton({
  rows = 3,
  label = "در حال بارگذاری",
}: {
  rows?: number;
  label?: string;
}) {
  return (
    <div
      className="gramiss-skeleton"
      aria-busy="true"
      aria-label={label}
      role="status"
    >
      <span className="gramiss-skeleton-title" />
      {Array.from({ length: rows }, (_, index) => (
        <span className="gramiss-skeleton-row" key={index} />
      ))}
    </div>
  );
}

export function SystemStateContent({
  visual,
  eyebrow,
  title,
  description,
  children,
  className = "",
  role,
}: {
  visual: ReactNode;
  eyebrow?: string;
  title: string;
  description: string;
  children: ReactNode;
  className?: string;
  role?: "alert" | "status";
}) {
  return (
    <section
      className={`system-state-content ${className}`.trim()}
      dir="rtl"
      role={role}
      aria-live={role === "alert" ? "assertive" : "polite"}
    >
      <div className="system-state-visual" aria-hidden="true">
        {visual}
      </div>
      {eyebrow ? <span className="system-state-eyebrow">{eyebrow}</span> : null}
      <h1>{title}</h1>
      <p>{description}</p>
      <div className="system-state-actions">{children}</div>
    </section>
  );
}

export function NetworkError({
  onRetry,
  loading = false,
  compact = false,
}: {
  onRetry: () => void;
  loading?: boolean;
  compact?: boolean;
}) {
  if (loading) {
    return (
      <section className={`system-state-loading ${compact ? "is-compact" : ""}`}>
        <GramissSkeleton rows={3} label="در حال تلاش مجدد" />
      </section>
    );
  }

  return (
    <SystemStateContent
      className={`network-error-state ${compact ? "is-compact" : ""}`}
      visual={<CircleAlert size={68} strokeWidth={1.35} />}
      eyebrow="NETWORK ERROR"
      title="اتصال برقرار نشد"
      description="اینترنت خود را بررسی کنید و دوباره تلاش کنید."
      role="alert"
    >
      <button className="system-state-primary" type="button" onClick={onRetry}>
        <RotateCw aria-hidden="true" size={18} strokeWidth={1.8} />
        تلاش مجدد
      </button>
      <Link className="system-state-secondary" href="/">
        بازگشت به صفحه اصلی
      </Link>
      <a
        className="system-state-support"
        href="mailto:hello@gramiss.com?subject=Gramiss%20Support"
      >
        <Headphones aria-hidden="true" size={17} strokeWidth={1.8} />
        تماس با پشتیبانی
      </a>
    </SystemStateContent>
  );
}

export function EmptyOrdersState({ compact = false }: { compact?: boolean }) {
  return (
    <SystemStateContent
      className={`empty-orders-state ${compact ? "is-compact" : ""}`}
      visual={<PackageOpen size={70} strokeWidth={1.25} />}
      title={compact ? "هنوز سفارشی ندارید" : "هنوز سفارشی ثبت نکرده‌اید"}
      description={
        compact
          ? "اولین خرید شما اینجا نمایش داده می‌شود."
          : "بعد از اولین خرید، وضعیت و تاریخچه سفارش‌ها در این بخش نمایش داده می‌شود."
      }
      role="status"
    >
      <Link className="system-state-primary" href="/shop">
        شروع خرید
      </Link>
    </SystemStateContent>
  );
}

export function NotFoundState() {
  return (
    <SystemPageChrome>
      <SystemStateContent
        className="not-found-state"
        visual={<SearchX size={78} strokeWidth={1.2} />}
        eyebrow="404"
        title="صفحه موردنظر پیدا نشد"
        description="ممکن است آدرس تغییر کرده باشد یا این صفحه دیگر وجود نداشته باشد."
        role="status"
      >
        <Link className="system-state-primary" href="/">
          بازگشت به صفحه اصلی
        </Link>
        <Link className="system-state-secondary" href="/shop">
          <ShoppingBag aria-hidden="true" size={17} strokeWidth={1.8} />
          رفتن به فروشگاه
        </Link>
        <Link className="not-found-search" href="/search">
          <Search aria-hidden="true" size={17} strokeWidth={1.8} />
          جست‌وجوی محصولات
        </Link>
      </SystemStateContent>
    </SystemPageChrome>
  );
}

export function SystemPageChrome({ children }: { children: ReactNode }) {
  const {
    wishlisted,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  return (
    <main className="page-shell system-page" id="top">
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
      {children}
      <Footer />
      {searchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={(product) => {
            setSearchOpen(false);
            setSelectedProduct(product);
          }}
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
        productsHref="/shop"
        onAddToCart={(product) => {
          addToCart(product);
          setDrawer(null);
          setSelectedProduct(null);
        }}
      />
    </main>
  );
}

export function NetworkErrorPage({
  onRetry,
  loading = false,
}: {
  onRetry: () => void;
  loading?: boolean;
}) {
  return (
    <SystemPageChrome>
      <NetworkError onRetry={onRetry} loading={loading} />
    </SystemPageChrome>
  );
}
