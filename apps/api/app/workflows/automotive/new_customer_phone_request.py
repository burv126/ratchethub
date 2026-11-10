"""Scenario 1 — New Customer Phone Repair Request.

Flow (business):
  Phone → Conversation → Customer ID → Vehicle → Repair recommendation
  → Appointment booking → SMS confirmation → CRM timeline
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, cond, meta
from app.workflows.enums import ActionType, ConditionOperator, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111101")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'Обрабатывает звонок нового клиента: определение клиента, рекомендации, запись, подтверждение SMS и история CRM.'
    ),
    trigger=DomainEventType.INBOUND_MESSAGE_RECEIVED.value,
    capabilities=[
        "CreateConversation",
        "FindCustomer",
        "CreateCustomer",
        "FindVehicle",
        "CreateVehicle",
        "AnalyzeConversation",
        "GenerateRepairRecommendation",
        "BookAppointment",
        "FindAvailableSlot",
        "AddCommunication",
        "AddTimeline",
        "UpdateConversation",
    ],
    ai_decisions=[
        "CustomerDecision",
        "VehicleDecision",
        "RepairRecommendationDecision",
        "EstimateExplanationDecision",
        "AppointmentDecision",
        "CustomerCommunicationDecision",
        "CrmUpdateDecision",
    ],
    events_published=[
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.REMINDER_SCHEDULED.value,
        DomainEventType.REVENUE_UPDATED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
        DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
    ],
    failure_handling=(
        "RetryPolicy 3x with backoff on CRM/reminder/notify failures; "
        "continue_on_error on non-critical dashboard refresh; "
        "compensation undoes reminder/CRM/revenue side-effects on rollback."
    ),
    human_escalation=(
        'Уведомляет консультантов, если автомобиль не определён или запись не завершена; отправляет human_escalation_requested для подключения руководителя.'
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name='Автосервис: запрос ремонта нового клиента по телефону',
        description=SPEC["purpose"],
        trigger=DomainEventType.INBOUND_MESSAGE_RECEIVED,
        conditions=[
            # Prefer phone/voice channels; still runs if channel omitted (simulate).
            cond("channel", ConditionOperator.IN, ["phone", "voice", "call", None]),
        ],
        tags=["phone", "repair", "scenario-1"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать ожидаемые решения ИИ',
                1,
                config={
                    "values": {
                        "scenario": "new_customer_phone_request",
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.LOG,
                'Проверка создания диалога',
                2,
                config={
                    "message": 'Проверить наличие диалога (CreateConversation / телефонный канал)',
                    "capability": "CreateConversation",
                    "ai_decision": None,
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Определение клиента в истории',
                3,
                config={
                    "note": 'Запрос ремонта по телефону — найти / создать клиента',
                    "fields": {
                        "capability": "FindCustomer|CreateCustomer",
                        "ai_decision": "CustomerDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_CRM,
                'Определение автомобиля в истории',
                4,
                config={
                    "note": 'Указать или найти автомобиль для ремонта',
                    "fields": {
                        "capability": "FindVehicle|CreateVehicle",
                        "ai_decision": "VehicleDecision",
                    },
                },
                continue_on_error=True,
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_CRM,
                'Рекомендация ремонта записана',
                5,
                config={
                    "note": "RatchetHub repair recommendation applied to CRM",
                    "fields": {
                        "capability": "AnalyzeConversation|GenerateRepairRecommendation",
                        "ai_decision": "RepairRecommendationDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_REVENUE,
                'Создать возможность выручки по запросу ремонта',
                6,
                config={"category": "phone_repair_request", "amount": 0},
                compensate={"type": "undo_revenue"},
            ),
            action(
                ActionType.SCHEDULE_REMINDER,
                "SMS confirmation / booking follow-up",
                7,
                config={
                    "hours_before": 0,
                    "channel": "sms",
                    "template": "phone_repair_sms_confirmation",
                    "capability_hint": "BookAppointment + CustomerCommunicationDecision",
                },
                compensate={"type": "cancel_reminder"},
            ),
            action(
                ActionType.NOTIFY,
                'Приём консультанта — подтвердить запись',
                8,
                config={
                    "channel": "in_app",
                    "message": 'Новый запрос ремонта по телефону требует подтверждения записи',
                },
                continue_on_error=True,
            ),
            action(
                ActionType.EMIT_EVENT,
                'Запросить сотрудника при незавершённой записи',
                9,
                config={
                    "event_type": DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
                    "payload": {
                        "reason": "phone_repair_booking_confirmation",
                        "scenario": "new_customer_phone_request",
                    },
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить операционную панель',
                10,
                config={
                    "widget": "overview",
                    "invalidate": ["appointments", "crm", "voice", "revenue"],
                },
                continue_on_error=True,
                compensate={"type": "undo_dashboard"},
            ),
        ],
    )
