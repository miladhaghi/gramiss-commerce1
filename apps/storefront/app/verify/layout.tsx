import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "تأیید حساب | Gramiss",
  description: "پیش‌نمایش تأیید حساب نمایشی Gramiss.",
  path: "/verify",
});

export default function VerifyLayout({ children }: { children: ReactNode }) {
  return children;
}
