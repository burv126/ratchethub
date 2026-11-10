import { ruLabel } from "@/lib/ru";
import Link from "next/link";
import { BrandLogo } from "@/components/BrandLogo";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    blurb: "Пробный период 14 дней для независимых автосервисов",
    features: [
      "Живая очередь и расшифровка VIN",
      "Записи",
      "CRM клиентов",
      "Роли и разрешения команды",
      "Импорт CSV / данных",
      "10 звонков ИИ / мес.",
      "2 места",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    price: "$150",
    blurb: "Для растущих автосервисов",
    features: [
      "Живая очередь и расшифровка VIN",
      "Записи",
      "CRM клиентов",
      "Роли и разрешения команды",
      "Импорт CSV / данных",
      "150 звонков ИИ / мес.",
      "4 места",
    ],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "$400",
    blurb: "Филиалы и индивидуальные лимиты",
    features: [
      "Живая очередь и расшифровка VIN",
      "Записи",
      "CRM клиентов",
      "Роли и разрешения команды",
      "Импорт CSV / данных",
      "500 звонков ИИ / мес.",
      "10 мест",
    ],
  },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-white">
      <header className="site-nav">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <BrandLogo
            size={40}
            wordmarkClassName="text-2xl font-extrabold tracking-tight"
          />
          <div className="flex items-center gap-2 text-sm">
            <Link href="/?login=1" className="rounded-full px-3 py-2 text-[#5c5c5c] hover:text-black">
              Войти
            </Link>
            <Link href="/register" className="btn-primary py-2">
              Начать бесплатно
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
        <p className="section-label">Тарифы</p>
        <h1 className="font-display mt-4 max-w-3xl text-4xl font-extrabold tracking-tight sm:text-6xl">
          Всё необходимое для любого автосервиса.
        </h1>
        <p className="mt-5 max-w-2xl text-base text-[#5c5c5c]">
          Простые ежемесячные тарифы. После регистрации тариф можно повысить в разделе оплаты.
        </p>

        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`flex flex-col rounded-2xl border bg-white p-7 shadow-[0_20px_50px_-36px_rgba(0,0,0,0.35)] ${
                plan.id === "pro"
                  ? "border-[var(--accent)] ring-2 ring-[var(--accent)]/25"
                  : "border-black/8"
              }`}
            >
              <p className="text-sm font-semibold text-[var(--accent)]">{ruLabel(plan.name)}</p>
              <p className="font-display mt-3 text-5xl font-extrabold tracking-tight">
                {plan.price}
                <span className="text-base font-medium text-[#5c5c5c]">/мес.</span>
              </p>
              <p className="mt-3 text-sm text-[#5c5c5c]">{plan.blurb}</p>
              <ul className="mt-7 flex-1 space-y-3 text-sm text-[#5c5c5c]">
                {plan.features.map((f) => (
                  <li key={f} className="flex gap-2.5">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--accent)]" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/register"
                className={`mt-8 inline-flex w-full items-center justify-center rounded-full px-4 py-3 text-sm font-semibold ${
                  plan.id === "pro"
                    ? "bg-[var(--accent)] text-white"
                    : "bg-black text-white hover:bg-[#1a1a1a]"
                }`}
              >
                Начать
              </Link>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
