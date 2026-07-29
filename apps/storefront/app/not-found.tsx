import type { Metadata } from "next";
import { NotFoundState } from "./components/system-states";
import { createPageMetadata } from "./lib/page-metadata";

export const metadata: Metadata = createPageMetadata({
  title: "صفحه پیدا نشد | Gramiss",
  description:
    "صفحه‌ای که به دنبال آن بودید پیدا نشد؛ از صفحه اصلی، فروشگاه یا جست‌وجوی Gramiss ادامه دهید.",
});

export default function NotFoundPage() {
  return <NotFoundState />;
}
