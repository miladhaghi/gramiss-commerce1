export type DemoOrderStatusKey = "shipping" | "delivered";

export type DemoOrderProduct = {
  id: string;
  name: string;
  english: string;
  image: string;
  quantity: number;
  unitPrice: number;
};

export type DemoOrderTimelineStep = {
  label: string;
  state: "complete" | "current" | "pending";
  detail: string;
};

export type DemoOrder = {
  id: string;
  date: string;
  status: string;
  statusKey: DemoOrderStatusKey;
  total: number;
  active: boolean;
  trackingInformation: string;
  products: DemoOrderProduct[];
  recipient: string;
  address: string;
  shippingMethod: string;
  shippingEta: string;
  shippingAmount: number;
  paymentMethod: string;
  subtotal: number;
  discount: number;
  timeline: DemoOrderTimelineStep[];
};

const deliveredTimeline: DemoOrderTimelineStep[] = [
  { label: "سفارش ثبت شد", state: "complete", detail: "انجام شد" },
  { label: "پرداخت تأیید شد", state: "complete", detail: "انجام شد" },
  { label: "آماده‌سازی", state: "complete", detail: "انجام شد" },
  { label: "تحویل به پست", state: "complete", detail: "انجام شد" },
  { label: "تحویل شده", state: "complete", detail: "سفارش تحویل شده است" },
];

export const demoOrders: readonly DemoOrder[] = [
  {
    id: "GR-2481",
    date: "۲۹ تیر ۱۴۰۵",
    status: "در حال ارسال",
    statusKey: "shipping",
    total: 3_480_000,
    active: true,
    trackingInformation:
      "بسته به شرکت پست تحویل شده و در مسیر آدرس گیرنده قرار دارد.",
    products: [
      {
        id: "sky-blue-cap",
        name: "کلاه آبی آسمانی",
        english: "SKY BLUE DAILY CAP",
        image: "/assets/product-cap.png",
        quantity: 1,
        unitPrice: 1_290_000,
      },
      {
        id: "crossbody-bag",
        name: "کیف کراس‌بادی مشکی",
        english: "CROSSBODY BAG",
        image: "/assets/product-bag.png",
        quantity: 1,
        unitPrice: 2_490_000,
      },
    ],
    recipient: "میلاد حقی",
    address: "تهران، نازی‌آباد، خیابان مدائن",
    shippingMethod: "ارسال استاندارد",
    shippingEta: "۲ تا ۴ روز کاری",
    shippingAmount: 0,
    paymentMethod: "درگاه پرداخت آنلاین — نمایشی",
    subtotal: 3_780_000,
    discount: 300_000,
    timeline: [
      { label: "سفارش ثبت شد", state: "complete", detail: "انجام شد" },
      { label: "پرداخت تأیید شد", state: "complete", detail: "انجام شد" },
      { label: "آماده‌سازی", state: "complete", detail: "انجام شد" },
      { label: "تحویل به پست", state: "complete", detail: "انجام شد" },
      { label: "در حال ارسال", state: "current", detail: "در حال انجام" },
    ],
  },
  {
    id: "GR-2412",
    date: "۱۶ تیر ۱۴۰۵",
    status: "تحویل شده",
    statusKey: "delivered",
    total: 1_920_000,
    active: false,
    trackingInformation: "سفارش با موفقیت به گیرنده تحویل شده است.",
    products: [
      {
        id: "essential-tee",
        name: "تیشرت مینیمال سفید",
        english: "ESSENTIAL WHITE TEE",
        image: "/assets/product-shirt.png",
        quantity: 1,
        unitPrice: 1_920_000,
      },
    ],
    recipient: "میلاد حقی",
    address: "تهران، نازی‌آباد",
    shippingMethod: "ارسال استاندارد",
    shippingEta: "تحویل شده",
    shippingAmount: 0,
    paymentMethod: "درگاه پرداخت آنلاین — نمایشی",
    subtotal: 1_920_000,
    discount: 0,
    timeline: deliveredTimeline,
  },
  {
    id: "GR-2298",
    date: "۲۵ خرداد ۱۴۰۵",
    status: "تحویل شده",
    statusKey: "delivered",
    total: 2_640_000,
    active: false,
    trackingInformation: "سفارش با موفقیت به گیرنده تحویل شده است.",
    products: [
      {
        id: "minimal-runner",
        name: "کتونی روزمره مینیمال",
        english: "MINIMAL DAILY RUNNER",
        image: "/assets/product-shoe.png",
        quantity: 1,
        unitPrice: 2_640_000,
      },
    ],
    recipient: "میلاد حقی",
    address: "تهران، نازی‌آباد",
    shippingMethod: "ارسال سریع",
    shippingEta: "تحویل شده",
    shippingAmount: 120_000,
    paymentMethod: "پرداخت در محل — نمایشی",
    subtotal: 2_520_000,
    discount: 0,
    timeline: deliveredTimeline,
  },
] as const;

const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

export function normalizeOrderNumber(value: string) {
  const normalizedDigits = value
    .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)))
    .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)));

  const compact = normalizedDigits
    .trim()
    .replace(/^#/, "")
    .replace(/[‐‑‒–—−]/g, "-")
    .replace(/\s+/g, "")
    .toUpperCase();

  if (/^\d+$/.test(compact)) return `GR-${compact}`;
  if (/^GR\d+$/.test(compact)) return compact.replace(/^GR/, "GR-");
  return compact;
}

export function findDemoOrder(value: string) {
  const normalized = normalizeOrderNumber(value);
  return demoOrders.find((order) => order.id === normalized);
}

export function formatTomanAmount(value: number) {
  return `${value.toLocaleString("fa-IR")} تومان`;
}
