"use client";
import { ruError } from "@/lib/ru-errors";


import { ruLabel } from "@/lib/ru";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { AdminPageHeader, AdminShell, LiveBadge, Panel, Stat } from "@/components/admin/AdminShell";
import {
  activateAdminOrganizationMember,
  activateAdminShop,
  changeAdminOrganizationPlan,
  getAdminOrganizationDetail,
  initializeAdminOrganizationMemberPassword,
  OrganizationDetail,
  resetAdminOrganizationMemberPassword,
  statusTone,
  streamAdminOrganizationDetail,
  suspendAdminOrganizationMember,
  suspendAdminShop,
} from "@/lib/admin";

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("ru-RU");
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("ru-RU");
}

function OnlineDot({ online }: { online: boolean }) {
  return (
    <span
      className={`inline-flex h-2.5 w-2.5 shrink-0 rounded-full ${
        online ? "bg-emerald-500" : "bg-red-500"
      }`}
      title={online ? "В сети" : "Не в сети"}
      aria-label={online ? "В сети" : "Не в сети"}
    />
  );
}

export default function AdminShopDetailPage() {
  return (
    <AdminShell>
      {({ accessToken }) => <DetailBody accessToken={accessToken} />}
    </AdminShell>
  );
}

function DetailBody({ accessToken }: { accessToken: string }) {
  const params = useParams<{ shopId: string }>();
  const shopId = params.shopId;
  const [data, setData] = useState<OrganizationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [live, setLive] = useState(false);
  const [actionBusy, setActionBusy] = useState(false);
  const [memberBusyId, setMemberBusyId] = useState<string | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState("");

  const load = useCallback(async (quiet = false) => {
    if (!shopId) return;
    if (!quiet) {
      setBusy(true);
      setError(null);
    }
    try {
      const next = await getAdminOrganizationDetail(accessToken, shopId);
      setData(next);
      setSelectedPlanId((prev) => prev || next.shop.plan_id || "");
      setError(null);
      setLive(true);
    } catch (err) {
      if (!quiet) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить автосервис");
        setLive(false);
      } else {
        setLive(false);
      }
    } finally {
      if (!quiet) setBusy(false);
    }
  }, [accessToken, shopId]);

  useEffect(() => {
    void load(false);
    const id = window.setInterval(() => void load(true), 3000);
    const onVis = () => {
      if (document.visibilityState === "visible") void load(true);
    };
    const onRefresh = () => void load(true);
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("focus", onRefresh);
    window.addEventListener("admin:shops-refresh", onRefresh);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("focus", onRefresh);
      window.removeEventListener("admin:shops-refresh", onRefresh);
    };
  }, [load]);

  useEffect(() => {
    if (!shopId) return;
    setLive(false);
    const stop = streamAdminOrganizationDetail(
      accessToken,
      shopId,
      (next) => {
        setData(next);
        setSelectedPlanId((prev) => {
          if (!prev) return next.shop.plan_id || "";
          // Keep admin selection unless plan changed remotely to something else.
          if (prev === next.shop.plan_id) return prev;
          const stillExists = (next.plans ?? []).some((p) => p.id === prev);
          return stillExists ? prev : next.shop.plan_id || "";
        });
        setLive(true);
        setError(null);
      },
      () => setLive(false),
    );
    return stop;
  }, [accessToken, shopId]);

  async function onSuspend() {
    if (!shopId) return;
    setActionBusy(true);
    setError(null);
    setMessage(null);
    try {
      await suspendAdminShop(accessToken, shopId);
      setMessage("Работа автосервиса приостановлена.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось приостановить");
    } finally {
      setActionBusy(false);
    }
  }

  async function onActivate() {
    if (!shopId) return;
    setActionBusy(true);
    setError(null);
    setMessage(null);
    try {
      await activateAdminShop(accessToken, shopId);
      setMessage("Автосервис активирован.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось активировать");
    } finally {
      setActionBusy(false);
    }
  }

  async function onChangePlan() {
    if (!shopId || !selectedPlanId) return;
    if (selectedPlanId === data?.shop.plan_id) {
      setMessage("Этот тариф уже выбран.");
      return;
    }
    setActionBusy(true);
    setError(null);
    setMessage(null);
    try {
      const res = await changeAdminOrganizationPlan(accessToken, shopId, selectedPlanId);
      setMessage(`Тариф изменён на ${ruLabel(res.plan_name)}.`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось изменить тариф");
    } finally {
      setActionBusy(false);
    }
  }

  async function onMemberSuspend(userId: string) {
    if (!shopId) return;
    setMemberBusyId(userId);
    setError(null);
    setMessage(null);
    try {
      await suspendAdminOrganizationMember(accessToken, shopId, userId);
      setMessage("Учётная запись сотрудника приостановлена.");
      await load(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось приостановить сотрудника");
    } finally {
      setMemberBusyId(null);
    }
  }

  async function onMemberActivate(userId: string) {
    if (!shopId) return;
    setMemberBusyId(userId);
    setError(null);
    setMessage(null);
    try {
      await activateAdminOrganizationMember(accessToken, shopId, userId);
      setMessage("Учётная запись сотрудника активирована.");
      await load(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось активировать сотрудника");
    } finally {
      setMemberBusyId(null);
    }
  }

  async function onPasswordReset(userId: string, label: string) {
    if (!shopId) return;
    setMemberBusyId(userId);
    setError(null);
    setMessage(null);
    setTempPassword(null);
    try {
      const res = await resetAdminOrganizationMemberPassword(accessToken, shopId, userId);
      const via = res.channel === "email" ? "email" : "phone";
      setMessage(
        res.dev_token
          ? `Ссылка для сброса пароля отправлена: ${label} через ${via}. Dev token: ${res.dev_token}`
          : `Ссылка для сброса пароля отправлена: ${label} через ${via}.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сбросить пароль");
    } finally {
      setMemberBusyId(null);
    }
  }

  async function onPasswordInitialize(userId: string, label: string) {
    if (!shopId) return;
    if (
      !window.confirm(
        `Задать новый временный пароль для ${label}? Текущие сессии будут завершены.`,
      )
    ) {
      return;
    }
    setMemberBusyId(userId);
    setError(null);
    setMessage(null);
    setTempPassword(null);
    try {
      const res = await initializeAdminOrganizationMemberPassword(accessToken, shopId, userId);
      setTempPassword(res.temporary_password);
      setMessage(`Временный пароль задан для ${label}. Скопируйте сейчас — повторно он не появится.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось задать пароль");
    } finally {
      setMemberBusyId(null);
    }
  }

  if (error && !data) {
    return (
      <div className="space-y-3">
        <Link href="/admin/shops" className="text-sm text-[var(--muted)] hover:text-[var(--accent)]">
          ← Автосервисы
        </Link>
        <p className="text-sm text-red-700">{ruError(error)}</p>
      </div>
    );
  }

  if (!data) {
    return <p className="text-sm text-[var(--muted)]">{busy ? "Загрузка…" : "Нет данных"}</p>;
  }

  const shop = data.shop;
  const usage = data.usage;
  const plans = data.plans ?? [];

  return (
    <>
      <AdminPageHeader
        eyebrow="Сведения об автосервисе"
        title={shop.shop_name}
        description={shop.shop_slug}
        action={
          <div className="flex flex-wrap items-center gap-2">
            <LiveBadge live={live} />
            {shop.status === "suspended" ? (
              <button
                type="button"
                disabled={actionBusy}
                onClick={() => void onActivate()}
                className="rounded-xl border border-[var(--line)] bg-white/80 px-3 py-1.5 text-sm shadow-[var(--shadow-soft)] disabled:opacity-50"
              >
                Активировать автосервис
              </button>
            ) : (
              <button
                type="button"
                disabled={actionBusy || shop.status === "none"}
                onClick={() => void onSuspend()}
                className="rounded-xl border border-[var(--line)] bg-white/80 px-3 py-1.5 text-sm text-red-700 shadow-[var(--shadow-soft)] disabled:opacity-50"
              >
                Приостановить автосервис
              </button>
            )}
          </div>
        }
      />
      <Link
        href="/admin/shops"
        className="inline-flex text-sm text-[var(--muted)] transition-colors hover:text-[var(--accent)]"
      >
        ← К автосервисам
      </Link>

      {error && <p className="text-sm text-red-700">{ruError(error)}</p>}
      {message && <p className="text-sm text-emerald-700">{message}</p>}
      {tempPassword ? (
        <div className="flex flex-wrap items-center gap-3 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
          <span className="text-amber-900">Временный пароль:</span>
          <code className="rounded bg-white px-2 py-1 font-mono text-base text-amber-950">
            {tempPassword}
          </code>
          <button
            type="button"
            className="rounded-md border border-amber-400 px-2 py-1 text-xs text-amber-900"
            onClick={() => void navigator.clipboard.writeText(tempPassword)}
          >
            Копировать
          </button>
        </div>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Тариф" value={ruLabel(shop.plan_name)} />
        <Stat label="Статус" value={ruLabel(shop.status)} tone={statusTone(shop.status)} />
        <Stat label="Пользователи" value={String(shop.users ?? 0)} />
        <Stat label="Звонки ИИ" value={String(usage?.ai_calls ?? shop.ai_calls ?? 0)} />
      </section>

      <Panel title="Смена тарифа">
        <div className="flex flex-wrap items-end gap-3 px-5 py-4">
          <label className="min-w-[220px] flex-1 text-sm">
            <span className="mb-1 block text-[var(--muted)]">Тариф подписки</span>
            <select
              value={selectedPlanId}
              onChange={(e) => setSelectedPlanId(e.target.value)}
              disabled={actionBusy || plans.length === 0}
              className="w-full rounded-md border border-[var(--line)] bg-[var(--background)] px-3 py-2 text-sm"
            >
              {plans.length === 0 ? <option value="">Нет тарифов</option> : null}
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {ruLabel(p.name)} · ${(p.price_cents_monthly / 100).toFixed(0)}/мес. · ИИ {p.ai_calls_monthly} · SMS{" "}
                  {p.sms_monthly}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            disabled={actionBusy || !selectedPlanId || selectedPlanId === shop.plan_id}
            onClick={() => void onChangePlan()}
            className="rounded-md border border-[var(--line)] px-3 py-2 text-sm disabled:opacity-50"
          >
            Применить тариф
          </button>
        </div>
      </Panel>

      <Panel title={`Использование (${usage?.period ?? "текущий период"})`}>
        <dl className="grid gap-4 px-5 py-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <dt className="text-[var(--muted)]">Звонки ИИ (квота)</dt>
            <dd className="mt-0.5 font-medium">{usage?.ai_calls ?? shop.ai_calls ?? 0}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">SMS (квота)</dt>
            <dd className="mt-0.5 font-medium">{usage?.sms ?? shop.sms_usage ?? 0}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Запросы ИИ</dt>
            <dd className="mt-0.5 font-medium">{usage?.ai_requests ?? 0}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Входящие / исходящие токены</dt>
            <dd className="mt-0.5 font-medium">
              {usage?.input_tokens ?? 0} / {usage?.output_tokens ?? 0}
            </dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Учтённые SMS</dt>
            <dd className="mt-0.5 font-medium">{usage?.sms_count ?? 0}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Минуты звонков</dt>
            <dd className="mt-0.5 font-medium">{usage?.voice_minutes ?? 0}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Расчётная стоимость (USD)</dt>
            <dd className="mt-0.5 font-medium">
              {typeof usage?.estimated_cost_usd === "number"
                ? usage.estimated_cost_usd.toFixed(4)
                : "0.0000"}
            </dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">ID автосервиса</dt>
            <dd className="mt-0.5 break-all font-mono text-xs">{shop.shop_id}</dd>
          </div>
        </dl>
      </Panel>

      <Panel title="Сведения об автосервисе">
        <dl className="grid gap-4 px-5 py-4 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[var(--muted)]">Владелец</dt>
            <dd className="mt-0.5 font-medium">{shop.owner_name || "—"}</dd>
            {shop.owner_email ? <dd className="text-xs text-[var(--muted)]">{shop.owner_email}</dd> : null}
            {shop.owner_phone ? <dd className="text-xs text-[var(--muted)]">{shop.owner_phone}</dd> : null}
          </div>
          <div>
            <dt className="text-[var(--muted)]">В сети</dt>
            {shop.joined && shop.joined_by ? (
              <dd className="mt-0.5">
                <div className="inline-flex items-center gap-1.5 font-medium">
                  <OnlineDot online />
                  <span>{shop.joined_by}</span>
                </div>
                {shop.joined_by_role ? (
                  <div className="pl-[14px] text-xs capitalize text-[var(--muted)]">
                    {shop.joined_by_role}
                  </div>
                ) : null}
                {shop.joined_at ? (
                  <div className="pl-[14px] text-xs text-[var(--muted)]">
                    {formatDate(shop.joined_at)}
                  </div>
                ) : null}
              </dd>
            ) : (
              <dd className="mt-0.5 inline-flex items-center gap-1.5 text-[var(--muted)]">
                <OnlineDot online={false} />
                не в сети
              </dd>
            )}
          </div>
          <div>
            <dt className="text-[var(--muted)]">Создано</dt>
            <dd className="mt-0.5">{formatDate(shop.created_at)}</dd>
          </div>
          <div>
            <dt className="text-[var(--muted)]">Последняя активность</dt>
            <dd className="mt-0.5">{formatDateTime(shop.last_activity_at)}</dd>
          </div>
        </dl>
      </Panel>

      <Panel title={`Сотрудники (${data.members.length})`}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-[var(--line)] bg-[var(--background)] text-[var(--muted)]">
              <tr>
                <th className="px-5 py-2 font-medium">Имя</th>
                <th className="px-5 py-2 font-medium">Контакт</th>
                <th className="px-5 py-2 font-medium">Роль</th>
                <th className="px-5 py-2 font-medium">Активно</th>
                <th className="px-5 py-2 font-medium">Дата вступления</th>
                <th className="px-5 py-2 font-medium">Действия</th>
              </tr>
            </thead>
            <tbody>
              {data.members.map((m) => {
                const busyMember = memberBusyId === m.user_id;
                const label = m.full_name || m.email || m.phone || m.user_id;
                return (
                  <tr key={m.user_id} className="border-b border-[var(--line)]">
                    <td className="px-5 py-3 font-medium">{m.full_name}</td>
                    <td className="px-5 py-3">
                      <div>{m.email || "—"}</div>
                      {m.phone ? <div className="text-xs text-[var(--muted)]">{m.phone}</div> : null}
                    </td>
                    <td className="px-5 py-3 capitalize">{ruLabel(m.role)}</td>
                    <td className="px-5 py-3">{m.is_active ? "Да" : "Нет"}</td>
                    <td className="px-5 py-3 text-[var(--muted)]">{formatDate(m.joined_at)}</td>
                    <td className="px-5 py-3">
                      <div className="flex flex-wrap gap-2">
                        {m.is_active ? (
                          <button
                            type="button"
                            disabled={busyMember}
                            onClick={() => void onMemberSuspend(m.user_id)}
                            className="rounded-md border border-[var(--line)] px-2 py-1 text-xs text-red-700 disabled:opacity-50"
                          >
                            Приостановить
                          </button>
                        ) : (
                          <button
                            type="button"
                            disabled={busyMember}
                            onClick={() => void onMemberActivate(m.user_id)}
                            className="rounded-md border border-[var(--line)] px-2 py-1 text-xs disabled:opacity-50"
                          >
                            Активировать
                          </button>
                        )}
                        <button
                          type="button"
                          disabled={busyMember || !m.is_active}
                          onClick={() => void onPasswordInitialize(m.user_id, label)}
                          className="rounded-md border border-[var(--line)] px-2 py-1 text-xs disabled:opacity-50"
                          title="Задать новый временный пароль"
                        >
                          Задать пароль
                        </button>
                        <button
                          type="button"
                          disabled={busyMember || !m.is_active || (!m.email && !m.phone)}
                          onClick={() => void onPasswordReset(m.user_id, label)}
                          className="rounded-md border border-[var(--line)] px-2 py-1 text-xs disabled:opacity-50"
                          title={!m.email && !m.phone ? "Нет почты и телефона" : "Отправить ссылку для сброса пароля"}
                        >
                          Ссылка для сброса
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {data.members.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-[var(--muted)]">
                    Нет сотрудников.
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
