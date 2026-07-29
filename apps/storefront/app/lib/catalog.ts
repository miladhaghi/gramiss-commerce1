import type { ShopProduct } from "../shop/shop-data";

const categoryDetails: Record<
  ShopProduct["categoryKey"],
  { use: string; tags: string[] }
> = {
  sneakers: {
    use: "پیاده‌روی، رفت‌وآمد شهری و استایل روزمره",
    tags: ["کفش", "کتانی", "شهری", "روزمره"],
  },
  caps: {
    use: "استایل روزمره، مینیمال و محافظت در برابر آفتاب",
    tags: ["کلاه", "کپ", "اکسسوری", "مردانه"],
  },
  bags: {
    use: "رفت‌وآمد روزانه، دانشگاه و سفرهای کوتاه",
    tags: ["کیف", "دوشی", "کراس بادی", "شهری"],
  },
  socks: {
    use: "استفاده روزمره و فعالیت سبک",
    tags: ["جوراب", "نخی", "راحت", "روزمره"],
  },
  "t-shirts": {
    use: "استایل روزمره، لایه‌سازی و استفاده چهارفصل",
    tags: ["تیشرت", "لباس", "پنبه‌ای", "مینیمال"],
  },
};

const materialDurability: Record<ShopProduct["material"], string> = {
  پنبه: "دوام خوب با شست‌وشوی ملایم",
  "پلی‌استر": "مقاومت بالا در استفاده روزمره",
  چرم: "دوام بسیار بالا با نگهداری صحیح",
  "کتان ترکیبی سبک": "دوام خوب با شست‌وشوی ملایم و آب سرد",
};

export type ProductDetails = {
  slug: string;
  href: string;
  description: string;
  colors: string[];
  tags: string[];
  durability: string;
  recommendedUse: string;
  shipping: string;
  rating: number;
  availability: string;
};

export function getProductDetails(product: ShopProduct): ProductDetails {
  const category = categoryDetails[product.categoryKey];
  return {
    slug: product.id,
    href: `/product/${product.id}`,
    description: `${product.name} با متریال ${product.material} برای ${category.use} طراحی شده است.`,
    colors: product.colors ? [...product.colors] : [product.color],
    tags: [
      ...category.tags,
      product.badge,
      product.category,
      product.english,
      product.color,
      product.material,
    ].filter(Boolean),
    durability: materialDurability[product.material],
    recommendedUse: category.use,
    shipping: product.inStock
      ? "ارسال استاندارد رایگان؛ ۲ تا ۴ روز کاری"
      : "ناموجود؛ اطلاع‌رسانی پس از شارژ",
    rating: Math.min(4.9, 4.2 + product.newestRank * 0.06),
    availability: product.inStock ? "موجود و آماده ارسال" : "ناموجود",
  };
}

export function getProductRoute(
  product: Pick<ShopProduct, "id"> | { id: string },
) {
  return `/product/${product.id}`;
}

export function getProductSearchFields(product: ShopProduct) {
  const details = getProductDetails(product);
  return [
    product.name,
    product.english,
    product.category,
    product.categoryKey,
    details.description,
    product.material,
    product.color,
    ...details.colors,
    ...details.tags,
  ];
}
