"use client";

/* eslint-disable @next/next/no-img-element */

import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  ArrowLeft,
  CheckCircle2,
  LockKeyhole,
  RotateCcw,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import {
  Drawer,
  Footer,
  Header,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import {
  formatToman,
  getCartItemHref,
  type ShippingMethod,
  useGramissStore,
} from "../hooks/use-gramiss-store";
import {
  CHECKOUT_DRAFT_STORAGE_KEY,
  mergeCheckoutIntoDemoProfile,
  readDemoProfile,
} from "../hooks/use-demo-auth";
import { shopProducts } from "../shop/shop-data";

type CheckoutValues = {
  fullName: string;
  mobile: string;
  province: string;
  city: string;
  address: string;
  postalCode: string;
  building: string;
  notes: string;
};

type RequiredField =
  | "fullName"
  | "mobile"
  | "province"
  | "city"
  | "address"
  | "postalCode";

type PaymentMethod = "online" | "cod";

const emptyValues: CheckoutValues = {
  fullName: "",
  mobile: "",
  province: "",
  city: "",
  address: "",
  postalCode: "",
  building: "",
  notes: "",
};

const provinces = [
  "تهران",
  "البرز",
  "آذربایجان شرقی",
  "آذربایجان غربی",
  "اصفهان",
  "فارس",
  "خراسان رضوی",
  "گیلان",
  "مازندران",
  "سایر استان‌ها",
];

function normalizeDigits(value: string) {
  const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
  const arabicDigits = "٠١٢٣٤٥٦٧٨٩";
  return value
    .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)))
    .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)));
}

function isTehranCity(value: string) {
  const normalized = value.trim().toLocaleLowerCase("fa");
  return normalized === "تهران" || normalized === "tehran";
}

function getFieldError(field: RequiredField, value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return {
      fullName: "نام و نام خانوادگی را وارد کنید.",
      mobile: "شماره موبایل را وارد کنید.",
      province: "استان را انتخاب کنید.",
      city: "شهر را وارد کنید.",
      address: "آدرس کامل را وارد کنید.",
      postalCode: "کد پستی را وارد کنید.",
    }[field];
  }

  if (field === "mobile") {
    return /^09\d{9}$/.test(normalizeDigits(trimmed))
      ? ""
      : "شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم داشته باشد.";
  }
  if (field === "postalCode") {
    return /^\d{10}$/.test(normalizeDigits(trimmed))
      ? ""
      : "کد پستی باید دقیقاً ۱۰ رقم باشد.";
  }
  return "";
}

function CheckoutField({
  name,
  label,
  value,
  error,
  required = false,
  type = "text",
  inputMode,
  autoComplete,
  dir,
  onChange,
  onBlur,
}: {
  name: keyof CheckoutValues;
  label: string;
  value: string;
  error?: string;
  required?: boolean;
  type?: string;
  inputMode?: "text" | "numeric" | "tel";
  autoComplete?: string;
  dir?: "rtl" | "ltr";
  onChange: (value: string) => void;
  onBlur?: () => void;
}) {
  const inputId = `checkout-${name}`;
  const errorId = `${inputId}-error`;

  return (
    <div className={`checkout-field ${error ? "has-error" : ""}`}>
      <label htmlFor={inputId}>
        {label}
        {required ? <span aria-hidden="true">*</span> : null}
      </label>
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        required={required}
        inputMode={inputMode}
        autoComplete={autoComplete}
        dir={dir}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        data-checkout-field
        onChange={(event) => onChange(event.target.value)}
        onBlur={onBlur}
      />
      <p id={errorId} role={error ? "alert" : undefined}>
        {error || "\u00a0"}
      </p>
    </div>
  );
}

export default function CheckoutPage() {
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [toast, setToast] = useState("");
  const [values, setValues] = useState<CheckoutValues>(emptyValues);
  const [errors, setErrors] = useState<
    Partial<Record<RequiredField, string>>
  >({});
  const [paymentMethod, setPaymentMethod] =
    useState<PaymentMethod>("online");
  const [draftHydrated, setDraftHydrated] = useState(false);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const modalReturnRef = useRef<HTMLButtonElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);
  const {
    wishlisted,
    cartItems,
    cartCount,
    subtotal,
    shippingMethod,
    shippingCost,
    discount,
    finalTotal,
    addToCart,
    setShippingMethod,
  } = useGramissStore();

  const codAvailable = isTehranCity(values.city);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const profile = readDemoProfile();
        const savedAddress =
          profile.addresses.find((address) => address.isDefault) ??
          profile.addresses[0];
        const profileValues: CheckoutValues = {
          ...emptyValues,
          fullName: profile.fullName,
          mobile: profile.mobile,
          province: savedAddress?.province ?? "",
          city: savedAddress?.city ?? "",
          address: savedAddress?.fullAddress ?? "",
          postalCode: savedAddress?.postalCode ?? "",
          building: savedAddress?.building ?? "",
        };
        const stored = window.sessionStorage.getItem(
          CHECKOUT_DRAFT_STORAGE_KEY,
        );
        if (stored) {
          const parsed = JSON.parse(stored) as Partial<{
            values: CheckoutValues;
            paymentMethod: PaymentMethod;
          }>;
          const draftValues =
            parsed.values && typeof parsed.values === "object"
              ? { ...emptyValues, ...parsed.values }
              : emptyValues;
          setValues(draftValues);
          if (
            parsed.paymentMethod === "online" ||
            (parsed.paymentMethod === "cod" &&
              isTehranCity(draftValues.city))
          ) {
            setPaymentMethod(parsed.paymentMethod);
          }
        } else {
          setValues(profileValues);
        }
      } catch {
        // Continue with an empty, safe draft.
      } finally {
        setDraftHydrated(true);
      }
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!draftHydrated) return;
    window.sessionStorage.setItem(
      CHECKOUT_DRAFT_STORAGE_KEY,
      JSON.stringify({ values, paymentMethod }),
    );
  }, [draftHydrated, paymentMethod, values]);

  useEffect(() => {
    if (!demoModalOpen) return;
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      modalReturnRef.current?.focus();
    }, 0);

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        setDemoModalOpen(false);
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(
        document.querySelectorAll<HTMLElement>(
          '.checkout-demo-modal button:not([disabled]), .checkout-demo-modal a[href], .checkout-demo-modal [tabindex]:not([tabindex="-1"])',
        ),
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
  }, [demoModalOpen]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  function setField(name: keyof CheckoutValues, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
    if (
      name === "city" &&
      paymentMethod === "cod" &&
      !isTehranCity(value)
    ) {
      setPaymentMethod("online");
    }
    if (name in errors) {
      setErrors((current) => ({ ...current, [name]: "" }));
    }
  }

  function validateSingle(field: RequiredField) {
    const error = getFieldError(field, values[field]);
    setErrors((current) => ({ ...current, [field]: error }));
  }

  function validateForm() {
    const fields: RequiredField[] = [
      "fullName",
      "mobile",
      "province",
      "city",
      "address",
      "postalCode",
    ];
    const nextErrors = Object.fromEntries(
      fields
        .map((field) => [field, getFieldError(field, values[field])] as const)
        .filter(([, error]) => Boolean(error)),
    ) as Partial<Record<RequiredField, string>>;
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function submitCheckout(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!cartItems.length) {
      announce("سبد خرید خالی است.");
      return;
    }
    if (!validateForm()) {
      window.requestAnimationFrame(() => {
        const firstInvalid =
          document.querySelector<HTMLElement>("[data-checkout-field][aria-invalid='true']");
        firstInvalid?.scrollIntoView({ behavior: "smooth", block: "center" });
        firstInvalid?.focus({ preventScroll: true });
      });
      return;
    }
    mergeCheckoutIntoDemoProfile(values);
    setDemoModalOpen(true);
  }

  function renderShippingMethod(
    method: ShippingMethod,
    title: string,
    description: string,
    price: string,
  ) {
    const selected = shippingMethod === method;
    return (
      <label className={`checkout-choice ${selected ? "is-selected" : ""}`}>
        <input
          type="radio"
          name="shipping-method"
          value={method}
          checked={selected}
          onChange={() => setShippingMethod(method)}
        />
        <span className="checkout-radio-mark" aria-hidden="true" />
        <strong>{title}</strong>
        <small>{description}</small>
        <b>{price}</b>
      </label>
    );
  }

  return (
    <main
      className="page-shell commerce-page checkout-page"
      id="top"
      data-node-id="33:63"
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

      <section className="checkout-heading" aria-labelledby="checkout-title">
        <h1 id="checkout-title">تکمیل سفارش</h1>
        <p>اطلاعات را بررسی و پرداخت را نهایی کن.</p>
      </section>

      <ol className="checkout-progress" aria-label="مراحل تکمیل سفارش">
        <li className="is-active" aria-current="step">
          <span>۱</span>
          اطلاعات ارسال
        </li>
        <li>
          <span>۲</span>
          روش پرداخت
        </li>
        <li>
          <span>۳</span>
          تأیید نهایی
        </li>
      </ol>

      {!cartItems.length ? (
        <div className="checkout-empty-notice" role="status">
          <p>سبد خرید خالی است؛ برای تکمیل سفارش ابتدا محصولی انتخاب کن.</p>
          <Link href="/shop">بازگشت به فروشگاه</Link>
        </div>
      ) : null}

      <div className="checkout-layout">
        <form
          className="checkout-form-card"
          id="checkout-form"
          onSubmit={submitCheckout}
          noValidate
          dir="rtl"
        >
          <section
            className="checkout-form-section checkout-contact"
            aria-labelledby="contact-title"
          >
            <h2 id="contact-title">اطلاعات تماس</h2>
            <div className="checkout-field-grid">
              <CheckoutField
                name="fullName"
                label="نام و نام خانوادگی"
                value={values.fullName}
                error={errors.fullName}
                required
                autoComplete="name"
                onChange={(value) => setField("fullName", value)}
                onBlur={() => validateSingle("fullName")}
              />
              <CheckoutField
                name="mobile"
                label="شماره موبایل"
                value={values.mobile}
                error={errors.mobile}
                required
                type="tel"
                inputMode="tel"
                autoComplete="tel"
                dir="ltr"
                onChange={(value) => setField("mobile", value)}
                onBlur={() => validateSingle("mobile")}
              />
              <div
                className={`checkout-field ${errors.province ? "has-error" : ""}`}
              >
                <label htmlFor="checkout-province">
                  استان
                  <span aria-hidden="true">*</span>
                </label>
                <select
                  id="checkout-province"
                  name="province"
                  required
                  value={values.province}
                  aria-invalid={Boolean(errors.province)}
                  aria-describedby={
                    errors.province ? "checkout-province-error" : undefined
                  }
                  data-checkout-field
                  onChange={(event) =>
                    setField("province", event.target.value)
                  }
                  onBlur={() => validateSingle("province")}
                >
                  <option value="">انتخاب استان</option>
                  {provinces.map((province) => (
                    <option value={province} key={province}>
                      {province}
                    </option>
                  ))}
                </select>
                <p
                  id="checkout-province-error"
                  role={errors.province ? "alert" : undefined}
                >
                  {errors.province || "\u00a0"}
                </p>
              </div>
              <CheckoutField
                name="city"
                label="شهر"
                value={values.city}
                error={errors.city}
                required
                autoComplete="address-level2"
                onChange={(value) => setField("city", value)}
                onBlur={() => validateSingle("city")}
              />
              <div className="checkout-field-wide">
                <CheckoutField
                  name="address"
                  label="آدرس کامل"
                  value={values.address}
                  error={errors.address}
                  required
                  autoComplete="street-address"
                  onChange={(value) => setField("address", value)}
                  onBlur={() => validateSingle("address")}
                />
              </div>
              <CheckoutField
                name="postalCode"
                label="کد پستی"
                value={values.postalCode}
                error={errors.postalCode}
                required
                inputMode="numeric"
                autoComplete="postal-code"
                dir="ltr"
                onChange={(value) => setField("postalCode", value)}
                onBlur={() => validateSingle("postalCode")}
              />
              <CheckoutField
                name="building"
                label="پلاک / واحد"
                value={values.building}
                inputMode="text"
                autoComplete="address-line2"
                onChange={(value) => setField("building", value)}
              />
            </div>
          </section>

          <section
            className="checkout-form-section checkout-shipping"
            aria-labelledby="shipping-title"
          >
            <h2 id="shipping-title">روش ارسال</h2>
            <fieldset>
              <legend className="sr-only">انتخاب روش ارسال</legend>
              {renderShippingMethod(
                "standard",
                "ارسال استاندارد",
                "۲ تا ۴ روز کاری",
                "رایگان",
              )}
              {renderShippingMethod(
                "express",
                "ارسال سریع",
                "تحویل روز بعد",
                "۱۲۰٬۰۰۰ تومان",
              )}
            </fieldset>
          </section>

          <section
            className="checkout-form-section checkout-payment"
            aria-labelledby="payment-title"
          >
            <h2 id="payment-title">روش پرداخت</h2>
            <fieldset>
              <legend className="sr-only">انتخاب روش پرداخت</legend>
              <label
                className={`checkout-choice ${
                  paymentMethod === "online" ? "is-selected" : ""
                }`}
              >
                <input
                  type="radio"
                  name="payment-method"
                  value="online"
                  checked={paymentMethod === "online"}
                  onChange={() => setPaymentMethod("online")}
                />
                <span className="checkout-radio-mark" aria-hidden="true" />
                <strong>درگاه پرداخت آنلاین</strong>
                <small>تمام کارت‌های بانکی</small>
              </label>
              <label
                className={`checkout-choice ${
                  paymentMethod === "cod" ? "is-selected" : ""
                } ${codAvailable ? "" : "is-disabled"}`}
                aria-disabled={!codAvailable}
              >
                <input
                  type="radio"
                  name="payment-method"
                  value="cod"
                  checked={paymentMethod === "cod"}
                  disabled={!codAvailable}
                  onChange={() => setPaymentMethod("cod")}
                />
                <span className="checkout-radio-mark" aria-hidden="true" />
                <strong>پرداخت در محل</strong>
                <small>فقط تهران</small>
              </label>
              {!codAvailable ? (
                <p className="checkout-choice-hint">
                  پرداخت در محل پس از انتخاب شهر تهران فعال می‌شود.
                </p>
              ) : null}
            </fieldset>
          </section>

          <section
            className="checkout-form-section checkout-notes"
            aria-labelledby="notes-title"
          >
            <label id="notes-title" htmlFor="checkout-notes">
              یادداشت سفارش
            </label>
            <textarea
              id="checkout-notes"
              name="notes"
              value={values.notes}
              rows={5}
              placeholder="اگر نکته‌ای برای آماده‌سازی یا ارسال داری، اینجا بنویس."
              onChange={(event) => setField("notes", event.target.value)}
            />
          </section>
        </form>

        <aside className="checkout-sidebar" dir="rtl">
          <section
            className="checkout-order-summary"
            aria-labelledby="order-summary-title"
          >
            <h2 id="order-summary-title">سفارش شما</h2>
            {cartItems.length ? (
              <div className="checkout-order-items">
                {cartItems.map((item) => (
                  <article key={item.lineId}>
                    <Link href={getCartItemHref(item)}>
                      <img
                        src={item.image}
                        width="110"
                        height="95"
                        alt={item.name}
                      />
                    </Link>
                    <div>
                      <Link href={getCartItemHref(item)}>{item.name}</Link>
                      <span>
                        {item.quantity.toLocaleString("fa-IR")} × {item.price}
                      </span>
                      {item.color || item.size ? (
                        <small>
                          {[item.color, item.size].filter(Boolean).join(" · ")}
                        </small>
                      ) : null}
                    </div>
                    <strong>
                      {formatToman(item.unitPrice * item.quantity)}
                    </strong>
                  </article>
                ))}
              </div>
            ) : (
              <p className="checkout-summary-empty">سبد خرید خالی است.</p>
            )}

            <dl className="checkout-totals">
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
              <div className="checkout-final-total">
                <dt>مبلغ نهایی</dt>
                <dd>{formatToman(finalTotal)}</dd>
              </div>
            </dl>

            <button
              className="checkout-submit"
              ref={submitButtonRef}
              type="submit"
              form="checkout-form"
              disabled={!cartItems.length}
            >
              پرداخت و ثبت سفارش
              <ArrowLeft aria-hidden="true" size={19} strokeWidth={1.8} />
            </button>
            <p className="checkout-terms">
              با ثبت سفارش، قوانین خرید را می‌پذیرم.
            </p>
          </section>

          <section className="checkout-secure" aria-labelledby="secure-title">
            <ShieldCheck aria-hidden="true" size={32} strokeWidth={1.6} />
            <h2 id="secure-title">خرید مطمئن</h2>
            <ul>
              <li>
                <LockKeyhole
                  aria-hidden="true"
                  size={18}
                  strokeWidth={1.7}
                />
                پرداخت امن
              </li>
              <li>
                <RotateCcw
                  aria-hidden="true"
                  size={18}
                  strokeWidth={1.7}
                />
                بازگشت ۷ روزه
              </li>
              <li>
                <CheckCircle2
                  aria-hidden="true"
                  size={18}
                  strokeWidth={1.7}
                />
                پشتیبانی واقعی
              </li>
            </ul>
          </section>
        </aside>
      </div>

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

      {demoModalOpen ? (
        <div
          className="checkout-modal-overlay"
          role="presentation"
          onMouseDown={() => {
            setDemoModalOpen(false);
            window.setTimeout(() => submitButtonRef.current?.focus(), 0);
          }}
        >
          <section
            className="checkout-demo-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="demo-modal-title"
            onMouseDown={(event) => event.stopPropagation()}
            dir="rtl"
          >
            <span aria-hidden="true">
              <CheckCircle2 size={32} strokeWidth={1.6} />
            </span>
            <h2 id="demo-modal-title">نسخه نمایشی Gramiss</h2>
            <p>
              نسخه نمایشی سایت آماده است. پرداخت و ثبت سفارش واقعی پس از اتصال
              Gramiss به WordPress و WooCommerce فعال می‌شود.
            </p>
            <div>
              <button
                ref={modalReturnRef}
                type="button"
                onClick={() => {
                  setDemoModalOpen(false);
                  window.setTimeout(
                    () => submitButtonRef.current?.focus(),
                    0,
                  );
                }}
              >
                بازگشت به سفارش
              </button>
              <Link href="/shop">ادامه خرید</Link>
            </div>
          </section>
        </div>
      ) : null}

      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}
