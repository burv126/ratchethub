"""Contextual SMS reply generation from agent pipeline + conversation memory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.agents.counselor import persona as counselor
from app.agents.orchestrator import PipelineResult
from app.agents.intent.models import CustomerIntent
from app.agents.intent.reschedule_text import looks_like_service_type_change
from app.sms.memory import ConversationMemorySnapshot


@dataclass(slots=True)
class ReplyDraft:
    body: str
    follow_up_question: str | None = None
    send: bool = True
    reason: str | None = None


def _format_appt_when(iso_start: str | None) -> str | None:
    if not iso_start:
        return None
    try:
        from zoneinfo import ZoneInfo

        shop_tz = ZoneInfo("America/Los_Angeles")
        dt = datetime.fromisoformat(iso_start.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=shop_tz)
        else:
            dt = dt.astimezone(shop_tz)
        # Keep a concrete calendar cue for SMS (weekday + month day).
        return f"{dt:%d.%m.%Y} в {dt:%H:%M}"
    except (ValueError, TypeError):
        return None


def _parse_dt(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _mentions_time_change_with_service(text: str | None) -> bool:
    """True when utterance asks to change both job and clock (compound move)."""
    if not text:
        return False
    low = text.casefold()
    has_when = any(
        t in low
        for t in (
            " time",
            "time ",
            " date",
            " day",
            "when",
            "timing",
            "schedule",
            "slot",
            "window",
            "hour",
        )
    )
    has_join = any(
        t in low
        for t in (
            " and ",
            "&",
            " both",
            "both ",
            " plus ",
            " as well",
            " also",
            " along with",
            " together with",
            " too",
            "not just",
            "not only",
        )
    )
    has_dual_new = (
        any(
            x in low
            for x in (
                "new service",
                "different service",
                "another service",
                "different job",
            )
        )
        and any(
            x in low
            for x in (
                "new time",
                "different time",
                "another time",
                "new day",
                "different day",
            )
        )
    )
    has_whole = any(
        x in low
        for x in (
            "whole appointment",
            "entire appointment",
            "full appointment",
            "whole booking",
            "entire booking",
            "change it all",
            "change everything",
        )
    )
    return (has_when and has_join) or has_dual_new or has_whole


def _service_type_or_time_reschedule_draft(
    *,
    last_customer: str,
    greeting: str,
    address_name: str | None,
    service_name: str | None,
    current_service: str | None = None,
    schedule_bit: str = "",
    is_first_reply: bool = False,
) -> ReplyDraft | None:
    """Service-type swap asks which job; pure time move asks day/time."""
    if looks_like_service_type_change(last_customer):
        if _mentions_time_change_with_service(last_customer):
            who = f"{address_name}, " if address_name and is_first_reply else ""
            cur = current_service or service_name
            svc_bit = f' вместо {cur}' if cur else ""
            ask = (
                f'{who}конечно — какая услуга{svc_bit}, какие день и время вам удобны?'
            )
            body = f"{greeting}{ask}" if is_first_reply and greeting else ask
            return ReplyDraft(
                body=body,
                follow_up_question='Какая услуга и новые день и время вам нужны?',
            )
        ask = counselor.ask_replacement_service(
            customer_name=address_name if is_first_reply else None,
            current_service=current_service or service_name,
        )
        body = f"{greeting}{ask}" if is_first_reply and greeting else ask
        return ReplyDraft(
            body=body,
            follow_up_question='Какую услугу выбрать вместо текущей?',
        )
    if counselor.looks_like_reschedule_desire(last_customer):
        existing = (schedule_bit or "").strip()
        if existing:
            return ReplyDraft(
                body=(
                    f'{greeting}конечно, перенесём запись. {existing} Какие новые день и время вам удобны?'
                ),
                follow_up_question='Какие новые день и время вам удобны?',
            )
        return ReplyDraft(
            body=counselor.summarize_reschedule_confirm(
                customer_name=address_name,
                service_name=service_name,
                when=None,
            ),
            follow_up_question='Какие новые день и время вам удобны?',
        )
    return None


def _next_appointment_bit(upcoming: list[dict]) -> str:
    if not upcoming:
        return ""
    appt = upcoming[0]
    when = _format_appt_when(appt.get("start"))
    service = appt.get("service_name")
    if when and service:
        return f' ваша запись на {service} — {when}.'
    if when:
        return f' ваша запись — {when}.'
    return ""


class ContextualReplyGenerator:
    """Heuristic reply templates grounded in agent outputs + memory (LLM-swappable)."""

    def generate(
        self,
        *,
        pipeline: PipelineResult,
        memory: ConversationMemorySnapshot,
        customer_name: str | None = None,
        shop_name: str | None = None,
    ) -> ReplyDraft:
        meta = pipeline.context.metadata or {}
        snapshot = meta.get("customer_snapshot") or {}
        upcoming = list(meta.get("upcoming_appointments") or [])
        # Speak only real names — never CRM placeholders / false extractions (e.g. Going).
        name = counselor.spoken_first_name(
            customer_name or snapshot.get("name")
        ) or None
        schedule_bit = _next_appointment_bit(upcoming)
        # Shop intro + name only on the first AI reply; later turns skip both.
        is_first_reply = not any(t.role == "assistant" for t in memory.turns)
        address_name = name if is_first_reply else None
        if is_first_reply:
            greeting = counselor.first_reply_prefix(
                shop_name=shop_name, customer_name=address_name
            )
        else:
            greeting = ""

        if pipeline.escalate:
            reason = (
                pipeline.supervisor.escalation_reason
                if pipeline.supervisor
                else 'нужна помощь сотрудника'
            )
            return ReplyDraft(
                body=(
                    f'{greeting}спасибо за обращение — сотрудник автосервиса скоро вам ответит.'
                ),
                send=True,
                reason=f"escalated: {reason}",
            )

        intent_stage = pipeline.stages.get("intent")
        intent = intent_stage.data.intent if intent_stage and intent_stage.data else None
        entities = (
            intent_stage.data.entities
            if intent_stage and intent_stage.data
            else {}
        )
        service_name = (
            entities.get("requested_service")
            or entities.get("service")
            or getattr(memory, "pending_service", None)
        )
        service_price = entities.get("service_price")
        scheduling = pipeline.stages.get("scheduling")
        sched_data = scheduling.data if scheduling else None
        decision = getattr(sched_data, "decision", None) if sched_data else None
        if sched_data and getattr(sched_data, "appointment", None):
            service_name = (
                getattr(sched_data.appointment, "service_name", None) or service_name
            )
        if decision is not None:
            service_name = getattr(decision, "service_name", None) or service_name

        candidates = list(entities.get("service_candidates") or [])
        if entities.get("service_needs_disambiguation") and candidates:
            return ReplyDraft(
                body=counselor.offer_service_candidates(
                    candidates, customer_name=address_name
                ),
                follow_up_question='Какая услуга вам нужна?',
            )

        last_customer = next(
            (
                t.content
                for t in reversed(memory.turns)
                if t.role in {"customer", "user"}
            ),
            "",
        )

        # Already booked this turn — confirm before asking for missing fields.
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and sched_data
            and sched_data.success
            and sched_data.appointment
        ):
            return ReplyDraft(
                body=counselor.summarize_done(
                    action="book",
                    customer_name=address_name,
                    service_name=service_name,
                    when=sched_data.appointment.start,
                ),
            )

        needs_name = counselor.needs_customer_name(customer_name or snapshot.get("name"))

        # Booking without a service → ask which service first (before day/time).
        # Time-change phrasing must not fall into this (keep existing service).
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and not service_name
            and not counselor.looks_like_reschedule_desire(last_customer)
        ):
            ask = counselor.ask_service(
                customer_name=None
            )
            body = f"{greeting}{ask}" if is_first_reply else ask
            return ReplyDraft(
                body=body,
                follow_up_question='Какая услуга вам нужна?',
            )

        # Misclassified BOOK that is actually a reschedule desire.
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and not service_name
            and counselor.looks_like_reschedule_desire(last_customer)
        ):
            if upcoming:
                service_name = upcoming[0].get("service_name") or service_name
            draft = _service_type_or_time_reschedule_draft(
                last_customer=last_customer,
                greeting=greeting,
                address_name=address_name,
                service_name=service_name,
                schedule_bit=schedule_bit,
                is_first_reply=is_first_reply,
            )
            if draft is not None:
                return draft

        # Customer answered the open "what can I help with?" with a booking desire.
        # Skip for reschedule/cancel — those keep the existing service and ask for time.
        if (
            not service_name
            and intent
            not in {
                CustomerIntent.RESCHEDULE,
                CustomerIntent.CANCEL_APPOINTMENT,
            }
            and counselor.looks_like_booking_desire(last_customer)
            and (
                counselor.is_purpose_question(memory.pending_question)
                or intent
                in {
                    CustomerIntent.OTHER,
                    CustomerIntent.NEW_CUSTOMER,
                    CustomerIntent.RETURNING_CUSTOMER,
                }
            )
        ):
            ask = counselor.ask_service(
                customer_name=None
            )
            body = f"{greeting}{ask}" if is_first_reply else ask
            return ReplyDraft(
                body=body,
                follow_up_question='Какая услуга вам нужна?',
            )

        # Preferred day/time rejected by scheduling (closed day, full slot, etc.)
        # must speak before partial needs_time re-asks (e.g. closed Sunday).
        sched_meta_early = (
            (getattr(sched_data, "metadata", None) or {}) if sched_data else {}
        )
        sched_message_early = (
            getattr(sched_data, "message", None) if sched_data else None
        )
        if (
            intent
            in {
                CustomerIntent.CHECK_AVAILABILITY,
                CustomerIntent.BOOK_APPOINTMENT,
                CustomerIntent.RESCHEDULE,
            }
            and (
                sched_message_early == "preferred_time_unavailable"
                or sched_meta_early.get("preferred_time_unavailable")
            )
        ):
            preferred = _parse_dt(entities.get("preferred_start")) or _parse_dt(
                sched_meta_early.get("preferred_start")
            )
            aspect = str(sched_meta_early.get("unavailable_aspect") or "both")
            if aspect not in {"date", "time", "both"}:
                aspect = "both"
            day_only = aspect == "date" and (
                entities.get("time_precision") in {"day", "part_of_day"}
                or (
                    bool(sched_meta_early.get("closed_day"))
                    and entities.get("time_precision") != "clock"
                )
            )
            follow = (
                'Какой другой день вам удобен?'
                if aspect == "date"
                else 'Какое другое время вам удобно?'
                if aspect == "time"
                else 'Какие другие день или время вам удобны?'
            )
            return ReplyDraft(
                body=counselor.time_unavailable(
                    preferred,
                    customer_name=address_name,
                    ask=aspect,
                    day_only=day_only,
                ),
                follow_up_question=follow,
            )

        # Partial date/time: day-only → ask clock; time-only → ask day.
        # Reschedule/cancel keep their own paths (acknowledge change, ask new time).
        if (
            intent
            not in {
                CustomerIntent.RESCHEDULE,
                CustomerIntent.CANCEL_APPOINTMENT,
            }
            and (
                entities.get("vague_time")
                or entities.get("needs_time")
                or entities.get("needs_date")
            )
        ):
            preferred_partial = _parse_dt(entities.get("preferred_start"))
            if intent == CustomerIntent.CHECK_AVAILABILITY and sched_data and sched_data.available_slots:
                ranges = [
                    (slot.start, getattr(slot, "end", None))
                    for slot in sched_data.available_slots
                ]
                body = counselor.offer_slots_spoken(
                    ranges,
                    customer_name=address_name,
                    service_name=service_name,
                    limit=4,
                )
                body = body.replace(
                    'Выбрать первый вариант или другое время?',
                    'Выбрать первый вариант? Ответьте YES или укажите удобные день и время.',
                )
                return ReplyDraft(
                    body=body,
                    follow_up_question='Какие день и время вам удобны для записи?',
                )
            if entities.get("needs_date") and not entities.get("needs_time"):
                return ReplyDraft(
                    body=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=preferred_partial,
                    ),
                    follow_up_question='Какой день вам удобен для записи?',
                )
            known_day = (
                preferred_partial
                if entities.get("time_precision") in {"day", "part_of_day"}
                else None
            )
            return ReplyDraft(
                body=counselor.ask_time(
                    customer_name=address_name,
                    service_name=service_name,
                    known_day=known_day,
                ),
                follow_up_question=(
                    'Какое время вам удобно для записи?'
                    if known_day
                    else 'Какие день и время вам удобны для записи?'
                ),
            )

        if memory.pending_question and intent == CustomerIntent.OTHER:
            # Never re-ask the same open purpose question after the customer answered.
            if counselor.is_purpose_question(memory.pending_question):
                if counselor.looks_like_reschedule_desire(last_customer):
                    if not service_name and upcoming:
                        service_name = upcoming[0].get("service_name") or service_name
                    draft = _service_type_or_time_reschedule_draft(
                        last_customer=last_customer,
                        greeting=greeting,
                        address_name=address_name,
                        service_name=service_name,
                        schedule_bit=schedule_bit,
                        is_first_reply=is_first_reply,
                    )
                    if draft is not None:
                        return draft
                if counselor.looks_like_booking_desire(last_customer):
                    return ReplyDraft(
                        body=counselor.ask_service(
                            customer_name=address_name
                        ),
                        follow_up_question='Какая услуга вам нужна?',
                    )
                return ReplyDraft(
                    body=(
                        f'{greeting}понятно — хотите записаться, перенести или отменить визит?'
                    ),
                    follow_up_question='Записать, перенести или отменить визит?',
                )
            return ReplyDraft(
                body=f'{greeting}понятно. {memory.pending_question}',
                follow_up_question=memory.pending_question,
            )

        if intent in {
            CustomerIntent.CHECK_AVAILABILITY,
            CustomerIntent.BOOK_APPOINTMENT,
        }:
            sched_meta = (getattr(sched_data, "metadata", None) or {}) if sched_data else {}
            sched_message = getattr(sched_data, "message", None) if sched_data else None
            if (
                sched_message == "preferred_time_unavailable"
                or sched_meta.get("preferred_time_unavailable")
            ):
                preferred = _parse_dt(entities.get("preferred_start")) or _parse_dt(
                    sched_meta.get("preferred_start")
                )
                aspect = str(sched_meta.get("unavailable_aspect") or "both")
                if aspect not in {"date", "time", "both"}:
                    aspect = "both"
                follow = (
                    'Какой другой день вам удобен?'
                    if aspect == "date"
                    else 'Какое другое время вам удобно?'
                    if aspect == "time"
                    else 'Какие другие день или время вам удобны?'
                )
                return ReplyDraft(
                    body=counselor.time_unavailable(
                        preferred, customer_name=address_name, ask=aspect
                    ),
                    follow_up_question=follow,
                )
            pending_when = _parse_dt(
                sched_meta.get("pending_slot_start")
            ) or _parse_dt(getattr(decision, "recommended_slot_start", None))
            # New / unnamed customers: ask for a name before the final confirm.
            if (
                intent == CustomerIntent.BOOK_APPOINTMENT
                and service_name
                and pending_when
                and needs_name
                and (
                    sched_message
                    in {
                        "awaiting_booking_confirmation",
                        "awaiting_customer_name",
                    }
                    or sched_meta.get("awaiting_confirmation")
                    or sched_meta.get("awaiting_customer_name")
                )
            ):
                ask = counselor.ask_name()
                body = f"{greeting}{ask}" if is_first_reply else ask
                return ReplyDraft(
                    body=body,
                    follow_up_question=ask,
                )
            # Only confirm a slot scheduling actually held — never echo a raw
            # preferred clock time just because other openings exist (that can
            # be outside business hours).
            if (
                intent == CustomerIntent.BOOK_APPOINTMENT
                and service_name
                and pending_when
                and sched_data
                and (
                    sched_message == "awaiting_booking_confirmation"
                    or sched_meta.get("awaiting_confirmation")
                )
                and not needs_name
            ):
                return ReplyDraft(
                    body=counselor.summarize_booking_confirm(
                        # Confirmation is a natural place to use their name (kind + clear).
                        customer_name=name,
                        service_name=service_name,
                        when=pending_when,
                    ),
                    follow_up_question='Записать вас?',
                )
            # Availability ask → list openings. Booking → ask when they want to come.
            if intent == CustomerIntent.CHECK_AVAILABILITY:
                if sched_data and sched_data.available_slots:
                    ranges = [
                        (slot.start, getattr(slot, "end", None))
                        for slot in sched_data.available_slots
                    ]
                    body = counselor.offer_slots_spoken(
                        ranges,
                        customer_name=address_name,
                        service_name=service_name,
                        limit=4,
                    )
                    body = body.replace(
                        'Выбрать первый вариант или другое время?',
                        'Выбрать первый вариант? Ответьте YES или укажите удобные день и время.',
                    )
                    return ReplyDraft(
                        body=body,
                        follow_up_question='Какие день и время вам удобны для записи?',
                    )
                if schedule_bit:
                    return ReplyDraft(
                        body=(
                            f"{greeting}{schedule_bit.strip()} Выбрать другое время{(' for ' + service_name if service_name else '')} или оставить текущее?"
                        ),
                        follow_up_question='Оставить текущую запись или выбрать новое время?',
                    )
                return ReplyDraft(
                    body=(
                        f"{greeting}на ближайшую неделю свободного времени{(' for ' + service_name if service_name else '')} не вижу. Проверить другой день?"
                    ),
                    follow_up_question='Другой диапазон дат?',
                )
            known_clock = _parse_dt(entities.get("preferred_start")) or _parse_dt(
                sched_meta.get("preferred_start")
            )
            if (
                entities.get("time_precision") == "time_only"
                or sched_meta.get("time_precision") == "time_only"
                or entities.get("needs_date")
                or sched_meta.get("needs_date")
            ) and known_clock is not None:
                return ReplyDraft(
                    body=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=known_clock,
                    ),
                    follow_up_question='Какой день вам удобен для записи?',
                )
            return ReplyDraft(
                body=counselor.ask_time(
                    customer_name=address_name, service_name=service_name
                ),
                follow_up_question='Какие день и время вам удобны?',
            )

        if intent == CustomerIntent.RESCHEDULE:
            named_this_turn = bool(
                entities.get("requested_service") or entities.get("service")
            )
            if (
                looks_like_service_type_change(last_customer)
                and not named_this_turn
                and not entities.get("prefer_earliest")
                and not entities.get("prefer_latest")
            ):
                current = upcoming[0].get("service_name") if upcoming else None
                if _mentions_time_change_with_service(last_customer):
                    draft = _service_type_or_time_reschedule_draft(
                        last_customer=last_customer,
                        greeting="",
                        address_name=address_name,
                        service_name=service_name,
                        current_service=current or service_name,
                        is_first_reply=False,
                    )
                    if draft is not None:
                        return draft
                return ReplyDraft(
                    body=counselor.ask_replacement_service(
                        customer_name=address_name,
                        current_service=current or service_name,
                    ),
                    follow_up_question='Какую услугу выбрать вместо текущей?',
                )
            if not service_name and upcoming:
                service_name = upcoming[0].get("service_name") or service_name
            if sched_data and sched_data.success and sched_data.appointment:
                return ReplyDraft(
                    body=counselor.summarize_done(
                        action="reschedule",
                        customer_name=address_name,
                        service_name=service_name,
                        when=sched_data.appointment.start,
                    )
                )
            sched_meta = (getattr(sched_data, "metadata", None) or {}) if sched_data else {}
            sched_message = getattr(sched_data, "message", None) if sched_data else None
            if sched_message == "no_appointment_to_reschedule" or sched_meta.get(
                "no_appointment"
            ):
                return ReplyDraft(
                    body=(
                        f'{greeting}будущей записи для переноса не вижу. Создать новую запись?'
                    ),
                    follow_up_question='Записать вас или помочь с другим вопросом?',
                )
            if (
                sched_message == "preferred_time_unavailable"
                or sched_meta.get("preferred_time_unavailable")
            ):
                preferred = _parse_dt(entities.get("preferred_start")) or _parse_dt(
                    sched_meta.get("preferred_start")
                )
                aspect = str(sched_meta.get("unavailable_aspect") or "both")
                if aspect not in {"date", "time", "both"}:
                    aspect = "both"
                follow = (
                    'Какой другой день вам удобен?'
                    if aspect == "date"
                    else 'Какое другое время вам удобно?'
                    if aspect == "time"
                    else 'Какие другие день или время вам удобны?'
                )
                return ReplyDraft(
                    body=counselor.time_unavailable(
                        preferred, customer_name=address_name, ask=aspect
                    ),
                    follow_up_question=follow,
                )
            pending_when = _parse_dt(
                sched_meta.get("pending_slot_start")
            ) or _parse_dt(getattr(decision, "recommended_slot_start", None))
            has_preference = bool(
                entities.get("preferred_start")
                or entities.get("prefer_earliest")
                or entities.get("prefer_latest")
            )
            customer_chose_clock = (
                has_preference
                and entities.get("time_precision") == "clock"
                and not entities.get("needs_date")
                and not entities.get("needs_time")
            )
            # Only confirm a slot the customer actually picked — never invent one.
            if pending_when and customer_chose_clock:
                return ReplyDraft(
                    body=counselor.summarize_reschedule_confirm(
                        customer_name=address_name,
                        service_name=service_name,
                        when=pending_when,
                    ),
                    follow_up_question='Перенести запись?',
                )
            preferred_partial = _parse_dt(entities.get("preferred_start"))
            if entities.get("needs_date") and not entities.get("needs_time"):
                return ReplyDraft(
                    body=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=preferred_partial,
                    ),
                    follow_up_question='Какой день вам удобен для записи?',
                )
            if entities.get("needs_time") or entities.get("vague_time"):
                known_day = (
                    preferred_partial
                    if entities.get("time_precision") in {"day", "part_of_day"}
                    else None
                )
                return ReplyDraft(
                    body=counselor.ask_time(
                        customer_name=address_name,
                        service_name=service_name,
                        known_day=known_day,
                    ),
                    follow_up_question=(
                        'Какое время вам удобно для записи?'
                        if known_day
                        else 'Какие новые день и время вам удобны?'
                    ),
                )
            # Soft day / earliest preference → list openings. Bare "change time" → ask.
            if sched_data and sched_data.available_slots and has_preference:
                ranges = [
                    (slot.start, getattr(slot, "end", None))
                    for slot in sched_data.available_slots
                ]
                body = counselor.offer_slots_spoken(
                    ranges,
                    customer_name=address_name,
                    service_name=service_name,
                    limit=4,
                )
                return ReplyDraft(
                    body=f'Конечно, перенесём запись. {body}',
                    follow_up_question='Какие новые день и время вам удобны?',
                )
            existing = schedule_bit.strip()
            if existing:
                return ReplyDraft(
                    body=(
                        f'{greeting}конечно, перенесём запись. {existing} Какие новые день и время вам удобны?'
                    ),
                    follow_up_question='Какие новые день и время вам удобны?',
                )
            return ReplyDraft(
                body=counselor.summarize_reschedule_confirm(
                    customer_name=address_name,
                    service_name=service_name,
                    when=None,
                ),
                follow_up_question='Какие новые день и время вам удобны?',
            )

        if intent == CustomerIntent.CANCEL_APPOINTMENT:
            if sched_data and sched_data.success and sched_data.appointment:
                return ReplyDraft(
                    body=counselor.summarize_done(
                        action="cancel",
                        customer_name=address_name,
                        service_name=service_name,
                    )
                )
            if sched_data and (
                getattr(sched_data, "message", None) == "no_appointment_to_cancel"
                or (getattr(sched_data, "metadata", None) or {}).get("no_appointment")
            ):
                return ReplyDraft(
                    body=(
                        f'{greeting}будущей записи в расписании не вижу. Создать новую?'
                    ),
                    follow_up_question='Записать вас или помочь с другим вопросом?',
                )
            existing = schedule_bit.strip()
            when = None
            svc = service_name
            if upcoming:
                when = _format_appt_when(upcoming[0].get("start"))
                svc = upcoming[0].get("service_name") or svc
            body = counselor.summarize_cancel_confirm(
                customer_name=address_name,
                service_name=svc,
                when=when,
            )
            if existing and not when:
                body = f"{greeting}{existing} {body}"
            return ReplyDraft(
                body=body,
                follow_up_question='Подтвердите отмену?',
            )

        if intent == CustomerIntent.ASK_REPAIR_STATUS:
            status_hint = schedule_bit.strip()
            if status_hint:
                return ReplyDraft(
                    body=(
                        f'{greeting}{status_hint} Уточняю состояние автомобиля — сотрудник скоро вам напишет.'
                    ),
                    follow_up_question='Номер заказ-наряда или автомобиль (год/марка/модель)?',
                )
            return ReplyDraft(
                body=(
                    f'{greeting}уточняю состояние автомобиля. Сотрудник скоро напишет вам — отправьте номер заказ-наряда или год, марку и модель для ускорения поиска.'
                ),
                follow_up_question='Номер заказ-наряда или автомобиль (год/марка/модель)?',
            )

        if intent == CustomerIntent.PRICE_QUESTION:
            if service_name and service_price is not None:
                return ReplyDraft(
                    body=(
                        f'{greeting}{service_name} обычно стоит около ${service_price}. Записать вас?'
                    ),
                    follow_up_question='Записать на эту услугу?',
                )
            if service_name:
                return ReplyDraft(
                    body=(
                        f'{greeting}точную стоимость {service_name} подтвердит консультант. Пока записать вас?'
                    ),
                    follow_up_question='Записать на эту услугу?',
                )
            return ReplyDraft(
                body=counselor.ask_service(customer_name=address_name),
                follow_up_question='Для какой услуги нужна стоимость?',
            )

        if intent == CustomerIntent.MAINTENANCE_QUESTION:
            if service_name:
                return ReplyDraft(
                    body=f'{greeting}да, мы выполняем {service_name}. Записать вас?',
                    follow_up_question=f'Записать на {service_name}?',
                )
            return ReplyDraft(
                body=(
                    f'{greeting}обычно мы рекомендуем менять масло каждые 5 000 миль, а тормоза проверять примерно каждые 20 000. Записать вас?'
                ),
                follow_up_question='Записать на обслуживание?',
            )

        if intent == CustomerIntent.EMERGENCY:
            return ReplyDraft(
                body=(
                    f'{greeting}сожалею, что вы столкнулись с этим. Мы отметили обращение как срочное; сотрудник свяжется с вами как можно скорее. При опасности звоните в экстренные службы.'
                ),
                reason="emergency",
            )

        if intent == CustomerIntent.COMPLAINT:
            return ReplyDraft(
                body=(
                    f'{greeting}очень жаль, что так получилось. Владелец или руководитель уведомлён и свяжется с вами лично.'
                ),
                reason="complaint",
            )

        if intent == CustomerIntent.NEW_CUSTOMER:
            shop = (shop_name or "").strip()
            if counselor.looks_like_booking_desire(last_customer):
                ask = counselor.ask_service(
                    customer_name=None
                )
                body = f"{greeting}{ask}" if is_first_reply else ask
                return ReplyDraft(
                    body=body,
                    follow_up_question='Какая услуга вам нужна?',
                )
            if is_first_reply and shop:
                body = (
                    f'{greeting}{counselor.ask_purpose()} Помогу записаться, перенести или отменить визит.'
                )
            elif shop:
                body = (
                    f'{greeting}добро пожаловать в {shop}! Чем мы можем помочь?'
                )
            else:
                body = (
                    f'{greeting}добро пожаловать! Чем мы можем помочь?'
                )
            return ReplyDraft(
                body=body,
                follow_up_question=counselor.ask_purpose()
                if is_first_reply
                else 'Чем мы можем вам помочь?',
            )

        if schedule_bit:
            return ReplyDraft(
                body=(
                    f'{greeting}{schedule_bit.strip()} Могу помочь изменить запись, что-то уточнить или решить другой вопрос.'
                ),
                follow_up_question='Чем я могу вам помочь?',
            )
        if counselor.looks_like_reschedule_desire(last_customer):
            draft = _service_type_or_time_reschedule_draft(
                last_customer=last_customer,
                greeting=greeting,
                address_name=address_name,
                service_name=service_name,
                schedule_bit=schedule_bit,
                is_first_reply=is_first_reply,
            )
            if draft is not None:
                return draft
        if counselor.looks_like_booking_desire(last_customer):
            ask = counselor.ask_service(
                customer_name=None
            )
            body = f"{greeting}{ask}" if is_first_reply else ask
            return ReplyDraft(
                body=body,
                follow_up_question='С какой услугой вам помочь?',
            )
        if is_first_reply:
            return ReplyDraft(
                body=(
                    f'{greeting}{counselor.ask_purpose()} Помогу записаться, перенести или отменить визит.'
                ),
                follow_up_question=counselor.ask_purpose(),
            )
        return ReplyDraft(
            body=(
                f'{greeting}{counselor.ask_purpose()} Помогу записаться, перенести или отменить визит.'
            ),
            follow_up_question='Чем я могу вам помочь?',
        )

