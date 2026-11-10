"""Russian aliases must preserve the existing English parser and canonical data."""

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from httpx import ASGITransport, AsyncClient

from app.agents.base.agent import AgentContext
from app.agents.communication.models import NormalizedMessage
from app.agents.counselor.persona import ask_name, looks_like_farewell, summarize_done, wants_to_end_after_offer
from app.agents.intent.datetime_parse import parse_preferred_datetime, parse_same_slot_preference
from app.agents.intent.models import CustomerIntent
from app.agents.intent.service import IntentAgent, _extract_entities
from app.agents.scheduling.catalog_match import extract_service_switch_target, match_catalog_service
from app.agents.scheduling.catalog_port import CatalogServiceView, InMemoryServiceCatalog
from app.analytics.enums import KpiId
from app.analytics.forecast import ForecastEngine
from app.analytics.reports import ReportBuilder
from app.application.crm_service import _normalize_vin
from app.api.routers.customers import _http_error
from app.domain.exceptions import ValidationError
from app.infrastructure.ai.heuristic import HeuristicRepairExtraction
from app.localization import benchmark_label, kpi_label


NOW = datetime(2026, 10, 20, 9, tzinfo=ZoneInfo("America/Los_Angeles"))


@pytest.mark.parametrize("russian,english", [
    ("завтра в 10:00", "tomorrow at 10:00"),
    ("послезавтра в 14:30", "day after tomorrow at 14:30"),
    ("сегодня вечером", "today evening"),
    ("в пятницу утром", "friday morning"),
    ("в среду днём", "wednesday afternoon"),
    ("в четверг в 11:00", "thursday at 11:00"),
    ("в субботу в полдень", "saturday noon"),
    ("в воскресенье", "sunday"),
    ("в следующий понедельник", "next monday"),
    ("через неделю", "next week"),
    ("завтра в 15 часов", "tomorrow at 15:00"),
    ("завтра в 03:15", "tomorrow at 3:15 am"),
    ("завтра в 00:30", "tomorrow at 0:30 am"),
    ("в пятницу после обеда", "friday afternoon"),
])
def test_dates_share_existing_precision_timezone_and_values(russian, english):
    expected = parse_preferred_datetime(english, now=NOW)
    actual = parse_preferred_datetime(russian, now=NOW)
    assert actual == expected
    assert actual.day_explicit
    assert actual.start.tzinfo == NOW.tzinfo


@pytest.mark.parametrize("text", ["", "вчера", "когда-нибудь", "not a date", "25:99", "в 15:999", "в 99:00", "в 03:80", "в 15:00abc"])
def test_unrecognized_or_invalid_dates_do_not_invent_a_clock(text):
    assert parse_preferred_datetime(text, now=NOW).start is None


@pytest.mark.parametrize("russian,english", [
    ("в то же время", "same time"),
    ("в тот же день", "same day"),
    ("в тот же день и в то же время", "same day and time"),
])
def test_same_slot_aliases(russian, english):
    assert parse_same_slot_preference(russian) == parse_same_slot_preference(english)
    assert parse_same_slot_preference("неизвестно") is None


@pytest.mark.parametrize("text,name", [
    ("Иван", "Иван"), ("Ёлкин Иван", "Ёлкин Иван"),
    ("Меня зовут Анна-Мария", "Анна-Мария"),
    ("Моё имя Ольга", "Ольга"), ("Alex", "Alex"),
    ("my name is Sam Rivera", "Sam Rivera"),
    ("нет", None), ("да", None), ("нет спасибо", None),
    ("завтра", None), ("перенесите запись", None), ("12345", None),
])
def test_names_and_non_names(text, name):
    context = AgentContext(shop_id=uuid4(), metadata={"pending_question": ask_name()})
    assert _extract_entities(text, context=context).get("name") == name


@pytest.mark.parametrize("text,confirmed", [
    ("да", True), ("Да, пожалуйста", True), ("подтверждаю", True),
    ("yes please", True), ("yes", True), ("нет", False),
    ("no", False), ("да, не надо", False), ("случайный текст", False),
])
def test_confirmations(text, confirmed):
    assert bool(_extract_entities(text).get("booking_confirmed")) is confirmed


@pytest.mark.parametrize("text", ["нет", "нет, спасибо", "no", "no thanks"])
def test_declines_after_an_offer_preserve_existing_explicit_farewells(text):
    offer = summarize_done(action="book", keep_open=True)
    assert wants_to_end_after_offer(text, last_assistant_text=offer)
    assert wants_to_end_after_offer(text, last_assistant_text=ask_name()) == looks_like_farewell(text)


@pytest.mark.asyncio
@pytest.mark.parametrize("text,intent", [
    ("Хочу записаться на замену масла", CustomerIntent.BOOK_APPOINTMENT),
    ("book an appointment for oil change", CustomerIntent.BOOK_APPOINTMENT),
    ("Мне нужна замена масла", CustomerIntent.BOOK_APPOINTMENT),
    ("I need an oil change", CustomerIntent.BOOK_APPOINTMENT),
    ("Перенесите мою запись на завтра", CustomerIntent.RESCHEDULE),
    ("reschedule my appointment tomorrow", CustomerIntent.RESCHEDULE),
    ("Отмените мою запись", CustomerIntent.CANCEL_APPOINTMENT),
    ("cancel my appointment", CustomerIntent.CANCEL_APPOINTMENT),
    ("Какое время свободно?", CustomerIntent.CHECK_AVAILABILITY),
    ("what times are available?", CustomerIntent.CHECK_AVAILABILITY),
    ("Сколько стоит замена масла?", CustomerIntent.PRICE_QUESTION),
    ("how much is an oil change?", CustomerIntent.PRICE_QUESTION),
    ("Не отменяйте запись", CustomerIntent.OTHER),
    ("не нужно переносить запись", CustomerIntent.OTHER),
    ("неизвестная команда", CustomerIntent.OTHER),
])
async def test_intent_aliases_preserve_raw_text_and_canonical_intent(text, intent):
    context = AgentContext(shop_id=uuid4())
    message = NormalizedMessage(channel="sms", direction="incoming", body=text,
        sender="+15550000001", recipient=None, subject=None, received_at=None,
        language="ru", metadata={})
    result = await IntentAgent().detect(message, context)
    assert result.data.intent == intent
    assert result.data.raw_excerpt == text
    assert message.body == text
    if text in {"Мне нужна замена масла", "I need an oil change"}:
        assert result.data.entities["requested_service"] == "Oil Change"


@pytest.mark.parametrize("query", ["замена масла", "oil change", "нужна замена масла"])
def test_service_search_uses_original_catalog_identity(query):
    catalog = InMemoryServiceCatalog()
    services = catalog.seed_from_starter(uuid4())
    original = next(service for service in services if service.name == "Oil Change")
    match = match_catalog_service(query, services)
    assert match.service_id == original.id
    assert match.name == original.name
    assert original.price == Decimal("49.99")
    assert original.duration_minutes == 30
    assert match_catalog_service("неизвестная услуга", services) is None
    assert match_catalog_service("unknown xyz service", services) is None


@pytest.mark.parametrize("text", ["Поменяйте услугу на ремонт тормозов", "change service type to brake repair"])
def test_service_switch_target(text):
    services = InMemoryServiceCatalog().seed_from_starter(uuid4())
    target = extract_service_switch_target(text)
    assert match_catalog_service(target, services).name == "Brake Repair"


def test_russian_custom_catalog_name_beats_english_alias():
    services = InMemoryServiceCatalog().seed_from_starter(uuid4())
    custom = CatalogServiceView(id=uuid4(), name="Замена масла", category="maintenance",
        duration_minutes=75, skill="oil_change", bay="general", price=Decimal("180"))
    services.append(custom)
    assert match_catalog_service("Замена масла", services).service_id == custom.id
    assert match_catalog_service("Oil Change", services).service_id != custom.id
    assert custom.name == "Замена масла" and custom.duration_minutes == 75


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [
    "Замена масла. Пробег: 124000. Рекомендую заменить фильтр.",
    "Oil change. Mileage: 124000. Recommend replace filter.",
])
async def test_mechanic_note_aliases_keep_canonical_service_and_mileage(text):
    result = await HeuristicRepairExtraction().extract(transcript=text)
    assert result.service == "Oil Change"
    assert result.mileage == 124000
    assert result.recommendation in {"заменить фильтр", "replace filter"}
    empty = await HeuristicRepairExtraction().extract(transcript=" ")
    assert empty.mileage is None and empty.recommendation is None


def test_report_display_does_not_translate_metric_codes_or_values():
    benchmark = SimpleNamespace(kpi=KpiId.REVENUE, label="Выручка", shop_value=120.5,
        industry_avg=100.0, top_quartile=150.0, status="ahead")
    section = ReportBuilder()._benchmark_section(SimpleNamespace(benchmarks=[benchmark]))
    assert "выше отрасли" in section.body
    assert section.metrics[0] == {"kpi": "revenue", "shop_value": 120.5,
        "industry_avg": 100.0, "top_quartile": 150.0, "status": "ahead"}
    forecast = ForecastEngine()._forecast_series(KpiId.REVENUE, [1, 2, 3], NOW.date(), horizon_days=2)
    assert "Выручка" in forecast.summary and "рост" in forecast.summary
    assert forecast.kpi.value == "revenue" and forecast.method == "linear_trend_weekend"
    assert kpi_label("custom") == "custom" and benchmark_label("custom") == "custom"


def test_domain_error_type_http_status_and_internal_message_stay_unchanged():
    with pytest.raises(ValidationError) as caught:
        _normalize_vin("invalid")
    error = _http_error(caught.value)
    assert error.status_code == 422
    assert error.detail == "VIN must be 17 characters and exclude I, O, and Q"


@pytest.mark.asyncio
async def test_api_validation_contract_retains_machine_readable_fields():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/v1/auth/register", json={})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert all({"type", "loc", "msg", "input"} <= item.keys() for item in detail)
    assert any(item["type"] == "missing" for item in detail)
    assert all(item["loc"][0] == "body" for item in detail)
