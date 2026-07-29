"use client";

/* eslint-disable @next/next/no-img-element */

import {
  Check,
  Headphones,
  ShoppingBag,
  Truck,
} from "lucide-react";
import Link from "next/link";
import { SystemPageChrome } from "../components/system-states";
import {
  demoOrders,
  formatTomanAmount,
} from "../lib/demo-orders";

export default function OrderSuccessPage() {
  const order = demoOrders[0];

  return (
    <SystemPageChrome>
      <div
        className="order-success-main"
        dir="rtl"
        data-node-id="49:3"
      >
        <span className="order-demo-label">
          پیش‌نمایش صفحه تأیید سفارش
        </span>

        <header className="order-success-hero">
          <div className="order-success-icon" aria-hidden="true">
            <Check size={58} strokeWidth={2.4} />
          </div>
          <h1>سفارش شما با موفقیت ثبت شد</h1>
          <p className="order-success-number" dir="rtl">
            شماره سفارش: <bdi dir="ltr">{order.id}</bdi>
          </p>
          <p className="order-success-message">
            این صفحه فقط یک پیش‌نمایش رابط کاربری با داده‌های نمونه است؛ هیچ
            پرداخت یا سفارش واقعی ثبت نشده است. وضعیت نمونه:{" "}
            <strong>{order.status}</strong>
          </p>
        </header>

        <div className="order-success-grid">
          <section className="order-panel" aria-labelledby="products-title">
            <h2 id="products-title">خلاصه محصولات سفارش نمونه</h2>
            <div className="order-product-list">
              {order.products.map((product) => (
                <article className="order-product" key={product.id}>
                  <img src={product.image} alt={product.name} />
                  <div className="order-product-copy">
                    <strong>{product.name}</strong>
                    <small dir="ltr">{product.english}</small>
                    <span>
                      تعداد: {product.quantity.toLocaleString("fa-IR")}
                    </span>
                  </div>
                  <b className="order-product-price">
                    {formatTomanAmount(product.unitPrice * product.quantity)}
                  </b>
                </article>
              ))}
            </div>
          </section>

          <div className="order-success-side">
            <section className="order-panel" aria-labelledby="shipping-title">
              <h2 id="shipping-title">ارسال و پرداخت</h2>
              <dl className="order-detail-list">
                <div>
                  <dt>گیرنده و آدرس</dt>
                  <dd>
                    {order.recipient}
                    <br />
                    {order.address}
                  </dd>
                </div>
                <div>
                  <dt>روش ارسال</dt>
                  <dd>
                    {order.shippingMethod}
                    <br />
                    {order.shippingEta}
                  </dd>
                </div>
                <div>
                  <dt>روش پرداخت</dt>
                  <dd>{order.paymentMethod}</dd>
                </div>
              </dl>
            </section>

            <section className="order-panel" aria-labelledby="totals-title">
              <h2 id="totals-title">جمع سفارش</h2>
              <dl className="order-total-list">
                <div>
                  <dt>جمع کالاها</dt>
                  <dd>{formatTomanAmount(order.subtotal)}</dd>
                </div>
                <div>
                  <dt>هزینه ارسال</dt>
                  <dd>
                    {order.shippingAmount
                      ? formatTomanAmount(order.shippingAmount)
                      : "رایگان"}
                  </dd>
                </div>
                <div className="is-discount">
                  <dt>تخفیف</dt>
                  <dd>
                    {order.discount
                      ? `− ${formatTomanAmount(order.discount)}`
                      : "بدون تخفیف"}
                  </dd>
                </div>
                <div className="is-total">
                  <dt>مبلغ نهایی</dt>
                  <dd>{formatTomanAmount(order.total)}</dd>
                </div>
              </dl>
            </section>
          </div>
        </div>

        <div className="order-success-actions">
          <Link
            className="order-primary-action"
            href={`/track-order?order=${encodeURIComponent(order.id)}`}
          >
            <Truck aria-hidden="true" size={18} strokeWidth={1.8} />
            پیگیری سفارش
          </Link>
          <Link className="order-secondary-action" href="/shop">
            <ShoppingBag aria-hidden="true" size={18} strokeWidth={1.8} />
            ادامه خرید
          </Link>
        </div>
        <p className="order-support-note">
          برای پرسش درباره این پیش‌نمایش با{" "}
          <a href="mailto:hello@gramiss.com">
            <Headphones
              aria-hidden="true"
              size={15}
              strokeWidth={1.8}
            />{" "}
            پشتیبانی Gramiss
          </a>{" "}
          در ارتباط باشید.
        </p>
      </div>
    </SystemPageChrome>
  );
}
