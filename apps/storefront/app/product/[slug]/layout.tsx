import type { Metadata } from "next";
import type { ReactNode } from "react";
import { getProductDetails } from "../../lib/catalog";
import { createPageMetadata } from "../../lib/page-metadata";
import { shopProducts } from "../../shop/shop-data";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const product = shopProducts.find((item) => item.id === slug);

  if (!product) {
    return createPageMetadata({
      title: "صفحه پیدا نشد | Gramiss",
      description:
        "محصول موردنظر پیدا نشد؛ از فروشگاه یا جست‌وجوی Gramiss ادامه دهید.",
      path: `/product/${slug}`,
    });
  }

  return createPageMetadata({
    title: `${product.name} | Gramiss`,
    description: getProductDetails(product).description,
    path: `/product/${product.id}`,
  });
}

export default function ProductLayout({ children }: { children: ReactNode }) {
  return children;
}
