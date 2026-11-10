"use client";

import { useEffect, useState } from "react";
import { getApiUrl } from "@/lib/api";

export function ApiHealthCard() {
  const [status, setStatus] = useState<"loading" | "ok" | "down">("loading");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    const apiUrl = getApiUrl();
    (async () => {
      try {
        const res = await fetch(`${apiUrl}/health`);
        const data = await res.json();
        if (cancelled) return;
        if (res.ok && data.status === "ok") {
          setStatus("ok");
          setDetail(`этап ${data.phase ?? "?"}`);
        } else {
          setStatus("down");
          setDetail("неожиданный ответ");
        }
      } catch {
        if (!cancelled) {
          setStatus("down");
          setDetail(`нет связи с ${apiUrl}`);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="surface-panel p-4">
      <p className="font-display text-sm font-semibold tracking-tight">Состояние API</p>
      <p className="mt-2 text-sm text-[var(--muted)]">
        {status === "loading" && "Проверка FastAPI…"}
        {status === "ok" && `Подключено (${detail})`}
        {status === "down" && `Недоступно — ${detail}`}
      </p>
    </div>
  );
}
