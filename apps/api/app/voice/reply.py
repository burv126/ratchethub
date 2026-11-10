"""Spoken reply drafting for phone conversations."""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass

from app.agents.counselor import persona as counselor
from app.agents.intent.models import CustomerIntent
from app.agents.intent.reschedule_text import looks_like_service_type_change
from app.agents.orchestrator import PipelineResult
from app.voice.memory import CallMemorySnapshot


@dataclass(slots=True)
class VoiceReplyDraft:
    text: str
    follow_up_question: str | None = None
    escalate_to_human: bool = False
    end_call: bool = False
    reason: str | None = None


def _parse_dt(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt
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
    # "new service and new time" / dual different without "and" already covered
    has_dual_new = (
        any(x in low for x in ("new service", "different service", "another service", "different job"))
        and any(x in low for x in ("new time", "different time", "another time", "new day", "different day"))
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
    address_name: str | None,
    service_name: str | None,
    current_service: str | None = None,
) -> VoiceReplyDraft | None:
    """Service-type swap asks which job; pure time move asks day/time."""
    if looks_like_service_type_change(last_customer):
        if _mentions_time_change_with_service(last_customer):
            who = f"{address_name}, " if address_name else ""
            cur = current_service or service_name
            svc_bit = f' вместо {cur}' if cur else ""
            return VoiceReplyDraft(
                text=(
                    f'{who}конечно — какая услуга{svc_bit}, какие день и время вам удобны?'
                ),
                follow_up_question='Какая услуга и новые день и время вам нужны?',
            )
        return VoiceReplyDraft(
            text=counselor.ask_replacement_service(
                customer_name=address_name,
                current_service=current_service or service_name,
            ),
            follow_up_question='Какую услугу выбрать вместо текущей?',
        )
    if counselor.looks_like_reschedule_desire(last_customer):
        return VoiceReplyDraft(
            text=counselor.summarize_reschedule_confirm(
                customer_name=address_name,
                service_name=service_name,
                when=None,
            ),
            follow_up_question='Какие новые день и время вам удобны?',
        )
    return None


class VoiceReplyGenerator:
    """Short, speakable replies grounded in agent outputs + call memory."""

    def greeting(
        self,
        *,
        customer_name: str | None = None,
        shop_name: str | None = None,
    ) -> VoiceReplyDraft:
        return VoiceReplyDraft(
            text=counselor.greeting(
                shop_name=shop_name,
                customer_name=counselor.spoken_first_name(customer_name) or None,
            ),
            follow_up_question=counselor.ask_purpose(),
        )

    def generate(
        self,
        *,
        pipeline: PipelineResult,
        memory: CallMemorySnapshot,
        customer_name: str | None = None,
        shop_name: str | None = None,
    ) -> VoiceReplyDraft:
        # Speak only real names — never CRM placeholders / false extractions (e.g. Going).
        name = counselor.spoken_first_name(customer_name) or None
        # Address by name only on the first AI turn (opening); later turns skip it.
        is_first_reply = not any(t.role == "assistant" for t in memory.turns)
        address_name = name if is_first_reply else None
        _ = shop_name  # reserved for future persona injection in mid-call turns
        meta = pipeline.context.metadata or {}
        snapshot = meta.get("customer_snapshot") or {}

        if pipeline.escalate:
            who = f'{address_name}, подождите немного — ' if address_name else 'Подождите немного — '
            return VoiceReplyDraft(
                text=(
                    f'{who}сейчас подключу сотрудника, который поможет. Пожалуйста, оставайтесь на линии.'
                ),
                escalate_to_human=True,
                reason=(
                    pipeline.supervisor.escalation_reason
                    if pipeline.supervisor
                    else "escalation"
                ),
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
            or memory.pending_service
        )
        scheduling = pipeline.stages.get("scheduling")
        sched = scheduling.data if scheduling else None
        revenue = pipeline.stages.get("revenue")
        rev = revenue.data if revenue else None
        if sched and getattr(sched, "appointment", None):
            service_name = getattr(sched.appointment, "service_name", None) or service_name
        decision = getattr(sched, "decision", None) if sched else None
        if decision is not None:
            service_name = getattr(decision, "service_name", None) or service_name

        candidates = list(entities.get("service_candidates") or [])
        if entities.get("service_needs_disambiguation") and candidates:
            return VoiceReplyDraft(
                text=counselor.offer_service_candidates(
                    candidates, customer_name=address_name
                ),
                follow_up_question='Какая услуга вам нужна?',
            )

        last_customer = next(
            (
                t.text
                for t in reversed(memory.turns)
                if t.role in {"caller", "customer", "user"}
            ),
            "",
        )

        # Off-topic chatter (weather, jokes, news…) — kindly guide back to service.
        # Run before needs_time / booking paths so leftover date words ("today")
        # do not pull the call into a scheduling flow.
        if (
            counselor.looks_like_off_topic(last_customer)
            and not service_name
            and intent
            not in {
                CustomerIntent.BOOK_APPOINTMENT,
                CustomerIntent.CHECK_AVAILABILITY,
                CustomerIntent.RESCHEDULE,
                CustomerIntent.CANCEL_APPOINTMENT,
                CustomerIntent.ASK_REPAIR_STATUS,
                CustomerIntent.PRICE_QUESTION,
                CustomerIntent.MAINTENANCE_QUESTION,
                CustomerIntent.EMERGENCY,
                CustomerIntent.COMPLAINT,
            }
        ):
            return VoiceReplyDraft(
                text=counselor.redirect_to_service_topic(
                    customer_name=address_name
                ),
                follow_up_question='Чем помочь с обслуживанием автомобиля?',
            )

        # Already booked this turn — confirm, then keep the line open.
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and sched
            and sched.success
            and sched.appointment
        ):
            return VoiceReplyDraft(
                text=counselor.summarize_done(
                    action="book",
                    customer_name=address_name,
                    service_name=service_name,
                    when=sched.appointment.start,
                    keep_open=True,
                ),
                follow_up_question='Могу помочь ещё с чем-нибудь?',
            )

        needs_name = counselor.needs_customer_name(
            customer_name or snapshot.get("name")
        )

        # Booking without a service → ask which service first (before day/time).
        # Time-change phrasing must not fall into this (keep existing service).
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and not service_name
            and not counselor.looks_like_reschedule_desire(last_customer)
        ):
            return VoiceReplyDraft(
                text=counselor.ask_service(customer_name=address_name),
                follow_up_question='Какая услуга вам нужна?',
            )

        # Misclassified BOOK that is actually a reschedule desire.
        if (
            intent == CustomerIntent.BOOK_APPOINTMENT
            and not service_name
            and counselor.looks_like_reschedule_desire(last_customer)
        ):
            draft = _service_type_or_time_reschedule_draft(
                last_customer=last_customer,
                address_name=address_name,
                service_name=service_name,
            )
            if draft is not None:
                return draft

        # Customer answered the open purpose question with a booking desire.
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
            return VoiceReplyDraft(
                text=counselor.ask_service(customer_name=address_name),
                follow_up_question='Какая услуга вам нужна?',
            )

        # Preferred day/time rejected by scheduling (closed day, full slot, etc.)
        # must speak before partial needs_time re-asks (e.g. closed Sunday).
        sched_meta_early = (getattr(sched, "metadata", None) or {}) if sched else {}
        sched_message_early = getattr(sched, "message", None) if sched else None
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
            return VoiceReplyDraft(
                text=counselor.time_unavailable(
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
            if intent == CustomerIntent.CHECK_AVAILABILITY and sched and sched.available_slots:
                ranges = [
                    (slot.start, getattr(slot, "end", None))
                    for slot in sched.available_slots
                ]
                return VoiceReplyDraft(
                    text=counselor.offer_slots_spoken(
                        ranges,
                        customer_name=address_name,
                        service_name=service_name,
                    ),
                    follow_up_question='Какое время вам удобно?',
                )
            # Clock/part without a day → only ask for the day.
            if entities.get("needs_date") and not entities.get("needs_time"):
                return VoiceReplyDraft(
                    text=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=preferred_partial,
                    ),
                    follow_up_question='Какой день вам удобен?',
                )
            # Day known, clock missing → only ask for the time.
            known_day = (
                preferred_partial
                if entities.get("time_precision") in {"day", "part_of_day"}
                else None
            )
            return VoiceReplyDraft(
                text=counselor.ask_time(
                    customer_name=address_name,
                    service_name=service_name,
                    known_day=known_day,
                ),
                follow_up_question=(
                    'Какое время вам удобно?' if known_day else 'Какие день и время вам удобны?'
                ),
            )

        if intent in {
            CustomerIntent.CHECK_AVAILABILITY,
            CustomerIntent.BOOK_APPOINTMENT,
        }:
            sched_meta = (getattr(sched, "metadata", None) or {}) if sched else {}
            sched_message = getattr(sched, "message", None) if sched else None
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
                day_only = aspect == "date" and (
                    entities.get("time_precision") in {"day", "part_of_day"}
                    or (
                        bool(sched_meta.get("closed_day"))
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
                return VoiceReplyDraft(
                    text=counselor.time_unavailable(
                        preferred,
                        customer_name=address_name,
                        ask=aspect,
                        day_only=day_only,
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
                return VoiceReplyDraft(
                    text=ask,
                    follow_up_question=ask,
                )
            # Only confirm a slot scheduling actually held — never echo a raw
            # preferred clock time just because other openings exist.
            if (
                intent == CustomerIntent.BOOK_APPOINTMENT
                and service_name
                and pending_when
                and sched
                and (
                    sched_message == "awaiting_booking_confirmation"
                    or sched_meta.get("awaiting_confirmation")
                )
                and not needs_name
            ):
                return VoiceReplyDraft(
                    text=counselor.summarize_booking_confirm(
                        # Confirmation is a natural place to use their name (kind + clear).
                        customer_name=name,
                        service_name=service_name,
                        when=pending_when,
                    ),
                    follow_up_question='Записать вас?',
                )
            if intent == CustomerIntent.CHECK_AVAILABILITY:
                if sched and sched.available_slots:
                    ranges = [
                        (slot.start, getattr(slot, "end", None))
                        for slot in sched.available_slots
                    ]
                    return VoiceReplyDraft(
                        text=counselor.offer_slots_spoken(
                            ranges,
                            customer_name=address_name,
                            service_name=service_name,
                        ),
                        follow_up_question='Какое время вам удобно?',
                    )
                who = f"{address_name}, " if address_name else ""
                return VoiceReplyDraft(
                    text=(
                        f'{who}на ближайшую неделю свободного времени не вижу. Проверить другой день?'
                    ),
                    follow_up_question='Другой день?',
                )
            # Clock already known (time_only / needs_date) — do not re-ask the hour.
            known_clock = _parse_dt(entities.get("preferred_start")) or _parse_dt(
                sched_meta.get("preferred_start")
            )
            if (
                entities.get("time_precision") == "time_only"
                or sched_meta.get("time_precision") == "time_only"
                or entities.get("needs_date")
                or sched_meta.get("needs_date")
            ) and known_clock is not None:
                return VoiceReplyDraft(
                    text=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=known_clock,
                    ),
                    follow_up_question='Какой день вам удобен?',
                )
            return VoiceReplyDraft(
                text=counselor.ask_time(
                    customer_name=address_name, service_name=service_name
                ),
                follow_up_question='Какие день и время вам удобны?',
            )

        if intent == CustomerIntent.RESCHEDULE:
            # Prefer known upcoming visit details (cleared after a book in-call).
            upcoming = list(meta.get("upcoming_appointments") or [])
            named_this_turn = bool(
                entities.get("requested_service") or entities.get("service")
            )
            # "Change the service type" without a destination → ask which job,
            # not "what new day/time" (that feels like we ignored them).
            # Ignore stashed preferred_start from a prior turn — type-swap is
            # a new job ask first; day/clock stays until they name a service.
            if (
                looks_like_service_type_change(last_customer)
                and not named_this_turn
                and not entities.get("prefer_earliest")
                and not entities.get("prefer_latest")
            ):
                current = None
                if upcoming:
                    current = upcoming[0].get("service_name")
                # Compound "service and time" — ask for both halves.
                if _mentions_time_change_with_service(last_customer):
                    draft = _service_type_or_time_reschedule_draft(
                        last_customer=last_customer,
                        address_name=address_name,
                        service_name=service_name,
                        current_service=current or service_name,
                    )
                    if draft is not None:
                        return draft
                return VoiceReplyDraft(
                    text=counselor.ask_replacement_service(
                        customer_name=address_name,
                        current_service=current or service_name,
                    ),
                    follow_up_question='Какую услугу выбрать вместо текущей?',
                )
            if not service_name and upcoming:
                service_name = upcoming[0].get("service_name") or service_name
            if sched and sched.success and sched.appointment:
                return VoiceReplyDraft(
                    text=counselor.summarize_done(
                        action="reschedule",
                        customer_name=address_name,
                        service_name=service_name,
                        when=sched.appointment.start,
                        keep_open=True,
                    ),
                    follow_up_question='Могу помочь ещё с чем-нибудь?',
                )
            sched_meta = (getattr(sched, "metadata", None) or {}) if sched else {}
            sched_message = getattr(sched, "message", None) if sched else None
            if sched_message == "no_appointment_to_reschedule" or sched_meta.get(
                "no_appointment"
            ):
                who = f"{address_name}, " if address_name else ""
                return VoiceReplyDraft(
                    text=(
                        f'{who}будущей записи для переноса не вижу. Хотите записаться на новый визит?'
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
                return VoiceReplyDraft(
                    text=counselor.time_unavailable(
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
            # Only confirm a slot the customer actually picked — service name optional.
            if pending_when and customer_chose_clock:
                return VoiceReplyDraft(
                    text=counselor.summarize_reschedule_confirm(
                        customer_name=address_name,
                        service_name=service_name,
                        when=pending_when,
                    ),
                    follow_up_question='Перенести запись?',
                )
            # Incomplete answers during reschedule — pin down the missing half.
            preferred_partial = _parse_dt(entities.get("preferred_start"))
            if entities.get("needs_date") and not entities.get("needs_time"):
                return VoiceReplyDraft(
                    text=counselor.ask_date(
                        customer_name=address_name,
                        service_name=service_name,
                        known_time=preferred_partial,
                    ),
                    follow_up_question='Какой день вам удобен?',
                )
            if entities.get("needs_time") or entities.get("vague_time"):
                known_day = (
                    preferred_partial
                    if entities.get("time_precision") in {"day", "part_of_day"}
                    else None
                )
                return VoiceReplyDraft(
                    text=counselor.ask_time(
                        customer_name=address_name,
                        service_name=service_name,
                        known_day=known_day,
                    ),
                    follow_up_question=(
                        'Какое время вам удобно?' if known_day else 'Какие день и время вам удобны?'
                    ),
                )
            if sched and sched.available_slots and has_preference:
                ranges = [
                    (slot.start, getattr(slot, "end", None))
                    for slot in sched.available_slots
                ]
                spoken = counselor.offer_slots_spoken(
                    ranges, customer_name=address_name, service_name=service_name
                )
                return VoiceReplyDraft(
                    text=spoken.replace('Есть', 'конечно — есть').replace(
                        'Выбрать первый вариант или другое время?',
                        'Какой вариант подходит, или выбрать другой день?',
                    ),
                    follow_up_question='Какое новое время вам удобно?',
                )
            return VoiceReplyDraft(
                text=counselor.summarize_reschedule_confirm(
                    customer_name=address_name,
                    service_name=service_name,
                    when=None,
                ),
                follow_up_question='Какие новые день и время вам удобны?',
            )

        if intent == CustomerIntent.CANCEL_APPOINTMENT:
            if sched and sched.success and sched.appointment:
                return VoiceReplyDraft(
                    text=counselor.summarize_done(
                        action="cancel",
                        customer_name=address_name,
                        service_name=service_name,
                        keep_open=True,
                    ),
                    follow_up_question='Могу помочь ещё с чем-нибудь?',
                )
            if sched and (
                getattr(sched, "message", None) == "no_appointment_to_cancel"
                or (getattr(sched, "metadata", None) or {}).get("no_appointment")
            ):
                who = f"{address_name}, " if address_name else ""
                return VoiceReplyDraft(
                    text=(
                        f'{who}будущей записи в расписании не вижу. Хотите записаться на визит?'
                    ),
                    follow_up_question='Записать вас или помочь с другим вопросом?',
                )
            # Prefer known upcoming visit details in the confirmation ask.
            upcoming = list(meta.get("upcoming_appointments") or [])
            when = None
            svc = service_name
            if upcoming:
                when = _parse_dt(upcoming[0].get("start"))
                svc = upcoming[0].get("service_name") or svc
            return VoiceReplyDraft(
                text=counselor.summarize_cancel_confirm(
                    customer_name=address_name,
                    service_name=svc,
                    when=when,
                ),
                follow_up_question='Подтвердите отмену?',
            )

        if intent == CustomerIntent.ASK_REPAIR_STATUS:
            who = f"{address_name}, " if address_name else ""
            return VoiceReplyDraft(
                text=(
                    f'{who}сейчас уточню. Сотрудник скоро сообщит подробности. У вас есть номер заказ-наряда?'
                ),
                follow_up_question='Номер заказ-наряда?',
            )

        if intent == CustomerIntent.PRICE_QUESTION:
            service_price = entities.get("service_price")
            who = f"{address_name}, " if address_name else ""
            if service_name and service_price is not None:
                return VoiceReplyDraft(
                    text=(
                        f'{who}{service_name} обычно стоит около ${service_price}. Записать вас?'
                    ),
                    follow_up_question=f'Записать на {service_name}?',
                )
            if service_name:
                return VoiceReplyDraft(
                    text=(
                        f'{who}могу уточнить стоимость {service_name}. Записать вас?'
                    ),
                    follow_up_question=f'Записать на {service_name}?',
                )
            return VoiceReplyDraft(
                text=counselor.ask_service(customer_name=address_name),
                follow_up_question='Какая услуга вам нужна?',
            )

        if intent == CustomerIntent.MAINTENANCE_QUESTION:
            who = f"{address_name}, " if address_name else ""
            if rev and rev.maintenance_reminders:
                tip = str(
                    rev.maintenance_reminders[0].get("service") or ""
                ).replace("_", " ").strip()
                if tip:
                    return VoiceReplyDraft(
                        text=(
                            f'{who}для вашего автомобиля скоро потребуется {tip}. Записать вас?'
                        ),
                        follow_up_question='Записать на обслуживание?',
                    )
            if service_name:
                return VoiceReplyDraft(
                    text=(
                        f'{who}да, мы выполняем {service_name}. Записать вас?'
                    ),
                    follow_up_question=f'Записать на {service_name}?',
                )
            return VoiceReplyDraft(
                text=f'{who}записать вас на визит?',
                follow_up_question='Записать вас?',
            )

        text_blob = " ".join(t.text.lower() for t in memory.turns[-3:])
        if "approve" in text_blob or "estimate" in text_blob:
            who = f"{address_name}, " if address_name else ""
            return VoiceReplyDraft(
                text=(
                    f'{who}понятно, ваше решение по смете записано. Сообщим автосервису. Могу помочь ещё с чем-нибудь?'
                )
            )

        if intent == CustomerIntent.EMERGENCY:
            who = f"{address_name}, " if address_name else ""
            return VoiceReplyDraft(
                text=(
                    f'{who}сожалею, что вы столкнулись с этим. Сейчас соединю с автосервисом — оставайтесь на линии.'
                ),
                escalate_to_human=True,
                reason="emergency",
            )

        if intent == CustomerIntent.COMPLAINT:
            who = f"{address_name}, " if address_name else ""
            return VoiceReplyDraft(
                text=(
                    f'{who}очень жаль, что так получилось. Сейчас подключу владельца — одну минуту.'
                ),
                escalate_to_human=True,
                reason="complaint",
            )

        if memory.pending_question and intent == CustomerIntent.OTHER:
            who = f"{address_name}, " if address_name else ""
            # After "anything else?" — never re-ask; farewell on decline / wrap-up.
            if counselor.is_anything_else_question(memory.pending_question):
                if counselor.looks_like_soft_no(last_customer) or counselor.looks_like_farewell(
                    last_customer
                ):
                    return self.farewell()
                if counselor.looks_like_reschedule_desire(last_customer):
                    draft = _service_type_or_time_reschedule_draft(
                        last_customer=last_customer,
                        address_name=address_name,
                        service_name=service_name,
                    )
                    if draft is not None:
                        return draft
                if counselor.looks_like_booking_desire(last_customer):
                    return VoiceReplyDraft(
                        text=counselor.ask_service(customer_name=address_name),
                        follow_up_question='Какая услуга вам нужна?',
                    )
                # Unclear OTHER after the offer — soft close instead of looping the same ask.
                return self.farewell()
            if counselor.is_purpose_question(memory.pending_question):
                if counselor.looks_like_reschedule_desire(last_customer):
                    draft = _service_type_or_time_reschedule_draft(
                        last_customer=last_customer,
                        address_name=address_name,
                        service_name=service_name,
                    )
                    if draft is not None:
                        return draft
                if counselor.looks_like_booking_desire(last_customer):
                    return VoiceReplyDraft(
                        text=counselor.ask_service(customer_name=address_name),
                        follow_up_question='Какая услуга вам нужна?',
                    )
                # Off-topic / unclear after the open purpose ask — guide back to service.
                return VoiceReplyDraft(
                    text=counselor.redirect_to_service_topic(
                        customer_name=address_name
                    ),
                    follow_up_question='Чем помочь с обслуживанием автомобиля?',
                )
            return VoiceReplyDraft(
                text=f'{who}понятно. {memory.pending_question}',
                follow_up_question=memory.pending_question,
            )

        draft = _service_type_or_time_reschedule_draft(
            last_customer=last_customer,
            address_name=address_name,
            service_name=service_name,
        )
        if draft is not None:
            return draft

        if counselor.looks_like_booking_desire(last_customer) and not service_name:
            return VoiceReplyDraft(
                text=counselor.ask_service(customer_name=address_name),
                follow_up_question='Какая услуга вам нужна?',
            )

        # Unrelated / unclear intent with no booking path — kindly stay on service topics.
        return VoiceReplyDraft(
            text=counselor.redirect_to_service_topic(customer_name=address_name),
            follow_up_question='Чем помочь с обслуживанием автомобиля?',
        )

    def farewell(self) -> VoiceReplyDraft:
        return VoiceReplyDraft(
            text='Спасибо за звонок! Всего доброго и хорошего дня.',
            end_call=True,
        )
