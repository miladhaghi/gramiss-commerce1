import type { Metadata } from "next";

const FALLBACK_SITE_URL = "http://localhost:3000";

function readSiteUrl(): URL {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim() || FALLBACK_SITE_URL;

  try {
    return new URL(configured);
  } catch {
    return new URL(FALLBACK_SITE_URL);
  }
}

export const SITE_URL = readSiteUrl();

const socialImageUrl =
  process.env.NEXT_PUBLIC_SOCIAL_IMAGE?.trim() || "/assets/hero-stage.png";

const socialImage = {
  url: socialImageUrl,
  width: 1440,
  height: 900,
  alt: "Gramiss — انتخاب هوشمند پوشاک مردانه",
};

function shouldIndex(): boolean {
  return (
    process.env.NODE_ENV === "production" &&
    process.env.NEXT_PUBLIC_ROBOTS_INDEX === "true"
  );
}

export function createPageMetadata({
  title,
  description,
  path,
}: {
  title: string;
  description: string;
  path?: string;
}): Metadata {
  const canonical = path ? new URL(path, SITE_URL).toString() : undefined;
  const index = shouldIndex();

  return {
    title,
    description,
    robots: {
      index,
      follow: index,
      googleBot: {
        index,
        follow: index,
      },
    },
    alternates: canonical ? { canonical } : undefined,
    openGraph: {
      title,
      description,
      url: canonical,
      siteName: "Gramiss",
      locale: "fa_IR",
      type: "website",
      images: [socialImage],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [socialImage.url],
    },
  };
}
