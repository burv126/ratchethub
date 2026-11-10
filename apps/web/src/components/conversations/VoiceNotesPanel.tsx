"use client";
import { ruLabel } from "@/lib/ru";
import { ruError } from "@/lib/ru-errors";


import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth";
import { loadSession } from "@/lib/api";
import {
  getAudioUrl,
  listShopVehicles,
  listVoiceNotes,
  uploadVoiceNote,
  VehicleOption,
  VoiceNote,
  VoiceNoteProcessResult,
} from "@/lib/voiceNotes";

function pickAudioMimeType(): string | undefined {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
  ];
  if (typeof MediaRecorder === "undefined" || !MediaRecorder.isTypeSupported) {
    return undefined;
  }
  return candidates.find((t) => MediaRecorder.isTypeSupported(t));
}

function extensionForMime(mime: string): string {
  if (mime.includes("mp4")) return "m4a";
  if (mime.includes("ogg")) return "ogg";
  return "webm";
}

function micErrorMessage(err: unknown): string {
  if (typeof window !== "undefined" && !window.isSecureContext) {
    return "Для микрофона требуется HTTPS (или localhost). Откройте страницу по защищённому соединению или используйте текстовую заметку ниже.";
  }
  const name = err instanceof DOMException || err instanceof Error ? err.name : "";
  const message = err instanceof Error ? err.message : "";
  if (name === "NotAllowedError" || /NotAllowedError|Permission|Permissions policy/i.test(message)) {
    return "Доступ к микрофону запрещён. Разрешите его для этого сайта в браузере и повторите попытку.";
  }
  if (name === "NotFoundError" || /NotFoundError|Requested device not found/i.test(message)) {
    return "Микрофон не найден. Используйте текстовую заметку ниже или подключите микрофон.";
  }
  if (name === "NotReadableError" || /NotReadableError|in use/i.test(message)) {
    return "Микрофон используется другим приложением. Закройте его и повторите попытку.";
  }
  if (message) return message;
  return "Не удалось получить доступ к микрофону. Используйте текстовую заметку или проверьте разрешения браузера.";
}

export function VoiceNotesPanel() {
  const { session, loading: authLoading } = useAuth();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const mimeTypeRef = useRef("audio/webm");

  const [vehicles, setVehicles] = useState<VehicleOption[]>([]);
  const [vehicleId, setVehicleId] = useState("");
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VoiceNoteProcessResult | null>(null);
  const [notes, setNotes] = useState<VoiceNote[]>([]);
  const [audioUrls, setAudioUrls] = useState<Record<string, string>>({});
  const [textFallback, setTextFallback] = useState(
    "Honda Accord 2019 года: замена масла выполнена. Остаток тормозных колодок — 30 процентов. Рекомендуется замена при следующем визите. Пробег 82000.",
  );

  useEffect(() => {
    if (authLoading || !session) return;
    void (async () => {
      try {
        setVehicles(await listShopVehicles());
        setNotes(await listVoiceNotes());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить");
      }
    })();
  }, [authLoading, session]);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    };
  }, []);

  async function startRecording() {
    setError(null);
    setResult(null);
    if (!vehicleId) {
      setError("Сначала выберите автомобиль");
      return;
    }
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setError("Браузер не поддерживает микрофон. Используйте текстовую заметку ниже.");
      return;
    }
    if (typeof window !== "undefined" && !window.isSecureContext) {
      setError(
        "Для микрофона требуется HTTPS (или localhost). Откройте страницу по защищённому соединению или используйте текстовую заметку ниже.",
      );
      return;
    }
    if (typeof MediaRecorder === "undefined") {
      setError("Браузер не поддерживает запись. Используйте текстовую заметку ниже.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = pickAudioMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);
      mimeTypeRef.current = recorder.mimeType || mimeType || "audio/webm";
      chunksRef.current = [];
      streamRef.current = stream;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch (err) {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
      setError(micErrorMessage(err));
    }
  }

  async function stopAndUpload() {
    const recorder = mediaRecorderRef.current;
    if (!recorder) return;

    setBusy(true);
    setError(null);
    setRecording(false);

    await new Promise<void>((resolve) => {
      recorder.onstop = () => resolve();
      // Request final chunk before stop (needed for some browsers when no timeslice was used).
      try {
        recorder.requestData();
      } catch {
        /* requestData unsupported or inactive */
      }
      recorder.stop();
    });

    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    mediaRecorderRef.current = null;

    try {
      const mime = mimeTypeRef.current || "audio/webm";
      const blob = new Blob(chunksRef.current, { type: mime });
      if (blob.size === 0) {
        throw new Error("Запись пустая. Попробуйте снова или используйте текстовую заметку ниже.");
      }
      const filename = `mechanic-note.${extensionForMime(mime)}`;
      const processed = await uploadVoiceNote(vehicleId, blob, filename);
      setResult(processed);
      setNotes(await listVoiceNotes());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить файл");
    } finally {
      setBusy(false);
    }
  }

  async function uploadTextAsNote() {
    if (!vehicleId) {
      setError("Сначала выберите автомобиль");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const blob = new Blob([textFallback], { type: "text/plain" });
      const processed = await uploadVoiceNote(vehicleId, blob, "mechanic-note.txt");
      setResult(processed);
      setNotes(await listVoiceNotes());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить файл");
    } finally {
      setBusy(false);
    }
  }

  async function playAudio(noteId: string) {
    if (audioUrls[noteId]) return;
    const current = loadSession();
    if (!current) {
      setError("Вход не выполнен");
      return;
    }
    try {
      const res = await fetch(getAudioUrl(noteId), {
        headers: { Authorization: `Bearer ${current.accessToken}` },
      });
      if (!res.ok) throw new Error("Не удалось получить аудио");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrls((prev) => ({ ...prev, [noteId]: url }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить аудио");
    }
  }

  return (
    <div className="min-h-0 flex-1 space-y-8 overflow-y-auto overscroll-contain">
      <p className="text-sm text-[var(--muted)]">
        Говорите естественно. Система распознает речь, извлечёт сведения и запишет их в историю ремонта.
      </p>

      {error && (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          {ruError(error)}
        </p>
      )}

      <section className="space-y-4 rounded-xl border border-[var(--line)] bg-[var(--panel)] p-4">
        <label className="block space-y-1.5">
          <span className="text-sm font-medium">Автомобиль</span>
          <select
            value={vehicleId}
            onChange={(e) => setVehicleId(e.target.value)}
            className="w-full rounded-md border border-[var(--line)] bg-white px-3 py-2 text-sm"
          >
            <option value="">Выберите автомобиль…</option>
            {vehicles.map((v) => (
              <option key={v.id} value={v.id}>
                {v.label}
              </option>
            ))}
          </select>
        </label>

        <div className="flex flex-wrap gap-3">
          {!recording ? (
            <button
              type="button"
              onClick={() => void startRecording()}
              disabled={busy}
              className="rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              Начать запись
            </button>
          ) : (
            <button
              type="button"
              onClick={() => void stopAndUpload()}
              disabled={busy}
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {busy ? "Обработка…" : "Остановить и обработать"}
            </button>
          )}
        </div>

        <div className="border-t border-[var(--line)] pt-4">
          <p className="text-sm font-medium">Нет микрофона? Вставьте или измените текст заметки</p>
          <textarea
            value={textFallback}
            onChange={(e) => setTextFallback(e.target.value)}
            rows={4}
            className="mt-2 w-full rounded-md border border-[var(--line)] bg-white px-3 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2"
          />
          <button
            type="button"
            onClick={() => void uploadTextAsNote()}
            disabled={busy}
            className="mt-3 rounded-md border border-[var(--line)] px-4 py-2 text-sm disabled:opacity-60"
          >
            {busy ? "Обработка…" : "Обработать текст как голосовую заметку"}
          </button>
        </div>
      </section>

      {result && (
        <section className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--panel)] p-4">
          <h2 className="text-sm font-semibold">Результат ИИ</h2>
          <p className="text-sm">
            <span className="font-medium">Расшифровка:</span> {result.voice_note.transcript}
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <Fact label="Услуга" value={ruLabel(result.extraction.service)} />
            <Fact label="Пробег" value={result.extraction.mileage?.toLocaleString("ru-RU") ?? "—"} />
            <Fact label="Условие" value={result.extraction.condition} />
            <Fact label="Рекомендация" value={result.extraction.recommendation ?? "—"} />
          </div>
          <p className="text-sm text-[var(--muted)]">
            Сохранённая запись о ремонте{" "}
            <Link
              href={`/dashboard/vehicles/${result.vehicle.id}`}
              className="font-medium text-[var(--accent)]"
            >
              на странице автомобиля
            </Link>
            .
          </p>
        </section>
      )}

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">Последние голосовые заметки</h2>
        {notes.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">Голосовых заметок пока нет</p>
        ) : (
          notes.map((n) => (
            <div key={n.id} className="rounded-xl border border-[var(--line)] bg-[var(--panel)] p-4">
              <p className="text-xs text-[var(--muted)]">
                {n.created_at ? new Date(n.created_at).toLocaleString("ru-RU") : "—"}
              </p>
              <p className="mt-2 text-sm">{n.transcript ?? "Обработка расшифровки…"}</p>
              <div className="mt-3">
                {audioUrls[n.id] ? (
                  <audio controls src={audioUrls[n.id]} className="w-full max-w-md" />
                ) : (
                  <button
                    type="button"
                    className="rounded-md border border-[var(--line)] px-3 py-1.5 text-xs"
                    onClick={() => void playAudio(n.id)}
                  >
                    Загрузить аудио
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.08em] text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-sm">{value}</p>
    </div>
  );
}
