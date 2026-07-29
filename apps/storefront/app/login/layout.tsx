import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "ورود به حساب | Gramiss",
  description: "ورود امن به حساب نمایشی Gramiss.",
  path: "/login",
});

export default function LoginLayout({ children }: { children: ReactNode }) {
  return children;
}
