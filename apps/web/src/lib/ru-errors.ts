/** User-visible errors only. Never modify response bodies, codes, or logged errors. */
const messages: Record<string, string> = {
  "VIN must be 17 characters and exclude I, O, and Q": "VIN должен содержать 17 символов без букв I, O и Q.",
  "VIN already exists for this shop": "Автомобиль с таким VIN уже есть в этом автосервисе.",
  "VIN cannot be empty": "Введите VIN.",
  "A customer with this phone number already exists": "Клиент с таким номером телефона уже существует.",
  "A customer with this email already exists": "Клиент с такой электронной почтой уже существует.",
  "A service with this name already exists": "Услуга с таким названием уже существует.",
  "Walk-in already has a customer": "К этому визиту уже привязан клиент.",
  "Walk-in visit is closed": "Визит уже закрыт.",
  "Walk-in visit is cancelled": "Визит отменён.",
  "MFA is not enabled": "Двухфакторная аутентификация не включена.",
  "Speech-to-text returned an empty transcript": "Не удалось распознать речь. Попробуйте записать ещё раз.",
  "Invalid credentials": "Неверные данные для входа.",
  "Invalid token": "Ссылка или сеанс недействительны. Войдите снова.",
  "Email already registered": "Электронная почта уже зарегистрирована.",
  "Shop name already taken": "Название автосервиса уже занято.",
  "Shop not found": "Автосервис не найден.",
  "Not authenticated": "Войдите в учётную запись.",
  "Not Found": "Запрошенные данные не найдены.",
  "Forbidden": "Недостаточно прав для этого действия.",
  "Unauthorized": "Войдите в учётную запись.",
  "Too Many Requests": "Слишком много запросов. Повторите попытку позже.",
  "Failed to fetch": "Нет связи с сервером. Проверьте подключение.",
  "NetworkError when attempting to fetch resource.": "Нет связи с сервером. Проверьте подключение.",
  "auth_method must be phone or email": "Выберите вход по телефону или электронной почте.",
  "email or phone is required": "Введите электронную почту или номер телефона.",
  "service_id is required to book an appointment": "Выберите услугу для записи.",
  preferred_time_unavailable: "Выбранное время недоступно. Выберите другое время.",
  appointment_not_found: "Запись не найдена.",
  permission_denied: "Недостаточно прав для этого действия.",
};

const fields: Record<string, string> = {
  shop_name: "Название автосервиса", shop_slug: "Автосервис", name: "Имя",
  owner_full_name: "Имя владельца", owner_phone: "Телефон владельца",
  owner_email: "Электронная почта владельца", email: "Электронная почта",
  phone: "Телефон", password: "Пароль", new_password: "Новый пароль",
  username: "Имя пользователя", plan_id: "Тариф", service_id: "Услуга",
  vin: "VIN", mileage: "Пробег", price: "Цена", token: "Код подтверждения",
};

function fallback(status?: number): string {
  if (status === 401) return "Войдите в учётную запись.";
  if (status === 403) return "Недостаточно прав для этого действия.";
  if (status === 404) return "Запрошенные данные не найдены.";
  if (status === 409) return "Данные уже существуют или были изменены. Обновите страницу.";
  if (status === 422 || status === 400) return "Проверьте введённые данные.";
  if (status === 429) return "Слишком много запросов. Повторите попытку позже.";
  return "Не удалось выполнить действие. Повторите попытку позже.";
}

export function ruError(value: unknown, status?: number): string {
  if (value instanceof Error) return ruError(value.message, status);
  if (Array.isArray(value)) return value.length ? value.map(v => ruError(v, 422)).join("; ") : fallback(status);
  if (value && typeof value === "object") {
    const detail = value as { detail?: unknown; code?: unknown; message?: unknown; type?: unknown; loc?: unknown; msg?: unknown };
    if (typeof detail.type === "string" && Array.isArray(detail.loc)) {
      const field = fields[String(detail.loc.at(-1))];
      const prefix = field ? `${field}: ` : "";
      const type = detail.type;
      return prefix + (type === "missing" ? "заполните обязательное поле." :
        type === "string_too_short" ? "введённое значение слишком короткое." :
        type === "string_too_long" ? "введённое значение слишком длинное." :
        type === "int_parsing" || type === "float_parsing" || type === "decimal_parsing" ? "введите корректное число." :
        "проверьте введённое значение.");
    }
    if (typeof detail.code === "string" && messages[detail.code]) return messages[detail.code];
    return ruError(detail.detail ?? detail.message ?? detail.msg, status);
  }
  if (typeof value !== "string") return fallback(status);
  const message = value.trim();
  if (messages[message]) return messages[message];
  const required = /^(\w+) is required$/.exec(message);
  if (required && fields[required[1]]) return `${fields[required[1]]}: заполните обязательное поле.`;
  // Unknown diagnostics are not UI copy. Never stringify response objects, inputs,
  // SQL/tracebacks, provider URLs or secrets into a user-visible error.
  if (message.length > 500 || /traceback|exception|\b\w*error\b|connection refused|timed out|postgres|sqlalchemy|https?:\/\/|bearer\s|sk-[\w-]+|(?:password|secret|token|api[_-]?key)\s*[=:]|\b(?:select|insert|delete|update)\b.+\b(?:from|into|set)\b|[A-Z]:\\|(?:^|\s)\/(?:etc|home|var|Users|app|srv|tmp)\//i.test(message)) return fallback(status);
  return /[А-Яа-яЁё]/.test(message) ? message : fallback(status);
}

export async function readApiError(response: Response): Promise<string> {
  try {
    return ruError(await response.json(), response.status);
  } catch {
    return ruError(null, response.status);
  }
}

export function ruNotification(note: { event_type?: string; message?: string; payload?: Record<string, unknown> }): string {
  const payload = note.payload ?? {};
  const shop = typeof payload.shop_name === "string" ? payload.shop_name : "";
  const person = typeof payload.joined_by === "string" ? payload.joined_by : "";
  if (note.event_type === "saas.signup") return shop ? `Зарегистрирован автосервис «${shop}».` : "Зарегистрирован новый автосервис.";
  if (note.event_type === "saas.member_joined") return person ? `К команде присоединился сотрудник: ${person}.` : "К команде присоединился новый сотрудник.";
  if (note.event_type === "saas.contact_changed") return "Контактные данные сотрудника обновлены.";
  const message = ruError(note.message);
  return message === fallback() ? "Новое уведомление. Откройте связанную запись." : message;
}

export function ruNotificationTitle(note: { title?: string; event_type?: string }): string {
  const titles: Record<string, string> = {
    "saas.signup": "Новый автосервис", "saas.member_joined": "Новый сотрудник",
    "saas.contact_changed": "Контакт обновлён",
  };
  return titles[note.event_type ?? ""] ?? (/[А-Яа-яЁё]/.test(note.title ?? "") ? ruError(note.title) : "Уведомление");
}

/** Redact only the displayed diagnostic copy; raw logs/API data stay intact. */
export function ruDiagnostic(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(ruDiagnostic);
  if (value && typeof value === "object") return Object.fromEntries(
    Object.entries(value).map(([key, item]) => [key,
      /password|secret|token|authorization|api[_-]?key/i.test(key) ? "[скрыто]" :
      /^(error|exception|last_error|failure_reason)$/i.test(key) && item ? ruError(item) : ruDiagnostic(item)]),
  );
  return value;
}

export function ruWorkflowLog(line: string): string {
  if (line === "Conditions matched") return "Условия выполнены";
  if (line.startsWith("Triggered by ")) return "Процесс запущен событием";
  if (/^Step \d+:/i.test(line)) return /failed|error/i.test(line) ? "Не удалось выполнить шаг процесса." : "Шаг процесса обработан.";
  const message = ruError(line);
  return message === fallback() ? "Запись в журнале процесса." : message;
}

export function ruIntegrationLog(log: { level: string; message: string }): string {
  const message = ruError(log.message);
  if (["error", "critical", "warning"].includes(log.level.toLowerCase())) return message;
  return message === fallback() ? "Событие интеграции зарегистрировано." : message;
}
