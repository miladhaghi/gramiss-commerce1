import type { Metadata } from "next";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "سبد خرید | Gramiss",
  description: "مرور و مدیریت محصولات انتخاب‌شده در سبد خرید Gramiss.",
  path: "/cart",
});

export default function CartLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
