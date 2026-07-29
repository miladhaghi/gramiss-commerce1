import type { Metadata } from "next";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "فروشگاه Gramiss | خرید پوشاک و اکسسوری مردانه",
  description:
    "محصولات منتخب Gramiss با تمرکز بر کیفیت، دوام و استایل روزمره مردانه.",
  path: "/shop",
});

export default function ShopLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
