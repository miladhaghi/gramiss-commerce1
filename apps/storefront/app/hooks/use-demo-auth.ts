"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

export const DEMO_AUTH_STORAGE_KEY = "gramiss:demo-auth";
export const DEMO_PROFILE_STORAGE_KEY = "gramiss:demo-profile";
export const CHECKOUT_DRAFT_STORAGE_KEY = "gramiss:checkout-draft";

const AUTH_CHANGE_EVENT = "gramiss:demo-auth-change";

export type NotificationPreferences = {
  orderUpdates: boolean;
  promotions: boolean;
  newCollections: boolean;
  journal: boolean;
  smartRecommendations: boolean;
};

export type DemoAddress = {
  id: string;
  title: string;
  recipient: string;
  mobile: string;
  province: string;
  city: string;
  fullAddress: string;
  postalCode: string;
  building: string;
  isDefault: boolean;
};

export type DemoProfile = {
  fullName: string;
  email: string;
  mobile: string;
  birthday: string;
  addresses: DemoAddress[];
  notifications: NotificationPreferences;
};

const defaultNotifications: NotificationPreferences = {
  orderUpdates: true,
  promotions: false,
  newCollections: true,
  journal: true,
  smartRecommendations: true,
};

export const emptyDemoProfile: DemoProfile = {
  fullName: "",
  email: "",
  mobile: "",
  birthday: "",
  addresses: [],
  notifications: defaultNotifications,
};

const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

export function normalizeAuthDigits(value: string) {
  return value
    .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)))
    .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)));
}

export function isIranianMobile(value: string) {
  return /^09\d{9}$/.test(normalizeAuthDigits(value.trim()));
}

export function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function normalizeAddress(value: unknown): DemoAddress | null {
  if (!value || typeof value !== "object") return null;
  const address = value as Partial<DemoAddress>;
  const fields: Array<keyof Omit<DemoAddress, "isDefault">> = [
    "id",
    "title",
    "recipient",
    "mobile",
    "province",
    "city",
    "fullAddress",
    "postalCode",
    "building",
  ];
  if (!fields.every((field) => isString(address[field]))) return null;

  return {
    id: address.id ?? "",
    title: address.title ?? "",
    recipient: address.recipient ?? "",
    mobile: address.mobile ?? "",
    province: address.province ?? "",
    city: address.city ?? "",
    fullAddress: address.fullAddress ?? "",
    postalCode: address.postalCode ?? "",
    building: address.building ?? "",
    isDefault: Boolean(address.isDefault),
  };
}

function normalizeNotifications(value: unknown): NotificationPreferences {
  if (!value || typeof value !== "object") return defaultNotifications;
  const preferences = value as Partial<NotificationPreferences>;
  return {
    orderUpdates:
      typeof preferences.orderUpdates === "boolean"
        ? preferences.orderUpdates
        : defaultNotifications.orderUpdates,
    promotions:
      typeof preferences.promotions === "boolean"
        ? preferences.promotions
        : defaultNotifications.promotions,
    newCollections:
      typeof preferences.newCollections === "boolean"
        ? preferences.newCollections
        : defaultNotifications.newCollections,
    journal:
      typeof preferences.journal === "boolean"
        ? preferences.journal
        : defaultNotifications.journal,
    smartRecommendations:
      typeof preferences.smartRecommendations === "boolean"
        ? preferences.smartRecommendations
        : defaultNotifications.smartRecommendations,
  };
}

function normalizeProfile(value: unknown): DemoProfile {
  if (!value || typeof value !== "object") return { ...emptyDemoProfile };
  const profile = value as Partial<DemoProfile>;
  const addresses = Array.isArray(profile.addresses)
    ? profile.addresses
        .map(normalizeAddress)
        .filter((address): address is DemoAddress => Boolean(address))
    : [];

  if (addresses.length && !addresses.some((address) => address.isDefault)) {
    addresses[0] = { ...addresses[0], isDefault: true };
  }

  return {
    fullName: isString(profile.fullName) ? profile.fullName : "",
    email: isString(profile.email) ? profile.email : "",
    mobile: isString(profile.mobile) ? profile.mobile : "",
    birthday: isString(profile.birthday) ? profile.birthday : "",
    addresses,
    notifications: normalizeNotifications(profile.notifications),
  };
}

export function readDemoProfile() {
  if (typeof window === "undefined") return { ...emptyDemoProfile };
  try {
    const stored = window.localStorage.getItem(DEMO_PROFILE_STORAGE_KEY);
    return stored ? normalizeProfile(JSON.parse(stored)) : { ...emptyDemoProfile };
  } catch {
    return { ...emptyDemoProfile };
  }
}

export function writeDemoProfile(profile: DemoProfile) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(
    DEMO_PROFILE_STORAGE_KEY,
    JSON.stringify(normalizeProfile(profile)),
  );
}

function announceAuthChange() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
}

function readAuthState() {
  if (typeof window === "undefined") return false;
  return (
    window.localStorage.getItem(DEMO_AUTH_STORAGE_KEY) === "true" ||
    window.sessionStorage.getItem(DEMO_AUTH_STORAGE_KEY) === "true"
  );
}

function writeAuthState(authenticated: boolean, remember = true) {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(DEMO_AUTH_STORAGE_KEY);
  window.sessionStorage.removeItem(DEMO_AUTH_STORAGE_KEY);
  if (authenticated) {
    const storage = remember ? window.localStorage : window.sessionStorage;
    storage.setItem(DEMO_AUTH_STORAGE_KEY, "true");
  }
}

type CheckoutDraftValues = {
  fullName?: string;
  mobile?: string;
  province?: string;
  city?: string;
  address?: string;
  postalCode?: string;
  building?: string;
};

function readCheckoutDraftValues(): CheckoutDraftValues | null {
  if (typeof window === "undefined") return null;
  try {
    const stored = window.sessionStorage.getItem(CHECKOUT_DRAFT_STORAGE_KEY);
    if (!stored) return null;
    const parsed = JSON.parse(stored) as { values?: CheckoutDraftValues };
    return parsed.values && typeof parsed.values === "object"
      ? parsed.values
      : null;
  } catch {
    return null;
  }
}

function addressFromCheckout(
  values: CheckoutDraftValues,
  id = "checkout-default",
): DemoAddress | null {
  const fullAddress = values.address?.trim() ?? "";
  const province = values.province?.trim() ?? "";
  const city = values.city?.trim() ?? "";
  if (!fullAddress || !province || !city) return null;

  return {
    id,
    title: "آدرس سفارش",
    recipient: values.fullName?.trim() ?? "",
    mobile: normalizeAuthDigits(values.mobile?.trim() ?? ""),
    province,
    city,
    fullAddress,
    postalCode: normalizeAuthDigits(values.postalCode?.trim() ?? ""),
    building: values.building?.trim() ?? "",
    isDefault: true,
  };
}

function mergeCheckoutDraft(profile: DemoProfile) {
  const values = readCheckoutDraftValues();
  if (!values) return profile;
  const checkoutAddress = addressFromCheckout(values);
  const shouldAddAddress =
    checkoutAddress && profile.addresses.length === 0;
  const nextProfile: DemoProfile = {
    ...profile,
    fullName: profile.fullName || values.fullName?.trim() || "",
    mobile:
      profile.mobile || normalizeAuthDigits(values.mobile?.trim() ?? ""),
    addresses: shouldAddAddress ? [checkoutAddress] : profile.addresses,
  };
  return nextProfile;
}

export function mergeCheckoutIntoDemoProfile(values: CheckoutDraftValues) {
  if (typeof window === "undefined") return;
  const profile = readDemoProfile();
  const currentDefault = profile.addresses.find((address) => address.isDefault);
  const checkoutAddress = addressFromCheckout(
    values,
    currentDefault?.id ?? "checkout-default",
  );
  const addresses = checkoutAddress
    ? [
        checkoutAddress,
        ...profile.addresses
          .filter((address) => address.id !== checkoutAddress.id)
          .map((address) => ({ ...address, isDefault: false })),
      ]
    : profile.addresses;
  writeDemoProfile({
    ...profile,
    fullName: values.fullName?.trim() || profile.fullName,
    mobile:
      normalizeAuthDigits(values.mobile?.trim() ?? "") || profile.mobile,
    addresses,
  });
  announceAuthChange();
}

export function getProfileCompleteness(profile: DemoProfile) {
  const completed = [
    profile.fullName.trim(),
    profile.email.trim(),
    profile.mobile.trim(),
    profile.birthday.trim(),
    profile.addresses.length ? "address" : "",
  ].filter(Boolean).length;
  return Math.round((completed / 5) * 100);
}

export function getFirstName(profile: DemoProfile) {
  return profile.fullName.trim().split(/\s+/)[0] || "دوست Gramiss";
}

export function useDemoAuth() {
  const [profile, setProfileState] =
    useState<DemoProfile>(emptyDemoProfile);
  const [isAuthenticated, setAuthenticated] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  const reload = useCallback(() => {
    const storedProfile = readDemoProfile();
    const mergedProfile = mergeCheckoutDraft(storedProfile);
    if (JSON.stringify(mergedProfile) !== JSON.stringify(storedProfile)) {
      writeDemoProfile(mergedProfile);
    }
    setProfileState(mergedProfile);
    setAuthenticated(readAuthState());
    setHydrated(true);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(reload, 0);
    function onStorage(event: StorageEvent) {
      if (
        event.key === DEMO_AUTH_STORAGE_KEY ||
        event.key === DEMO_PROFILE_STORAGE_KEY
      ) {
        reload();
      }
    }
    window.addEventListener("storage", onStorage);
    window.addEventListener(AUTH_CHANGE_EVENT, reload);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(AUTH_CHANGE_EVENT, reload);
    };
  }, [reload]);

  const commitProfile = useCallback((nextProfile: DemoProfile) => {
    const normalized = normalizeProfile(nextProfile);
    setProfileState(normalized);
    writeDemoProfile(normalized);
    announceAuthChange();
    return normalized;
  }, []);

  const login = useCallback(
    (identifier: string, remember: boolean) => {
      const normalizedIdentifier = identifier.trim();
      const current = readDemoProfile();
      const nextProfile = {
        ...current,
        email: isValidEmail(normalizedIdentifier)
          ? normalizedIdentifier
          : current.email,
        mobile: isIranianMobile(normalizedIdentifier)
          ? normalizeAuthDigits(normalizedIdentifier)
          : current.mobile,
      };
      writeDemoProfile(nextProfile);
      writeAuthState(true, remember);
      setProfileState(nextProfile);
      setAuthenticated(true);
      announceAuthChange();
    },
    [],
  );

  const register = useCallback(
    (details: { fullName: string; mobile: string; email: string }) => {
      const current = readDemoProfile();
      const nextProfile = {
        ...current,
        fullName: details.fullName.trim(),
        mobile: normalizeAuthDigits(details.mobile.trim()),
        email: details.email.trim(),
      };
      writeDemoProfile(nextProfile);
      writeAuthState(true, true);
      setProfileState(nextProfile);
      setAuthenticated(true);
      announceAuthChange();
    },
    [],
  );

  const logout = useCallback(() => {
    writeAuthState(false);
    setAuthenticated(false);
    announceAuthChange();
  }, []);

  const updateProfile = useCallback(
    (updates: Pick<DemoProfile, "fullName" | "mobile" | "email" | "birthday">) =>
      commitProfile({
        ...readDemoProfile(),
        ...updates,
        mobile: normalizeAuthDigits(updates.mobile.trim()),
      }),
    [commitProfile],
  );

  const saveAddress = useCallback(
    (address: DemoAddress) => {
      const current = readDemoProfile();
      const exists = current.addresses.some((item) => item.id === address.id);
      const shouldDefault =
        address.isDefault || (!exists && current.addresses.length === 0);
      const nextAddress = {
        ...address,
        mobile: normalizeAuthDigits(address.mobile),
        postalCode: normalizeAuthDigits(address.postalCode),
        isDefault: shouldDefault,
      };
      const addresses = exists
        ? current.addresses.map((item) =>
            item.id === address.id ? nextAddress : item,
          )
        : [...current.addresses, nextAddress];
      return commitProfile({
        ...current,
        addresses: shouldDefault
          ? addresses.map((item) => ({
              ...item,
              isDefault: item.id === nextAddress.id,
            }))
          : addresses,
      });
    },
    [commitProfile],
  );

  const deleteAddress = useCallback(
    (id: string) => {
      const current = readDemoProfile();
      const removedWasDefault = current.addresses.some(
        (address) => address.id === id && address.isDefault,
      );
      const addresses = current.addresses.filter((address) => address.id !== id);
      if (removedWasDefault && addresses.length) {
        addresses[0] = { ...addresses[0], isDefault: true };
      }
      return commitProfile({ ...current, addresses });
    },
    [commitProfile],
  );

  const setDefaultAddress = useCallback(
    (id: string) => {
      const current = readDemoProfile();
      return commitProfile({
        ...current,
        addresses: current.addresses.map((address) => ({
          ...address,
          isDefault: address.id === id,
        })),
      });
    },
    [commitProfile],
  );

  const setNotification = useCallback(
    (key: keyof NotificationPreferences, enabled: boolean) => {
      const current = readDemoProfile();
      return commitProfile({
        ...current,
        notifications: {
          ...current.notifications,
          [key]: enabled,
        },
      });
    },
    [commitProfile],
  );

  const profileCompleteness = useMemo(
    () => getProfileCompleteness(profile),
    [profile],
  );

  return {
    hydrated,
    isAuthenticated,
    profile,
    firstName: getFirstName(profile),
    profileCompleteness,
    login,
    register,
    logout,
    updateProfile,
    saveAddress,
    deleteAddress,
    setDefaultAddress,
    setNotification,
  };
}
