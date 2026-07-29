import type { Metadata } from "next";
import type { ReactNode } from "react";
import { createPageMetadata } from "../lib/page-metadata";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ notFound: string[] }>;
}): Promise<Metadata> {
  const { notFound: segments } = await params;
  return createPageMetadata({
    title: "صفحه پیدا نشد | Gramiss",
    description:
      "صفحه‌ای که به دنبال آن بودید پیدا نشد؛ از صفحه اصلی، فروشگاه یا جست‌وجوی Gramiss ادامه دهید.",
    path: `/${segments.join("/")}`,
  });
}

export default function CatchAllLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
