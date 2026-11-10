"use client";
import { ruError } from "@/lib/ru-errors";


import { ruLabel } from "@/lib/ru";

import { useCallback, useEffect, useState } from "react";
import { AdminPageHeader, AdminShell, LiveBadge, Panel, Stat } from "@/components/admin/AdminShell";
import { getAdminUsage, statusTone, streamAdminUsage, UsageResponse } from "@/lib/admin";

const POLL_MS = 3000;

export default function AdminTokensPage() {
  return (
    <AdminShell>
      {({ accessToken }) => <TokensBody accessToken={accessToken} />}
    </AdminShell>
  );
}

function TokensBody({ accessToken }: { accessToken: string }) {
  const [data, setData] = useState<UsageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);
  const [live, setLive] = useState(false);

  const applyData = useCallback((next: UsageResponse) => {
    setData((prev) => {
      if (prev?.generated_at && next.generated_at) {
        const prevTs = Date.parse(prev.generated_at);
        const nextTs = Date.parse(next.generated_at);
        if (Number.isFinite(prevTs) && Number.isFinite(nextTs) && nextTs < prevTs) {
          return prev;
        }
      }
      return next;
    });
    setLive(true);
    setError(null);
  }, []);

  const load = useCallback(
    async (quiet = false) => {
      if (!quiet) {
        setBusy(true);
        setError(null);
      }
      try {
        applyData(await getAdminUsage(accessToken));
      } catch (err) {
        if (!quiet) {
          setLive(false);
          setError(err instanceof Error ? err.message : "Не удалось загрузить использование");
        } else {
          setLive(false);
        }
      } finally {
        if (!quiet) setBusy(false);
      }
    },
    [accessToken, applyData],
  );

  useEffect(() => {
    void load(false);
    const id = window.setInterval(() => void load(true), POLL_MS);
    const onVis = () => {
      if (document.visibilityState === "visible") void load(true);
    };
    const onRefresh = () => void load(true);
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("focus", onRefresh);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("focus", onRefresh);
    };
  }, [load]);

  useEffect(() => {
    const stop = streamAdminUsage(
      accessToken,
      (next) => applyData(next),
      () => setLive(false),
    );
    return stop;
  }, [accessToken, applyData]);

  if (error && !data) return <p className="text-sm text-red-700">{ruError(error)}</p>;
  if (!data) return <p className="text-sm text-[var(--muted)]">{busy ? "Загрузка…" : "Нет данных"}</p>;

  const sms = data.sms_runtime;
  const voice = data.voice_runtime;

  return (
    <>
      <AdminPageHeader
        title="Токены"
        description={`Суммарное использование за текущий период · обновлено ${
          data.generated_at ? new Date(data.generated_at).toLocaleString("ru-RU") : "—"
        }`}
        action={<LiveBadge live={live} />}
      />

      <section className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Период" value={data.period} />
        <Stat label="Звонки ИИ (токены)" value={String(data.totals.ai_calls)} />
        <Stat label="Использование SMS (квота)" value={String(data.totals.sms)} />
        <Stat label="Учтённые автосервисы" value={String(data.shops.length)} />
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Входящие SMS"
          value={String(sms.inbound_received ?? 0)}
          hint="Из базы данных"
        />
        <Stat label="Исходящие SMS" value={String(sms.outbound_sent ?? 0)} />
        <Stat
          label="Начатые звонки"
          value={String(voice.calls_started ?? 0)}
          hint="Из базы данных"
        />
        <Stat label="Завершённые звонки" value={String(voice.calls_completed ?? 0)} />
      </section>

      <Panel title="Использование ИИ и SMS по автосервисам">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-[var(--line)] bg-[var(--background)] text-[var(--muted)]">
              <tr>
                <th className="px-5 py-2 font-medium">Автосервис</th>
                <th className="px-5 py-2 font-medium">Тариф</th>
                <th className="px-5 py-2 font-medium">Статус</th>
                <th className="px-5 py-2 font-medium">Звонки ИИ</th>
                <th className="px-5 py-2 font-medium">SMS</th>
              </tr>
            </thead>
            <tbody>
              {data.shops.map((s) => (
                <tr key={s.shop_id} className="border-b border-[var(--line)]">
                  <td className="px-5 py-3">
                    <div className="font-medium">{s.shop_name}</div>
                    <div className="font-mono text-xs text-[var(--muted)]">{s.shop_slug}</div>
                  </td>
                  <td className="px-5 py-3">{ruLabel(s.plan_name)}</td>
                  <td className={`px-5 py-3 capitalize ${statusTone(s.status)}`}>{ruLabel(s.status)}</td>
                  <td className="px-5 py-3 font-medium">{s.ai_calls}</td>
                  <td className="px-5 py-3">{s.sms}</td>
                </tr>
              ))}
              {data.shops.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-[var(--muted)]">
                    За этот период использование не зарегистрировано.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}
