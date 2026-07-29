import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "حساب من | Gramiss",
  description: "مدیریت اطلاعات، آدرس‌ها، سفارش‌های نمونه و تنظیمات حساب Gramiss.",
  path: "/account",
});

export default function AccountLayout({ children }: { children: ReactNode }) {
  return children;
}
