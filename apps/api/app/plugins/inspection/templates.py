"""Customer communication templates for inspection outcomes."""

from __future__ import annotations

from typing import Any


TEMPLATES: dict[str, str] = {
    "safety_warning": (
        'Предупреждение о безопасности вашего {vehicle}: выявлено {issue}. Устраните проблему до длительных поездок. Ответьте YES для согласования ремонта (~${amount}).'
    ),
    "recommended_repair": (
        'По результатам осмотра вашего {vehicle} рекомендуем: {issue}. Ориентировочная стоимость ~${amount}. Ответьте YES для согласования или ASK для уточнения.'
    ),
    "optional_repair": (
        'Необязательное улучшение для вашего {vehicle}: {issue}. Несрочно, стоимость ~${amount}. Запишем в удобное время.'
    ),
    "maintenance_reminder": (
        'Обслуживание вашего {vehicle}: {issue}. Своевременные работы помогут избежать серьёзного ремонта. Стоимость ~${amount}.'
    ),
    "approval_request": (
        'Согласуйте ремонт вашего {vehicle} по результатам осмотра: {services}. Смета ~${amount}. Ответьте YES для согласования, NO для отказа или CALL для звонка.'
    ),
    "follow_up": (
        'По результатам осмотра вашего {vehicle} остаётся нерешённый вопрос: {issue}. Поможем, когда вам будет удобно. Стоимость ~${amount}.'
    ),
}


def render_template(name: str, **kwargs: Any) -> str:
    template = TEMPLATES.get(name) or TEMPLATES["recommended_repair"]
    defaults = {
        "vehicle": "vehicle",
        "issue": "an item needing attention",
        "amount": "0.00",
        "services": "recommended services",
    }
    defaults.update({k: (str(v) if v is not None else defaults.get(k, "")) for k, v in kwargs.items()})
    try:
        return template.format(**defaults)
    except KeyError:
        return template
