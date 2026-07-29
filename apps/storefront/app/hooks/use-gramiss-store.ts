"use client";

import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { shopProducts } from "../shop/shop-data";

const WISHLIST_KEY = "gramiss:wishlist";
export const COMPARE_STORAGE_KEY = "gramiss:compare";
export const CART_STORAGE_KEY = "gramiss:cart-count";

export type ShippingMethod = "standard" | "express";
export type CartProduct = {
  id: string;
  name: string;
  english: string;
  category: string;
  price: string;
  image: string;
  productHref?: string;
  unitPrice?: number;
  priceValue?: number;
  color?: string;
  colors?: readonly string[];
  sizes?: readonly string[];
};

export type CartSelection = {
  color?: string;
  size?: string;
};
export type CartItem = Omit<CartProduct, "color" | "sizes"> & {
  lineId: string;
  quantity: number;
  color: string;
  size: string;
  unitPrice: number;
};

type StoredCart = {
  version: 3;
  items: CartItem[];
  shippingMethod: ShippingMethod;
  discountCode: string;
};

const defaultCartItems: CartItem[] = [
  {
    id: "sky-blue-cap",
    lineId: "sky-blue-cap::آبی آسمانی::Free Size",
    name: "کلاه آبی آسمانی",
    english: "SKY BLUE DAILY CAP",
    category: "کلاه",
    price: "۱٬۲۹۰٬۰۰۰ تومان",
    unitPrice: 1_290_000,
    image: "/assets/product-cap.png",
    productHref: "/product/sky-blue-cap",
    color: "آبی آسمانی",
    size: "Free Size",
    quantity: 1,
  },
  {
    id: "crossbody-bag",
    lineId: "crossbody-bag::خاکی::M",
    name: "کیف دوشی روزمره",
    english: "CROSSBODY BAG",
    category: "کیف",
    price: "۲٬۶۹۰٬۰۰۰ تومان",
    unitPrice: 2_690_000,
    image: "/assets/product-bag.png",
    productHref: "/product/crossbody-bag",
    color: "خاکی",
    size: "M",
    quantity: 1,
  },
];

const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

export function priceToNumber(value: string | number | undefined) {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }
  if (!value) return 0;

  const normalized = value
    .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)))
    .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)))
    .replace(/[^\d]/g, "");

  return Number.parseInt(normalized || "0", 10);
}

export function formatToman(value: number) {
  return `${Math.max(0, Math.round(value)).toLocaleString("fa-IR")} تومان`;
}

export function getCartItemHref(item: Pick<CartItem, "id" | "productHref">) {
  if (item.productHref) return item.productHref;
  return `/product/${item.id}`;
}

function getDefaultSelection(
  product: CartProduct,
  selection: CartSelection = {},
) {
  const inferredColor =
    selection.color ??
    product.colors?.[0] ??
    product.color ??
    (product.id === "sky-blue-cap" ? "آبی آسمانی" : "");
  const inferredSize =
    selection.size ??
    product.sizes?.[0] ??
    (product.id === "sky-blue-cap" ? "Free Size" : "");

  return { color: inferredColor, size: inferredSize };
}

function createCartItem(
  product: CartProduct,
  selection: CartSelection = {},
): CartItem {
  const { color, size } = getDefaultSelection(product, selection);
  const unitPrice =
    product.unitPrice ?? product.priceValue ?? priceToNumber(product.price);

  return {
    id: product.id,
    lineId: `${product.id}::${color}::${size}`,
    name: product.name,
    english: product.english,
    category: product.category,
    price: formatToman(unitPrice),
    image: product.image,
    productHref:
      product.productHref ??
      `/product/${product.id}`,
    unitPrice,
    color,
    size,
    quantity: 1,
  };
}

function normalizeCartItem(value: unknown): CartItem | null {
  if (!value || typeof value !== "object") return null;
  const item = value as Partial<CartItem>;
  if (
    typeof item.id !== "string" ||
    typeof item.name !== "string" ||
    typeof item.english !== "string" ||
    typeof item.category !== "string" ||
    typeof item.price !== "string" ||
    typeof item.image !== "string" ||
    typeof item.quantity !== "number" ||
    !Number.isFinite(item.quantity) ||
    item.quantity < 1
  ) {
    return null;
  }

  const catalogProduct = shopProducts.find((product) => product.id === item.id);
  const storedColor = typeof item.color === "string" ? item.color : "";
  const supportedColors = catalogProduct?.colors?.length
    ? catalogProduct.colors
    : catalogProduct
      ? [catalogProduct.color]
      : [];
  const color =
    catalogProduct && !supportedColors.includes(storedColor)
      ? supportedColors[0] ?? ""
      : storedColor;
  const storedSize = typeof item.size === "string" ? item.size : "";
  const size =
    catalogProduct &&
    catalogProduct.sizes.length > 0 &&
    !catalogProduct.sizes.includes(storedSize)
      ? catalogProduct.sizes[0]
      : storedSize;
  const unitPrice = catalogProduct
    ? catalogProduct.priceValue
    : typeof item.unitPrice === "number" && Number.isFinite(item.unitPrice)
      ? item.unitPrice
      : priceToNumber(item.price);

  return {
    id: item.id,
    lineId: `${item.id}::${color}::${size}`,
    name: catalogProduct?.name ?? item.name,
    english: catalogProduct?.english ?? item.english,
    category: catalogProduct?.category ?? item.category,
    price: formatToman(unitPrice),
    image: catalogProduct?.image ?? item.image,
    productHref: catalogProduct
      ? `/product/${catalogProduct.id}`
      : typeof item.productHref === "string"
        ? item.productHref
        : `/product/${item.id}`,
    unitPrice,
    color,
    size,
    quantity: Math.max(1, Math.floor(item.quantity)),
  };
}

function mergeItems(items: CartItem[]) {
  const merged = new Map<string, CartItem>();
  for (const item of items) {
    const existing = merged.get(item.lineId);
    if (existing) {
      merged.set(item.lineId, {
        ...existing,
        quantity: existing.quantity + item.quantity,
      });
    } else {
      merged.set(item.lineId, item);
    }
  }
  return [...merged.values()];
}

function migrateLegacyCount(items: CartItem[], count: number) {
  if (count <= 0) return items;
  const legacyItems = defaultCartItems.map((item) => ({ ...item }));
  let remaining = Math.floor(count);
  const additions: CartItem[] = [];

  for (const item of legacyItems) {
    if (remaining <= 0) break;
    additions.push({ ...item, quantity: 1 });
    remaining -= 1;
  }

  if (remaining > 0 && additions.length) {
    additions[0] = {
      ...additions[0],
      quantity: additions[0].quantity + remaining,
    };
  }

  return mergeItems([...items, ...additions]);
}

function parseStoredCart(value: string): Omit<StoredCart, "version"> | null {
  try {
    const parsed = JSON.parse(value) as number | Partial<StoredCart> & {
      legacyCount?: number;
    };

    if (typeof parsed === "number") {
      return {
        items: migrateLegacyCount([], Math.max(0, parsed)),
        shippingMethod: "standard",
        discountCode: "",
      };
    }

    if (!parsed || typeof parsed !== "object") return null;
    const items = Array.isArray(parsed.items)
      ? parsed.items
          .map(normalizeCartItem)
          .filter((item): item is CartItem => Boolean(item))
      : [];
    const legacyCount =
      typeof parsed.legacyCount === "number" &&
      Number.isFinite(parsed.legacyCount)
        ? Math.max(0, parsed.legacyCount)
        : 0;

    return {
      items: migrateLegacyCount(items, legacyCount),
      shippingMethod:
        parsed.shippingMethod === "express" ? "express" : "standard",
      discountCode:
        typeof parsed.discountCode === "string" ? parsed.discountCode : "",
    };
  } catch {
    const legacyCount = Number.parseInt(value, 10);
    if (!Number.isFinite(legacyCount)) return null;
    return {
      items: migrateLegacyCount([], Math.max(0, legacyCount)),
      shippingMethod: "standard",
      discountCode: "",
    };
  }
}

export function useGramissStore(): {
  hydrated: boolean;
  wishlisted: Set<string>;
  setWishlisted: Dispatch<SetStateAction<Set<string>>>;
  compareIds: Set<string>;
  addToCompare: (productId: string) => "added" | "duplicate" | "limit";
  removeFromCompare: (productId: string) => void;
  clearCompare: () => void;
  cartItems: CartItem[];
  cartCount: number;
  subtotal: number;
  shippingMethod: ShippingMethod;
  shippingCost: number;
  discountCode: string;
  discount: number;
  finalTotal: number;
  addToCart: (product: CartProduct, selection?: CartSelection) => void;
  updateQuantity: (lineId: string, quantity: number) => void;
  removeFromCart: (lineId: string) => void;
  setShippingMethod: (method: ShippingMethod) => void;
  applyDiscount: (code: string) => boolean;
  clearDiscount: () => void;
} {
  const [wishlisted, setWishlisted] = useState<Set<string>>(
    () => new Set(["sky-blue-cap"]),
  );
  const [compareIds, setCompareIds] = useState<Set<string>>(() => new Set());
  const [cartItems, setCartItems] = useState<CartItem[]>(() =>
    defaultCartItems.map((item) => ({ ...item })),
  );
  const [shippingMethod, setShippingMethodState] =
    useState<ShippingMethod>("standard");
  const [discountCode, setDiscountCode] = useState("");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const loadTimer = window.setTimeout(() => {
      try {
        const storedWishlist = window.localStorage.getItem(WISHLIST_KEY);
        const storedCompare = window.localStorage.getItem(COMPARE_STORAGE_KEY);
        const storedCart = window.localStorage.getItem(CART_STORAGE_KEY);

        if (storedWishlist) {
          const parsed = JSON.parse(storedWishlist);
          if (Array.isArray(parsed)) {
            setWishlisted(
              new Set(parsed.filter((item) => typeof item === "string")),
            );
          }
        }

        if (storedCompare) {
          const parsed = JSON.parse(storedCompare);
          if (Array.isArray(parsed)) {
            setCompareIds(
              new Set(
                parsed
                  .filter((item) => typeof item === "string")
                  .slice(0, 4),
              ),
            );
          }
        }

        if (storedCart !== null) {
          const parsed = parseStoredCart(storedCart);
          if (parsed) {
            setCartItems(parsed.items);
            setShippingMethodState(parsed.shippingMethod);
            setDiscountCode(parsed.discountCode);
          }
        }
      } catch {
        // Keep the safe sample state if browser storage is unavailable.
      } finally {
        setHydrated(true);
      }
    }, 0);

    return () => window.clearTimeout(loadTimer);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    window.localStorage.setItem(WISHLIST_KEY, JSON.stringify([...wishlisted]));
  }, [hydrated, wishlisted]);

  useEffect(() => {
    if (!hydrated) return;
    window.localStorage.setItem(
      COMPARE_STORAGE_KEY,
      JSON.stringify([...compareIds]),
    );
  }, [compareIds, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    const storedCart: StoredCart = {
      version: 3,
      items: cartItems,
      shippingMethod,
      discountCode,
    };
    window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(storedCart));
  }, [cartItems, discountCode, hydrated, shippingMethod]);

  useEffect(() => {
    function onStorage(event: StorageEvent) {
      if (event.newValue === null) return;

      if (event.key === WISHLIST_KEY) {
        try {
          const parsed = JSON.parse(event.newValue);
          if (Array.isArray(parsed)) {
            setWishlisted(
              new Set(parsed.filter((item) => typeof item === "string")),
            );
          }
        } catch {
          // Ignore malformed state written outside Gramiss.
        }
        return;
      }

      if (event.key === COMPARE_STORAGE_KEY) {
        try {
          const parsed = JSON.parse(event.newValue);
          if (Array.isArray(parsed)) {
            setCompareIds(
              new Set(
                parsed
                  .filter((item) => typeof item === "string")
                  .slice(0, 4),
              ),
            );
          }
        } catch {
          // Ignore malformed state written outside Gramiss.
        }
        return;
      }

      if (event.key === CART_STORAGE_KEY) {
        const parsed = parseStoredCart(event.newValue);
        if (!parsed) return;
        setCartItems(parsed.items);
        setShippingMethodState(parsed.shippingMethod);
        setDiscountCode(parsed.discountCode);
      }
    }

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const subtotal = useMemo(
    () =>
      cartItems.reduce(
        (total, item) => total + item.unitPrice * item.quantity,
        0,
      ),
    [cartItems],
  );
  const cartCount = useMemo(
    () => cartItems.reduce((total, item) => total + item.quantity, 0),
    [cartItems],
  );
  const shippingCost = shippingMethod === "express" ? 120_000 : 0;
  const discount =
    discountCode === "GRAMISS10" ? Math.floor(subtotal * 0.1) : 0;
  const finalTotal = Math.max(0, subtotal + shippingCost - discount);

  const addToCart = useCallback(
    (product: CartProduct, selection: CartSelection = {}) => {
      const nextItem = createCartItem(product, selection);
      setCartItems((current) => {
        const existing = current.find(
          (item) => item.lineId === nextItem.lineId,
        );
        if (!existing) return [...current, nextItem];

        return current.map((item) =>
          item.lineId === nextItem.lineId
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      });
    },
    [],
  );

  const updateQuantity = useCallback((lineId: string, quantity: number) => {
    setCartItems((current) =>
      current.map((item) =>
        item.lineId === lineId
          ? { ...item, quantity: Math.max(1, Math.floor(quantity)) }
          : item,
      ),
    );
  }, []);

  const removeFromCart = useCallback((lineId: string) => {
    setCartItems((current) =>
      current.filter((item) => item.lineId !== lineId),
    );
  }, []);

  const setShippingMethod = useCallback((method: ShippingMethod) => {
    setShippingMethodState(method);
  }, []);

  const applyDiscount = useCallback((code: string) => {
    const normalized = code.trim().toUpperCase();
    if (normalized !== "GRAMISS10") return false;
    setDiscountCode(normalized);
    return true;
  }, []);

  const clearDiscount = useCallback(() => setDiscountCode(""), []);

  const addToCompare = useCallback(
    (productId: string): "added" | "duplicate" | "limit" => {
      if (compareIds.has(productId)) return "duplicate";
      if (compareIds.size >= 4) return "limit";
      const next = new Set(compareIds);
      next.add(productId);
      setCompareIds(next);
      return "added";
    },
    [compareIds],
  );

  const removeFromCompare = useCallback((productId: string) => {
    setCompareIds((current) => {
      if (!current.has(productId)) return current;
      const next = new Set(current);
      next.delete(productId);
      return next;
    });
  }, []);

  const clearCompare = useCallback(() => setCompareIds(new Set()), []);

  return {
    hydrated,
    wishlisted,
    setWishlisted,
    compareIds,
    addToCompare,
    removeFromCompare,
    clearCompare,
    cartItems,
    cartCount,
    subtotal,
    shippingMethod,
    shippingCost,
    discountCode,
    discount,
    finalTotal,
    addToCart,
    updateQuantity,
    removeFromCart,
    setShippingMethod,
    applyDiscount,
    clearDiscount,
  };
}
