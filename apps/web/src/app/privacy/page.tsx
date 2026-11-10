import { BrandLogo } from "@/components/BrandLogo";

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
        <BrandLogo size={40} wordmarkClassName="text-2xl font-semibold tracking-tight" />
      <h1 className="font-display mt-10 text-3xl font-semibold tracking-tight sm:text-4xl">
        Политика конфиденциальности
      </h1>
      <p className="mt-2 text-sm text-[var(--muted)]">Последнее обновление: 29 июля 2026 г.</p>
      <div className="surface-panel mt-8 space-y-4 p-6 text-sm leading-relaxed text-[var(--muted)]">
        <p>
          АвтоЦентр обрабатывает данные автосервисов, клиентов, автомобилей и коммуникаций для работы платформы управления автосервисами с изоляцией данных.
        </p>
        <p>
          Владельцы могут экспортировать данные и удалить учётную запись автосервиса в разделе оплаты. По другим вопросам конфиденциальности обратитесь в поддержку.
        </p>
        <p>
          Мы используем идентификаторы входа (телефон/почта), учёт использования для ограничений тарифа и при настройке оператором — сторонние сервисы Twilio, OpenAI и Stripe.
        </p>
      </div>
    </main>
  );
}
