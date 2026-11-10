"""Bounded Russian input aliases for existing English parsers; never stored."""

import re


def _replace(text: str, aliases: tuple[tuple[str, str], ...]) -> str:
    for pattern, canonical in aliases:
        text = re.sub(rf"(?<!\w)(?:{pattern})(?!\w)", canonical, text, flags=re.I)
    return text


def normalize_datetime_input(text: str) -> str:
    def clock(match: re.Match[str]) -> str:
        hour, minute = int(match[1]), match[2]
        if hour > 23 or (minute is not None and int(minute) > 59):
            return match[0]
        if minute is None and hour <= 12:
            return match[0]  # Keep the existing ambiguous-hour policy.
        # Russian explicit clocks use 24h time, including 03:00. Do not let
        # the English shop-hours heuristic silently turn that into 15:00.
        suffix = " am" if hour < 12 and minute is not None else ""
        return f"at {hour}:{minute or '00'}{suffix}"

    text = re.sub(r"(?<!\w)в\s+(\d{1,2})(?::(\d{2}))?(?:\s+час(?:а|ов)?)?(?![\w:])", clock, text, flags=re.I)
    return _replace(text, (
        (r"послезавтра", "day after tomorrow"),
        (r"завтра", "tomorrow"), (r"сегодня", "today"),
        (r"через\s+неделю|на\s+следующей\s+неделе", "next week"),
        (r"в\s+следующ(?:ий|ую|ее)|следующ(?:ий|ая|ую|ее)", "next"),
        (r"понедельник(?:а|у|ом)?", "monday"),
        (r"вторник(?:а|у|ом)?", "tuesday"),
        (r"сред(?:а|у|ы)", "wednesday"),
        (r"четверг(?:а|у|ом)?", "thursday"),
        (r"пятниц(?:а|у|ы)", "friday"),
        (r"суббот(?:а|у|ы)", "saturday"),
        (r"воскресень(?:е|я)", "sunday"),
        (r"утром|утро|до\s+обеда", "morning"), (r"дн[её]м|после\s+обеда", "afternoon"),
        (r"вечером|вечер", "evening"), (r"в\s+полдень|полдень", "noon"),
        (r"в\s+то\s+же\s+время|то\s+же\s+время", "same time"),
        (r"в\s+тот\s+же\s+день|тот\s+же\s+день", "same day"),
        (r"в(?=\s+\d{1,2}(?::\d{2})?\b)", "at"),
    ))


def normalize_service_input(text: str) -> str:
    return _replace(text, (
        (r"замен(?:а|у|ы)\s+масла", "oil change"),
        (r"ремонт\s+тормозов", "brake repair"),
        (r"проверк(?:а|у)\s+тормозов", "brake inspection"),
        (r"перестановк(?:а|у)\s+шин", "tire rotation"),
        (r"развал[ -]схождение", "alignment"),
        (r"диагностик(?:а|у)", "diagnostic"),
    ))


def normalize_command_input(text: str) -> str:
    # Do not turn a negated request into a destructive affirmative command.
    if re.search(r"\bне\s+(?:(?:надо|нужно|хочу)\s+)?(?:отмен|перен|запис)\w*", text, re.I):
        return text
    return _replace(text, (
        (r"(?:отмени(?:те|ть)?|отменяю)\s+(?:мою\s+)?запись", "cancel appointment"),
        (r"(?:перенеси(?:те)?|перенести)\s+(?:мою\s+)?запись", "reschedule appointment"),
        (r"(?:измени(?:те|ть)?|поменяй(?:те)?)\s+(?:услугу|тип\s+услуги)\s+на", "change service type to"),
        (r"(?:измени(?:те|ть)?|поменяй(?:те)?)\s+(?:услугу|тип\s+услуги)", "change service type"),
        (r"хочу\s+записаться|запишите\s+меня|записаться\s+на", "book an appointment"),
        (r"какое\s+время\s+(?:есть|свободно)|какие\s+есть\s+(?:окна|свободные\s+места)", "what times are available"),
        (r"сколько\s+стоит|какая\s+цена|стоимость", "how much"),
        (r"мне\s+нужн(?:а|о)|хочу", "I need"),
        (r"пожалуйста", "please"),
    ))
