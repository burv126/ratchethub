"""Upgrading display copy must not recreate or overwrite seeded workflows."""

from dataclasses import replace
from uuid import uuid4

import pytest

from app.workflows.seeds import default_workflows, seed_default_workflows
from app.workflows.store import InMemoryWorkflowStore


# Names exported by the pre-localization Git baseline, in seed order.
LEGACY_NAMES = (
    "Appointment booked cascade",
    "Appointment cancelled cascade",
    "Invoice paid cascade",
    "Walk-in created",
    "Customer created welcome",
    "Maintenance reminder requested",
    "Automotive: New customer phone repair request",
    "Automotive: Maintenance reminder",
    "Automotive: Inspection completed",
    "Automotive: Declined estimate recovery",
    "Automotive: Walk-in customer",
    "Automotive: Repair completed",
)


@pytest.mark.asyncio
async def test_localized_reseed_preserves_prelocalization_templates():
    store = InMemoryWorkflowStore()
    definitions = default_workflows()
    assert len(definitions) == len(LEGACY_NAMES)
    for definition, name in zip(definitions, LEGACY_NAMES, strict=True):
        await store.save_workflow(
            replace(definition, name=name, description="Existing approved template")
        )
    original = dict(store.workflows)
    timestamps = {key: value.updated_at for key, value in original.items()}

    assert await seed_default_workflows(store) == []
    assert await seed_default_workflows(store) == []
    assert store.workflows == original
    assert {key: value.updated_at for key, value in store.workflows.items()} == timestamps
    assert len(await store.list_workflows(uuid4())) == len(LEGACY_NAMES)
