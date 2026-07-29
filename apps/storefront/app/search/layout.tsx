import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "جستجو | Gramiss",
  description: "جست‌وجوی فارسی محصولات، دسته‌بندی‌ها و جنس‌های موجود در Gramiss.",
  path: "/search",
});

export default function SearchLayout({ children }: { children: ReactNode }) {
  return children;
}
