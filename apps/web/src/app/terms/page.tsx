import { BrandLogo } from "@/components/BrandLogo";

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
        <BrandLogo size={40} wordmarkClassName="text-2xl font-semibold tracking-tight" />
      <h1 className="font-display mt-10 text-3xl font-semibold tracking-tight sm:text-4xl">
        Условия использования
      </h1>
      <p className="mt-2 text-sm text-[var(--muted)]">Последнее обновление: 29 июля 2026 г.</p>
      <div className="surface-panel mt-8 space-y-4 p-6 text-sm leading-relaxed text-[var(--muted)]">
        <p>
          Создавая учётную запись автосервиса, вы соглашаетесь использовать АвтоЦентр только для законной деятельности по обслуживанию автомобилей и обеспечивать безопасность учётных данных.
        </p>
        <p>
          Платные тарифы продлеваются ежемесячно до отмены. При превышении квот использование может быть заблокировано до повышения тарифа. Тариф «Бесплатный» включает пробный период.
        </p>
        <p>
          Сервис предоставляется «как есть». Операторы могут приостановить работу автосервисов, злоупотребляющих SMS, ИИ или платёжными системами.
        </p>
      </div>
    </main>
  );
}
