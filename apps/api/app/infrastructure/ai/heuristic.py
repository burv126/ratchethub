from __future__ import annotations

import re

from app.infrastructure.ai.ports import (
    RepairExtractionPort,
    RepairExtractionResult,
    SpeechSynthesisResult,
    SpeechToTextPort,
    TextToSpeechPort,
)
from app.infrastructure.ai.provider import AIProviderUnavailable


class HeuristicSpeechToText(SpeechToTextPort):
    """Text-only STT path (no demo/sample transcripts for audio).

    - If the uploaded file is UTF-8 text (e.g. .txt), treat contents as transcript.
    - Audio requires a real STT provider (Local Whisper / OpenAI).
    """

    name = "heuristic_stt"

    async def transcribe(self, *, audio_bytes: bytes, filename: str, content_type: str | None) -> str:
        lower = (filename or "").lower()
        if lower.endswith(".txt") or (content_type or "").startswith("text/"):
            try:
                text = audio_bytes.decode("utf-8").strip()
            except UnicodeDecodeError as exc:
                raise AIProviderUnavailable(
                    'Текстовая заметка не в UTF-8; загрузите обычный текст или используйте распознавание аудио'
                ) from exc
            if text:
                return text
            raise AIProviderUnavailable('Текстовая заметка пуста')

        raise AIProviderUnavailable(
            'Распознавание речи не настроено. Запустите Local Whisper (LOCAL_WHISPER_URL), задайте AI_PROVIDER=openai или загрузите заметку .txt.'
        )


class HeuristicTextToSpeech(TextToSpeechPort):
    """Dev/test TTS — returns UTF-8 spoken text (Twilio <Say> uses text)."""

    async def synthesize(self, *, text: str, voice: str | None = None) -> SpeechSynthesisResult:
        spoken = (text or "").strip()
        return SpeechSynthesisResult(
            audio_bytes=spoken.encode("utf-8"),
            content_type="text/plain",
            voice=voice or "alice",
            text=spoken,
        )


class HeuristicRepairExtraction(RepairExtractionPort):
    """Rule-based extractor for demos/tests without an LLM API key."""

    async def extract(self, *, transcript: str) -> RepairExtractionResult:
        text = " ".join(transcript.strip().split())
        if not text:
            return RepairExtractionResult(
                service="Inspection",
                condition='Нет текста расшифровки',
                recommendation=None,
                mileage=None,
            )

        mileage = None
        mileage_match = re.search(
            r"(?:пробег|одометр|mileage|odometer|miles?)\s*(?:is|=|:)?\s*([\d,]+)",
            text,
            flags=re.IGNORECASE,
        )
        if mileage_match:
            mileage = int(mileage_match.group(1).replace(",", ""))
        else:
            bare = re.search(r"\b(\d{4,6})\b(?:\s*(?:miles?|mi))?", text, flags=re.IGNORECASE)
            if bare:
                mileage = int(bare.group(1).replace(",", ""))

        recommendation = None
        rec_match = re.search(
            r"(?:рекомендую|рекомендуется|рекомендация:?|recommend(?:ed|ation)?|suggest(?:ed)?)\s+(.+?)(?:\.|$)",
            text,
            flags=re.IGNORECASE,
        )
        if rec_match:
            recommendation = rec_match.group(1).strip(" .")

        service = 'Общие работы'
        service_patterns = [
            (r"oil\s*change|замена\s+масла", "Oil Change"),
            (r"brake\s*pad|тормозн\w*\s+колод\w*", "Brake Service"),
            (r"tire|rotation|шины|перестановка\s+шин", "Tire Service"),
            (r"diagnostic|check\s*engine|диагностика", "Diagnostics"),
            (r"inspection|осмотр", "Inspection"),
        ]
        for pattern, label in service_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                service = label
                break

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        condition = sentences[0] if sentences else text
        for sentence in sentences:
            if re.search(r"percent|%|worn|completed|condition|износ|состояние|выполнено", sentence, flags=re.IGNORECASE):
                condition = sentence.rstrip(".")
                break

        return RepairExtractionResult(
            service=service,
            condition=condition,
            recommendation=recommendation,
            mileage=mileage,
        )
