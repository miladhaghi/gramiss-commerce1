"use client";

import {
  ClipboardEvent,
  FormEvent,
  KeyboardEvent,
  ReactNode,
  useEffect,
  useState,
} from "react";
import { CheckCircle2, Eye, EyeOff, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  isIranianMobile,
  isValidEmail,
  normalizeAuthDigits,
  useDemoAuth,
} from "../hooks/use-demo-auth";

export type AuthMode = "login" | "register" | "forgot" | "verify" | "reset";

type FieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
  inputMode?: "email" | "tel" | "text" | "numeric";
  dir?: "rtl" | "ltr";
  required?: boolean;
  action?: ReactNode;
};

const authCopy: Record<
  AuthMode,
  { title: string; description: string; button: string }
> = {
  login: {
    title: "ورود به حساب",
    description: "برای ادامه، شماره موبایل یا ایمیل و رمز عبور را وارد کنید.",
    button: "ورود به حساب",
  },
  register: {
    title: "ساخت حساب جدید",
    description: "با ساخت حساب، محصولات دلخواه و سفارش‌های خود را مدیریت کنید.",
    button: "ایجاد حساب",
  },
  forgot: {
    title: "بازیابی رمز عبور",
    description: "کد بازیابی برای شما ارسال می‌شود.",
    button: "ارسال کد بازیابی",
  },
  verify: {
    title: "تأیید کد",
    description: "کد پنج‌رقمی ارسال‌شده را وارد کنید.",
    button: "تأیید و ادامه",
  },
  reset: {
    title: "رمز عبور جدید",
    description: "رمزی امن و قابل یادآوری انتخاب کنید.",
    button: "ذخیره رمز جدید",
  },
};

function isValidIdentifier(value: string) {
  return isValidEmail(value) || isIranianMobile(value);
}

function getSafeReturnTo() {
  if (typeof window === "undefined") return "/account";
  const candidate = new URLSearchParams(window.location.search).get("returnTo");
  return candidate && candidate.startsWith("/") && !candidate.startsWith("//")
    ? candidate
    : "/account";
}

function AuthField({
  id,
  label,
  value,
  onChange,
  error,
  type = "text",
  placeholder,
  autoComplete,
  inputMode,
  dir,
  required = false,
  action,
}: FieldProps) {
  const errorId = `${id}-error`;
  return (
    <div className={`auth-field ${error ? "has-error" : ""}`}>
      <label htmlFor={id}>
        {label}
        {required ? <span aria-hidden="true">*</span> : null}
      </label>
      <div className="auth-input-wrap">
        <input
          id={id}
          name={id}
          type={type}
          value={value}
          placeholder={placeholder}
          autoComplete={autoComplete}
          inputMode={inputMode}
          dir={dir}
          required={required}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          onChange={(event) => onChange(event.target.value)}
        />
        {action}
      </div>
      {error ? (
        <p id={errorId} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function PasswordAction({
  visible,
  onToggle,
  label,
}: {
  visible: boolean;
  onToggle: () => void;
  label: string;
}) {
  return (
    <button
      className="auth-password-toggle"
      type="button"
      aria-label={label}
      aria-pressed={visible}
      onClick={onToggle}
    >
      {visible ? (
        <EyeOff aria-hidden="true" size={19} strokeWidth={1.8} />
      ) : (
        <Eye aria-hidden="true" size={19} strokeWidth={1.8} />
      )}
    </button>
  );
}

function AuthArtwork({ mode }: { mode: AuthMode }) {
  const labels = {
    login: ["محصولات ذخیره‌شده", "پیگیری سفارش", "پیشنهاد شخصی"],
    register: ["پروفایل شخصی", "انتخاب‌های محبوب", "مسیر خرید کوتاه"],
    forgot: ["بازیابی امن", "بدون ذخیره رمز", "دسترسی دوباره"],
    verify: ["کد نمایشی", "تأیید سریع", "بدون پیامک واقعی"],
    reset: ["رمز تازه", "حداقل ۸ کاراکتر", "ورود دوباره"],
  }[mode];

  return (
    <div className="auth-artwork" aria-hidden="true">
      <span className="auth-artwork-mark">G</span>
      <div>
        {labels.map((label) => (
          <span key={label}>{label}</span>
        ))}
      </div>
    </div>
  );
}

export default function AuthFlow({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const { login, register } = useDemoAuth();
  const [identifier, setIdentifier] = useState("");
  const [fullName, setFullName] = useState("");
  const [mobile, setMobile] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState("");
  const [code, setCode] = useState(["", "", "", "", ""]);
  const [resendSeconds, setResendSeconds] = useState(60);
  const [resetSucceeded, setResetSucceeded] = useState(false);

  useEffect(() => {
    if (mode !== "login") return;
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams(window.location.search);
      if (params.get("logout") === "1") {
        setToast("با موفقیت از حساب نمایشی خارج شدید.");
      } else if (params.get("reset") === "1") {
        setToast("رمز نمایشی با موفقیت تغییر کرد. اکنون وارد شوید.");
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, [mode]);

  useEffect(() => {
    if (mode !== "verify" || resendSeconds <= 0) return;
    const timer = window.setInterval(
      () => setResendSeconds((seconds) => Math.max(0, seconds - 1)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [mode, resendSeconds]);

  function clearError(field: string) {
    if (!errors[field]) return;
    setErrors((current) => ({ ...current, [field]: "" }));
  }

  function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors: Record<string, string> = {};
    if (!isValidIdentifier(identifier)) {
      nextErrors.identifier =
        "یک ایمیل معتبر یا شماره موبایل ایرانی وارد کنید.";
    }
    if (password.length < 8) {
      nextErrors.password = "رمز عبور باید حداقل ۸ کاراکتر باشد.";
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setLoading(true);
    window.setTimeout(() => {
      login(identifier, remember);
      router.push(getSafeReturnTo());
    }, 650);
  }

  function submitRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors: Record<string, string> = {};
    if (!fullName.trim()) {
      nextErrors.fullName = "نام و نام خانوادگی را وارد کنید.";
    }
    if (!isIranianMobile(mobile)) {
      nextErrors.mobile =
        "شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم داشته باشد.";
    }
    if (!isValidEmail(email)) {
      nextErrors.email = "یک ایمیل معتبر وارد کنید.";
    }
    if (password.length < 8) {
      nextErrors.password = "رمز عبور باید حداقل ۸ کاراکتر باشد.";
    }
    if (confirmPassword !== password) {
      nextErrors.confirmPassword = "تکرار رمز عبور با رمز اصلی یکسان نیست.";
    }
    if (!termsAccepted) {
      nextErrors.terms = "برای ادامه باید قوانین را بپذیرید.";
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setLoading(true);
    window.setTimeout(() => {
      register({ fullName, mobile, email });
      router.push("/account?welcome=1");
    }, 700);
  }

  function submitForgot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!isValidIdentifier(identifier)) {
      setErrors({
        identifier: "یک ایمیل معتبر یا شماره موبایل ایرانی وارد کنید.",
      });
      return;
    }
    setLoading(true);
    window.setTimeout(() => router.push("/verify"), 600);
  }

  function updateCode(index: number, value: string) {
    const digit = normalizeAuthDigits(value).replace(/\D/g, "").slice(-1);
    setCode((current) =>
      current.map((item, itemIndex) => (itemIndex === index ? digit : item)),
    );
    clearError("code");
    if (digit && index < code.length - 1) {
      document
        .querySelector<HTMLInputElement>(`#verification-digit-${index + 1}`)
        ?.focus();
    }
  }

  function handleCodeKeyDown(
    index: number,
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Backspace" && !code[index] && index > 0) {
      document
        .querySelector<HTMLInputElement>(`#verification-digit-${index - 1}`)
        ?.focus();
    }
    if (event.key === "ArrowLeft" && index > 0) {
      document
        .querySelector<HTMLInputElement>(`#verification-digit-${index - 1}`)
        ?.focus();
    }
    if (event.key === "ArrowRight" && index < code.length - 1) {
      document
        .querySelector<HTMLInputElement>(`#verification-digit-${index + 1}`)
        ?.focus();
    }
  }

  function handleCodePaste(event: ClipboardEvent<HTMLDivElement>) {
    const pasted = normalizeAuthDigits(event.clipboardData.getData("text"))
      .replace(/\D/g, "")
      .slice(0, code.length);
    if (!pasted) return;
    event.preventDefault();
    const next = Array.from({ length: code.length }, (_, index) =>
      pasted[index] ? pasted[index] : "",
    );
    setCode(next);
    clearError("code");
    document
      .querySelector<HTMLInputElement>(
        `#verification-digit-${Math.min(pasted.length, code.length) - 1}`,
      )
      ?.focus();
  }

  function submitVerify(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (code.some((digit) => !digit)) {
      setErrors({ code: "کد پنج‌رقمی را کامل وارد کنید." });
      return;
    }
    setLoading(true);
    window.setTimeout(() => router.push("/reset-password"), 550);
  }

  function submitReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors: Record<string, string> = {};
    if (password.length < 8) {
      nextErrors.password = "رمز عبور باید حداقل ۸ کاراکتر باشد.";
    }
    if (confirmPassword !== password) {
      nextErrors.confirmPassword = "تکرار رمز عبور با رمز اصلی یکسان نیست.";
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setLoading(true);
    window.setTimeout(() => {
      setLoading(false);
      setResetSucceeded(true);
      setPassword("");
      setConfirmPassword("");
      window.setTimeout(() => router.push("/login?reset=1"), 950);
    }, 650);
  }

  function renderLogin() {
    return (
      <form className="auth-form" onSubmit={submitLogin} noValidate>
        <AuthField
          id="login-identifier"
          label="ایمیل یا شماره موبایل"
          value={identifier}
          onChange={(value) => {
            setIdentifier(value);
            clearError("identifier");
          }}
          error={errors.identifier}
          placeholder="example@email.com"
          autoComplete="username"
          dir="ltr"
          required
        />
        <AuthField
          id="login-password"
          label="رمز عبور"
          value={password}
          onChange={(value) => {
            setPassword(value);
            clearError("password");
          }}
          error={errors.password}
          type={showPassword ? "text" : "password"}
          placeholder="حداقل ۸ کاراکتر"
          autoComplete="current-password"
          dir="ltr"
          required
          action={
            <PasswordAction
              visible={showPassword}
              onToggle={() => setShowPassword((current) => !current)}
              label={showPassword ? "پنهان کردن رمز عبور" : "نمایش رمز عبور"}
            />
          }
        />
        <div className="auth-form-options">
          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={remember}
              onChange={(event) => setRemember(event.target.checked)}
            />
            <span aria-hidden="true" />
            مرا به خاطر بسپار
          </label>
          <Link href="/forgot-password">رمز عبور را فراموش کرده‌اید؟</Link>
        </div>
        <AuthSubmit loading={loading} label={authCopy.login.button} />
        <p className="auth-switch">
          حساب ندارید؟ <Link href="/register">ثبت‌نام کنید</Link>
        </p>
      </form>
    );
  }

  function renderRegister() {
    return (
      <form className="auth-form auth-register-form" onSubmit={submitRegister} noValidate>
        <AuthField
          id="register-full-name"
          label="نام و نام خانوادگی"
          value={fullName}
          onChange={(value) => {
            setFullName(value);
            clearError("fullName");
          }}
          error={errors.fullName}
          autoComplete="name"
          required
        />
        <div className="auth-field-row">
          <AuthField
            id="register-mobile"
            label="شماره موبایل"
            value={mobile}
            onChange={(value) => {
              setMobile(value);
              clearError("mobile");
            }}
            error={errors.mobile}
            placeholder="09123456789"
            autoComplete="tel"
            inputMode="tel"
            dir="ltr"
            required
          />
          <AuthField
            id="register-email"
            label="ایمیل"
            value={email}
            onChange={(value) => {
              setEmail(value);
              clearError("email");
            }}
            error={errors.email}
            placeholder="example@email.com"
            autoComplete="email"
            inputMode="email"
            dir="ltr"
            required
          />
        </div>
        <div className="auth-field-row">
          <AuthField
            id="register-password"
            label="رمز عبور"
            value={password}
            onChange={(value) => {
              setPassword(value);
              clearError("password");
            }}
            error={errors.password}
            type={showPassword ? "text" : "password"}
            placeholder="حداقل ۸ کاراکتر"
            autoComplete="new-password"
            dir="ltr"
            required
            action={
              <PasswordAction
                visible={showPassword}
                onToggle={() => setShowPassword((current) => !current)}
                label={showPassword ? "پنهان کردن رمز عبور" : "نمایش رمز عبور"}
              />
            }
          />
          <AuthField
            id="register-confirm-password"
            label="تکرار رمز عبور"
            value={confirmPassword}
            onChange={(value) => {
              setConfirmPassword(value);
              clearError("confirmPassword");
            }}
            error={errors.confirmPassword}
            type={showConfirmPassword ? "text" : "password"}
            placeholder="رمز عبور را دوباره وارد کنید"
            autoComplete="new-password"
            dir="ltr"
            required
            action={
              <PasswordAction
                visible={showConfirmPassword}
                onToggle={() =>
                  setShowConfirmPassword((current) => !current)
                }
                label={
                  showConfirmPassword
                    ? "پنهان کردن تکرار رمز عبور"
                    : "نمایش تکرار رمز عبور"
                }
              />
            }
          />
        </div>
        <label className={`auth-checkbox auth-terms ${errors.terms ? "has-error" : ""}`}>
          <input
            type="checkbox"
            checked={termsAccepted}
            onChange={(event) => {
              setTermsAccepted(event.target.checked);
              clearError("terms");
            }}
          />
          <span aria-hidden="true" />
          <b>
            قوانین استفاده و حریم خصوصی Gramiss را می‌پذیرم.
          </b>
        </label>
        {errors.terms ? (
          <p className="auth-standalone-error" role="alert">
            {errors.terms}
          </p>
        ) : null}
        <AuthSubmit loading={loading} label={authCopy.register.button} />
        <p className="auth-switch">
          قبلاً ثبت‌نام کرده‌اید؟ <Link href="/login">وارد شوید</Link>
        </p>
      </form>
    );
  }

  function renderForgot() {
    return (
      <form className="auth-form" onSubmit={submitForgot} noValidate>
        <AuthField
          id="forgot-identifier"
          label="ایمیل یا شماره موبایل"
          value={identifier}
          onChange={(value) => {
            setIdentifier(value);
            clearError("identifier");
          }}
          error={errors.identifier}
          placeholder="example@email.com"
          autoComplete="username"
          dir="ltr"
          required
        />
        <p className="auth-demo-note">
          این مرحله نمایشی است و پیامک یا ایمیل واقعی ارسال نمی‌شود.
        </p>
        <AuthSubmit loading={loading} label={authCopy.forgot.button} />
        <p className="auth-switch">
          <Link href="/login">بازگشت به صفحه ورود</Link>
        </p>
      </form>
    );
  }

  function renderVerify() {
    return (
      <form className="auth-form" onSubmit={submitVerify} noValidate>
        <div
          className={`verification-code ${errors.code ? "has-error" : ""}`}
          dir="ltr"
          onPaste={handleCodePaste}
        >
          {code.map((digit, index) => (
            <input
              key={index}
              id={`verification-digit-${index}`}
              aria-label={`رقم ${index + 1} کد تأیید`}
              inputMode="numeric"
              autoComplete={index === 0 ? "one-time-code" : "off"}
              maxLength={1}
              value={digit}
              onChange={(event) => updateCode(index, event.target.value)}
              onKeyDown={(event) => handleCodeKeyDown(index, event)}
            />
          ))}
        </div>
        {errors.code ? (
          <p className="auth-standalone-error" role="alert">
            {errors.code}
          </p>
        ) : null}
        <p className="auth-demo-note">
          در نسخه نمایشی، هر کد پنج‌رقمی کامل پذیرفته می‌شود.
        </p>
        <AuthSubmit loading={loading} label={authCopy.verify.button} />
        <button
          className="auth-resend"
          type="button"
          disabled={resendSeconds > 0}
          onClick={() => {
            setResendSeconds(60);
            setToast("ارسال مجدد کد به‌صورت نمایشی انجام شد.");
          }}
        >
          {resendSeconds > 0
            ? `ارسال مجدد تا ${resendSeconds.toLocaleString("fa-IR")} ثانیه`
            : "ارسال مجدد کد"}
        </button>
      </form>
    );
  }

  function renderReset() {
    return (
      <form className="auth-form" onSubmit={submitReset} noValidate>
        {resetSucceeded ? (
          <div className="auth-success" role="status">
            <CheckCircle2 aria-hidden="true" size={22} />
            رمز نمایشی با موفقیت به‌روزرسانی شد.
          </div>
        ) : null}
        <AuthField
          id="reset-password"
          label="رمز عبور جدید"
          value={password}
          onChange={(value) => {
            setPassword(value);
            clearError("password");
          }}
          error={errors.password}
          type={showPassword ? "text" : "password"}
          placeholder="حداقل ۸ کاراکتر"
          autoComplete="new-password"
          dir="ltr"
          required
          action={
            <PasswordAction
              visible={showPassword}
              onToggle={() => setShowPassword((current) => !current)}
              label={showPassword ? "پنهان کردن رمز عبور" : "نمایش رمز عبور"}
            />
          }
        />
        <AuthField
          id="reset-confirm-password"
          label="تکرار رمز عبور"
          value={confirmPassword}
          onChange={(value) => {
            setConfirmPassword(value);
            clearError("confirmPassword");
          }}
          error={errors.confirmPassword}
          type={showConfirmPassword ? "text" : "password"}
          placeholder="رمز عبور را دوباره وارد کنید"
          autoComplete="new-password"
          dir="ltr"
          required
          action={
            <PasswordAction
              visible={showConfirmPassword}
              onToggle={() => setShowConfirmPassword((current) => !current)}
              label={
                showConfirmPassword
                  ? "پنهان کردن تکرار رمز عبور"
                  : "نمایش تکرار رمز عبور"
              }
            />
          }
        />
        <p className="auth-demo-note">
          رمز فقط برای اعتبارسنجی این فرم استفاده می‌شود و ذخیره نخواهد شد.
        </p>
        <AuthSubmit loading={loading} label={authCopy.reset.button} />
        <p className="auth-switch">
          <Link href="/login">بازگشت به ورود</Link>
        </p>
      </form>
    );
  }

  return (
    <main className={`auth-page auth-${mode}`} data-auth-route={mode}>
      <aside className="auth-editorial" dir="rtl">
        <Link className="auth-logo" href="/" dir="ltr">
          GRAMISS
        </Link>
        <h2>خرید بهتر، با تصمیم آگاهانه‌تر آغاز می‌شود.</h2>
        <p>
          حساب کاربری شما مسیر ذخیره محصولات، پیگیری سفارش‌ها و دریافت
          پیشنهادهای شخصی را ساده می‌کند.
        </p>
        <AuthArtwork mode={mode} />
      </aside>
      <section className="auth-form-panel" aria-labelledby="auth-title">
        <Link className="auth-mobile-logo" href="/" dir="ltr">
          GRAMISS
        </Link>
        <div className="auth-form-heading">
          <h1 id="auth-title">{authCopy[mode].title}</h1>
          <p>{authCopy[mode].description}</p>
        </div>
        {mode === "login"
          ? renderLogin()
          : mode === "register"
            ? renderRegister()
            : mode === "forgot"
              ? renderForgot()
              : mode === "verify"
                ? renderVerify()
                : renderReset()}
        <div className="auth-security-note">
          <ShieldCheck aria-hidden="true" size={17} strokeWidth={1.8} />
          <span>نسخه نمایشی — بدون ایجاد حساب یا تراکنش واقعی</span>
        </div>
      </section>
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status">
        {toast}
      </div>
    </main>
  );
}

function AuthSubmit({ loading, label }: { loading: boolean; label: string }) {
  return (
    <button className="auth-submit" type="submit" disabled={loading}>
      {loading ? (
        <>
          <span className="auth-spinner" aria-hidden="true" />
          در حال بررسی...
        </>
      ) : (
        label
      )}
    </button>
  );
}
