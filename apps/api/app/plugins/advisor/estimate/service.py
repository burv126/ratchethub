"""Estimate assistance — decide only (explanations / approval requests)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.agents.decisions.types import (
    ApprovalRequestDecision,
    EstimateExplanationDecision,
    RepairRecommendationDecision,
)
from app.plugins.advisor.models import AdvisorContext


class AdvisorEstimateService:
    def generate_summary(
        self, ctx: AdvisorContext, *, recommendations: list[RepairRecommendationDecision] | None = None
    ) -> list[Any]:
        recs = recommendations or []
        if not recs and not ctx.revenue_opportunities:
            return []
        line_items: list[dict[str, Any]] = []
        total = Decimal("0.00")
        for r in recs:
            line_items.append(
                {
                    "service": r.service_type,
                    "title": r.title,
                    "amount": str(r.estimated_cost),
                }
            )
            total += r.estimated_cost
        if not line_items:
            for opp in ctx.revenue_opportunities[:3]:
                amt = Decimal(str(opp.get("expected_revenue") or opp.get("amount") or "0"))
                line_items.append(
                    {
                        "service": opp.get("kind") or opp.get("service") or "service",
                        "title": opp.get("reason") or opp.get("title") or 'Рекомендуемая услуга',
                        "amount": str(amt),
                    }
                )
                total += amt

        plain = (
            'Рекомендуемые работы: '
            + "; ".join(f"{i['title']} (~${i['amount']})" for i in line_items)
            + f'. Ориентировочная сумма: ${total}.'
        )
        return [
            EstimateExplanationDecision(
                customer_id=ctx.customer_id,
                vehicle_id=ctx.vehicle_id,
                amount=total,
                line_items=line_items,
                summary=f'Итог сметы: ${total}',
                plain_language=plain,
                channel=ctx.channel or "sms",
                confidence=0.7,
                rationale='Объяснение сметы по рекомендациям консультанта',
            )
        ]

    def generate_approval_request(
        self, ctx: AdvisorContext, *, amount: Decimal | None = None, services: list[str] | None = None
    ) -> list[Any]:
        svcs = services or []
        amt = amount or Decimal("0.00")
        if not svcs and ctx.inbound_text and any(
            w in (ctx.inbound_text or "").lower() for w in ("approve", "estimate", "how much", "cost")
        ):
            svcs = ["recommended_repairs"]
            amt = amt or Decimal("250.00")
        if not svcs and not amt:
            return []
        body = (
            f'Для продолжения требуется ваше согласие'
            + (f" with: {', '.join(svcs)}" if svcs else "")
            + (f' (около ${amt})' if amt else "")
            + '. Ответьте YES для согласования или позвоните в автосервис, если есть вопросы.'
        )
        return [
            ApprovalRequestDecision(
                customer_id=ctx.customer_id,
                vehicle_id=ctx.vehicle_id,
                amount=amt,
                services=svcs,
                message_body=body,
                channel=ctx.channel or "sms",
                priority="high",
                confidence=0.68,
                rationale='Помощь с согласованием клиентом',
            )
        ]
