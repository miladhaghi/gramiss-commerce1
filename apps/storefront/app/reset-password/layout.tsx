import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "تنظیم رمز جدید | Gramiss",
  description: "پیش‌نمایش تنظیم رمز عبور جدید برای حساب Gramiss.",
  path: "/reset-password",
});

export default function ResetPasswordLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
