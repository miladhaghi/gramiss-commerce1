import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "مقایسه محصولات | Gramiss",
  description: "مقایسه ویژگی‌ها، قیمت و کاربرد محصولات منتخب Gramiss.",
  path: "/compare",
});

export default function CompareLayout({ children }: { children: ReactNode }) {
  return children;
}
