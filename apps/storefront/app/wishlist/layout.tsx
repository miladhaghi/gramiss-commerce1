import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "علاقه‌مندی‌ها | Gramiss",
  description: "مرور و مدیریت محصولات ذخیره‌شده در علاقه‌مندی‌های Gramiss.",
  path: "/wishlist",
});

export default function WishlistLayout({ children }: { children: ReactNode }) {
  return children;
}
