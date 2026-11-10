"""Scenario 2 — Maintenance Reminder.

Flow:
  Vehicle health → Customer risk → Revenue opportunity → Marketing follow-up
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, meta
from app.workflows.enums import ActionType, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111102")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'При запросе напоминания оценивает состояние автомобиля и риск ухода клиента, выявляет возможность выручки и планирует маркетинговое обращение.'
    ),
    trigger=DomainEventType.MAINTENANCE_REMINDER_REQUESTED.value,
    capabilities=[
        "CalculateVehicleHealth",
        "CalculateCustomerHealth",
        "DetectRevenueOpportunity",
        "GenerateUpsellRecommendations",
        "GenerateMaintenanceReminder",
        "AddTimeline",
        "AddCommunication",
    ],
    ai_decisions=[
        "MaintenanceReminderDecision",
        "RevenueDecision",
        "RetentionDecision",
        "MarketingDecision",
        "CustomerCommunicationDecision",
    ],
    events_published=[
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.REVENUE_OPPORTUNITY_DETECTED.value,
        DomainEventType.REMINDER_SCHEDULED.value,
        DomainEventType.MARKETING_ACTION_REQUESTED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
    ],
    failure_handling=(
        'Повторяет шаги CRM и напоминания; маркетинг продолжает при ошибке; откат отменяет записи CRM и напоминания. Выявление выручки не вызывает вложенный UPDATE_REVENUE для предотвращения цикла.'
    ),
    human_escalation=(
        'Высокий риск ухода вызывает уведомление консультанта для личного обращения.'
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name='Автосервис: напоминание об обслуживании',
        description=SPEC["purpose"],
        trigger=DomainEventType.MAINTENANCE_REMINDER_REQUESTED,
        tags=["maintenance", "marketing", "scenario-2"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать контекст напоминания',
                1,
                config={
                    "values": {
                        "scenario": "maintenance_reminder",
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.LOG,
                'Анализ состояния автомобиля',
                2,
                config={
                    "message": 'CalculateVehicleHealth / анализ обслуживания консультантом',
                    "capability": "CalculateVehicleHealth",
                },
            ),
            action(
                ActionType.LOG,
                'Оценка риска клиента',
                3,
                config={
                    "message": "CalculateCustomerHealth / RetentionDecision inputs",
                    "capability": "CalculateCustomerHealth",
                    "ai_decision": "RetentionDecision",
                },
            ),
            action(
                ActionType.LOG,
                'Выявить возможность выручки от обслуживания',
                4,
                config={
                    "message": 'Возможности DetectRevenueOpportunity / GenerateUpsellRecommendations',
                    "capability": "DetectRevenueOpportunity",
                    "ai_decision": "RevenueDecision",
                },
            ),
            action(
                ActionType.EMIT_EVENT,
                'Опубликовать найденную возможность выручки',
                5,
                config={
                    "event_type": DomainEventType.REVENUE_OPPORTUNITY_DETECTED.value,
                    "payload": {"source": "maintenance_reminder"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_CRM,
                "CRM maintenance follow-up note",
                6,
                config={
                    "note": 'Напоминание — состояние автомобиля и риск оценены',
                    "fields": {"ai_decision": "MaintenanceReminderDecision"},
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.SCHEDULE_REMINDER,
                'Запланировать связь по обслуживанию',
                7,
                config={
                    "hours_before": 0,
                    "channel": "sms",
                    "template": "maintenance_due",
                },
                compensate={"type": "cancel_reminder"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Запросить маркетинговое обращение',
                8,
                config={
                    "event_type": DomainEventType.MARKETING_ACTION_REQUESTED.value,
                    "payload": {"campaign": "maintenance_reminder", "channel": "sms"},
                },
            ),
            action(
                ActionType.NOTIFY,
                'Передать консультантам клиентов с высоким риском',
                9,
                config={
                    "channel": "in_app",
                    "message": "High-risk maintenance customer may need personal call",
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить виджеты маркетинга и выручки',
                10,
                config={
                    "widget": "overview",
                    "invalidate": ["marketing", "revenue", "retention"],
                },
                continue_on_error=True,
            ),
        ],
    )
