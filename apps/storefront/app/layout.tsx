import type { Metadata } from "next";
import "@fontsource-variable/estedad";
import "@fontsource-variable/inter";
import "./globals.css";
import { createPageMetadata, SITE_URL } from "./lib/page-metadata";

export const metadata: Metadata = {
  metadataBase: SITE_URL,
  ...createPageMetadata({
    title: "Gramiss | انتخاب هوشمند پوشاک مردانه",
    description:
      "Gramiss برای انتخاب هوشمند پوشاک و اکسسوری مردانه با اطلاعات شفاف درباره جنس، دوام و کاربرد.",
    path: "/",
  }),
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
