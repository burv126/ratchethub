"use client";
import { ruError } from "@/lib/ru-errors";

import { FormEvent, Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AdminLoginLockoutError, loadSession, MfaRequiredError } from "@/lib/api";
import { getAdminSystem, lockAdmin, unlockAdmin } from "@/lib/admin";
import { useAuth } from "@/lib/auth";
import { PasswordField } from "@/components/PasswordField";

function safeAdminNextPath(raw: string | null): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return "/admin";
  if (raw === "/admin/login" || raw.startsWith("/admin/login/")) return "/admin";
  if (raw === "/admin" || raw.startsWith("/admin/")) return raw;
  return "/admin";
}

function formatCountdown(totalSeconds: number): string {
  const seconds = Math.max(0, Math.ceil(totalSeconds));
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

const ADMIN_LOGIN_LOCKOUT_KEY = "asa.admin.login.lockout.endsAt";

function readPersistedLockoutEndsAt(): number | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(ADMIN_LOGIN_LOCKOUT_KEY);
    if (!raw) return null;
    const endsAt = Number(raw);
    if (!Number.isFinite(endsAt) || endsAt <= Date.now()) {
      sessionStorage.removeItem(ADMIN_LOGIN_LOCKOUT_KEY);
      return null;
    }
    return endsAt;
  } catch {
    return null;
  }
}

function persistLockoutEndsAt(endsAt: number | null): void {
  if (typeof window === "undefined") return;
  try {
    if (endsAt == null || endsAt <= Date.now()) {
      sessionStorage.removeItem(ADMIN_LOGIN_LOCKOUT_KEY);
      return;
    }
    sessionStorage.setItem(ADMIN_LOGIN_LOCKOUT_KEY, String(endsAt));
  } catch {
    // Ignore quota / private-mode failures; in-memory countdown still works.
  }
}

function AdminLoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = useMemo(() => safeAdminNextPath(searchParams.get("next")), [searchParams]);
  const { adminLogin, completeMfa, session, loading, logout } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  // Start null on SSR + first client paint; hydrate from sessionStorage after mount.
  const [lockoutEndsAt, setLockoutEndsAt] = useState<number | null>(null);
  const [lockoutRemaining, setLockoutRemaining] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Opening /admin/login always requires credentials (no auto-bounce).
    lockAdmin();
  }, []);

  useEffect(() => {
    const endsAt = readPersistedLockoutEndsAt();
    if (endsAt == null) return;
    setLockoutEndsAt(endsAt);
    setError("Слишком много неудачных попыток. Повторите позже.");
  }, []);

  useEffect(() => {
    // Drop shop sessions so they cannot piggy-back into admin after login UI.
    if (loading) return;
    if (session && session.accountType !== "platform_admin") {
      void logout();
    }
  }, [loading, session, logout]);

  useEffect(() => {
    if (lockoutEndsAt == null) {
      setLockoutRemaining(0);
      persistLockoutEndsAt(null);
      return;
    }
    persistLockoutEndsAt(lockoutEndsAt);
    const tick = () => {
      const remaining = Math.max(0, Math.ceil((lockoutEndsAt - Date.now()) / 1000));
      setLockoutRemaining(remaining);
      if (remaining <= 0) {
        setLockoutEndsAt(null);
        setError(null);
        persistLockoutEndsAt(null);
      }
    };
    tick();
    const id = window.setInterval(tick, 250);
    return () => window.clearInterval(id);
  }, [lockoutEndsAt]);

  async function enterAdminConsole() {
    const accessToken = loadSession()?.accessToken;
    if (!accessToken) {
      throw new Error("После входа отсутствует сессия администратора");
    }
    try {
      await getAdminSystem(accessToken);
    } catch (err) {
      lockAdmin();
      await logout();
      const msg = err instanceof Error ? err.message : "Доступ администратора запрещён";
      if (/platform admin required/i.test(msg) || /403/.test(msg)) {
        throw new Error(
          "Эта учётная запись не является администратором платформы. Войдите с разрешённым именем администратора.",
        );
      }
      throw err instanceof Error ? err : new Error("Доступ администратора запрещён");
    }
    unlockAdmin();
    router.replace(nextPath);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (lockoutRemaining > 0) {
      setError("Слишком много неудачных попыток. Повторите позже.");
      return;
    }

    if (mfaToken) {
      if (!mfaCode.trim()) {
        setError("Введите код из приложения-аутентификатора");
        return;
      }
    } else {
      const normalizedCheck = username.trim();
      if (!normalizedCheck) {
        setError("Введите имя администратора");
        return;
      }
      if (!password) {
        setError("Введите пароль");
        return;
      }
    }

    setSubmitting(true);
    try {
      const normalized = username.trim().toLowerCase();
      if (mfaToken) {
        await completeMfa({ mfaToken, code: mfaCode.trim() });
        await enterAdminConsole();
        return;
      }
      await adminLogin({ username: normalized, password });
      setLockoutEndsAt(null);
      persistLockoutEndsAt(null);
      await enterAdminConsole();
    } catch (err) {
      if (err instanceof MfaRequiredError) {
        setMfaToken(err.mfaToken);
        setError(null);
      } else if (err instanceof AdminLoginLockoutError) {
        lockAdmin();
        const endsAt = Date.now() + err.retryAfterSeconds * 1000;
        setLockoutEndsAt(endsAt);
        persistLockoutEndsAt(endsAt);
        setError(err.message || "Слишком много неудачных попыток. Повторите позже.");
      } else {
        lockAdmin();
        setError(err instanceof Error ? err.message : "Не удалось войти");
      }
    } finally {
      setSubmitting(false);
    }
  }

  const locked = lockoutRemaining > 0;

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10 sm:py-14">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_0%,var(--accent-soft),transparent_45%),radial-gradient(ellipse_at_90%_10%,rgba(0,0,0,0.04),transparent_40%),linear-gradient(180deg,#f7f7f7,var(--background))]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 top-10 h-64 w-64 rounded-full bg-[var(--accent-glow)] blur-3xl"
      />
      <div className="auth-form-motion relative w-full max-w-md overflow-hidden rounded-[1.5rem] border border-[var(--line)] bg-[linear-gradient(145deg,rgba(255,255,255,0.98)_0%,rgba(255,255,255,0.92)_100%)] p-6 shadow-[var(--shadow-soft)] sm:p-8">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 left-0 w-[3px] bg-[linear-gradient(180deg,transparent_6%,var(--accent)_48%,transparent_94%)]"
        />
        <div className="relative pl-1">
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
            Платформа
          </p>
          <h1 className="font-display mt-2 text-2xl font-semibold tracking-tight sm:text-[1.85rem]">
            {mfaToken ? "Двухфакторная аутентификация" : "Вход администратора"}
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
            {mfaToken
              ? "Введите 6-значный код из аутентификатора или одноразовый резервный код."
              : "Войдите в консоль администратора. Регистр имени не учитывается."}
          </p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4" autoComplete="off">
            {!mfaToken ? (
              <>
                <label className="block space-y-1.5">
                  <span className="text-sm font-medium">
                    Имя администратора <span className="text-red-600">*</span>
                  </span>
                  <input
                    type="text"
                    name="asa-admin-username"
                    autoComplete="off"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    aria-required="true"
                    minLength={3}
                    maxLength={32}
                    disabled={locked}
                    className="w-full rounded-xl border border-[var(--line)] bg-white/90 px-3 py-2.5 text-sm outline-none ring-[var(--accent)] focus:ring-2 disabled:opacity-60"
                  />
                </label>
                <PasswordField
                  label="Пароль"
                  name="asa-admin-password"
                  value={password}
                  onChange={setPassword}
                  required
                  minLength={1}
                  autoComplete="off"
                  disabled={locked}
                />
              </>
            ) : (
              <label className="block space-y-1.5">
                <span className="text-sm font-medium">Код аутентификатора</span>
                <input
                  type="text"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  required
                  className="w-full rounded-xl border border-[var(--line)] bg-white/90 px-3 py-2.5 text-sm outline-none ring-[var(--accent)] focus:ring-2"
                />
              </label>
            )}

            {(error || locked) && (
              <p
                className="rounded-xl border border-red-200/80 bg-red-50/90 px-3 py-2 text-sm text-red-700"
                role="alert"
              >
                {locked
                  ? `Слишком много неудачных попыток. Повторите через ${formatCountdown(lockoutRemaining)}`
                  : ruError(error)}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting || loading || locked}
              className="btn-primary w-full disabled:opacity-60"
            >
              {locked
                ? `Повторите через ${formatCountdown(lockoutRemaining)}`
                : submitting
                  ? "Подождите…"
                  : mfaToken
                    ? "Подтвердить"
                    : "Войти как администратор"}
            </button>
            {mfaToken && (
              <button
                type="button"
                onClick={() => {
                  setMfaToken(null);
                  setMfaCode("");
                }}
                className="w-full text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
              >
                Назад
              </button>
            )}
          </form>
        </div>
      </div>
    </main>
  );
}

export default function AdminLoginPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center text-sm text-[var(--muted)]">
          Загрузка входа для администратора…
        </main>
      }
    >
      <AdminLoginForm />
    </Suspense>
  );
}
