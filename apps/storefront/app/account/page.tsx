"use client";

/* eslint-disable @next/next/no-img-element */

import {
  Bell,
  Check,
  ChevronLeft,
  Headphones,
  Heart,
  LayoutDashboard,
  LogOut,
  MapPin,
  Package,
  Pencil,
  Plus,
  Trash2,
  Truck,
  UserRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FormEvent,
  ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Drawer,
  Footer,
  Header,
  Newsletter,
  SearchDialog,
  type DrawerView,
  type Product,
} from "../home-client";
import {
  EmptyOrdersState,
  NetworkErrorPage,
} from "../components/system-states";
import {
  type DemoAddress,
  type NotificationPreferences,
  isIranianMobile,
  isValidEmail,
  normalizeAuthDigits,
  useDemoAuth,
} from "../hooks/use-demo-auth";
import { useGramissStore } from "../hooks/use-gramiss-store";
import { useNetworkAction } from "../hooks/use-network-action";
import {
  demoOrders,
  formatTomanAmount,
} from "../lib/demo-orders";
import { shopProducts } from "../shop/shop-data";

type AccountSection =
  | "overview"
  | "orders"
  | "addresses"
  | "profile"
  | "notifications";

type AddressErrors = Partial<
  Record<
    | "title"
    | "recipient"
    | "mobile"
    | "province"
    | "city"
    | "fullAddress"
    | "postalCode",
    string
  >
>;

const navItems: Array<{
  key?: AccountSection;
  label: string;
  icon: ReactNode;
  href?: string;
  logout?: boolean;
}> = [
  {
    key: "overview",
    label: "نمای کلی",
    icon: <LayoutDashboard aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    key: "orders",
    label: "سفارش‌های من",
    icon: <Package aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    label: "علاقه‌مندی‌ها",
    href: "/wishlist",
    icon: <Heart aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    key: "addresses",
    label: "آدرس‌ها",
    icon: <MapPin aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    key: "profile",
    label: "اطلاعات حساب",
    icon: <UserRound aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    key: "notifications",
    label: "اعلان‌ها",
    icon: <Bell aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
  {
    label: "خروج از حساب",
    logout: true,
    icon: <LogOut aria-hidden="true" size={18} strokeWidth={1.8} />,
  },
];

const notificationOptions: Array<{
  key: keyof NotificationPreferences;
  title: string;
  description: string;
}> = [
  {
    key: "orderUpdates",
    title: "به‌روزرسانی سفارش‌ها",
    description: "تغییر وضعیت، ارسال و تحویل سفارش‌های نمایشی",
  },
  {
    key: "promotions",
    title: "تخفیف‌ها و پیشنهادها",
    description: "پیشنهادهای منتخب و فرصت‌های خرید Gramiss",
  },
  {
    key: "newCollections",
    title: "کالکشن‌های جدید",
    description: "اطلاع از تازه‌ترین محصولات و مجموعه‌ها",
  },
  {
    key: "journal",
    title: "مجله Gramiss",
    description: "راهنمای پارچه، نگهداری و انتخاب بهتر",
  },
  {
    key: "smartRecommendations",
    title: "پیشنهادهای هوشمند",
    description: "پیشنهادهای شخصی‌تر بر اساس انتخاب‌های شما",
  },
];

const emptyAddress = (): DemoAddress => ({
  id: "",
  title: "",
  recipient: "",
  mobile: "",
  province: "",
  city: "",
  fullAddress: "",
  postalCode: "",
  building: "",
  isDefault: false,
});

function AccountCard({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`account-card ${className}`}>{children}</section>;
}

export default function AccountPage() {
  const router = useRouter();
  const {
    hydrated,
    isAuthenticated,
    profile,
    firstName,
    profileCompleteness,
    logout,
    updateProfile,
    saveAddress,
    deleteAddress,
    setDefaultAddress,
    setNotification,
  } = useDemoAuth();
  const {
    wishlisted,
    setWishlisted,
    cartItems,
    cartCount,
    addToCart,
  } = useGramissStore();
  const [activeSection, setActiveSection] =
    useState<AccountSection>("overview");
  const [drawer, setDrawer] = useState<DrawerView>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [toast, setToast] = useState("");
  const [addressModalOpen, setAddressModalOpen] = useState(false);
  const [addressDraft, setAddressDraft] = useState<DemoAddress>(emptyAddress);
  const [addressErrors, setAddressErrors] = useState<AddressErrors>({});
  const [deleteAddressId, setDeleteAddressId] = useState<string | null>(null);
  const addAddressButtonRef = useRef<HTMLButtonElement>(null);
  const logoutInProgressRef = useRef(false);
  const {
    status: networkStatus,
    retry: retryAccountData,
    checkInitialLoad,
  } = useNetworkAction("account");

  const wishlistProducts = useMemo(
    () => shopProducts.filter((product) => wishlisted.has(product.id)),
    [wishlisted],
  );
  const defaultAddress =
    profile.addresses.find((address) => address.isDefault) ??
    profile.addresses[0];
  const activeOrderCount = demoOrders.filter((order) => order.active).length;
  const hasAccountModal = Boolean(addressModalOpen || deleteAddressId);

  useEffect(() => {
    checkInitialLoad();
  }, [checkInitialLoad]);

  useEffect(() => {
    if (!hydrated) return;
    if (!isAuthenticated) {
      if (logoutInProgressRef.current) return;
      const intended =
        window.location.pathname + window.location.search;
      window.location.replace(
        `/login?returnTo=${encodeURIComponent(intended)}`,
      );
      return;
    }
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams(window.location.search);
      const requestedSection = params.get("section") as AccountSection | null;
      if (
        requestedSection &&
        ["overview", "orders", "addresses", "profile", "notifications"].includes(
          requestedSection,
        )
      ) {
        setActiveSection(requestedSection);
      }
      if (params.get("welcome") === "1") {
        setToast(`خوش آمدی ${firstName}؛ حساب نمایشی شما آماده است.`);
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, [firstName, hydrated, isAuthenticated]);

  useEffect(() => {
    if (!hasAccountModal) return;
    const previousOverflow = document.documentElement.style.overflow;
    const previousFocus = document.activeElement as HTMLElement | null;
    document.documentElement.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      const dialog = document.querySelector<HTMLElement>(
        ".account-address-modal, .account-confirm-modal",
      );
      dialog
        ?.querySelector<HTMLElement>(
          'input:not([disabled]), textarea:not([disabled]), button:not([disabled])',
        )
        ?.focus();
    }, 0);

    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        setAddressModalOpen(false);
        setDeleteAddressId(null);
        return;
      }
      if (event.key !== "Tab") return;
      const dialog = document.querySelector<HTMLElement>(
        ".account-address-modal, .account-confirm-modal",
      );
      const controls = Array.from(
        dialog?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? [],
      );
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.documentElement.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
      previousFocus?.focus();
    };
  }, [hasAccountModal]);

  function announce(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3400);
  }

  function closeDrawer() {
    setDrawer(null);
    setSelectedProduct(null);
  }

  function switchSection(section: AccountSection) {
    setActiveSection(section);
    window.history.replaceState(null, "", `/account?section=${section}`);
    window.scrollTo({ top: 160, behavior: "smooth" });
  }

  function handleLogout() {
    logoutInProgressRef.current = true;
    logout();
    router.push("/login?logout=1");
  }

  function toggleWishlist(product: Product) {
    setWishlisted((current) => {
      const next = new Set(current);
      const removing = next.has(product.id);
      if (removing) next.delete(product.id);
      else next.add(product.id);
      announce(
        removing
          ? `${product.name} از علاقه‌مندی‌ها حذف شد.`
          : `${product.name} به علاقه‌مندی‌ها اضافه شد.`,
      );
      return next;
    });
  }

  function openAddress(address?: DemoAddress) {
    setAddressDraft(
      address
        ? { ...address }
        : {
            ...emptyAddress(),
            id: `address-${Date.now()}`,
            recipient: profile.fullName,
            mobile: profile.mobile,
            isDefault: profile.addresses.length === 0,
          },
    );
    setAddressErrors({});
    setAddressModalOpen(true);
  }

  function validateAddress() {
    const nextErrors: AddressErrors = {};
    if (!addressDraft.title.trim())
      nextErrors.title = "عنوان آدرس را وارد کنید.";
    if (!addressDraft.recipient.trim())
      nextErrors.recipient = "نام گیرنده را وارد کنید.";
    if (!isIranianMobile(addressDraft.mobile)) {
      nextErrors.mobile = "شماره موبایل معتبر ایرانی وارد کنید.";
    }
    if (!addressDraft.province.trim())
      nextErrors.province = "استان را وارد کنید.";
    if (!addressDraft.city.trim()) nextErrors.city = "شهر را وارد کنید.";
    if (!addressDraft.fullAddress.trim())
      nextErrors.fullAddress = "آدرس کامل را وارد کنید.";
    if (!/^\d{10}$/.test(normalizeAuthDigits(addressDraft.postalCode.trim()))) {
      nextErrors.postalCode = "کد پستی باید دقیقاً ۱۰ رقم باشد.";
    }
    setAddressErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function submitAddress(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validateAddress()) return;
    saveAddress(addressDraft);
    setAddressModalOpen(false);
    announce("آدرس با موفقیت ذخیره شد.");
  }

  if (networkStatus === "loading") {
    return <NetworkErrorPage loading onRetry={retryAccountData} />;
  }

  if (networkStatus === "error") {
    return <NetworkErrorPage onRetry={retryAccountData} />;
  }

  if (!hydrated || !isAuthenticated) {
    return (
      <main className="account-access-loading" aria-live="polite">
        <Link href="/" className="wordmark" dir="ltr">
          GRAMISS
        </Link>
        <span className="auth-spinner" aria-hidden="true" />
        <p>{hydrated ? "در حال انتقال به صفحه ورود..." : "در حال آماده‌سازی حساب..."}</p>
      </main>
    );
  }

  return (
    <main className="page-shell account-page" id="top" data-node-id="34:2">
      <Header
        cartCount={cartCount}
        wishlistCount={wishlisted.size}
        onSearch={() => {
          setDrawer(null);
          setSearchOpen(true);
        }}
        onDrawer={(view) => {
          setSelectedProduct(null);
          setDrawer(view);
        }}
      />

      <header className="account-page-heading" dir="rtl">
        <nav className="account-breadcrumb" aria-label="مسیر صفحه">
          <Link href="/">خانه</Link>
          <ChevronLeft aria-hidden="true" size={14} strokeWidth={1.8} />
          <span>حساب من</span>
        </nav>
        <h1>حساب من</h1>
        <p>سفارش‌ها، علاقه‌مندی‌ها و اطلاعات شخصی خود را یک‌جا مدیریت کنید.</p>
      </header>

      <MobileAccountNavigation
        activeSection={activeSection}
        onChange={switchSection}
        onLogout={handleLogout}
      />

      <div className="account-layout">
        <AccountSidebar
          activeSection={activeSection}
          fullName={profile.fullName || "کاربر Gramiss"}
          email={profile.email || profile.mobile || "پروفایل نمایشی"}
          onChange={switchSection}
          onLogout={handleLogout}
        />

        <div className="account-main-content" dir="rtl">
          {activeSection === "overview" ? (
            <OverviewSection
              firstName={firstName}
              activeOrderCount={activeOrderCount}
              wishlistProducts={wishlistProducts}
              wishlistCount={wishlisted.size}
              addressCount={profile.addresses.length}
              defaultAddress={defaultAddress}
              profileCompleteness={profileCompleteness}
              onChangeSection={switchSection}
              onToggleWishlist={toggleWishlist}
              onAnnounce={announce}
              profileForm={
                <ProfileForm
                  profile={profile}
                  onSave={(values) => {
                    updateProfile(values);
                    announce("اطلاعات حساب با موفقیت ذخیره شد.");
                  }}
                />
              }
            />
          ) : null}
          {activeSection === "orders" ? (
            <OrdersSection onAnnounce={announce} />
          ) : null}
          {activeSection === "addresses" ? (
            <AddressesSection
              addresses={profile.addresses}
              addButtonRef={addAddressButtonRef}
              onAdd={() => openAddress()}
              onEdit={openAddress}
              onDelete={(id) => setDeleteAddressId(id)}
              onDefault={(id) => {
                setDefaultAddress(id);
                announce("آدرس پیش‌فرض تغییر کرد.");
              }}
            />
          ) : null}
          {activeSection === "profile" ? (
            <section className="account-section-stack">
              <SectionHeading
                title="اطلاعات حساب"
                description="اطلاعات پایه پروفایل نمایشی خود را ویرایش کنید."
              />
              <ProfileForm
                profile={profile}
                expanded
                onSave={(values) => {
                  updateProfile(values);
                  announce("اطلاعات حساب با موفقیت ذخیره شد.");
                }}
              />
            </section>
          ) : null}
          {activeSection === "notifications" ? (
            <NotificationsSection
              preferences={profile.notifications}
              onChange={(key, enabled) => {
                setNotification(key, enabled);
                announce("تنظیمات اعلان‌ها ذخیره شد.");
              }}
            />
          ) : null}
        </div>
      </div>

      <div className="account-lower-content">
        <Newsletter variant="account" />
      </div>
      <Footer />

      {searchOpen ? (
        <SearchDialog
          open
          catalog={shopProducts}
          onClose={() => setSearchOpen(false)}
          onOpenProduct={(product) => {
            setSearchOpen(false);
            setSelectedProduct(product);
          }}
        />
      ) : null}
      <Drawer
        view={drawer}
        onClose={closeDrawer}
        wishlisted={wishlisted}
        selectedProduct={selectedProduct}
        cartCount={cartCount}
        cartItems={cartItems}
        catalog={shopProducts}
        productsHref="/shop"
        onAddToCart={(product) => {
          addToCart(product);
          announce(`${product.name} به سبد خرید اضافه شد.`);
          closeDrawer();
        }}
      />

      {addressModalOpen ? (
        <AddressModal
          address={addressDraft}
          isEditing={profile.addresses.some(
            (address) => address.id === addressDraft.id,
          )}
          errors={addressErrors}
          onChange={(field, value) => {
            setAddressDraft((current) => ({ ...current, [field]: value }));
            if (addressErrors[field as keyof AddressErrors]) {
              setAddressErrors((current) => ({ ...current, [field]: "" }));
            }
          }}
          onClose={() => setAddressModalOpen(false)}
          onSubmit={submitAddress}
        />
      ) : null}

      {deleteAddressId ? (
        <div
          className="account-modal-overlay"
          role="presentation"
          onMouseDown={() => setDeleteAddressId(null)}
        >
          <section
            className="account-confirm-modal"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="delete-address-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <Trash2 aria-hidden="true" size={24} strokeWidth={1.7} />
            <h2 id="delete-address-title">حذف این آدرس؟</h2>
            <p>این آدرس از پروفایل نمایشی شما حذف می‌شود.</p>
            <div>
              <button type="button" onClick={() => setDeleteAddressId(null)}>
                انصراف
              </button>
              <button
                className="is-danger"
                type="button"
                onClick={() => {
                  deleteAddress(deleteAddressId);
                  setDeleteAddressId(null);
                  announce("آدرس حذف شد.");
                }}
              >
                حذف آدرس
              </button>
            </div>
          </section>
        </div>
      ) : null}

      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}

function AccountSidebar({
  activeSection,
  fullName,
  email,
  onChange,
  onLogout,
}: {
  activeSection: AccountSection;
  fullName: string;
  email: string;
  onChange: (section: AccountSection) => void;
  onLogout: () => void;
}) {
  return (
    <aside className="account-sidebar" dir="rtl">
      <div className="account-sidebar-user">
        <strong>{fullName}</strong>
        <span dir="ltr">{email}</span>
      </div>
      <nav aria-label="بخش‌های حساب">
        {navItems.map((item) =>
          item.href ? (
            <Link href={item.href} key={item.label}>
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ) : item.logout ? (
            <button type="button" key={item.label} onClick={onLogout}>
              {item.icon}
              <span>{item.label}</span>
            </button>
          ) : (
            <button
              className={activeSection === item.key ? "is-active" : ""}
              type="button"
              key={item.label}
              aria-current={activeSection === item.key ? "page" : undefined}
              onClick={() => onChange(item.key!)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ),
        )}
      </nav>
      <div className="account-support">
        <Headphones aria-hidden="true" size={23} strokeWidth={1.7} />
        <strong>نیاز به کمک دارید؟</strong>
        <p>پشتیبانی Gramiss برای راهنمایی سفارش و انتخاب محصول کنار شماست.</p>
        <a href="mailto:hello@gramiss.com">تماس با پشتیبانی</a>
      </div>
    </aside>
  );
}

function MobileAccountNavigation({
  activeSection,
  onChange,
  onLogout,
}: {
  activeSection: AccountSection;
  onChange: (section: AccountSection) => void;
  onLogout: () => void;
}) {
  return (
    <nav className="account-mobile-tabs" aria-label="بخش‌های حساب" dir="rtl">
      {navItems.map((item) =>
        item.href ? (
          <Link href={item.href} key={item.label}>
            {item.icon}
            <span>{item.label}</span>
          </Link>
        ) : item.logout ? (
          <button type="button" key={item.label} onClick={onLogout}>
            {item.icon}
            <span>{item.label}</span>
          </button>
        ) : (
          <button
            className={activeSection === item.key ? "is-active" : ""}
            type="button"
            key={item.label}
            onClick={() => onChange(item.key!)}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ),
      )}
    </nav>
  );
}

function OverviewSection({
  firstName,
  activeOrderCount,
  wishlistProducts,
  wishlistCount,
  addressCount,
  defaultAddress,
  profileCompleteness,
  onChangeSection,
  onToggleWishlist,
  onAnnounce,
  profileForm,
}: {
  firstName: string;
  activeOrderCount: number;
  wishlistProducts: Product[];
  wishlistCount: number;
  addressCount: number;
  defaultAddress?: DemoAddress;
  profileCompleteness: number;
  onChangeSection: (section: AccountSection) => void;
  onToggleWishlist: (product: Product) => void;
  onAnnounce: (message: string) => void;
  profileForm: ReactNode;
}) {
  return (
    <div className="account-overview">
      <header className="account-greeting">
        <h2>سلام {firstName}، خوش آمدی.</h2>
        <p>این خلاصه‌ای از فعالیت حساب نمایشی شماست.</p>
      </header>

      <div className="account-stat-grid">
        <StatCard value={activeOrderCount} label="سفارش فعال" />
        <StatCard value={wishlistCount} label="محصول محبوب" />
        <StatCard value={addressCount} label="آدرس ذخیره‌شده" />
      </div>

      <AccountCard className="account-orders-preview">
        <div className="account-card-heading">
          <div>
            <h3>سفارش‌های اخیر</h3>
            <span>داده‌های نمونه برای نمایش رابط کاربری</span>
          </div>
          <button type="button" onClick={() => onChangeSection("orders")}>
            مشاهده همه
            <ChevronLeft aria-hidden="true" size={16} />
          </button>
        </div>
        <OrderList compact onAnnounce={onAnnounce} />
      </AccountCard>

      <AccountCard className="account-wishlist-preview">
        <div className="account-card-heading">
          <div>
            <h3>علاقه‌مندی‌های شما</h3>
            <span>{wishlistCount.toLocaleString("fa-IR")} محصول ذخیره‌شده</span>
          </div>
          <Link href="/wishlist">
            مشاهده همه
            <ChevronLeft aria-hidden="true" size={16} />
          </Link>
        </div>
        {wishlistProducts.length ? (
          <div className="account-wishlist-grid">
            {wishlistProducts.slice(0, 3).map((product) => (
              <article key={product.id}>
                <Link
                  className="account-wishlist-media"
                  href={`/product/${product.id}`}
                >
                  <img src={product.image} alt={product.name} />
                </Link>
                <div>
                  <Link
                    href={`/product/${product.id}`}
                  >
                    {product.name}
                  </Link>
                  <span>{product.price}</span>
                </div>
                <button
                  type="button"
                  aria-label={`حذف ${product.name} از علاقه‌مندی‌ها`}
                  onClick={() => onToggleWishlist(product)}
                >
                  <X aria-hidden="true" size={17} />
                </button>
              </article>
            ))}
          </div>
        ) : (
          <div className="account-inline-empty">
            <Heart aria-hidden="true" size={30} strokeWidth={1.5} />
            <p>هنوز محصولی به علاقه‌مندی‌ها اضافه نکرده‌اید.</p>
            <Link href="/shop">دیدن محصولات</Link>
          </div>
        )}
      </AccountCard>

      <div className="account-overview-split">
        <AccountCard className="account-default-address">
          <div className="account-card-heading">
            <h3>آدرس پیش‌فرض</h3>
          </div>
          {defaultAddress ? (
            <>
              <strong>
                <MapPin aria-hidden="true" size={17} />
                {defaultAddress.title}
              </strong>
              <p>
                {defaultAddress.province}، {defaultAddress.city}،
                {" "}{defaultAddress.fullAddress}
              </p>
              <span>
                کد پستی: {defaultAddress.postalCode || "تکمیل نشده"}
              </span>
              <span>
                گیرنده: {defaultAddress.recipient || "تکمیل نشده"} —{" "}
                <bdi dir="ltr">{defaultAddress.mobile || "—"}</bdi>
              </span>
              <button
                type="button"
                onClick={() => onChangeSection("addresses")}
              >
                ویرایش آدرس
              </button>
            </>
          ) : (
            <div className="account-inline-empty is-compact">
              <p>هنوز آدرسی ذخیره نشده است.</p>
              <button
                type="button"
                onClick={() => onChangeSection("addresses")}
              >
                افزودن آدرس
              </button>
            </div>
          )}
        </AccountCard>

        <AccountCard className="account-profile-progress">
          <div className="account-card-heading">
            <h3>تکمیل اطلاعات حساب</h3>
            <strong>{profileCompleteness.toLocaleString("fa-IR")}٪</strong>
          </div>
          <div
            className="account-progress"
            role="progressbar"
            aria-label="درصد تکمیل پروفایل"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={profileCompleteness}
          >
            <span style={{ width: `${profileCompleteness}%` }} />
          </div>
          <p>
            با تکمیل تاریخ تولد و آدرس، پیشنهادهای Gramiss دقیق‌تر می‌شوند.
          </p>
          <button type="button" onClick={() => onChangeSection("profile")}>
            تکمیل پروفایل
          </button>
        </AccountCard>
      </div>

      {profileForm}
    </div>
  );
}

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <AccountCard className="account-stat-card">
      <strong>{value.toLocaleString("fa-IR")}</strong>
      <span>{label}</span>
    </AccountCard>
  );
}

function OrderList({
  compact = false,
  onAnnounce,
}: {
  compact?: boolean;
  onAnnounce: (message: string) => void;
}) {
  if (!demoOrders.length) {
    return <EmptyOrdersState compact />;
  }

  return (
    <div className={`account-order-list ${compact ? "is-compact" : ""}`}>
      {demoOrders.map((order) => (
        <article key={order.id}>
          <div className="account-order-number">
            <strong dir="ltr">#{order.id}</strong>
            <small>سفارش نمونه</small>
          </div>
          <span>{order.date}</span>
          <span className={`account-order-status is-${order.statusKey}`}>
            {order.status}
          </span>
          <b>{formatTomanAmount(order.total)}</b>
          <div className="account-order-actions">
            <button
              type="button"
              onClick={() =>
                onAnnounce(`جزئیات سفارش نمونه ${order.id} نمایش داده شد.`)
              }
            >
              مشاهده جزئیات
            </button>
            <Link
              href={`/track-order?order=${encodeURIComponent(order.id)}`}
              title={order.trackingInformation}
              aria-label={`پیگیری سفارش ${order.id}: ${order.trackingInformation}`}
            >
              <Truck aria-hidden="true" size={16} />
              پیگیری سفارش
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}

function OrdersSection({
  onAnnounce,
}: {
  onAnnounce: (message: string) => void;
}) {
  return (
    <section className="account-section-stack">
      <SectionHeading
        title="سفارش‌های من"
        description="این سفارش‌ها نمونه‌اند و به پرداخت یا سفارش واقعی متصل نیستند."
        tag="DEMO DATA"
      />
      {demoOrders.length ? (
        <AccountCard className="account-orders-full">
          <div className="account-orders-head" aria-hidden="true">
            <span>شماره سفارش</span>
            <span>تاریخ</span>
            <span>وضعیت</span>
            <span>مبلغ کل</span>
            <span>عملیات</span>
          </div>
          <OrderList onAnnounce={onAnnounce} />
        </AccountCard>
      ) : (
        <AccountCard className="account-orders-full">
          <EmptyOrdersState compact />
        </AccountCard>
      )}
    </section>
  );
}

function AddressesSection({
  addresses,
  addButtonRef,
  onAdd,
  onEdit,
  onDelete,
  onDefault,
}: {
  addresses: DemoAddress[];
  addButtonRef: React.RefObject<HTMLButtonElement | null>;
  onAdd: () => void;
  onEdit: (address: DemoAddress) => void;
  onDelete: (id: string) => void;
  onDefault: (id: string) => void;
}) {
  return (
    <section className="account-section-stack">
      <SectionHeading
        title="آدرس‌ها"
        description="آدرس‌های دریافت سفارش را در یک محل مدیریت کنید."
        action={
          <button
            ref={addButtonRef}
            className="account-section-action"
            type="button"
            onClick={onAdd}
          >
            <Plus aria-hidden="true" size={18} />
            افزودن آدرس
          </button>
        }
      />
      {addresses.length ? (
        <div className="account-address-grid">
          {addresses.map((address) => (
            <AccountCard className="account-address-card" key={address.id}>
              <div>
                <strong>{address.title}</strong>
                {address.isDefault ? (
                  <span className="account-default-badge">
                    <Check aria-hidden="true" size={14} />
                    پیش‌فرض
                  </span>
                ) : null}
              </div>
              <p>
                {address.province}، {address.city}، {address.fullAddress}
              </p>
              <span>گیرنده: {address.recipient}</span>
              <span dir="ltr">{address.mobile}</span>
              <span>کد پستی: {address.postalCode}</span>
              {address.building ? (
                <span>پلاک / واحد: {address.building}</span>
              ) : null}
              <div className="account-address-actions">
                <button type="button" onClick={() => onEdit(address)}>
                  <Pencil aria-hidden="true" size={16} />
                  ویرایش
                </button>
                <button type="button" onClick={() => onDelete(address.id)}>
                  <Trash2 aria-hidden="true" size={16} />
                  حذف
                </button>
                {!address.isDefault ? (
                  <button type="button" onClick={() => onDefault(address.id)}>
                    انتخاب به‌عنوان پیش‌فرض
                  </button>
                ) : null}
              </div>
            </AccountCard>
          ))}
        </div>
      ) : (
        <AccountCard className="account-empty-card">
          <MapPin aria-hidden="true" size={42} strokeWidth={1.4} />
          <h3>آدرسی ذخیره نشده است</h3>
          <p>اولین آدرس دریافت سفارش خود را اضافه کنید.</p>
          <button type="button" onClick={onAdd}>
            افزودن آدرس
          </button>
        </AccountCard>
      )}
    </section>
  );
}

function ProfileForm({
  profile,
  expanded = false,
  onSave,
}: {
  profile: {
    fullName: string;
    mobile: string;
    email: string;
    birthday: string;
  };
  expanded?: boolean;
  onSave: (values: {
    fullName: string;
    mobile: string;
    email: string;
    birthday: string;
  }) => void;
}) {
  const [values, setValues] = useState(profile);
  const [errors, setErrors] = useState<Record<string, string>>({});

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors: Record<string, string> = {};
    if (!values.fullName.trim())
      nextErrors.fullName = "نام و نام خانوادگی را وارد کنید.";
    if (!isIranianMobile(values.mobile))
      nextErrors.mobile = "شماره موبایل معتبر ایرانی وارد کنید.";
    if (!isValidEmail(values.email))
      nextErrors.email = "یک ایمیل معتبر وارد کنید.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    onSave(values);
  }

  return (
    <AccountCard
      className={`account-profile-form-card ${expanded ? "is-expanded" : ""}`}
    >
      {!expanded ? (
        <div className="account-card-heading">
          <h3>اطلاعات حساب</h3>
        </div>
      ) : null}
      <form className="account-profile-form" onSubmit={submit} noValidate>
        <AccountInput
          id={expanded ? "profile-full-name" : "overview-full-name"}
          label="نام و نام خانوادگی"
          value={values.fullName}
          error={errors.fullName}
          autoComplete="name"
          onChange={(value) => {
            setValues((current) => ({ ...current, fullName: value }));
            setErrors((current) => ({ ...current, fullName: "" }));
          }}
        />
        <AccountInput
          id={expanded ? "profile-mobile" : "overview-mobile"}
          label="شماره موبایل"
          value={values.mobile}
          error={errors.mobile}
          autoComplete="tel"
          inputMode="tel"
          dir="ltr"
          onChange={(value) => {
            setValues((current) => ({ ...current, mobile: value }));
            setErrors((current) => ({ ...current, mobile: "" }));
          }}
        />
        <AccountInput
          id={expanded ? "profile-email" : "overview-email"}
          label="ایمیل"
          value={values.email}
          error={errors.email}
          autoComplete="email"
          inputMode="email"
          dir="ltr"
          onChange={(value) => {
            setValues((current) => ({ ...current, email: value }));
            setErrors((current) => ({ ...current, email: "" }));
          }}
        />
        <AccountInput
          id={expanded ? "profile-birthday" : "overview-birthday"}
          label="تاریخ تولد"
          value={values.birthday}
          type="date"
          dir="ltr"
          onChange={(value) =>
            setValues((current) => ({ ...current, birthday: value }))
          }
        />
        <button className="account-save-button" type="submit">
          ذخیره تغییرات
        </button>
      </form>
    </AccountCard>
  );
}

function AccountInput({
  id,
  label,
  value,
  onChange,
  error,
  type = "text",
  autoComplete,
  inputMode,
  dir,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  type?: string;
  autoComplete?: string;
  inputMode?: "text" | "email" | "tel" | "numeric";
  dir?: "rtl" | "ltr";
}) {
  const errorId = `${id}-error`;
  return (
    <div className={`account-form-field ${error ? "has-error" : ""}`}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        autoComplete={autoComplete}
        inputMode={inputMode}
        dir={dir}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
      {error ? (
        <p id={errorId} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function NotificationsSection({
  preferences,
  onChange,
}: {
  preferences: NotificationPreferences;
  onChange: (key: keyof NotificationPreferences, enabled: boolean) => void;
}) {
  return (
    <section className="account-section-stack">
      <SectionHeading
        title="اعلان‌ها"
        description="مشخص کنید چه خبرهایی از Gramiss دریافت کنید."
      />
      <AccountCard className="account-notifications-card">
        {notificationOptions.map((option) => (
          <label className="account-notification-row" key={option.key}>
            <span>
              <strong>{option.title}</strong>
              <small>{option.description}</small>
            </span>
            <input
              type="checkbox"
              checked={preferences[option.key]}
              onChange={(event) => onChange(option.key, event.target.checked)}
            />
            <i aria-hidden="true" />
          </label>
        ))}
      </AccountCard>
    </section>
  );
}

function SectionHeading({
  title,
  description,
  tag,
  action,
}: {
  title: string;
  description: string;
  tag?: string;
  action?: ReactNode;
}) {
  return (
    <header className="account-section-heading">
      <div>
        {tag ? <span>{tag}</span> : null}
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}

function AddressModal({
  address,
  isEditing,
  errors,
  onChange,
  onClose,
  onSubmit,
}: {
  address: DemoAddress;
  isEditing: boolean;
  errors: AddressErrors;
  onChange: (field: keyof DemoAddress, value: string | boolean) => void;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div
      className="account-modal-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="account-address-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="address-modal-title"
        onMouseDown={(event) => event.stopPropagation()}
        dir="rtl"
      >
        <div className="account-modal-heading">
          <div>
            <span>ADDRESS</span>
            <h2 id="address-modal-title">
              {isEditing ? "ویرایش آدرس" : "افزودن آدرس"}
            </h2>
          </div>
          <button type="button" onClick={onClose} aria-label="بستن">
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <form onSubmit={onSubmit} noValidate>
          <AccountInput
            id="address-title"
            label="عنوان آدرس"
            value={address.title}
            error={errors.title}
            onChange={(value) => onChange("title", value)}
          />
          <AccountInput
            id="address-recipient"
            label="گیرنده"
            value={address.recipient}
            error={errors.recipient}
            autoComplete="name"
            onChange={(value) => onChange("recipient", value)}
          />
          <AccountInput
            id="address-mobile"
            label="شماره موبایل"
            value={address.mobile}
            error={errors.mobile}
            inputMode="tel"
            autoComplete="tel"
            dir="ltr"
            onChange={(value) => onChange("mobile", value)}
          />
          <AccountInput
            id="address-province"
            label="استان"
            value={address.province}
            error={errors.province}
            autoComplete="address-level1"
            onChange={(value) => onChange("province", value)}
          />
          <AccountInput
            id="address-city"
            label="شهر"
            value={address.city}
            error={errors.city}
            autoComplete="address-level2"
            onChange={(value) => onChange("city", value)}
          />
          <div className="account-form-field account-field-wide">
            <label htmlFor="address-full">آدرس کامل</label>
            <textarea
              id="address-full"
              value={address.fullAddress}
              autoComplete="street-address"
              aria-invalid={Boolean(errors.fullAddress)}
              onChange={(event) => onChange("fullAddress", event.target.value)}
            />
            {errors.fullAddress ? (
              <p role="alert">{errors.fullAddress}</p>
            ) : null}
          </div>
          <AccountInput
            id="address-postal-code"
            label="کد پستی"
            value={address.postalCode}
            error={errors.postalCode}
            inputMode="numeric"
            autoComplete="postal-code"
            dir="ltr"
            onChange={(value) => onChange("postalCode", value)}
          />
          <AccountInput
            id="address-building"
            label="پلاک / واحد"
            value={address.building}
            onChange={(value) => onChange("building", value)}
          />
          <label className="account-checkbox account-field-wide">
            <input
              type="checkbox"
              checked={address.isDefault}
              onChange={(event) => onChange("isDefault", event.target.checked)}
            />
            <span aria-hidden="true" />
            این آدرس پیش‌فرض من باشد
          </label>
          <div className="account-modal-actions account-field-wide">
            <button type="button" onClick={onClose}>
              انصراف
            </button>
            <button type="submit">ذخیره آدرس</button>
          </div>
        </form>
      </section>
    </div>
  );
}
