"""Scenario 5 — Walk-in Customer.

Flow:
  Temporary customer → Vehicle capture → Inspection workflow → Customer merge
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, meta
from app.workflows.enums import ActionType, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111105")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'Обрабатывает визиты без записи: временный приём без полного профиля, данные автомобиля, запуск осмотра и последующее объединение или преобразование клиента.'
    ),
    trigger=DomainEventType.WALK_IN_CREATED.value,
    capabilities=[
        "CreateVehicle",
        "FindVehicle",
        "CreateCustomer",
        "UpdateCustomer",
        "AddTimeline",
        "WalkInCheckIn",
        "AnalyzeConversation",
        "GenerateRepairRecommendation",
        "BookAppointment",
    ],
    ai_decisions=[
        "VehicleDecision",
        "CustomerDecision",
        "RepairRecommendationDecision",
        "AppointmentDecision",
        "CrmUpdateDecision",
    ],
    events_published=[
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.VEHICLE_CREATED.value,
        DomainEventType.REPAIR_STARTED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
        DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
    ],
    failure_handling=(
        'Повторяет обновления CRM; запуск осмотра продолжает при ошибке; откат отменяет изменения CRM и панели.'
    ),
    human_escalation=(
        'Уведомляет консультантов о посетителе; передаёт сотруднику при необходимости преобразования или объединения до ремонта.'
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name="Автосервис: посетитель без записи",
        description=SPEC["purpose"],
        trigger=DomainEventType.WALK_IN_CREATED,
        tags=["walkin", "intake", "scenario-5"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать сценарий живой очереди',
                1,
                config={
                    "values": {
                        "scenario": "walk_in_customer",
                        "temporary_customer": True,
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Временный клиент / приём визита',
                2,
                config={
                    "note": "Walk-in created — temporary intake (customer optional)",
                    "fields": {
                        "capability": "WalkInCheckIn|CreateCustomer",
                        "ai_decision": "CustomerDecision",
                        "temporary": True,
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_CRM,
                'Данные автомобиля',
                3,
                config={
                    "note": "Walk-in vehicle captured (VIN/year/make/model/mileage)",
                    "fields": {
                        "capability": "CreateVehicle|FindVehicle",
                        "ai_decision": "VehicleDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Подтвердить автомобиль визита',
                4,
                config={
                    "event_type": DomainEventType.VEHICLE_CREATED.value,
                    "payload": {"source": "walk_in_customer"},
                },
                continue_on_error=True,
            ),
            action(
                ActionType.EMIT_EVENT,
                'Запустить процесс осмотра',
                5,
                config={
                    "event_type": DomainEventType.REPAIR_STARTED.value,
                    "payload": {"phase": "inspection", "source": "walk_in"},
                },
            ),
            action(
                ActionType.NOTIFY,
                'Уведомить консультантов — новый посетитель',
                6,
                config={
                    "channel": "in_app",
                    "message": 'Пришёл посетитель — преобразуйте или объедините клиента, когда будет возможно',
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Проверка объединения клиента',
                7,
                config={
                    "note": 'Ожидает преобразования в клиента или объединения с записью CRM',
                    "fields": {
                        "capability": "UpdateCustomer|CreateCustomer",
                        "ai_decision": "CustomerDecision",
                        "merge_pending": True,
                    },
                },
                continue_on_error=True,
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Передать сотруднику при блокировке объединения до ремонта',
                8,
                config={
                    "event_type": DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
                    "payload": {
                        "reason": "walk_in_customer_merge",
                        "scenario": "walk_in_customer",
                    },
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить виджет живой очереди',
                9,
                config={
                    "widget": "overview",
                    "invalidate": ["walk_ins", "crm", "appointments"],
                },
                continue_on_error=True,
            ),
        ],
    )
