import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "خطای ارتباط | Gramiss",
  description: "صفحه نمایشی خطای ارتباط و تلاش دوباره در Gramiss.",
  path: "/network-error",
});

export default function NetworkErrorLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
