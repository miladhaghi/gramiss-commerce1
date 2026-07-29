import type { Metadata } from "next";
import { createPageMetadata } from "../../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "کلاه آبی آسمانی | Gramiss",
  description:
    "کلاه آبی آسمانی Gramiss؛ کتان ترکیبی سبک با بند قابل تنظیم برای استفاده روزمره و استایل شهری.",
  path: "/product/sky-blue-cap",
});

export default function SkyBlueCapLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
