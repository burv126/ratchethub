"use client";
import { ruError } from "@/lib/ru-errors";


import { ruLabel } from "@/lib/ru";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import {
  AnalyticsBenchmark,
  AnalyticsChart,
  AnalyticsDashboard,
  AnalyticsExport,
  AnalyticsForecast,
  AnalyticsKpi,
  AnalyticsReport,
  createAnalyticsExport,
  createAnalyticsReport,
  downloadAnalyticsExport,
  formatKpiValue,
  getAnalyticsDashboard,
  getAnalyticsMetrics,
  getReport,
  listAnalyticsExports,
  listAnalyticsReports,
  refreshAnalyticsDashboard,
} from "@/lib/analytics";

function MiniBars({ chart }: { chart: AnalyticsChart }) {
  const points = chart.points.slice(-14);
  const max = Math.max(...points.map((p) => p.value), 1);
  return (
    <div className="mt-3 flex h-24 items-end gap-1">
      {points.map((p) => (
        <div key={p.label} className="flex flex-1 flex-col items-center gap-1">
          <div
            className="w-full rounded-sm bg-[var(--accent)] opacity-80"
            style={{ height: `${Math.max(8, (p.value / max) * 100)}%` }}
            title={`${p.label}: ${p.value}`}
          />
        </div>
      ))}
    </div>
  );
}

function KpiCard({ kpi }: { kpi: AnalyticsKpi }) {
  return (
    <div className="rounded-md border border-[var(--line)] px-4 py-3">
      <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{kpi.label}</p>
      <p className="mt-1 text-xl font-semibold">{formatKpiValue(kpi)}</p>
      <p className="mt-1 text-xs text-[var(--muted)]">
        {kpi.delta_pct >= 0 ? "+" : ""}
        {kpi.delta_pct.toFixed(1)}% · {ruLabel(kpi.trend)}
        {kpi.vs_benchmark_pct != null && (
          <span>
            {" "}
            · к эталону {kpi.vs_benchmark_pct >= 0 ? "+" : ""}
            {kpi.vs_benchmark_pct.toFixed(1)}%
          </span>
        )}
      </p>
      {kpi.detail && <p className="mt-1 text-xs text-[var(--muted)]">{kpi.detail}</p>}
    </div>
  );
}

export default function AnalyticsPage() {
  const { session, loading: authLoading } = useAuth();
  const [tab, setTab] = useState<"dashboard" | "reports" | "exports">("dashboard");
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [exports, setExports] = useState<AnalyticsExport[]>([]);
  const [selectedReport, setSelectedReport] = useState<AnalyticsReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [reportType, setReportType] = useState("full");
  const [analyticsMetrics, setAnalyticsMetrics] = useState<Record<string, unknown> | null>(null);

  const loadDashboard = useCallback(async (force = false) => {
    const dash = force ? await refreshAnalyticsDashboard(30) : await getAnalyticsDashboard(force, 30);
    setData(dash);
  }, []);

  const loadLists = useCallback(async () => {
    const [r, e, m] = await Promise.all([
      listAnalyticsReports(),
      listAnalyticsExports(),
      getAnalyticsMetrics().catch(() => null),
    ]);
    setReports(r);
    setExports(e);
    setAnalyticsMetrics(m);
  }, []);

  useEffect(() => {
    if (authLoading || !session) return;
    void (async () => {
      try {
        await loadDashboard(true);
        await loadLists();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить аналитику");
      }
    })();
  }, [authLoading, session, loadDashboard, loadLists]);

  async function onRefresh() {
    setBusy(true);
    setError(null);
    try {
      await loadDashboard(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось обновить");
    } finally {
      setBusy(false);
    }
  }

  async function onCreateReport() {
    setBusy(true);
    setError(null);
    try {
      const report = await createAnalyticsReport({ report_type: reportType, period_days: 30 });
      setSelectedReport(report);
      await loadLists();
      setTab("reports");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сформировать отчёт");
    } finally {
      setBusy(false);
    }
  }

  async function onExport(format: "csv" | "json", reportId?: string) {
    setBusy(true);
    setError(null);
    try {
      const artifact = await createAnalyticsExport({
        format,
        period_days: 30,
        report_id: reportId,
      });
      await downloadAnalyticsExport(artifact.id, artifact.filename);
      await loadLists();
      setTab("exports");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось экспортировать");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="page-title">Аналитика</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Показатели, прогнозы, сравнения, отчёты и экспорт.
            {data && (
              <span className="ml-2 text-xs">
                · версия{data.version} · {data.period_start} → {data.period_end}
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(["dashboard", "reports", "exports"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`rounded-md border px-3 py-2 text-sm capitalize ${
                tab === t
                  ? "border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent)]"
                  : "border-[var(--line)] text-[var(--muted)]"
              }`}
            >
              {t}
            </button>
          ))}
          <button
            type="button"
            disabled={busy}
            onClick={() => void onRefresh()}
            className="rounded-md bg-[var(--accent)] px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {busy ? "Обработка…" : "Обновить"}
          </button>
        </div>
      </div>

      {error && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{ruError(error)}</p>
      )}

      {analyticsMetrics && (
        <p className="rounded-md border border-[var(--line)] px-3 py-2 text-xs text-[var(--muted)]">
          Метрики: {JSON.stringify(analyticsMetrics)}
        </p>
      )}

      {tab === "dashboard" && data && (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {data.kpis.map((kpi) => (
              <KpiCard key={kpi.id} kpi={kpi} />
            ))}
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            {data.charts.map((chart) => (
              <div key={chart.id} className="rounded-md border border-[var(--line)] p-4">
                <h2 className="text-sm font-medium">{chart.title}</h2>
                <MiniBars chart={chart} />
              </div>
            ))}
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-md border border-[var(--line)] p-4">
              <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Прогноз</h2>
              <ul className="mt-3 space-y-3">
                {data.forecasts.map((f: AnalyticsForecast) => (
                  <li key={f.kpi} className="text-sm">
                    <p className="font-medium capitalize">{f.kpi.replaceAll("_", " ")}</p>
                    <p className="text-xs text-[var(--muted)]">{f.summary}</p>
                    {f.points[0] && (
                      <p className="mt-1 text-xs">
                        Далее: {f.points[0].predicted.toLocaleString("ru-RU")} ({f.points[0].low}–{f.points[0].high})
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-md border border-[var(--line)] p-4">
              <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Сравнения</h2>
              <ul className="mt-3 space-y-2">
                {data.benchmarks.map((b: AnalyticsBenchmark) => (
                  <li
                    key={b.kpi}
                    className="flex items-center justify-between gap-2 border-b border-[var(--line)] pb-2 text-sm last:border-0"
                  >
                    <span>{b.label}</span>
                    <span className="text-xs text-[var(--muted)]">
                      {ruLabel(b.status)} · автосервис {b.shop_value.toFixed(2)} / среднее {b.industry_avg.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={busy}
              onClick={() => void onExport("csv")}
              className="rounded-md border border-[var(--line)] px-3 py-2 text-sm"
            >
              Экспорт панели в CSV
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void onExport("json")}
              className="rounded-md border border-[var(--line)] px-3 py-2 text-sm"
            >
              Экспорт панели в JSON
            </button>
          </div>
        </>
      )}

      {tab === "reports" && (
        <section className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <div className="space-y-3 rounded-md border border-[var(--line)] p-4">
            <h2 className="text-sm font-medium">Создать отчёт</h2>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full rounded-md border border-[var(--line)] bg-transparent px-3 py-2 text-sm"
            >
              {[
                "full",
                "executive_summary",
                "revenue",
                "retention",
                "marketing",
                "operations",
                "ai_performance",
              ].map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={busy}
              onClick={() => void onCreateReport()}
              className="w-full rounded-md bg-[var(--accent)] px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              Сформировать
            </button>
            <ul className="max-h-80 space-y-1 overflow-auto text-sm">
              {reports.map((r) => (
                <li key={r.id}>
                  <button
                    type="button"
                    className={`w-full rounded px-2 py-1.5 text-left ${
                      selectedReport?.id === r.id ? "bg-[var(--accent-soft)]" : "hover:bg-[var(--accent-soft)]"
                    }`}
                    onClick={() =>
                      void getReport(r.id)
                        .then(setSelectedReport)
                        .catch((err) => {
                          setSelectedReport(r);
                          setError(err instanceof Error ? err.message : "Не удалось открыть отчёт");
                        })
                    }
                  >
                    <span className="font-medium">{r.title}</span>
                    <span className="mt-0.5 block text-[11px] text-[var(--muted)]">
                      {new Date(r.generated_at).toLocaleString("ru-RU")}
                    </span>
                  </button>
                </li>
              ))}
              {!reports.length && <li className="text-xs text-[var(--muted)]">Отчётов пока нет</li>}
            </ul>
          </div>
          <div className="rounded-md border border-[var(--line)] p-4">
            {selectedReport ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <h2 className="text-lg font-medium">{selectedReport.title}</h2>
                    <p className="mt-1 text-sm text-[var(--muted)]">{selectedReport.summary}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="rounded border border-[var(--line)] px-2 py-1 text-xs"
                      onClick={() => void onExport("csv", selectedReport.id)}
                    >
                      Экспорт в CSV
                    </button>
                    <button
                      type="button"
                      className="rounded border border-[var(--line)] px-2 py-1 text-xs"
                      onClick={() => void onExport("json", selectedReport.id)}
                    >
                      Экспорт в JSON
                    </button>
                  </div>
                </div>
                {selectedReport.sections.map((s) => (
                  <div key={s.id}>
                    <h3 className="text-sm font-medium">{s.title}</h3>
                    <pre className="mt-2 whitespace-pre-wrap text-xs text-[var(--muted)]">{s.body}</pre>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--muted)]">Выберите или создайте отчёт</p>
            )}
          </div>
        </section>
      )}

      {tab === "exports" && (
        <section className="overflow-x-auto rounded-md border border-[var(--line)]">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-[var(--line)] text-xs uppercase text-[var(--muted)]">
              <tr>
                <th className="px-3 py-2">Имя файла</th>
                <th className="px-3 py-2">Формат</th>
                <th className="px-3 py-2">Строки</th>
                <th className="px-3 py-2">Создано</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {exports.map((ex) => (
                <tr key={ex.id} className="border-b border-[var(--line)] last:border-0">
                  <td className="px-3 py-2">{ex.filename}</td>
                  <td className="px-3 py-2 uppercase">{ex.format}</td>
                  <td className="px-3 py-2">{ex.row_count}</td>
                  <td className="px-3 py-2">{new Date(ex.created_at).toLocaleString("ru-RU")}</td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      className="text-xs text-[var(--accent)]"
                      onClick={() => void downloadAnalyticsExport(ex.id, ex.filename)}
                    >
                      Скачать
                    </button>
                  </td>
                </tr>
              ))}
              {!exports.length && (
                <tr>
                  <td colSpan={5} className="px-3 py-4 text-sm text-[var(--muted)]">
                    Экспорта пока нет — экспортируйте данные из панели или отчётов.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {exports[0]?.preview && (
            <pre className="max-h-48 overflow-auto border-t border-[var(--line)] p-3 text-[11px]">
              {exports[0].preview}
            </pre>
          )}
        </section>
      )}
    </div>
  );
}
