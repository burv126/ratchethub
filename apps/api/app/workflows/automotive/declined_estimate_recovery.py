"""Scenario 4 — Declined Estimate Recovery.

Flow:
  Lost revenue detection → Follow-up workflow → Customer recovery
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, meta
from app.workflows.enums import ActionType, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111104")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'Возвращает клиентов, отклонивших смету: выявляет упущенную выручку, планирует повторную связь и помогает удержанию.'
    ),
    trigger=DomainEventType.ESTIMATE_DECLINED.value,
    capabilities=[
        "DetectRevenueOpportunity",
        "CalculateCustomerHealth",
        "GenerateRetentionPlan",
        "GenerateFollowUp",
        "AddTimeline",
        "AddCommunication",
    ],
    ai_decisions=[
        "RevenueDecision",
        "RetentionDecision",
        "CustomerCommunicationDecision",
        "CrmUpdateDecision",
        "MarketingDecision",
    ],
    events_published=[
        DomainEventType.REVENUE_UPDATED.value,
        DomainEventType.REVENUE_OPPORTUNITY_DETECTED.value,
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.REMINDER_SCHEDULED.value,
        DomainEventType.MARKETING_ACTION_REQUESTED.value,
        DomainEventType.CUSTOMER_RETURNED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
        DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
    ],
    failure_handling=(
        'Повторяет шаги выручки, CRM и напоминания; маркетинг продолжает при ошибке; откат отменяет изменения CRM, выручки и напоминания.'
    ),
    human_escalation=(
        "High-value declined estimates notify advisors for personal recovery call."
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name='Автосервис: возврат отклонённых смет',
        description=SPEC["purpose"],
        trigger=DomainEventType.ESTIMATE_DECLINED,
        tags=["estimate", "recovery", "revenue", "scenario-4"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать сценарий возвращения',
                1,
                config={
                    "values": {
                        "scenario": "declined_estimate_recovery",
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.UPDATE_REVENUE,
                'Выявление упущенной выручки',
                2,
                config={"category": "declined_estimate"},
                compensate={"type": "undo_revenue"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Отметить возможность выручки / возвращения',
                3,
                config={
                    "event_type": DomainEventType.REVENUE_OPPORTUNITY_DETECTED.value,
                    "payload": {"source": "declined_estimate", "kind": "recovery"},
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                "CRM recovery follow-up plan",
                4,
                config={
                    "note": 'Смета отклонена — повторная связь начата',
                    "fields": {
                        "capability": "GenerateFollowUp|GenerateRetentionPlan",
                        "ai_decision": "RetentionDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.SCHEDULE_REMINDER,
                'Запланировать повторную связь',
                5,
                config={
                    "hours_before": -72,  # ~3 days later (action treats negative specially)
                    "channel": "sms",
                    "template": "declined_estimate_recovery",
                },
                compensate={"type": "cancel_reminder"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Маркетинговое действие для возвращения',
                6,
                config={
                    "event_type": DomainEventType.MARKETING_ACTION_REQUESTED.value,
                    "payload": {"campaign": "declined_estimate_recovery"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.EMIT_EVENT,
                'Отметить возвращение клиента',
                7,
                config={
                    "event_type": DomainEventType.CUSTOMER_RETURNED.value,
                    "payload": {"source": "declined_estimate_recovery"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.NOTIFY,
                'Звонок консультанта для возвращения',
                8,
                config={
                    "channel": "in_app",
                    "message": 'Смета отклонена — рекомендуется личное обращение',
                },
            ),
            action(
                ActionType.EMIT_EVENT,
                'Передача сотруднику важного клиента',
                9,
                config={
                    "event_type": DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
                    "payload": {
                        "reason": "declined_estimate_recovery",
                        "scenario": "declined_estimate_recovery",
                    },
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить виджеты отклонённых смет',
                10,
                config={
                    "widget": "overview",
                    "invalidate": ["revenue", "declined_estimates", "marketing"],
                },
                continue_on_error=True,
            ),
        ],
    )
