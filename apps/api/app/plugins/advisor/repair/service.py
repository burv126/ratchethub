"""Repair recommendation / status — decide only."""

from __future__ import annotations

from typing import Any

from app.agents.decisions.types import RepairStatusDecision
from app.plugins.advisor.models import AdvisorContext


class AdvisorRepairService:
    def generate_update(self, ctx: AdvisorContext, *, status: str | None = None) -> list[Any]:
        text = (ctx.inbound_text or "").lower()
        st = status
        if st is None:
            if any(w in text for w in ("ready", "done", "finished", "complete")):
                st = "ready"
            elif any(w in text for w in ("status", "update", "progress", "where is")):
                st = "in_progress"
            else:
                return []
        messages = {
            "received": 'Мы приняли автомобиль и начали оформление.',
            "diagnosing": 'Наши специалисты проводят диагностику автомобиля.',
            "awaiting_parts": 'Ожидаем запчасти и сообщим, когда работы возобновятся.',
            "in_progress": 'Ремонт выполняется — сообщим, когда автомобиль будет готов.',
            "ready": 'Хорошие новости — автомобиль готов к выдаче.',
            "completed": 'Ремонт завершён. Спасибо, что выбрали нас.',
        }
        body = messages.get(st, messages["in_progress"])
        return [
            RepairStatusDecision(
                customer_id=ctx.customer_id,
                vehicle_id=ctx.vehicle_id,
                status=st,  # type: ignore[arg-type]
                message_body=body,
                channel=ctx.channel or "sms",
                advisor_notes=f'Решение об обновлении статуса: {st}',
                confidence=0.75,
                rationale='Помощь со статусом ремонта',
            )
        ]
