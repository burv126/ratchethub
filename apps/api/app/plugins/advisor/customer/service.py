"""Customer analysis — decide only (reads CRM via capabilities / local context)."""

from __future__ import annotations

from typing import Any

from app.agents.decisions.types import CustomerCommunicationDecision, RetentionDecision
from app.plugins.advisor.models import AdvisorContext


class AdvisorCustomerService:
    def analyze(self, ctx: AdvisorContext) -> list[Any]:
        decisions: list[Any] = []
        name = (ctx.customer or {}).get("name") or "there"
        if ctx.customer_id is None and ctx.inbound_text:
            # Reception: recommend communication welcome; CRM create handled elsewhere
            decisions.append(
                CustomerCommunicationDecision(
                    customer_id=None,
                    conversation_id=_conv_uuid(ctx),
                    channel=ctx.channel or "sms",
                    body=f'Здравствуйте, {name}! Спасибо за обращение. Консультант рассматривает ваш запрос.',
                    intent=ctx.intent,
                    rationale='Приём клиента — профиль пока не привязан',
                )
            )
        risk = float((ctx.metadata or {}).get("lost_customer_risk") or 0.0)
        if risk >= 0.5 and ctx.customer_id is not None:
            decisions.append(
                RetentionDecision(
                    customer_id=ctx.customer_id,
                    risk_score=risk,
                    plan="Win-back outreach with complimentary inspection offer",
                    actions=["send_retention_message", "flag_high_value" if risk >= 0.7 else "follow_up"],
                    suggested_offer='Бесплатный комплексный осмотр',
                    priority="urgent" if risk >= 0.75 else "high",
                    rationale='Повышенный риск ухода клиента',
                )
            )
        return decisions


def _conv_uuid(ctx: AdvisorContext):
    from uuid import UUID

    if not ctx.conversation_id:
        return None
    try:
        return UUID(str(ctx.conversation_id))
    except (ValueError, TypeError):
        return None
