import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "پیگیری سفارش | Gramiss",
  description: "پیگیری وضعیت سفارش‌های نمونه Gramiss با شماره سفارش.",
  path: "/track-order",
});

export default function TrackOrderLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
