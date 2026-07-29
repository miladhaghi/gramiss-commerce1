import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "بازیابی رمز عبور | Gramiss",
  description: "پیش‌نمایش جریان بازیابی رمز عبور حساب Gramiss.",
  path: "/forgot-password",
});

export default function ForgotPasswordLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
