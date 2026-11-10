"""Follow-up / maintenance / review — decide only."""

from __future__ import annotations

from typing import Any

from app.agents.decisions.types import (
    MaintenanceReminderDecision,
    ReviewRequestDecision,
)
from app.plugins.advisor.models import AdvisorContext


class AdvisorFollowUpService:
    def generate_follow_up(self, ctx: AdvisorContext) -> list[Any]:
        # Prefer maintenance reminders from revenue opportunities / metadata
        decisions: list[Any] = []
        reminders = list((ctx.metadata or {}).get("maintenance_reminders") or [])
        for rem in reminders[:2]:
            service = str(rem.get("service") or "service")
            due = rem.get("due_mileage")
            decisions.append(
                MaintenanceReminderDecision(
                    customer_id=ctx.customer_id,
                    vehicle_id=ctx.vehicle_id,
                    service=service,
                    due_mileage=str(due) if due is not None else None,
                    message_body=(
                        f"Напоминаем: возможно, пора выполнить {service.replace('_', ' ')}"
                        + (f' при пробеге около {due} миль' if due else "")
                        + '. Ответьте, чтобы выбрать удобное время.'
                    ),
                    channel=ctx.channel or "sms",
                    confidence=0.7,
                    rationale='Напоминание об обслуживании по рекомендации консультанта',
                )
            )
        intent = (ctx.intent or "").lower()
        if intent in {"thank_you", "completed", "pickup"} or (
            ctx.inbound_text and "thank" in ctx.inbound_text.lower()
        ):
            decisions.append(
                ReviewRequestDecision(
                    customer_id=ctx.customer_id,
                    channel=ctx.channel or "sms",
                    message_body=(
                        'Спасибо за визит! Уделите полминуты отзыву — он поможет другим водителям найти надёжный автосервис.'
                    ),
                    confidence=0.6,
                    rationale="Post-service review request",
                )
            )
        return decisions

    def generate_maintenance_reminder(
        self, ctx: AdvisorContext, *, service: str = "service", due_mileage: str | None = None
    ) -> list[Any]:
        return [
            MaintenanceReminderDecision(
                customer_id=ctx.customer_id,
                vehicle_id=ctx.vehicle_id,
                service=service,
                due_mileage=due_mileage,
                message_body=(
                    f"Напоминание: скоро потребуется {service.replace('_', ' ')}"
                    + (f' при пробеге около {due_mileage} миль' if due_mileage else "")
                    + '. Записать вас?'
                ),
                channel=ctx.channel or "sms",
                confidence=0.75,
                rationale='Создание напоминания об обслуживании',
            )
        ]

    def generate_review_request(self, ctx: AdvisorContext) -> list[Any]:
        return [
            ReviewRequestDecision(
                customer_id=ctx.customer_id,
                channel=ctx.channel or "sms",
                message_body=(
                    'Будем рады вашему отзыву! Он поможет нам стать лучше.'
                ),
                confidence=0.7,
                rationale='Создание запроса отзыва',
            )
        ]
