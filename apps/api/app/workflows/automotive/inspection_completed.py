"""Scenario 3 — Inspection Completed.

Flow:
  Inspection analysis → Customer explanation → Estimate recommendation → Approval request
"""

from __future__ import annotations

from uuid import UUID

from app.workflows.automotive.spec import action, build_definition, cond, meta
from app.workflows.enums import ActionType, ConditionOperator, DomainEventType
from app.workflows.models import WorkflowDefinition

WORKFLOW_ID = UUID("a1111111-1111-4111-8111-111111111103")

SPEC = meta(
    workflow_id=str(WORKFLOW_ID),
    purpose=(
        'После осмотра формирует объяснение клиенту, рекомендацию сметы и запрос согласования с обновлением CRM и выручки.'
    ),
    trigger=DomainEventType.REPAIR_FINISHED.value,
    capabilities=[
        "AnalyzeConversation",
        "GenerateRepairRecommendation",
        "GenerateEstimateSummary",
        "GenerateCustomerExplanation",
        "GenerateApprovalRequest",
        "AddRepair",
        "AddCommunication",
        "AddTimeline",
    ],
    ai_decisions=[
        "RepairRecommendationDecision",
        "EstimateExplanationDecision",
        "ApprovalRequestDecision",
        "CustomerCommunicationDecision",
        "CrmUpdateDecision",
    ],
    events_published=[
        DomainEventType.ESTIMATE_SENT.value,
        DomainEventType.CRM_UPDATED.value,
        DomainEventType.REVENUE_UPDATED.value,
        DomainEventType.DASHBOARD_UPDATED.value,
        DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
    ],
    failure_handling=(
        'Повторяет шаги сметы и CRM; уведомление о согласовании продолжает при ошибке; откат отменяет изменения CRM и выручки.'
    ),
    human_escalation=(
        'Ожидающие согласования уведомляют владельца или руководителя; превышение порога сметы требует передачи сотруднику.'
    ),
)


def build() -> WorkflowDefinition:
    return build_definition(
        workflow_id=WORKFLOW_ID,
        name='Автосервис: осмотр завершён',
        description=SPEC["purpose"],
        trigger=DomainEventType.REPAIR_FINISHED,
        conditions=[
            cond("phase", ConditionOperator.EQ, "inspection"),
        ],
        tags=["inspection", "estimate", "approval", "scenario-3"],
        spec=SPEC,
        actions=[
            action(
                ActionType.SET_CONTEXT,
                'Привязать сценарий осмотра',
                1,
                config={
                    "values": {
                        "scenario": "inspection_completed",
                        "expected_decisions": SPEC["ai_decisions"],
                        "required_capabilities": SPEC["required_capabilities"],
                    }
                },
            ),
            action(
                ActionType.LOG,
                'Анализ осмотра',
                2,
                config={
                    "message": 'AnalyzeConversation консультанта / результаты осмотра автомобиля',
                    "capability": "AnalyzeConversation|GenerateRepairRecommendation",
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Объяснение клиенту в истории',
                3,
                config={
                    "note": 'Осмотр завершён — объяснение клиенту подготовлено',
                    "fields": {
                        "capability": "GenerateCustomerExplanation",
                        "ai_decision": "CustomerCommunicationDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.EMIT_EVENT,
                'Опубликовать рекомендацию сметы',
                4,
                config={
                    "event_type": DomainEventType.ESTIMATE_SENT.value,
                    "payload": {"source": "inspection_completed"},
                },
            ),
            action(
                ActionType.UPDATE_CRM,
                'Рекомендация сметы записана',
                5,
                config={
                    "note": 'Рекомендация сметы по осмотру',
                    "fields": {
                        "capability": "GenerateEstimateSummary",
                        "ai_decision": "EstimateExplanationDecision",
                    },
                },
                compensate={"type": "undo_crm"},
            ),
            action(
                ActionType.UPDATE_REVENUE,
                'Открыть возможность выручки по смете',
                6,
                config={"category": "inspection_estimate"},
                compensate={"type": "undo_revenue"},
            ),
            action(
                ActionType.NOTIFY,
                'Запросить согласование владельца / руководителя',
                7,
                config={
                    "channel": "in_app",
                    "message": 'Смета по осмотру ожидает согласования клиента / владельца',
                    "ai_decision": "ApprovalRequestDecision",
                },
            ),
            action(
                ActionType.EMIT_EVENT,
                'Передача сотруднику для согласования',
                8,
                config={
                    "event_type": DomainEventType.HUMAN_ESCALATION_REQUESTED.value,
                    "payload": {
                        "reason": "inspection_approval_request",
                        "scenario": "inspection_completed",
                    },
                },
                continue_on_error=True,
            ),
            action(
                ActionType.UPDATE_DASHBOARD,
                'Обновить виджет согласований',
                9,
                config={
                    "widget": "overview",
                    "invalidate": ["approvals", "estimates", "revenue"],
                },
                continue_on_error=True,
            ),
        ],
    )
