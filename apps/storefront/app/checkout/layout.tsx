import type { Metadata } from "next";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "تسویه حساب | Gramiss",
  description: "ثبت اطلاعات ارسال و مرور سفارش در نسخه نمایشی Gramiss.",
  path: "/checkout",
});

export default function CheckoutLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
