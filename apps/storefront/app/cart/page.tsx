"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useMemo, useState } from "react";
import {
  ArrowLeft,
  Check,
  Minus,
  Plus,
  ShoppingBag,
  Tag,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import {
  Drawer,
  Footer,
  getProductHref,
  Header,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import {
  formatToman,
  getCartItemHref,
  useGramissStore,
} from "../hooks/use-gramiss-store";
import { shopProducts } from "../shop/shop-data";

export default function CartPage() {
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [toast, setToast] = useState("");
  const {
    wishlisted,
    cartItems,
    cartCount,
    subtotal,
    shippingCost,
    discountCode,
    discount,
    finalTotal,
    addToCart,
    updateQuantity,
    removeFromCart,
    applyDiscount,
    clearDiscount,
  } = useGramissStore();
  const [discountInput, setDiscountInput] = useState(discountCode);
  const [discountMessage, setDiscountMessage] = useState("");

  const recommendations = useMemo(
    () =>
      shopProducts
        .filter(
          (product) => !cartItems.some((item) => item.id === product.id),
        )
        .slice(0, 3),
    [cartItems],
  );
  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  function submitDiscount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const success = applyDiscount(discountInput);
    if (success) {
      setDiscountMessage("کد تخفیف با موفقیت اعمال شد.");
      announce("تخفیف روی سفارش اعمال شد.");
      return;
    }
    setDiscountMessage("کد تخفیف معتبر نیست.");
  }

  return (
    <main
      className="page-shell commerce-page cart-page"
      id="top"
      data-node-id="33:2"
    >
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => {
          setDrawer(null);
          setSearchOpen(true);
        }}
        onDrawer={(view) => {
          setSearchOpen(false);
          setSelectedProduct(null);
          setDrawer(view);
        }}
      />

      <section className="cart-heading" aria-labelledby="cart-title">
        <h1 id="cart-title">سبد خرید</h1>
        <p role="status">{cartCount.toLocaleString("fa-IR")} کالا در سبد شما</p>
      </section>

      {cartItems.length ? (
        <>
          <section className="cart-products" aria-label="محصولات سبد خرید">
            <div className="cart-table-head" aria-hidden="true">
              <span>محصول</span>
              <span>تعداد</span>
              <span>قیمت</span>
            </div>
            <div className="cart-product-list">
              {cartItems.map((item) => (
                <article className="cart-product-row" key={item.lineId}>
                  <div className="cart-product-main">
                    <Link
                      className="cart-product-image"
                      href={getCartItemHref(item)}
                      aria-label={`مشاهده ${item.name}`}
                    >
                      <img
                        src={item.image}
                        width="160"
                        height="160"
                        alt={item.name}
                      />
                    </Link>
                    <div className="cart-product-copy">
                      <Link href={getCartItemHref(item)}>{item.name}</Link>
                      <span dir="ltr">{item.english}</span>
                      {item.color || item.size ? (
                        <p>
                          {item.color ? `رنگ: ${item.color}` : null}
                          {item.color && item.size ? (
                            <i aria-hidden="true">|</i>
                          ) : null}
                          {item.size ? `سایز: ${item.size}` : null}
                        </p>
                      ) : null}
                      <button
                        className="cart-remove"
                        type="button"
                        onClick={() => {
                          removeFromCart(item.lineId);
                          announce(`${item.name} از سبد خرید حذف شد.`);
                        }}
                      >
                        <Trash2
                          aria-hidden="true"
                          size={16}
                          strokeWidth={1.8}
                        />
                        حذف
                      </button>
                    </div>
                  </div>

                  <div
                    className="cart-quantity"
                    aria-label={`تعداد ${item.name}`}
                  >
                    <button
                      type="button"
                      aria-label={`کاهش تعداد ${item.name}`}
                      disabled={item.quantity <= 1}
                      onClick={() =>
                        updateQuantity(item.lineId, item.quantity - 1)
                      }
                    >
                      <Minus aria-hidden="true" size={17} strokeWidth={1.8} />
                    </button>
                    <output aria-live="polite">
                      {item.quantity.toLocaleString("fa-IR")}
                    </output>
                    <button
                      type="button"
                      aria-label={`افزایش تعداد ${item.name}`}
                      onClick={() =>
                        updateQuantity(item.lineId, item.quantity + 1)
                      }
                    >
                      <Plus aria-hidden="true" size={17} strokeWidth={1.8} />
                    </button>
                  </div>

                  <div className="cart-product-price">
                    <strong>
                      {formatToman(item.unitPrice * item.quantity)}
                    </strong>
                    <span>قیمت واحد: {formatToman(item.unitPrice)}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <div className="cart-after-products">
            <section className="cart-summary" aria-labelledby="summary-title">
              <h2 id="summary-title">خلاصه سفارش</h2>
              <dl>
                <div>
                  <dt>جمع کالاها</dt>
                  <dd>{formatToman(subtotal)}</dd>
                </div>
                <div>
                  <dt>هزینه ارسال</dt>
                  <dd>{shippingCost ? formatToman(shippingCost) : "رایگان"}</dd>
                </div>
                {discount ? (
                  <div className="is-discount">
                    <dt>تخفیف</dt>
                    <dd>− {formatToman(discount)}</dd>
                  </div>
                ) : null}
                <div className="cart-final-total">
                  <dt>مبلغ قابل پرداخت</dt>
                  <dd>{formatToman(finalTotal)}</dd>
                </div>
              </dl>

              <form
                className="cart-discount"
                onSubmit={submitDiscount}
                noValidate
              >
                <label htmlFor="cart-discount-code">کد تخفیف</label>
                <div>
                  <Tag aria-hidden="true" size={18} strokeWidth={1.8} />
                  <input
                    id="cart-discount-code"
                    type="text"
                    value={discountInput}
                    placeholder="GRAMISS10"
                    autoComplete="off"
                    dir="ltr"
                    onChange={(event) => {
                      setDiscountInput(event.target.value);
                      setDiscountMessage("");
                    }}
                  />
                  <button type="submit">
                    {discount ? (
                      <Check
                        aria-hidden="true"
                        size={18}
                        strokeWidth={2}
                      />
                    ) : (
                      "اعمال"
                    )}
                  </button>
                </div>
                <p
                  className={
                    discountMessage.includes("موفقیت")
                      ? "is-success"
                      : discountMessage
                        ? "is-error"
                        : ""
                  }
                  role="status"
                >
                  {discountMessage ||
                    (discount
                      ? `${discountCode} فعال است.`
                      : "کد را وارد و اعمال کنید.")}
                  {discount ? (
                    <button
                      type="button"
                      onClick={() => {
                        clearDiscount();
                        setDiscountInput("");
                        setDiscountMessage("کد تخفیف حذف شد.");
                      }}
                    >
                      حذف کد
                    </button>
                  ) : null}
                </p>
              </form>

              <Link className="commerce-primary-link" href="/checkout">
                ادامه و ثبت سفارش
                <ArrowLeft aria-hidden="true" size={19} strokeWidth={1.8} />
              </Link>
              <Link className="commerce-secondary-link" href="/shop">
                ادامه خرید
              </Link>
              <p className="cart-trust">
                بازگشت ۷ روزه <i>•</i> پرداخت امن <i>•</i> ارسال رایگان
              </p>
            </section>
          </div>

          <section
            className="cart-recommendations"
            aria-labelledby="recommendation-title"
          >
            <div className="cart-recommendation-copy">
              <h2 id="recommendation-title">فراموش نکردی؟</h2>
              <p>محصولات مکملی که انتخابت را کامل می‌کنند.</p>
            </div>
            <div className="cart-recommendation-grid">
              {recommendations.map((product) => (
                <article key={product.id}>
                  <Link
                    href={getProductHref(product, "/shop")}
                    aria-label={`مشاهده ${product.name}`}
                  >
                    <img
                      src={product.image}
                      width="180"
                      height="160"
                      alt={product.name}
                    />
                  </Link>
                  <div>
                    <Link href={getProductHref(product, "/shop")}>
                      {product.name}
                    </Link>
                    <span>{product.price}</span>
                    <button
                      type="button"
                      onClick={() => {
                        addToCart(product);
                        announce(`${product.name} به سبد خرید اضافه شد.`);
                      }}
                    >
                      افزودن
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : (
        <section className="cart-empty-state" aria-labelledby="empty-cart-title">
          <span aria-hidden="true">
            <ShoppingBag size={48} strokeWidth={1.4} />
          </span>
          <h2 id="empty-cart-title">سبد خریدت خالی است.</h2>
          <p>محصولی انتخاب نکرده‌ای؛ از فروشگاه شروع کن.</p>
          <Link className="commerce-primary-link" href="/shop">
            بازگشت به فروشگاه
            <ArrowLeft aria-hidden="true" size={19} strokeWidth={1.8} />
          </Link>
        </section>
      )}

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
        onAddToCart={(product) => {
          addToCart(product);
          announce(`${product.name} به سبد خرید اضافه شد.`);
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
