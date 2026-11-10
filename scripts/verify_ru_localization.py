"""Check localization boundaries without accessing customer data or services."""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from app.agents.counselor.persona import (  # noqa: E402
    ask_name,
    ask_purpose,
    format_when,
    is_name_question,
    is_purpose_question,
    summarize_done,
    wants_to_end_after_offer,
)
from app.localization import status_label  # noqa: E402
from app.marketing.enums import CampaignType, Channel  # noqa: E402
from app.marketing.templates import render_template  # noqa: E402
from app.sms.reply import _format_appt_when  # noqa: E402
from app.voice.twilio.provider import render_gather_twiml  # noqa: E402


def main() -> None:
    name = "Иван {имя}"
    vehicle = "Honda Accord"
    for kind in CampaignType:
        for channel in Channel:
            body = render_template(
                kind, channel, name=name, vehicle=vehicle, service="Oil Change",
                shop="Авто & Сервис", offer="https://example.com/?a=1&b=2",
            )
            assert name in body
            assert re.search("[А-Яа-яЁё]", body)
            assert "{shop}" not in body and "{offer}" not in body

    custom = "Customer template: {name} / {vehicle}"
    assert render_template(
        CampaignType.THANK_YOU, Channel.SMS,
        name=name, vehicle=vehicle, custom=custom,
    ) == f"Customer template: {name} / {vehicle}"

    instant = datetime(2026, 8, 5, 15, tzinfo=timezone.utc)
    assert format_when(instant) == "среда в 08:00"
    assert _format_appt_when(instant.isoformat()) == "05.08.2026 в 08:00"
    assert is_name_question(ask_name())
    assert is_purpose_question(ask_purpose())
    completed = summarize_done(action="book", keep_open=True)
    assert wants_to_end_after_offer("No, thank you", last_assistant_text=completed)
    assert wants_to_end_after_offer("нет, спасибо", last_assistant_text=completed)
    assert status_label("completed") == "завершено"
    assert status_label("custom_status") == "custom_status"

    action_url = "https://example.com/callback?shop=1&call=2"
    text = "Здравствуйте! Авто & Сервис <запись>"
    for configured, expected in [("Polly.Joanna", "Polly.Tatyana"), ("Polly.Maxim", "Polly.Maxim")]:
        xml = render_gather_twiml(
            say_text=text, action_url=action_url, voice=configured,
            barge_in=True, gather_timeout=5, speech_timeout="auto",
        )
        root = ElementTree.fromstring(xml)
        gather = root.find("Gather")
        assert gather is not None
        assert gather.attrib["language"] == "ru-RU"
        assert gather.attrib["action"] == action_url
        say = gather.find("Say")
        assert say is not None and say.text == text
        assert say.attrib["voice"] == expected

    print("Russian templates, interpolation, conversation cues, dates and TwiML: passed")


if __name__ == "__main__":
    main()
