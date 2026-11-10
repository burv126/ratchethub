"""Default seeded workflows (global templates)."""

from __future__ import annotations

from uuid import uuid4

from app.workflows.automotive import automotive_workflows
from app.workflows.enums import ActionType, DomainEventType, WorkflowStatus
from app.workflows.models import RetryPolicy, WorkflowAction, WorkflowCondition, WorkflowDefinition
from app.workflows.enums import ConditionOperator
from app.workflows.store import WorkflowStorePort


def default_workflows() -> list[WorkflowDefinition]:
    """Appointment Created → Reminder → CRM → Revenue → Dashboard."""
    appointment_booked = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name='Цепочка создания записи',
        description='Напоминание → CRM → выручка → панель при appointment.booked',
        trigger=DomainEventType.APPOINTMENT_BOOKED,
        conditions=[],
        actions=[
            WorkflowAction(
                type=ActionType.SCHEDULE_REMINDER,
                name='Запланировать напоминание',
                order=1,
                config={"hours_before": 24, "channel": "sms", "template": "appointment_reminder"},
                compensate={"type": "cancel_reminder"},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_CRM,
                name='Обновить CRM',
                order=2,
                config={"note": 'Запись создана'},
                compensate={"type": "undo_crm"},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_REVENUE,
                name='Обновить выручку',
                order=3,
                config={"category": "appointment"},
                compensate={"type": "undo_revenue"},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_DASHBOARD,
                name='Обновить панель',
                order=4,
                config={"widget": "overview", "invalidate": ["appointments", "revenue"]},
                compensate={"type": "undo_dashboard"},
            ),
        ],
        retry=RetryPolicy(max_attempts=3, backoff_ms=500),
        status=WorkflowStatus.ACTIVE,
        tags=["default", "appointments"],
    )

    appointment_cancelled = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name='Цепочка отмены записи',
        description='CRM + выручка + панель при отмене',
        trigger=DomainEventType.APPOINTMENT_CANCELLED,
        actions=[
            WorkflowAction(
                type=ActionType.UPDATE_CRM,
                name='Записать отмену в CRM',
                order=1,
                config={"note": 'Запись отменена'},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_REVENUE,
                name='Скорректировать прогноз выручки',
                order=2,
                config={"category": "cancellation"},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_DASHBOARD,
                name='Обновить панель',
                order=3,
                config={"widget": "overview"},
            ),
        ],
        status=WorkflowStatus.ACTIVE,
        tags=["default", "appointments"],
    )

    invoice_paid = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name='Цепочка оплаты счёта',
        description='Выручка + CRM + панель при оплате счёта',
        trigger=DomainEventType.INVOICE_PAID,
        actions=[
            WorkflowAction(type=ActionType.UPDATE_REVENUE, name='Записать платёж', order=1),
            WorkflowAction(type=ActionType.UPDATE_CRM, name="CRM payment note", order=2),
            WorkflowAction(type=ActionType.UPDATE_DASHBOARD, name='Обновить панель', order=3),
        ],
        status=WorkflowStatus.ACTIVE,
        tags=["default", "billing"],
    )

    walk_in = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name="Walk-in created",
        description='CRM + панель для новых визитов без записи',
        trigger=DomainEventType.WALK_IN_CREATED,
        actions=[
            WorkflowAction(type=ActionType.UPDATE_CRM, name="CRM walk-in", order=1),
            WorkflowAction(type=ActionType.UPDATE_DASHBOARD, name='Обновить панель', order=2),
            WorkflowAction(
                type=ActionType.NOTIFY,
                name='Уведомить консультантов',
                order=3,
                config={"channel": "in_app", "message": 'Пришёл посетитель без записи'},
            ),
        ],
        status=WorkflowStatus.ACTIVE,
        tags=["default", "walkins"],
    )

    customer_created = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name='Приветствие нового клиента',
        trigger=DomainEventType.CUSTOMER_CREATED,
        conditions=[
            WorkflowCondition(field="name", operator=ConditionOperator.EXISTS),
        ],
        actions=[
            WorkflowAction(
                type=ActionType.LOG,
                name='Записать нового клиента',
                order=1,
                config={"message": 'Новый клиент зарегистрирован'},
            ),
            WorkflowAction(type=ActionType.UPDATE_CRM, name='Создать историю CRM', order=2),
            WorkflowAction(type=ActionType.UPDATE_DASHBOARD, name='Обновить панель', order=3),
        ],
        status=WorkflowStatus.ACTIVE,
        tags=["default", "crm"],
    )

    maintenance_reminder = WorkflowDefinition(
        id=uuid4(),
        shop_id=None,
        name='Запрошено напоминание об обслуживании',
        description='Журнал + заметка CRM при запросе напоминания об обслуживании',
        trigger=DomainEventType.MAINTENANCE_REMINDER_REQUESTED,
        actions=[
            WorkflowAction(
                type=ActionType.LOG,
                name='Записать организацию напоминания',
                order=1,
                config={"message": 'Напоминание запрошено координатором процессов'},
            ),
            WorkflowAction(
                type=ActionType.UPDATE_CRM,
                name="CRM maintenance reminder note",
                order=2,
                config={"note": 'Запрошено напоминание об обслуживании'},
            ),
        ],
        status=WorkflowStatus.ACTIVE,
        tags=["default", "marketing", "orchestration"],
    )

    return [
        appointment_booked,
        appointment_cancelled,
        invoice_paid,
        walk_in,
        customer_created,
        maintenance_reminder,
        *automotive_workflows(),
    ]


# Names were historically used as seed identities. Recognize the original names
# without renaming stored templates or running their actions a second time.
_LEGACY_TEMPLATE_NAMES = {
    "Цепочка создания записи": "Appointment booked cascade",
    "Цепочка отмены записи": "Appointment cancelled cascade",
    "Цепочка оплаты счёта": "Invoice paid cascade",
    "Приветствие нового клиента": "Customer created welcome",
    "Запрошено напоминание об обслуживании": "Maintenance reminder requested",
    "Автосервис: запрос ремонта нового клиента по телефону": "Automotive: New customer phone repair request",
    "Автосервис: напоминание об обслуживании": "Automotive: Maintenance reminder",
    "Автосервис: осмотр завершён": "Automotive: Inspection completed",
    "Автосервис: возврат отклонённых смет": "Automotive: Declined estimate recovery",
    "Автосервис: посетитель без записи": "Automotive: Walk-in customer",
    "Автосервис: ремонт завершён": "Automotive: Repair completed",
}


async def seed_default_workflows(store: WorkflowStorePort) -> list[WorkflowDefinition]:
    existing = await store.list_workflows(shop_id=uuid4())  # lists globals + none for random shop
    # Prefer check by name among globals
    names = {w.name for w in existing if w.shop_id is None}
    seeded: list[WorkflowDefinition] = []
    for wf in default_workflows():
        if wf.name in names or _LEGACY_TEMPLATE_NAMES.get(wf.name) in names:
            continue
        seeded.append(await store.save_workflow(wf))
    return seeded
