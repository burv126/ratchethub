"""Marketing Agent — pure Decision Layer (compose messages; do not dispatch)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.agents.base.agent import Agent, AgentContext, AgentResult
from app.agents.base.logging import get_agent_logger
from app.agents.decisions.types import MarketingDecision
from app.agents.marketing.interfaces import MarketingDispatcherPort
from app.agents.marketing.models import (
    MarketingActionResult,
    MarketingActionType,
    MarketingRequest,
)

_TEMPLATES = {
    MarketingActionType.SMS_CAMPAIGN: (
        'Здравствуйте{name}! Это {shop}. Когда вам понадобится обслуживание, ответьте на это сообщение или запишитесь онлайн. Будем рады помочь.'
    ),
    MarketingActionType.EMAIL_CAMPAIGN: (
        'Здравствуйте{name}! Спасибо за доверие к {shop}. Полезный совет для вашего автомобиля: {tip}'
    ),
    MarketingActionType.REVIEW_REQUEST: (
        'Здравствуйте{name}! Надеемся, после визита в {shop} всё в порядке. Будем благодарны за отзыв: {review_link}'
    ),
    MarketingActionType.THANK_YOU: (
        'Спасибо{name}, что выбрали {shop}! Были рады помочь с вашим автомобилем.'
    ),
    MarketingActionType.MAINTENANCE_REMINDER: (
        'Здравствуйте{name}! Напоминаем: скоро потребуется {service} (около {due_mileage} миль). Ответьте BOOK, чтобы записаться.'
    ),
}


class LoggingMarketingDispatcher:
    """Default dispatcher — used only by Workflow DecisionExecutor."""

    def __init__(self) -> None:
        self._logger = get_agent_logger("marketing.dispatcher")
        self.sent: list[MarketingActionResult] = []

    async def dispatch(self, action: MarketingActionResult) -> MarketingActionResult:
        self._logger.info(
            "marketing.dispatch channel=%s type=%s",
            action.channel,
            action.action_type,
        )
        action.dispatched = True
        self.sent.append(action)
        return action


class MarketingAgent(Agent[MarketingRequest, MarketingActionResult]):
    """Decision-only marketing AI — composes content; Workflow dispatches."""

    name = "marketing"

    def __init__(self, dispatcher: MarketingDispatcherPort | None = None) -> None:
        super().__init__()
        # Dispatcher retained for DI into DecisionPorts — agent never calls it.
        self._dispatcher = dispatcher or LoggingMarketingDispatcher()

    @property
    def dispatcher(self) -> MarketingDispatcherPort:
        return self._dispatcher

    async def handle(
        self, payload: MarketingRequest, context: AgentContext
    ) -> AgentResult[MarketingActionResult]:
        return await self.execute(payload, context)

    async def execute(
        self, request: MarketingRequest, context: AgentContext
    ) -> AgentResult[MarketingActionResult]:
        template_key = request.action_type
        template = request.template or _TEMPLATES[template_key]
        ctx = {
            "name": "",
            "shop": 'наш автосервис',
            "tip": 'проверяйте давление в шинах ежемесячно',
            "review_link": "https://reviews.example.com",
            "service": "oil change",
            "due_mileage": "—",
            **request.context,
        }
        if ctx.get("name"):
            ctx["name"] = f" {ctx['name']}"
        body = template.format_map(_SafeDict(ctx))
        scheduled_at = request.scheduled_at or datetime.now(timezone.utc)

        decision = MarketingDecision(
            action_type=request.action_type.value,
            channel=request.channel,
            customer_id=request.customer_id or context.customer_id,
            template=template,
            body=body,
            context=dict(request.context),
            scheduled_at=scheduled_at,
            rationale=f'Составить маркетинговое сообщение: {request.action_type.value}',
        )

        action = MarketingActionResult(
            action_type=request.action_type.value,
            channel=request.channel,
            customer_id=request.customer_id or context.customer_id,
            template=template,
            body=body,
            scheduled_at=scheduled_at,
            dispatched=False,
            payload=dict(request.context),
            decision=decision,
        )
        return AgentResult.ok(action)


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""
