import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "پیش‌نمایش تأیید سفارش | Gramiss",
  description: "پیش‌نمایش نمایشی صفحه تأیید سفارش آینده Gramiss.",
  path: "/order-success",
});

export default function OrderSuccessLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
