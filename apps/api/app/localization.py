"""Russian display labels; persisted status codes remain unchanged."""

_STATUS_LABELS = {
    "booked": "записано",
    "confirmed": "подтверждено",
    "in_progress": "в работе",
    "completed": "завершено",
    "closed": "закрыто",
    "cancelled": "отменено",
    "canceled": "отменено",
    "rescheduled": "перенесено",
}


def status_label(value: str) -> str:
    return _STATUS_LABELS.get(value, value)


_KPI_LABELS = {
    "revenue": "Выручка", "retention": "Удержание клиентов",
    "average_repair_order": "Средний заказ-наряд",
    "customer_lifetime_value": "Пожизненная ценность клиента",
    "appointment_conversion": "Конверсия в запись", "marketing_roi": "Окупаемость маркетинга",
    "mechanic_productivity": "Производительность механиков", "ai_success_rate": "Успешность ИИ",
}


def kpi_label(value: str) -> str:
    return _KPI_LABELS.get(value, value)


def benchmark_label(value: str) -> str:
    return {"ahead": "выше отрасли", "behind": "ниже отрасли", "on_par": "на уровне отрасли"}.get(value, value)
