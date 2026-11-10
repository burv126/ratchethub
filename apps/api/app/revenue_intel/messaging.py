"""Recommended channel + message templates."""

from __future__ import annotations

from app.revenue_intel.enums import ContactChannel, OpportunityKind
from app.revenue_intel.models import CustomerSnapshot


def recommend_channel(customer: CustomerSnapshot, kind: OpportunityKind) -> ContactChannel:
    has_sms = bool(customer.phone)
    has_email = bool(customer.email)
    recent_sms = any(c.channel == "sms" for c in customer.communications[-5:])

    if kind == OpportunityKind.LOST_CUSTOMER:
        return ContactChannel.PHONE if has_sms else ContactChannel.EMAIL
    if kind in {OpportunityKind.BRAKES, OpportunityKind.BATTERY} and has_sms:
        return ContactChannel.SMS
    if recent_sms and has_sms:
        return ContactChannel.SMS
    if has_sms:
        return ContactChannel.SMS
    if has_email:
        return ContactChannel.EMAIL
    return ContactChannel.IN_APP


_TEMPLATES: dict[OpportunityKind, str] = {
    OpportunityKind.LOST_CUSTOMER: (
        'Здравствуйте, {name}! Будем рады снова видеть вас в автосервисе. Запишитесь на бесплатный комплексный осмотр на этой неделе — найдём время для вашего {vehicle}.'
    ),
    OpportunityKind.LIKELY_RETURN: (
        'Здравствуйте, {name}! Судя по истории визитов, вашему {vehicle} пора на проверку. Подобрать удобное время?'
    ),
    OpportunityKind.LIKELY_ACCEPT: (
        'Здравствуйте, {name}! Предыдущая смета на {service} для вашего {vehicle} ещё актуальна. Ответьте YES для записи.'
    ),
    OpportunityKind.MAINTENANCE_OVERDUE: (
        'Здравствуйте, {name}! Для вашего {vehicle} просрочено обслуживание: {service}. Запись сейчас поможет избежать более серьёзного ремонта.'
    ),
    OpportunityKind.BATTERY: (
        'Здравствуйте, {name}! В холодный сезон повышается риск отказа аккумулятора. Рекомендуем проверить или заменить аккумулятор вашего {vehicle}.'
    ),
    OpportunityKind.BRAKES: (
        'Здравствуйте, {name}! По пробегу и истории вашему {vehicle} пора обслужить тормоза. Безопасность прежде всего — записать на осмотр?'
    ),
    OpportunityKind.OIL_CHANGE: (
        'Здравствуйте, {name}! Вашему {vehicle} пора заменить масло. На этой неделе есть свободное время — ответьте для записи.'
    ),
    OpportunityKind.TIRES: (
        'Здравствуйте, {name}! По износу и пробегу пора проверить шины вашего {vehicle}. Уточните текущие предложения.'
    ),
    OpportunityKind.ALIGNMENT: (
        'Здравствуйте, {name}! Регулировка углов установки колёс вашего {vehicle} поможет продлить срок службы шин и улучшить управляемость. Запишитесь на удобное время.'
    ),
    OpportunityKind.FLUIDS: (
        'Здравствуйте, {name}! Вашему {vehicle} пора заменить технические жидкости. Своевременная замена защищает основные узлы.'
    ),
    OpportunityKind.DECLINED_ESTIMATE: (
        'Здравствуйте, {name}! Хотим вернуться к смете на {service} для вашего {vehicle}. Можем подобрать варианты под ваш бюджет.'
    ),
}


def recommend_message(
    *,
    kind: OpportunityKind,
    customer: CustomerSnapshot,
    vehicle_label: str | None,
    service: str | None = None,
) -> str:
    tmpl = _TEMPLATES.get(kind, "Здравствуйте, {name}! Для вашего {vehicle} есть рекомендуемая услуга.")
    return tmpl.format(
        name=customer.name.split()[0] if customer.name else "there",
        vehicle=vehicle_label or "vehicle",
        service=service or "service",
    )
