export const RECENT_SEARCHES_KEY = "gramiss:recent-searches";
export const MAX_RECENT_SEARCHES = 6;

const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

export function normalizeSearchText(value: string) {
  return value
    .normalize("NFKC")
    .replace(/ي/g, "ی")
    .replace(/ك/g, "ک")
    .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)))
    .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)))
    .replace(/\s+/g, " ")
    .trim()
    .toLocaleLowerCase("fa-IR");
}

export function readRecentSearches() {
  if (typeof window === "undefined") return [] as string[];
  try {
    const parsed = JSON.parse(
      window.localStorage.getItem(RECENT_SEARCHES_KEY) ?? "[]",
    );
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((item): item is string => typeof item === "string")
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, MAX_RECENT_SEARCHES);
  } catch {
    return [];
  }
}

export function saveRecentSearch(query: string) {
  if (typeof window === "undefined") return [] as string[];
  const trimmed = query.trim();
  if (!trimmed) return readRecentSearches();

  const normalized = normalizeSearchText(trimmed);
  const next = [
    trimmed,
    ...readRecentSearches().filter(
      (item) => normalizeSearchText(item) !== normalized,
    ),
  ].slice(0, MAX_RECENT_SEARCHES);

  window.localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
  return next;
}

export function removeRecentSearch(query: string) {
  if (typeof window === "undefined") return [] as string[];
  const normalized = normalizeSearchText(query);
  const next = readRecentSearches().filter(
    (item) => normalizeSearchText(item) !== normalized,
  );
  window.localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
  return next;
}

export function clearRecentSearches() {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(RECENT_SEARCHES_KEY, "[]");
}

