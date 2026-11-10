"""Scenario 6 — Repair Completed.

Flow:
  Payment workflow → Review request → Maintenance reminder → Revenue update
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, cond, meta
from app.workflows.enums import ActionType, ConditionOperator, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111106")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'Завершает ремонт: проверка оплаты, запрос отзыва, напоминание об обслуживании и итоговое обновление выручки и панели.'
    ),
    trigger=DomainEventType.REPAIR_FINISHED.value,
    capabilities=[
        "AddRepair",
        "AddCommunication",
        "AddTimeline",
        "GenerateReviewRequest",
        "GenerateMaintenanceReminder",
        "DetectRevenueOpportunity",
        "UpdateConversation",
    ],
    ai_decisions=[
        "RepairStatusDecision",
        "ReviewRequestDecision",
        "MaintenanceReminderDecision",
        "RevenueDecision",
        "CustomerCommunicationDecision",
        "CrmUpdateDecision",
    ],
    events_published=[
        DomainEventType.INVOICE_PAID.value,
        DomainEventType.REVIEW_SUBMITTED.value,
        DomainEventType.MAINTENANCE_REMINDER_REQUESTED.value,
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.REVENUE_UPDATED.value,
        DomainEventType.REMINDER_SCHEDULED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
    ],
    failure_handling=(
        "Payment/review emits continue_on_error so closeout continues; "
        "CRM/revenue/reminder retried; rollback reverses CRM/revenue/reminder."
    ),
    human_escalation=(
        'Уведомляет приёмную, если после ремонта оплата не завершена.'
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name='Автосервис: ремонт завершён',
        description=SPEC["purpose"],
        trigger=DomainEventType.REPAIR_FINISHED,
        conditions=[
            # Runs for normal repair closeout; inspection phase handled by sibling workflow.
            cond("phase", ConditionOperator.NE, "inspection"),
        ],
        tags=["repair", "payment", "review", "scenario-6"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать сценарий завершения ремонта',
                1,
                config={
                    "values": {
                        "scenario": "repair_completed",
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Завершение ремонта в истории',
                2,
                config={
                    "note": 'Ремонт завершён — начато закрытие',
                    "fields": {
                        "capability": "AddRepair|AddTimeline",
                        "ai_decision": "RepairStatusDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Запуск процесса оплаты',
                3,
                config={
                    "event_type": DomainEventType.INVOICE_PAID.value,
                    "payload": {"source": "repair_completed", "status": "payment_due_or_paid"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.NOTIFY,
                'Проверка оплаты приёмной',
                4,
                config={
                    "channel": "in_app",
                    "message": 'Ремонт завершён — подтвердите оплату',
                },
                continue_on_error=True,
            ),
            action(
                ActionType.SCHEDULE_REMINDER,
                'Запрос отзыва',
                5,
                config={
                    "hours_before": -24,
                    "channel": "sms",
                    "template": "review_request",
                    "ai_decision": "ReviewRequestDecision",
                },
                compensate={"type": "cancel_reminder"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Запрос отзыва записан',
                6,
                config={
                    "event_type": DomainEventType.REVIEW_SUBMITTED.value,
                    "payload": {"source": "repair_completed", "status": "requested"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.EMIT_EVENT,
                'Поставить напоминание об обслуживании в очередь',
                7,
                config={
                    "event_type": DomainEventType.MAINTENANCE_REMINDER_REQUESTED.value,
                    "payload": {"source": "repair_completed"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_REVENUE,
                'Итоговое обновление выручки',
                8,
                config={"category": "repair_completed"},
                compensate={"type": "undo_revenue"},
            ),
            action(
                ActionType.UPDATE_CRM,
                'Итоговое сообщение CRM',
                9,
                config={
                    "note": 'Ремонт завершён — запланированы отзыв и напоминания',
                    "fields": {
                        "ai_decision": "CustomerCommunicationDecision|MaintenanceReminderDecision"
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить виджеты завершения',
                10,
                config={
                    "widget": "overview",
                    "invalidate": ["revenue", "repairs", "reviews", "marketing"],
                },
                continue_on_error=True,
            ),
        ],
    )
