/**
 * Admin System Health — derives component levels from /v1/admin/system.
 * One admin endpoint (or its SSE stream) is enough; no multi-endpoint fan-out.
 */

import { getAdminSystem, type SystemStatus } from "@/lib/admin";

export type HealthLevel = "green" | "yellow" | "red";

export type HealthComponentId =
  | "api"
  | "database"
  | "ai"
  | "sms"
  | "voice"
  | "integrations";

/** Feature groups for admin System Health UI */
export type HealthFeatureGroupId =
  | "platform"
  | "ai"
  | "messaging"
  | "voice"
  | "integrations";

export type HealthFeatureGroup = {
  id: HealthFeatureGroupId;
  label: string;
  description: string;
  componentIds: HealthComponentId[];
};

export const HEALTH_FEATURE_GROUPS: HealthFeatureGroup[] = [
  {
    id: "platform",
    label: "Платформа",
    description: "Основной API и слой данных",
    componentIds: ["api", "database"],
  },
  {
    id: "ai",
    label: "ИИ",
    description: "Стек LLM и мониторинг использования",
    componentIds: ["ai"],
  },
  {
    id: "messaging",
    label: "Сообщения",
    description: "Провайдер SMS и среда выполнения",
    componentIds: ["sms"],
  },
  {
    id: "voice",
    label: "Звонки",
    description: "Провайдер звонков и среда выполнения",
    componentIds: ["voice"],
  },
  {
    id: "integrations",
    label: "Интеграции",
    description: "Внешние коннекторы автосервисов и оплаты",
    componentIds: ["integrations"],
  },
];

export type HealthComponent = {
  id: HealthComponentId;
  label: string;
  level: HealthLevel;
  status: string;
  detail: string;
};

export type SystemHealthSnapshot = {
  generated_at: string;
  overall: HealthLevel;
  components: HealthComponent[];
  incidents: SystemStatus["incidents"];
  metrics: {
    sms: Record<string, number | string | null>;
    voice: Record<string, number | string | null>;
  };
};

const COMPONENT_LABELS: Record<HealthComponentId, string> = {
  api: "API",
  database: "База данных",
  ai: "Сервис ИИ",
  sms: "Провайдер SMS",
  voice: "Провайдер звонков",
  integrations: "Интеграции",
};

function num(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

function openIncidentsFor(
  incidents: SystemStatus["incidents"],
  keys: string[],
): SystemStatus["incidents"] {
  return incidents.filter(
    (i) =>
      i.status !== "resolved" &&
      i.affected_components.some((c) => keys.some((k) => c.toLowerCase().includes(k))),
  );
}

function worst(...levels: HealthLevel[]): HealthLevel {
  if (levels.includes("red")) return "red";
  if (levels.includes("yellow")) return "yellow";
  return "green";
}

function levelLabel(level: HealthLevel): string {
  if (level === "green") return "healthy";
  if (level === "yellow") return "degraded";
  return "outage";
}

function providerLevel(args: {
  metrics: Record<string, number | string | null>;
  enabled?: boolean;
  provider?: string;
  queueDepth?: number | null;
  failureKeys: string[];
}): { level: HealthLevel; detail: string } {
  const provider = args.provider || "unknown";
  const failures = args.failureKeys.reduce((sum, k) => sum + num(args.metrics[k]), 0);
  const queueDepth = num(args.queueDepth ?? args.metrics.queue_depth);

  if (args.enabled === false) {
    return {
      level: "yellow",
      detail: `Отключено · провайдер ${provider}`,
    };
  }
  if (failures > 0 || queueDepth > 25) {
    return {
      level: "yellow",
      detail: `Провайдер ${provider} · ${failures} ошибок · очередь ${queueDepth}`,
    };
  }
  return {
    level: "green",
    detail: `Провайдер ${provider} · очередь ${queueDepth}`,
  };
}

function aiLevel(args: {
  apiOk: boolean;
  incidents: SystemStatus["incidents"];
  sms: Record<string, number | string | null>;
  voice: Record<string, number | string | null>;
}): { level: HealthLevel; detail: string } {
  const aiIncidents = openIncidentsFor(args.incidents, ["ai", "openai", "llm"]);
  const critical = aiIncidents.some((i) => i.severity === "critical" || i.severity === "major");
  if (!args.apiOk) {
    return { level: "red", detail: "API недоступен — нет связи со стеком ИИ" };
  }
  if (critical) {
    return {
      level: "red",
      detail: aiIncidents[0]?.title || "Открыт критический инцидент ИИ",
    };
  }
  if (aiIncidents.length > 0) {
    return {
      level: "yellow",
      detail: aiIncidents[0]?.title || "Открыт инцидент ИИ",
    };
  }
  const escalations = num(args.sms.escalations) + num(args.voice.escalations);
  if (escalations > 0) {
    return {
      level: "yellow",
      detail: `${escalations} недавних передач сотруднику (SMS/звонки)`,
    };
  }
  return { level: "green", detail: "API доступен · открытых инцидентов ИИ нет" };
}

function integrationsLevel(args: {
  sms: HealthLevel;
  voice: HealthLevel;
  redis: HealthLevel;
  incidents: SystemStatus["incidents"];
}): { level: HealthLevel; detail: string } {
  const integIncidents = openIncidentsFor(args.incidents, [
    "integration",
    "integrations",
    "stripe",
    "shopmonkey",
    "tekmetric",
    "quickbooks",
  ]);
  const critical = integIncidents.some((i) => i.severity === "critical" || i.severity === "major");
  if (critical) {
    return {
      level: "red",
      detail: integIncidents[0]?.title || "Критический инцидент интеграции",
    };
  }
  const providers = worst(args.sms, args.voice);
  const level = worst(providers, args.redis, integIncidents.length > 0 ? "yellow" : "green");
  if (level === "green") {
    return { level, detail: "Провайдеры связи и Redis работают" };
  }
  if (level === "red") {
    return { level, detail: "Одна или несколько зависимостей интеграций недоступны" };
  }
  return {
    level,
    detail:
      integIncidents[0]?.title ||
      (args.redis === "yellow" || args.redis === "red"
        ? "Сбой Redis — риск для очереди интеграций"
        : "Предупреждение провайдера или интеграции"),
  };
}

export function healthDotClass(level: HealthLevel): string {
  if (level === "green") return "bg-emerald-500";
  if (level === "yellow") return "bg-amber-400";
  return "bg-red-500";
}

export function healthTextClass(level: HealthLevel): string {
  if (level === "green") return "text-emerald-700";
  if (level === "yellow") return "text-amber-700";
  return "text-red-700";
}

/** Build UI snapshot from a single admin system status payload. */
export function buildSystemHealthFromStatus(system: SystemStatus): SystemHealthSnapshot {
  const incidents = system.incidents ?? [];
  const smsMetrics = system.sms ?? {};
  const voiceMetrics = system.voice ?? {};
  const providers = system.providers ?? {};

  const apiOk = Boolean(system.readiness);
  const env =
    system.readiness && typeof system.readiness === "object"
      ? String((system.readiness as { environment?: string }).environment ?? "—")
      : "—";

  const dbCheck = system.readiness?.checks?.database;
  const redisCheck = system.readiness?.checks?.redis;
  const dbUp = dbCheck?.status === "up";
  const redisUp = redisCheck?.status === "up";

  const api: HealthComponent = {
    id: "api",
    label: COMPONENT_LABELS.api,
    level: apiOk ? "green" : "red",
    status: apiOk ? "healthy" : "outage",
    detail: apiOk ? `среда ${env}` : "Ошибка системного запроса администратора",
  };

  const database: HealthComponent = {
    id: "database",
    label: COMPONENT_LABELS.database,
    level: dbUp ? "green" : "red",
    status: dbUp ? "healthy" : "outage",
    detail: dbUp ? "Соединение установлено" : dbCheck?.error || "Ошибка проверки базы данных",
  };

  const smsProv = providerLevel({
    metrics: smsMetrics,
    enabled: providers.sms?.enabled,
    provider: providers.sms?.provider,
    queueDepth: providers.sms?.queue_depth,
    failureKeys: ["queue_failures", "webhook_rejected"],
  });
  const sms: HealthComponent = {
    id: "sms",
    label: COMPONENT_LABELS.sms,
    level: smsProv.level,
    status: levelLabel(smsProv.level),
    detail: smsProv.detail,
  };

  const voiceProv = providerLevel({
    metrics: voiceMetrics,
    enabled: providers.voice?.enabled,
    provider: providers.voice?.provider,
    queueDepth: providers.voice?.queue_depth,
    failureKeys: ["webhook_rejected"],
  });
  const voice: HealthComponent = {
    id: "voice",
    label: COMPONENT_LABELS.voice,
    level: voiceProv.level,
    status: levelLabel(voiceProv.level),
    detail: voiceProv.detail,
  };

  const aiProv = aiLevel({
    apiOk,
    incidents,
    sms: smsMetrics,
    voice: voiceMetrics,
  });
  const ai: HealthComponent = {
    id: "ai",
    label: COMPONENT_LABELS.ai,
    level: aiProv.level,
    status: levelLabel(aiProv.level),
    detail: aiProv.detail,
  };

  const redisLevel: HealthLevel = redisCheck
    ? redisUp
      ? "green"
      : "yellow"
    : apiOk
      ? "yellow"
      : "red";

  const integProv = integrationsLevel({
    sms: sms.level,
    voice: voice.level,
    redis: redisLevel,
    incidents,
  });
  const integrations: HealthComponent = {
    id: "integrations",
    label: COMPONENT_LABELS.integrations,
    level: integProv.level,
    status: levelLabel(integProv.level),
    detail: integProv.detail,
  };

  const components = [api, database, ai, sms, voice, integrations];
  const overall = worst(...components.map((c) => c.level));

  return {
    generated_at: system.generated_at ?? new Date().toISOString(),
    overall,
    components,
    incidents,
    metrics: { sms: smsMetrics, voice: voiceMetrics },
  };
}

export async function loadSystemHealth(accessToken: string): Promise<SystemHealthSnapshot> {
  const system = await getAdminSystem(accessToken);
  return buildSystemHealthFromStatus(system);
}
