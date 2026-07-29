"use client";

/* eslint-disable @next/next/no-img-element */

import {
  Check,
  Circle,
  CircleAlert,
  Headphones,
  PackageCheck,
} from "lucide-react";
import {
  type FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  GramissSkeleton,
  NetworkErrorPage,
  SystemPageChrome,
} from "../components/system-states";
import {
  isIranianMobile,
  normalizeAuthDigits,
} from "../hooks/use-demo-auth";
import { useNetworkAction } from "../hooks/use-network-action";
import {
  type DemoOrder,
  findDemoOrder,
  formatTomanAmount,
  normalizeOrderNumber,
} from "../lib/demo-orders";

type TrackingErrors = {
  order?: string;
  mobile?: string;
};

export default function TrackOrderPage() {
  const [orderNumber, setOrderNumber] = useState("");
  const [mobile, setMobile] = useState("");
  const [errors, setErrors] = useState<TrackingErrors>({});
  const [result, setResult] = useState<DemoOrder | null>(null);
  const [notFound, setNotFound] = useState(false);
  const orderRef = useRef<HTMLInputElement>(null);
  const mobileRef = useRef<HTMLInputElement>(null);
  const {
    status: networkStatus,
    attempt,
    retry,
    checkInitialLoad,
  } = useNetworkAction("order-tracking");

  const showOrder = useCallback((value: string) => {
    const found = findDemoOrder(value) ?? null;
    setResult(found);
    setNotFound(!found);
  }, []);

  useEffect(() => {
    function syncFromUrl() {
      const queryValue =
        new URLSearchParams(window.location.search).get("order") ?? "";
      if (!queryValue) {
        setResult(null);
        setNotFound(false);
        checkInitialLoad();
        return;
      }
      const normalized = normalizeOrderNumber(queryValue);
      setOrderNumber(normalized);
      setErrors((current) => ({ ...current, order: "" }));
      attempt(() => showOrder(normalized));
    }

    syncFromUrl();
    window.addEventListener("popstate", syncFromUrl);
    return () => window.removeEventListener("popstate", syncFromUrl);
  }, [attempt, checkInitialLoad, showOrder]);

  function validate() {
    const nextErrors: TrackingErrors = {};
    if (!orderNumber.trim()) {
      nextErrors.order = "وارد کردن شماره سفارش الزامی است.";
    }
    if (!mobile.trim()) {
      nextErrors.mobile = "وارد کردن شماره موبایل الزامی است.";
    } else if (!isIranianMobile(mobile)) {
      nextErrors.mobile = "شماره موبایل معتبر ایرانی وارد کنید.";
    }
    setErrors(nextErrors);

    const firstInvalid =
      nextErrors.order ? orderRef.current : nextErrors.mobile ? mobileRef.current : null;
    if (firstInvalid) {
      firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
      window.setTimeout(() => firstInvalid.focus(), 250);
      return false;
    }
    return true;
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (networkStatus === "loading" || !validate()) return;
    const normalized = normalizeOrderNumber(orderNumber);
    setOrderNumber(normalized);
    const url = new URL(window.location.href);
    url.searchParams.set("order", normalized);
    url.searchParams.delete("mobile");
    window.history.pushState({}, "", `${url.pathname}${url.search}`);
    attempt(() => showOrder(normalized));
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retry} />;
  }

  return (
    <SystemPageChrome>
      <div className="tracking-main" dir="rtl" data-node-id="49:29">
        <header className="tracking-heading">
          <span className="order-demo-label">SAMPLE ORDER TRACKING</span>
          <h1>پیگیری سفارش</h1>
          <p>
            شماره سفارش و موبایل را وارد کنید. سفارش‌های این صفحه فقط دادهٔ
            نمایشی هستند و به سفارش واقعی متصل نیستند.
          </p>
        </header>

        <form className="tracking-form" onSubmit={submit} noValidate>
          <div className={`tracking-field ${errors.order ? "has-error" : ""}`}>
            <label htmlFor="tracking-order">شماره سفارش</label>
            <input
              id="tracking-order"
              ref={orderRef}
              value={orderNumber}
              placeholder="مثال: GR-2481"
              dir="ltr"
              autoComplete="off"
              aria-invalid={Boolean(errors.order)}
              aria-describedby={
                errors.order ? "tracking-order-error" : undefined
              }
              onChange={(event) => {
                setOrderNumber(event.target.value);
                setErrors((current) => ({ ...current, order: "" }));
              }}
            />
            {errors.order ? (
              <p id="tracking-order-error" role="alert">
                {errors.order}
              </p>
            ) : null}
          </div>

          <div className={`tracking-field ${errors.mobile ? "has-error" : ""}`}>
            <label htmlFor="tracking-mobile">شماره موبایل</label>
            <input
              id="tracking-mobile"
              ref={mobileRef}
              value={mobile}
              placeholder="۰۹۱۲۱۲۳۴۵۶۷"
              dir="ltr"
              inputMode="tel"
              autoComplete="tel"
              aria-invalid={Boolean(errors.mobile)}
              aria-describedby={
                errors.mobile ? "tracking-mobile-error" : undefined
              }
              onChange={(event) => {
                setMobile(normalizeAuthDigits(event.target.value));
                setErrors((current) => ({ ...current, mobile: "" }));
              }}
            />
            {errors.mobile ? (
              <p id="tracking-mobile-error" role="alert">
                {errors.mobile}
              </p>
            ) : null}
          </div>

          <button
            className="tracking-submit"
            type="submit"
            disabled={networkStatus === "loading"}
          >
            {networkStatus === "loading" ? "در حال بررسی..." : "پیگیری سفارش"}
          </button>
        </form>

        <div className="tracking-result" aria-live="polite">
          {networkStatus === "loading" ? (
            <div className="tracking-result-skeleton">
              <GramissSkeleton rows={4} label="در حال دریافت وضعیت سفارش" />
            </div>
          ) : notFound ? (
            <section className="tracking-not-found" role="status">
              <CircleAlert aria-hidden="true" size={27} strokeWidth={1.7} />
              <div>
                <h2>سفارش نمونه‌ای با این شماره پیدا نشد</h2>
                <p>
                  شماره را دوباره بررسی کنید. سفارش‌های نمایشی پشتیبانی‌شده:
                  <bdi dir="ltr"> GR-2481، GR-2412، GR-2298</bdi>
                </p>
              </div>
            </section>
          ) : result ? (
            <TrackingResult order={result} />
          ) : null}
        </div>
      </div>
    </SystemPageChrome>
  );
}

function TrackingResult({ order }: { order: DemoOrder }) {
  return (
    <>
      <div className="tracking-result-heading">
        <strong>
          شماره سفارش <bdi dir="ltr">{order.id}</bdi>
        </strong>
        <span>سفارش نمونه — داده نمایشی</span>
      </div>

      <section
        className="tracking-current-status"
        aria-labelledby="tracking-status-title"
      >
        <span>وضعیت فعلی</span>
        <h2 id="tracking-status-title">{order.status}</h2>
        <p>{order.trackingInformation}</p>
      </section>

      <div className="tracking-layout">
        <section
          className="tracking-timeline"
          aria-label="مراحل وضعیت سفارش"
        >
          {order.timeline.map((step) => (
            <article
              className={`tracking-step is-${step.state}`}
              key={step.label}
            >
              <span className="tracking-step-indicator" aria-hidden="true">
                {step.state === "complete" ? (
                  <Check size={14} strokeWidth={2.4} />
                ) : step.state === "current" ? (
                  <PackageCheck size={14} strokeWidth={2} />
                ) : (
                  <Circle size={9} fill="currentColor" />
                )}
              </span>
              <div className="tracking-step-copy">
                <strong>{step.label}</strong>
                <span>{step.detail}</span>
              </div>
            </article>
          ))}
        </section>

        <aside className="tracking-side">
          <section className="order-panel" aria-labelledby="tracking-summary">
            <h2 id="tracking-summary">خلاصه سفارش</h2>
            <div className="tracking-mini-products">
              {order.products.map((product) => (
                <article className="tracking-mini-product" key={product.id}>
                  <img src={product.image} alt="" />
                  <span>
                    <strong>{product.name}</strong>
                    <small>تعداد {product.quantity.toLocaleString("fa-IR")}</small>
                  </span>
                  <b>{formatTomanAmount(product.unitPrice * product.quantity)}</b>
                </article>
              ))}
            </div>
          </section>

          <section className="order-panel" aria-labelledby="tracking-shipping">
            <h2 id="tracking-shipping">اطلاعات ارسال</h2>
            <dl className="order-detail-list">
              <div>
                <dt>گیرنده</dt>
                <dd>{order.recipient}</dd>
              </div>
              <div>
                <dt>آدرس</dt>
                <dd>{order.address}</dd>
              </div>
              <div>
                <dt>روش ارسال</dt>
                <dd>{order.shippingMethod}</dd>
              </div>
              <div>
                <dt>مبلغ سفارش</dt>
                <dd>{formatTomanAmount(order.total)}</dd>
              </div>
            </dl>
          </section>

          <section className="tracking-support">
            <h2>برای پیگیری بیشتر کمک می‌خواهید؟</h2>
            <p>پشتیبانی Gramiss پاسخ‌گوی پرسش‌های مربوط به این پیش‌نمایش است.</p>
            <a href="mailto:hello@gramiss.com">
              <Headphones aria-hidden="true" size={17} strokeWidth={1.8} />
              تماس با پشتیبانی
            </a>
          </section>
        </aside>
      </div>
    </>
  );
}
