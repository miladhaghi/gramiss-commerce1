"use client";

/* eslint-disable @next/next/no-img-element */

import {
  Check,
  GitCompareArrows,
  Heart,
  ShoppingBag,
  X,
} from "lucide-react";
import Link from "next/link";
import {
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
  type RefObject,
  useEffect,
  useRef,
  useState,
} from "react";
import { getProductDetails, getProductRoute } from "../lib/catalog";
import type { ShopProduct } from "../shop/shop-data";

function getFocusable(container: HTMLElement | null) {
  if (!container) return [];
  return Array.from(
    container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  ).filter((item) => !item.hasAttribute("hidden"));
}

function useDialogBehavior(
  ref: RefObject<HTMLElement | null>,
  onClose: () => void,
) {
  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";
    const timer = window.setTimeout(() => getFocusable(ref.current)[0]?.focus());

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = getFocusable(ref.current);
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
      previouslyFocused?.focus();
    };
  }, [onClose, ref]);
}

export function CompareIcon({
  size = 18,
}: {
  size?: number;
}) {
  return (
    <GitCompareArrows
      aria-hidden="true"
      size={size}
      strokeWidth={1.75}
    />
  );
}

export function CommerceProductCard({
  product,
  wishlisted,
  compared,
  variant = "catalog",
  onToggleWishlist,
  onToggleCompare,
  onAddToCart,
  extraAction,
}: {
  product: ShopProduct;
  wishlisted: boolean;
  compared: boolean;
  variant?: "catalog" | "wishlist" | "compact";
  onToggleWishlist: (product: ShopProduct) => void;
  onToggleCompare: (product: ShopProduct) => void;
  onAddToCart: (product: ShopProduct) => void;
  extraAction?: ReactNode;
}) {
  const details = getProductDetails(product);

  return (
    <article
      className={`commerce-card commerce-card-${variant}`}
      data-product-id={product.id}
      dir="rtl"
    >
      <Link
        className="commerce-card-media"
        href={getProductRoute(product)}
        aria-label={`مشاهده ${product.name}`}
      >
        {product.badge ? (
          <span className="commerce-card-badge">{product.badge}</span>
        ) : null}
        <img src={product.image} alt={product.name} loading="lazy" />
      </Link>
      <div className="commerce-card-top-actions">
        <button
          className={wishlisted ? "is-active" : ""}
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
            size={19}
            strokeWidth={1.7}
            fill={wishlisted ? "currentColor" : "none"}
          />
        </button>
        <button
          className={compared ? "is-active" : ""}
          type="button"
          aria-label={
            compared
              ? `مشاهده ${product.name} در مقایسه`
              : `افزودن ${product.name} به مقایسه`
          }
          aria-pressed={compared}
          onClick={() => onToggleCompare(product)}
        >
          <CompareIcon size={18} />
        </button>
      </div>
      <div className="commerce-card-copy">
        <span>{product.category}</span>
        <Link href={getProductRoute(product)}>{product.name}</Link>
        <small dir="ltr">{product.english}</small>
        <strong>{product.price}</strong>
        <p className={product.inStock ? "is-in-stock" : "is-out-of-stock"}>
          {details.availability}
        </p>
      </div>
      <div className="commerce-card-actions">
        <button type="button" onClick={() => onAddToCart(product)}>
          <ShoppingBag aria-hidden="true" size={17} strokeWidth={1.8} />
          افزودن به سبد
        </button>
        {extraAction}
      </div>
    </article>
  );
}

export function QuickAddModal({
  product,
  onClose,
  onConfirm,
}: {
  product: ShopProduct;
  onClose: () => void;
  onConfirm: (selection: { color: string; size: string }) => void;
}) {
  const ref = useRef<HTMLElement>(null);
  const details = getProductDetails(product);
  const [color, setColor] = useState(
    details.colors.length === 1 ? details.colors[0] : "",
  );
  const [size, setSize] = useState(
    product.sizes.length === 1 ? product.sizes[0] : "",
  );
  const [error, setError] = useState("");
  useDialogBehavior(ref, onClose);

  function submit() {
    if (!color || !size) {
      setError("لطفاً رنگ و اندازه را کامل انتخاب کنید.");
      return;
    }
    onConfirm({ color, size });
  }

  return (
    <div
      className="feature-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="quick-add-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="quick-add-title"
        ref={ref}
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="feature-dialog-heading">
          <div>
            <span>QUICK SELECTION</span>
            <h2 id="quick-add-title">انتخاب مشخصات محصول</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="بستن">
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <div className="quick-add-product">
          <div>
            <img src={product.image} alt="" />
          </div>
          <span>
            <strong>{product.name}</strong>
            <small dir="ltr">{product.english}</small>
            <b>{product.price}</b>
          </span>
        </div>
        <fieldset className="quick-add-options">
          <legend>رنگ</legend>
          <div>
            {details.colors.map((item) => (
              <button
                className={color === item ? "is-selected" : ""}
                type="button"
                aria-pressed={color === item}
                key={item}
                onClick={() => {
                  setColor(item);
                  setError("");
                }}
              >
                {color === item ? <Check aria-hidden="true" size={15} /> : null}
                {item}
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset className="quick-add-options">
          <legend>اندازه</legend>
          <div>
            {product.sizes.map((item) => (
              <button
                className={size === item ? "is-selected" : ""}
                type="button"
                aria-pressed={size === item}
                key={item}
                onClick={() => {
                  setSize(item);
                  setError("");
                }}
              >
                {item}
              </button>
            ))}
          </div>
        </fieldset>
        <p className="feature-form-error" role="alert">
          {error}
        </p>
        <button
          className="feature-primary-button"
          type="button"
          onClick={submit}
        >
          افزودن به سبد خرید
        </button>
      </section>
    </div>
  );
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  onConfirm,
  onClose,
}: {
  title: string;
  description: string;
  confirmLabel: string;
  onConfirm: () => void;
  onClose: () => void;
}) {
  const ref = useRef<HTMLElement>(null);
  useDialogBehavior(ref, onClose);

  function onDialogKeyDown(event: ReactKeyboardEvent<HTMLElement>) {
    if (event.key !== "Enter" || event.target !== event.currentTarget) return;
    onConfirm();
  }

  return (
    <div
      className="feature-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        ref={ref}
        tabIndex={-1}
        onKeyDown={onDialogKeyDown}
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="feature-dialog-heading">
          <h2 id="confirm-title">{title}</h2>
          <button type="button" onClick={onClose} aria-label="بستن">
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <p>{description}</p>
        <div className="confirm-dialog-actions">
          <button type="button" onClick={onClose}>
            انصراف
          </button>
          <button
            className="is-danger"
            type="button"
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
