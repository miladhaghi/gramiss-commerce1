import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "ساخت حساب | Gramiss",
  description: "ساخت حساب نمایشی Gramiss بدون ایجاد حساب واقعی در سامانه فروش.",
  path: "/register",
});

export default function RegisterLayout({ children }: { children: ReactNode }) {
  return children;
}
