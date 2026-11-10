"use client";
import { ruError } from "@/lib/ru-errors";


import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BrandLogo } from "@/components/BrandLogo";
import { PasswordField } from "@/components/PasswordField";
import { getApiUrl } from "@/lib/api";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    setToken(q.get("token") || "");
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${getApiUrl()}/v1/auth/password-reset/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail || res.statusText);
      router.replace("/?login=1");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сбросить пароль");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center px-4 py-10">
      <div className="surface-panel w-full max-w-md p-6 sm:p-8">
        <BrandLogo
          size={40}
          wordmarkClassName="text-2xl font-semibold tracking-tight text-[var(--ink)]"
        />
        <h1 className="font-display mt-5 text-2xl font-semibold tracking-tight">Сбросить пароль</h1>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <PasswordField
            label="Новый пароль"
            value={password}
            onChange={setPassword}
            required
            minLength={8}
            autoComplete="new-password"
          />
          {error && <p className="text-sm text-red-700">{ruError(error)}</p>}
          <button
            type="submit"
            disabled={busy || !token}
            className="btn-primary w-full disabled:opacity-60"
          >
            {busy ? "Сохранение…" : "Обновить пароль"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-[var(--muted)]">
          <Link href="/?login=1" className="text-[var(--accent)]">
            Вернуться к входу
          </Link>
        </p>
      </div>
    </main>
  );
}
